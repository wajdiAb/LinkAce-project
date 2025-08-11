# tests/api/test_links.py
import os
import uuid
import requests
from urllib.parse import urljoin

from dotenv import load_dotenv; load_dotenv()


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
    payload = {"url": unique_url, "title": "Example Website"}

    r = requests.post(api(), json=payload, headers=auth_headers())
    print("Create:", r.status_code, r.text)
    assert r.status_code in (200, 201)

    obj = get_payload(r.json())
    # some installs return the object directly, others wrap it
    link_id = obj.get("id")
    assert link_id, f"Response missing id: {obj}"

    # server may normalize url/title; just check they exist
    assert "url" in obj and "title" in obj

def test_delete_link():
    # create
    unique_url = f"https://example.com/?q={uuid.uuid4()}"
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
    assert d.status_code in (200, 204)

    # verify gone
    g = requests.get(api(f"/{link_id}"), headers=auth_headers())
    print("Get-after-delete:", g.status_code, g.text)
    assert g.status_code == 404

def test_invalid_token():
    r = requests.get(api(), headers={"Accept": "application/json", "Authorization": "Bearer bad"})
    print("Invalid-token:", r.status_code, r.text)
    assert r.status_code in (401, 403)





# import requests
# import uuid

# API_URL = "http://localhost/api/v2/links"
# API_TOKEN = "1|M5RqwZ6db4OEK2sSitRyR6SsZScUz0UOm0jZgRP876261d63"  # Replace with your actual API token

# def test_get_links():
#     headers = {
#         "Accept": "application/json",
#         "Authorization": f"Bearer {API_TOKEN}",
#     }
#     response = requests.get(API_URL, headers=headers)
#     print(response.text)  # For debugging
#     assert response.status_code == 200
#     data = response.json()
#     assert "data" in data or isinstance(data, list)  # Adjust depending on response format


# def test_create_link():
#     unique_url = f"https://www.example.com/?q={uuid.uuid4()}"
#     headers = {
#         "Accept": "application/json",
#         "Authorization": f"Bearer {API_TOKEN}",
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "url": unique_url,
#         "title": "Example Website"
#     }
#     response = requests.post(API_URL, json=payload, headers=headers)
#     print(response.text)
#     assert response.status_code in [200, 201]
#     data = response.json()
#     assert "id" in data
#     assert data["url"] == payload["url"]
#     assert data["title"] == payload["title"]

# def test_delete_link():
#     # Step 1: Create a unique link
#     unique_url = f"https://www.example.com/?q={uuid.uuid4()}"
#     headers = {
#         "Accept": "application/json",
#         "Authorization": f"Bearer {API_TOKEN}",
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "url": unique_url,
#         "title": "Delete Test"
#     }
#     create_resp = requests.post(API_URL, json=payload, headers=headers)
#     print("Create response:", create_resp.text)
#     assert create_resp.status_code in [200, 201]
#     link = create_resp.json()
#     link_id = link["id"]

#     # Step 2: Delete the link
#     delete_url = f"{API_URL}/{link_id}"
#     delete_resp = requests.delete(delete_url, headers=headers)
#     print("Delete response:", delete_resp.text)
#     assert delete_resp.status_code in [200, 204]  # LinkAce may return 200 OK or 204 No Content

#     # Step 3: Verify the link no longer exists
#     get_resp = requests.get(delete_url, headers=headers)
#     print("Get-after-delete response:", get_resp.text)
#     assert get_resp.status_code == 404

# # def test_auth_required():
# #     url = "http://localhost/api/v2/links"
# #     # No headers
# #     response = requests.get(url)
# #     print("No-auth response:", response.text)
# #     assert response.status_code in [401, 403]


# def test_invalid_token():
#     url = "http://localhost/api/v2/links"
#     headers = {
#         "Accept": "application/json",
#         "Authorization": "Bearer totallywrongtoken"
#     }
#     response = requests.get(url, headers=headers)
#     print("Invalid-token response:", response.text)
#     assert response.status_code in [401, 403]
