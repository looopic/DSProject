CREATE MATERIALIZED VIEW water AS
SELECT
	1 as osm_id,
	ST_Union(
		ARRAY(
			SELECT way
			FROM planet_osm_polygon 
			WHERE "natural" = 'water')) 
	AS geom;

CREATE MATERIALIZED VIEW forest AS
SELECT
	1 AS osm_id,
    ST_Union(
		ARRAY(
			SELECT way 
			FROM planet_osm_polygon 
			WHERE landuse = 'forest'))
	AS geom;

CREATE MATERIALIZED VIEW building AS
SELECT
	1 AS osm_id,
    ST_Union(
		ARRAY(
			SELECT way 
			FROM planet_osm_polygon 
			WHERE landuse IN ('commercial','education','industrial','residential','retail','institutional')))
	AS geom;

CREATE MATERIALIZED VIEW communities AS
SELECT
	c.osm_id AS osm_id,
	c.name AS name,
	c.way AS way,
	(ST_Area(ST_Intersection(way, w.geom)))/1000000 AS water_area,
	(ST_Area(ST_Intersection(way, f.geom)))/1000000 AS forest_area,
	(ST_Area(ST_Intersection(way, b.geom)))/1000000 AS building_area,
	(ST_Area(way)-ST_Area(ST_Intersection(way, b.geom)))/1000000 AS free_space
FROM planet_osm_polygon c
LEFT JOIN water w ON ST_Intersects(way,w.geom)
LEFT JOIN forest f ON ST_Intersects(way,f.geom)
LEFT JOIN building b ON ST_Intersects(way,b.geom)
WHERE admin_level='8';

CREATE VIEW countries AS
SELECT name, ST_Union(way) AS merged_polygon
FROM planet_osm_polygon
WHERE admin_level = '2' AND boundary = 'administrative'
GROUP BY name;

REFRESH MATERIALIZED VIEW water;
REFRESH MATERIALIZED VIEW forest;
REFRESH MATERIALIZED VIEW building;
REFRESH MATERIALIZED VIEW communities;

SELECT * FROM communities;