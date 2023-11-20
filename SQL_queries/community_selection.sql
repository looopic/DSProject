SELECT name, ST_Union(way) AS aggregated_way
FROM planet_osm_polygon 
WHERE admin_level='8' 
  AND ST_CONTAINS(
    (
      SELECT ST_Union(array_agg(way)) 
      FROM planet_osm_polygon 
      WHERE admin_level='4' AND name='Solothurn'
    ), 
    way
  ) 
GROUP BY name
ORDER BY name;