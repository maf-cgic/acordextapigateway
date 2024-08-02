import json

def handler(event, context):
    body = json.loads(event['body'])
    acord = body.get('ACORD')
    # Process the ACORD-compliant application data here (e.g., store in a database)

    response = {
        "statusCode": 201,
        "body": json.dumps({
            "RqUID": acord.get('InsuranceSvcRq').get('RqUID'),
            "StatusCd": "201",
            "StatusDesc": "Application submitted successfully"
        })
    }
    return response

