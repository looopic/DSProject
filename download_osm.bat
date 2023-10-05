@echo off
setlocal enabledelayedexpansion

REM Define default values for parameters
set "db=gisdb"
set "username=postgres"

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

echo Process completed.