import pytest


@pytest.mark.parametrize(
    "how_to_contact, date_time, topic, message, type_of_expert",
    [
        ("whatsapp", "2023-01-12 02:02:12", "general", "message", "local"),
        ("zoom", "2023-01-12 02:02:12", "disease", "message", "international"),
    ],
)
def test_success_schedule_call_create(
    client, farmer, how_to_contact, date_time, topic, message, type_of_expert
):
    payload = {
        "how_to_contact": how_to_contact,
        "date_time": date_time,
        "topic": topic,
        "message": message,
        "type_of_expert": type_of_expert,
    }

    response = client.post(
        f"/schedule_call?api_key={farmer.apikey}",
        json=payload,
    )

    assert response.status_code == 201


@pytest.mark.parametrize(
    "how_to_contact, date_time, topic, message, type_of_expert",
    [
        ("invalid", "2023-01-12 02:02:12", "general", "message", "local"),
        ("whatsapp", "2023-01-12 02:02:12", "invalid", "message", "local"),
        ("whatsapp", "2023-01-12 02:02:12", "general", "message", "invalid"),
        ("whatsapp", "", "general", "message", "local"),
    ],
)
def test_validation_schedule_call_create(
    client, farmer, how_to_contact, date_time, topic, message, type_of_expert
):
    payload = {
        "how_to_contact": how_to_contact,
        "date_time": date_time,
        "topic": topic,
        "message": message,
        "type_of_expert": type_of_expert,
    }

    response = client.post(
        f"/schedule_call?api_key={farmer.apikey}",
        json=payload,
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "how_to_contact, date_time, topic, message, type_of_expert",
    [
        ("whatsapp", "2023-01-12 02:02:12", "general", "", "local"),
    ],
)
def test_invalid_message_schedule_call_create(
    client, farmer, how_to_contact, date_time, topic, message, type_of_expert
):
    payload = {
        "how_to_contact": how_to_contact,
        "date_time": date_time,
        "topic": topic,
        "message": message,
        "type_of_expert": type_of_expert,
    }

    response = client.post(
        f"/schedule_call?api_key={farmer.apikey}",
        json=payload,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "The message is not valid"


def test_success_index(client, superadmin):
    response = client.get(f"/schedule_call?api_key={superadmin.apikey}")

    assert response.status_code == 200


def test_invalid_user_index(client, farmer):
    response = client.get(f"/schedule_call?api_key={farmer.apikey}")

    assert response.status_code == 404
    assert response.json()["detail"] == "User with given key and role does not exist"
