from typing import List, Tuple
import os
import boto3
import sys


filename = sys.argv[1]
def parse_quotes(filename) -> List[Tuple[str,str]]:
    quotes = []
    c = "|"
    with open(filename, "r") as f:
        for l in f:
            quote_and_author = l.rsplit(c)
            if len(quote_and_author) > 2:
                raise Exception(f"There is extra separator in this quote or author:\n{quote_and_author}")
            msg, author = quote_and_author
            author = author.strip()
            if not author:
                raise Exception(f"Error, empty author. Line: {l}")
            msg = msg.strip()
            if not msg:
                raise Exception(f"Error, empty msg. Line: {l}")
            item = (author, msg)
            quotes.append(item)
    return quotes

def get_item(item: tuple):
    return {"author": item[0], "msg": item[1]}


def main(filename):
    region = os.environ.get("AWS_DEFAULT_REGION")
    dynamodb = boto3.resource("dynamodb", region_name=region)
    table = dynamodb.Table("quotes")
    quotes = parse_quotes(filename)
    for q in quotes:
        item = get_item(q)
        print(f"{item=}")
        response = ""
        try:
            response = table.put_item(
                Item=item, ConditionExpression="attribute_not_exists(msg)"
            )
            print(f"Successfull insertion : {response}")
            print("----------------------------------")
        except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            print(f"Item already exists.\nSkipped item: {item}")
        except Exception as e:
            print(f"Exception {e}")


if __name__ == "__main__":
    main(filename)
