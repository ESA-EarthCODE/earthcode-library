from earthcode.metadata_input_definitions import (
    ProductCollectionMetadata,
    ProjectCollectionMetadata,
)
from earthcode.static import create_product_collection, create_project_collection


def osc_project_from_prr(
    prr_collection,  
    project_id,
    project_status,
    technical_officer,
    consortium_members,
    project_start_datetime,
    project_end_datetime,
    project_bbox):
    """"Extract as much data as possible from a PRR collection and return an OSC project."""

    themes = [
        concept["id"]
        for theme in prr_collection["themes"]
        if theme["scheme"] == "https://github.com/stac-extensions/osc#theme"
        for concept in theme["concepts"]
    ]

    project = create_project_collection(
            ProjectCollectionMetadata(
                project_id=project_id,
                project_title=prr_collection["osc:project"],
                project_description=prr_collection["osc:project_description"],
                project_status=project_status,
                project_license=prr_collection["license"],
                project_bbox=project_bbox,
                project_start_datetime=project_start_datetime,
                project_end_datetime=project_end_datetime,
                project_themes=themes,
                to_name=technical_officer[0],
                to_email=technical_officer[1],
                consortium_members=list(consortium_members),
                website_link=prr_collection["osc:project_website"],
            )
        )

    return project


def osc_product_from_prr(prr_collection, prr_collection_url, product_missions, product_variables, project_id):
    """"Extract as much data as possible from a PRR collection and return the OSC product equivalent collection."""
    product_id = prr_collection["id"]
    product_title = prr_collection["title"]
    project_title = prr_collection["osc:project"]
    bbox = prr_collection["extent"]["spatial"]["bbox"]
    start, end = prr_collection["extent"]["temporal"]["interval"][0]
    themes = [
        concept["id"]
        for theme in prr_collection["themes"]
        if theme["scheme"] == "https://github.com/stac-extensions/osc#theme"
        for concept in theme["concepts"]
    ]
    product_status = 'completed'

    parameters = [entry["name"] for entry in prr_collection.get("cf:parameter", [])]
    product = create_product_collection(
        ProductCollectionMetadata(
            product_id=product_id,
            product_title=product_title,
            product_description=prr_collection["description"],
            product_bbox=bbox,
            product_start_datetime=start,
            product_end_datetime=end,
            product_license=prr_collection["license"],
            product_keywords=prr_collection.get("keywords"),
            product_status=product_status,
            product_region=prr_collection.get("osc:region"),
            product_themes=themes,
            product_missions=list(product_missions),
            product_variables=list(product_variables),
            project_id=project_id,
            project_title=prr_collection["osc:project"],
            product_parameters=parameters or None,
            product_doi=prr_collection.get("sci:doi"),
            access_link=prr_collection_url,
            item_link=prr_collection_url,
            item_title=product_title,
        )
    )
    return product