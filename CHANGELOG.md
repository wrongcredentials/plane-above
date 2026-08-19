# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.3.0]: https://github.com/wrongcredentials/plane-above/releases/tag/v0.3.0
[0.2.0]: https://github.com/wrongcredentials/plane-above/releases/tag/v0.2.0
[0.1.1]: https://github.com/wrongcredentials/plane-above/releases/tag/v0.1.1
[0.1.0]: https://github.com/wrongcredentials/plane-above/releases/tag/v0.1.0
