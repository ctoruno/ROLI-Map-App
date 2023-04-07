#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module Name:    GeoBoundaries Cleaaning
Author:         Carlos Alberto Toruño Paniagua
Date:           April 6th, 2023
Description:    This module is focused in reading the Comprehensive Global Administrative Zones (CGAZ) dataset
                provided by GeoBoundaries.org, filter the respective polygons and simplify their geometries for 
                their use in the ROLI Map Generator App. The CGAZ dataset can be found here: 
                https://www.geoboundaries.org/downloadCGAZ.html
"""

import os
import geopandas as gpd
import pandas as pd

# Loading GeoJSON file from GeoBoundaries.com
path2gjson = os.path.join(os.path.dirname(__file__), 
                          '..',
                          "Data", 
                          "geoBoundariesCGAZ_ADM0.geojson")
raw_boundaries = gpd.read_file(path2gjson)

# Simplify polygons with a tolerance of 0.01
simplified_boundaries = raw_boundaries.simplify(tolerance = 0.01, 
                                                preserve_topology = True)

# Replacing old and accurate geometries for simplified ones
gboundaries = gpd.GeoDataFrame(raw_boundaries.drop(columns = ['geometry']), 
                               geometry = simplified_boundaries, 
                               crs = raw_boundaries.crs)

# Filtering Antarctica and those polygons without a shapeGroup value
filtered_boundaries = gboundaries.query("shapeGroup != 'ATA' and not(shapeGroup.isna())")

# Save the updated GeoJSON to a file
path4saving = os.path.join(os.path.dirname(__file__), 
                           '..',
                           "Data", 
                           "data4app.geojson")
filtered_boundaries.to_file(path4saving, 
                            driver="GeoJSON")

