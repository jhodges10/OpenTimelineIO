// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/timeline.h"
#include "opentimelineio/clip.h"
#include "opentimelineio/multicamClip.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

Timeline::Timeline(
    std::string const&          name,
    std::optional<RationalTime> global_start_time,
    AnyDictionary const&        metadata)
    : SerializableObjectWithMetadata(name, metadata)
    , _global_start_time(global_start_time)
    , _tracks(new Stack("tracks"))
{}

Timeline::~Timeline()
{}

void
Timeline::set_tracks(Stack* stack)
{
    _tracks = stack ? stack : new Stack("tracks");
}

void
Timeline::set_multicams(Multicams const& multicams)
{
    _multicams.clear();
    for (auto const& m: multicams)
    {
        if (m.second)
        {
            _multicams[m.first] = m.second;
        }
    }
}

Multicam*
Timeline::multicam(std::string const& key) const noexcept
{
    auto found = _multicams.find(key);
    return found == _multicams.end() ? nullptr : found->second.value;
}

Multicam*
Timeline::multicam_for(MulticamClip const* multicam_clip) const noexcept
{
    return multicam_clip ? multicam(multicam_clip->multicam()) : nullptr;
}

bool
Timeline::read_from(Reader& reader)
{
    return reader.read("tracks", &_tracks)
           && reader.read_if_present("global_start_time", &_global_start_time)
           && reader.read_if_present("multicams", &_multicams)
           && Parent::read_from(reader);
}

void
Timeline::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("global_start_time", _global_start_time);
    writer.write("tracks", _tracks);
    if (!_multicams.empty())
    {
        writer.write("multicams", _multicams);
    }
}

std::vector<Track*>
Timeline::video_tracks() const
{
    std::vector<Track*> result;
    for (auto c: _tracks->children())
    {
        if (auto t = dynamic_retainer_cast<Track>(c))
        {
            if (t->kind() == Track::Kind::video)
            {
                result.push_back(t);
            }
        }
    }
    return result;
}

std::vector<Track*>
Timeline::audio_tracks() const
{
    std::vector<Track*> result;
    for (auto c: _tracks->children())
    {
        if (auto t = dynamic_retainer_cast<Track>(c))
        {
            if (t->kind() == Track::Kind::audio)
            {
                result.push_back(t);
            }
        }
    }
    return result;
}

std::vector<SerializableObject::Retainer<Clip>>
Timeline::find_clips(
    ErrorStatus*                    error_status,
    std::optional<TimeRange> const& search_range,
    bool                            shallow_search) const
{
    return _tracks.value->find_clips(
        error_status,
        search_range,
        shallow_search);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
