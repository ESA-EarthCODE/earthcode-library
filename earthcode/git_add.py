import pystac
from pathlib import Path
REMOTE_URL =  'https://esa-earthcode.github.io/open-science-catalog-metadata/'

def save_catalog_with_remote_selfhref(catalog_object, local_catalog_path, catalog_extension):
    
    # set remote href
    remote_catalog_path = REMOTE_URL + catalog_extension

    # overwrite self reference to be the online one
    catalog_dict = catalog_object.to_dict()
    for link in catalog_dict['links']:
        if link['rel'] == 'self':
            link['href'] = remote_catalog_path
    
    import json
    with open(local_catalog_path, 'w', encoding='utf-8') as f:
        json.dump(catalog_dict, f, indent=2, ensure_ascii=False)


# save project to catalog
def save_project_collection_to_osc(project_collection, catalog_root):

    # create a directory  under /projects with the same ID as the project ID
    project_dir = catalog_root / 'projects' / project_collection.id
    project_dir.mkdir()

    # save the collection in the new folder
    project_collection.save_object(
        dest_href=str(project_dir / 'collection.json'),
    )

    # create a link from the parent Projects catalog to the new item.
    catalog_extension = 'projects/catalog.json'
    local_catalog_path = catalog_root / catalog_extension
    projects_catalog = pystac.Catalog.from_file(local_catalog_path)
    projects_catalog.add_link(
        pystac.Link(
            rel='child',
            target=f'./{project_collection.id}/collection.json',
            media_type="application/json",
            title=project_collection.title

        )
    )
    save_catalog_with_remote_selfhref(projects_catalog, local_catalog_path, catalog_extension)




def save_product_collection_to_catalog(product_collection, catalog_root):

    product_dict = product_collection.to_dict()
    project_id = product_dict['osc:project']
    product_themes = [p['concepts'][0]['id'] for p in product_dict['themes']]
    product_variables = [v for v in product_dict['osc:variables']]
    product_missions = [m for m in product_dict['osc:missions']]

    
    # create a directory  under /projects with the same ID as the project ID
    product_dir = catalog_root / 'products' / product_collection.id
    product_dir.mkdir()


    # create a link from the parent products catalog to the new item.
    catalog_extension = 'products/catalog.json'
    local_catalog_path = catalog_root / catalog_extension
    products_catalog = pystac.Catalog.from_file(local_catalog_path)
    products_catalog.add_link(
        pystac.Link(
            rel='child',
            target=f'./{product_collection.id}/collection.json',
            media_type="application/json",
            title=f'{product_collection.title}'
        )
    )
    save_catalog_with_remote_selfhref(products_catalog, local_catalog_path, catalog_extension)

    # add product to project Collection
    import json
    with open(catalog_root / f'projects/{project_id}/collection.json') as f:
        project_collection = json.load(f)
        project_collection = pystac.Collection.from_dict(project_collection,
                                                         migrate=False,
                                                         root=None,
                                                         preserve_dict=True)
    project_collection.add_link(
        pystac.Link(
            rel='child',
            target=f'../../products/{product_collection.id}/collection.json',
            media_type="application/json",
            title=f'{product_collection.title}'
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
        theme_catalog.add_link(
            pystac.Link(
                rel='child',
                target=f'../../products/{product_collection.id}/collection.json',
                media_type="application/json",
                title=f'{product_collection.title}'
            )
        )
        save_catalog_with_remote_selfhref(theme_catalog, local_catalog_path, catalog_extension)

    # add variable return links
    for var in product_variables:
        catalog_extension = f'variables/{var}/catalog.json'
        local_catalog_path = catalog_root / catalog_extension
        var_catalog =  pystac.Catalog.from_file(local_catalog_path)
        var_catalog.add_link(
            pystac.Link(
                rel='child',
                target=f'../../products/{product_collection.id}/collection.json',
                media_type="application/json",
                title=f'{product_collection.title}'
            )
        )
        save_catalog_with_remote_selfhref(var_catalog, local_catalog_path, catalog_extension)
        

    # add mission return links
    for mission in product_missions:
        catalog_extension = f'eo-missions/{mission}/catalog.json'
        local_catalog_path = catalog_root / catalog_extension
        mission_catalog = pystac.Catalog.from_file(local_catalog_path)
        mission_catalog.add_link(
            pystac.Link(
                rel='child',
                target=f'../../products/{product_collection.id}/collection.json',
                media_type="application/json",
                title=f'{product_collection.title}'
            )
        )
        save_catalog_with_remote_selfhref(mission_catalog, local_catalog_path, catalog_extension)

    # update link titles
    for link in product_collection.get_links('related'):
        link_elements = link.href.split('/')
        if link_elements[2] in ['variables', 'eo-missions']:
            catalog_title = pystac.Catalog.from_file(catalog_root / f'{link_elements[2]}/{link_elements[3]}/catalog.json').title
            prefix = 'Variable: ' if link_elements[2] == 'variables' else 'EO Mission: '
            link.title = prefix + catalog_title

    # save the collection in the new folder
    product_collection.save_object(
        dest_href=str(product_dir / 'collection.json'),
    )


def save_workflow_record_to_osc(workflow_record, catalog_root):

    # create a directory  under /projects with the same ID as the project ID
    wf_dir = catalog_root / 'workflows' / workflow_record['id']
    wf_dir.mkdir()

    # save the record in the new folder
    import json
    with open(wf_dir / 'record.json', 'w', encoding='utf-8') as f:
        json.dump(workflow_record, f, indent=2, ensure_ascii=False)

    # create a link from the parent Projects catalog to the new item.
    catalog_extension = 'workflows/catalog.json'
    local_catalog_path = catalog_root / catalog_extension
    wf_catalog = pystac.Catalog.from_file(local_catalog_path)
    wf_catalog.add_link(
        pystac.Link(
            rel='item',
            target=f'./{workflow_record['id']}/record.json',
            media_type="application/json",
            title=workflow_record['properties']['title']

        )
    )
    save_catalog_with_remote_selfhref(wf_catalog, local_catalog_path, catalog_extension)


def save_experiment_record_to_osc(experiment_record, catalog_root):

    # create a directory  under /projects with the same ID as the project ID
    experiment_dir = catalog_root / 'experiments' / experiment_record['id']
    experiment_dir.mkdir()

    # save the record in the new folder
    import json
    with open(experiment_dir / 'record.json', 'w', encoding='utf-8') as f:
        json.dump(experiment_record, f, indent=2, ensure_ascii=False)

    # create a link from the parent Projects catalog to the new item.
    catalog_extension = 'experiments/catalog.json'
    local_catalog_path = catalog_root / catalog_extension
    experiments_catalog = pystac.Catalog.from_file(local_catalog_path)
    experiments_catalog.add_link(
        pystac.Link(
            rel='item',
            target=f'./{experiment_record['id']}/record.json',
            media_type="application/json",
            title=experiment_record['properties']['title']

        )
    )
    save_catalog_with_remote_selfhref(experiments_catalog, local_catalog_path, catalog_extension)


def save_item_to_product_collection(item, product_collection, catalog_root):

    item.add_link(pystac.Link.from_dict(
         {
      "rel": "collection",
      "href": "./collection.json",
      "type": "application/json",
      "title": product_collection.title
        }
    ))

    item.add_link(pystac.Link.from_dict(
    {
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