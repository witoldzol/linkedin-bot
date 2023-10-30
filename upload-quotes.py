import os
import boto3


def parse_quotes(filename):
    quotes = []
    with open(filename, "r") as f:
        c = chr(8211)  # this is a long dash -
        for l in f:
            msg, author = l.rsplit(c, 1)
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
    return {"author": item[0], "msg": item[1], "used": 0}


def main():
    region = os.environ.get("AWS_DEFAULT_REGION")
    dynamodb = boto3.resource("dynamodb", region_name=region)
    table = dynamodb.Table("quotes")
    quotes = parse_quotes("quotes")
    for q in quotes:
        item = get_item(q)
        response = ""
        try:
            response = table.put_item(
                Item=item, ConditionExpression="attribute_not_exists(msg)"
            )
            print(f"Successfull insertion : {response}")
            print('----------------------------------')
        except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            print(f"Item already exists.\nSkipped item: {item}")
        except Exception as e:
            print(f"Exception {e}")


if __name__ == "__main__":
    main()
