from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProjectCollectionMetadata(BaseModel):
    """Defines validated inputs used to construct an OSC project collection."""

    project_id: str = Field(
        ...,
        description="Custom project identifier using dashes to separate words, e.g. '4datlantic-ohc'.",
    )
    project_title: str = Field(
        ...,
        description="Official project title as used in the ESA contract.",
    )
    project_description: str = Field(
        ...,
        description="Short textual description of the project.",
    )
    project_status: str = Field(
        ...,
        description="Project status, expected as 'ongoing' or 'completed'.",
    )
    project_license: str = Field(
        ...,
        description="Overall license used for project outputs; use an allowed SPDX-style value or 'various'.",
    )
    project_bbox: list[list[float]] = Field(..., description="One or more [west, south, east, north] bounding boxes.")
    project_start_datetime: datetime = Field(
        ...,
        description="Project start date and time.",
    )
    project_end_datetime: datetime = Field(
        ...,
        description="Project end date and time.",
    )
    project_themes: list[str] = Field(
        ...,
        description="One or more OSC themes, e.g. atmosphere, cryosphere, land, magnetosphere-ionosphere, oceans, solid-earth.",
    )
    to_name: str = Field(
        ...,
        description="Full name of the ESA Technical Officer supporting the project.",
    )
    to_email: str = Field(
        ...,
        description="Email address of the ESA Technical Officer.",
    )
    consortium_members: list[tuple[str, str]] = Field(
        ...,
        description="Project consortium members as (name, contact_email) tuples.",
    )
    website_link: str = Field(
        ...,
        description="Project website URL.",
    )
    eo4society_link: Optional[str] = Field(
        None,
        description="EO4Society project page URL when available.",
    )


class ProductCollectionMetadata(BaseModel):
    """Defines validated inputs used to construct an OSC product collection."""

    product_id: str = Field(
        ...,
        description="Custom product identifier distinct from the project ID, using dashes between words.",
    )
    product_title: Optional[str] = Field(
        None,
        description="Human-readable product title.",
    )
    product_description: str = Field(
        ...,
        description="General metadata description of the product or dataset.",
    )
    product_bbox: list[list[float]] = Field(..., description="One or more [west, south, east, north] bounding boxes.")
    product_start_datetime: datetime = Field(
        ...,
        description="Product or dataset start date and time.",
    )
    product_end_datetime: datetime = Field(
        ...,
        description="Product or dataset end date and time.",
    )
    product_license: str = Field(
        ...,
        description="License for this product; should be a valid allowed OSC license value.",
    )
    product_keywords: Optional[list[str]] = Field(
        None,
        description="Up to five short keywords to improve product discovery.",
    )
    product_status: str = Field(
        ...,
        description="Product status, expected as 'ongoing' or 'completed'.",
    )
    product_region: Optional[str] = Field(
        None,
        description="Semantic region covered by the product, e.g. Belgium or Global.",
    )
    product_themes: list[str] = Field(
        ...,
        description="One or more OSC themes applicable to the product.",
    )
    product_missions: list[str] = Field(
        ...,
        description="One or more EO mission identifiers used to generate the product.",
    )
    product_variables: list[str] = Field(
        ...,
        description="One or more OSC variable identifiers describing the product.",
    )
    project_id: str = Field(
        ...,
        description="Identifier of the related project; must match an existing or newly created project.",
    )
    project_title: str = Field(
        ...,
        description="Title of the related project corresponding to project_id.",
    )
    product_parameters: Optional[list[str]] = Field(
        None,
        description="CF-convention style parameter names associated with the product, e.g. 'leaf_area_index'.",
    )
    product_doi: Optional[str] = Field(
        None,
        description="DOI URL assigned to the product, if available.",
    )
    access_link: Optional[str] = Field(
        None,
        description="Direct URL for accessing data; this should be a valid URL.",
    )
    documentation_link: Optional[str] = Field(
        None,
        description="URL to supporting documentation such as handbook or validation report.",
    )
    license_link: Optional[str] = Field(
        None,
        description="URL to license, if its not a standard SPDX one.",
    ) 
    item_link: Optional[str] = Field(
        None,
        description="URL to an external STAC item or collection representing the dataset, if available.",
    )
    item_title: Optional[str] = Field(
        None,
        description="Title to the item.",
    )
    


