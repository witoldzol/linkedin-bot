# refactor code 
we keep duplicating dynamodb resource code
move it to main and pass as param

# use logging instead of prints

## DONE

# create dynamodb
columns: 
quote :str> partition
author: str 
used : bool > range ( we want to get only non used items quick)

# create uploader function
has access to dynamodb
parse input into msg & author
when uploading strip whitespace left & right
when uploading use ConditionExpression on quote to dedup
print how many go uploaded, how many got deduped

# update publisher lambda
it can read from dynamo, and update rows
when it reads and publishes quote to linkedin, it marks that quote as 'used'

# create sns topic
when we successfully post to linkedin, send message to sns so that I get an email with the posted message

# delete sns topic
use telegram instead - its faster than email

# create event trigger in cloudwatch, set retry=0

# remove sys.exit()  from code
just raise and let Lambda handle it, if call is sync it will not retry

