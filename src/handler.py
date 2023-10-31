import random
from typing import List
import boto3
import sys
import os

# we use lib to separate requried packages from unnecessary crap like pip, setuptools etc
# because we have it separated, we can package it and upload with code
# we use sys.path.insert to add this folder to pythonpath so that python can find dependencies
sys.path.insert(0, "lib")
import requests


def get_quotes(table_name: str, limit: int) -> List[str]:
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
        print("Error getting user id from linkedin: ", response.json())
        sys.exit(1)
    return user_id


def update_value(key_value: str):
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
    print("Update sucessful")


def post_on_timeline(msg: str, token: str, user_id: str) -> None:
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


def main(event, context=None):
    user_id = os.environ.get("LINKEDIN_USER")
    token = os.environ.get("LINKEDIN_TOKEN")
    if not token:
        print("Linkedin token not found, exiting")
        sys.exit(1)
    if not user_id:
        print("Linkedin user id not found, exiting")
        sys.exit(1)
    quotes = get_quotes("quotes", 10)
    random_quote = random.choice(quotes)
    text = f'{random_quote["msg"]}\n- {random_quote["author"]}'
    print(f"Selected random quote:\n{text}")
    print("Posting on linkedin timeline")
    # post_on_timeline(text, token, user_id)
    print("Successfuly posted on timeline, marking quote as `used`")
    update_value(random_quote["msg"])


if __name__ == "__main__":
    main({})