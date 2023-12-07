@echo off
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

powershell -command "(New-Object System.Net.WebClient).DownloadFile('https://download.geofabrik.de/europe/monaco-latest.osm.pbf', '%userprofile%\Downloads\monaco-latest.osm.pbf')"
osm2pgsql -c -d %db% -U %username% -H localhost -S "%userprofile%\Downloads\default.style" "%userprofile%\Downloads\monaco-latest.osm.pbf.pbf"

psql -d %db% -U %username% -f SQL_queries\community_coverage.sql