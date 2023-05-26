"""
Module Name:    GeoBoundaries Cleaaning
Author:         Carlos Alberto Toruño Paniagua
Date:           April 6th, 2023
Description:    This module is focused in reading and preparing the World Bank Official Boundaries  
                dataset provided by the World Bank Cartography Unit for their use in the ROLI-MAP-app.
                The CGAZ dataset can be found here: 
                https://datacatalog.worldbank.org/search/dataset/0038272/World-Bank-Official-Boundaries
This version:   April 27th, 2023
"""

import os
import numpy as np
import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union

# Defining path to data files
path2data = os.path.join(os.path.dirname(__file__), 
                         '..', 
                         "Data/WB_geodata/")

# Loading Boundaries GeoJSON
raw_boundaries       = (gpd
                        .read_file(path2data + "WB_countries_Admin0.geojson"))
raw_boundaries       = raw_boundaries[["TYPE", "WB_A3", "CONTINENT", 
                                       "REGION_UN", "SUBREGION", "REGION_WB", 
                                       "NAME_EN", "WB_NAME", "WB_REGION", 
                                       "geometry"]]

# Adjusting Dependent Territories labeled as "Country"
raw_boundaries.loc[raw_boundaries["WB_A3"] == "JEY", "TYPE"]    = "Dependency"
raw_boundaries.loc[raw_boundaries["WB_A3"] == "GGY", "TYPE"]    = "Dependency"
raw_boundaries.loc[raw_boundaries["WB_A3"] == "IMY", "TYPE"]    = "Dependency"
raw_boundaries.loc[raw_boundaries["WB_A3"] == "SXM", "TYPE"]    = "Dependency"
raw_boundaries.loc[raw_boundaries["WB_A3"] == "CUW", "TYPE"]    = "Dependency"
raw_boundaries.loc[raw_boundaries["WB_A3"] == "ABW", "TYPE"]    = "Dependency"
raw_boundaries.loc[raw_boundaries["WB_A3"] == "BES", "TYPE"]    = "Dependency"
raw_boundaries.loc[raw_boundaries["WB_A3"] == "SXM", "TYPE"]    = "Dependency"
raw_boundaries.loc[raw_boundaries["WB_A3"] == "TKL", "TYPE"]    = "Dependency"
raw_boundaries.loc[raw_boundaries["TYPE"]  == "Lease", "WB_A3"] = "XXX"

# Adjusting Geographical allocaations to match WJP's allocation
raw_boundaries.loc[raw_boundaries["WB_A3"] == "MEX", "SUBREGION"] = "Central America"
raw_boundaries.loc[raw_boundaries["WB_A3"] == "MLT", "REGION_WB"] = "Europe & Central Asia"

# Adjusting Three-Letter Country Codes to match index data
raw_boundaries.loc[raw_boundaries["WB_A3"] == "ZAR", "WB_A3"] = "COD"
raw_boundaries.loc[raw_boundaries["WB_A3"] == "KSV", "WB_A3"] = "XKX"
raw_boundaries.loc[raw_boundaries["WB_A3"] == "ROM", "WB_A3"] = "ROU"

# Splitting China's geometries
china    = raw_boundaries.loc[raw_boundaries["WB_A3"] == "CHN"]
exploded = china.explode().reset_index(drop = True)
# exploded["area"] = exploded.geometry.area
# Using the aarea I am able to identify Taiwan as row #31

# Manually inputting Taiwan's info
exploded.at[31, 'WB_A3']   = "TWN"
exploded.at[31, 'NAME_EN'] = "Taiwan"
exploded.at[31, 'WB_NAME'] = "Taiwan"

# Disolving exploded geopandas for China
china = (exploded
         .dissolve(by      = "WB_A3",
                   aggfunc = "first")).reset_index()

# Appending china+taiwan geopandas to raw_boundaries
raw_boundaries = (pd.concat([raw_boundaries.loc[raw_boundaries["WB_A3"] != "CHN"],
                             china],
                             ignore_index = True))

# Loading Disputed Territories GeoJSON
disputed_territories = (gpd
                        .read_file(path2data + "WB_Admin0_disputed_areas.geojson")
                        .drop(6)
                        .assign(TYPE="Disputed"))
disputed_territories = disputed_territories[["TYPE", "WB_A3", "CONTINENT", 
                                             "REGION_UN", "SUBREGION", "REGION_WB", 
                                             "NAME_EN", "WB_NAME", "WB_REGION", 
                                             "geometry"]]
disputed_territories["WB_grouped_A3"] = disputed_territories["WB_A3"]

# The following steps were needed when using the GeoBoundaries data. However,
# Now that we are using the World Bank Data, these steps are not required anymore.

# Simplify polygons with a tolerance of 0.01
# simplified_boundaries = boundaries_adt.simplify(tolerance = 0.01, 
#                                                 preserve_topology = True)

# Replacing old and accurate geometries for simplified ones
# gboundaries = gpd.GeoDataFrame(raw_boundaries.drop(columns = ['geometry']), 
#                                geometry = simplified_boundaries, 
#                                crs = raw_boundaries.crs)

# Filtering Antarctica and those polygons without a shapeGroup value
# filtered_boundaries = gboundaries.query("shapeGroup != 'ATA' and not(shapeGroup.isna())")

# Defining a function to group dependencies to their "Parent State"
def group_dependencies(row):
    code = row["WB_A3"]
    if code in ["ASM", "UMI", "GUM", "MNP", "PRI", "VIR"]:
        return "USA"
    elif code in ["AIA", "BMU", "IOT", "VGB", "CYM", "FLK", "GIB", "GGY", 
                  "IMY", "JEY", "MSR", "PCN", "SHN", "SGS", "TCA"]:
        return "GBR"
    elif code in ["ABW", "BES", "CUW", "SXM"]:
        return "NLD"
    elif code in ["PYF", "ATF", "NCL", "BLM", "MAF", "SPM", "WLF"]:
        return "FRA"
    elif code in ["CXR", "CCK", "HMD", "NFK"]:
        return "AUS"
    elif code in ["COK", "NIU", "TKL"]:
        return "NZL"
    elif code in ["FRO"]: # Greenland "GRL" stays as a separate territory
        return "DNK"
    # elif code in ["HKG", "MAC"]:
    #     return "CHN"
    else:
        return row["WB_A3"]

# Creating a grouped WB code
raw_boundaries["WB_grouped_A3"] = raw_boundaries.apply(group_dependencies, 
                                                       axis = 1)

# Transforming variables from all DEPENDENCY territories to NaN
raw_boundaries.loc[raw_boundaries["TYPE"] == "Dependency", 
                   ~(raw_boundaries
                     .columns
                     .isin(["WB_grouped_A3", "geometry"]))] = np.nan

# Dissolving the geo data frame
raw_boundaries = (raw_boundaries
                  .dissolve(by      = "WB_grouped_A3",
                            aggfunc = "first")).reset_index()

# Unifying TYPE == COUNTRY
raw_boundaries.loc[raw_boundaries["TYPE"] == "Sovereign country", "TYPE"] = "Country"

# Concatenating boundaries with disputed territories
boundaries = pd.concat([raw_boundaries, disputed_territories])
boundaries = boundaries.drop(["WB_grouped_A3", "CONTINENT", "WB_REGION", "NAME_EN"], 
                             axis = 1)

# Save the updated GeoJSON to a file
path4saving = os.path.join(os.path.dirname(__file__), 
                           '..',
                           "Data")
boundaries.to_file(path4saving + "/data4app.geojson", 
                   driver="GeoJSON")

# Converting data to a Pandas DataFrame and saving it as CSV
(pd
 .DataFrame(boundaries.drop(columns="geometry"))
 .to_csv(path4saving + "/data4app.csv"))

