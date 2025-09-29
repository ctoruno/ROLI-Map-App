"""
Module Name:    GeoBoundaries Cleaaning
Author:         Carlos Alberto Toruño Paniagua
Date:           April 6th, 2023
Description:    This module is focused in reading and preparing the World Bank Official Boundaries  
                dataset provided by the World Bank Cartography Unit for their use in the ROLI-MAP-app.
                The CGAZ dataset can be found here: 
                https://datacatalog.worldbank.org/search/dataset/0038272/World-Bank-Official-Boundaries
This version:   September 14th, 2023
"""

import os
import numpy as np
import geopandas as gpd
import pandas as pd
from shapely.geometry import box

# Defining path to data files
path2data = os.path.join(os.path.dirname(__file__), 
                         '..', 
                         "Data/WB_geodata/")

# Loading Boundaries GeoJSON
raw_boundaries  = (gpd
                   .read_file(path2data + "WB_countries_Admin0.geojson"))
raw_boundaries  = raw_boundaries[["TYPE", "WB_A3", "CONTINENT", "REGION_UN", 
                                  "SUBREGION", "REGION_WB", "NAME_EN", "WB_NAME", 
                                  "WB_REGION", "geometry"]]

# Adjusting Dependent Territories labeled as "Country"
raw_boundaries.loc[raw_boundaries["WB_A3"] == "JEY", "TYPE"]    = "Dependency"  # Jersey (UK)
raw_boundaries.loc[raw_boundaries["WB_A3"] == "GGY", "TYPE"]    = "Dependency"  # Guernsey (UK)
raw_boundaries.loc[raw_boundaries["WB_A3"] == "IMY", "TYPE"]    = "Dependency"  # Isle of Man (UK)
raw_boundaries.loc[raw_boundaries["WB_A3"] == "SXM", "TYPE"]    = "Dependency"  # Sint Maarten (Neth.)
raw_boundaries.loc[raw_boundaries["WB_A3"] == "CUW", "TYPE"]    = "Dependency"  # Curaçao (Neth.)
raw_boundaries.loc[raw_boundaries["WB_A3"] == "ABW", "TYPE"]    = "Dependency"  # Aruba (Neth.)	
raw_boundaries.loc[raw_boundaries["WB_A3"] == "BES", "TYPE"]    = "Dependency"  # Saba (Neth.)
raw_boundaries.loc[raw_boundaries["WB_A3"] == "TKL", "TYPE"]    = "Dependency"  # Tokelau (NZ)	
raw_boundaries.loc[raw_boundaries["WB_A3"] == "HKG", "TYPE"]    = "Dependency"  # Hong Kong (SAR, China)
raw_boundaries.loc[raw_boundaries["WB_A3"] == "MAC", "TYPE"]    = "Dependency"  # Macau (SAR, China)
raw_boundaries.loc[raw_boundaries["WB_A3"] == "GRL", "TYPE"]    = "Dependency"  # Greenland (Den.)

# Adjusting WB_A3 codes of dependent territories that have the same country code as
# their respective sovereign country
raw_boundaries.loc[raw_boundaries["NAME_EN"]  == "Clipperton Island", "WB_A3"]    = "FRA-OT"
raw_boundaries.loc[raw_boundaries["WB_NAME"]  == "Navassa Island (US)", "WB_A3"]  = "USA-OT"

# Converting all geometries classified as "Country" to "Sovereign country"
raw_boundaries.loc[raw_boundaries["TYPE"] == "Country", "TYPE"]    = "Sovereign country"

# Modifying the WB_A3 code for Guantanamo Bay
raw_boundaries.loc[raw_boundaries["TYPE"]  == "Lease", "WB_A3"] = "XXX"

# Adjusting Geographical allocations to match WJP's allocation
raw_boundaries.loc[raw_boundaries["WB_A3"] == "MEX", "SUBREGION"] = "Central America"
raw_boundaries.loc[raw_boundaries["WB_A3"] == "MLT", "REGION_WB"] = "Europe & Central Asia"

# Adjusting Three-Letter Country Codes to match index data (ISO CODES)
raw_boundaries.loc[raw_boundaries["WB_A3"] == "ZAR", "WB_A3"] = "COD"   # D.R. Congo
raw_boundaries.loc[raw_boundaries["WB_A3"] == "KSV", "WB_A3"] = "XKX"   # Kosovo
raw_boundaries.loc[raw_boundaries["WB_A3"] == "ROM", "WB_A3"] = "ROU"   # Romania

# FIXING THE TAIWAN-CHINA ISSUE
# Splitting China's geometries
china    = raw_boundaries.loc[raw_boundaries["WB_A3"] == "CHN"]
china_ex = china.explode(index_parts = True).reset_index(drop = True)

# Using the area I am able to identify Taiwan as row #31
# exploded["area_m2"] = (exploded
#                        .to_crs("ESRI:54003")
#                        .geometry
#                        .area)
# china_exsort = exploded.sort_values(by = "area_m2", 
#                                     ascending = False)

# Manually inputting Taiwan's info
china_ex.at[31, 'WB_A3']   = "TWN"
china_ex.at[31, 'NAME_EN'] = "Taiwan"
china_ex.at[31, 'WB_NAME'] = "Taiwan"

# Disolving exploded geopandas for China
china = (china_ex
         .dissolve(by      = "WB_A3",
                   aggfunc = "first")).reset_index()

# Appending china+taiwan geopandas to raw_boundaries
raw_boundaries = (pd.concat([raw_boundaries.loc[raw_boundaries["WB_A3"] != "CHN"],
                             china],
                             ignore_index = True))

# FIXING THE FRANCE OVERSEES TERRITORIES ISSUE
# Splitting France's geometries
france    = raw_boundaries.loc[raw_boundaries["WB_A3"] == "FRA"]
france_ex = france.explode(index_parts = True).reset_index(drop = True)

# Continental France bounding box
FRbox  = box(-16.4, 34, 23, 52.5)

# Define a function to check if the feature's geometry falls within FRA bounding box
def location_checker(row):
    if row.geometry.within(FRbox):
        return "France"
    else:
        return "France Oversees Territories"

# Adjusting info of the Oversees Territories
france_ex["WB_NAME"] = france_ex.apply(location_checker, axis=1)
france_ex.loc[france_ex["WB_NAME"] == "France Oversees Territories", "TYPE"]  = "Dependency"
france_ex.loc[france_ex["WB_NAME"] == "France Oversees Territories", "WB_A3"] = "FRA-OT"
france_ex.loc[france_ex["WB_NAME"] == "France Oversees Territories", "REGION_UN"] = "Other"
france_ex.loc[france_ex["WB_NAME"] == "France Oversees Territories", "SUBREGION"] = "Other"

# Disolving exploded geopandas for France
france = (france_ex
          .dissolve(by      = "WB_A3",
                    aggfunc = "first")).reset_index()

# Appending china+taiwan geopandas to raw_boundaries
raw_boundaries = (pd.concat([raw_boundaries.loc[raw_boundaries["WB_A3"] != "FRA"],
                             france],
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

# THE FOLLOWING STEPS ARE NO LONGER NEEDED!!!
# DEPENDENCIES ARE LEFT AS SEPARATE GEOMETRIES

# Creating a grouped WB code
# raw_boundaries["WB_grouped_A3"] = raw_boundaries.apply(group_dependencies, 
#                                                        axis = 1)

# Transforming variables from all DEPENDENCY territories to NaN
# raw_boundaries.loc[raw_boundaries["TYPE"] == "Dependency", 
#                    ~(raw_boundaries
#                      .columns
#                      .isin(["WB_grouped_A3", "geometry"]))] = np.nan

# Dissolving the geo data frame
# raw_boundaries = (raw_boundaries
#                   .dissolve(by      = "WB_grouped_A3",
#                             aggfunc = "first")).reset_index()

# Unifying TYPE == COUNTRY
# raw_boundaries.loc[raw_boundaries["TYPE"] == "Sovereign country", "TYPE"] = "Country"

# Concatenating boundaries with disputed territories
boundaries = pd.concat([raw_boundaries, disputed_territories])
boundaries = boundaries.drop(["WB_grouped_A3", "CONTINENT", "WB_REGION", "NAME_EN"], 
                             axis = 1)

# THE FOLLOWING STEPS ARE NO LONGER NEEDED!!!
# NO MORE SPECIAL BORDERS

# ## DEFINING SPECIAL BORDERS
# ## Sudan - South Sudan
# sudan       = boundaries[boundaries["WB_A3"] == "SDN"].iloc[0].geometry
# south_sudan = boundaries[boundaries["WB_A3"] == "SSD"].iloc[0].geometry
# sudan.touches(south_sudan)
# sudan_border = sudan.intersection(south_sudan)

# ## Ethiopia - Somalia
# ethiopia = boundaries[boundaries["WB_A3"] == "ETH"].iloc[0].geometry
# somalia  = boundaries[boundaries["WB_A3"] == "SOM"].iloc[0].geometry 
# ethiopia.touches(somalia)
# etsom_border = ethiopia.intersection(somalia)

# ## Kosovo - Serbia
# kosovo = boundaries[boundaries["WB_A3"] == "XKX"].iloc[0].geometry
# serbia = boundaries[boundaries["WB_A3"] == "SRB"].iloc[0].geometry
# kosovo.touches(serbia)
# koser_border = kosovo.intersection(serbia)

# ## South - North Korea
# skorea = boundaries[boundaries["WB_A3"] == "KOR"].iloc[0].geometry
# nkorea = boundaries[boundaries["WB_A3"] == "PRK"].iloc[0].geometry
# skorea.touches(nkorea)
# korea_border = skorea.intersection(nkorea)

# ## Creating geopandas dataframe with special borders
# bnames = ["Sudan - South Sudan",
#           "Ethiopia - Somalia",
#           "Kosovo - Serbia",
#           "Korea"]
# types = "Special Border"
# geometries = [sudan_border, 
#               etsom_border,
#               koser_border,
#               korea_border]
# dictionary = {"TYPE": "Special Border",
#               "WB_NAME": bnames, 
#               "geometry": geometries}
# sborders   = gpd.GeoDataFrame(dictionary, geometry = geometries)

# # Creating extended bounndaries
# boundaries_extended = pd.concat([boundaries, sborders])

# Save the updated GeoJSON to a file
path4saving = os.path.join(os.path.dirname(__file__), 
                           '..',
                           "Data")
boundaries.to_file(path4saving + "/data4app.geojson", 
                   driver="GeoJSON")
# boundaries_extended.to_file(path4saving + "/data4app.geojson", 
#                             driver="GeoJSON")

# Converting data to a Pandas DataFrame and saving it as CSV
(pd
 .DataFrame(boundaries.drop(columns="geometry"))
 .to_csv(path4saving + "/data4app.csv"))