Drop View potential_PR_locations;
Create VIEW potential_PR_locations AS
SELECT DISTINCT ON (parking.osm_id) 
    parking.*
FROM
    (SELECT *
    FROM planet_osm_polygon
    WHERE amenity IN ('parking','parking_entrence','parking_space')
    ) AS parking
JOIN
    (SELECT osm_id, highway, way
    FROM planet_osm_roads
    WHERE highway IN ('trunk_link','primary_link','motorway_link')
    ) AS road
ON ST_Distance(parking.way, road.way) <= 2500
JOIN
    (SELECT osm_id, public_transport, way
    FROM planet_osm_polygon
    WHERE public_transport IN ('station','stop_position')
    ) AS public_transport
ON ST_Distance(parking.way, public_transport.way) <= 500;
SELECT * FROM potential_pr_locations;