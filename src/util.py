from typing import List, Dict
import os
import boto3

""" MANUAL USE ONLY"""

source_table_name = 'quotes'
destination_table_name = 'used_quotes'

def copy_and_delete_from_dynamodb_table(source_table_name, destination_table_name):
    dynamodb = boto3.resource('dynamodb')
    source_table = dynamodb.Table(source_table_name)
    destination_table = dynamodb.Table(destination_table_name)
    scan_response = get_quotes(source_table_name, 50)
    # Copy each item to the destination table
    for item in scan_response:
        del item['used']
        destination_table.put_item(Item=item)
    print(f"Copied {len(scan_response)} items from table: {source_table_name} to table: {destination_table_name}")
    # Delete items from the source table
    for item in scan_response:
        source_table.delete_item(
            Key={
                'msg': item['msg']
            }
        )
    print(f"Deleted {len(scan_response)} items from table: {source_table_name}")

# this is a copy from handler.py - with modified attribute (:val: 1 instead of 0)
def get_quotes(table_name: str, limit: int) -> List[Dict[str, str]]:
    region = os.environ.get("AWS_REGION")
    dynamodb = boto3.resource("dynamodb", region_name=region)
    table = dynamodb.Table(table_name)
    expression_attribute_names = {"#used": "used"}
    expression_attribute_values = {":val": 1}
    filter_expression = "#used = :val"
    scan_response = table.scan(
        FilterExpression=filter_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values,
        Limit=limit,
    )
    items = scan_response.get("Items", [])
    return items


# def mark_quote_as_used_in_db(key_value: str):
#     print("Marking quote as `used`")
#     region = os.environ.get("AWS_REGION")
#     dynamodb = boto3.resource("dynamodb", region_name=region)
#     table_name = "quotes"
#     table = dynamodb.Table(table_name)
#     key = {"msg": key_value}
#     update_expression = "SET #attributeName = :newValue"
#     expression_attribute_names = {"#attributeName": "used"}
#     expression_attribute_values = {":newValue": 1}
#     print(f"Updating key: {key}")
#     table.update_item(
#         Key=key,
#         UpdateExpression=update_expression,
#         ExpressionAttributeNames=expression_attribute_names,
#         ExpressionAttributeValues=expression_attribute_values,
#     )
#     print("Successfully marked item in dynamodb as `used`")


# def parse_quotes(filename) -> List[Tuple[str,str]]:
#     quotes = []
#     c = chr(8211)  # this is a long dash -
#     # check what type of separator we use in the file
#     with open(filename, "r") as f:
#         first_line = f.readline()
#         result = first_line.split(c, 1)
#         if len(result) == 2:
#             print("We have a long dash")
#         else:
#             print("It's a normal dash")
#             c = "-"
#     with open(filename, "r") as f:
#         for l in f:
#             quote_and_author = l.rsplit(c)
#             if len(quote_and_author) > 2:
#                 raise Exception(f"There is extra separator in this quote or author:\n{quote_and_author}")
#             msg, author = quote_and_author
#             author = author.strip()
#             if not author:
#                 raise Exception(f"Error, empty author. Line: {l}")
#             msg = msg.strip()
#             if not msg:
#                 raise Exception(f"Error, empty msg. Line: {l}")
#             item = (author, msg)
#             quotes.append(item)
#     return quotes



# def replace_dash_with_pipe(filename):
#     file_output = "piped"
#     separator = "-"
#     with open(filename, "r") as f:
#         with open(file_output, "a") as wf:
#             for l in f:
#                 arr = l.split(separator)
#                 if len(arr) > 2:
#                     print("============================================================")
#                     print(f"{arr}")
#                     print("============================================================")
#                 replaced = l.replace("-", "|")
#                 wf.write(replaced)

#
# def parse_quotes(filename) -> List[Tuple[str,str]]:
#     quotes = []
#     c = chr(8211)  # this is a long dash -
#     # check what type of separator we use in the file
#     with open(filename, "r") as f:
#         first_line = f.readline()
#         result = first_line.split(c, 1)
#         if len(result) == 2:
#             print("We have a long dash")
#         else:
#             print("It's a normal dash")
#             c = "-"
#     with open(filename, "r") as f:
#         for l in f:
#             quote_and_author = l.rsplit(c)
#             if len(quote_and_author) > 2:
#                 raise Exception(f"There is extra separator in this quote or author:\n{quote_and_author}")
#             msg, author = quote_and_author
#             author = author.strip()
#             if not author:
#                 raise Exception(f"Error, empty author. Line: {l}")
#             msg = msg.strip()
#             if not msg:
#                 raise Exception(f"Error, empty msg. Line: {l}")
#             item = (author, msg)
#             quotes.append(item)
#     return quotes




copy_and_delete_from_dynamodb_table(source_table_name, destination_table_name)
