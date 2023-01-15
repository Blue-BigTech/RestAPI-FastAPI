def test_success_send_notification(client, farmer, success_create_contact):
    response = client.post(
        f"/contact?api_key={farmer.apikey}",
        json=success_create_contact,
    )

    assert response.status_code == 200


def test_invalid_title_send_notification(client, farmer, invalid_name_create_contact):
    response = client.post(
        f"/contact?api_key={farmer.apikey}",
        json=invalid_name_create_contact,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Name is not valid"


def test_invalid_phone_create_contact(client, farmer, invalid_phone_create_contact):
    response = client.post(
        f"/contact?api_key={farmer.apikey}",
        json=invalid_phone_create_contact,
    )

    assert response.status_code == 422


def test_invalid_message_create_contact(client, farmer, invalid_message_create_contact):
    response = client.post(
        f"/contact?api_key={farmer.apikey}",
        json=invalid_message_create_contact,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Message is not valid"
