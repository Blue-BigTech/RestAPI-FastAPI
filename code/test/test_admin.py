import pytest

def test_success_create_company(client, superadmin, success_create_company):

    response = client.post(
        f"/admin/company?api_key={superadmin.apikey}",
        json=success_create_company,
    )

    success = success_create_company
    del success["password"]

    assert response.status_code == 200
    assert response.json().items() >= success.items()

    return success_create_company


