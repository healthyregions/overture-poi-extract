import uuid
from datetime import datetime
from pathlib import Path
from argparse import Namespace
import subprocess

import click
import duckdb
import geopandas as gpd
import pandas as pd
from shapely import bounds, from_geojson

cb_lookup = {
    "040": "https://herop-geodata.s3.us-east-2.amazonaws.com/census/state-2018-500k-shp.zip",
    "050": "https://herop-geodata.s3.us-east-2.amazonaws.com/census/county-2018-500k-shp.zip",
    "140": "https://herop-geodata.s3.us-east-2.amazonaws.com/census/tract-2018-500k-shp.zip",
    "150": "https://herop-geodata.s3.us-east-2.amazonaws.com/census/bg-2018-500k-shp.zip",
    "160": "https://herop-geodata.s3.us-east-2.amazonaws.com/census/place-2018-500k-shp.zip",
    "860": "https://herop-geodata.s3.us-east-2.amazonaws.com/census/zcta-2018-500k-shp.zip",
}


def get_connection():
    connection = duckdb.connect()

    # these props must be set to empty before the query to s3, otherwise it fails. See:
    # https://github.com/duckdb/duckdb/issues/7970#issuecomment-2118343680
    connection.execute("SET s3_access_key_id='';SET s3_secret_access_key='';")

    connection.install_extension("spatial")
    connection.install_extension("httpfs")
    connection.load_extension("spatial")
    connection.load_extension("httpfs")

    return connection


def get_filter_geometry(input_file: str, filter_value: str):
    print(input_file)

    gdf = gpd.read_file(input_file)
    filter_field, filter_value = filter_value.split("=")

    filter_row = gdf[gdf[filter_field] == filter_value]

    return filter_row["geometry"].values[0]

def get_herop_geometry(herop_ids: list[str]):

    prefix = herop_ids[0][:3]
    gdf = gpd.read_file(cb_lookup[prefix])
    rows = gdf[gdf["HEROP_ID"].isin(herop_ids)]
    dissolved = rows.geometry.unary_union
    return dissolved

def get_full_us_filter():

    with open("full-us-geoms-dissolved.geojson", "r") as o:
        geojson = from_geojson(o.read())

    return geojson.geoms

def get_data(
    geometry_filters: list = [],
    categories: list = [],
    confidence: str = ".9",
):
    con_clause = f"confidence >= {confidence} AND" if confidence != "-1" else ""
    print(f"confidence filter: {con_clause}")

    cat_clause = (
        "category IN ('{}') AND".format("', '".join(categories)) if categories else ""
    )
    print(f"category filter: {cat_clause}")

    gdfs = []
    for geom in geometry_filters:

        bbox = bounds(geom)

        overture_url = (
            "s3://overturemaps-us-west-2/release/2025-10-22.0/theme=places/type=place/*"
        )

        query_sql = """SELECT
            names.primary as name,
            categories.primary as category,
            addresses[1].freeform as address,
            addresses[1].locality as city,
            addresses[1].postcode as zip,
            addresses[1].region as state,
            ROUND(confidence,2) as confidence,
            ST_AsText(geometry) as wkt
        FROM read_parquet('{}', filename=true, hive_partitioning=1)
        WHERE
            {}
            {}
            bbox.xmin BETWEEN {} AND {} AND
            bbox.ymin BETWEEN {} AND {}
            """.format(
            overture_url,
            con_clause,
            cat_clause,
            bbox[0],
            bbox[2],
            bbox[1],
            bbox[3],
        )

        print(query_sql)

        start = datetime.now()
        connection = get_connection()
        df = connection.execute(query_sql).df()
        print(datetime.now() - start)

        # strip the extra 4 from zip codes
        df["zip"] = df["zip"].str[:5]

        gs = gpd.GeoSeries.from_wkt(df["wkt"])
        gdf = gpd.GeoDataFrame(df, geometry=gs, crs="EPSG:4326")

        del gdf["wkt"]

        print(f"{len(gdf)} rows returned")

        gdf = gdf.clip(gpd.GeoSeries(geom, crs="EPSG:4326"))

        gdfs.append(gdf)

    return pd.concat(gdfs)

def write_output(gdf: gpd.GeoDataFrame, outpath: Path, tippecanoe_path:str=None):

    if outpath.suffix == ".geojson":
        gdf.to_file(outpath, driver="GeoJSON")
    elif outpath.suffix == ".shp":
        gdf.to_file(outpath)
    elif outpath.suffix == ".pmtiles":
        json_path = str(outpath).replace(".pmtiles", ".geojson")
        print(json_path)
        gdf.to_file(json_path, driver="GeoJSON")
        cmd = [
            tippecanoe_path,
            # "-zg",
            # tried a lot of zoom level directives, and seems like for block group
            # (which I believe is the densest)shp_paths 10 is needed to preserve shapes well enough.
            "-z10",
            "--cluster-distance",
            "10",
            "--cluster-maxzoom",
            "g",
            "-r1",
            "-d",
            "20",
            "--projection",
            "EPSG:4326",
            "-o",
            str(outpath),
            "-l",
            "resources",
            "--force",
            str(json_path),
        ]
        print(cmd)
        subprocess.run(cmd)

    return outpath


