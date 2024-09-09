import json
import boto3
from dicttoxml import dicttoxml
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info(f"Received ACORD 103 event: {json.dumps(event)}")
    
    try:
        # Parse the incoming event
        body = json.loads(event['body'])
        
        logger.info(f"Parsed request body: {json.dumps(body)}")
        
        # Process the ACORD 103 request
        # This is a placeholder for your actual business logic
        response_data = {
            "TXLife": {
                "UserAuthResponse": {
                    "TransResult": {
                        "ResultCode": {"tc": "1", "value": "Success"},
                        "ResultInfo": {
                            "ResultInfoCode": {"tc": "1", "value": "Success"},
                            "ResultInfoDesc": f"ACORD 103 request processed successfully"
                        }
                    }
                },
                "TXLifeResponse": {
                    "TransRefGUID": body['TXLife']['TXLifeRequest']['TransRefGUID'],
                    "TransType": body['TXLife']['TXLifeRequest']['TransType'],
                    "TransExeDate": "2024-08-30",  # Replace with actual date
                    "TransExeTime": "15:30:00",  # Replace with actual time
                    "TransResult": {
                        "ResultCode": {"tc": "1", "value": "Success"},
                        "ResultInfo": {
                            "ResultInfoCode": {"tc": "1", "value": "Success"},
                            "ResultInfoDesc": f"ACORD 103 request processed successfully"
                        }
                    },
                    "OLifE": {
                        "Holding": {
                            "Policy": {
                                "PolNumber": body['TXLife']['TXLifeRequest']['OLifE']['Holding']['Policy']['PolNumber'],
                                # Add more fields as per ACORD 103 specification
                            }
                        }
                    }
                }
            }
        }
        
        logger.info(f"Generated response data: {json.dumps(response_data)}")
        
        # Determine the response format based on the Accept header
        accept_header = event['headers'].get('Accept', 'application/json')
        
        if 'xml' in accept_header.lower():
            response_body = dicttoxml(response_data, custom_root='TXLife', attr_type=False)
            content_type = 'application/xml'
            logger.info("Returning XML response")
        else:
            response_body = json.dumps(response_data)
            content_type = 'application/json'
            logger.info("Returning JSON response")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': content_type
            },
            'body': response_body
        }
    
    except Exception as e:
        logger.error(f"Error processing ACORD 103 request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }
