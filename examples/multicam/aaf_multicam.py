#!/usr/bin/env python
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""EXPERIMENTAL (OTIO issue #427): read an Avid multicam AAF into the
prototype Multicam / MulticamClip schema.

Avid writes a multicam edit as one ``Selector`` per cut (Selected plus
Alternates). Every Selector points into one shared backing CompositionMob
whose slots are the angles' picture and mono audio tracks, padded with Filler
to the multicam's length. This script turns that backing mob into one
``Multicam`` (an angle per source clip, named after its first master clip),
and each Selector into a ``MulticamClip``.

    pip install pyaaf2
    python aaf_multicam.py "Avid MCAM EDIT.aaf" out.otio [--flat flat.otio]

Tested against Trevor Aylward's Avid project in
https://github.com/TrevorAyl/otio-multicam-tests.
"""

import argparse
import os
import sys

import aaf2
import opentimelineio as otio

RT = otio.opentime.RationalTime
TR = otio.opentime.TimeRange


def _rate(slot):
    r = slot.edit_rate
    return float(r.numerator) / float(r.denominator)


def _kind(slot_or_component):
    kind = slot_or_component.media_kind
    if kind == "Picture":
        return otio.schema.TrackKind.Video
    if kind == "Sound":
        return otio.schema.TrackKind.Audio
    return None


def _components(segment):
    if isinstance(segment, aaf2.components.Sequence):
        return segment.components
    return [segment]


def _gap(length, rate):
    return otio.schema.Gap(source_range=TR(RT(0, rate), RT(length, rate)))


class Reader:
    def __init__(self, aaf_file):
        self.f = aaf_file
        self.report = []
        self._master_cache = {}
        self.multicams = {}  # backing mob id -> (key, Multicam, slot map)

    # -- master clips -----------------------------------------------------

    def _file_info(self, master_mob, slot_id):
        """(url, timecode start, available length) of a master clip slot."""
        key = (str(master_mob.mob_id), slot_id)
        if key in self._master_cache:
            return self._master_cache[key]
        url, tc_start, length = None, 0, None
        try:
            slot = master_mob.slot_at(slot_id)
            length = slot.segment.length
            seg = slot.segment
            if isinstance(seg, aaf2.components.Sequence):
                seg = seg.components[0]
            src = seg.mob if hasattr(seg, "mob") else None
            # walk down to a file SourceMob with a locator, and a tape/file
            # SourceMob with timecode
            depth = 0
            while src is not None and depth < 4:
                desc = src.descriptor if hasattr(src, "descriptor") else None
                if desc is not None and url is None:
                    for loc in desc.get("Locator", []) or []:
                        url = loc["URLString"].value
                        break
                for s in src.slots:
                    if isinstance(s.segment, aaf2.components.Timecode):
                        tc_start = s.segment.start
                    elif isinstance(s.segment, aaf2.components.Sequence):
                        for c in s.segment.components:
                            if isinstance(c, aaf2.components.Timecode):
                                tc_start = c.start
                nxt = None
                for s in src.slots:
                    seg2 = s.segment
                    if isinstance(seg2, aaf2.components.Sequence) and len(
                        seg2.components
                    ):
                        seg2 = seg2.components[0]
                    if isinstance(seg2, aaf2.components.SourceClip) and seg2.mob:
                        nxt = seg2.mob
                        break
                src, depth = nxt, depth + 1
        except Exception as err:  # pragma: no cover - diagnostic only
            self.report.append("master {}: {}".format(master_mob.name, err))
        result = (url, tc_start, length)
        self._master_cache[key] = result
        return result

    def _clip(self, source_clip, rate):
        mob = source_clip.mob
        start = source_clip.start
        length = source_clip.length
        if mob is None:
            return _gap(length, rate)
        url, tc_start, available = self._file_info(mob, source_clip.slot_id)
        name = mob.name or "clip"
        if url:
            ref = otio.schema.ExternalReference(target_url=url)
        else:
            ref = otio.schema.MissingReference(name=name)
        if available is not None:
            ref.available_range = TR(RT(tc_start, rate), RT(available, rate))
        clip = otio.schema.Clip(
            name=name,
            media_reference=ref,
            source_range=TR(RT(tc_start + start, rate), RT(length, rate)),
        )
        clip.metadata["AAF"] = {
            "MobID": str(mob.mob_id),
            "SlotID": source_clip.slot_id,
        }
        return clip

    # -- multicam definitions ---------------------------------------------

    def multicam_for(self, backing_mob):
        """Build (once) the Multicam for a backing CompositionMob."""
        mob_id = str(backing_mob.mob_id)
        if mob_id in self.multicams:
            return self.multicams[mob_id]

        angles = {}  # angle name -> [ (kind, slot) ]
        order = []
        for slot in backing_mob.slots:
            kind = _kind(slot)
            if kind is None:
                continue
            first = None
            seg = slot.segment
            comps = _components(seg)
            for c in comps:
                if isinstance(c, aaf2.components.SourceClip) and c.mob is not None:
                    first = c.mob.name
                    break
            name = os.path.splitext(first or "Angle {}".format(slot.slot_id))[0]
            if name not in angles:
                angles[name] = []
                order.append(name)
            angles[name].append((kind, slot))

        slot_map = {}  # backing slot id -> (angle name, kind, index in kind)
        stacks = []
        for name in order:
            stack = otio.schema.Stack(name=name)
            per_kind = {}
            for kind, slot in angles[name]:
                rate = _rate(slot)
                track = otio.schema.Track(kind=kind)
                seg = slot.segment
                comps = _components(seg)
                for c in comps:
                    if isinstance(c, aaf2.components.SourceClip):
                        track.append(self._clip(c, rate))
                    else:
                        track.append(_gap(c.length, rate))
                index = per_kind.get(kind, 0)
                per_kind[kind] = index + 1
                slot_map[slot.slot_id] = (name, kind, index)
                stack.append(track)
            stacks.append(stack)

        group_name = self._group_name_for(backing_mob) or backing_mob.name or "Multicam"
        multicam = otio.schema.Multicam(
            name=group_name,
            angles=stacks,
            global_start_time=RT(0, _rate(backing_mob.slots[0])),
        )
        multicam.metadata["AAF"] = {"MobID": mob_id}
        key = "aaf:" + mob_id
        self.multicams[mob_id] = (key, multicam, slot_map)
        return self.multicams[mob_id]

    def _group_name_for(self, backing_mob):
        """Name of the lower-level group mob that selects from this mob."""
        for mob in self.f.content.mobs:
            if not isinstance(mob, aaf2.mobs.CompositionMob) or mob is backing_mob:
                continue
            for slot in mob.slots:
                seg = slot.segment
                if isinstance(seg, aaf2.components.Selector):
                    sel = seg["Selected"].value
                    if getattr(sel, "mob", None) is backing_mob and mob.name:
                        return mob.name
        return None

    # -- the edit ---------------------------------------------------------

    def _selector(self, selector, rate, kind):
        selected = selector["Selected"].value
        length = selector.length
        if selected is None or not isinstance(selected, aaf2.components.SourceClip):
            return _gap(length, rate)
        backing = selected.mob
        key, multicam, slot_map = self.multicam_for(backing)
        angle, angle_kind, index = slot_map.get(selected.slot_id, (None, None, 0))
        if angle is None:
            self.report.append(
                "selector into unknown slot {}".format(selected.slot_id)
            )
            return _gap(length, rate)
        cut = otio.schema.MulticamClip(
            name=angle,
            multicam=key,
            angle=angle,
            angle_track=index,
            source_range=TR(RT(selected.start, rate), RT(length, rate)),
        )
        if angle_kind != kind:
            self.report.append(
                "cut {} on a {} track selects a {} slot".format(angle, kind, angle_kind)
            )
        return cut

    def component(self, comp, rate, kind):
        if isinstance(comp, aaf2.components.Selector):
            return self._selector(comp, rate, kind)
        if isinstance(comp, aaf2.components.SourceClip):
            mob = comp.mob
            if isinstance(mob, aaf2.mobs.CompositionMob):
                # a nested composition: keep it as a stack of its slot
                return otio.schema.Gap(
                    name="nested " + (mob.name or ""),
                    source_range=TR(RT(0, rate), RT(comp.length, rate)),
                )
            return self._clip(comp, rate)
        if isinstance(comp, aaf2.components.OperationGroup):
            op_name = comp.operation.name if comp.operation else ""
            stack = otio.schema.Stack(name=op_name)
            for seg in comp.segments:
                stack.append(self.track(seg, rate, kind))
            stack.effects.append(otio.schema.Effect(effect_name=op_name))
            return stack
        if isinstance(comp, aaf2.components.Sequence):
            return self.track(comp, rate, kind)
        return _gap(comp.length, rate)

    def track(self, segment, rate, kind, name=""):
        track = otio.schema.Track(name=name, kind=kind)
        comps = _components(segment)
        for comp in comps:
            item = self.component(comp, rate, kind)
            if isinstance(item, otio.schema.Track):
                track.extend([c.deepcopy() for c in item])
            else:
                track.append(item)
        return track

    def timeline(self):
        top = next(
            m for m in self.f.content.mobs
            if isinstance(m, aaf2.mobs.CompositionMob)
            and m.usage == "Usage_TopLevel"
        )
        timeline = otio.schema.Timeline(name=top.name)
        video, audio = [], []
        for slot in top.slots:
            kind = _kind(slot)
            if kind is None:
                continue
            rate = _rate(slot)
            seg = slot.segment
            if isinstance(seg, aaf2.components.NestedScope):
                for i, inner in enumerate(seg["Slots"].value):
                    video.append(self.track(inner, rate, kind, "V{}".format(i + 1)))
            else:
                audio.append(self.track(seg, rate, kind, "A{}".format(len(audio) + 1)))
        for t in video + audio:
            timeline.tracks.append(t)
        timeline.set_multicams({k: mc for (k, mc, _) in self.multicams.values()})
        return timeline


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("aaf")
    parser.add_argument("otio")
    parser.add_argument("--flat", help="also write the flattened timeline here")
    args = parser.parse_args(argv)

    with aaf2.open(args.aaf, "r") as f:
        reader = Reader(f)
        timeline = reader.timeline()

    problems = otio.algorithms.validate_multicams(timeline)
    otio.adapters.write_to_file(timeline, args.otio)
    cuts = list(
        timeline.find_children(descended_from_type=otio.schema.MulticamClip)
    )
    print("multicams: {}  angles: {}  cuts: {}  size: {} bytes".format(
        len(timeline.multicams()),
        sum(len(m) for m in timeline.multicams().values()),
        len(cuts),
        os.path.getsize(args.otio),
    ))
    for line in reader.report + problems:
        print("  !", line)
    if args.flat:
        flat, report = otio.algorithms.flatten_multicam(timeline)
        otio.adapters.write_to_file(flat, args.flat)
        for line in report:
            print("  flatten:", line)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
