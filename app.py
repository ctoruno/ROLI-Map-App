import io
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import streamlit as st
from shapely.geometry import box
from PIL import Image

# Defining a function to check for password
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

# Checking for password
if check_password():

    # Settings
    st.set_page_config(
        page_title = "Map Generator",
        page_icon  = ":earth_americas:"
    )

    # Reading CSS
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
        This is an interactive app designed to display and generate 
        <a href="https://datavizcatalogue.com/methods/choropleth.html">
        <b style="color:#003249">Choropleth Maps</b></a> using the WJP's <i>Rule of Law Index</i> 
        scores as data inputs. This app is still under development. However, the data presented in 
        this app is up-to-date according to the latest datasets published by the World Justice 
        Project in its website.
        </p>

        <p class='jtext'>
        If you have questions, suggestions or you want to report a bug, you can send an email to 
        <b style="color:#003249">carlos.toruno@gmail.com</b>. The Python code for this app
        is publicly available on <a href="https://github.com/ctoruno/ROLI-Map-App" target="_blank" 
        style="color:#003249"> this GitHub repository</a>.
        </p>
        """,
        unsafe_allow_html = True
    )

    st.markdown("""---""")

    # Creating a container for the geographical extension of the map
    extension_container = st.container()
    with extension_container:

        # Extension Container Title
        st.markdown("<h4>Step 1: Define the geographical extension of your map.</h4>",
                        unsafe_allow_html = True)
        st.markdown(
        """
        <p class='jtext'>
        The extension refers to the geographical coverage of your desired map. 
        It can be a world or regional map. For regional maps, you can select from
        a predefined list of options or you can customize the extension using 
        geographical coordinates in order to define a bounding box for your map.
        </p>
        """,
        unsafe_allow_html = True)
            
        # Defining helper texts used by the app
        regions_help = """ 
        The app provides two different regional classifications: (i) The regions used 
        by the World Justice Project in their Insights Reports, and (ii) the regions 
        and subregions used by the United Nations in their Sustainable Development 
        Goals Reports.
        """

        cbar_help = """
        By default, the app generates a map with the color scale bar on the right side
        of the map. You can turn off this setting to have a better control of the output
        dimensions.
        """

        # Extension input
        extension = st.radio("Select an extension for your map:", 
                            ["World", "Regional", "Custom"],
                            horizontal = True)

        # Available Regions
        UN_regions    = ['Asia', 'Americas', 'Africa', 'Europe', 'Oceania']
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
                listed_subregions = (master_data["boundaries"][master_data["boundaries"]["REGION_UN"]
                                                            .isin(regions)]["SUBREGION"]
                                                            .unique()
                                                            .tolist())
                selected_regions  = st.multiselect("Select the regions you would like to work with:", 
                                                listed_subregions,
                                                default = listed_subregions,
                                                help    = "You can select more than one subregion.")

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
                
                if min_lat >= max_lat:
                    st.error("Minimum latitude should be lower than the maximum latitude", 
                            icon = "🚨")
            
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
                
                if min_lon >= max_lon:
                    st.error("Minimum longitude should be lower than the maximum longitude", 
                            icon = "🚨")
                
        else:
            selected_regions = None
            regfilter        = None

    st.markdown("""---""")

    # Creating a container for the data selection
    data_container = st.container()
    with data_container:

        # Data Container Title
        st.markdown("<h4>Step 2: Select the scores that you would like to display in your map</h4>",
                    unsafe_allow_html = True)
        st.markdown(
        """
        <p class='jtext'>
        If you would like to display scores from the Rule of Law Index, you can select
        a variable from a specific year in the dropdown lists below. Additionally,
        the app allows you to upload your own custom data to use in the map.
        </p>
        """,
        unsafe_allow_html = True)
        
        # Choose the data input
        data_input = st.radio("Select a data input for your map:", 
                            ["Rule of Law Index", "Custom Data"],
                            horizontal = True)
        
        if data_input == "Custom Data":

            delta_bin = False

            # Custom Data Example
            cdata_example = Image.open("Media/custom_data_example.png")
            with st.expander(
                label = "Please click here to see an example of how to structure the custom data."
            ) :
                st.image(cdata_example)

            # File uploader
            uploaded_file = st.file_uploader("Upload Excel file", 
                                            type = ["xlsx"])
            
            # Process uploaded data
            if uploaded_file is not None:

                try:
                    # Read the Excel file into a Pandas DataFrame
                    master_data["roli"] = (pd
                                        .read_excel(uploaded_file)
                                        .rename(columns = {"COUNTRY" : "country",
                                                            "CODE"    : "code",
                                                            "YEAR"    : "year"}))
                    master_data["roli"]["year"] = master_data["roli"]["year"].astype(str)

                    # Displaying data
                    data_preview = st.expander("Click here to preview your data")
                    with data_preview:
                        st.write(master_data["roli"])

                    # Searchbox to define a target variable
                    cnames = master_data["roli"].columns
                    available_variables = [col 
                                        for col in cnames 
                                        if col not in ["country", "year", "code"]]
                    available_years = sorted(master_data["roli"]["year"].unique().tolist(),
                                            reverse = True)
                    
                    target_variable = st.selectbox("Select a variable from the following list:",
                                                   available_variables)
                    target_year     = st.selectbox("Select which year do you want to display from the following list:",
                                                   available_years)
                    
                    # Floor and ceiling values
                    floor_input, ceiling_input = st.columns(2)

                    with floor_input:
                        floor   = st.number_input("What's the minimum expected value?")
                    
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

            # Checkbox for yearly changes
            delta_bin = st.checkbox("Would you like to display yearly percentage changes?",
                                    help = "This will transform the variables into categorical groups.")

        if delta_bin == True:
            
            # Adjusting floor/ceiling
            floor   = -1
            ceiling = +1
            
            # Options for categorical values
            end_year  = target_year

            # Creating columns for additional options
            cc1, cc2 = st.columns(2)

            # Base year selection
            with cc1:
                perc_method = st.selectbox("What's the base change?",
                                        ["1-year change", "6-years change"])
            
            # Value breaks to form categories
            with cc2:
                vbreaks = st.number_input("Define your categories", 
                                        min_value = 2, 
                                        max_value = 6, 
                                        value     = 2,
                                        step      = 2)

            # Empty list to store value breaks
            value_breaks = []

            # Defining default value breaks
            if vbreaks == 2:
                default_breaks = [0.0]
            if vbreaks == 4:
                default_breaks = [-2.05, 0.0, 2.05]
            if vbreaks == 6:
                default_breaks = [-4.05, -2.05, 0.0, 2.05, 4.05]

            # Creating dynamic columns    
            cls    = st.columns(vbreaks-1)
            for i, x in enumerate(cls):
                input_edge = x.number_input(f"Value Break #{i+1}:", 
                                            min_value = -100.0,
                                            max_value = 100.0,
                                            value     = default_breaks[i],
                                            step      = 0.05,
                                            key       = f"vbreak{i}")
                value_breaks.append(input_edge/100)
            
            bin_edges  = [floor] + value_breaks + [ceiling]
            bin_labels = []
            for x,y in enumerate(bin_edges):
                print(x)
                if x < len(bin_edges) - 1:
                    b = "From " + str(y) + " to " + str(bin_edges[x+1])
                    bin_labels.append(b)

    st.markdown("""---""")

    # Creating a container for the customization options
    customization = st.container()
    with customization:

        # Map Customization Container Title
        st.markdown("<h4>Step 3: Customize your map</h4>",
                        unsafe_allow_html = True)
        st.markdown(
        """
        <p class='jtext'>
        You can customize your map by customizing your color gradient, removing the color bar,
        adjusting the output dimensions, the DPI and the border widths.
        </p>
        """,
        unsafe_allow_html = True)

        # Defining default colors
        if delta_bin == False:
            default_colors = [["#578e7f"],
                              ["#E51328", "#578e7f"],
                              ["#E51328", "#ccc555", "#578e7f"],
                              ["#E51328", "#f2a241", "#ccc555", "#578e7f"],
                              ["#E51328", "#f2a241", "#ccc555", "#578e7f", "#012d28"],
                              ["#D40276", "#E51328", "#f2a241", "#ccc555", "#578e7f", "#012d28"],
                              ["#D40276", "#E51328", "#f2a241", "#ffffff", "#ccc555", "#578e7f", "#012d28"]]
        else:
            default_colors = [["#C41229", "#0559D4"],
                              ["#C41229", "#EB6975", "#69A2FF", "#0559D4"],
                              ["#C41229", "#EB6975", "#FEBECC", "#B2D3FF", "#69A2FF", "#0559D4"]]

        # Empty list to store color codes
        color_breaks = []

        # Dropdown menu for number of color breaks
        if delta_bin == False:
            ncolors = st.number_input("Select number of color breaks", 2, 7, 5,
                                    help = "You can select to a maximum of 7 color breaks for your gradient.")
        else:
            ncolors = vbreaks
        
        # Dynamic Color Pickers
        if delta_bin == False:
            cindex = int(ncolors-1)
        else:
            cindex = int((ncolors/2)-1)
        
        st.markdown("<b>Select or write down the color codes for your legend</b>:",
                    unsafe_allow_html = True)
        cols    = st.columns(ncolors)
        for i, x in enumerate(cols):
            input_value = x.color_picker(f"Break #{i+1}:", 
                                            default_colors[cindex][i],
                                            key = f"break{i}")
            x.write(str(input_value))
            color_breaks.append(input_value)

        # Should we keep/remove the color scale bar from the map?
        color_bar = st.toggle("Display color bar from output", 
                            value = True,
                            help  = cbar_help)
        
        st.markdown("""<br>""",
                    unsafe_allow_html = True)

        # Map dimensions
        st.markdown("<b>Specify your map dimensions</b>:",
                    unsafe_allow_html = True)
        
        mwidth, mheight, mres, bthick  = st.columns(4)
        with mwidth:
            width_in  = st.number_input("Width (inches)", 
                                        0, 500, 25)

        with mheight:
            height_in = st.number_input("Height (inches)",
                                        0, 500, 16)
            
        with mres:
            dpi       = st.number_input("Dots per inch (DPI)",
                                        0, 250, 100)
        
        with bthick:
            linewidth = st.number_input("Border width (in points)",
                                        0.0, 5.0, 0.75,
                                        help = "The map has a resolution of 72 PPI")

    st.markdown("""---""")

    # Creating a container for the saving options
    saving = st.container()
        
    with saving:
        #Saving Options Title
        st.markdown("<h4>Step 4: Draw your map</h4>",
                    unsafe_allow_html = True)
        st.markdown(
        """
        <p class='jtext'>
        You can now click on the <b>Display button</b> to visualize the outcomes 
        with the current settings. Once you do it, you will observe three tabs.
        
        <ul>
        <li>
        In the <i>first tab</i>, you can visualize the map. If you need to zoom into 
        the image, you can enlarge the outcome by hovering near the top right corner
        of the image and clicking the <b>enlarge button</b>. If you like the visual, 
        you can click on the <b>Save map button</b> to save the image as an SVG file.
        </li>

        <li>
        In the <i>second tab</i>, the app produces a table with the respective scores 
        and color codes by country. You also have the option to download this table
        as an excel file.
        </li>

        <li>
        In the <i>third tab</i>, you will find a bar chart with the selected
        scores by country-year. You have the option to download this chart as a SVG
        file in your local machine.
        </li>
        </ul>
        </p>
        """,
        unsafe_allow_html = True)

        submit_button = st.button(label = "Display")

    # Server
    if submit_button:

        # Filtering ROLI Data
        if delta_bin == False:
            filtered_roli = master_data["roli"][master_data["roli"]['year'] == target_year]
        
        else:

            # If we are plotting categorical data, we need to transform the data
            filtered_roli = master_data["roli"]

            # Filtering for 6-years change
            if perc_method == "6-years change":
                base_year = int(target_year) - 6
                pattern   = str(target_year) + "|" + str(base_year)
                filtered_roli = (filtered_roli[filtered_roli["year"]
                                            .str.contains(pattern)])
            
            # Calculating percentage change
            filtered_roli = (filtered_roli
                            .sort_values(["country", "year"])
                            .set_index(["country", "code", "year"])
                            .select_dtypes(np.number)
                            .groupby("country")
                            .pct_change()
                            .reset_index()
                            )
            filtered_roli = filtered_roli[filtered_roli["year"] == target_year]

            # Transforming target variable into a categorical variable
            filtered_roli["score"] = filtered_roli[target_variable]
            filtered_roli[target_variable] = (pd
                                            .cut(filtered_roli[target_variable],
                                                bins   = bin_edges,
                                                labels = bin_labels)) 

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
        
        # Parameters for missing values
        missing_kwds = {
            "color"    : "#EBEBEB",
            "edgecolor": "#EBEBEB",
            "label"    : "Missing values"
        }

        # Create a custom colormap
        colors_list = color_breaks
        cmap_name   = "default_cmap"

        if delta_bin == False:
            cmap = colors.LinearSegmentedColormap.from_list(cmap_name, colors_list)
        else:
            value2color     = dict(zip(bin_labels, color_breaks))
            colors_list     = [value2color[value] for value in bin_labels]
            cmap = colors.ListedColormap(colors_list)

        # Creating tabs for displaying the results
        map_tab, table_tab, graph_tab = st.tabs(["Map", "Table", "Graph"])
        # if delta_bin == False:
        #     map_tab, table_tab, graph_tab = st.tabs(["Map", "Table", "Graph"])
        # else:    
        #     map_tab, table_tab = st.tabs(["Map", "Table"])

        with map_tab:
            
            # Drawing map with matplotlib
            fig, ax = plt.subplots(1, 
                                figsize = (width_in, height_in),
                                dpi     = dpi)
            if delta_bin == False:
                data4drawing.plot(
                    column       = target_variable, 
                    cmap         = cmap,
                    linewidth    = linewidth,
                    ax           = ax,
                    edgecolor    = "#EBEBEB",
                    legend       = color_bar,
                    vmin         = floor,
                    vmax         = ceiling,
                    missing_kwds = missing_kwds
                )
            else:
                data4drawing.plot(
                    column       = target_variable, 
                    cmap         = cmap,
                    linewidth    = linewidth,
                    ax           = ax,
                    edgecolor    = "#EBEBEB",
                    legend       = color_bar,
                    missing_kwds = missing_kwds
                )
            ax.axis("off")

            # Displaying map
            st.pyplot(fig)

            # Export image as SVG file
            svg_file = io.StringIO()
            plt.savefig(svg_file, 
                        format = "svg")
            
            # Download button
            st.download_button(label     = "Save Map", 
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
            if delta_bin == False:
                outcome_table = (outcome_table[["country", "WB_A3", target_variable]]
                                .sort_values(by = "country", ascending = True))
            else:
                outcome_table = (outcome_table[["country", "WB_A3", target_variable, "score"]]
                                .sort_values(by = "country", ascending = True))

            # Cleaning table to display
            if delta_bin == False:

                # Adding minimmum and maximum hypothetical values
                minmax = pd.DataFrame({"country"      : ['Floor-Ceiling', 'Floor-Ceiling'],
                                    "WB_A3"        : ['Floor-Ceiling', 'Floor-Ceiling'], 
                                    target_variable: [floor, ceiling]})

                # Add a new column to the GeoDataFrame for color codes
                outcome_table["color_code"] = (outcome_table
                                                .apply(
                                                    lambda row: (colors
                                                                    .rgb2hex(plt
                                                                            .cm
                                                                            .get_cmap(cmap)(row[target_variable]))
                                                                    ), 
                                                        axis = 1))
                
                # Excluding the hypothetical values and sorting values
                outcome_table = (outcome_table
                                .query("WB_A3 != 'Floor-Ceiling'"))
            
            else:
                outcome_table["color_code"] = (outcome_table[target_variable]
                                            .map(value2color))

            
            # Displaying Table
            st.write(outcome_table)

            # Converting to EXCEL
            # You need to install the XlsxWriter. See: https://xlsxwriter.readthedocs.io/
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                outcome_table.to_excel(writer,
                                    sheet_name = "Data-Table")
                
                writer.close()

            # Download button
            st.download_button(
                label     = "Download Table as an Excel file",
                data      = buffer,
                file_name = "color_map.xlsx",
                mime      = "application/vnd.ms-excel"
            )
        
        # if delta_bin == False:
        with graph_tab:
            
            if delta_bin == False:
                # Defining height for plot
                h = len(outcome_table)/5
                
                # Creating plot
                bars = plt.figure(figsize = (10, h))
                plt.barh(outcome_table["country"],
                         outcome_table[target_variable], 
                         color = outcome_table["color_code"])
                plt.gca().invert_yaxis()
                plt.margins(y = 0)

            else:
                # Filtering data
                outcome_table = (outcome_table
                                 .dropna(subset = ["score"])
                                 .sort_values("score"))

                # Defining height for plot
                h = len(outcome_table)/5
                
                # Creating plot
                bars = plt.figure(figsize = (10, h))
                plt.barh(outcome_table["country"],
                         outcome_table["score"], 
                         color = outcome_table["color_code"])
                plt.gca().invert_yaxis()
                plt.margins(y = 0)

            # Add labels and a title
            plt.title("Scores by Country")

            # Displaying map
            st.pyplot(bars)

            # Export image as SVG file
            svg_file = io.StringIO()
            plt.savefig(svg_file, 
                        format = "svg")
            
            # Download button
            st.download_button(label     = "Save Chart", 
                            data      = svg_file.getvalue(), 
                            file_name = "bar_chart.svg",
                            key       = "download-chart")  

        
