import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import pystac
from jsonschema import validate, RefResolver

# Try importing PIL for image validation
try:
    from PIL import Image
except ImportError:
    Image = None

ROOT_CHILDREN = ["eo-missions", "products", "projects", "themes", "variables", "experiments", "workflows"]
EXTENSION_SCHEMES = {
    "osc": "https://stac-extensions.github.io/osc/v1.0.0/schema.json",
    "themes": "https://stac-extensions.github.io/themes/v1.0.0/schema.json",
    "contacts": "https://stac-extensions.github.io/contacts/v0.1.1/schema.json",
}
LINK_PREFIX = "https://esa-earthcode.github.io/open-science-catalog-metadata/"
THEMES_SCHEME = "https://github.com/stac-extensions/osc#theme"
RELATED_TITLE_PREFIX = {
    "projects": "Project",
    "products": "Product",
    "eo-missions": "EO Mission",
    "themes": "Theme",
    "variables": "Variable",
    "workflows": "Workflow",
    "experiments": "Experiment"
}


# --- Common Utilities ---

def _infer_file_path(data: Dict, root: Path) -> Path:
    obj_id = data.get("id")
    obj_type = data.get("type")
    
    if obj_id == "osc" and obj_type == "Catalog":
        return root / "catalog.json"
    
    if obj_id in ROOT_CHILDREN and obj_type == "Catalog":
        return root / obj_id / "catalog.json"

    osc_type = data.get("osc:type")
    
    if osc_type == "project":
        return root / "projects" / obj_id / "collection.json"
    if osc_type == "product":
        return root / "products" / obj_id / "collection.json"
    
    candidates = [
        root / "eo-missions" / obj_id / "catalog.json",
        root / "themes" / obj_id / "catalog.json",
        root / "variables" / obj_id / "catalog.json",
        root / "workflows" / obj_id / "record.json",
        root / "experiments" / obj_id / "record.json"
    ]
    
    for c in candidates:
        if c.exists():
            return c
    
    # check if the file is a product STAC item
    if data.get('collection') is not None:
        return  root / "products" / data.get('collection') / f"{obj_id}.json"
            
    if osc_type: 
        raise ValueError(f"Could not locate file for {osc_type} with id {obj_id}")
    
    raise ValueError(f"Could not infer file path for object id '{obj_id}'. Ensure file exists in standard OSC structure.")


def _assert(ctx, condition, message):
    if not condition:
        ctx["errors"].append(message)

def _resolve(ctx, href):
    if href.startswith(LINK_PREFIX):
        href = href[len(LINK_PREFIX):]
    
    base = ctx["file_path"].parent
    return (base / href).resolve()

