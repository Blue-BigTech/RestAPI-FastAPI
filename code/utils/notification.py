import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint
from typing import Literal, Any
from config import setting
from twilio.rest import Client

SENDER_EMAIL = {"name": "Alerts", "email": "alerts@mapmycrop.com"}
SENDER_PHONE_NUMBER = "+17742737442"


def _send_email(receiver: Any, subject: str, body: str) -> None:
    # Configure API key authorization: api-key
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = setting.SENDINBLUE_KEY

    # create an instance of the API class
    api_instance = sib_api_v3_sdk.SMTPApi(sib_api_v3_sdk.ApiClient(configuration))
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        sender=SENDER_EMAIL,
        to=[receiver],
        subject=subject,
        text_content=body,
    )

    try:
        # Send a transactional email
        api_response = api_instance.send_transac_email(send_smtp_email)
        # TODO: Remove print statement
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)


def _send_sms(contact: str, body: str):
    account_sid = setting.TWILIO_SID
    auth_token = setting.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)

    message = client.messages.create(to=contact, from_=SENDER_PHONE_NUMBER, body=body)
    # TODO: Remove print statement
    print(message)


def send_notification(
    type: Literal["WHATSAPP", "EMAIL", "SMS"],
    contact: str,
    body: str,
    **extra,
) -> None:
    if type == "EMAIL":
        if extra["subject"] == None or extra["name"] == None:
            raise Exception(
                f'Notifcation type {type} must have a "subject" and "name" as extra args'
            )

        _send_email({"name": extra["name"], "email": contact}, extra["subject"], body)

    elif type == "SMS":
        _send_sms(contact, body)

    elif type == "WHATSAPP":
        print(f"Sedn whatsapp to {contact} with {body}")

    else:
        raise Exception("Type did not match any of the given values")
