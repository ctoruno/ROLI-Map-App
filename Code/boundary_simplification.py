import geopandas as gpd
import topojson as tp
import os

path4saving = os.path.join(os.path.dirname(__file__), 
                           '..',
                           "Data")

# Reading data
boundaries = gpd.read_file(path4saving + "/data4app.geojson")

# Convert the GeoDataFrame to a TopoJSON format
topojson_data = tp.Topology(boundaries,
                            prequantize = 1000000)

# Saving as TOPOJSON
topojson_data.to_json(path4saving + "/Simplified files/WJPboundaries.topojson")

# Set your tolerance in degrees
tolerance_degrees_10m = 0.000090  # Approximately 10 meters in degrees
tolerance_degrees_25m = 0.000225  # Approximately 25 meters in degrees
tolerance_degrees_50m = 0.000450  # Approximately 50 meters in degrees

# Simplify the TopoJSON geometries with specified tolerances in degrees
topojson_simplified_10m = topojson_data.toposimplify(
    epsilon = tolerance_degrees_10m, 
    simplify_algorithm   = 'vw', 
    simplify_with        = 'simplification', 
    prevent_oversimplify = True
)

topojson_simplified_25m = topojson_data.toposimplify(
    epsilon = tolerance_degrees_25m, 
    simplify_algorithm   = 'vw', 
    simplify_with        = 'simplification', 
    prevent_oversimplify = True
)

topojson_simplified_50m = topojson_data.toposimplify(
    epsilon = tolerance_degrees_50m, 
    simplify_algorithm   = 'vw', 
    simplify_with        = 'simplification', 
    prevent_oversimplify = True
)

# Convert the simplified TopoJSON back to GeoDataFrame
simplified_gdf_10m = topojson_simplified_10m.to_gdf()
simplified_gdf_25m = topojson_simplified_25m.to_gdf()
simplified_gdf_50m = topojson_simplified_50m.to_gdf()

# Saving geodataframes
simplified_gdf_10m.to_file(path4saving + "/Simplified files/simplified_gdf_10m.geojson", 
                           driver="GeoJSON")
topojson_simplified_10m.to_json(path4saving + "/Simplified files/simplified_gdf_10m.topojson")

simplified_gdf_25m.to_file(path4saving + "/Simplified files/simplified_gdf_25m.geojson", 
                           driver="GeoJSON")
topojson_simplified_25m.to_json(path4saving + "/Simplified files/simplified_gdf_25m.topojson")

simplified_gdf_50m.to_file(path4saving + "/Simplified files/simplified_gdf_50m.geojson", 
                           driver="GeoJSON")
topojson_simplified_50m.to_json(path4saving + "/Simplified files/simplified_gdf_50m.topojson")

# Visualizing simplified versions
simplified_gdf_50m.plot(color     = "orange", 
                        edgecolor = "#EBEBEB",
                        linewidth = 0.50)
plt.title('Simplified geometries: Precision 50m')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.savefig('boundaries50m.png', dpi=300, bbox_inches='tight')