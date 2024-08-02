import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info("Event: %s", json.dumps(event))

    try:
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
    
    except Exception as e:
        logger.error("Error: %s", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }

