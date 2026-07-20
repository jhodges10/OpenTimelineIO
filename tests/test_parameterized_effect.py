# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Unit tests for the ParameterizedEffect schema."""

import unittest

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils


class ParameterizedEffectTest(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_constructor(self):
        pe = otio.schema.ParameterizedEffect(
            name="pip",
            effect_name="Picture-in-Picture",
            metadata={"vendor": {"note": "example"}},
            enabled=True,
            effect_id="com.example.pip",
            effect_version="1.2.3",
            host="Resolve",
            host_version="19.0",
            context="video_filter",
            parameters={
                "scale": 0.73,
                "rotation": 37.0,
                "position": {
                    "type": "2D XY",
                    "x": -72.4465649,
                    "y": -43.875,
                },
                "border_color": {
                    "type": "color",
                    "red": 0.9,
                    "green": 0.8,
                    "blue": 0.2,
                },
                "motion_blur": True,
                "blend_mode": "Screen",
            },
        )
        self.assertEqual(pe.name, "pip")
        self.assertEqual(pe.effect_name, "Picture-in-Picture")
        self.assertEqual(pe.enabled, True)
        self.assertEqual(pe.effect_id, "com.example.pip")
        self.assertEqual(pe.effect_version, "1.2.3")
        self.assertEqual(pe.host, "Resolve")
        self.assertEqual(pe.host_version, "19.0")
        self.assertEqual(pe.context, "video_filter")
        self.assertEqual(pe.parameters["scale"], 0.73)
        self.assertEqual(pe.parameters["position"]["type"], "2D XY")
        self.assertEqual(pe.parameters["position"]["x"], -72.4465649)
        self.assertEqual(pe.parameters["border_color"]["green"], 0.8)
        self.assertEqual(pe.parameters["motion_blur"], True)
        self.assertEqual(pe.parameters["blend_mode"], "Screen")
        self.assertEqual(pe.metadata["vendor"]["note"], "example")

    def test_is_an_effect(self):
        pe = otio.schema.ParameterizedEffect()
        self.assertIsInstance(pe, otio.schema.Effect)

    def test_setters(self):
        pe = otio.schema.ParameterizedEffect()
        pe.effect_id = "com.example.blur"
        pe.effect_version = "2.0"
        pe.host = "Media Composer"
        pe.host_version = "2025.12"
        pe.context = "video_transition"
        pe.parameters["width"] = 50
        self.assertEqual(pe.effect_id, "com.example.blur")
        self.assertEqual(pe.effect_version, "2.0")
        self.assertEqual(pe.host, "Media Composer")
        self.assertEqual(pe.host_version, "2025.12")
        self.assertEqual(pe.context, "video_transition")
        self.assertEqual(pe.parameters["width"], 50)

    def test_serialize(self):
        pe = otio.schema.ParameterizedEffect(
            name="flare",
            effect_name="Lens Flare",
            effect_id="com.acme-vfx.lensflare",
            effect_version="1.2.3",
            host="Resolve",
            host_version="19.0",
            context="video_filter",
            parameters={"brightness": 1.0, "lens": "105mm Prime"},
        )
        encoded = otio.adapters.otio_json.write_to_string(pe)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertJsonEqual(pe, decoded)
        self.assertEqual(decoded.effect_id, "com.acme-vfx.lensflare")
        self.assertEqual(decoded.context, "video_filter")
        self.assertEqual(decoded.parameters["brightness"], 1.0)
        self.assertEqual(decoded.parameters["lens"], "105mm Prime")

    def test_attached_to_clip(self):
        cl = otio.schema.Clip(
            name="clip1",
            effects=[
                otio.schema.ParameterizedEffect(
                    name="pip",
                    effect_name="Picture-in-Picture",
                    effect_id="com.example.pip",
                    context="video_filter",
                    parameters={"scale": 0.5},
                )
            ],
        )
        encoded = otio.adapters.otio_json.write_to_string(cl)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertJsonEqual(cl, decoded)
        fx = decoded.effects[0]
        self.assertIsInstance(fx, otio.schema.ParameterizedEffect)
        self.assertEqual(fx.parameters["scale"], 0.5)

    def test_str_repr(self):
        pe = otio.schema.ParameterizedEffect(effect_id="com.example.pip")
        self.assertIn("ParameterizedEffect", str(pe))
        self.assertIn("com.example.pip", repr(pe))


if __name__ == '__main__':
    unittest.main()
