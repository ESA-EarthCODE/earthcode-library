import base64
import json
from urllib.parse import quote
import pystac

def generate_osc_editor_link(json_object, object_type, session_title=None) -> None:

    if type(json_object) is pystac.Collection:
        json_object = json_object.to_dict()

    if session_title is None:
        session_title = json_object['title']
    session_title = quote(session_title, safe="")
    # Use URL-safe base64 encoding (replaces + with - and / with _)

    base64_content = base64.urlsafe_b64encode(json.dumps(json_object).encode("utf-8")).decode("utf-8")
    
    # https://workspace.earthcode-staging.earthcode.eox.at/osc-editor?session=<your session title, e.g. "Add File">&automation=add-file&type=<osc type, e.g. "product">&file=<base64encoded content>
    url = f"https://workspace.earthcode-staging.earthcode.eox.at/osc-editor?session={session_title}&automation=add-file&&type={object_type}&file={base64_content}"

    return url