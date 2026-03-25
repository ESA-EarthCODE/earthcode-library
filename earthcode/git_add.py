import pystac
from pathlib import Path
import json
from typing import Any, Mapping

REMOTE_URL =  'https://esa-earthcode.github.io/open-science-catalog-metadata/'


## need to force pystac to respect 1.0.0
pystac.set_stac_version('1.0.0')

def _add_link_if_missing(stac_obj: pystac.STACObject, link: pystac.Link) -> None:
    """Adds a link only when no existing link has the same rel and href."""

    for existing in stac_obj.get_links():
        if existing.rel == link.rel and existing.href == link.href:
            return
    stac_obj.add_link(link)


def _require_product_field(product_dict: Mapping[str, Any], key: str) -> Any:
    """Ensures a required product metadata key exists and is non-empty."""

    value = product_dict.get(key)
    if value is None:
        raise ValueError(f"Missing required product field: {key}")
    if isinstance(value, (list, str, dict)) and len(value) == 0:
        raise ValueError(f"Empty required product field: {key}")
    return value


def _collection_to_dict(
    collection: dict[str, Any] | pystac.Collection, context_name: str
) -> dict[str, Any]:
    """Normalizes a collection input to a dictionary representation."""

    if isinstance(collection, pystac.Collection):
        return collection.to_dict()
    if isinstance(collection, dict):
        return collection
    raise TypeError(f"{context_name} must be a dict or pystac.Collection")


def save_catalog_with_remote_selfhref(
    catalog_object: pystac.Catalog,
    local_catalog_path: Path,
    catalog_extension: str,
) -> None:
    """Saves a catalog JSON file while forcing the self link to the configured remote OSC URL."""
    
    # set remote href
    remote_catalog_path = REMOTE_URL + catalog_extension

    # overwrite self reference to be the online one
    catalog_dict = catalog_object.to_dict()
    for link in catalog_dict['links']:
        if link['rel'] == 'self':
            link['href'] = remote_catalog_path
    
    with open(local_catalog_path, 'w', encoding='utf-8') as f:
        json.dump(catalog_dict, f, indent=2, ensure_ascii=False)


# save project to catalog
def save_project_collection_to_osc(
    project_collection: dict[str, Any] | pystac.Collection,
    catalog_root: Path,
) -> None:
    """Writes a project collection into the local OSC tree and links it from the projects catalog."""

    project_dict = _collection_to_dict(project_collection, "project_collection")
    project_id = project_dict["id"]
    project_title = project_dict.get("title")

    # create a directory  under /projects with the same ID as the project ID
    project_dir = catalog_root / 'projects' / project_id
    project_dir.mkdir(parents=True, exist_ok=True)

    # save the collection in the new folder
    with open(project_dir / 'collection.json', 'w', encoding='utf-8') as f:
        json.dump(project_dict, f, indent=2, ensure_ascii=False)

    # create a link from the parent Projects catalog to the new item.
    catalog_extension = 'projects/catalog.json'
    local_catalog_path = catalog_root / catalog_extension
    projects_catalog = pystac.Catalog.from_file(local_catalog_path)
    _add_link_if_missing(
        projects_catalog,
        pystac.Link(
            rel='child',
            target=f'./{project_id}/collection.json',
            media_type="application/json",
            title=project_title

        )
    )
    save_catalog_with_remote_selfhref(projects_catalog, local_catalog_path, catalog_extension)




