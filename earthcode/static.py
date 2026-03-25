from __future__ import annotations

from datetime import datetime, timezone

import pystac
from pystac.extensions.scientific import ScientificExtension

from earthcode.metadata_input_definitions import (
    ExperimentMetadata,
    ItemMetadata,
    ProductCollectionMetadata,
    ProjectCollectionMetadata,
    WorkflowMetadata,
)

OSC_SCHEMA_URI = "https://stac-extensions.github.io/osc/v1.0.0/schema.json"
THEMES_SCHEMA_URI = "https://stac-extensions.github.io/themes/v1.0.0/schema.json"
CONTACTS_SCHEMA_URI = "https://stac-extensions.github.io/contacts/v0.1.1/schema.json"
CF_SCHEMA_URI = "https://stac-extensions.github.io/cf/v0.2.0/schema.json"
THEMES_SCHEME_URI = "https://github.com/stac-extensions/osc#theme"

## need to force pystac to respect 1.0.0
pystac.set_stac_version('1.0.0')


def _build_extent(bboxes: list[list[float]], start_datetime: datetime, end_datetime: datetime) -> pystac.Extent:
    """Builds a STAC extent object from bbox coordinates and start/end datetimes."""

    return pystac.Extent(
        spatial=pystac.SpatialExtent(bboxes),
        temporal=pystac.TemporalExtent([[start_datetime, end_datetime]]),
    )


def _add_links(collection: pystac.Collection, relations: list[str], targets: list[str], titles: list[str]) -> None:
    """Adds a batch of links from relation, target, and title lists."""

    links = [pystac.Link(rel=rel, target=target, title=title) for rel, target, title in zip(relations, targets, titles)]
    collection.add_links(links)


def _ensure_extension(collection: pystac.Collection, schema_uri: str) -> None:
    """Adds a schema URI to collection extensions if it is not already present."""

    if schema_uri not in collection.stac_extensions:
        collection.stac_extensions.append(schema_uri)


def _set_osc_fields(
    collection: pystac.Collection,
    *,
    project: str | None = None,
    status: str | None = None,
    region: str | None = None,
    osc_type: str | None = None,
) -> None:
    """Sets OSC core properties on a collection and ensures OSC extension registration."""

    _ensure_extension(collection, OSC_SCHEMA_URI)
    if project is not None:
        collection.extra_fields["osc:project"] = project
    if status is not None:
        collection.extra_fields["osc:status"] = status
    if region is not None:
        collection.extra_fields["osc:region"] = region
    if osc_type is not None:
        collection.extra_fields["osc:type"] = osc_type


def _apply_themes(collection: pystac.Collection, theme_ids: list[str]) -> None:
    """Adds theme links and writes themes metadata to a collection."""

    _ensure_extension(collection, THEMES_SCHEMA_URI)

    themes_list = []
    for theme in theme_ids:
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


def _apply_missions(collection: pystac.Collection, mission_ids: list[str]) -> None:
    """Adds mission links and OSC missions metadata to a collection."""

    _ensure_extension(collection, OSC_SCHEMA_URI)
    for mission in mission_ids:
        collection.add_link(
            pystac.Link(
                rel="related",
                target=f"../../eo-missions/{mission}/catalog.json",
                media_type="application/json",
                title=f"Mission: {mission.capitalize()}",
            )
        )
    collection.extra_fields["osc:missions"] = mission_ids


def _apply_variables(collection: pystac.Collection, variable_ids: list[str]) -> None:
    """Adds variable links and OSC variables metadata to a collection."""

    _ensure_extension(collection, OSC_SCHEMA_URI)
    for variable in variable_ids:
        collection.add_link(
            pystac.Link(
                rel="related",
                target=f"../../variables/{variable}/catalog.json",
                media_type="application/json",
                title=f"Variable: {' '.join(segment.capitalize() for segment in variable.split('-'))}",
            )
        )
    collection.extra_fields["osc:variables"] = variable_ids


