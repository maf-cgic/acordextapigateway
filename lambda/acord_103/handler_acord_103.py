import json
import logging
import dicttoxml  # Ensure this package is installed

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def generate_response(body, status_code=200, format="json"):
    if format == "json":
        return {
            "statusCode": status_code,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(body)
        }
    elif format == "xml":
        return {
            "statusCode": status_code,
            "headers": {"Content-Type": "application/xml"},
            "body": dicttoxml.dicttoxml(body, custom_root='Response', attr_type=False).decode()
        }

def handler(event, context):
    logger.info("Event: %s", json.dumps(event))
    response_format = "json"  # Default to JSON
    if 'application/xml' in event.get('headers', {}).get('Accept', ''):
        response_format = "xml"

    try:
        body = json.loads(event['body'])
        acord = body.get('ACORD')
        
        # Process the ACORD-compliant application data here (e.g., store in a database)
        
        response_body = {
            "RqUID": acord.get('InsuranceSvcRq').get('RqUID'),
            "StatusCd": "201",
            "StatusDesc": "ACORD 103 submitted successfully"
        }
        return generate_response(response_body, status_code=201, format=response_format)
    
    except ValueError as ve:
        logger.error("Invalid input: %s", str(ve))
        response_body = {"error": "Invalid input", "message": str(ve)}
        return generate_response(response_body, status_code=400, format=response_format)
    
    except Exception as e:
        logger.error("Internal server error: %s", str(e))
        response_body = {"error": "Internal server error", "message": str(e)}
        return generate_response(response_body, status_code=500, format=response_format)

