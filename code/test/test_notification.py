def test_success_send_notification(client, farmer, success_send_notification):
    response = client.post(
        f"/notification?api_key={farmer.apikey}",
        json=success_send_notification,
    )

    assert response.status_code == 200


def test_invalid_title_send_notification(
    client, farmer, invalid_title_send_notification
):
    response = client.post(
        f"/notification?api_key={farmer.apikey}",
        json=invalid_title_send_notification,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "The title is not valid"


def test_invalid_description_send_notification(
    client, farmer, invalid_description_send_notification
):
    response = client.post(
        f"/notification?api_key={farmer.apikey}", json=invalid_description_send_notification
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "The description is not valid"


def test_invalid_datetime_send_notification(
    client, farmer, invalid_datetime_send_notification
):
    response = client.post(
        f"/notification?api_key={farmer.apikey}",
        json=invalid_datetime_send_notification,
    )

    assert response.status_code == 422


def test_invalid_polygon_send_notification(
    client, farmer, invalid_polygon_send_notification
):
    response = client.post(
        f"/notification?api_key={farmer.apikey}",
        json=invalid_polygon_send_notification,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "The polygon is incorrect"
