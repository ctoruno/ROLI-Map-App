import io
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import streamlit as st
from shapely.geometry import box

st.set_page_config(
    page_title = "Map Generator",
    page_icon  = ":earth_americas:"
)

with open("styles.css") as stl:
    st.markdown(f"<style>{stl.read()}</style>", 
                unsafe_allow_html=True)

# Cache of data
@st.cache_data
def load_data():
    # Loading data
    boundaries        = gpd.read_file("Data/data4app.geojson")
    roli_data         = pd.read_excel("Data/ROLI_data.xlsx")
    roli_data["year"] = roli_data["year"].apply(str)
    data              = {"boundaries" : boundaries,
                         "roli"       : roli_data}
    return data 
master_data = load_data()

# Loading a list with variable labels
variable_labels = ["Rule of Law Index Overall Score",
                   "Factor 1: Constraints on Government Powers",    
                   "1.1 Government powers are effectively limited by the legislature",    
                   "1.2 Government powers are effectively limited by the judiciary",    
                   "1.3 Government powers are effectively limited by independent auditing and review",    
                   "1.4 Government officials are sanctioned for misconduct",    
                   "1.5 Government powers are subject to non-governmental checks",    
                   "1.6 Transition of power is subject to the law",    
                   "Factor 2: Absence of Corruption",    
                   "2.1 Government officials in the executive branch do not use public office for private gain",    
                   "2.2 Government officials in the judicial branch do not use public office for private gain",    
                   "2.3 Government officials in the police and the military do not use public office for private gain",    
                   "2.4 Government officials in the legislative branch do not use public office for private gain",    
                   "Factor 3: Open Government",    
                   "3.1. Publicized laws and government data",    
                   "3.2 Right to information",    
                   "3.3 Civic participation",    
                   "3.4 Complaint mechanisms",    
                   "Factor 4: Fundamental Rights",    
                   "4.1 Equal treatment and absence of discrimination",    
                   "4.2 The right to life and security of the person is effectively guaranteed",    
                   "4.3 Due process of the law and rights of the accused",    
                   "4.4 Freedom of opinion and expression is effectively guaranteed",    
                   "4.5 Freedom of belief and religion is effectively guaranteed",    
                   "4.6 Freedom from arbitrary interference with privacy is effectively guaranteed",    
                   "4.7 Freedom of assembly and association is effectively guaranteed",    
                   "4.8 Fundamental labor rights are effectively guaranteed",   
                   "Factor 5: Order and Security",    
                   "5.1 Crime is effectively controlled",    
                   "5.2 Civil conflict is effectively limited",    
                   "5.3 People do not resort to violence to redress personal grievances",    
                   "Factor 6: Regulatory Enforcement",    
                   "6.1 Government regulations are effectively enforced",    
                   "6.2 Government regulations are applied and enforced without improper influence",    
                   "6.3 Administrative proceedings are conducted without unreasonable delay",    
                   "6.4 Due process is respected in administrative proceedings",    
                   "6.5 The government does not expropriate without lawful process and adequate compensation",    
                   "Factor 7: Civil Justice",    
                   "7.1 People can access and afford civil justice",    
                   "7.2 Civil justice is free of discrimination",    
                   "7.3 Civil justice is free of corruption",    
                   "7.4 Civil justice is free of improper government influence",    
                   "7.5 Civil justice is not subject to unreasonable delay",   
                   "7.6. Civil justice is effectively enforced",    
                   "7.7 Alternative dispute resolution mechanisms are accessible, impartial, and effective",    
                   "Factor 8: Criminal Justice",    
                   "8.1 Criminal investigation system is effective",    
                   "8.2 Criminal adjudication system is timely and effective",    
                   "8.3 Correctional system is effective in reducing criminal behavior",    
                   "8.4 Criminal system is impartial",    
                   "8.5 Criminal system is free of corruption",   
                   "8.6 Criminal system is free of improper government influence",    
                   "8.7 Due process of the law and rights of the accused"]

# Loading a Data Frame with regional bbox coordinates
bbox_coords = pd.DataFrame([

        # UN regions
        ['Southern Europe', -10, 35, 30, 47],
        ['Southern Asia', 42, 5, 105, 40],
        ['Middle Africa', 5, -19.2, 35, 24.5],
        ['Western Asia', 25, 10, 65, 45],
        ['South America', -90, -60, -30, 15],
        ['Caribbean', -85, 8, -57, 28],
        ['Australia and New Zealand', 105, -50, 180, -5],
        ['Western Europe', -10, 35, 20, 60],
        ['Eastern Africa', 20, -27.5, 58, 22.8],
        ['Western Africa', -25, -1, 25, 28.5],
        ['Eastern Europe', 11, 40, 45, 65],
        ['Central America', -93, 5, -76, 20],
        ['South-Eastern Asia', 90, -11, 145, 29],
        ['Southern Africa', 10, -35, 55, -16],
        ['Northern America', -170, 13, -50, 88],
        ['Eastern Asia', 73, 20, 150, 55],
        ['Northern Europe', -25, 50, 36, 72],
        ['Northern Africa', -15, 9, 37, 40],
        ['Melanesia', 139, -20.5, 180, 0],
        ['Micronesia', 133, 3, 170, 11],
        ['Central Asia', 45, 35, 90, 56],
        ['Polynesia', -176, -22.5, -166, -12],

        # WJP regions
        ['East Asia & Pacific', 73, -48.7, 180, 54.8],
        ['Eastern Europe and Central Asia', 13, 35, 180, 88],
        ['EU, EFTA, and North America', -172, 24, 36, 88],
        ['Latin America & Caribbean', -119.5, -66, -29, 38.3],
        ['Middle East & North Africa', -19.5, 18, 64.3, 45], 
        ['South Asia', 57, 5, 100, 40], 
        ['Sub-Saharan Africa', -21, -36.9, 61.3, 38.3],

        # Additional WB regions
        ['Europe & Central Asia', -12, 33.5,88, 75],
        ['North America', -170, 24, -50, 88]

], columns = ["region", "min_X", "min_Y", "max_X", "max_Y"]
)

# Intro text
st.title("ROLI Map Generator")

st.markdown(
    """
    <p class='jtext'>
    This is an interactive app designed to display and generate <a href="https://datavizcatalogue.com/methods/choropleth.html">
    <b style="color:#003249">Choropleth Maps</b></a> using the WJP's <i>Rule of Law Index</i> scores as data inputs. 
    This app is still under deevelopment. Therefore, customization is limited at the moment. However, the data
    presented in this app is up-to-date according to the latest datasets published by the World Justice Project in its website.
    </p>
    
    <p class='jtext'>
    In order to generate a map, follow the next steps:
    </p>

    <ol>
        <li class='jtext'>
            Define the geographical extension of your map. It can be either a global map or limited to a specific region or geographical
            coordinates.
        </li>
        <li class='jtext'>
            Select the data that you would like the map to display from the available options or load your own set of data.
        </li>
        <li class='jtext'>
            You can further customize your map by adding color breaks or changing the color key. You don't need to set a color for every country, 
            you just need to define the major color breaks that your Choropleth Map should have. The app will then, do the rest. 
        </li>
        <li class='jtext'>
            Once you are ready, click on the <b style="color:#003249">"Display"</b> button to visualize your map.
        </li>
        <li class='jtext'>
            If you like the map and you would like to save it as a SVG file, click on the 
            <b style="color:#003249">"Save"</b> button.
        </li>
    </ol>

    <p class='jtext'>
    If you have questions, suggestions or you want to report a bug, you can send an email to 
    <b style="color:#003249">carlos.toruno@gmail.com</b>. The Python code for this app
    is publicly available on <a href="https://github.com/ctoruno/ROLI-Map-App" target="_blank" style="color:#003249">
    this GitHub repository</a>.
    </p>
    <p class='jtext'>
    Galingan!
    </p>
    """,
    unsafe_allow_html = True
)

st.markdown("""---""")

