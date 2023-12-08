CREATE VIEW countries AS
SELECT name, ST_Union(way) AS merged_polygon
FROM planet_osm_polygon
WHERE admin_level = '2' AND boundary = 'administrative'
GROUP BY name

SELECT
	ST_UNION(ARRAY(SELECT way 
			FROM planet_osm_polygon 
			WHERE landuse = 'forest' 
			AND ST_WITHIN(way,c.merged_polygon))) AS way,
	c.name as name
FROM
	countries as c;