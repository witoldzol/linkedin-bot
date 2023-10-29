import sys

# we use lib to separate requried packages from unnecessary crap like pip, setuptools etc
# because we have it separated, we can package it and upload with code
# we use sys.path.insert at add this folder to pythonpath so that it can find dependencies
sys.path.insert(0, "lib")
import requests


def main(event, context=None):
    response = requests.get("http://google.com")
    print(response.status_code)
    print(f"Event is : {event}")
    print(f"Context is : {context}")


if __name__ == "__main__":
    main({})
