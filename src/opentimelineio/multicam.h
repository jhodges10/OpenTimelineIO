// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/stack.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

/// @brief A multicam definition: a set of synced angles, held once on a
/// Timeline (see Timeline::multicams) and played by MulticamClip items.
///
/// Each child is a Stack representing one angle. The angle Stack's name is
/// its identity and must be unique within the multicam. An angle holds at
/// most one video Track and any number of audio Tracks, all on the
/// multicam's own time.
///
/// EXPERIMENTAL: prototype for OTIO issue #427, not an approved schema.
class OTIO_API_TYPE Multicam : public Stack
{
public:
    /// @brief This struct provides the Multicam schema.
    struct Schema
    {
        static auto constexpr name   = "Multicam";
        static int constexpr version = 1;
    };

    using Parent = Stack;

    /// @brief Create a new multicam.
    ///
    /// @param name The name of the multicam.
    /// @param global_start_time Source timecode at multicam time zero.
    /// @param metadata The metadata for the multicam.
    OTIO_API Multicam(
        std::string const&          name              = std::string(),
        std::optional<RationalTime> global_start_time = std::nullopt,
        AnyDictionary const&        metadata          = AnyDictionary());

    /// @brief Return the source timecode at multicam time zero.
    std::optional<RationalTime> global_start_time() const noexcept
    {
        return _global_start_time;
    }

    /// @brief Set the source timecode at multicam time zero.
    void
    set_global_start_time(std::optional<RationalTime> const& global_start_time)
    {
        _global_start_time = global_start_time;
    }

    /// @brief Return the angle Stack with this name, or null.
    OTIO_API Stack* angle(std::string const& name) const noexcept;

    /// @brief Return the angle names in display order.
    OTIO_API std::vector<std::string> angle_names() const;

protected:
    virtual ~Multicam();

    std::string composition_kind() const override;

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    std::optional<RationalTime> _global_start_time;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
