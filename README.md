# overture-poi-extract

A standalone script for creating geojson, shp, and pmtiles extracts from the [Overture Maps Foundation](https://overturemaps.org/) open data, specifically the "places" theme. It uses DuckDB to query the dataset, GeoPandas to handle the output, and Click for command-line args. (Click is a holdover from how this was originally built within a Flask app, the script should probably be refactored to use argparse instead.)

Overture [Places data](https://docs.overturemaps.org/guides/places/) is published under a [CDLA Permissive 2.0](https://cdla.dev/permissive-2-0/).

## Installation

Create a virtual environment and install all Python requirements.

```
python3 -m venv env
source ./env/bin/activate
pip install -r requirements.txt
```

## Usage

```
python extract_pois.py [-c/--category] [-g/--geometry-ids] [-o/--out-file]
```

Note: If you are creating a PMTiles output file, you must provide a local path to a [tippecanoe](https://github.com/felt/tippecanoe) executable.

For a few undocumented arguments, see the script itself.

## Geometry Filters

The POI extract can be filtered by US Census geometry boundaries (state, county, census tract, etc), or an arbitrary geojson or shapefile input. If no filter is provided, the command will default to using the `full-us-geoms-dissolved.geojson` file in this repo (see below).

For each geometry supplied, a query to Overture is made using the bounding box of that geometry, and once the results have been converted to a GeoDataframe, then a clip operation is further used to refine the results within the actual geometry itself.

### Using Census Boundaries

`-g/--geometry-ids`

To filter by Census Boundaries, provide one or more `-g <HEROP_ID>` arguments. A **HEROP_ID** is essentially a standard FIPS or GEOID preceded by the summary level code for the unit and the string "US". You can read more about this ID structure in our [Github org page](https://github.com/healthyregions). State, county, tract, block group, and zip-code tabulation area are all supported.

For example, this will return a GeoJSON of all restaurants in Louisiana:

```
python extract_pois.py -c restaurants -g 040US22 -o parks-in-louisiana.geojson
```


### Using arbitrary geometry

`--filter-file` & `--filter-unit`

You can also provide a shapefile or geojson file, and specify a single feature within it to be used as the filter geometry. Provide a path to the file, and then a `field=value` to specify the feature.

For example, given an existing shapefile of country boundaries that has a field `NAME`:

```
python extract_pois.py -c park --filter-file world-countries.shp --filter-unit NAME=Spain -o parks-in-spain.geojson
```

### Full US GeoJSON

Without any geometry filter arguments, a boundary of the whole US will be used, including Alaska, Hawaii, Puerto Rico, Pacific Islands, and Guam. The following code was first used to create the geojson:

```
import geopandas as gpd

gdf = gpd.read_file("https://herop-geodata.s3.us-east-2.amazonaws.com/oeps/state-2018-500k-shp.zip")
dissolved = gdf.geometry.buffer(0.1).unary_union.buffer(-0.1)
with open("us-geom.geojson", "w") as o:
    o.write(to_geojson(dissolved, indent=1))
```

and then I manually edited the file in QGIS to convert from 100 individual polygons to 7 multipolygons, grouped across the world. These 7 are iterated in the script and handled as individual spatial queries.

## SDOH & Place Project layers

The following extracts have been created for use as independent data overlays within the SDOH & Place Project's Data Discovery App. Without any filter geometry provided, they default to using the full US geometry in this repo.

#### Grocery/Supermarkets

```
python ./extract_pois.py \
    -c sdoh-community-assets-categories/grocery.txt
    -o output/us-airports.pmtiles \
    --tippecanoe-path /opt/tippecanoe/tippecanoe
```

[grocery.txt](./sdoh-community-assets-categories/grocery.txt)


#### Schools

```
python ./extract_pois.py \
    -c sdoh-community-assets-categories/schools.txt
    -o output/us-schools.pmtiles \
    --tippecanoe-path /opt/tippecanoe/tippecanoe
```

[schools.txt](./sdoh-community-assets-categories/schools.txt)

#### Parks

```
python ./extract_pois.py \
    -c sdoh-community-assets-categories/parks.txt
    -o output/us-parks.pmtiles \
    --tippecanoe-path /opt/tippecanoe/tippecanoe
```

[parks.txt](./sdoh-community-assets-categories/parks.txt)

#### Exercise/Gyms

```
python ./extract_pois.py \
    -c sdoh-community-assets-categories/exercise.txt
    -o output/us-exercise.pmtiles \
    --tippecanoe-path /opt/tippecanoe/tippecanoe
```

[exercise.txt](./sdoh-community-assets-categories/exercise.txt)

#### Libraries

```
python ./extract_pois.py \
    -c sdoh-community-assets-categories/libraries.txt
    -o output/us-libraries.pmtiles \
    --tippecanoe-path /opt/tippecanoe/tippecanoe
```

[libraries.txt](./sdoh-community-assets-categories/libraries.txt)

#### Child Enrichment

```
python ./extract_pois.py \
    -c sdoh-community-assets-categories/child-enrichment.txt
    -o output/us-child-enrichment.pmtiles \
    --tippecanoe-path /opt/tippecanoe/tippecanoe
```

[child-enrichment.txt](./sdoh-community-assets-categories/child-enrichment.txt)

#### Adult Education

```
python ./extract_pois.py \
    -c sdoh-community-assets-categories/adult-education.txt
    -o output/us-adult-education.pmtiles \
    --tippecanoe-path /opt/tippecanoe/tippecanoe
```

[adult-education.txt](./sdoh-community-assets-categories/adult-education.txt)
