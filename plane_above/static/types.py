OSNStateVectorType = tuple[
    str,  # icao24
    str | None,  # callsign
    str,  # origin_country
    int | None,  # time_position
    int,  # last_contact
    float | None,  # longitude
    float | None,  # latitude
    float | None,  # baro_altitude
    bool,  # on_ground
    float | None,  # velocity
    float | None,  # true_track
    float | None,  # vertical_rate
    list[int] | None,  # sensors
    float | None,  # geo_altitude
    str | None,  # squawk
    bool,  # spi
    int,  # position_source
    int,  # category
]
