<img src="https://raw.githubusercontent.com/wrongcredentials/plane-above/v0.1.1/logo.svg" alt="plane-above" width="170">

# Plane Above
[![PyPI version](https://img.shields.io/pypi/v/plane-above.svg)](https://pypi.org/project/plane-above/)
[![Python versions](https://img.shields.io/pypi/pyversions/plane-above.svg)](https://pypi.org/project/plane-above/)
[![License](https://img.shields.io/pypi/l/plane-above.svg)](https://pypi.org/project/plane-above/)
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
like manufacturer, model, age (based on built date), photo and some others.
At the same time it fecthes flight route by sending multiple requests as well to receive information about departure,
destination and for some cases midpoint airports.
#### 5. COLLECT RESULT
This is the last step where all data are being collected and returned in [declared format](#object-reference).

## Installation
```bash
pip install plane-above
```

## Usage
First, import library, create instance and pass your values of latitude & longitude as a tuple:
```pycon
>>> from plane_above import PlaneAbove
>>> pa = PlaneAbove((52.4573212, 5.5301535))
```
Optionally, you can pass a distance attribute (in km, 15 by default):
```pycon
>>> pa = PlaneAbove((52.4573212, 5.5301535), distance=20)
```
By this time we already know what is happening _above_, so let's check:
```pycon
>>> pa.spotted.success
True
>>> pa.spotted.how_many
2
```
In cases when there are no any planes detected, or we failed to retrieve information you will get
```True, 0``` and ```False, 0``` respectively. Let's go further and see what are these 2 flying objects:
```pycon
>>> for above in pa.fetch():
...     print(
...         f"{above.aircraft.manufacturer} {above.aircraft.model} flying to "
...         f"{above.flight.destination.name} is {above.state.altitude} meters above you!"
...     )

Boeing 777 212ER flying to London Heathrow Airport is 11232 meters above you!
Airbus A330 342 flying to Brussels Airport (Zaventem Airport) is 1006 meters above you!
```
⚠️ If you use acynchronious environment, call ```async_fetch()``` instead:
```text
async for above in pa.async_fetch():
    ...
```

## Object Reference
Both ```fetch()``` and ```async_fetch()``` methods will return an iterator consisting of ```Above``` objects.
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
    country: str  # Origin country from the transponder.
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
    stops: list[Airport]  # Mostly empty; Just a small percentage have stops in route.
    airline: str = ""  # Airline performing flight; May differ from aircraft.operator.
```
</details>

<details>
  <summary>Airport</summary>

```python
class Airport:
    iata: str = "N/A"
    name: str = "Unknown airport"  # If route is not found - "Unknown departure" or "Unknown destination".
    country_code: str = "UN"  # ISO2 code (NL, KR, BR...).
```
</details>

<details>
  <summary>State</summary>

```python
class State:
    altitude: int  # Geometric altitude  in meters. Can be below zero.
    velocity: int  # Velocity over ground in m/s. Can be zero.
    latitude: float | None = None  # WGS-84 latitude in decimal degrees.
    longitude: float | None = None  # WGS-84 longitude in decimal degrees.
```
</details>

## Limitations & Workarounds
### OpenSky Network Authentication
OSN allows to use it's api anonymously, but with limits.
If you wish to extend your usage - consider obtaining ```client_id``` and  ```client_secret```
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

### Planespotters.net additional requirement
This photo source has a strict policy about making requests with
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