def _create_contact(name: str, roles: list[str], emails: list[str] | None = None) -> dict:
    """Builds a contacts entry with optional email objects."""

    contact = {"name": name, "roles": [role for role in roles]}
    if emails:
        contact["emails"] = [{"value": email} for email in emails]
    return contact


def _apply_project_contacts(
    collection: pystac.Collection, technical_officer_name: str, technical_officer_email: str, consortium_members: list[tuple[str, str]]
) -> None:
    """Builds and writes project contacts from technical officer and consortium members."""

    _ensure_extension(collection, CONTACTS_SCHEMA_URI)
    to_contact = _create_contact(technical_officer_name, ["technical_officer"], [technical_officer_email])
    consortium_contacts = [_create_contact(name, ["consoritum_member"], [email]) for name, email in consortium_members]
    collection.extra_fields["contacts"] = [to_contact] + consortium_contacts


def _apply_cf_parameters(collection: pystac.Collection, parameter_names: list[str]) -> None:
    """Writes CF parameter metadata to a collection."""

    _ensure_extension(collection, CF_SCHEMA_URI)
    collection.extra_fields["cf:parameter"] = [{"name": parameter_name} for parameter_name in parameter_names]


def create_project_collection(project_metadata: ProjectCollectionMetadata) -> pystac.Collection:
    """Creates an OSC project collection from validated metadata inputs."""

    extent = _build_extent(
        bboxes=project_metadata.project_bbox,
        start_datetime=project_metadata.project_start_datetime,
        end_datetime=project_metadata.project_end_datetime,
    )

    collection = pystac.Collection(
        id=project_metadata.project_id,
        description=project_metadata.project_description,
        extent=extent,
        license=project_metadata.project_license,
        title=project_metadata.project_title,
    )

    common = pystac.CommonMetadata(collection)
    now = datetime.now(timezone.utc)
    common.created = now
    common.updated = now

    _set_osc_fields(collection, status=project_metadata.project_status, osc_type="project")

    collection.add_links(
        [
            pystac.Link(rel="root", target="../../catalog.json", media_type="application/json", title="Open Science Catalog"),
            pystac.Link(rel="parent", target="../catalog.json", media_type="application/json", title="Projects"),
        ]
    )

    if project_metadata.eo4society_link is None:
        _add_links(collection, ["via"], [project_metadata.website_link], ["Website"])
    else:
        _add_links(
            collection,
            ["via", "via"],
            [project_metadata.website_link, project_metadata.eo4society_link],
            ["Website", "EO4Society Link"],
        )

    _apply_themes(collection, project_metadata.project_themes)

    _apply_project_contacts(
        technical_officer_name=project_metadata.to_name,
        technical_officer_email=project_metadata.to_email,
        collection=collection,
        consortium_members=project_metadata.consortium_members,
    )

    return collection


def manually_add_product_links(collection: pystac.Collection, product_metadata: ProductCollectionMetadata) -> None:
    """Adds access, documentation, and child data links from product metadata."""

    if product_metadata.access_link:
        _add_links(collection, ["via"], [product_metadata.access_link], ["Access"])
    if product_metadata.documentation_link:
        _add_links(collection, ["via"], [product_metadata.documentation_link], ["Documentation"])
    if product_metadata.item_link:
        _add_links(collection, ["child"], [product_metadata.item_link], [product_metadata.item_title])
    if product_metadata.license_link and product_metadata.product_license == 'other':
        _add_links(collection, ["license"], [product_metadata.license_link], ["License"])


