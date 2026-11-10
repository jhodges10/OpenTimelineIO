// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/item.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

/// @brief One cut to one angle of a Multicam, on one track.
///
/// The OTIO counterpart of AAF's Selector and FCPXML's mc-clip. The
/// multicam is named by its key in Timeline::multicams; the source range is
/// in multicam time. On an audio track, angle_track picks which of the
/// angle's audio tracks plays (counting audio tracks only); on a video
/// track it counts video tracks.
///
/// A MulticamClip cannot find its Multicam on its own (items do not know
/// their Timeline), so available_range() fails unless resolved through
/// Timeline::multicam_for(). Cuts should always carry a source_range.
///
/// EXPERIMENTAL: prototype for OTIO issue #427, not an approved schema.
class OTIO_API_TYPE MulticamClip : public Item
{
public:
    /// @brief This struct provides the MulticamClip schema.
    struct Schema
    {
        static auto constexpr name   = "MulticamClip";
        static int constexpr version = 1;
    };

    using Parent = Item;

    /// @brief Create a new multicam clip.
    ///
    /// @param name The name of the cut.
    /// @param multicam The key of the multicam in Timeline::multicams.
    /// @param angle The name of the live angle.
    /// @param angle_track Which track of that angle, counting only tracks
    /// of this item's track kind.
    /// @param source_range The range of the multicam played, in multicam time.
    /// @param metadata The metadata for the cut.
    OTIO_API MulticamClip(
        std::string const&              name         = std::string(),
        std::string const&              multicam     = std::string(),
        std::string const&              angle        = std::string(),
        int                             angle_track  = 0,
        std::optional<TimeRange> const& source_range = std::nullopt,
        AnyDictionary const&            metadata     = AnyDictionary(),
        std::vector<Effect*> const&     effects      = std::vector<Effect*>(),
        std::vector<Marker*> const&     markers      = std::vector<Marker*>());

    std::string multicam() const noexcept { return _multicam; }
    void set_multicam(std::string const& multicam) { _multicam = multicam; }

    std::string angle() const noexcept { return _angle; }
    void        set_angle(std::string const& angle) { _angle = angle; }

    int  angle_track() const noexcept { return _angle_track; }
    void set_angle_track(int angle_track) { _angle_track = angle_track; }

    TimeRange
    available_range(ErrorStatus* error_status = nullptr) const override;

protected:
    virtual ~MulticamClip();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    std::string _multicam;
    std::string _angle;
    int         _angle_track;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
