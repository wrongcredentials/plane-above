<img src="https://raw.githubusercontent.com/wrongcredentials/plane-above/v0.1.1/logo.svg" alt="plane-above" width="170">

# Plane Above
[![PyPI version](https://img.shields.io/pypi/v/plane-above.svg)](https://pypi.org/project/plane-above/)
[![License](https://img.shields.io/pypi/l/plane-above.svg)](https://pypi.org/project/plane-above/)
[![Python versions](https://img.shields.io/pypi/pyversions/plane-above.svg)](https://pypi.org/project/plane-above/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

🛩 Plane Above is a python package featuring a convinient way to retrieve planes above certain point.

<details>
  <summary>One notable usage example...</summary>

  Try <a href="https://t.me/plane_above_bot">Plane Above</a> telegram bot.
  <img src="https://raw.githubusercontent.com/wrongcredentials/plane-above/v0.1.1/tg.png" alt="tg-bot" width="400">
</details>

## Before we start...
To collect data, this library utilizes various sources. They are open and maintained by enthusiasts mostly.
So, use responsively! Don't push the limits and take actions with care.
Please mind that data might be missing, incorrect or outdated.

## How it works
_Note: here and after I would refer to any flying object as an «aircraft» or «plane»,
but keep in mind that it also includes helicopters, gliders, rotorcraft and even balloons._
#### 1. BUILD SEARCHING AREA
With given latitude and longitude of point  it builds area of search by calculating bounding box coordinates
based on required distance from point.
#### 2. RETRIEVE STATES
Next it makes a request to OpenSky API to retrieve all states in searching area.
Each state represents [state vector](https://openskynetwork.github.io/opensky-api/index.html#state-vectors)
and contains information of ADS-B messages from transponder installed in aircraft.
#### 3. PICK DATA
After receiving states (if request was successful, we did not exceed limits and received at least one state)
it picks crucial data and filters out excessive entries: for instance objects that are on ground will be discarded.
At this point we already have some valuable data such as transponder hex code and flight callsign,
along with registered altitude and velocity.
#### 4. FETCH DETAILS
Based on previous step we enrich the data by making requests to multiple sources to retrieve information about aircraft
such as: registration code, manufacturer and model, age (based on built date) and operating airline/registered owner.
It continues with the route and send multiple requests as well to receive information about departure,
destination and for some cases midpoint airports. Finally, it searches for the aircraft photo.
#### 5. BUILD RESULT
This is the last step where all data being returned in declared format.

## Installation
```bash
pip install plane-above
```

## Usage
First, import library, create instance and pass your values of latitude & longitude as a tuple:
```python
>>> from plane_above import PlaneAbove
>>> pa = PlaneAbove((52.4573212, 5.5301535))
```
Optionally, you can pass a distance attribute (in km, 15 by default):
```python
>>> pa = PlaneAbove((52.4573212, 5.5301535), distance=20)
```
Great, by this time we already know what is happening above that point, so let's check it:
```python
>>> pa.spotted.success
True
>>> pa.spotted.how_many
2
```
In cases when there are no plane detected, or we failed to retrieve information you will get
```True, 0``` and ```False, 0``` respectively. Let's go further and see what are that 2 flying objects:
```python
>>> for plane in pa.fetch():
...     print(
...         f"{plane.aircraft.manufacturer} {plane.aircraft.model} flying to "
...         f"{plane.route.destination.name} is {plane.state.altitude} meters above you!"
...     )

Boeing 777 212ER flying to London Heathrow Airport is 11232 meters above you!
Airbus A330 342 flying to Brussels Airport (Zaventem Airport) is 1006 meters above you!
```
⚠️ If you use acynchronious environment, call ```async_fetch()``` instead:
```python
>>> async for plane in pa.async_fetch():
    ...
```

## Object Reference
<details>
  <summary>Aircraft</summary>

  ```python
class Aircraft:
    registration: str  # Can be empty string.
    manufacturer: str  # Can be empty string.
    model: str  # Can be empty string.
    operator: str  # Can be empty string.
    age: float  # Don’t take age 0.0 as a really new plane, age likely was missing in our sources.
  ```
</details>

<details>
  <summary>Photo</summary>

  ```python
class Photo:
    image_url: str  # Can be empty string.
    origin_url: str  # Can be empty string.
    photographer: str  # Can be empty string.
  ```
</details>

<details>
  <summary>Airport</summary>

  ```python
class Airport:
    iata: str = "N/A"
    name: str = "Unknown airport"  # If route is not found - "Unknown departuture" or "Unknown destination".
    country_code: str = ""  # ISO2 (NL, KR, BR...).
  ```
</details>

<details>
  <summary>Route</summary>

  ```python
class Route:
    departure: Airport
    destination: Airport
    stops: list[Airport]  # Mostly empty; Just a small percentage have stops in route.
    airline: str | None = None  # Airline name performing flight; May differ from aircraft.operator.
  ```
</details>

<details>
  <summary>State</summary>

  ```python
class State:
    altitude: int  # Geometric altitude  in meters. Can be below zero.
    velocity: int  # Velocity over ground in m/s. Can be zero.
  ```
</details>

<details>
  <summary>Plane</summary>

  ```python
class Plane:
    icao24: str  # Always present.
    callsign: str  # Can be empty string.
    country_code: str  # ISO2 (NL, KR, BR...).
    aircraft: Aircraft
    route: Route
    state: State
    photo: Photo
  ```
</details>

## Limitations & Workarounds
OpenSky Network allows to use it's api anonymously, but with limits.
If you wish to extend your usage - consider obtaining ```client_id``` and  ```client_secret```
[here](https://openskynetwork.github.io/opensky-api/rest.html#authentication). Then you pass it like this:
```python
PlaneAbove((52.4573212, 5.5301535), osn_id="your_client_id", osn_secret="your_client_secret")
```

In some cases your calls to OpenSky Network might be timed-out without any specific reason, that's due to OSN
blocking policies and you probably would like to utilize proxy here as a workaround:
```python
PlaneAbove((52.4573212, 5.5301535), osn_proxy="http://username:password@host:port")
```
Please note that this will be used for making an OSN request only; other sources won't be called with that proxy.

One of our photo sources has a strict policy about making requests with
[unique and descriptive user-agents](https://www.planespotters.net/photo/api). That's doable with an extra param:
```python
PlaneAbove((52.4573212, 5.5301535), ps_user_agent="YourApp/1.0 (+https://example.com/contact)")
```
However, you are free to skip it as it won't affect other photo sources.

## Credits
* Flying objects in area: https://opensky-network.org/
* Aircraft data & photo, route & airport details: https://hexdb.io/
* Aircraft data, route & airport details: https://adsbdb.com/
* Aircraft photo, airport details: https://airport-data.com/
* Aircraft data: https://flightdb.net/
* Aircraft photo: https://planespotters.net/