def create_product_collection(product_metadata: ProductCollectionMetadata) -> pystac.Collection:
    """Creates an OSC product collection from validated metadata inputs."""

    extent = _build_extent(
        bboxes=product_metadata.product_bbox,
        start_datetime=product_metadata.product_start_datetime,
        end_datetime=product_metadata.product_end_datetime,
    )

    collection = pystac.Collection(
        id=product_metadata.product_id,
        title=product_metadata.product_title,
        description=product_metadata.product_description,
        extent=extent,
        license=product_metadata.product_license,
        keywords=product_metadata.product_keywords,
    )

    collection.add_links(
        [
            pystac.Link(rel="root", target="../../catalog.json", media_type="application/json", title="Open Science Catalog"),
            pystac.Link(rel="parent", target="../catalog.json", media_type="application/json", title="Products"),
            pystac.Link(
                rel="related",
                target=f"../../projects/{product_metadata.project_id}/collection.json",
                media_type="application/json",
                title=f"Project: {product_metadata.project_title}",
            ),
        ]
    )

    common = pystac.CommonMetadata(collection)
    now = datetime.now(timezone.utc)
    common.created = now
    common.updated = now

    _set_osc_fields(
        collection,
        project=product_metadata.project_id,
        status=product_metadata.product_status,
        region=product_metadata.product_region,
        osc_type="product",
    )
    _apply_missions(collection, product_metadata.product_missions)
    _apply_variables(collection, product_metadata.product_variables)
    _apply_themes(collection, product_metadata.product_themes)

    if product_metadata.product_doi is not None:
        _ensure_extension(collection, "https://stac-extensions.github.io/scientific/v1.0.0/schema.json")
        ScientificExtension.ext(collection, add_if_missing=True).doi = product_metadata.product_doi

    if product_metadata.product_parameters:
        _apply_cf_parameters(collection, product_metadata.product_parameters)

    manually_add_product_links(collection, product_metadata)

    return collection


def create_workflow_record(workflow_metadata: WorkflowMetadata) -> dict:
    """Creates an OSC workflow record dictionary from validated metadata inputs."""

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    collection = {
        "id": workflow_metadata.workflow_id,
        "type": "Feature",
        "geometry": None,
        "conformsTo": ["http://www.opengis.net/spec/ogcapi-records-1/1.0/req/record-core"],
        "properties": {
            "title": workflow_metadata.workflow_title,
            "description": workflow_metadata.workflow_description,
            "type": "workflow",
            "osc:project": workflow_metadata.project_id,
            "osc:status": "completed",
            "formats": [{"name": format_name} for format_name in workflow_metadata.workflow_formats],
            "updated": now,
            "created": now,
            "keywords": workflow_metadata.workflow_keywords,
            "license": workflow_metadata.workflow_license,
            "version": "1",
            "themes": [
                {
                    "scheme": THEMES_SCHEME_URI,
                    "concepts": [{"id": theme_id} for theme_id in workflow_metadata.workflow_themes],
                }
            ],
        },
        "linkTemplates": [],
        "links": [
            {"rel": "root", "href": "../../catalog.json", "type": "application/json", "title": "Open Science Catalog"},
            {"rel": "parent", "href": "../catalog.json", "type": "application/json", "title": "Workflows"},
            {
                "rel": "related",
                "href": f"../../projects/{workflow_metadata.project_id}/collection.json",
                "type": "application/json",
                "title": f"Project: {workflow_metadata.project_title}",
            },
            {"rel": "git", "href": workflow_metadata.codeurl, "type": "application/json", "title": "Git source repository"},
        ],
    }

    for theme_id in workflow_metadata.workflow_themes:
        collection["links"].append(
            {
                "rel": "related",
                "href": f"../../themes/{theme_id}/catalog.json",
                "type": "application/json",
                "title": f"Theme: {theme_id.capitalize()}",
            }
        )

    if workflow_metadata.workflow_doi:
        collection["properties"]["DOI"] = workflow_metadata.workflow_doi

    if workflow_metadata.workflow_bbox:
        collection["bbox"] = workflow_metadata.workflow_bbox[0]

    if workflow_metadata.workflow_start_datetime:
        collection["properties"]["start_datetime"] = workflow_metadata.workflow_start_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")

    if workflow_metadata.workflow_end_datetime:
        collection["properties"]["end_datetime"] = workflow_metadata.workflow_end_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")

    return collection


