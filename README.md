# overture-poi-extract

A standalone script for creating geojson, shp, and pmtiles extracts from the [Overture Maps Foundation](https://overturemaps.org/) open data, specifically the "places" theme. It uses DuckDB to query the dataset, GeoPandas to handle the output, and Click for command-line args. (Click is a holdover from how this was originally built within a Flask app, the script should probably be refactored to use argparse instead.)

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

and then I manually edited the file in QGIS to convert from 100 polygons to 7 multipolygons, grouped across the world.

## SDOH & Place Project layers

The following extracts have been created for use as independent data overlays within the SDOH & Place Project's Data Discovery App. Without any filter geometry provided, they default to using the full US geometry in this repo.

#### Grocery/Supermarkets

```
python ./extract_pois.py \
    -c asian_grocery_store \
    -c ethical_grocery \
    -c grocery_store \
    -c international_grocery_store \
    -c korean_grocery_store \
    -c kosher_grocery_store \
    -c mexican_grocery_store \
    -c organic_grocery_store \
    -c specialty_grocery_store \
    -c supermarket \
    -c wholesale_grocer \
    -o output/us-grocery.pmtiles \
    --tippecanoe-path /opt/tippecanoe/tippecanoe
```

#### Schools

```
python ./extract_pois.py \
    -c charter_school \
    -c day_care_preschool \
    -c education \
    -c elementary_school \
    -c high_school \
    -c middle_school \
    -c montessori_school \
    -c preschool \
    -c private_school \
    -c public_school \
    -c religious_school \
    -c school \
    -o output/us-schools.pmtiles \
    --tippecanoe-path /opt/tippecanoe/tippecanoe
```

#### Airports

```
python ./extract_pois.py \
    -c airport \
    -c airport_lounge \
    -c airport_shuttles \
    -c airport_terminal \
    -o output/us-airports.pmtiles \
    --tippecanoe-path /opt/tippecanoe/tippecanoe
```

#### Parks

```
python ./extract_pois.py \
    -c campground \
    -c dog_park \
    -c hiking_trail \
    -c national_park \
    -c park \
    -c playground \
    -c state_park \
    -o output/us-parks.pmtiles \
    --tippecanoe-path /opt/tippecanoe/tippecanoe
```

#### Exercise/Gyms

```
python ./extract_pois.py \
    -c boxing_club \
    -c boxing_gym \
    -c brazilian_jiu_jitsu_club \
    -c chinese_martial_arts_club \
    -c cricket_ground \
    -c cycling_classes \
    -c fencing_club \
    -c golf_club \
    -c golf_course \
    -c gym \
    -c gymnastics_center \
    -c health_and_wellness_club \
    -c hiking_trail \
    -c karate_club \
    -c kickboxing_club \
    -c martial_arts_club \
    -c muay_thai_club \
    -c pilates_studio \
    -c racquetball_court \
    -c soccer_club \
    -c soccer_field \
    -c sports_club_and_league \
    -c squash_court \
    -c swimming_pool \
    -c taekwondo_club \
    -c tai_chi_studio \
    -c tennis_court \
    -c volleyball_court \
    -o output/us-exercise.pmtiles \
    --tippecanoe-path /opt/tippecanoe/tippecanoe
```

#### Libraries

```
python ./extract_pois.py \
    -c library \
    -o output/us-libraries.pmtiles \
    --tippecanoe-path /opt/tippecanoe/tippecanoe
```

#### Child Enrichment

```
python ./extract_pois.py \
    -c after_school_program \
    -c child_care_and_day_care \
    -c "children''s_museum" \
    -c day_care_preschool \
    -c educational_camp \
    -c library \
    -c music_school \
    -c private_tutor \
    -c tutoring_center \
    -o output/us-child-enrichment.pmtiles \
    --tippecanoe-path /opt/tippecanoe/tippecanoe
```

#### Adult Education

```
python ./extract_pois.py \
    -c art_school \
    -c bartending_school \
    -c business_schools \
    -c college_university \
    -c cooking_classes \
    -c cooking_school \
    -c cosmetology_school \
    -c dance_school \
    -c dentistry_schools \
    -c drama_school \
    -c driving_school \
    -c dui_school \
    -c engineering_schools \
    -c flight_school \
    -c language_school \
    -c library \
    -c massage_school \
    -c medical_school \
    -c medical_sciences_schools \
    -c music_school \
    -c nursing_school \
    -c ski_and_snowboard_school \
    -c specialty_school \
    -c sports_school \
    -c traffic_school \
    -c vocational_and_technical_school \
    -o output/us-adult-education.pmtiles \
    --tippecanoe-path /opt/tippecanoe/tippecanoe
```
