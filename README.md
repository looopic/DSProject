# Readme

## Prerequisites
1. Have osm2pgsql installed (manual: https://learnosm.org/en/osm-data/osm2pgsql/ download:             https://osm2pgsql.org/doc/install.html#installing-on-windows)
2. Have POSTgreSQL installed (manual at next chapter)

## Prepare your POSTgreSQL database
1. Download POSTgreSQL
2. Install POSTgreSQL with all standard parameters
3. When the stackbuilder pops up, you need to select to install POSTgis
4. When the installation is complete, go to "C:\Program Files\PostgreSQL\16\data\pg_hba.conf"
5. Change the "scram-sha-256" to "trust" for the first three entries ("local" is for Unix domain socket connections only, IPv4 local connections and IPv6 local connections)
6. Save the changes
7. Open services.msc and restart the postgresql-x64-16 service
8. Add psql to Path (C:\Program Files\PostgreSQL\16\bin)
9. Open pgAdmin 4 and open the Server
10. Create a new database
11. Open the query tool for the database and enter "CREATE EXTENSION postgis;"
12. Execute the query.

## download_osm.bat
This batch file will download the newest version of the .osm.pbf file of switzerland from geofabrik.de
It has two optional parameters.

Usage: download_osm.bat (db_name) (username)
If you don't specify anything, it will try to connect to the database "gisdb" with the user "postgres"

The style-file will also be automatically downloaded if it doesn't exist in the download folder.
