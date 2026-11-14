# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] - 2026-11-15

### Added

- `Config` object for advanced usage of `PlaneAbove`
- `to_dict()` and `to_json()` methods to `Above` object

### Changed

- `PlaneAbove` settings (such as user-agent, proxy, sources setup, etc.) are now passed via `config` parameter
- `ps_user_agent` parameter renamed to `user_agent` and is now shared across all requests
- `osn_proxy` parameter renamed to `proxy_url` and is now shared across selected sources in `proxy_scope`

### Deprecated

> [!IMPORTANT]
> Deprecated entities emit `DeprecationWarning` and will be removed in **v1.0.0**.

- Passing `route_sources`, `photo_sources`, `ps_user_agent`, `osn_proxy`, `osn_id` and `osn_secret` directly to `PlaneAbove` without `Config` object

## [0.5.1] - 2026-11-07

### Fixed

- Missing `airline` field in response could cause `flight` processing error
- Incorrect `Photo` attributes due to `flightdb.net` photo provider switch (closing [#8](https://github.com/wrongcredentials/plane-above/issues/8))

## [0.5.0] - 2026-10-31

### Added

- Fourth source to retrieve aircraft details

### Fixed

- Retrieving of `.photo.origin_url` from [adsbdb.com](https://github.com/mrjackwills/adsbdb/issues/92)
- Parsing of aircraft details from `flightdb.net` (closing [#6](https://github.com/wrongcredentials/plane-above/issues/6))

## [0.4.0] - 2026-10-18

### Changed

- Route lookup now queries all enabled providers concurrently and picks optimal result
- Routes with identical departure and destination may now be discarded by internal validation
- Reduced the number of unnecessary API calls during route lookup
- Requests to `airport-data.com` now include provided User-Agent header to avoid `HTTP 403`

### Fixed

- Parsing error when a flight has an empty callsign

## [0.3.0] - 2026-08-19

### Added

- Configurable `route_sources` and `photo_sources` parameters

### Changed

- `.aircraft.photos` returning list with `Photo` objects fetched from `photo_sources`

## [0.2.0] - 2026-08-11

### Added

- `.aircraft.country` _e.g. "Kingdom of the Netherlands"_
- `.aircraft.type_code` _e.g. "A35K"_
- `.aircraft.photos` returning list with `Photo` object _(currently limited to 1)_
- `.state.latitude` and `.state.longitude`

### Changed

- `Plane` renamed to `Above`
- `Route` renamed to `Flight`
- `.route` renamed to `.flight`
- `.callsign` moved to `.flight.callsign`
- `.icao24` moved to `.aircraft.icao24`

### Deprecated

> [!IMPORTANT]
> Deprecated entities emit `DeprecationWarning` and will be removed in **v1.0.0**.

- `Plane` and `Route` models
- `.route`, `.callsign`, `.country_code`, `.icao24` and `.photo` attributes

### Fixed

- Lock unavailable sources to prevent hitting timeouts constantly
- `.photo.image_url` and `.photo.origin_url` might point to different photos in some cases

## [0.1.1] - 2026-08-03

### Fixed

- Explicit timeouts in http calls

## [0.1.0] - 2026-08-03

### Added

- Initial release

[0.6.0]: https://github.com/wrongcredentials/plane-above/releases/tag/v0.6.0
[0.5.1]: https://github.com/wrongcredentials/plane-above/releases/tag/v0.5.1
[0.5.0]: https://github.com/wrongcredentials/plane-above/releases/tag/v0.5.0
[0.4.0]: https://github.com/wrongcredentials/plane-above/releases/tag/v0.4.0
[0.3.0]: https://github.com/wrongcredentials/plane-above/releases/tag/v0.3.0
[0.2.0]: https://github.com/wrongcredentials/plane-above/releases/tag/v0.2.0
[0.1.1]: https://github.com/wrongcredentials/plane-above/releases/tag/v0.1.1
[0.1.0]: https://github.com/wrongcredentials/plane-above/releases/tag/v0.1.0
