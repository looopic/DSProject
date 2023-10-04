@echo off
setlocal enabledelayedexpansion

REM Define default values for parameters
set "db=gisdb"
set "username=gisdb"
set "password="

REM Check for and process command line arguments
if not "%~1"=="" set "db=%~1"
if not "%~2"=="" set "username=%~2"
if not "%~3"=="" set "password=%~3"

REM Check if default.style file exists in the Downloads folder
if not exist "%userprofile%\Downloads\default.style" (
    echo Downloading default.style...
    powershell -command "(New-Object System.Net.WebClient).DownloadFile('https://learnosm.org/files/default.style', '%userprofile%\Downloads\default.style')"
)

REM Check if .pgpass file exists, and if not, create it with the provided password
if not exist "%userprofile%\.pgpass" (
    echo Creating .pgpass file...
    echo localhost:5432:*:%username%:%password% > "%userprofile%\.pgpass"
)

REM Check if pg_hba.conf contains the necessary line, and if not, add it
set "pg_hba_file=C:\Program Files\PostgreSQL\16\data\pg_hba.conf"
set "auth_line=host    all             %username%           127.0.0.1/32            md5"
findstr /C:"%auth_line%" "%pg_hba_file%" >nul || (
    echo Adding line to pg_hba.conf...
    echo %auth_line% >> "%pg_hba_file%"

    REM Restart PostgreSQL service
    echo Restarting PostgreSQL service...
    net stop postgresql-x64-16
    net start postgresql-x64-16
)

REM Download Switzerland OSM data
echo Downloading Switzerland OSM data...
powershell -command "(New-Object System.Net.WebClient).DownloadFile('http://download.geofabrik.de/europe/switzerland-latest.osm.pbf', '%userprofile%\Downloads\switzerland-latest.osm.pbf')"

REM Import OSM data into PostgreSQL using osm2pgsql
echo Importing OSM data into PostgreSQL...
osm2pgsql -c -d %db% -U %username% -H localhost -S "%userprofile%\Downloads\default.style" "%userprofile%\Downloads\switzerland-latest.osm.pbf"

echo Process completed.