class WorkflowMetadata(BaseModel):
    """Defines validated inputs used to construct an OSC workflow record."""

    workflow_id: str = Field(
        ...,
        description="Custom workflow identifier, distinct from project and product IDs.",
    )
    workflow_title: str = Field(
        ...,
        description="Workflow title.",
    )
    workflow_description: str = Field(
        ...,
        description="Short description of the workflow purpose and content.",
    )
    workflow_license: str = Field(
        ...,
        description="Workflow license value, typically SPDX-style or 'various' when needed.",
    )
    workflow_keywords: list[str] = Field(
        ...,
        description="Up to five short keywords to improve workflow discovery.",
    )
    workflow_formats: list[str] = Field(
        ...,
        description="Input/output data formats used by the workflow, e.g. GeoTIFF or NetCDF.",
    )
    workflow_themes: list[str] = Field(
        ...,
        description="One or more OSC themes associated with the workflow.",
    )
    codeurl: str = Field(
        ...,
        description="Active URL to the repository where the workflow/code can be discovered.",
    )
    project_id: str = Field(
        ...,
        description="Identifier of the associated project; must match an existing or newly created project.",
    )
    project_title: str = Field(
        ...,
        description="Title of the associated project corresponding to project_id.",
    )
    workflow_doi: Optional[str] = Field(
        None,
        description="DOI for the workflow record when available.",
    )
    workflow_bbox: Optional[list[list[float]]] = Field(
        None,
        description="Optional workflow spatial coverage as [west, south, east, north] bounding boxes.",
    )
    workflow_start_datetime: Optional[datetime] = Field(
        None,
        description="Optional workflow validity/execution start datetime.",
    )
    workflow_end_datetime: Optional[datetime] = Field(
        None,
        description="Optional workflow validity/execution end datetime.",
    )


class ExperimentMetadata(BaseModel):
    """Defines validated inputs used to construct an OSC experiment record."""

    experiment_id: str = Field(
        ...,
        description="Custom identifier of the experiment record.",
    )
    experiment_title: str = Field(
        ...,
        description="Experiment title.",
    )
    experiment_description: str = Field(
        ...,
        description="Description of the workflow execution that generated the product.",
    )
    experiment_license: str = Field(
        ...,
        description="License value for the experiment record.",
    )
    experiment_keywords: list[str] = Field(
        ...,
        description="Keywords supporting experiment discovery.",
    )
    experiment_formats: list[str] = Field(
        ...,
        description="Input/output formats used in the experiment, e.g. GeoTIFF, Zarr, netCDF.",
    )
    experiment_themes: list[str] = Field(
        ...,
        description="One or more OSC themes associated with the experiment.",
    )
    experiment_input_parameters_link: str = Field(
        ...,
        description="URL to the specification of experiment input parameters.",
    )
    experiment_enviroment_link: str = Field(
        ...,
        description="URL to the runtime environment description used to execute the experiment.",
    )
    workflow_id: str = Field(
        ...,
        description="Identifier of the associated workflow.",
    )
    workflow_title: str = Field(
        ...,
        description="Title of the associated workflow.",
    )
    product_id: str = Field(
        ...,
        description="Identifier of the associated product.",
    )
    product_title: str = Field(
        ...,
        description="Title of the associated product.",
    )
    contacts: Optional[list[dict]] = Field(
        None,
        description="Optional contact objects for the experiment record.",
    )
    experiment_bbox: Optional[list[list[float]]] = Field(
        None,
        description="Optional experiment spatial coverage as [west, south, east, north] bounding boxes.",
    )
    experiment_start_datetime: Optional[datetime] = Field(
        None,
        description="Optional experiment start datetime.",
    )
    experiment_end_datetime: Optional[datetime] = Field(
        None,
        description="Optional experiment end datetime.",
    )


class ItemMetadata(BaseModel):
    """Defines validated inputs used to construct an OSC STAC Item."""

    itemid: str = Field(
        ...,
        description="Unique STAC item identifier.",
    )
    geometry: dict = Field(
        ...,
        description="GeoJSON geometry describing the item footprint.",
    )
    data_time: datetime = Field(
        ...,
        description="Primary timestamp of the item.",
    )
    bbox: list[float] = Field(
        ...,
        description="Item bounding box as [west, south, east, north].",
    )
    product_id: str = Field(
        ...,
        description="Identifier of the parent product/collection for this item.",
    )
    license: str = Field(
        ...,
        description="License applicable to this item.",
    )
    description: str = Field(
        ...,
        description="Short item description.",
    )
    data_url: str = Field(
        ...,
        description="URL to the primary data asset.",
    )
    data_mime_type: str = Field(
        ...,
        description="Media type of the primary data asset.",
    )
    data_title: str = Field(
        ...,
        description="Human-readable title of the primary data asset.",
    )
    extra_fields: Optional[dict] = Field(
        None,
        description="Additional custom STAC fields to add to the item.",
    )
