# Writing an OTIO Effects Linker

```{note}
Effects linkers, `Effect.2` and `Transition.2` are a prototype of the
OpenTimelineIO effects schema proposal. They are not part of a released
version of OTIO and may change as the proposal is discussed.
```

OpenTimelineIO Effects Linkers are plugins that rewrite effects after an
adapter reads a file. They work the way [media linkers](write-a-media-linker)
do, but for effects. A typical one turns host-native effects (a Premiere
"Gaussian Blur", an Avid "Blur Effect") into the shared `otio.fx.*` registry
vocabulary, or into a studio's own effect ids, so that every adapter does not
have to know every host's effects.

An effects linker can be named in the call to `otio.adapters.read_from_file`
or set by an environment variable. When neither is set, nothing runs.

```python
import opentimelineio as otio

timeline = otio.adapters.read_from_file(
    "something.xml",
    effects_linker_name="otio_fx_registry",
)
```

## When it runs

Reading a file runs these steps in order:

1. The adapter reads the file.
2. The `post_adapter_read` hook.
3. The media linker.
4. The `post_media_linker` hook.
5. The effects linker.
6. The `post_effects_linker` hook, passed the effects linker argument map.

The linker visits every effect in the result: each entry of an Item's
`effects` (clips, gaps, tracks and stacks) and each Transition's `effect`.

## Registering Your Effects Linker

Write a file `myeffectslinker.py` and add a manifest that points at it:

```json
{
    "OTIO_SCHEMA" : "PluginManifest.1",
    "effects_linkers" : [
        {
            "OTIO_SCHEMA" : "EffectsLinker.1",
            "name" : "awesome_studios_effects_linker",
            "filepath" : "myeffectslinker.py"
        }
    ]
}
```

Add the manifest to your {term}`OTIO_PLUGIN_MANIFEST_PATH` environment
variable. To make it the default effects linker, set
{term}`OTIO_DEFAULT_EFFECTS_LINKER`:

```bash
export OTIO_DEFAULT_EFFECTS_LINKER="awesome_studios_effects_linker"
```

To skip effects linking for one read, pass
`effects_linker_name=otio.effects_linker.EffectsLinkingPolicy.DoNotLinkEffects`.

## Writing an Effects Linker

An effects linker is a python file with a `link_effect` function. It takes
the effect, the Item or Transition that holds it (`parent`), and the argument
map passed to the read call. Return an effect to put in its place, or `None`
to keep the original. A linker never removes an effect.

```python
def link_effect(in_effect, parent, effects_linker_argument_map):
    if in_effect.effect_name != "Acme Glow":
        return None

    original = {
        "effect_id": in_effect.effect_id,
        "effect_version": in_effect.effect_version,
        "parameters": dict(in_effect.parameters),
        "linker": "awesome_studios_effects_linker",
    }
    in_effect.metadata["otio.fx"] = {
        "linked_from": original,
        "fidelity": "approximate",
    }
    in_effect.effect_id = "com.awesome-studios.glow"
    in_effect.effect_version = "2.1"
    in_effect.context = "filter"
    return in_effect
```

A linker should leave `host` and `host_version` alone, since the effect still
came from that host. It should also keep what it replaced in
`metadata["otio.fx"]["linked_from"]`, so a writer for the original host can
still round-trip the effect.

## The registry linker

OTIO ships one effects linker, `otio_fx_registry`. It applies a data-driven
mapping table, `otio_fx_registry.json`, that maps native effects onto the
`otio.fx.*` registry. It is never the default, so it runs only when named or
set in {term}`OTIO_DEFAULT_EFFECTS_LINKER`. Pass `registry_path` in the effects
linker argument map to use your own table:

```python
timeline = otio.adapters.read_from_file(
    "something.xml",
    effects_linker_name="otio_fx_registry",
    effects_linker_argument_map={"registry_path": "/studio/fx_registry.json"},
)
```

Each mapping names a registry entry, a `match`, an optional `fidelity` and an
optional `parameter_map`:

```json
{
    "effect_id": "otio.fx.gaussian_blur",
    "match": {"effect_name": "Gaussian Blur", "metadata_key": "fcp_xml"},
    "fidelity": "approximate",
    "parameter_map": {"amount": {"from": "radius", "scale": 0.01}}
}
```

`effect_id`, `effect_name` and `host` in `match` compare equal, and
`metadata_key` requires that key in the effect's metadata. Parameters start
from the registry entry's defaults, and `parameter_map` copies native values
across, scaling numbers by `scale` and adding `offset`. The linker skips
retimes and effects that already carry an `otio.fx.*` id.
