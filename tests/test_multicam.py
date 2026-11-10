# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""EXPERIMENTAL multicam prototype (OTIO issue #427)."""

import unittest

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils

RT = otio.opentime.RationalTime
TR = otio.opentime.TimeRange


def _clip(name, start, duration, rate=25):
    return otio.schema.Clip(
        name=name,
        media_reference=otio.schema.ExternalReference(
            target_url=name + ".mov",
            available_range=TR(RT(0, rate), RT(4500, rate)),
        ),
        source_range=TR(RT(start, rate), RT(duration, rate)),
    )


def _gap(duration, rate=25):
    return otio.schema.Gap(duration=RT(duration, rate))


def _cut(angle, start, duration, angle_track=0, multicam="mc", rate=25):
    return otio.schema.MulticamClip(
        name=angle,
        multicam=multicam,
        angle=angle,
        angle_track=angle_track,
        source_range=TR(RT(start, rate), RT(duration, rate)),
    )


def _timeline():
    a = otio.schema.Stack(name="A", children=[
        otio.schema.Track(kind="Video", children=[_clip("A", 0, 1000)]),
        otio.schema.Track(kind="Audio", children=[_clip("A.ch1", 0, 1000)]),
        otio.schema.Track(kind="Audio", children=[_clip("A.ch2", 0, 1000)]),
    ])
    b = otio.schema.Stack(name="B", children=[
        otio.schema.Track(kind="Video", children=[
            _gap(100), _clip("B1", 0, 300), _gap(50), _clip("B2", 0, 550),
        ]),
    ])
    rec = otio.schema.Stack(name="REC", children=[
        otio.schema.Track(kind="Audio", children=[_clip("REC", 0, 1000)]),
    ])
    mc = otio.schema.Multicam(
        name="Group", angles=[a, b, rec], global_start_time=RT(90000, 25)
    )
    tl = otio.schema.Timeline(name="edit")
    tl.set_multicams({"mc": mc})
    tl.tracks.append(otio.schema.Track(kind="Video", children=[
        _cut("A", 0, 38), _cut("B", 380, 40),
    ]))
    tl.tracks.append(otio.schema.Track(kind="Audio", children=[
        _cut("A", 0, 37, angle_track=1), _cut("REC", 37, 41),
    ]))
    return tl


class MulticamSchemaTest(unittest.TestCase, otio_test_utils.OTIOAssertions):

    def test_round_trip(self):
        tl = _timeline()
        text = otio.adapters.write_to_string(tl)
        back = otio.adapters.read_from_string(text)
        self.assertJsonEqual(tl, back)
        self.assertEqual(list(back.multicams()), ["mc"])
        mc = back.multicam("mc")
        self.assertIsInstance(mc, otio.schema.Multicam)
        self.assertIsInstance(mc, otio.schema.Stack)
        self.assertEqual(mc.angle_names(), ["A", "B", "REC"])
        self.assertEqual(mc.global_start_time, RT(90000, 25))
        self.assertEqual(mc.angle("B").name, "B")
        self.assertIsNone(mc.angle("nope"))
        cut = back.tracks[1][0]
        self.assertIsInstance(cut, otio.schema.MulticamClip)
        self.assertEqual(
            (cut.multicam, cut.angle, cut.angle_track), ("mc", "A", 1)
        )
        self.assertIs(back.multicam_for(cut), mc)

    def test_no_multicams_key_when_empty(self):
        text = otio.adapters.write_to_string(otio.schema.Timeline())
        self.assertNotIn("multicams", text)

    def test_angle_track_defaults_to_zero(self):
        text = otio.adapters.write_to_string(_cut("A", 0, 1))
        text = text.replace('"angle_track": 0,', "")
        self.assertEqual(otio.adapters.read_from_string(text).angle_track, 0)

    def test_available_range_needs_the_timeline(self):
        with self.assertRaises(otio.exceptions.CannotComputeAvailableRangeError):
            _cut("A", 0, 1).available_range()
        # trimmed_range works from source_range alone
        self.assertEqual(_cut("A", 5, 10).trimmed_range().duration, RT(10, 25))

    def test_track_duration(self):
        tl = _timeline()
        self.assertEqual(tl.tracks[0].duration(), RT(78, 25))
        self.assertEqual(tl.duration(), RT(78, 25))


