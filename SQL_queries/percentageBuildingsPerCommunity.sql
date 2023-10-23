CREATE VIEW buildings as
SELECT building.*, community.osm_id as community FROM
(SELECT * FROM planet_osm_polygon WHERE building is not NULL) as building
JOIN
(SELECT osm_id, way from planet_osm_polygon WHERE admin_level='8') as community
ON ST_CONTAINSPROPERLY(community.way,building.way);
SELECT * from buildings;

WITH building_areas AS (
  SELECT building.community, SUM(ST_AREA(building.way)) AS total_building_area
  FROM buildings AS building
  GROUP BY building.community
)

SELECT DISTINCT ON (community.osm_id)
	community.osm_id, community.name, community.way, 
  (CASE
    WHEN ST_AREA(community.way) > 0
    THEN (SUM(building_areas.total_building_area) / ST_AREA(community.way)) * 100
    ELSE 0
  END) AS percentage_built
FROM planet_osm_polygon AS community
LEFT JOIN building_areas ON community.osm_id = building_areas.community
WHERE community.admin_level = '8'
GROUP BY community.osm_id, community.name, community.way;
