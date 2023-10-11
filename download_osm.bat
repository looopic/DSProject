@echo off
setlocal enabledelayedexpansion

REM Define default values for parameters
set "db=gisdb"
set "username=gisdb"

REM Check for and process command line arguments
if not "%~1"=="" set "db=%~1"
if not "%~2"=="" set "username=%~2"

REM Check if default.style file exists in the Downloads folder
if not exist "%userprofile%\Downloads\default.style" (
    echo Downloading default.style...
    powershell -command "(New-Object System.Net.WebClient).DownloadFile('https://learnosm.org/files/default.style', '%userprofile%\Downloads\default.style')"
)

REM Download Switzerland OSM data
echo Downloading Switzerland OSM data...
powershell -command "(New-Object System.Net.WebClient).DownloadFile('http://download.geofabrik.de/europe/switzerland-latest.osm.pbf', '%userprofile%\Downloads\switzerland-latest.osm.pbf')"

REM Import OSM data into PostgreSQL using osm2pgsql
echo Importing OSM data into PostgreSQL...
osm2pgsql -c -d %db% -U %username% -H localhost -S "%userprofile%\Downloads\default.style" "%userprofile%\Downloads\switzerland-latest.osm.pbf"

REM Run SQL commands to create columns and compute data
echo Creating columns and computing data...
psql -U %username% -d %db% -c "alter table planet_osm_line add column ST_AsText varchar; alter table planet_osm_point add column ST_AsText varchar; alter table planet_osm_point add column ST_X varchar; alter table planet_osm_point add column ST_Y varchar; alter table planet_osm_polygon add column ST_AsText varchar; alter table planet_osm_polygon add column ST_Area varchar; alter table planet_osm_roads add column ST_AsText varchar;"
psql -U %username% -d %db% -c "update planet_osm_line set ST_AsText=ST_AsText(way); update planet_osm_point set ST_AsText=ST_AsText(way); update planet_osm_point set ST_X=ST_X(way); update planet_osm_point set ST_Y=ST_Y(way); update planet_osm_polygon set ST_AsText=ST_AsText(way); update planet_osm_polygon set ST_Area=ST_Area(way); update planet_osm_roads set ST_AsText=ST_AsText(way);"

echo Process completed.