import requests
import uuid

API_URL = "http://localhost/api/v2/links"
API_TOKEN = "1|M5RqwZ6db4OEK2sSitRyR6SsZScUz0UOm0jZgRP876261d63"  # Replace with your actual API token

def test_get_links():
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {API_TOKEN}",
    }
    response = requests.get(API_URL, headers=headers)
    print(response.text)  # For debugging
    assert response.status_code == 200
    data = response.json()
    assert "data" in data or isinstance(data, list)  # Adjust depending on response format


def test_create_link():
    unique_url = f"https://www.example.com/?q={uuid.uuid4()}"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "url": unique_url,
        "title": "Example Website"
    }
    response = requests.post(API_URL, json=payload, headers=headers)
    print(response.text)
    assert response.status_code in [200, 201]
    data = response.json()
    assert "id" in data
    assert data["url"] == payload["url"]
    assert data["title"] == payload["title"]

def test_delete_link():
    # Step 1: Create a unique link
    unique_url = f"https://www.example.com/?q={uuid.uuid4()}"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "url": unique_url,
        "title": "Delete Test"
    }
    create_resp = requests.post(API_URL, json=payload, headers=headers)
    print("Create response:", create_resp.text)
    assert create_resp.status_code in [200, 201]
    link = create_resp.json()
    link_id = link["id"]

    # Step 2: Delete the link
    delete_url = f"{API_URL}/{link_id}"
    delete_resp = requests.delete(delete_url, headers=headers)
    print("Delete response:", delete_resp.text)
    assert delete_resp.status_code in [200, 204]  # LinkAce may return 200 OK or 204 No Content

    # Step 3: Verify the link no longer exists
    get_resp = requests.get(delete_url, headers=headers)
    print("Get-after-delete response:", get_resp.text)
    assert get_resp.status_code == 404

# def test_auth_required():
#     url = "http://localhost/api/v2/links"
#     # No headers
#     response = requests.get(url)
#     print("No-auth response:", response.text)
#     assert response.status_code in [401, 403]


def test_invalid_token():
    url = "http://localhost/api/v2/links"
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer totallywrongtoken"
    }
    response = requests.get(url, headers=headers)
    print("Invalid-token response:", response.text)
    assert response.status_code in [401, 403]