class MulticamValidationTest(unittest.TestCase):

    def test_valid(self):
        self.assertEqual(otio.algorithms.validate_multicams(_timeline()), [])

    def test_missing_multicam_angle_and_track(self):
        tl = _timeline()
        tl.tracks[0].append(_cut("A", 0, 1, multicam="nope"))
        tl.tracks[0].append(_cut("Z", 0, 1))
        tl.tracks[1].append(_cut("A", 0, 1, angle_track=5))
        tl.tracks[0].append(_cut("REC", 0, 1))  # audio-only angle on video
        problems = otio.algorithms.validate_multicams(tl)
        self.assertEqual(len(problems), 4, problems)
        self.assertIn("no multicam with key 'nope'", problems[0])
        self.assertIn("has no angle 'Z'", problems[1])

    def test_duplicate_angle_names(self):
        tl = _timeline()
        tl.multicam("mc").append(otio.schema.Stack(name="A"))
        problems = otio.algorithms.validate_multicams(tl)
        self.assertTrue(any("duplicate angle names ['A']" in p for p in problems))

    def test_cycle(self):
        tl = _timeline()
        inner = otio.schema.Stack(name="loop", children=[
            otio.schema.Track(kind="Video", children=[_cut("A", 0, 10)]),
        ])
        tl.multicam("mc").append(inner)
        problems = otio.algorithms.validate_multicams(tl)
        self.assertIn("multicam 'mc' contains itself", problems)


class FlattenMulticamTest(unittest.TestCase):

    def _sig(self, track):
        return [
            (
                item.schema_name(),
                item.name if isinstance(item, otio.schema.Clip) else None,
                item.trimmed_range().start_time.value
                if isinstance(item, otio.schema.Clip) else None,
                item.duration().value,
            )
            for item in track
        ]

    def test_flatten(self):
        tl = _timeline()
        flat, report = otio.algorithms.flatten_multicam(tl)
        self.assertEqual(report, [])
        self.assertEqual(flat.multicams(), {})
        self.assertEqual(
            list(flat.find_children(descended_from_type=otio.schema.MulticamClip)),
            [],
        )
        # B at 380 for 40: B1 covers 100-400 (offset 280), gap 400-420
        self.assertEqual(self._sig(flat.tracks[0]), [
            ("Clip", "A", 0, 38),
            ("Clip", "B1", 280, 20),
            ("Gap", None, None, 20),
        ])
        self.assertEqual(self._sig(flat.tracks[1]), [
            ("Clip", "A.ch2", 0, 37),
            ("Clip", "REC", 37, 41),
        ])
        self.assertEqual(flat.duration(), tl.duration())
        # the original is untouched
        self.assertEqual(len(tl.multicams()), 1)
        meta = flat.tracks[0][0].metadata["otio.multicam"]["flattened_from"]
        self.assertEqual(meta["angle"], "A")

    def test_flatten_reports_unresolved_as_gap(self):
        tl = _timeline()
        tl.tracks[0].append(_cut("Z", 0, 12))
        flat, report = otio.algorithms.flatten_multicam(tl)
        self.assertEqual(len(report), 1)
        self.assertIn("replaced with a gap", report[0])
        self.assertEqual(self._sig(flat.tracks[0])[-1], ("Gap", None, None, 12))

    def test_flatten_keeps_effects_on_single_item(self):
        tl = _timeline()
        tl.tracks[0][0].effects.append(otio.schema.Effect(effect_name="Blur"))
        flat, _ = otio.algorithms.flatten_multicam(tl)
        self.assertEqual(flat.tracks[0][0].effects[0].effect_name, "Blur")

    def test_flatten_nested_multicam(self):
        tl = _timeline()
        quad = otio.schema.Multicam(name="Quad", angles=[
            otio.schema.Stack(name="Q", children=[
                otio.schema.Track(kind="Video", children=[
                    _cut("A", 0, 10), _cut("B", 120, 10),
                ]),
            ]),
        ])
        multicams = tl.multicams()
        multicams["quad"] = quad
        tl.set_multicams(multicams)
        tl.tracks[0].append(_cut("Q", 5, 10, multicam="quad"))
        self.assertEqual(otio.algorithms.validate_multicams(tl), [])
        flat, report = otio.algorithms.flatten_multicam(tl)
        self.assertEqual(report, [])
        self.assertEqual(self._sig(flat.tracks[0])[-2:], [
            ("Clip", "A", 5, 5),
            ("Clip", "B1", 20, 5),
        ])


if __name__ == "__main__":
    unittest.main()
