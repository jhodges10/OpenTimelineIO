# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.ParameterizedEffect)
def __str__(self):
    return (
        "ParameterizedEffect("
        "{}, "
        "{}, "
        "{}, "
        "{}, "
        "{}, "
        "{}, "
        "{}, "
        "{}, "
        "{}, "
        "{}"
        ")".format(
            str(self.name),
            str(self.effect_name),
            str(self.metadata),
            str(self.enabled),
            str(self.effect_id),
            str(self.effect_version),
            str(self.host),
            str(self.host_version),
            str(self.context),
            str(self.parameters),
        )
    )


@add_method(_otio.ParameterizedEffect)
def __repr__(self):
    return (
        "otio.schema.ParameterizedEffect("
        "name={}, "
        "effect_name={}, "
        "metadata={}, "
        "enabled={}, "
        "effect_id={}, "
        "effect_version={}, "
        "host={}, "
        "host_version={}, "
        "context={}, "
        "parameters={}"
        ")".format(
            repr(self.name),
            repr(self.effect_name),
            repr(self.metadata),
            repr(self.enabled),
            repr(self.effect_id),
            repr(self.effect_version),
            repr(self.host),
            repr(self.host_version),
            repr(self.context),
            repr(self.parameters),
        )
    )
