SELECT name,ST_UNION(array_agg(way)) AS way_union
FROM planet_osm_polygon
WHERE admin_level='4'
AND ST_CONTAINS((SELECT way FROM planet_osm_polygon WHERE osm_id=-51701),way)
AND building IS NULL
GROUP BY name;


SELECT *
FROM planet_osm_polygon 
WHERE admin_level='8' AND ST_CONTAINS((SELECT ST_UNION(array_agg(way)) AS way_union
FROM planet_osm_polygon
WHERE admin_level='4'
AND name='Schaffhausen'),way) 
ORDER BY name