# Creating a container for the geographical extension of the map
extension_container = st.container()
with extension_container:

    # Extension Container Title
    st.markdown("<h4>Step 1: Define the geographical extension of your map</h4>",
                    unsafe_allow_html = True)
        
    # Extension input
    extension_help = '''
    The extension refers to the geographical coverage of your desired map. It can be a world or regional map.
    A world map is straightforward, but if you want to draw a regional map, you will need to fulfill additional 
    options about the geographical extension of your map.
    '''
    regions_help = '''
    The World Bank classification divides countries and territories in seven regions,
    an it is driven by geography and development criteria. This is the classification 
    used by WJP to present their results. The United Nations classification divides
    countries and territories in 5 continents and 22 subregions.
    '''
    dinput_help = '''
    Would you like to use the index scores data or would you like to input your own custom data?
    '''
    data_format_help = '''
    For uploading a file, make sure the workbook has a single sheet and it has two columns at the 
    beginning: "WB_A3" and "year". Each row should represnt the achieved value for a country in a certain 
    year.
    '''

    extension = st.radio("Select an extension for your map:", 
                        ["World", "Regional", "Custom"],
                        horizontal = True,
                        help       = extension_help)

    # Available Regions
    UN_regions    = master_data["boundaries"]["REGION_UN"].dropna().unique().tolist()
    # UN_regions.remove('Seven seas (open ocean)')
    UN_subregions = master_data["boundaries"]["SUBREGION"].unique().tolist()
    WB_regions    = master_data["boundaries"]["REGION_WB"].unique().tolist()
    WJP_regions   = ['East Asia & Pacific',
                     'Eastern Europe and Central Asia',
                     'EU, EFTA, and North America',
                     'Latin America & Caribbean',
                     'Middle East & North Africa',
                     'South Asia',
                     'Sub-Saharan Africa']

    # Conditional display of regional options
    if extension == "Regional":
        
        # Which regions are we working with?
        regions_div = st.radio("Which region classification would you like to use?",
                              ["WJP", "United Nations"],
                              horizontal = True,
                              help       = regions_help)
        
        if regions_div == "WJP":

            # Defining the filtering variable
            regfilter = "REGION_WJP"

            # Dropdown menu for regions
            selected_regions = st.multiselect("Select the regions you would like to work with:", 
                                              WJP_regions,
                                              help = "You can select more than one region.")
            
        if regions_div == "United Nations":

            # Defining the filtering variable
            regfilter = "SUBREGION"

            # Dropdown menu for regions
            regions = st.multiselect("Select the regions you would like to work with:",  
                                     UN_regions,
                                     help = "You can select more than one region.")
            
            # Dropdown menu for subregions
            listed_subregions = master_data["boundaries"][master_data["boundaries"]["REGION_UN"].isin(regions)]["SUBREGION"].unique().tolist()
            selected_regions  = st.multiselect("Select the regions you would like to work with:", 
                                               listed_subregions,
                                               default = listed_subregions,
                                               help = "You can select more than one subregion.")

    # Conditional display for customized extension
    elif extension == "Custom":
        clatitudes, clongitudes = st.columns(2)

        with clatitudes:
            min_lat = st.number_input(label     = "Minimum Latitude",
                                      min_value = -90,
                                      max_value = 90,
                                      value     = 5,
                                      help      = "Insert coordinates in degrees")
            max_lat = st.number_input(label     = "Maximum Latitude",
                                      min_value = -90,
                                      max_value = 90,
                                      value     = 40,
                                      help      = "Insert coordinates in degrees")
        
        with clongitudes:
            min_lon = st.number_input(label     = "Minimum Longitude",
                                      min_value = -180,
                                      max_value = 180,
                                      value     = 57,
                                      help      = "Insert coordinates in degrees")
            max_lon = st.number_input(label     = "Maximum Longitude",
                                      min_value = -180,
                                      max_value = 180,
                                      value     = 100,
                                      help      = "Insert coordinates in degrees")

    else:
        selected_regions = None
        regfilter        = None

st.markdown("""---""")

