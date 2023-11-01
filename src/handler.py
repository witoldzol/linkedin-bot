import random
from typing import List, Dict
import boto3
import sys
import os

# we use lib to separate requried packages from unnecessary crap like pip, setuptools etc
# because we have it separated, we can package it and upload with code
# we use sys.path.insert to add this folder to pythonpath so that python can find dependencies
sys.path.insert(0, "lib")
import requests
import sentry_sdk

sentry_sdk.init(
    dsn = os.environ.get("SENTRY_DSN"),
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

def get_quotes(table_name: str, limit: int) -> List[Dict[str, str]]:
    region = os.environ.get("AWS_REGION")
    dynamodb = boto3.resource("dynamodb", region_name=region)
    table = dynamodb.Table(table_name)
    expression_attribute_names = {"#used": "used"}
    expression_attribute_values = {":val": 0}
    filter_expression = "#used = :val"
    scan_response = table.scan(
        FilterExpression=filter_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values,
        Limit=limit,
    )
    items = scan_response.get("Items", [])
    return items


def get_user_id(token: str) -> str:
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    user_id = ""
    if response.ok:
        user_id = response.json()["sub"]
    else:
        raise Exception("Error getting user id from linkedin: ", response.json())
    return user_id


def mark_quote_as_used_in_db(key_value: str):
    print("Marking quote as `used`")
    region = os.environ.get("AWS_REGION")
    dynamodb = boto3.resource("dynamodb", region_name=region)
    table_name = "quotes"
    table = dynamodb.Table(table_name)
    key = {"msg": key_value}
    update_expression = "SET #attributeName = :newValue"
    expression_attribute_names = {"#attributeName": "used"}
    expression_attribute_values = {":newValue": 1}
    print(f"Updating key: {key}")
    table.update_item(
        Key=key,
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values,
    )
    print("Successfully marked item in dynamodb as `used`")


def post_on_linkedin_timeline(msg: str, token: str, user_id: str) -> None:
    print("Posting on linkedin timeline")
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    body = {
        "author": f"urn:li:person:{user_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": f"{msg}"},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }
    response = requests.post(url, json=body, headers=headers)
    if response.ok:
        print("Successfuly posted message on the timeline")
    else:
        print("Error posting to timeline: ", response.json())


def send_telegram_message(message):
    message = f"This message was posted on your timeline:\n\n{message}"
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not chat_id:
        raise Exception("TELEGRAM_CHAT_ID variable not set, exiting")
    telegram_token = os.environ.get("TELEGRAM_TOKEN")
    if not telegram_token:
        raise Exception("TELEGRAM_TOKEN variable not set, exiting")
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Message sent successfully to telegram channel")
    else:
        print("Failed to send message to telegram channel")
        print(response.json())


def main(event, context=None):
    linkedin_user_id = os.environ.get("LINKEDIN_USER")
    linkedin_token = os.environ.get("LINKEDIN_TOKEN")
    if not linkedin_token:
        raise Exception("LINKEDIN_TOKEN var not set, exiting")
    if not linkedin_user_id:
        raise Exception("LINKEDIN_USER var not set, exiting")
    quotes = get_quotes("quotes", 10)
    random_quote: Dict[str, str] = random.choice(quotes)
    text = f'{random_quote["msg"]}\n- {random_quote["author"]}'
    print(f"Selected random quote:\n{text}\n")
    post_on_linkedin_timeline(text, linkedin_token, linkedin_user_id)
    mark_quote_as_used_in_db(random_quote["msg"])
    send_telegram_message(text)


if __name__ == "__main__":
    main({})
