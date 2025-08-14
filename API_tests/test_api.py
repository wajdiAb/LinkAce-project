# tests/api/test_links.py
import os
import uuid
import requests
from urllib.parse import urljoin

from dotenv import load_dotenv; load_dotenv()
# fsddf
BASE_URL = os.getenv("BASE_URL").rstrip("/")
API_TOKEN = os.getenv("LINKACE_API_TOKEN") or os.getenv("API_TOKEN")

def api(path=""):
    # e.g. /api/v2/links, /api/v2/links/{id}
    return urljoin(BASE_URL + "/", f"api/v2/links{path}")

def auth_headers():
    assert API_TOKEN, "Missing LINKACE_API_TOKEN in environment"
    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }

def get_payload(obj):
    """Handle both {'data': {...}} and {...}"""
    if isinstance(obj, dict) and "data" in obj and isinstance(obj["data"], dict):
        return obj["data"]
    return obj

def test_get_links():
    
    r = requests.get(api(), headers=auth_headers())
    print(r.status_code, r.text)
    assert r.status_code == 200
    data = r.json()
    # allow array or {"data":[...]}
    assert isinstance(data, (list, dict))
    if isinstance(data, dict):
        assert "data" in data
        assert isinstance(data["data"], list)

def test_create_link():
    print(f'{BASE_URL}')
    unique_url = f"https://example.com/?q={uuid.uuid4()}"
    # unique_url = f"https://www.wikipedia.org/"
    payload = {"url": unique_url, "title": "wikipedia"}

    r = requests.post(api(), json=payload, headers=auth_headers())
    print("Create:", r.status_code, r.text)
    assert r.status_code == 200

    obj = get_payload(r.json())
    # some installs return the object directly, others wrap it
    link_id = obj.get("id")
    assert link_id, f"Response missing id: {obj}"

    # server may normalize url/title; just check they exist
    assert "url" in obj and "title" in obj
# 
def test_delete_link():
    # create
    # unique_url = f"https://example2.com/?q={uuid.uuid4()}"
    unique_url = f"https://www.wikipedia.org/"
    create = requests.post(
        api(), json={"url": unique_url, "title": "Delete Test"}, headers=auth_headers()
    )
    print("Create:", create.status_code, create.text)
    assert create.status_code in (200, 201)
    link = get_payload(create.json())
    link_id = link["id"]

    # delete
    d = requests.delete(api(f"/{link_id}"), headers=auth_headers())
    print("Delete:", d.status_code, d.text)
    assert d.status_code == 200

    # verify gone
    g = requests.get(api(f"/{link_id}"), headers=auth_headers())
    print("Get-after-delete:", g.status_code, g.text)
    assert g.status_code == 404

    t = requests.delete(BASE_URL + "/api/v2/trash/clear", headers=auth_headers(),json={"model": "links"})
    print("Trash clear:", t.status_code, t.text)
    assert t.status_code == 200

def test_invalid_token():
    r = requests.get(api(), headers={"Accept": "application/json", "Authorization": "Bearer bad"})
    print("Invalid-token:", r.status_code, r.text)
    assert r.status_code == 401 # Unauthorized

def test_create_link_missing_url_returns_4xx():
    # Missing required "url" should be rejected
    r = requests.post(api(), json={"title": "No URL"}, headers=auth_headers())
    print("Create missing url:", r.status_code, r.text)
    # LinkAce typically returns 422 for validation errors; allow 400 just in case
    assert r.status_code in (400, 422)