# Creating a container for the data selection
data_container = st.container()
with data_container:

    # Data Container Title
    st.markdown("<h4>Step 2: Select the scores to be displayed in your map</h4>",
                    unsafe_allow_html = True)
    
    # Choose the data input
    data_input = st.radio("Select a data input for your map:", 
                          ["Index Variables", "Custom Data"],
                          horizontal = True,
                          help       = dinput_help)
    
    if data_input == "Custom Data":

        # File uploader
        uploaded_file = st.file_uploader("Upload Excel file", 
                                         type = ["xlsx"],
                                         help = data_format_help)
        
        # Process uploaded data
        if uploaded_file is not None:

            try:
                # Read the Excel file into a Pandas DataFrame
                master_data["roli"] = pd.read_excel(uploaded_file).rename(columns = {"country_code": "code"})
                master_data["roli"]["year"] = master_data["roli"]["year"].astype(str)

                # Displaying data
                data_preview = st.expander("Click here to preview your data")
                with data_preview:
                    st.write(master_data["roli"])

                # Searchbox to define a target variable
                cnames = master_data["roli"].columns
                available_variables = [col for col in cnames if col not in ["year", "code"]]
                available_years = sorted(master_data["roli"]["year"].unique().tolist(),
                                         reverse = True)
                
                target_variable = st.selectbox("Select a variable from the following list:",
                                               available_variables)
                target_year     = st.selectbox("Select which year do you want to display from the following list:",
                                               available_years)
                
                # Floor and ceiling values
                floor_input, ceiling_input = st.columns(2)

                with floor_input:
                    floor = st.number_input("What's the minimum expected value?")
                
                with ceiling_input:
                    ceiling = st.number_input("What's the maximum expected value?")

            except Exception as e:
                st.error("Error: Unable to read the file. Please upload a valid Excel file.")
                st.exception(e)
    
    else:

        # Searchbox to define a target variable
        available_variables = dict(zip(master_data["roli"].iloc[:, 4:].columns.tolist(),
                                    variable_labels))
        available_years = sorted(master_data["roli"]["year"].unique().tolist(),
                                reverse = True)
        target_variable = st.selectbox("Select a variable from the following list:",
                                    list(available_variables.keys()),
                                    format_func=lambda x: available_variables[x])
        target_year     = st.selectbox("Select which year do you want to display from the following list:",
                                    available_years)
        
        # Floor and ceiling values
        floor   = 0
        ceiling = 1

st.write()

st.markdown("""---""")

# Creating a container for the customization options
customization = st.container()
with customization:

    # Data Cistomization Container Title
    st.markdown("<h4>Step 3: Customize your map</h4>",
                    unsafe_allow_html = True)

    # Defining default colors
    default_colors = [["#1A7154"],
                      ["#A41010", "#1E3231"],
                      ["#A41010", "#F0C412", "#1E3231"],
                      ["#A41010", "#F0C412", "#1A7154", "#1E3231"],
                      ["#A41010", "#CA6A11", "#F0C412", "#1A7154", "#1E3231"],
                      ["#A41010", "#CA6A11", "#F0C412", "#859B33", "#1A7154", "#1E3231"],
                      ["#A41010", "#CA6A11", "#DD9712", "#F0C412", "#859B33", "#1A7154", "#1E3231"]]
    
    color_breaks = []

    # Dropdown menu for number of color breaks
    ncolors = st.number_input("Select number of color breaks", 2, 7, 5,
                              help = "You can select to a maximum of 7 color breaks.")

    # Dynamic Color Pickers
    st.markdown("<b>Select or write down the color codes for your legend</b>:",
                unsafe_allow_html = True)
    cols    = st.columns(ncolors)
    for i, x in enumerate(cols):
        input_value = x.color_picker(f"Break #{i+1}:", 
                                        default_colors[ncolors-1][i],
                                        key = f"break{i}")
        x.write(str(input_value))
        color_breaks.append(input_value)

st.markdown("""---""")

# Creating a container for the saving options
saving = st.container()
    
with saving:
    #Saving Options Title
    st.markdown("<h4>Step 4: Draw your map</h4>",
                unsafe_allow_html = True)

    submit_button = st.button(label = "Display")

