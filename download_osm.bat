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

REM Check if osmconvert file exists in the Downloads folder
if not exist "%userprofile%\Downloads\osmconvert64-0.8.8p.exe" (
    echo Downloading osmconvert...
    powershell -command "Invoke-WebRequest -OutFile %userprofile%\Downloads\osmconvert64-0.8.8p.exe 'https://drive.google.com/uc?export=download&id=1g7uYHpO31p0CLiE86g2mrBo9Yw_kMSiE'"
)

REM Download Switzerland OSM data
echo Downloading Switzerland OSM data...
powershell -command "(New-Object System.Net.WebClient).DownloadFile('http://download.geofabrik.de/europe/switzerland-latest.osm.pbf', '%userprofile%\Downloads\switzerland-latest.osm.pbf')"
echo Downloading Austria OSM data...
powershell -command "(New-Object System.Net.WebClient).DownloadFile('https://download.geofabrik.de/europe/austria-latest.osm.pbf', '%userprofile%\Downloads\austria-latest.osm.pbf')"
echo Downloading Netherlands OSM data...
powershell -command "(New-Object System.Net.WebClient).DownloadFile('https://download.geofabrik.de/europe/netherlands-latest.osm.pbf', '%userprofile%\Downloads\netherlands-latest.osm.pbf')"

REM Create merged OSM-File
echo Merging OSM-files
%userprofile%\Downloads\osmconvert64-0.8.8p.exe %userprofile%\Downloads\switzerland-latest.osm.pbf --out-o5m | %userprofile%\Downloads\osmconvert64-0.8.8p.exe - %userprofile%\Downloads\austria-latest.osm.pbf -o=%userprofile%\Downloads\merge1.pbf
%userprofile%\Downloads\osmconvert64-0.8.8p.exe %userprofile%\Downloads\merge1.pbf --out-o5m | %userprofile%\Downloads\osmconvert64-0.8.8p.exe - %userprofile%\Downloads\netherlands-latest.osm.pbf -o=%userprofile%\Downloads\merged.pbf

REM Import OSM data into PostgreSQL using osm2pgsql
echo Importing OSM data into PostgreSQL...
osm2pgsql -c -d %db% -U %username% -H localhost -S "%userprofile%\Downloads\default.style" "%userprofile%\Downloads\merged.pbf"

echo Process completed.