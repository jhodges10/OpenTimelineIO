// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/parameterizedEffect.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

ParameterizedEffect::ParameterizedEffect(
    std::string const&   name,
    std::string const&   effect_name,
    AnyDictionary const& metadata,
    bool                 enabled,
    std::string const&   effect_id,
    std::string const&   effect_version,
    std::string const&   host,
    std::string const&   host_version,
    std::string const&   context,
    AnyDictionary const& parameters)
    : Parent(name, effect_name, metadata, enabled)
    , _effect_id(effect_id)
    , _effect_version(effect_version)
    , _host(host)
    , _host_version(host_version)
    , _context(context)
    , _parameters(parameters)
{}

ParameterizedEffect::~ParameterizedEffect()
{}

bool
ParameterizedEffect::read_from(Reader& reader)
{
    return reader.read_if_present("effect_id", &_effect_id)
           && reader.read_if_present("effect_version", &_effect_version)
           && reader.read_if_present("host", &_host)
           && reader.read_if_present("host_version", &_host_version)
           && reader.read_if_present("context", &_context)
           && reader.read_if_present("parameters", &_parameters)
           && Parent::read_from(reader);
}

void
ParameterizedEffect::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("effect_id", _effect_id);
    writer.write("effect_version", _effect_version);
    writer.write("host", _host);
    writer.write("host_version", _host_version);
    writer.write("context", _context);
    writer.write("parameters", _parameters);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
