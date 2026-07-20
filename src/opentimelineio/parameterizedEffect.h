// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/effect.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

/// @brief An effect with a stable identity and a dictionary of typed
/// parameter values, suitable for interchange between host applications.
///
/// A ParameterizedEffect extends Effect with:
/// - a stable, host-independent identifier (e.g. an OpenFX plugin
///   identifier such as "com.acme-vfx.lensflare", or a generalized
///   effect name for host-native effects)
/// - the version of the effect that authored the parameter values
/// - the host application (and version) that authored the values
/// - the context the effect operates in (filter, transition, generator,
///   audio_filter, or audio_transition), mirroring OpenFX contexts
/// - a dictionary of parameter values keyed by the effect's stable
///   parameter script names
///
/// Parameter values are stored in an AnyDictionary. Scalar values
/// (bool, int64_t, double, std::string) are stored directly. Structured
/// values (2D points, colors, enumerations/choices) are stored as nested
/// AnyDictionary values carrying a "type" key describing their
/// interpretation. Animated (keyframed) parameter values are not yet
/// specified; see the OpenTimelineIO Effects schema proposal for the
/// planned evolution.
class OTIO_API_TYPE ParameterizedEffect : public Effect
{
public:
    /// @brief This struct provides the ParameterizedEffect schema.
    struct Schema
    {
        static auto constexpr name   = "ParameterizedEffect";
        static int constexpr version = 1;
    };

    using Parent = Effect;

    /// @brief Create a new parameterized effect.
    ///
    /// @param name The name of the effect object.
    /// @param effect_name The name of the effect.
    /// @param metadata The metadata for the effect.
    /// @param enabled Whether the effect is enabled.
    /// @param effect_id The stable, host-independent identifier for the
    /// effect (e.g. "com.acme-vfx.lensflare").
    /// @param effect_version The version of the effect.
    /// @param host The host application that authored the parameter values.
    /// @param host_version The version of the host application.
    /// @param context The context the effect operates in. One of "filter",
    /// "transition", "generator", "audio_filter", or "audio_transition".
    /// @param parameters The parameter values, keyed by stable parameter
    /// script name.
    OTIO_API ParameterizedEffect(
        std::string const&   name           = std::string(),
        std::string const&   effect_name    = std::string(),
        AnyDictionary const& metadata       = AnyDictionary(),
        bool                 enabled        = true,
        std::string const&   effect_id      = std::string(),
        std::string const&   effect_version = std::string(),
        std::string const&   host           = std::string(),
        std::string const&   host_version   = std::string(),
        std::string const&   context        = std::string(),
        AnyDictionary const& parameters     = AnyDictionary());

    /// @brief Return the stable identifier for the effect.
    std::string effect_id() const noexcept { return _effect_id; }

    /// @brief Set the stable identifier for the effect.
    void set_effect_id(std::string const& effect_id)
    {
        _effect_id = effect_id;
    }

    /// @brief Return the version of the effect.
    std::string effect_version() const noexcept { return _effect_version; }

    /// @brief Set the version of the effect.
    void set_effect_version(std::string const& effect_version)
    {
        _effect_version = effect_version;
    }

    /// @brief Return the host application that authored the values.
    std::string host() const noexcept { return _host; }

    /// @brief Set the host application that authored the values.
    void set_host(std::string const& host) { _host = host; }

    /// @brief Return the version of the host application.
    std::string host_version() const noexcept { return _host_version; }

    /// @brief Set the version of the host application.
    void set_host_version(std::string const& host_version)
    {
        _host_version = host_version;
    }

    /// @brief Return the context the effect operates in.
    std::string context() const noexcept { return _context; }

    /// @brief Set the context the effect operates in.
    void set_context(std::string const& context) { _context = context; }

    /// @brief Return the parameter values.
    AnyDictionary parameters() const noexcept { return _parameters; }

    /// @brief Return a reference to the parameter values.
    AnyDictionary& parameters() noexcept { return _parameters; }

protected:
    virtual ~ParameterizedEffect();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    std::string   _effect_id;
    std::string   _effect_version;
    std::string   _host;
    std::string   _host_version;
    std::string   _context;
    AnyDictionary _parameters;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
