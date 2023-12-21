# Readme

## Prerequisites
1. Have osm2pgsql installed (manual: https://learnosm.org/en/osm-data/osm2pgsql/ download:             https://osm2pgsql.org/doc/install.html#installing-on-windows)
2. Have POSTgreSQL installed (manual at next chapter)
3. Download POSTgreSQL
4. Install POSTgreSQL with all standard parameters

## Prepare your POSTgreSQL database
1. During the installation of POSTgreSQL, when the stackbuilder pops up, you need to select to install POSTgis
2. When the installation is complete, go to "C:\Program Files\PostgreSQL\16\data\pg_hba.conf"
3. Change the "scram-sha-256" to "trust" for the first three entries ("local" is for Unix domain socket connections only, IPv4 local connections and IPv6 local connections)
4. Save the changes
5. Open services.msc and restart the postgresql-x64-16 service
6. Add psql to Path (C:\Program Files\PostgreSQL\16\bin)
7. Open pgAdmin 4 and open the Server
8. Create a new database
9. Open the query tool for the database and enter "CREATE EXTENSION postgis;"
10. Execute the query.

## setup.bat
After you've set up your database, you need to set up the tables and views needed for our project.
To do this, please run the setup.bat file once. This will download the OSM-file of monaco and create the views and tables.

## download_osm.bat
This batch file will download the newest version of the .osm.pbf file of switzerland from geofabrik.de and import it to your database.
It has two parameters.

> Usage: download_osm.bat (db_name) (username)
If you don't specify anything, it will try to connect to the database "gisdb" with the user "postgres"

The style-file will also be automatically downloaded if it doesn't exist in the download folder.

***Keep the size of the osm-file in mind. An import and the refreshing of the views can take several hours up to days!***
