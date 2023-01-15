def test_success_create(client, farmer, success_create_scouting):
    response = client.post(
        f"/scouting?api_key={farmer.apikey}",
        json=success_create_scouting,
    )

    assert response.status_code == 201


def test_invalid_geometry_create(client, farmer, invalid_geometry_create_scouting):
    response = client.post(
        f"/scouting?api_key={farmer.apikey}",
        json=invalid_geometry_create_scouting,
    )

    assert response.status_code == 422


def test_invalid_note_type_create(client, farmer, invalid_note_type_create_scouting):
    response = client.post(
        f"/scouting?api_key={farmer.apikey}",
        json=invalid_note_type_create_scouting,
    )

    assert response.status_code == 422
