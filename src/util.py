from typing import List, Dict
import os
import boto3

""" MANUAL USE ONLY """

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

copy_and_delete_from_dynamodb_table(source_table_name, destination_table_name)
