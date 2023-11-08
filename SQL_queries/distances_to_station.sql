WITH building_to_station AS (
    SELECT
        b.osm_id AS building_osm_id,
        b.way AS building_geom,
        s.osm_id AS station_osm_id,
        s.way AS station_geom,
        ST_Distance(b.way, s.way) / 1000 AS distance_km
    FROM
        planet_osm_polygon b
    JOIN
        (SELECT osm_id, way FROM planet_osm_point WHERE railway = 'station') s
    ON ST_DWithin(b.way, s.way, 5000)
),
avg_min_max_distances AS (
    SELECT
        c.osm_id AS gemeinde_osm_id,
        c.name AS gemeinde_name,
        MAX(bs.distance_km) AS max_distance_km,
        MIN(bs.distance_km) AS min_distance_km,
        AVG(bs.distance_km) AS avg_distance_km
    FROM
        planet_osm_polygon c
    LEFT JOIN
        building_to_station bs ON ST_Within(bs.building_geom, c.way)
    WHERE
        c.admin_level = '2'
    GROUP BY
        c.osm_id, c.name
)
SELECT
    gemeinde_name,
    gemeinde_osm_id,
    avg_distance_km,
    min_distance_km,
    max_distance_km
FROM avg_min_max_distances;