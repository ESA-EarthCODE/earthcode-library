import pystac
from datetime import datetime

from earthcode.static import (
    create_product_collection, 
    create_project_collection, 
    create_workflow_collection,
    create_experiment_collection,
    generate_OSC_dummy_entries
)




def test_project_ohc():
    # Define id, title, description, project status, license
    # a custom id of the project, it can be related to the title
    project_id = "4datlantic-ohc" 
    # the title of your project
    project_title = "4DAtlantic-OHC" 
    project_description = "Given the major role of the ocean in the climate system, it is essential to characterize the temporal and spatial variations of its heat content. The OHC product results from the space geodetic approach also called altimetry-gravimetry approach." # a description of the project
    project_status = "completed" # project status, pick from - ongoing, completed

    # overall license for all related data that will be uploaded from the project., i.e. CC-BYB4.0
    # if you have multiple licenses, you can pick 'various'
    project_license = 'proprietary' 

    # Define spatial extent of the project study area in epsg:4326
    # if you have multiple disjoint study areas, specify the bounding box that covers all of them
    # i.e project_s, project_w, project_n, project_e = -180.0, -90.0, 180.0, 90.0 
    project_s, project_w, project_n, project_e = -180.0, -90.0, 180.0, 90.0 

    # the project start and end times
    project_start_year, project_start_month, project_start_day = 2021, 7, 6
    project_end_year, project_end_month, project_end_day = 2025,6,12

    # Define the links to the project website and  EO4SocietyLink
    website_link = "https://www.4datlantic-ohc.org/"
    eo4society_link = "https://eo4society.esa.int/projects/4datlantic-ohc/"

    # Define project themes. Pick one or more from:
    # - atmosphere, cryosphere, land, magnetosphere-ionosphere, oceans, solid-earth.
    project_themes = ["oceans"]

    # provide the TO name and TO email
    to_name, to_email = 'Roberto Sabia', 'roberto.sabia@esa.int'

    # List the consortium members in a tuple with format (name, contact_email), for example - ('Magellium', "magellium.fr")
    consortium_members = [('Magellium', "magellium.fr")]

    # combine the spatial and temporal extent
    spatial_extent = pystac.SpatialExtent([[project_s, project_w, project_n, project_e]])
    temporal_extent = pystac.TemporalExtent(
        [[datetime(project_start_year, project_start_month, project_start_day), 
        datetime(project_end_year, project_end_month, project_end_day)]])
    extent = pystac.Extent(spatial=spatial_extent, temporal=temporal_extent)

    # generate project collection
    project_collection = create_project_collection(project_id, 
                                project_title,
                                project_description, 
                                project_status,
                                project_license,
                                extent,
                                project_themes,
                                to_name,
                                to_email,
                                consortium_members,
                                website_link,
                                eo4society_link=eo4society_link)
    project_collection.validate()



