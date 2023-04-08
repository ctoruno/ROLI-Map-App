import io
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import streamlit as st

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
    boundaries = gpd.read_file("Data/data4app.geojson")
    roli_data  = pd.read_excel("Data/ROLI_data.xlsx")
    data       = {"boundaries": boundaries,
                  "roli": roli_data}
    return data 

master_data = load_data()
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

# Intro text
st.title("ROLI Map Generator")
st.markdown(
    """
    <p class='jtext'>
    This is an interactive app designed to display and generate <b style="color:#003249">Choropleth Maps</b> using the WJP's Rule of Law Index. 
    This app is still under deevelopment. Therefore, customization is limited at the moment. However, the data
    presented in this app is up-to-date to the latest datasets published by the World Justice Project in its website.
    </p>
    
    <p class='jtext'>
    In order to generate a map, follow the next steps:
    </p>

    <ol>
        <li class='jtext'>
            Select the extension of the map. It can be either global or limited to a specific region.
        </li>
        <li class='jtext'>
            Select a variable and year from the dropdown menu.
        </li>
        <li class='jtext'>
            Fill in the customization options.
        </li>
        <li class='jtext'>
            Click on the <b style="color:#003249">"Let's rock!!"</b> button to visualize your map.
        </li>
        <li class='jtext'>
            If you like the map and you would like to save it as a SVG file, click on the 
            <b style="color:#003249">"I love it!! Please save it"</b> button.
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

# Creating a container for the general options
goptions_container = st.container()
with goptions_container:

    # Inputs Box Title
    st.markdown("<h4>General Options:</h4>",
                    unsafe_allow_html = True)
        
    # Extension input
    extension = st.radio("Select an extension for your map:", 
                        ["World", "Regional"],
                        horizontal = True)

    # Possible Regions
    regions = ["The Americas", "Eurasia and Africa",  "East Asia and Pacific", "Eastern Europe and Central Asia", 
            "EU, EFTA, and North America", "Latin America and Caribbean", "Middle East and North Africa",
            "South Asia", "Sub-Saharan Africa"]

    extension_container = st.empty()

    # Conditional display
    if extension == "Regional":
        
        # Dropdown menu for regions
        region = extension_container.selectbox("Select a region:", 
                                               regions)
    else:
        region = None

# Search Box Inputs
with st.form(key = "inputsForm"):
    st.markdown("<h4>What are we mapping?</h4>",
                unsafe_allow_html = True)
    
    # Searchbox to define a target variable
    available_variables = dict(zip(master_data["roli"].iloc[:, 4:].columns.tolist(),
                                   variable_labels))
    available_years = master_data["roli"]["year"].unique().tolist()
    target_variable = st.selectbox("Select a variable from the following list:",
                                   list(available_variables.keys()),
                                   format_func=lambda x: available_variables[x])
    target_year     = st.selectbox("Select which year do you want to display from the following list:",
                                   available_years)
    
    # Container for cutomizing options
    with st.expander("Do you want to customize your map?"):

        # Defining default colors
        default_colors = [["#B49A67"],
                          ["#B49A67", "#001A23"],
                          ["#98473E", "#B49A67", "#001A23"],
                          ["#98473E", "#B49A67", "#395E66", "#001A23"],
                          ["#98473E", "#B49A67", "#7A9E7E", "#395E66", "#001A23"]]
        
        color_breaks = []
        
        # Dropdown menu for number of color breaks
        ncolors = st.number_input("Select number of color breaks", 2, 5, 4)
        st.markdown("<b>Select or write down the color codes for your legend</b>:",
                    unsafe_allow_html = True)
        cols    = st.columns(ncolors)

        for i, x in enumerate(cols):
            input_value = x.color_picker(f"Break #{i+1}:", 
                                         default_colors[ncolors-1][i],
                                         key = f"break{i}")
            x.write(str(input_value))
            color_breaks.append(input_value)
        
        # Update customization button
        custom_button = st.form_submit_button(label = "Update my custom settings please")

    # Generate Button
    st.write("Don't forget to update your custom settings if you want to rock...")
    submit_button = st.form_submit_button(label = "Let's rock!!")

# Server
if submit_button:

    # Filtering ROLI Data
    filtered_roli = master_data["roli"][master_data["roli"]['year'] == target_year]

    # Merge the two DataFrames on a common column
    data4map = master_data["boundaries"].merge(filtered_roli,
                                               left_on  = "shapeGroup", 
                                               right_on = "code",
                                               how      = "left")
    
    # Parameters for missing values
    missing_kwds = {
        "color": "#EBEBEB",
        "edgecolor": "white",
        "label": "Missing values"
    }

    # Default colors
    # Create a custom colormap
    colors_list = color_breaks
    cmap_name   = "default_cmap"
    cmap        = colors.LinearSegmentedColormap.from_list(cmap_name, colors_list)

    # Drawing map with matplotlib
    fig, ax = plt.subplots(1, figsize=(25, 16))
    data4map.plot(column       = target_variable, 
                  cmap         = cmap, 
                  linewidth    = 0.5, 
                  ax           = ax, 
                  edgecolor    = "white", 
                  legend       = True,
                  missing_kwds = missing_kwds)
    ax.axis("off")
    st.pyplot(fig)

    # Export image as SVG file
    svg_file = io.StringIO()
    plt.savefig(svg_file, 
                format = "svg")
    st.download_button(label     = "I love it!! Please save it", 
                        data      = svg_file.getvalue(), 
                        file_name = "choropleth_map.svg")




