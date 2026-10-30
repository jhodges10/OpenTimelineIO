# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Reference effects linker for the ``otio.fx.*`` common effect registry.

Rewrites host-native effects into registry effects using the mapping table in
``otio_fx_registry.json``, which ships beside this file. Pass
``registry_path`` in the effects linker argument map to use another table.

Each mapping names a registry ``effect_id``, a ``match`` (all of whose keys
must hold), an optional ``fidelity`` and an optional ``parameter_map``:

.. code-block:: json

    {
        "effect_id": "otio.fx.gaussian_blur",
        "match": {"effect_name": "Gaussian Blur", "metadata_key": "fcp_xml"},
        "fidelity": "approximate",
        "parameter_map": {"amount": {"from": "radius", "scale": 0.01}}
    }

Match keys: ``effect_id``, ``effect_name`` and ``host`` compare equal;
``metadata_key`` requires that key in the effect's metadata.

A linked effect keeps what it was in ``metadata["otio.fx"]["linked_from"]``,
so a writer for the original host can still round-trip it.
"""

import json
import numbers
import os

from .. import schema

LINKER_NAME = "otio_fx_registry"
REGISTRY_PREFIX = "otio.fx."
DEFAULT_REGISTRY_PATH = os.path.join(
    os.path.dirname(__file__),
    "otio_fx_registry.json"
)

_registry_cache = {}


def load_registry(path=None):
    """Return the registry document at path (default: the bundled one)."""

    path = path or DEFAULT_REGISTRY_PATH
    if path not in _registry_cache:
        with open(path, encoding="utf-8") as fo:
            _registry_cache[path] = json.load(fo)
    return _registry_cache[path]


def _matches(match, effect):
    for key, expected in match.items():
        if key == "metadata_key":
            if expected not in effect.metadata:
                return False
        elif key in ("effect_id", "effect_name", "host"):
            if getattr(effect, key) != expected:
                return False
        else:
            # an unknown match key never holds, so a newer table cannot
            # silently match more than it means to
            return False
    return True


def _mapped_parameters(entry, mapping, effect):
    parameters = {}
    for parameter in entry.get("parameters", []):
        if "default" in parameter:
            parameters[parameter["key"]] = parameter["default"]

    for std_key, rule in mapping.get("parameter_map", {}).items():
        native_key = rule.get("from", std_key)
        if native_key not in effect.parameters:
            continue
        value = effect.parameters[native_key]
        if isinstance(value, numbers.Number) and not isinstance(value, bool):
            value = value * rule.get("scale", 1.0) + rule.get("offset", 0.0)
        parameters[std_key] = value

    return parameters


def link_effect(in_effect, parent, effects_linker_argument_map):
    """Map a host-native effect onto its ``otio.fx`` registry entry.

    Leaves retimes (:class:`.TimeEffect`), effects already in the registry
    and effects no mapping matches alone.
    """

    if isinstance(in_effect, schema.TimeEffect):
        return None
    if in_effect.effect_id.startswith(REGISTRY_PREFIX):
        return None

    registry = load_registry(
        (effects_linker_argument_map or {}).get("registry_path")
    )
    mapping = next(
        (
            m for m in registry.get("mappings", [])
            if _matches(m.get("match", {}), in_effect)
        ),
        None
    )
    if mapping is None:
        return None

    entry = next(
        (
            e for e in registry.get("effects", [])
            if e["effect_id"] == mapping["effect_id"]
        ),
        None
    )
    if entry is None:
        return None

    parameters = _mapped_parameters(entry, mapping, in_effect)

    otio_fx = dict(in_effect.metadata.get("otio.fx", {}))
    otio_fx["linked_from"] = {
        "effect_id": in_effect.effect_id,
        "effect_version": in_effect.effect_version,
        "parameters": dict(in_effect.parameters),
        "linker": LINKER_NAME,
    }
    otio_fx["fidelity"] = mapping.get("fidelity", "approximate")
    in_effect.metadata["otio.fx"] = otio_fx

    in_effect.effect_id = entry["effect_id"]
    in_effect.effect_version = entry["effect_version"]
    in_effect.parameters.clear()
    in_effect.parameters.update(parameters)
    if not in_effect.context:
        in_effect.context = entry["context"]

    return in_effect
