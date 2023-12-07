CREATE VIEW countries AS
SELECT name, ST_Union(way) AS merged_polygon
FROM planet_osm_polygon
WHERE admin_level = '2' AND boundary = 'administrative'
GROUP BY name