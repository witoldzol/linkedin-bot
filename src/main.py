import sys
import os

# we use lib to separate requried packages from unnecessary crap like pip, setuptools etc
# because we have it separated, we can package it and upload with code
# we use sys.path.insert to add this folder to pythonpath so that python can find dependencies
sys.path.insert(0, "lib")
import requests


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
    post_on_timeline("test", token, user_id)


if __name__ == "__main__":
    main({})
