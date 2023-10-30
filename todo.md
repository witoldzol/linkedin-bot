# create dynamodb
columns: 
quote :str> partition
author: str 
used : bool > range ( we want to get only non used items quick)

# create uploader lambda
has access to dynamodb
when uploading strip whitespace left & right
when uploading use ConditionExpression on quote to dedup
print how many go uploaded, how many got deduped

# update publisher lambda
it can rean read from dynamo, and update rows
when it reads and publishes quote to linkedin, it marks that quote as 'used'

