import pystac
from datetime import datetime

pystac.set_stac_version('1.0.0')


def add_themes(collection, themes_to_add):
    '''Add themes to the collection custom fields and add links to the themes collection.'''
    
    themes_list = []
    for theme in themes_to_add:
        
        # assert theme in allowed_themes

        # add the correct link
        collection.add_link(
            pystac.Link(rel="related", 
                        target=f'../../themes/{theme}/catalog.json', 
                        media_type="application/json",
                        title=f"Theme: {theme.capitalize()}")
        )
        
        themes_list.append(
            {
                "scheme": "https://github.com/stac-extensions/osc#theme",
                "concepts": [{"id": theme}]
            }
        )

    # Add themes to the custom fields
    collection.extra_fields.update({
        "themes": themes_list
        }
    )


def add_links(collection, relations, targets, titles):

    '''Add links from the collection to outside websites.'''
    links = []
    
    for rel, target, title in zip(relations, targets, titles):
        links.append(pystac.Link(rel=rel, target=target, title=title)),
    
    collection.add_links(links)


def create_contract(name, roles, emails):
    '''Create a contact template'''
    contact =  {
        "name": name,
        "roles": [r for r in roles]
    }
    if emails:
        contact['emails'] = [{"value":email} for email in emails]
    return contact


def add_product_missions(collection, missions_to_add):
    '''Add missions to the collection custom fields and add links to the missions collection.'''
    
    for mission in missions_to_add:
        
        # add the correct link
        collection.add_link(
            pystac.Link(rel="related", 
                        target=f'../../eo-missions/{mission}/catalog.json', 
                        media_type="application/json",
                        title=f"Mission: {mission.capitalize()}"
            )
        )

    # Add themes to the custom fields
    collection.extra_fields.update({
            "osc:missions": missions_to_add
    }
    )


def add_product_variables(collection, variables_to_add):
    '''Add variables to the collection custom fields and add links to the missions collection.'''
    
    for variable in variables_to_add:
        
        # add the correct link
        collection.add_link(
            pystac.Link(rel="related", 
                        target=f'../../variables/{variable}/catalog.json', 
                        media_type="application/json",
                        title=f"Variable: {' '.join(s.capitalize() for s in variable.split('-')) }")
        )

    # Add themes to the custom fields
    collection.extra_fields.update({
        "osc:variables": variables_to_add
    })


