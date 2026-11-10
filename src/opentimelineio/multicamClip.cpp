// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/multicamClip.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

MulticamClip::MulticamClip(
    std::string const&              name,
    std::string const&              multicam,
    std::string const&              angle,
    int                             angle_track,
    std::optional<TimeRange> const& source_range,
    AnyDictionary const&            metadata,
    std::vector<Effect*> const&     effects,
    std::vector<Marker*> const&     markers)
    : Parent(name, source_range, metadata, effects, markers)
    , _multicam(multicam)
    , _angle(angle)
    , _angle_track(angle_track)
{}

MulticamClip::~MulticamClip()
{}

TimeRange
MulticamClip::available_range(ErrorStatus* error_status) const
{
    if (error_status)
    {
        *error_status = ErrorStatus(
            ErrorStatus::CANNOT_COMPUTE_AVAILABLE_RANGE,
            "A MulticamClip's available range comes from its Multicam; "
            "resolve it through Timeline::multicam_for()",
            this);
    }
    return TimeRange();
}

bool
MulticamClip::read_from(Reader& reader)
{
    int64_t angle_track = _angle_track;
    bool    ok          = reader.read("multicam", &_multicam)
              && reader.read("angle", &_angle)
              && reader.read_if_present("angle_track", &angle_track)
              && Parent::read_from(reader);
    _angle_track = static_cast<int>(angle_track);
    return ok;
}

void
MulticamClip::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("multicam", _multicam);
    writer.write("angle", _angle);
    writer.write("angle_track", int64_t(_angle_track));
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