def save_product_collection_to_catalog(
    product_collection: dict[str, Any] | pystac.Collection,
    catalog_root: Path,
) -> None:
    """Writes a product collection and updates all related reverse links in projects, themes, variables, and missions catalogs."""

    product_dict = _collection_to_dict(product_collection, "product_collection")
    product_id = product_dict["id"]
    product_title = product_dict.get("title")
    project_id = _require_product_field(product_dict, 'osc:project')
    product_themes = [p['concepts'][0]['id'] for p in _require_product_field(product_dict, 'themes')]
    product_variables = [v for v in _require_product_field(product_dict, 'osc:variables')]
    product_missions = [m for m in _require_product_field(product_dict, 'osc:missions')]

    
    # create a directory  under /projects with the same ID as the project ID
    product_dir = catalog_root / 'products' / product_id
    product_dir.mkdir(parents=True, exist_ok=True)


    # create a link from the parent products catalog to the new item.
    catalog_extension = 'products/catalog.json'
    local_catalog_path = catalog_root / catalog_extension
    products_catalog = pystac.Catalog.from_file(local_catalog_path)
    _add_link_if_missing(
        products_catalog,
        pystac.Link(
            rel='child',
            target=f'./{product_id}/collection.json',
            media_type="application/json",
            title=f'{product_title}'
        )
    )
    save_catalog_with_remote_selfhref(products_catalog, local_catalog_path, catalog_extension)

    # add product to project Collection
    with open(catalog_root / f'projects/{project_id}/collection.json') as f:
        project_collection = json.load(f)
        project_collection = pystac.Collection.from_dict(project_collection,
                                                         migrate=False,
                                                         root=None,
                                                         preserve_dict=True)
    _add_link_if_missing(
        project_collection,
        pystac.Link(
            rel='child',
            target=f'../../products/{product_id}/collection.json',
            media_type="application/json",
            title=f'{product_title}'
        )
    )
    with open(catalog_root / f'projects/{project_id}/collection.json', 'w') as f:
        json.dump(
            project_collection.to_dict(include_self_link=False, transform_hrefs=False), 
            f, ensure_ascii=False, indent=2)


    # add theme return links
    for theme in product_themes:
        catalog_extension = f'themes/{theme}/catalog.json'
        local_catalog_path = catalog_root / catalog_extension
        theme_catalog =  pystac.Catalog.from_file(local_catalog_path)
        _add_link_if_missing(
            theme_catalog,
            pystac.Link(
                rel='child',
                target=f'../../products/{product_id}/collection.json',
                media_type="application/json",
                title=f'{product_title}'
            )
        )
        save_catalog_with_remote_selfhref(theme_catalog, local_catalog_path, catalog_extension)

    # add variable return links
    for var in product_variables:
        catalog_extension = f'variables/{var}/catalog.json'
        local_catalog_path = catalog_root / catalog_extension
        var_catalog =  pystac.Catalog.from_file(local_catalog_path)
        _add_link_if_missing(
            var_catalog,
            pystac.Link(
                rel='child',
                target=f'../../products/{product_id}/collection.json',
                media_type="application/json",
                title=f'{product_title}'
            )
        )
        save_catalog_with_remote_selfhref(var_catalog, local_catalog_path, catalog_extension)
        

    # add mission return links
    for mission in product_missions:
        catalog_extension = f'eo-missions/{mission}/catalog.json'
        local_catalog_path = catalog_root / catalog_extension
        mission_catalog = pystac.Catalog.from_file(local_catalog_path)
        _add_link_if_missing(
            mission_catalog,
            pystac.Link(
                rel='child',
                target=f'../../products/{product_id}/collection.json',
                media_type="application/json",
                title=f'{product_title}'
            )
        )
        save_catalog_with_remote_selfhref(mission_catalog, local_catalog_path, catalog_extension)

    # update link titles
    for link in product_dict.get("links", []):
        if link.get("rel") != "related":
            continue
        href = link.get("href", "")
        link_elements = href.split('/')
        if len(link_elements) > 3 and link_elements[2] in ['variables', 'eo-missions']:
            catalog_title = pystac.Catalog.from_file(
                catalog_root / f'{link_elements[2]}/{link_elements[3]}/catalog.json'
            ).title
            prefix = 'Variable: ' if link_elements[2] == 'variables' else 'EO Mission: '
            link["title"] = prefix + catalog_title

    # save the collection in the new folder
    with open(product_dir / 'collection.json', 'w', encoding='utf-8') as f:
        json.dump(product_dict, f, indent=2, ensure_ascii=False)


def save_workflow_record_to_osc(
    workflow_record: dict[str, Any], catalog_root: Path
) -> None:
    """Writes a workflow record into the local OSC tree and links it from the workflows catalog."""

    # create a directory  under /projects with the same ID as the project ID
    wf_dir = catalog_root / 'workflows' / workflow_record['id']
    wf_dir.mkdir(parents=True, exist_ok=True)

    # save the record in the new folder
    with open(wf_dir / 'record.json', 'w', encoding='utf-8') as f:
        json.dump(workflow_record, f, indent=2, ensure_ascii=False)

    # create a link from the parent Projects catalog to the new item.
    catalog_extension = 'workflows/catalog.json'
    local_catalog_path = catalog_root / catalog_extension
    wf_catalog = pystac.Catalog.from_file(local_catalog_path)
    _add_link_if_missing(
        wf_catalog,
        pystac.Link(
            rel='item',
            target=f"./{workflow_record['id']}/record.json",
            media_type="application/json",
            title=workflow_record['properties']['title']

        )
    )
    save_catalog_with_remote_selfhref(wf_catalog, local_catalog_path, catalog_extension)


