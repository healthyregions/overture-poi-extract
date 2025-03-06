# overture-poi-extract

A standalone script for creating geojson, shp, and pmtiles extracts from the Overture Maps POI dataset, specifically for  that uses GeoPandas and DuckDB.

## Pre-made layers

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
    -c children's_museum \
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
