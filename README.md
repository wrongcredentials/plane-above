<h1></h1>
<p align="center"><img src="https://raw.githubusercontent.com/wrongcredentials/plane-above/v0.1.1/logo.svg" alt="plane-above" width="160"></p>
<h1 align="center">Plane Above</h1>
<p align="center"><i>What’s flying up there, huh?</i></p>

<div align="center">

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://pypi.org/project/plane-above/)
[![Pypi](https://img.shields.io/pypi/v/plane-above.svg)](https://pypi.org/project/plane-above/)
[![License](https://img.shields.io/pypi/l/plane-above.svg)](https://github.com/wrongcredentials/plane-above/blob/main/LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

</div>

## About

🛩 Plane Above is a Python package featuring a convenient way to retrieve _planes_ above a given point.
> [!NOTE]
> In this document I would refer to any flying object as an _«aircraft»_ or _«plane»_,
> but keep in mind that it also includes helicopters, gliders, rotorcraft and even hot air balloons.

<details>
  <summary>One notable usage example...</summary>

  Try <a href="https://t.me/plane_above_bot">Plane Above</a> telegram bot.
  <img src="https://raw.githubusercontent.com/wrongcredentials/plane-above/v0.1.1/tg.png" alt="tg-bot" width="400">
</details>

## Before we start

To collect data, this project uses several third-party sources, including public APIs and
enthusiast-maintained services. Please use them responsibly: don't push rate limits, and take care when using them so
these sources remain available for everyone.

Keep in mind that returned data may be missing, incorrect, outdated, or temporarily unavailable. The project does not
claim ownership of third-party data, and each source may have its own terms regarding how its data can be stored,
shared, or reused. Before doing anything beyond simple lookups for educational purposes, please review the terms
that apply to each source (see [data sources](#data-sources) for details).

## How it works

#### 1. BUILD SEARCHING AREA

Using the given latitude and longitude, it builds a search area by calculating bounding box coordinates
based on requested distance from the point.

#### 2. RETRIEVE STATES

Next, it makes a request to OpenSky API to retrieve states within the search area.
Each state represents [state vector](https://openskynetwork.github.io/opensky-api/index.html#state-vectors)
and contains information of ADS-B messages from transponder installed in aircraft.

#### 3. PICK DATA

After receiving the state vectors, provided that the request was successful, the rate limits were not exceeded,
and at least one state was returned, it extracts the required fields and filters out irrelevant entries: for instance
objects that are on ground will be discarded. At this point we already have some valuable data such as transponder
hex code and flight callsign, along with reported altitude, velocity and coordinates.

#### 4. FETCH DETAILS

Based on previous step we enrich the data by making requests to multiple sources to retrieve information about aircraft
like manufacturer, model, age (based on year of manufacture), photo and some others.
At the same time it fetches flight route by sending multiple requests as well to receive information about departure,
destination and for some cases midpoint airports.

#### 5. COLLECT RESULT

This is the last step where all data are being collected and returned in [declared format](#object-reference).

## Installation

```bash
pip install plane-above
```

## Quickstart

First, import library, create instance and pass your values of latitude & longitude as a tuple:

```pycon
>>> from plane_above import PlaneAbove
>>> pa = PlaneAbove((52.4573212, 5.5301535))
```

Optionally, you can pass a distance attribute (_in km, 15 by default_):

```pycon
>>> pa = PlaneAbove((52.4573212, 5.5301535), distance=20)
```

At this point, we can check what is happening _above_:

```pycon
>>> pa.spotted.success
True
>>> pa.spotted.how_many
2
```

In cases when there are no planes detected, or retrieving information fails you will get `True, 0` and `False, 0`
respectively. Let's go further and see what are these _2 flying objects_:

```pycon
>>> for above in pa.fetch():
...     print(
...         f"{above.aircraft.manufacturer} {above.aircraft.model} flying to "
...         f"{above.flight.destination.name} is {above.state.altitude} meters above you!"
...     )

Boeing 777 212ER flying to London Heathrow Airport is 11232 meters above you!
Airbus A330 342 flying to Brussels Airport (Zaventem Airport) is 1006 meters above you!
```

> [!TIP]
> If you use asynchronous environment, call `async_fetch()` instead:
>
>```text
> async for above in pa.async_fetch():
>    ...
>```

## Object Reference

Both `fetch()` and `async_fetch()` methods will return an iterator consisting of `Above` objects.
<details>
  <summary>Above</summary>

```python
class Above:
    aircraft: Aircraft
    flight: Flight
    state: State
```

</details>

<details>
  <summary>Aircraft</summary>

```python
class Aircraft:
    icao24: str  # Hex code of the transponder installed in the aircraft.
    country: str  # Country inferred from the aircraft's transponder address.
    age: float  # Don’t take 0.0 as a brand new plane; age likely was missing from our sources.
    photos: list[Photo]
    registration: str = ""
    manufacturer: str = ""
    model: str = ""
    type_code: str = ""  # ICAO type code.
    operator: str = ""
```

</details>

<details>
  <summary>Photo</summary>

```python
class Photo:
    image_url: str = ""
    origin_url: str = ""
    photographer: str = ""
```

</details>

<details>
  <summary>Flight</summary>

```python
class Flight:
    callsign: str  # Might be empty string if not received.
    departure: Airport
    destination: Airport
    stops: list[Airport]  # Usually empty; only a small percentage of routes include stops.
    airline: str = ""  # Airline performing flight; May differ from aircraft.operator.
```

</details>

<details>
  <summary>Airport</summary>

```python
class Airport:
    iata: str = "N/A"
    name: str = "Unknown airport"  # May be "Unknown departure" or "Unknown destination" when no route is found.
    country_code: str = "UN"  # ISO2 code (NL, KR, BR...).
```

</details>

<details>
  <summary>State</summary>

```python
class State:
    altitude: int  # Geometric altitude in meters. Can be below zero.
    velocity: int  # Ground speed in m/s. Can be zero.
    latitude: float | None = None  # WGS-84 latitude in decimal degrees.
    longitude: float | None = None  # WGS-84 longitude in decimal degrees.
```

</details>

## Limitations & Workarounds

### Sources Setup

By default, only sources without severe usage restrictions are queried, resulting in some data for `Route` and `Photo`
being excluded. You can review and enable each source manually using `RouteSource` and `PhotoSource`:

> [!WARNING]
> By including a source, you confirm that you have read and agree to its terms
> (see [sources](#sources) below for details).

```python
from plane_above import RouteSource, PhotoSource

route_sources = (RouteSource.HX, RouteSource.SB)
photo_sources = (PhotoSource.HX, PhotoSource.AD, PhotoSource.PS)

PlaneAbove((52.4573212, 5.5301535), route_sources=route_sources, photo_sources=photo_sources)
```

You can skip direct calls to photo sources entirely for performance or liability reasons and still receive photos
(if available) when requesting aircraft details:

```python
PlaneAbove((52.4573212, 5.5301535), photo_sources=())
```

### Planespotters.net Additional Requirement

This photo source has a strict policy about making requests with
[unique and descriptive user-agents](https://www.planespotters.net/photo/api). That's doable with an extra param:

```python
PlaneAbove((52.4573212, 5.5301535), ps_user_agent="YourApp/1.0 (+https://example.com/contact)")
```

Even if `PhotoSource.PS` is enabled in `photo_sources`, requests won't be processed without a valid `ps_user_agent`.
Other photo sources are unaffected.

### OpenSky Network Authentication

OSN allows to use its API anonymously, but with limits.
If you wish to extend your usage - consider obtaining `client_id` and  `client_secret`
[here](https://openskynetwork.github.io/opensky-api/rest.html#authentication). Then you pass extra params:

```python
PlaneAbove((52.4573212, 5.5301535), osn_id="your_client_id", osn_secret="your_client_secret")
```

### OpenSky Network Timeouts

In some cases your calls to OSN might be timed-out without any specific reason. That's due to their
blocking policies and you probably would like to utilize proxy here as a workaround:

```python
PlaneAbove((52.4573212, 5.5301535), osn_proxy="http://username:password@host:port")
```

Please note that this will be used for making an OSN request only; other sources won't be called with that proxy.

## Data sources

### General terms

This project aggregates data from multiple third-party services and does not claim ownership of any data returned
by those services. The specific terms, restrictions, and licence conditions vary by source. Users must review and comply
with the terms applicable to each source before storing, publishing, redistributing, exporting, or incorporating
returned data into another database.

None of the sources we use guarantee the accuracy, timeliness, or completeness of their data, and use of each is at
the user's own risk. This project is not affiliated with, endorsed by, or responsible for the content, availability,
or practices of the third-party services it queries. Users must not use this project, or the sources it queries,
unlawfully or in any way that could damage, disable, or impair the underlying services.

### Sources

* Flying objects in area: [opensky-network.org](https://opensky-network.org/)
* Aircraft data and photos; route and airport details:
  [hexdb.io](https://hexdb.io/)
* Aircraft data; route and airport details:
  [adsbdb.com](https://www.adsbdb.com/)
* Aircraft photos; airport details:
  [airport-data.com](https://airport-data.com/)
* Aircraft data: [flightdb.net](https://flightdb.net/)
* Aircraft photos: [planespotters.net](https://www.planespotters.net/)

### Route data notice

> The flight route data is the work of David Taylor, Edinburgh and Jim Mason, Glasgow, and may not be copied,
> published, or incorporated into other databases without the explicit permission of David J Taylor, Edinburgh.

This notice applies specifically to flight route data obtained via [adsbdb](https://www.adsbdb.com/) (_excluded by default and requires
manual enabling_), and is reproduced here for transparency and attribution purposes only. It does not constitute
permission, and no such permission is granted or implied by this project.

### Photo data notice

This project does not intentionally download or persist image files. It may return photo metadata and image URLs
provided by third-party photo sources. Image use is subject to the terms and attribution requirements of the
respective source.