# Server
if submit_button:

    # Filtering ROLI Data
    filtered_roli = master_data["roli"][master_data["roli"]['year'] == target_year]

    # Merge the two DataFrames on a common column
    data4map = master_data["boundaries"].merge(filtered_roli,
                                               left_on  = "WB_A3", 
                                               right_on = "code",
                                               how      = "left")
    
    # Subsetting countries within selected regions
    if extension != "World":
        
        if extension == "Regional":
            # Defining bounding box
            regions_coords = (bbox_coords[bbox_coords["region"].isin(selected_regions)])
            min_X = regions_coords.min_X.min()
            min_Y = regions_coords.min_Y.min()
            max_X = regions_coords.max_X.max()
            max_Y = regions_coords.max_Y.max()
            bbox  = box(min_X, min_Y, max_X, max_Y)

            # Masking the world map using the bounding box
            # We also changed the projection to Miller Cilindrical Projection
            # see: https://epsg.io/54003

        if extension == "Custom":
            bbox  = box(min_lon, min_lat, max_lon, max_lat)

        data4drawing = data4map[data4map.intersects(bbox)].copy()
        data4drawing.loc[:, 'geometry'] = data4drawing.intersection(bbox)
        data4drawing = data4drawing.to_crs('ESRI:54003')
    
    else:
         data4drawing = data4map.copy()

    # Creating a special borders geo-data-frame
    disp = data4drawing[data4drawing.TYPE.isin(["Disputed"])]
    disp = gpd.GeoDataFrame(disp, geometry = disp.boundary)
    sbor = data4drawing[data4drawing.TYPE.isin(["Special Border"])]
    sborders = pd.concat([disp, sbor])
    
    # Parameters for missing values
    missing_kwds = {
        "color"    : "#EBEBEB",
        "edgecolor": "#EBEBEB",
        "label"    : "Missing values"
    }

    # Create a custom colormap
    colors_list = color_breaks
    cmap_name   = "default_cmap"
    cmap        = colors.LinearSegmentedColormap.from_list(cmap_name, colors_list)

    # Drawing plotly
    # data4drawing.set_index("WB_NAME")
    # fig = px.choropleth(
    #     data_frame             = data4drawing,
    #     geojson                = data4drawing.geometry,
    #     locations              = data4drawing.index,
    #     color                  = target_variable,
    #     color_continuous_scale = color_breaks,
    #     range_color            = (0, 1),
    #     labels                 = {"country": target_variable}
    # )

    # fig.update_geos(
    #     projection_type=<projection_type>,
    #     showcoastlines=True,  # Display coastlines on the map
    #     coastlinecolor="white",  # Set the color of the coastlines
    #     showland=True,  # Display landmasses on the map
    #     landcolor="lightgray",  # Set the color of the landmasses
    # )

    # Display the plotly figure using Streamlit
    # st.plotly_chart(fig)

    # Creating tabs for displaying the results
    map_tab, table_tab = st.tabs(["Map", "Table"])

    with map_tab:
        # Drawing map with matplotlib
        fig, ax = plt.subplots(1, 
                            figsize = (25, 16),
                            dpi     = 100)
        data4drawing.plot(
            column       = target_variable, 
            cmap         = cmap,
            linewidth    = 0.2,
            ax           = ax,
            edgecolor    = "#EBEBEB",
            legend       = True,
            vmin         = floor,
            vmax         = ceiling,
            missing_kwds = missing_kwds
        )
        sborders.plot(
            ax           = ax,
            linestyle    = "dotted",
            linewidth    = 0.2, 
            color        = "#CCCCCC"
        )
        ax.axis("off")

        # Displaying map
        st.pyplot(fig)

        # Export image as SVG file
        svg_file = io.StringIO()
        plt.savefig(svg_file, 
                    format = "svg")
        
        # Download button
        st.download_button(label     = "Save map", 
                           data      = svg_file.getvalue(), 
                           file_name = "choropleth_map.svg",
                           key       = "download-map")
        
    with table_tab:

        buffer = io.BytesIO()

        # Dropping geometries
        outcome_table = (pd
                         .DataFrame(data4drawing.drop(columns = "geometry")))
        
        # Subsetting data frame to export
        outcome_table = outcome_table[outcome_table["year"] == target_year]
        outcome_table = outcome_table[["WB_A3", target_variable]]

        # Adding minimmum and maximum hypothetical values
        outcome_table = outcome_table.append({'WB_A3': 'Floor-Ceiling', target_variable: floor}, 
                                             ignore_index = True)
        outcome_table = outcome_table.append({'WB_A3': 'Floor-Ceiling', target_variable: ceiling}, 
                                             ignore_index = True)

        # Add a new column to the GeoDataFrame for color codes
        outcome_table["color_code"] = (outcome_table
                                       .apply(lambda row: colors.rgb2hex(plt.cm.get_cmap(cmap)(row[target_variable])), 
                                              axis = 1))
        
        # Excluding the hypothetical values
        outcome_table = outcome_table.query("WB_A3 != 'Floor-Ceiling'")
        
        # Displaying Table
        st.write(outcome_table)

        # Converting to EXCEL
        # You need to install the XlsxWriter. See: https://xlsxwriter.readthedocs.io/
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            outcome_table.to_excel(writer,
                                   sheet_name = "Data-Table")
            
            writer.save()

        # Download button
        st.download_button(
            label     = "Download Table as an Excel file",
            data      = buffer,
            file_name = "color_map.xlsx",
            mime      = "application/vnd.ms-excel"
        )

    