def create_project_collection(project_id, 
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
                              eo4society_link=None):

    '''Create project collection template from the provided information.'''

    # Create the collection
    collection = pystac.Collection(
        id=project_id,
        description=project_description,
        extent=extent,
        license=project_license,
        title=project_title,
        extra_fields = {
            "osc:status": project_status,
            "osc:type": "project",
            "updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        },
        stac_extensions=[
            "https://stac-extensions.github.io/osc/v1.0.0/schema.json",
            "https://stac-extensions.github.io/themes/v1.0.0/schema.json",
            "https://stac-extensions.github.io/contacts/v0.1.1/schema.json"
        ]

    )

    # Add pre-determined links 
    collection.add_links([
        pystac.Link(rel="root", target="../../catalog.json", media_type="application/json", title="Open Science Catalog"),
        pystac.Link(rel="parent", target="../catalog.json", media_type="application/json", title="Projects"),
    ])

    # add the website links
    if eo4society_link is None:
        add_links(collection, ['via', ], [website_link], ["Website"])
    else:
        add_links(collection, ['via', 'via'], [website_link, eo4society_link], ["Website", "EO4Society Link"])

    
    # add the themes
    add_themes(collection, project_themes)

    # add the contacts
    to_contact = [(to_name, ['technical_officer'], [to_email])]
    consortium = [(cm[0], ['consoritum_member'], [cm[1]]) for cm in consortium_members]
    collection.extra_fields.update({

        "contacts": [create_contract(*info) for info in to_contact + consortium]
        
    })

    return collection


def manually_add_product_links(collection, 
                               access_link,
                               documentation_link=None,
                               item_link=None):
     # add extra links
    add_links(collection, ['via'], [access_link], ['Access'])
    if documentation_link:
        add_links(collection,  ['via'], [documentation_link], ['Documentation'])
    if item_link:
        add_links(collection,  ['child'], [item_link], ['Data collection'])


def create_product_collection(product_id, product_title, product_description, 
                              product_extent, product_license,
                              product_keywords, product_status, product_region,
                              product_themes, product_missions, product_variables,
                              project_id, project_title,
                              product_parameters=None, 
                              product_doi=None):
    '''Create a product collection template from the provided information.'''

    collection = pystac.Collection(
            id=product_id,
            title=product_title,
            description=product_description,
            extent=product_extent,
            license=product_license,
            keywords=product_keywords,
            stac_extensions=[
                "https://stac-extensions.github.io/osc/v1.0.0/schema.json",
                "https://stac-extensions.github.io/themes/v1.0.0/schema.json",
                "https://stac-extensions.github.io/cf/v0.2.0/schema.json"
            ],
        )

    # Add pre-determined links 
    collection.add_links([
        pystac.Link(rel="root", target="../../catalog.json", media_type="application/json", title="Open Science Catalog"),
        pystac.Link(rel="parent", target="../catalog.json", media_type="application/json", title="Products"),
        pystac.Link(rel="related", target=f"../../projects/{project_id}/collection.json", media_type="application/json", title=f"Project: {project_title}"),

    ])

    # Add extra properties
    collection.extra_fields.update({
        "osc:project": project_id,
        "osc:status": product_status,
        "osc:region": product_region,
        "osc:type": "product",
        "created": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
    })

    if product_doi is not None:
        collection.extra_fields["sci:doi"] = product_doi


    if product_parameters:
        collection.extra_fields["cf:parameter"] = [{"name": p} for p in product_parameters]

    add_themes(collection, product_themes)

    add_product_missions(collection, product_missions)

    add_product_variables(collection, product_variables)
    
    return collection


def create_workflow_collection(workflow_id, workflow_title, 
                               workflow_description, workflow_license,
                               workflow_keywords, workflow_formats, workflow_themes,
                               codeurl, project_id, project_title, workflow_doi=None):

    '''Create a workflow collection template from the provided information.'''

    collection = {
        'id': workflow_id,
        'type': 'Feature',
        'geometry': None,
        "conformsTo": ["http://www.opengis.net/spec/ogcapi-records-1/1.0/req/record-core"],
        "properties": {
            "title": workflow_title,
            "description": workflow_description,
            "type": "workflow",
            "osc:project": project_id,
            "osc:status": "completed",
            "formats": [{"name": f} for f in workflow_formats],
            "updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "created": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "keywords": workflow_keywords,
            "license": workflow_license,
            "version": "1"
        },
        "linkTemplates": [],
        "links": [
            
            {
                "rel": "root",
                "href": "../../catalog.json",
                "type": "application/json",
                "title": "Open Science Catalog"
            },            
            {
                "rel": "parent",
                "href": "../catalog.json",
                "type": "application/json",
                "title": "Workflows"
            },            

            {
                "rel": "related",
                "href": f"../../projects/{project_id}/collection.json",
                "type": "application/json",
                "title": f"Project: {project_title}"
            },
            {
                "rel": 'git',
                "href": codeurl,
                "type": "application/json",
                "title": 'Git source repository'
            }
            
        ]

    }

    collection['properties']['themes'] = [
        {
            "scheme": "https://github.com/stac-extensions/osc#theme",
            "concepts": [{"id": t} for t in workflow_themes]
        }
    ]

    for t in workflow_themes:
        collection['links'].append(
                {
                        "rel": 'related',
                        "href": f"../../{t}/land/catalog.json",
                        "type": "application/json",
                        "title": f'Theme: {t.capitalize()}'
                    }
    )
        
    if workflow_doi:
        collection['properties']['DOI'] = workflow_doi
    
    return collection


def create_experiment_collection(experiment_id, experiment_title, experiment_description,
                        experiment_license, experiment_keywords, experiment_formats, 
                        experiment_themes, experiment_input_parameters_link, experiment_enviroment_link, 
                        workflow_id, workflow_title, 
                        product_id, product_title, 
                        contacts=None):

    '''Create an experiment record from the provided information.'''

    if contacts is None:
        contacts =  [
            {
                "name": "EarthCODE Demo",
                "organization": "EarthCODE",
                "links": [
                    {
                        "rel": "about",
                        "type": "text/html",
                        "href": "https://opensciencedata.esa.int/"
                    }
                ],
                "contactInstructions": "Contact via EarthCODE",
                "roles": ["host"]
            }
        ]

    # Generate timestamps
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    collection = {
        "id": experiment_id,
        "type": "Feature",
        "conformsTo": [
            "http://www.opengis.net/spec/ogcapi-records-1/1.0/req/record-core"
        ],
        "geometry": None,
        "properties": {
            "created": current_time,
            "updated": current_time,
            "type": "experiment",
            "title": experiment_title,
            "description": experiment_description,
            "keywords": experiment_keywords,
            "contacts": contacts,
            "themes": [
                {
                    "scheme": "https://github.com/stac-extensions/osc#theme",
                    "concepts": [{"id": t} for t in experiment_themes]
                }
            ],
            "formats": [{"name": f} for f in experiment_formats],
            "license": experiment_license,
            "osc:workflow": workflow_id,
        },
        "linkTemplates": [],
        "links": [
            {
                "rel": "root",
                "href": "../../catalog.json",
                "type": "application/json",
                "title": "Open Science Catalog"
            },
            {
                "rel": "parent",
                "href": "../catalog.json",
                "type": "application/json",
                "title": "Experiments"
            },
            {
                "rel": "related",
                "href": f"../../products/{product_id}/collection.json",
                "type": "application/json",
                "title": product_title
            },
            {
            "rel": "related",
            "href": f"../../workflows/{workflow_id}/record.json",
            "type": "application/json",
            "title": f"Workflow: {workflow_title}"
            },
            {
                "rel": "input",
                "href": f"{experiment_input_parameters_link}",
                "type": "application/yaml",
                "title": "Input parameters"
            },
            {
                "rel": "environment",
                "href": f"{experiment_enviroment_link}",
                "type": "application/yaml",
                "title": "Execution environment"
            }
        ]
    }

    # Add Theme links
    for t in experiment_themes:
        collection['links'].append(
            {
                "rel": "related",
                "href": f"../../themes/{t}/catalog.json",
                "type": "application/json",
                "title": f"Theme: {t.capitalize()}"
            }
        )

    return collection


def generate_OSC_dummy_entries(id_extension='+123'):

    # project
    project_id = "4datlantic-ohc" + id_extension
    project_title = "4DAtlantic-OHC" 
    project_description = "Given the major role of the ocean in the climate system, it is essential to characterize the temporal and spatial variations of its heat content. The OHC product results from the space geodetic approach also called altimetry-gravimetry approach."
    project_status = "completed" 
    project_license = "various" 
    project_s, project_w, project_n, project_e = -180.0, -90.0, 180.0, 90.0 
    project_start_year, project_start_month, project_start_day = 2021, 7, 6
    project_end_year, project_end_month, project_end_day = 2025,6,12
    website_link = "https://www.4datlantic-ohc.org/"
    eo4society_link = "https://eo4society.esa.int/projects/4datlantic-ohc/"
    project_themes = ["oceans"]
    to_name, to_email = 'Roberto Sabia', 'roberto.sabia@esa.int'
    consortium_members = [('Magellium', "magellium.fr")]
    spatial_extent = pystac.SpatialExtent([[project_s, project_w, project_n, project_e]])
    temporal_extent = pystac.TemporalExtent(
        [[datetime(project_start_year, project_start_month, project_start_day), 
        datetime(project_end_year, project_end_month, project_end_day)]])
    extent = pystac.Extent(spatial=spatial_extent, temporal=temporal_extent)
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
    # product
    product_id = "4d-atlantic-ohc-global" + id_extension
    product_title = "Global Ocean Heat Content"
    product_description = "Given the major role of the ocean in the climate system, it is essential to characterize the temporal and spatial variations of its heat content. The OHC product results from the space geodetic approach also called altimetry-gravimetry approach. This dataset contains variables as 3D grids of ocean heat content anomalies at 1x1 resolution and monthly time step. Error variance-covariance matrices of OHC at regional scale and annual resolution are also provided. See Experimental Dataset Description for details: https://www.aviso.altimetry.fr/fileadmin/documents/data/tools/OHC-EEI/OHCATL-DT-035-MAG_EDD_V3.0.pdf. Version V3-0 of Dataset published 2025 in ODATIS-AVISO portal. This dataset has been produced within the framework of the 4DAtlantic-Ocean heat content Project funded by ESA."
    product_status = "completed"
    product_license = "various"
    product_keywords = [ 
        "ocean",
        "heat",
        'content'
    ] 
    product_s =  [-180.0]
    product_w = [-90.0]
    product_n = [180.0]
    product_e = [90.0]
    product_start_year, product_start_month, product_start_day = 2021, 1, 1
    product_end_year, product_end_month, product_end_day = 2021,12,31
    product_region = "Global"
    product_themes = ["oceans"]
    product_missions = ['in-situ-observations', 'grace']
    product_variables = ['ocean-heat-budget']
    product_parameters = ['ocean-heat-budget']
    spatial_extent = pystac.SpatialExtent([list(data) for data in zip(product_s, product_w, product_n, product_e)])
    temporal_extent = pystac.TemporalExtent(
        [[datetime(product_start_year, product_start_month, product_start_day), 
        datetime(product_end_year, product_end_month, product_end_day)]])
    product_extent = pystac.Extent(spatial=spatial_extent, temporal=temporal_extent)
    project_id = project_id
    project_title = project_title
    product_collection = create_product_collection(product_id, product_title, product_description, 
                              product_extent, product_license,
                              product_keywords, product_status, product_region,
                              product_themes, product_missions, product_variables,
                              project_id, project_title, product_parameters=product_parameters)
    item_link = 'https://s3.waw4-1.cloudferro.com/EarthCODE/Catalogs/4datlantic-ohc/collection.json'
    access_link = f'https://opensciencedata.esa.int/stac-browser/#/external/{item_link}'
    documentation_link = 'https://www.aviso.altimetry.fr/fileadmin/documents/data/tools/OHC-EEI/OHCATL-DT-035-MAG_EDD_V3.0.pdf'
    manually_add_product_links(product_collection, access_link, documentation_link, item_link,)

    # workflow
    workflow_id = "4datlantic-wf" + id_extension
    workflow_title="4D-Atlantic-Workflow"
    workflow_description="This describes the OHC workflow"
    workflow_keywords= ["ocean", "heat", 'çontent']
    workflow_license = 'CC-BY-4.0' 
    workflow_formats = ['netcdf64']
    workflow_themes = ['oceans']
    workflow_contracts_info = [('Magellium', "contact@magellium.fr")]
    codeurl = 'https://github.com/ESA-EarthCODE/open-science-catalog-metadata'
    workflow_collection = create_workflow_collection(workflow_id, workflow_title, 
                               workflow_description, workflow_license,
                               workflow_keywords, workflow_formats, workflow_themes,
                               codeurl, project_id, project_title)
    

    ### experiment
    # experiment info
    # Experiment id
    experiment_id = "4datlantic-experiment" + id_extension
    experiment_title = "4D-Atlantic-Experiment"
    experiment_description = "This describes the OHC experiment"
    experiment_license = "CC-BY-SA-4.0"
    experiment_keywords = ["ocean", "heat", 'content']

    # Define the input output formats that this experiment works with
    # i.e. GeoTIFF, Zarr, netCDF, etc
    experiment_formats = ["GeoTIFF"] 

    # Define themes i.e. land. Pick one or more from:
    # - atmosphere, cryosphere, land, magnetosphere-ionosphere, oceans, solid-earth.
    experiment_themes = ["oceans"]

    # link to the specification of the input paramters for the experiment
    experiment_input_parameters_link = 'https://github.com/deepesdl/cube-gen'
    # link to the enviroment in which the experiment was performed
    experiment_enviroment_link  = 'https://github.com/deepesdl/cube-gen'

    ## ID and title of the associated workflow
    workflow_id = "4datlantic-wf" + id_extension
    workflow_title = "4D-Atlantic-Workflow"

    ## ID and title title of the associated product
    product_id = "4d-atlantic-ohc-global" + id_extension
    product_title = "Global Ocean Heat Content"

    experiment = create_experiment_collection(
    experiment_id, experiment_title, experiment_description,
    experiment_license, experiment_keywords, experiment_formats, 
    experiment_themes, experiment_input_parameters_link, experiment_enviroment_link, 
    workflow_id, workflow_title, 
    product_id, product_title, 
    )
    
    return project_collection, product_collection, workflow_collection, experiment


def add_item_link_to_product_collection(product_collection, item_id, item_title):

    product_collection.add_link(
        pystac.Link(
            rel='item', target=f'./{item_id}.json', 
            media_type='application/json', 
            title=item_title
        )
    )


def create_item(itemid, geometry, data_time, bbox, product_id, 
                license, description, data_url, data_mime_type, 
                data_title, extra_fields=None):
    
    item = pystac.Item(
        id=itemid,
        geometry=geometry,
        datetime=data_time,
        bbox=bbox,
        collection=product_id,
        properties= {
            "license": license,
            "description": description,
        }
    )

    # 3. add an asset (the actual link to the file)
    item.add_asset(
        key="data",
        asset=pystac.Asset(
            href=data_url,
            media_type=data_mime_type,
            roles=["data"],
            title=data_title
        )
    )

    for k,v in extra_fields.items():
        item.extra_fields[k] = v

    return item
