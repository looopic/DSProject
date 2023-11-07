CREATE OR REPLACE VIEW water AS
SELECT
    osm_id,
    ST_Union(way) AS geom
FROM planet_osm_polygon
WHERE "natural" = 'water'
GROUP BY osm_id;

CREATE OR REPLACE VIEW forest AS
SELECT
    osm_id,
    ST_Union(way) AS geom
FROM planet_osm_polygon
WHERE landuse = 'forest'
GROUP BY osm_id;

CREATE OR REPLACE VIEW building AS
SELECT
    osm_id,
    ST_Union(way) AS geom
FROM planet_osm_polygon
WHERE building IS NOT NULL
GROUP BY osm_id;

CREATE OR REPLACE VIEW communities AS
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