def save_experiment_record_to_osc(
    experiment_record: dict[str, Any], catalog_root: Path
) -> None:
    """Writes an experiment record into the local OSC tree and links it from the experiments catalog."""

    # create a directory  under /projects with the same ID as the project ID
    experiment_dir = catalog_root / 'experiments' / experiment_record['id']
    experiment_dir.mkdir(parents=True, exist_ok=True)

    # save the record in the new folder
    with open(experiment_dir / 'record.json', 'w', encoding='utf-8') as f:
        json.dump(experiment_record, f, indent=2, ensure_ascii=False)

    # create a link from the parent Projects catalog to the new item.
    catalog_extension = 'experiments/catalog.json'
    local_catalog_path = catalog_root / catalog_extension
    experiments_catalog = pystac.Catalog.from_file(local_catalog_path)
    _add_link_if_missing(
        experiments_catalog,
        pystac.Link(
            rel='item',
            target=f"./{experiment_record['id']}/record.json",
            media_type="application/json",
            title=experiment_record['properties']['title']

        )
    )
    save_catalog_with_remote_selfhref(experiments_catalog, local_catalog_path, catalog_extension)


def save_item_to_product_collection(
    item: pystac.Item, product_collection: pystac.Collection | str, catalog_root: Path
) -> None:
    """Adds parent and collection links to an item and saves it under the target product directory."""

    if type(product_collection) is str:
        with open(catalog_root/f'products/{product_collection}/collection.json', 'r', encoding='utf-8') as f:
            product_collection = json.load(f)
            product_collection = pystac.Collection.from_dict(product_collection,
                                                        migrate=False,
                                                        root=None,
                                                        preserve_dict=True)

    item.add_link(pystac.Link.from_dict(
         {
      "rel": "collection",
      "href": "./collection.json",
      "type": "application/json",
      "title": product_collection.title
        }
    ))

    item.add_link(pystac.Link.from_dict({
      "rel": "parent",
      "href": "./collection.json",
      "type": "application/json",
      "title": product_collection.title
     },
    ))


    item.save_object(
        include_self_link=False, 
        dest_href=catalog_root/f'products/{product_collection.id}/{item.id}.json'
    )

    # add to product collection if not already existing
    with open(catalog_root / f'products/{product_collection.id}/collection.json') as f:
        existing_product_collection = json.load(f)
        existing_product_collection = pystac.Collection.from_dict(existing_product_collection,
                                                         migrate=False,
                                                         root=None,
                                                         preserve_dict=True)
    _add_link_if_missing(
        existing_product_collection,
        pystac.Link(rel="item", target=f"./{item.id}.json", media_type="application/json", title=item.assets['data'].title)
    )
    
    with open(catalog_root / f'products/{product_collection.id}/collection.json', 'w', encoding='utf-8') as f:
        json.dump(
            existing_product_collection.to_dict(include_self_link=False, transform_hrefs=False), 
            f, ensure_ascii=False, indent=2)



def save_item_links_to_product_collection(catalog_root: Path, product_id: str, item_link: str, access_link: str=None, documentation_link: str=None):
    """Adds links to an existing product collection"""
    
    with open(catalog_root/f'products/{product_id}/collection.json', 'r', encoding='utf-8') as f:
        product_collection = json.load(f)
        product_collection = pystac.Collection.from_dict(product_collection,
                                                    migrate=False,
                                                    root=None,
                                                    preserve_dict=True)
    links = [
        pystac.Link.from_dict({
                "rel": "child",
                "href": item_link,
                "type": "application/json",
                "title": "PRR Data Collection"
                }
            )
    ]

    if documentation_link:
        links.append(
            pystac.Link.from_dict({
                "rel": "via",
                "href": documentation_link,
                "type": "application/json",
                "title": "Documentation"
                }
            )
        )

    if access_link:
        links.append( 
            pystac.Link.from_dict({
                "rel": "via",
                "href": access_link,
                "type": "application/json",
                "title": "Access"
                }
            )
        )
    
    product_collection.add_links(links)
    with open(catalog_root / f'products/{product_collection.id}/collection.json', 'w', encoding='utf-8') as f:
        json.dump(
            product_collection.to_dict(include_self_link=False, transform_hrefs=False), 
            f, ensure_ascii=False, indent=2)
