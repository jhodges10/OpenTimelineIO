// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/serializableObjectWithMetadata.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

/// @brief An effect that can be applied to an item, such as an image or audio filter.
///
/// Version 2 adds a stable identity, provenance and typed parameter values
/// for interchange between hosts:
/// - effect_id: a stable, host-independent identifier, such as an OpenFX
///   plugin identifier ("com.acme-vfx.lensflare") or an "otio.fx.*"
///   registry id
/// - effect_version: the version of the effect that wrote the values
/// - host, host_version: the application that wrote the values
/// - context: empty, or one of "filter", "transition" or "generator"
/// - parameters: values keyed by the effect's stable parameter names.
///   Scalars are stored directly; structured values (points, colors,
///   curves) are dictionaries carrying a "type" key.
///
/// An Effect with these fields empty is exactly a version 1 effect.
class OTIO_API_TYPE Effect : public SerializableObjectWithMetadata
{
public:
    /// @brief This struct provides the Effect schema.
    struct Schema
    {
        static auto constexpr name   = "Effect";
        static int constexpr version = 2;
    };

    using Parent = SerializableObjectWithMetadata;

    /// @brief Create a new effect.
    ///
    /// @param name The name of the effect object.
    /// @param name The name of the effect.
    /// @param metadata The metadata for the clip.
    /// @param enabled Whether the effect is enabled.
    /// @param effect_id The stable identifier of the effect.
    /// @param effect_version The version of the effect.
    /// @param host The host application that wrote the parameter values.
    /// @param host_version The version of the host application.
    /// @param context Empty, or one of "filter", "transition", "generator".
    /// @param parameters The parameter values, keyed by stable name.
    OTIO_API Effect(
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

    /// @brief Return the effect name.
    std::string effect_name() const noexcept { return _effect_name; }

    /// @brief Set the effect name.
    void set_effect_name(std::string const& effect_name)
    {
        _effect_name = effect_name;
    }

    /// @brief Return whether the effect is enabled.
    bool enabled() const { return _enabled; };

    /// @brief Set whether the effect is enabled.
    void set_enabled(bool enabled) { _enabled = enabled; }

    /// @brief Return the stable identifier of the effect.
    std::string effect_id() const noexcept { return _effect_id; }

    /// @brief Set the stable identifier of the effect.
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

    /// @brief Return the host application that wrote the parameter values.
    std::string host() const noexcept { return _host; }

    /// @brief Set the host application that wrote the parameter values.
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
    virtual ~Effect();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    std::string   _effect_name;
    bool          _enabled;
    std::string   _effect_id;
    std::string   _effect_version;
    std::string   _host;
    std::string   _host_version;
    std::string   _context;
    AnyDictionary _parameters;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
