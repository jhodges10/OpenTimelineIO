# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Algorithms for multicam (EXPERIMENTAL, OTIO issue #427).

A :class:`.Multicam` is held once in :meth:`.Timeline.multicams`; each cut is a
:class:`.MulticamClip` on an ordinary track that names the multicam, the live
angle and (counting only tracks of its own track's kind) the angle track.
"""

import copy

from .. import schema, opentime
from . import track_algo


class MulticamResolutionError(ValueError):
    """A MulticamClip names something the timeline does not hold."""


def _kind_of(item, default=schema.TrackKind.Video):
    parent = item.parent()
    while parent is not None and not isinstance(parent, schema.Track):
        parent = parent.parent()
    return parent.kind if parent is not None else default


def angle_tracks(angle, kind):
    """The angle's tracks of ``kind`` ("Video" or "Audio"), in order."""
    return [t for t in angle if isinstance(t, schema.Track) and t.kind == kind]


def resolve_multicam_clip(timeline, multicam_clip, kind=None):
    """Return ``(multicam, angle, angle_track)`` for a cut.

    ``kind`` defaults to the kind of the track holding the cut.
    Raises :class:`MulticamResolutionError` when something is missing.
    """
    kind = kind or _kind_of(multicam_clip)
    multicam = timeline.multicam(multicam_clip.multicam)
    if multicam is None:
        raise MulticamResolutionError(
            "{!r}: no multicam with key {!r}".format(
                multicam_clip.name, multicam_clip.multicam
            )
        )
    angle = multicam.angle(multicam_clip.angle)
    if angle is None:
        raise MulticamResolutionError(
            "{!r}: multicam {!r} has no angle {!r}".format(
                multicam_clip.name, multicam_clip.multicam, multicam_clip.angle
            )
        )
    tracks = angle_tracks(angle, kind)
    if not 0 <= multicam_clip.angle_track < len(tracks):
        raise MulticamResolutionError(
            "{!r}: angle {!r} has {} {} track(s), angle_track is {}".format(
                multicam_clip.name,
                multicam_clip.angle,
                len(tracks),
                kind,
                multicam_clip.angle_track,
            )
        )
    return multicam, angle, tracks[multicam_clip.angle_track]


def _multicam_clips_in(composition):
    return composition.find_children(descended_from_type=schema.MulticamClip)


def validate_multicams(timeline):
    """Return a list of problems (empty when valid).

    Checks: unique angle names per multicam, every cut resolves, and no
    multicam reaches itself through its angles.
    """
    problems = []
    multicams = timeline.multicams()

    for key, multicam in multicams.items():
        names = multicam.angle_names()
        dupes = sorted({n for n in names if names.count(n) > 1})
        if dupes:
            problems.append(
                "multicam {!r}: duplicate angle names {}".format(key, dupes)
            )

    # cycles: edges from a multicam to the multicams its angles cut to
    edges = {
        key: {c.multicam for c in _multicam_clips_in(multicam)}
        for key, multicam in multicams.items()
    }

    def reaches(start, target, seen):
        for nxt in edges.get(start, ()):
            if nxt == target:
                return True
            if nxt not in seen:
                seen.add(nxt)
                if reaches(nxt, target, seen):
                    return True
        return False

    for key in multicams:
        if reaches(key, key, set()):
            problems.append("multicam {!r} contains itself".format(key))

    cuts = list(_multicam_clips_in(timeline.tracks))
    for multicam in multicams.values():
        cuts.extend(_multicam_clips_in(multicam))
    for cut in cuts:
        try:
            resolve_multicam_clip(timeline, cut)
        except MulticamResolutionError as err:
            problems.append(str(err))
    return problems


def _slice(timeline, cut, report, depth):
    """The items a cut plays, as a list of new items in the cut's time."""
    kind = _kind_of(cut)
    rng = cut.trimmed_range()
    try:
        _, _, track = resolve_multicam_clip(timeline, cut, kind)
    except MulticamResolutionError as err:
        report.append("{} (replaced with a gap)".format(err))
        return [schema.Gap(source_range=opentime.TimeRange(duration=rng.duration))]
    if depth > 32:
        report.append("{!r}: multicam nesting too deep".format(cut.name))
        return [schema.Gap(source_range=opentime.TimeRange(duration=rng.duration))]

    trimmed = track_algo.track_trimmed_to_range(track, rng)
    _flatten_composition(timeline, trimmed, report, depth + 1)
    items = [copy.deepcopy(child) for child in trimmed]

    # a cut past the end of the angle's content: pad with a gap
    played = sum(
        (i.duration() for i in items if not isinstance(i, schema.Transition)),
        opentime.RationalTime(0, rng.duration.rate),
    )
    if played < rng.duration:
        items.append(
            schema.Gap(source_range=opentime.TimeRange(duration=rng.duration - played))
        )

    if cut.effects or cut.markers:
        if len(items) == 1:
            items[0].effects.extend(copy.deepcopy(e) for e in cut.effects)
            items[0].markers.extend(copy.deepcopy(m) for m in cut.markers)
        else:
            report.append(
                "{!r}: effects/markers on a cut spanning {} items were dropped".format(
                    cut.name, len(items)
                )
            )
    for item in items:
        item.metadata.setdefault("otio.multicam", {})["flattened_from"] = {
            "multicam": cut.multicam,
            "angle": cut.angle,
            "angle_track": cut.angle_track,
        }
    return items


def _flatten_composition(timeline, composition, report, depth=0):
    for index in reversed(range(len(composition))):
        child = composition[index]
        if isinstance(child, schema.MulticamClip):
            items = _slice(timeline, child, report, depth)
            del composition[index]
            if isinstance(composition, schema.Track):
                for offset, item in enumerate(items):
                    composition.insert(index + offset, item)
            else:
                composition.insert(index, schema.Track(children=items))
        elif hasattr(child, "find_children"):
            _flatten_composition(timeline, child, report, depth)


def flatten_multicam(in_timeline):
    """Return ``(timeline, report)``: a copy with every MulticamClip replaced
    by the clips its angle plays, and the multicam definitions removed.

    ``report`` lists anything that could not be carried over.
    """
    timeline = copy.deepcopy(in_timeline)
    report = []
    _flatten_composition(timeline, timeline.tracks, report)
    timeline.set_multicams({})
    return timeline, report