def create_experiment_record(experiment_metadata: ExperimentMetadata) -> dict:
    """Creates an OSC experiment record dictionary from validated metadata inputs."""

    contacts_payload = experiment_metadata.contacts
    if contacts_payload is None:
        contacts_payload = [
            {
                "name": "EarthCODE Demo",
                "organization": "EarthCODE",
                "links": [{"rel": "about", "type": "text/html", "href": "https://opensciencedata.esa.int/"}],
                "contactInstructions": "Contact via EarthCODE",
                "roles": ["host"],
            }
        ]

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    collection = {
        "id": experiment_metadata.experiment_id,
        "type": "Feature",
        "conformsTo": ["http://www.opengis.net/spec/ogcapi-records-1/1.0/req/record-core"],
        "geometry": None,
        "properties": {
            "created": now,
            "updated": now,
            "type": "experiment",
            "title": experiment_metadata.experiment_title,
            "description": experiment_metadata.experiment_description,
            "keywords": experiment_metadata.experiment_keywords,
            "contacts": contacts_payload,
            "themes": [
                {
                    "scheme": THEMES_SCHEME_URI,
                    "concepts": [{"id": theme_id} for theme_id in experiment_metadata.experiment_themes],
                }
            ],
            "formats": [{"name": format_name} for format_name in experiment_metadata.experiment_formats],
            "license": experiment_metadata.experiment_license,
            "osc:workflow": experiment_metadata.workflow_id,
        },
        "linkTemplates": [],
        "links": [
            {"rel": "root", "href": "../../catalog.json", "type": "application/json", "title": "Open Science Catalog"},
            {"rel": "parent", "href": "../catalog.json", "type": "application/json", "title": "Experiments"},
            {
                "rel": "related",
                "href": f"../../products/{experiment_metadata.product_id}/collection.json",
                "type": "application/json",
                "title": experiment_metadata.product_title,
            },
            {
                "rel": "related",
                "href": f"../../workflows/{experiment_metadata.workflow_id}/record.json",
                "type": "application/json",
                "title": f"Workflow: {experiment_metadata.workflow_title}",
            },
            {
                "rel": "input",
                "href": experiment_metadata.experiment_input_parameters_link,
                "type": "application/yaml",
                "title": "Input parameters",
            },
            {
                "rel": "environment",
                "href": experiment_metadata.experiment_enviroment_link,
                "type": "application/yaml",
                "title": "Execution environment",
            },
        ],
    }

    for theme_id in experiment_metadata.experiment_themes:
        collection["links"].append(
            {
                "rel": "related",
                "href": f"../../themes/{theme_id}/catalog.json",
                "type": "application/json",
                "title": f"Theme: {theme_id.capitalize()}",
            }
        )

    if experiment_metadata.experiment_bbox:
        collection["bbox"] = experiment_metadata.experiment_bbox[0]

    if experiment_metadata.experiment_start_datetime:
        collection["properties"]["start_datetime"] = experiment_metadata.experiment_start_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")

    if experiment_metadata.experiment_end_datetime:
        collection["properties"]["end_datetime"] = experiment_metadata.experiment_end_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")

    return collection