def test_product_ohc():
    # Define id, title, description, project status, license
    product_id = "4d-atlantic-ohc-global"
    product_title = "Global Ocean Heat Content"
    product_description = "Given the major role of the ocean in the climate system, it is essential to characterize the temporal and spatial variations of its heat content. The OHC product results from the space geodetic approach also called altimetry-gravimetry approach. This dataset contains variables as 3D grids of ocean heat content anomalies at 1x1 resolution and monthly time step. Error variance-covariance matrices of OHC at regional scale and annual resolution are also provided. See Experimental Dataset Description for details: https://www.aviso.altimetry.fr/fileadmin/documents/data/tools/OHC-EEI/OHCATL-DT-035-MAG_EDD_V3.0.pdf. Version V3-0 of Dataset published 2025 in ODATIS-AVISO portal. This dataset has been produced within the framework of the 4DAtlantic-Ocean heat content Project funded by ESA."
    product_status = "completed"

    # Define the product license
    product_license = 'proprietary'

    # Define at most five keywords for the product
    product_keywords = [ 
        "ocean",
        "heat",
        'content'
    ] 

    # Define spatial  in epsg:4326. If the dataset covers discontinuous regions,
    # add the bounding box boundaries for each
    # i..e a dataset with global coverage is:product_s product_w, product_n, product_e = [-180.0], [-90.0], [180.0], [90.0]
    product_s =  [-180.0]
    product_w = [-90.0]
    product_n = [180.0]
    product_e = [90.0]

    # Define the temporal extent
    product_start_year, product_start_month, product_start_day = 2021, 1, 1
    product_end_year, product_end_month, product_end_day = 2021,12,31


    # define the semantic region covered by this product, i.e. Belgium
    product_region = "Global"

    # Define project themes i.e. land. Pick one or more from:
    # - atmosphere, cryosphere, land, magnetosphere-ionosphere, oceans, solid-earth.
    product_themes = ["oceans"]

    # Define the EO misisons used in the product. i.e. - "sentinel-2", sentinel-1
    # Pick one or more from - https://github.com/ESA-EarthCODE/open-science-catalog-metadata/tree/main/eo-missions
    product_missions = ['in-situ-observations', 'grace']

    # define output variables and input parameters, i.e. "crop-yield-forecast"
    # Pick one or more from from https://github.com/ESA-EarthCODE/open-science-catalog-metadata/tree/main/variables
    # If you dont think, your parameters or variables are available, send us a description and name of them and we can add them to the list
    product_variables = ['ocean-heat-budget']
    product_parameters = ['ocean-heat-budget']

    # Define doi if available, i.e. "https://doi.org/10.57780/s3d-83ad619" else None
    product_doi = None

    # Define the related project id and title
    # these have to match the new or an already existing project in the catalog
    project_id = '4d-atlantic-ohc'
    project_title = '4D Atlantic OHC'

    # combine the spatial and temporal extent
    spatial_extent = pystac.SpatialExtent([list(data) for data in zip(product_s, product_w, product_n, product_e)])
    temporal_extent = pystac.TemporalExtent(
        [[datetime(product_start_year, product_start_month, product_start_day), 
        datetime(product_end_year, product_end_month, product_end_day)]])
    product_extent = pystac.Extent(spatial=spatial_extent, temporal=temporal_extent)

    product_collection = create_product_collection(product_id, product_title, product_description, 
                                product_extent, product_license,
                                product_keywords, product_status, product_region,
                                product_themes, product_missions, product_variables,
                                project_id, project_title,)
    
    from earthcode.static import manually_add_product_links
    # Define the relevant data links to be manually added
    # link to an external data collection if available. If not, leave as None
    item_link = 'https://s3.waw4-1.cloudferro.com/EarthCODE/Catalogs/4datlantic-ohc/collection.json'
    # Link to accessing the data, this link is required. Leave as None, if you are adding children in this notebook.
    access_link = f'https://opensciencedata.esa.int/stac-browser/#/external/{item_link}'
    #Link to the documentation, leave as None, if not available
    documentation_link = 'https://www.aviso.altimetry.fr/fileadmin/documents/data/tools/OHC-EEI/OHCATL-DT-035-MAG_EDD_V3.0.pdf'


    manually_add_product_links(product_collection, access_link, documentation_link, item_link,)

    product_collection.validate()


def test_workflow_ohc():
    # Define id, title, description, keywords, license
    workflow_id = "4datlantic-wf"
    workflow_title="4D-Atlantic-Workflow"
    workflow_description="This describes the OHC workflow"
    workflow_keywords= ["ocean", "heat", 'çontent']
    workflow_license = 'CC-BYB4.0' 

    # what data the workflow takes as input and output, i.e. GeoTIFF, Netcdf
    workflow_formats = ['netcdf64']

    # Define which project the workflow is associated with
    # if are adding to an existing project see the id and titles from here:
    # - https://github.com/ESA-EarthCODE/open-science-catalog-metadata/projects/
    project_id = "4datlantic-ohc"
    project_title = "4D Atlantic OHC"


    # Define themes i.e. land. Pick one or more from:
    # - atmosphere, cryosphere, land, magnetosphere-ionosphere, oceans, solid-earth.
    workflow_themes = ['oceans']


    # # List the contacts in a tuple with format (name, contact_email), for example - ('Magellium', "contact@magellium.fr")
    workflow_contracts_info = [('Magellium', "contact@magellium.fr")]

    # Define the code url, i.e. https://github.com/ESA-EarthCODE/open-science-catalog-metadata
    codeurl = 'https://github.com/ESA-EarthCODE/open-science-catalog-metadata'

    workflow_collection = create_workflow_collection(workflow_id, workflow_title, 
                                workflow_description, workflow_license,
                                workflow_keywords, workflow_formats, workflow_themes,
                                codeurl, project_id, project_title)
    

def test_generate_dummy():
    project, product ,workflow, experiment = generate_OSC_dummy_entries()