def _get_title_for_file(path: Path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            stac = json.load(f)
            if stac.get("type") == "Feature":
                return stac.get("properties", {}).get("title")
            return stac.get("title")
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def _get_link_with_rel(data, rel):
    links = data.get("links", [])
    if isinstance(links, list):
        for link in links:
            if link.get("href") and link.get("rel") == rel:
                return link
    return None

def _has_link_with_rel(ctx, rel):
    link = _get_link_with_rel(ctx["data"], rel)
    _assert(ctx, isinstance(link, dict), f"must have {rel} link")
    return link

def _has_extensions(ctx, extensions):
    stac_ext = ctx["data"].get("stac_extensions", [])
    if isinstance(stac_ext, list):
        for ext in extensions:
            url = EXTENSION_SCHEMES.get(ext)
            if url:
                _assert(ctx, url in stac_ext, f"must implement extension: {ext}")
            else:
                _assert(ctx, False, f"Extension definition missing for {ext}")
    else:
        _assert(ctx, False, f"must implement extensions: {', '.join(extensions)}")

def _ensure_id_is_folder_name(ctx):
    parent_folder_name = ctx["file_path"].parent.name
    _assert(ctx, ctx["data"].get("id") == parent_folder_name, "parent folder name must match id")

def _check_stac_links_rel_abs(ctx, include_item_child=True):
    rels = ['related', 'parent']
    if include_item_child:
        rels.extend(['item', 'child'])
    
    for link in ctx["data"].get("links", []):
        href = link.get("href", "")
        rel = link.get("rel")
        if rel == 'self':
            _assert(ctx, href.startswith(LINK_PREFIX), f"Link 'self' must start with '{LINK_PREFIX}'")
        elif rel in rels:
            _assert(ctx, "://" not in href, f"Link '{rel}' to '{href}' must be relative")

def _check_link_title(ctx, link, prefix=''):
    href_resolved = _resolve(ctx, link['href'])
    title = _get_title_for_file(href_resolved)
    
    if isinstance(title, str):
        expected = f"{prefix}{title}" if prefix else title
        msg = f"'{expected}'" if prefix else f"title of linked file {href_resolved}"
        _assert(ctx, link.get("title") == expected, f"Title of link to {link['href']} (rel: {link['rel']}) must be {msg}")

def _require_parent_link(ctx, expected_path):
    _check_stac_link(ctx, 'parent', expected_path)

def _require_root_link(ctx, expected_path):
    _check_stac_link(ctx, 'root', expected_path)

def _require_via_link(ctx):
    _has_link_with_rel(ctx, "via")

def _check_stac_link(ctx, rel_type, expected_path):
    link = _has_link_with_rel(ctx, rel_type)
    if not link: return
    
    res_link = _resolve(ctx, link['href'])
    res_expected = _resolve(ctx, expected_path)
    
    _assert(ctx, res_link == res_expected, f"{rel_type} link must point to {expected_path}")
    _assert(ctx, link.get("type") == "application/json", f"{rel_type} link must be application/json")
    _check_link_title(ctx, link)

def _check_preview_image(ctx):
    link = _has_link_with_rel(ctx, "preview")
    if not link: return

    _assert(ctx, link.get("type") == "image/webp", "Preview type must be image/webp")
    _assert(ctx, link.get("proj:epsg") is None, "proj:epsg must be null")

    preview_path = _resolve(ctx, link['href'])
    
    if Image and preview_path.exists():
        try:
            with Image.open(preview_path) as img:
                w, h = img.size
                _assert(ctx, link.get("proj:shape") == [h, w], f"proj:shape mismatch for {preview_path}")
        except Exception:
             _assert(ctx, False, f"Preview image corrupt: {preview_path}")
    elif not preview_path.exists():
         _assert(ctx, False, f"Preview image doesn't exist: {preview_path}")

def _check_child_links(ctx, expected_type="products", expected_filename="collection"):
    links = [l for l in ctx["data"].get("links", []) if l.get("rel") == "child"]
    
    for link in links:
        _assert(ctx, link.get("type") == "application/json", f"Link child to {link['href']} type must be json")
        href_path = Path(link['href'])
        ftype = href_path.parent.parent.name
        fname = href_path.name
        
        _assert(ctx, ftype == expected_type, f"Child link to {link['href']} must point to folder '{expected_type}'")
        _assert(ctx, fname == f"{expected_filename}.json", f"Child link must point to '{expected_filename}.json'")
        _check_link_title(ctx, link)

        resolved = _resolve(ctx, link['href'])
        _assert(ctx, resolved.exists(), f"must have file for link {resolved}")

def _require_child_links_for_other_json(ctx, files_to_check=None, filename="collection", link_rel='child'):
    target_files = []
    
    if files_to_check:
        # Assuming files_to_check is a list of folder names in the current directory
        # logic mirrors JS: resolve(file) -> check exists
        for f in files_to_check:
            # Construct path relative to current folder
            # JS logic: if array, map resolve. resolve() uses folder.
            # ROOT_CHILDREN are folders.
            p = ctx["file_path"].parent / f / "catalog.json" # Assumption for root children
            if not p.exists():
                 p = ctx["file_path"].parent / f / "collection.json"
            
            if p.exists():
                target_files.append(p)
    else:
        # Scan directory
        current_folder = ctx["file_path"].parent
        if current_folder.exists():
            for entry in os.scandir(current_folder):
                if entry.is_dir():
                    if filename:
                        cand = Path(entry.path) / f"{filename}.json"
                        if cand.exists(): target_files.append(cand)
                    else:
                        for sub in os.scandir(entry.path):
                            if sub.name.endswith(".json"):
                                target_files.append(Path(sub.path))

    links = [l for l in ctx["data"].get("links", []) if l.get("href") and l.get("rel") == link_rel]
    link_hrefs = [_resolve(ctx, l['href']) for l in links]

    for link in links:
        _assert(ctx, link.get("type") == "application/json", f"{link_rel} link type error")
        _check_link_title(ctx, link)

    for tf in target_files:
        if tf not in link_hrefs:
            _assert(ctx, False, f"must have link with relation {link_rel} to {tf}")

    for lh in link_hrefs:
        # If we have a link, the file MUST exist
        if not lh.exists():
             _assert(ctx, False, f"must have file for link {lh}")

def _check_themes(ctx):
    themes = ctx["data"].get("themes")
    _assert(ctx, isinstance(themes, list), "'themes' must be an array")
    _has_extensions(ctx, ["themes"])
    
    if not isinstance(themes, list): return

    theme_obj = next((th for th in themes if th.get("scheme") == THEMES_SCHEME), None)
    _assert(ctx, theme_obj is not None, f"must have theme with scheme '{THEMES_SCHEME}'")
    if not theme_obj: return
            
    concepts = theme_obj.get("concepts")
    _assert(ctx, isinstance(concepts, list), "concepts must be an array")
    
    if isinstance(concepts, list):
        for obj in concepts:
            theme_path = _resolve(ctx, f"../../themes/{obj['id']}/catalog.json")
            _assert(ctx, theme_path.exists(), f"Referenced theme '{obj['id']}' must exist at {theme_path}")
            _check_related_link(ctx, "themes", obj['id'], "catalog")

def _check_related_link(ctx, type_name, id_val, filename="collection"):
    suffix = f"/{type_name}/{id_val}/{filename}.json"
    link = next((l for l in ctx["data"].get("links", []) 
                 if l.get("rel") == "related" and l.get("href", "").endswith(suffix)), None)
    
    _assert(ctx, link is not None, f"must have 'related' link to {type_name} with id '{id_val}'")
    
    if link:
        _assert(ctx, link.get("type") == "application/json", "related link type must be json")
        prefix = RELATED_TITLE_PREFIX.get(type_name, "") + ": "
        _check_link_title(ctx, link, prefix)

def _check_osc_cross_ref_array(ctx, field, type_name, required=False):
    vals = ctx["data"].get(field)
    if required:
        _assert(ctx, isinstance(vals, list), f"'{field}' must be array")
    if isinstance(vals, list):
        for val in vals:
            _check_osc_cross_ref(ctx, val, type_name, True)

def _check_osc_cross_ref(ctx, value, type_name, required=False):
    if not value and not required: return
    
    fname = "catalog"
    if type_name in ["projects", "products"]: fname = "collection"
    if type_name in ["experiments", "workflows"]: fname = "record"
    
    path_ref = _resolve(ctx, f"../../{type_name}/{value}/{fname}.json")
    _assert(ctx, path_ref.exists(), f"Referenced {type_name} '{value}' must exist")
    _check_related_link(ctx, type_name, value, fname)

def _require_technical_officer(ctx):
    contacts = ctx["data"].get("contacts")
    _assert(ctx, isinstance(contacts, list), "must have contacts")
    if not isinstance(contacts, list): return
    
    tech = next((c for c in contacts if "technical_officer" in c.get("roles", [])), None)
    if tech:
        _assert(ctx, len(tech.get("name", "")) > 1, "tech officer must have name")
        emails = tech.get("emails", [])
        _assert(ctx, len(emails) > 0 and len(emails[0].get("value", "")) > 1, "tech officer must have email")
    else:
        _assert(ctx, False, "must have technical officer contact")

def _no_duplicated_links(ctx):
    links = [(l['rel'], l.get('title', ''), l['href']) for l in ctx['data'].get("links", [])]
    _assert(ctx, len(links) == len(set(links)), "There should be no duplciated links")

def _validate_project(ctx):
    
    data = ctx["data"]
    _assert(ctx, data.get("type") == "Collection", "type must be 'Collection'")
    
    _ensure_id_is_folder_name(ctx)
    _require_via_link(ctx)
    
    _require_parent_link(ctx, "../catalog.json")
    _require_root_link(ctx, "../../catalog.json")
    _check_child_links(ctx)
    _check_stac_links_rel_abs(ctx)

   
    _assert(ctx, data.get("osc:type") == "project", "'osc:type' must be 'project'")
    
    _check_osc_cross_ref_array(ctx, "osc:workflows", "workflows")
    
    _check_themes(ctx)

    _has_extensions(ctx, ["osc", "contacts"])
    _require_technical_officer(ctx)



def _validate_product(ctx):
    data = ctx["data"]
    _assert(ctx, data.get("type") == "Collection", "type must be 'Collection'")
    _has_extensions(ctx, ["osc"])
    _ensure_id_is_folder_name(ctx)
    _require_via_link(ctx)

    _require_parent_link(ctx, "../catalog.json")
    _require_root_link(ctx, "../../catalog.json")
    _check_stac_links_rel_abs(ctx, include_item_child=False)

    _assert(ctx, data.get("osc:type") == "product", "'osc:type' must be 'product'")
    _assert(ctx, isinstance(data.get("osc:project"), str), "'osc:project' must be a string")
    
    _check_osc_cross_ref(ctx, data.get("osc:project"), "projects", required=True)
    _check_osc_cross_ref_array(ctx, "osc:variables", "variables")
    _check_osc_cross_ref_array(ctx, "osc:missions", "eo-missions")
    _check_osc_cross_ref(ctx, data.get("osc:experiment"), "experiments")

    _check_themes(ctx)


def _validate_root(ctx):
    if ctx["data"].get("type") != "Catalog":
        ctx["errors"].append("type must be 'Catalog'")
    if ctx["data"].get("id") != "osc":
        ctx["errors"].append("id must be 'osc'")
    if ctx["data"].get("title") != "Open Science Catalog":
        ctx["errors"].append("title must be 'Open Science Catalog'")

    _require_root_link(ctx, "./catalog.json")
    
    if _get_link_with_rel(ctx["data"], 'parent'):
        ctx["errors"].append("must NOT have a parent")
        
    _check_stac_links_rel_abs(ctx)
    _require_child_links_for_other_json(ctx, ROOT_CHILDREN)

def _validate_sub_catalogs(ctx, child_stac_type):
    if ctx["data"].get("type") != "Catalog":
        ctx["errors"].append("type must be 'Catalog'")
        
    _ensure_id_is_folder_name(ctx)
    _require_parent_link(ctx, "../catalog.json")
    _require_root_link(ctx, "../catalog.json")
    _check_stac_links_rel_abs(ctx)
    
    rel_type = 'item' if child_stac_type == 'Record' else 'child'
    _require_child_links_for_other_json(ctx, None, child_stac_type.lower(), rel_type)
    

def _validate_eo_mission(ctx):
    if ctx["data"].get("type") != "Catalog":
        ctx["errors"].append("type must be 'Catalog'")
        
    _ensure_id_is_folder_name(ctx)
    _require_via_link(ctx)
    _require_parent_link(ctx, "../catalog.json")
    _require_root_link(ctx, "../../catalog.json")
    _check_child_links(ctx)
    _check_stac_links_rel_abs(ctx)

def _validate_theme(ctx):
    if ctx["data"].get("type") != "Catalog":
        ctx["errors"].append("type must be 'Catalog'")
        
    _ensure_id_is_folder_name(ctx)
    _require_parent_link(ctx, "../catalog.json")
    _require_root_link(ctx, "../../catalog.json")
    _check_child_links(ctx)
    _check_stac_links_rel_abs(ctx)
    _check_preview_image(ctx)

def _validate_variable(ctx):
    if ctx["data"].get("type") != "Catalog":
        ctx["errors"].append("type must be 'Catalog'")
        
    _has_extensions(ctx, ["themes"])
    _ensure_id_is_folder_name(ctx)
    _require_via_link(ctx)
    _require_parent_link(ctx, "../catalog.json")
    _require_root_link(ctx, "../../catalog.json")
    _check_child_links(ctx)
    _check_stac_links_rel_abs(ctx)
    _check_themes(ctx)

def _validate_workflow(ctx):
    pass
    # data = ctx["data"]
    # if data.get("type") != "Feature":
    #     ctx["errors"].append("type must be 'Feature'")
        
    # _ensure_id_is_folder_name(ctx)
    # _require_parent_link(ctx, "../catalog.json")
    # _require_root_link(ctx, "../../catalog.json")
    # _check_child_links(ctx, "experiments", "record")
    # _check_stac_links_rel_abs(ctx, False)

    # props = data.get("properties", {})
    # if not isinstance(props.get("osc:project"), str):
    #     ctx["errors"].append("'osc:project' must be a string")
        
    # _check_osc_cross_ref(ctx, props.get("osc:project"), "projects", True)

def _validate_experiment(ctx):
    pass
    # data = ctx["data"]
    # if data.get("type") != "Feature":
    #     ctx["errors"].append("type must be 'Feature'")
    
    # _ensure_id_is_folder_name(ctx)
    # _require_parent_link(ctx, "../catalog.json")
    # _require_root_link(ctx, "../../catalog.json")
    # _check_child_links(ctx)
    # _check_stac_links_rel_abs(ctx, False)

    # props = data.get("properties", {})
    # if not isinstance(props.get("osc:workflow"), str):
    #     ctx["errors"].append("'osc:workflow' must be a string")
        
    # _check_osc_cross_ref(ctx, props.get("osc:workflow"), "workflows", True)
    
    # _has_link_with_rel(ctx, "environment")
    # _has_link_with_rel(ctx, "input")


def _validate_relative_schema(ctx, schema_file):

    schema_file = Path(__file__).resolve().parent / schema_file
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    with open(ctx['file_path'], 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Create a base URI for the folder containing the schema
    base_uri = Path(schema_file).absolute().parent.as_uri() + "/"
    resolver = RefResolver(base_uri=base_uri, referrer=schema)
    try:
        validate(instance=data, schema=schema, resolver=resolver)
    except Exception as e:
        ctx['errors'].append(e)


#TODO: Implement Item checks
def _validate_user_content(ctx):
    pass

def validateOSCEntry(data: dict, catalog_root: Path) -> List[str]:
    """
    Validates a STAC project (or catalog/collection) against OSC rules.
    """

    errors = []
    catalog_root = Path(catalog_root).resolve()
    
    # infer the objects's location in the OSC structure
    try:
        file_path = _infer_file_path(data, catalog_root)
    except ValueError as e:
        errors.append(str(e))
        return errors
    

    # Generate validation context
    rel_path = "/" + file_path.relative_to(catalog_root).as_posix()
    
    is_root_catalog = rel_path.endswith("/catalog.json") and data.get("id") == "osc"
    is_eo_mission = "/eo-missions/" in rel_path and rel_path.endswith("/catalog.json")
    is_product = "/products/" in rel_path and rel_path.endswith("/collection.json")
    is_project = "/projects/" in rel_path and rel_path.endswith("/collection.json")
    is_theme = "/themes/" in rel_path and rel_path.endswith("/catalog.json")
    is_variable = "/variables/" in rel_path and rel_path.endswith("/catalog.json")
    is_workflow = "/workflows/" in rel_path and rel_path.endswith("/record.json")
    is_experiment = "/experiments/" in rel_path and rel_path.endswith("/record.json")
    
    is_sub_catalog_root = bool(re.search(r"/(eo-missions|products|projects|themes|variables|workflows|experiments)/catalog\.json", rel_path))
 
    # Context object to pass around
    ctx = {
        "data": data,
        "file_path": file_path,
        "root": catalog_root,
        "errors": errors
    }

    # do General Checks
    if (data.get("stac_version") not in ["1.0.0", "1.1.0"]) and not(is_experiment or is_workflow):
        errors.append("stac_version must be '1.0.0' or '1.1.0'")
    
    if data.get("type") in ["Catalog", "Collection"]:
        title = data.get("title")
        if not (isinstance(title, str) and len(title) > 0):
            errors.append("must have a title")

    # _no_duplicated_links(ctx)
    
    # call specific validation function
    if is_sub_catalog_root:

        child_entity = Path(rel_path).parent.name
        child_stac_type = 'Catalog'
        if child_entity in ['products', 'projects']:
            child_stac_type = 'Collection'
        elif child_entity in ['workflows', 'experiments']:
            child_stac_type = 'Record'
        _validate_sub_catalogs(ctx, child_stac_type)
        
    elif is_root_catalog:
        # validate schema
        schema_path = 'schemas/catalog.json'
        _validate_relative_schema(ctx, schema_path)
        #validate custom rules
        _validate_root(ctx)
    elif is_eo_mission:
        _validate_relative_schema(ctx, 'schemas/eo-missions/children.json')
        _validate_eo_mission(ctx)
    elif is_product:
        _validate_relative_schema(ctx, 'schemas/products/children.json')
        _validate_product(ctx)
    elif is_project:
        _validate_relative_schema(ctx, 'schemas/projects/children.json')
        _validate_project(ctx)
    elif is_theme:
        _validate_relative_schema(ctx,  'schemas/themes/children.json')
        _validate_theme(ctx)
    elif is_variable:
        _validate_relative_schema(ctx, 'schemas/variables/children.json')
        _validate_variable(ctx)
    elif is_workflow:
        _validate_relative_schema(ctx, 'schemas/workflows/children.json')
        _validate_workflow(ctx)
    elif is_experiment:
        _validate_relative_schema(ctx, 'schemas/experiments/children.json')
        _validate_experiment(ctx)
    else:
        ## TODO: add users updates
        if "/products/" in rel_path: 
            _validate_user_content(ctx)
        else:
            errors.append(f"Validation context could not be determined for path: {rel_path}")

    return errors

def validate_catalog(root_path):
    root = Path(root_path).resolve()
    if not root.exists():
        print(f"Error: Path {root} does not exist.")

    errors = []
    error_files = []

    # Recursive walk
    for current_dir, _, files in os.walk(root):
        for file in files:
            if file.endswith(".json"):
                full_path = Path(current_dir) / file
                with open(full_path, 'r', encoding='utf-8') as f:
                    stac_object = json.load(f)
                file_errors = validateOSCEntry(stac_object, root)
                if file_errors:
                    errors.append(file_errors)
                    error_files.append(full_path)
    
    return errors, error_files