def generate_OSC_dummy_entries(id_extension: str = "+123"):
    """Generates demo OSC project, product, workflow, and experiment records."""

    project_id = "4datlantic-ohc" + id_extension
    project_title = "4DAtlantic-OHC"

    project_collection = create_project_collection(
        ProjectCollectionMetadata(
            project_id=project_id,
            project_title=project_title,
            project_description=(
                "Given the major role of the ocean in the climate system, it is essential to characterize "
                "the temporal and spatial variations of its heat content."
            ),
            project_status="completed",
            project_license="various",
            project_bbox=[[-180.0, -90.0, 180.0, 90.0]],
            project_start_datetime=datetime(2021, 7, 6),
            project_end_datetime=datetime(2025, 6, 12),
            project_themes=["oceans"],
            to_name="Roberto Sabia",
            to_email="roberto.sabia@esa.int",
            consortium_members=[("Magellium", "magellium.fr")],
            website_link="https://www.4datlantic-ohc.org/",
            eo4society_link="https://eo4society.esa.int/projects/4datlantic-ohc/",
        )
    )

    product_id = "4d-atlantic-ohc-global" + id_extension
    product_collection = create_product_collection(
        ProductCollectionMetadata(
            product_id=product_id,
            product_title="Global Ocean Heat Content",
            product_description="Given the major role of the ocean in the climate system.",
            product_bbox=[[-180.0, -90.0, 180.0, 90.0]],
            product_start_datetime=datetime(2021, 1, 1),
            product_end_datetime=datetime(2021, 12, 31),
            product_license="various",
            product_keywords=["ocean", "heat", "content"],
            product_status="completed",
            product_region="Global",
            product_themes=["oceans"],
            product_missions=["in-situ-observations", "grace"],
            product_variables=["ocean-heat-budget"],
            project_id=project_id,
            project_title=project_title,
            product_parameters=["ocean-heat-budget"],
            access_link="https://opensciencedata.esa.int/stac-browser/#/external/https://s3.waw4-1.cloudferro.com/EarthCODE/Catalogs/4datlantic-ohc/collection.json",
            documentation_link="https://www.aviso.altimetry.fr/fileadmin/documents/data/tools/OHC-EEI/OHCATL-DT-035-MAG_EDD_V3.0.pdf",
            item_link="https://s3.waw4-1.cloudferro.com/EarthCODE/Catalogs/4datlantic-ohc/collection.json",
        )
    )

    workflow_id = "4datlantic-wf" + id_extension
    workflow_title = "4D-Atlantic-Workflow"
    workflow_collection = create_workflow_record(
        WorkflowMetadata(
            workflow_id=workflow_id,
            workflow_title=workflow_title,
            workflow_description="This describes the OHC workflow",
            workflow_license="CC-BY-4.0",
            workflow_keywords=["ocean", "heat", "content"],
            workflow_formats=["netcdf64"],
            workflow_themes=["oceans"],
            codeurl="https://github.com/ESA-EarthCODE/open-science-catalog-metadata",
            project_id=project_id,
            project_title=project_title,
        )
    )

    experiment = create_experiment_record(
        ExperimentMetadata(
            experiment_id="4datlantic-experiment" + id_extension,
            experiment_title="4D-Atlantic-Experiment",
            experiment_description="This describes the OHC experiment",
            experiment_license="CC-BY-SA-4.0",
            experiment_keywords=["ocean", "heat", "content"],
            experiment_formats=["GeoTIFF"],
            experiment_themes=["oceans"],
            experiment_input_parameters_link="https://github.com/deepesdl/cube-gen",
            experiment_enviroment_link="https://github.com/deepesdl/cube-gen",
            workflow_id=workflow_id,
            workflow_title=workflow_title,
            product_id=product_id,
            product_title="Global Ocean Heat Content",
        )
    )

    return project_collection, product_collection, workflow_collection, experiment


def add_item_link_to_product_collection(product_collection: pystac.Collection, item_id: str, item_title: str) -> None:
    """Adds an item relation link to a product collection."""

    product_collection.add_link(
        pystac.Link(rel="item", target=f"./{item_id}.json", media_type="application/json", title=item_title)
    )


def create_item(item_metadata: ItemMetadata, stac_version='1.0.0') -> pystac.Item:
    """Creates a STAC item with one data asset and optional extra fields."""

    item = pystac.Item(
        id=item_metadata.itemid,
        geometry=item_metadata.geometry,
        datetime=item_metadata.data_time,
        bbox=item_metadata.bbox,
        collection=item_metadata.product_id,
        properties={
            "license": item_metadata.license,
            "description": item_metadata.description,
        },
    )

    extra_fields = {}
    for key, value in (item_metadata.extra_fields or {}).items():
        extra_fields[key] = value

    item.add_asset(
        key="data",
        asset=pystac.Asset(
            href=item_metadata.data_url,
            media_type=item_metadata.data_mime_type,
            roles=["data"],
            title=item_metadata.data_title,
            extra_fields=extra_fields
        ),
    )

    return item