@click.command("get-pois")
@click.option(
    "--categories",
    "-c",
    multiple=True,
    help="The exact name of one or more categories to include in the query. If not provided, all points "
    "will be included in the export. You can also pass a text file list of categories.",
)
@click.option(
    "--outfile",
    "-o",
    help="Path to output file. If not provided, a small preview of the query result will be printed to "
    "the console.",
    type=click.Path(
        resolve_path=True,
        path_type=Path,
    ),
)
@click.option(
    "--confidence",
    default=".9",
    help="level of confidence to use when querying Overture data (greater than or equal to)",
)
@click.option(
    "-g", "--geometry-ids",
    multiple=True,
    help="One or more HEROP_IDs which will be matched against prepared Census Boundary files to acquire a geometry filter",
)
@click.option(
    "--filter-file",
    help="Geospatial dataset with geometry to filter against. Can be a shapefile or geojson dataset, either "
    "a local path or a url to one stored in S3.",
)
@click.option(
    "--filter-unit",
    help="Field=Value for a single feature to find in the filter-file and use as a geometry filter in the query.",
)
@click.option(
    "--export-category-list",
    is_flag=True,
    default=False,
    help="Export a list of all categories included in the query to a CSV file. Only really useful if "
    "you don't include any categories in the filter.",
)
@click.option(
    "--separate-files",
    is_flag=True,
    default=False,
    help="Write separate file for each category in the results.",
)
@click.option(
    "--tippecanoe-path",
    default=None,
    help="Path to tippecanoe binary needed for conversion to PMTiles.",
)
@click.option(
    "--upload", is_flag=True, default=False, help="Upload the output file to S3."
)
@click.option(
    "--upload-prefix", is_flag=True, default=False, help="Upload the output file to S3."
)
def get_pois(**kwargs):
    """This operation will query the Overture Places (a.k.a. Point of Interest) dataset and extract all points
    matching the specified categories that fall within the provided spatial boundary.

    Example:

    ```
    flask overture get-pois --filter-file "https://herop-geodata.s3.us-east-2.amazonaws.com/place-2018.shp" -c hospital --filter-unit 3651000
    ```
    """
    args = Namespace(**kwargs)

    ## 0) INITIAL ARGS VALIDATION

    if args.geometry_ids:
        prefixes = set([i[:3] for i in args.geometry_ids])
        if len(prefixes) > 1:
            raise Exception("Can only ids with the same prefixes.")
        if list(prefixes)[0] not in cb_lookup:
            raise Exception("Invalid prefix on HEROP_ID:", args.geometry_ids[0][:3])
    if args.filter_file or args.filter_unit:
        if not args.filter_file or not args.filter_unit:
            raise Exception("--filter-file and --filter-unit must both be provided if one is to be used.")
    if (
        args.outfile and Path(args.outfile).suffix == ".pmtiles"
    ) and args.tippecanoe_path is None:
        raise Exception("Tippecanoe path needed for PMTiles output.")

    categories = []
    for c in args.categories:
        if Path(c).is_file():
            with open(c, "r") as o:
                for i in o.readlines():
                    categories.append(i.rstrip().lstrip())
        else:
            categories.append(c)

    ## 1) CREATE GEOMETRY FILTER BASED ON INPUT

    if args.geometry_ids:
        filter_geoms = [get_herop_geometry(args.geometry_ids)]
    elif args.filter_file or args.filter_unit:
        filter_geoms = [get_filter_geometry(args.filter_file, args.filter_unit)]
    else:
        filter_geoms = get_full_us_filter()

    ## 2) QUERY FOR POI DATA
    data = get_data(
        geometry_filters=filter_geoms,
        categories=categories,
        confidence=args.confidence,
    )

    ## 3) (optional) WRITE OUT A LIST OF ALL RETURNED CATEGORIES
    if args.export_category_list:
        # Get the distinct values of the column
        distinct_values = data["category"].drop_duplicates()

        fpath = (
            args.outfile.name + "__categories.csv"
            if args.outfile
            else f"categories__{uuid.uuid4().hex}.csv"
        )

        # Write the distinct values to a CSV file
        distinct_values.to_csv(fpath, index=False, header=None)

    ## 4) (optional) WRITE DATA TO OUTPUT FILE(S)
    if args.outfile:
        outpath = write_output(data, args.outfile, args.tippecanoe_path)
        print(f"saved to: {outpath}")

if __name__ == "__main__":
    get_pois()
