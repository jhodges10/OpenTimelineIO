// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/multicam.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

Multicam::Multicam(
    std::string const&          name,
    std::optional<RationalTime> global_start_time,
    AnyDictionary const&        metadata)
    : Parent(name, std::nullopt, metadata)
    , _global_start_time(global_start_time)
{}

Multicam::~Multicam()
{}

std::string
Multicam::composition_kind() const
{
    static std::string kind = "Multicam";
    return kind;
}

Stack*
Multicam::angle(std::string const& name) const noexcept
{
    for (auto const& child: children())
    {
        if (auto stack = dynamic_cast<Stack*>(child.value))
        {
            if (stack->name() == name)
            {
                return stack;
            }
        }
    }
    return nullptr;
}

std::vector<std::string>
Multicam::angle_names() const
{
    std::vector<std::string> result;
    for (auto const& child: children())
    {
        if (auto stack = dynamic_cast<Stack*>(child.value))
        {
            result.push_back(stack->name());
        }
    }
    return result;
}

bool
Multicam::read_from(Reader& reader)
{
    return reader.read_if_present("global_start_time", &_global_start_time)
           && Parent::read_from(reader);
}

void
Multicam::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("global_start_time", _global_start_time);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
