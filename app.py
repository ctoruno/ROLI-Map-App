import io
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import streamlit as st
from shapely.geometry import box
from PIL import Image

from src.utils.passcheck import check_password
from src.utils.data_adds import variable_labels, bbox_coords

if check_password():

    st.set_page_config(
        page_title = "Map Generator",
        page_icon  = ":earth_americas:"
    )

    with open("styles.css") as stl:
        st.markdown(f"<style>{stl.read()}</style>", 
                    unsafe_allow_html=True)

    @st.cache_data
    def load_data():
        boundaries        = gpd.read_file("Data/data4app.geojson")
        roli_data         = pd.read_excel("Data/ROLI_data.xlsx")
        roli_data["year"] = roli_data["year"].apply(str)
        data              = {
            "boundaries" : boundaries,
            "roli"       : roli_data
        }
        return data 
    master_data = load_data()
    

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

    # MAP EXTENSION CONTAINER
    extension_container = st.container()
    with extension_container:

        st.markdown(
            "<h4>Step 1: Define the geographical extension of your map.</h4>",
            unsafe_allow_html = True
        )
        st.markdown(
            """
            <p class='jtext'>
            The extension refers to the geographical coverage of your desired map. 
            It can be a world or regional map. For regional maps, you can select from
            a predefined list of options or you can customize the extension using 
            geographical coordinates in order to define a bounding box for your map.
            </p>
            """,
            unsafe_allow_html = True
        )
            
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

        extension = st.radio(
            "Select an extension for your map:", 
            ["World", "Regional", "Custom"],
            horizontal = True
        )

        UN_regions    = ["Asia", "Americas", "Africa", "Europe", "Oceania"]
        WJP_regions   = [
            "East Asia and Pacific",
            "Eastern Europe and Central Asia",
            "EU, EFTA, and North America",
            "Latin America and Caribbean",
            "Middle East and North Africa",
            "South Asia",
            "Sub-Saharan Africa"
        ]

        if extension == "Regional":
            
            regions_div = st.radio(
                "Which region classification would you like to use?",
                ["WJP", "United Nations"],
                horizontal = True,
                help       = regions_help
            )
            
            if regions_div == "WJP":
                regfilter = "REGION_WJP"
                selected_regions = st.multiselect(
                    "Select the regions you would like to work with:", 
                    WJP_regions,
                    help = "You can select more than one region."
                )
                
            if regions_div == "United Nations":
                regfilter = "SUBREGION"
                regions = st.multiselect(
                    "Select the regions you would like to work with:",  
                    UN_regions,
                    help = "You can select more than one region."
                )
                listed_subregions = (
                    master_data["boundaries"][master_data["boundaries"]["REGION_UN"]
                    .isin(regions)]["SUBREGION"]
                    .unique()
                    .tolist()
                )
                selected_regions  = st.multiselect(
                    "Select the regions you would like to work with:", 
                    listed_subregions,
                    default = listed_subregions,
                    help    = "You can select more than one subregion."
                )
                
            opac = st.toggle(
                "Apply different opacities to countries?", 
                value = True,
                help  = "Countries within the map that are not part of the target region will have an alpha value of 20%"
            )
            
            if regions_div == "WJP":
                highlighted_countries = (
                    master_data["roli"][master_data["roli"]["region"]
                    .isin(selected_regions)]["code"]
                    .unique()
                    .tolist()
                )
            if regions_div == "United Nations":
                highlighted_countries = (
                    master_data["boundaries"][master_data["boundaries"]["SUBREGION"]
                    .isin(selected_regions)]["WB_A3"]
                    .unique()
                    .tolist()
                )
            
        elif extension == "Custom":

            clatitudes, clongitudes = st.columns(2)

            with clatitudes:
                min_lat = st.number_input(
                    label     = "Minimum Latitude",
                    min_value = -90,
                    max_value = 90,
                    value     = 5,
                    help      = "Insert coordinates in degrees"
                )
                max_lat = st.number_input(
                    label     = "Maximum Latitude",
                    min_value = -90,
                    max_value = 90,
                    value     = 40,
                    help      = "Insert coordinates in degrees"
                )
                
                if min_lat >= max_lat:
                    st.error(
                        "Minimum latitude should be lower than the maximum latitude", 
                        icon = "🚨"
                    )
            
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
            
            opac = st.toggle(
                "Apply different opacities to countries?", 
                value = True,
                help  = "Countries within the map that are not part of the target region will have an alpha value of 20%"
            )
            if opac:
                countries4high = st.multiselect(
                    "Select the countries you would like to highlight:",  
                    (master_data["roli"]["country"]
                    .unique()
                    .tolist())
                )
                highlighted_countries = (
                    master_data["roli"][master_data["roli"]["country"]
                    .isin(countries4high)]["code"]
                    .unique()
                    .tolist()
                )
        
        else:
            selected_regions = None
            regfilter        = None
            opac             = False

    st.markdown("""---""")

    # DATA OPTIONS CONTAINER
    data_container = st.container()
    with data_container:

        st.markdown(
            "<h4>Step 2: Select the scores that you would like to display in your map</h4>",
            unsafe_allow_html = True
        )
        st.markdown(
            """
            <p class='jtext'>
            If you would like to display scores from the Rule of Law Index, you can select
            a variable from a specific year in the dropdown lists below. Additionally,
            the app allows you to upload your own custom data to use in the map.
            </p>
            """,
            unsafe_allow_html = True
        )
        
        data_input = st.radio(
            "Select a data input for your map:", 
            ["Rule of Law Index", "Custom Data"],
            horizontal = True
        )
        
        if data_input == "Custom Data":

            delta_bin = False

            cdata_example = Image.open("Media/custom_data_example.png")
            with st.expander(
                label = "Please click here to see an example of how to structure the custom data."
            ) :
                st.image(cdata_example)

            uploaded_file = st.file_uploader(
                "Upload Excel file", 
                type = ["xlsx"]
            )
            
            if uploaded_file is not None:
                try:
                    master_data["roli"] = (
                        pd.read_excel(uploaded_file)
                        .rename(
                            columns = {
                                "COUNTRY" : "country",
                                "CODE"    : "code",
                                "YEAR"    : "year"
                            }
                        )
                    )
                    master_data["roli"]["year"] = master_data["roli"]["year"].astype(str)

                    data_preview = st.expander("Click here to preview your data")
                    with data_preview:
                        st.write(master_data["roli"])

                    cnames = master_data["roli"].columns
                    available_variables = [
                        col for col in cnames 
                        if col not in ["country", "year", "code"]
                    ]
                    available_years = sorted(
                        master_data["roli"]["year"].unique().tolist(),
                        reverse = True
                    )
                    
                    target_variable = st.selectbox(
                        "Select a variable from the following list:",
                        available_variables
                    )
                    target_year = st.selectbox(
                        "Select which year do you want to display from the following list:",
                        available_years
                    )
                    
                    floor_input, ceiling_input = st.columns(2)

                    with floor_input:
                        floor   = st.number_input("What's the minimum expected value?")
                    
                    with ceiling_input:
                        ceiling = st.number_input("What's the maximum expected value?")

                except Exception as e:
                    st.error("Error: Unable to read the file. Please upload a valid Excel file.")
                    st.exception(e)
        
        else:
            available_variables = dict(
                zip(master_data["roli"].iloc[:, 4:].columns.tolist(),
                variable_labels)
            )
            available_years = sorted(
                master_data["roli"]["year"].unique().tolist(),
                reverse = True
            )
            target_variable = st.selectbox(
                "Select a variable from the following list:",
                list(available_variables.keys()),
                format_func=lambda x: available_variables[x]
            )
            target_year = st.selectbox(
                "Select which year do you want to display from the following list:",
                available_years
            )
            
            floor   = 0
            ceiling = 1

            if target_year != "2012-2013":
                delta_bin = st.checkbox(
                    "Would you like to display yearly percentage changes?",
                    help = "This will transform the variables into categorical groups."
                )
            else:
                delta_bin = False

        if delta_bin:
            floor   = -1
            ceiling = +1
            end_year = target_year
            available_base_years = [x for x in available_years if x < end_year]

            cc1, cc2 = st.columns(2)

            with cc1:
                base_year = st.selectbox(
                    "What's the base year?",
                    available_base_years
                )
            
            with cc2:
                vbreaks = st.number_input(
                    "Define your categories", 
                    min_value = 2, 
                    max_value = 6, 
                    value     = 6,
                    step      = 2
                )

            if vbreaks == 2:
                default_breaks = [0.0]
            if vbreaks == 4:
                default_breaks = [-2.05, 0.0, 2.05]
            if vbreaks == 6:
                default_breaks = [-4.05, -2.05, 0.0, 2.05, 4.05]
            
            value_breaks = [x/100 for x in default_breaks]

            cls = st.columns(vbreaks-1)
            for i, x in enumerate(cls):
                x.info(
                    f"Value Break #{i+1}: {default_breaks[i]}"
                )
            
            bin_edges  = [floor] + value_breaks + [ceiling]
            bin_labels = []
            for x,y in enumerate(bin_edges):
                if x < len(bin_edges) - 1:
                    b = f"From {y:.2f} to {bin_edges[x+1]:.2f}"
                    bin_labels.append(b)

    st.markdown("""---""")

    # CUSTOMIZATION OPTIONS CONTAINER
    customization = st.container()
    with customization:

        st.markdown(
            "<h4>Step 3: Customize your map</h4>",
            unsafe_allow_html = True
        )
        st.markdown(
            """
            <p class='jtext'>
            You can customize your map by customizing your color gradient, removing the color bar,
            adjusting the output dimensions, the DPI and the border widths.
            </p>
            """,
            unsafe_allow_html = True
        )

        if not delta_bin:
            default_colors = [
                ["#578e7f"],
                ["#E51328", "#578e7f"],
                ["#E51328", "#ccc555", "#578e7f"],
                ["#E51328", "#f2a241", "#ccc555", "#578e7f"],
                ["#E51328", "#f2a241", "#ccc555", "#578e7f", "#012d28"],
                ["#D40276", "#E51328", "#f2a241", "#ccc555", "#578e7f", "#012d28"],
                ["#D40276", "#E51328", "#f2a241", "#ffffff", "#ccc555", "#578e7f", "#012d28"]
            ]
        else:
            default_colors = [
                ["#C41229", "#0559D4"],
                ["#C41229", "#EB6975", "#69A2FF", "#0559D4"],
                ["#C41229", "#EB6975", "#FEBECC", "#B2D3FF", "#69A2FF", "#0559D4"]
            ]

        color_breaks = []

        if not delta_bin:
            ncolors = st.number_input(
                "Select number of color breaks", 2, 7, 6,
                help = "You can select to a maximum of 7 color breaks for your gradient."
            )
        else:
            ncolors = vbreaks
        
        if not delta_bin:
            cindex = int(ncolors-1)
        else:
            cindex = int((ncolors/2)-1)
        
        st.markdown(
            "<b>Select or write down the color codes for your legend</b>:",
            unsafe_allow_html = True
        )
        cols    = st.columns(ncolors)
        for i, x in enumerate(cols):
            input_value = x.color_picker(
                f"Break #{i+1}:", 
                default_colors[cindex][i],
                key = f"break{i}"
            )
            x.write(str(input_value))
            color_breaks.append(input_value)

        color_bar = st.toggle(
            "Display color bar from output", 
            value = True,
            help  = cbar_help
        )

        st.markdown("""<br>""", unsafe_allow_html = True)

        st.markdown("<b>Specify your map dimensions</b>:", unsafe_allow_html = True)
        
        mwidth, mheight, mres, bthick  = st.columns(4)
        with mwidth:
            width_in = st.number_input("Width (inches)", 0, 500, 25)

        with mheight:
            height_in = st.number_input("Height (inches)", 0, 500, 16)
            
        with mres:
            dpi = st.number_input("Dots per inch (DPI)", 0, 250, 100)

        with bthick:
            linewidth = st.number_input(
                "Border width (in points)",
                0.0, 5.0, 0.75,
                help = "The map has a resolution of 72 PPI"
            )

    st.markdown("""---""")

    # OUTPUT CONTAINER
    output = st.container()
        
    with output:
        st.markdown(
            "<h4>Step 4: Draw your map</h4>",
            unsafe_allow_html = True
        )
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
            unsafe_allow_html = True
        )

        if data_input == "Custom Data":
            if uploaded_file is None:
                st.error("Please upload a file to continue", icon = "🚨")
                submit_button = False
        else:
            submit_button = st.button(label = "Display")


    # BACKEND OPERATIONS
    if submit_button:

        if not delta_bin:
            filtered_roli = master_data["roli"][master_data["roli"]["year"] == target_year]
        
        else:
            filtered_roli = master_data["roli"]

            if base_year is not None:
                pattern = str(target_year) + "|" + str(base_year)
                filtered_roli = (
                    filtered_roli[filtered_roli["year"]
                    .str.contains(pattern)]
                )
            
            filtered_roli = (
                filtered_roli
                .sort_values(["country", "year"])
                .set_index(["country", "code", "year", "region"])
                .select_dtypes(np.number)
                .groupby("country")
                .pct_change()
                .reset_index()
            )
            
            filtered_roli = filtered_roli[filtered_roli["year"] == target_year]

            filtered_roli["score"] = filtered_roli[target_variable]
            filtered_roli[target_variable] = (
                pd.cut(filtered_roli[target_variable],
                bins   = bin_edges,
                labels = bin_labels)
            ) 

        data4map = master_data["boundaries"].merge(
            filtered_roli,
            left_on  = "WB_A3", 
            right_on = "code",
            how      = "left"
        )
        
        if extension != "World":
            
            if extension == "Regional":

                regions_coords = (bbox_coords[bbox_coords["region"].isin(selected_regions)])

                min_X = regions_coords.min_X.min()
                min_Y = regions_coords.min_Y.min() 
                max_X = regions_coords.max_X.max() 
                max_Y = regions_coords.max_Y.max() 
                bbox  = box(min_X, min_Y, max_X, max_Y)

            if extension == "Custom":
                bbox  = box(min_lon, min_lat, max_lon, max_lat)
            
            # Masking the world map using the bounding box
            # We also changed the projection to Miller Cilindrical Projection
            # See: https://epsg.io/54003

            data4drawing = data4map[data4map.intersects(bbox)].copy()
            data4drawing.loc[:, "geometry"] = data4drawing.intersection(bbox)
            data4drawing = data4drawing.to_crs("ESRI:54003")
        
        else:
            data4drawing = data4map.copy()
        
        missing_kwds = {
            "color"    : "#EBEBEB",
            "edgecolor": "#EBEBEB",
            "label"    : "Missing values",
            "alpha"    : 1
        }

        colors_list = color_breaks
        cmap_name   = "default_cmap"

        if not delta_bin:
            cmap = colors.LinearSegmentedColormap.from_list(cmap_name, colors_list)
        else:
            value2color     = dict(zip(bin_labels, color_breaks))
            colors_list     = [value2color[value] for value in bin_labels]
            cmap            = colors.ListedColormap(colors_list)
        
        if opac:
            data4drawing["alpha"] = (
                data4drawing["WB_A3"]
                .apply(lambda x: 1 if x in highlighted_countries else 0.2)
            )
        else:
            data4drawing["alpha"] = 1

        if opac and delta_bin:
            data4drawing.loc[~data4drawing["WB_A3"].isin(highlighted_countries), target_variable] = np.nan
        
        map_tab, table_tab, graph_tab = st.tabs(["Map", "Table", "Graph"])


        with map_tab:
            fig, ax = plt.subplots(
                1, 
                figsize = (width_in, height_in),
                dpi     = dpi
            )
            if not delta_bin:
                data4drawing.plot(
                    column       = target_variable, 
                    cmap         = cmap,
                    linewidth    = linewidth,
                    ax           = ax,
                    edgecolor    = "#EBEBEB",
                    legend       = color_bar,
                    vmin         = floor,
                    vmax         = ceiling,
                    alpha        = data4drawing.dropna(subset = ["country"]).alpha,
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
                    alpha        = None,
                    missing_kwds = missing_kwds
                )
            ax.axis("off")

            st.pyplot(fig)

            svg_file = io.StringIO()
            plt.savefig(svg_file, format = "svg")
            
            st.download_button(
                label     = "Save Map", 
                data      = svg_file.getvalue(), 
                file_name = "choropleth_map.svg",
                key       = "download-map"
            )


        with table_tab:

            buffer = io.BytesIO()
            outcome_table = (
                pd.DataFrame(data4drawing.drop(columns = "geometry"))
            )     
            outcome_table = outcome_table[outcome_table["year"] == target_year]
        
            if not delta_bin:
                outcome_table = (
                    outcome_table[["country", "WB_A3", target_variable]]
                    .sort_values(by = "country", ascending = True)
                )
                
            else:
                outcome_table = (
                    outcome_table[["country", "WB_A3", target_variable, "score"]]
                    .sort_values(by = "country", ascending = True)
                )
                original_scores = master_data["roli"][master_data["roli"]["year"] == target_year][["country", "code", target_variable]]
                outcome_table = outcome_table.merge(
                    original_scores[["country", "code", target_variable]],
                    left_on="WB_A3", right_on="code",
                    suffixes=("_pct_change", "_original")
                )
                            
                outcome_table["change"] = outcome_table["score"]
                outcome_table["score"] = outcome_table[f"{target_variable}_original"]
                outcome_table  = outcome_table.rename(
                    columns={
                        "country_pct_change": "country",
                        "roli_pct_change": "roli"
                    }
                )
                outcome_table = outcome_table.drop(
                    columns = ["country_original", "roli_original", "code"]
                )

            if not delta_bin:
                minmax = pd.DataFrame(
                    {
                        "country"       : ["Floor-Ceiling", "Floor-Ceiling"],
                        "WB_A3"         : ["Floor-Ceiling", "Floor-Ceiling"], 
                        target_variable : [floor, ceiling]
                    }
                )

                outcome_table["color_code"] = (
                    outcome_table.apply(
                        lambda row: (
                            colors.rgb2hex(plt.cm.get_cmap(cmap)(row[target_variable]))        
                        ), 
                        axis = 1
                    )
                )
                
                outcome_table = (
                    outcome_table
                    .query("WB_A3 != 'Floor-Ceiling'")
                )
            
            else:
                outcome_table["color_code"] = (
                    outcome_table[target_variable]
                    .map(value2color)
                )

            if extension == "Regional" or extension == "Custom":
                outcome_table = outcome_table[outcome_table["WB_A3"].isin(highlighted_countries)]

            if delta_bin:
                outcome_table = outcome_table.drop(columns=["roli"])
                outcome_table["score"] = outcome_table["score"]*100
                outcome_table["change"] = outcome_table["change"]*100
            st.write(outcome_table)

            # You need to install the XlsxWriter. See: https://xlsxwriter.readthedocs.io/
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                outcome_table.to_excel(writer, sheet_name = "Data-Table")
                writer.close()

            st.download_button(
                label     = "Download Table as an Excel file",
                data      = buffer,
                file_name = "color_map.xlsx",
                mime      = "application/vnd.ms-excel"
            )
        

        with graph_tab:
            
            if not delta_bin:
                h = len(outcome_table)/5
                bars = plt.figure(figsize = (10, h))
                plt.barh(
                    outcome_table["country"],
                    outcome_table[target_variable], 
                    color = outcome_table["color_code"]
                )
                plt.gca().invert_yaxis()
                plt.margins(y = 0)

            else:
                outcome_table = (
                    outcome_table
                    .dropna(subset = ["change", "color_code"])
                    .sort_values("change", ascending = False)
                )
                h = len(outcome_table)/5
                bars = plt.figure(figsize = (10, h))
                plt.barh(
                    outcome_table["country"],
                    outcome_table["change"], 
                    color = outcome_table["color_code"]
                )
                plt.gca().invert_yaxis()
                plt.margins(y = 0)

            plt.title("Scores by Country")
            st.pyplot(bars)
            svg_file = io.StringIO()
            plt.savefig(svg_file, format = "svg")
            
            st.download_button(
                label     = "Save Chart", 
                data      = svg_file.getvalue(), 
                file_name = "bar_chart.svg",
                key       = "download-chart"
            )  

            
