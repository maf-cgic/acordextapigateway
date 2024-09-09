from aws_cdk import (
    Stack,
    aws_apigateway as apigateway,
    aws_lambda as _lambda,
    aws_sqs as sqs,
    aws_lambda_event_sources as event_sources,
    aws_cognito as cognito,
    CfnOutput,
)
from constructs import Construct
import json

class ApiGatewayWithAcordSchemaStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a new Cognito User Pool
        user_pool = cognito.UserPool(self, "UserPool",
                                     self_sign_up_enabled=True,
                                     auto_verify=cognito.AutoVerifiedAttrs(email=True))

        # Create a Cognito User Pool Client
        user_pool_client = cognito.UserPoolClient(self, "UserPoolClient",
            user_pool=user_pool,
            auth_flows=cognito.AuthFlow(
                admin_user_password=True,
                user_password=True,
                user_srp=True
            ),
            supported_identity_providers=[cognito.UserPoolClientIdentityProvider.COGNITO]
        )


        # SQS Queues for each Lambda
        sqs_queue_103 = sqs.Queue(self, "Acord103Queue", fifo=True)
        sqs_queue_1125 = sqs.Queue(self, "Acord1125Queue", fifo=True)
        sqs_queue_203 = sqs.Queue(self, "Acord203Queue", fifo=True)
        
        # Add SQS Queue for ACORD 302
        sqs_queue_302 = sqs.Queue(self, "Acord302Queue", fifo=True)



        # Lambda functions for each ACORD code
        lambda_103 = _lambda.Function(self, "Acord103Function",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="handler_acord_103.handler",
            code=_lambda.Code.from_asset("lambda/acord_103")
        )
        
        lambda_1125 = _lambda.Function(self, "Acord1125Function",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="handler_acord_1125.handler",
            code=_lambda.Code.from_asset("lambda/acord_1125")
        )
        
        lambda_203 = _lambda.Function(self, "Acord203Function",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="handler_acord_203.handler",
            code=_lambda.Code.from_asset("lambda/acord_203")
        )
        
        # Add Lambda function for ACORD 302
        lambda_302 = _lambda.Function(self, "Acord302Function",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="handler_acord_302.handler",
            code=_lambda.Code.from_asset("lambda/acord_302")
        )



        # Attach SQS as Event Source
        lambda_103.add_event_source(event_sources.SqsEventSource(sqs_queue_103))
        lambda_1125.add_event_source(event_sources.SqsEventSource(sqs_queue_1125))
        lambda_203.add_event_source(event_sources.SqsEventSource(sqs_queue_203))
        # Attach SQS as Event Source for ACORD 302
        # Check if the event source already exists before adding it
        existing_event_sources = lambda_302.node.children
        sqs_event_source_exists = any(isinstance(child, event_sources.SqsEventSource) for child in existing_event_sources)
        
        if not sqs_event_source_exists:
            lambda_302.add_event_source(event_sources.SqsEventSource(sqs_queue_302))


        
        # API Gateway setup

        api = apigateway.RestApi(
            self, "MyApi",
            deploy_options=apigateway.StageOptions(stage_name="dev"),
            endpoint_types=[apigateway.EndpointType.REGIONAL],
            description="API for ACORD insurance application processing",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=["*"],
                allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key", "X-Amz-Security-Token"]
            )
        )



        # Create the 'acord' resource once
        acord_resource = api.root.add_resource("acord")
        
        # ACORD 103 endpoint
        applications_103 = acord_resource.add_resource("103")
        applications_103.add_method("POST", apigateway.LambdaIntegration(lambda_103, proxy=True))
        
        # ACORD 1125 endpoint
        applications_1125 = acord_resource.add_resource("1125")
        applications_1125.add_method("PUT", apigateway.LambdaIntegration(lambda_1125, proxy=True))
        
        # ACORD 203 endpoint
        applications_203 = acord_resource.add_resource("203")
        applications_203.add_method("POST", apigateway.LambdaIntegration(lambda_203, proxy=True))
        
        # Add ACORD 302 endpoint
        applications_302 = acord_resource.add_resource("302")
        applications_302.add_method("POST", apigateway.LambdaIntegration(lambda_302, proxy=True))
        


        # Swagger integration
        swagger_definition = {
 "openapi": "3.0.1",
  "info": {
    "title": "ACORD Insurance API",
    "description": "API for ACORD insurance transactions",
    "version": "1.0.0"
  },
  "paths": {
    "/acord/103": {
      "post": {
        "summary": "Submit ACORD 103 New Business Submission for a Policy",
        "operationId": "submitAcord103",
        "requestBody": {
          "content": {
            "application/xml": {
              "schema": {
                "$ref": "#/components/schemas/ACORD103Request"
              }
            },
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/ACORD103RequestJSON"
              }
            }
          },
          "required": True
        },
        "responses": {
          "200": {
            "description": "Successful response",
            "content": {
              "application/xml": {
                "schema": {
                  "$ref": "#/components/schemas/ACORD103Response"
                }
              },
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ACORD103ResponseJSON"
                }
              }
            }
          },
          "400": {
            "description": "Bad request",
            "content": {
              "application/xml": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              },
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponseJSON"
                }
              }
            }
          },
          "500": {
            "description": "Internal server error",
            "content": {
              "application/xml": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              },
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponseJSON"
                }
              }
            }
          }
        }
      }
    },
    "/acord/1125": {
      "put": {
        "summary": "Submit ACORD 1125 Policy Change",
        "operationId": "submitAcord1125",
        "requestBody": {
          "content": {
            "application/xml": {
              "schema": {
                "$ref": "#/components/schemas/ACORD1125Request"
              }
            },
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/ACORD1125RequestJSON"
              }
            }
          },
          "required": True
        },
        "responses": {
          "200": {
            "description": "Successful response",
            "content": {
              "application/xml": {
                "schema": {
                  "$ref": "#/components/schemas/ACORD1125Response"
                }
              },
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ACORD1125ResponseJSON"
                }
              }
            }
          },
          "400": {
            "description": "Bad request",
            "content": {
              "application/xml": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              },
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponseJSON"
                }
              }
            }
          },
          "500": {
            "description": "Internal server error",
            "content": {
              "application/xml": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              },
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponseJSON"
                }
              }
            }
          }
        }
      }
    },
    "/acord/203": {
      "post": {
        "summary": "Submit ACORD 203 Pending Case Status Inquiry",
        "operationId": "submitAcord203",
        "requestBody": {
          "content": {
            "application/xml": {
              "schema": {
                "$ref": "#/components/schemas/ACORD203Request"
              }
            },
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/ACORD203RequestJSON"
              }
            }
          },
          "required": True
        },
        "responses": {
          "200": {
            "description": "Successful response",
            "content": {
              "application/xml": {
                "schema": {
                  "$ref": "#/components/schemas/ACORD203Response"
                }
              },
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ACORD203ResponseJSON"
                }
              }
            }
          },
          "400": {
            "description": "Bad request",
            "content": {
              "application/xml": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              },
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponseJSON"
                }
              }
            }
          },
          "500": {
            "description": "Internal server error",
            "content": {
              "application/xml": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              },
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponseJSON"
                }
              }
            }
          }
        }
      }
    },
    "/acord/302": {
      "post": {
        "summary": "Submit ACORD 302 Pending Case Status Update",
        "operationId": "submitAcord302",
        "requestBody": {
          "content": {
            "application/xml": {
              "schema": {
                "$ref": "#/components/schemas/ACORD302Request"
              }
            },
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/ACORD302RequestJSON"
              }
            }
          },
          "required": True
        },
        "responses": {
          "200": {
            "description": "Successful response",
            "content": {
              "application/xml": {
                "schema": {
                  "$ref": "#/components/schemas/ACORD302Response"
                }
              },
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ACORD302ResponseJSON"
                }
              }
            }
          },
          "400": {
            "description": "Bad request",
            "content": {
              "application/xml": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              },
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponseJSON"
                }
              }
            }
          },
          "500": {
            "description": "Internal server error",
            "content": {
              "application/xml": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              },
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponseJSON"
                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "ACORD1125Request": {
        "type": "object",
        "xml": {
          "name": "TXLife"
        },
        "properties": {
          "UserAuthRequest": {
            "$ref": "#/components/schemas/UserAuthRequest"
          },
          "TXLifeRequest": {
            "$ref": "#/components/schemas/TXLifeRequest"
          }
        }
      },
      "ACORD1125RequestJSON": {
        "type": "object",
        "properties": {
          "TXLife": {
            "type": "object",
            "properties": {
              "UserAuthRequest": {
                "$ref": "#/components/schemas/UserAuthRequestJSON"
              },
              "TXLifeRequest": {
                "$ref": "#/components/schemas/TXLifeRequestJSON"
              }
            }
          }
        }
      },
      "ACORD1125Response": {
        "type": "object",
        "xml": {
          "name": "TXLife"
        },
        "properties": {
          "UserAuthResponse": {
            "$ref": "#/components/schemas/UserAuthResponse"
          },
          "TXLifeResponse": {
            "$ref": "#/components/schemas/TXLifeResponse"
          }
        }
      },
      "ACORD1125ResponseJSON": {
        "type": "object",
        "properties": {
          "TXLife": {
            "type": "object",
            "properties": {
              "UserAuthResponse": {
                "$ref": "#/components/schemas/UserAuthResponseJSON"
              },
              "TXLifeResponse": {
                "$ref": "#/components/schemas/TXLifeResponseJSON"
              }
            }
          }
        }
      },
      "UserAuthRequest": {
        "type": "object",
        "properties": {
          "UserLoginName": {
            "type": "string"
          },
          "UserPswd": {
            "type": "string"
          },
          "VendorApp": {
            "type": "object",
            "properties": {
              "VendorName": {
                "type": "string"
              },
              "AppName": {
                "type": "string"
              },
              "AppVer": {
                "type": "string"
              }
            }
          }
        }
      },
      "UserAuthRequestJSON": {
        "type": "object",
        "properties": {
          "UserLoginName": {
            "type": "string"
          },
          "UserPswd": {
            "type": "string"
          },
          "VendorApp": {
            "type": "object",
            "properties": {
              "VendorName": {
                "type": "string"
              },
              "AppName": {
                "type": "string"
              },
              "AppVer": {
                "type": "string"
              }
            }
          }
        }
      },
      "TXLifeRequest": {
        "type": "object",
        "properties": {
          "TransRefGUID": {
            "type": "string"
          },
          "TransType": {
            "$ref": "#/components/schemas/TransType"
          },
          "TransExeDate": {
            "type": "string",
            "format": "date"
          },
          "TransExeTime": {
            "type": "string",
            "format": "time"
          },
          "OLifE": {
            "$ref": "#/components/schemas/OLifE"
          }
        }
      },
      "TXLifeRequestJSON": {
        "type": "object",
        "properties": {
          "TransRefGUID": {
            "type": "string"
          },
          "TransType": {
            "$ref": "#/components/schemas/TransTypeJSON"
          },
          "TransExeDate": {
            "type": "string",
            "format": "date"
          },
          "TransExeTime": {
            "type": "string",
            "format": "time"
          },
          "OLifE": {
            "$ref": "#/components/schemas/OLifEJSON"
          }
        }
      },
      "UserAuthResponse": {
        "type": "object",
        "properties": {
          "TransResult": {
            "$ref": "#/components/schemas/TransResult"
          },
          "SvrDate": {
            "type": "string",
            "format": "date"
          },
          "SvrTime": {
            "type": "string",
            "format": "time"
          }
        }
      },
      "UserAuthResponseJSON": {
        "type": "object",
        "properties": {
          "TransResult": {
            "$ref": "#/components/schemas/TransResultJSON"
          },
          "SvrDate": {
            "type": "string",
            "format": "date"
          },
          "SvrTime": {
            "type": "string",
            "format": "time"
          }
        }
      },
      "TXLifeResponse": {
        "type": "object",
        "properties": {
          "TransRefGUID": {
            "type": "string"
          },
          "TransType": {
            "$ref": "#/components/schemas/TransType"
          },
          "TransExeDate": {
            "type": "string",
            "format": "date"
          },
          "TransExeTime": {
            "type": "string",
            "format": "time"
          },
          "TransResult": {
            "$ref": "#/components/schemas/TransResult"
          },
          "OLifE": {
            "$ref": "#/components/schemas/OLifE"
          }
        }
      },
      "TXLifeResponseJSON": {
        "type": "object",
        "properties": {
          "TransRefGUID": {
            "type": "string"
          },
          "TransType": {
            "$ref": "#/components/schemas/TransTypeJSON"
          },
          "TransExeDate": {
            "type": "string",
            "format": "date"
          },
          "TransExeTime": {
            "type": "string",
            "format": "time"
          },
          "TransResult": {
            "$ref": "#/components/schemas/TransResultJSON"
          },
          "OLifE": {
            "$ref": "#/components/schemas/OLifEJSON"
          }
        }
      },
      "TransType": {
        "type": "object",
        "properties": {
          "@tc": {
            "type": "string"
          },
          "#text": {
            "type": "string"
          }
        }
      },
      "TransTypeJSON": {
        "type": "object",
        "properties": {
          "tc": {
            "type": "string"
          },
          "value": {
            "type": "string"
          }
        }
      },
      "TransResult": {
        "type": "object",
        "properties": {
          "ResultCode": {
            "$ref": "#/components/schemas/TransType"
          },
          "ResultInfo": {
            "type": "object",
            "properties": {
              "ResultInfoCode": {
                "$ref": "#/components/schemas/TransType"
              },
              "ResultInfoDesc": {
                "type": "string"
              }
            }
          }
        }
      },
      "TransResultJSON": {
        "type": "object",
        "properties": {
          "ResultCode": {
            "$ref": "#/components/schemas/TransTypeJSON"
          },
          "ResultInfo": {
            "type": "object",
            "properties": {
              "ResultInfoCode": {
                "$ref": "#/components/schemas/TransTypeJSON"
              },
              "ResultInfoDesc": {
                "type": "string"
              }
            }
          }
        }
      },
      "OLifE": {
        "type": "object",
        "properties": {
          "Holding": {
            "$ref": "#/components/schemas/Holding"
          }
        }
      },
      "OLifEJSON": {
        "type": "object",
        "properties": {
          "Holding": {
            "$ref": "#/components/schemas/HoldingJSON"
          }
        }
      },
      "Holding": {
        "type": "object",
        "properties": {
          "Policy": {
            "$ref": "#/components/schemas/Policy"
          }
        }
      },
      "HoldingJSON": {
        "type": "object",
        "properties": {
          "Policy": {
            "$ref": "#/components/schemas/PolicyJSON"
          }
        }
      },
      "Policy": {
        "type": "object",
        "properties": {
          "PolNumber": {
            "type": "string"
          },
          "LineOfBusiness": {
            "$ref": "#/components/schemas/TransType"
          },
          "ProductType": {
            "$ref": "#/components/schemas/TransType"
          },
          "PolicyStatus": {
            "$ref": "#/components/schemas/TransType"
          },
          "ChangeInfo": {
            "$ref": "#/components/schemas/ChangeInfo"
          }
        }
      },
      "PolicyJSON": {
        "type": "object",
        "properties": {
          "PolNumber": {
            "type": "string"
          },
          "LineOfBusiness": {
            "$ref": "#/components/schemas/TransTypeJSON"
          },
          "ProductType": {
            "$ref": "#/components/schemas/TransTypeJSON"
          },
          "PolicyStatus": {
            "$ref": "#/components/schemas/TransTypeJSON"
          },
          "ChangeInfo": {
            "$ref": "#/components/schemas/ChangeInfoJSON"
          }
        }
      },
      "ChangeInfo": {
        "type": "object",
        "properties": {
          "ChangeType": {
            "$ref": "#/components/schemas/TransType"
          },
          "ChangeSubType": {
            "$ref": "#/components/schemas/TransType"
          },
          "ChangeEffDate": {
            "type": "string",
            "format": "date"
          }
        }
      },
      "ChangeInfoJSON": {
        "type": "object",
        "properties": {
          "ChangeType": {
            "$ref": "#/components/schemas/TransTypeJSON"
          },
          "ChangeSubType": {
            "$ref": "#/components/schemas/TransTypeJSON"
          },
          "ChangeEffDate": {
            "type": "string",
            "format": "date"
          }
        }
      },
      "ErrorResponse": {
        "type": "object",
        "properties": {
          "error": {
            "type": "string"
          },
          "message": {
            "type": "string"
          }
        }
      },
      "ErrorResponseJSON": {
        "type": "object",
        "properties": {
          "error": {
            "type": "string"
          },
          "message": {
            "type": "string"
          }
        }
      }
    },
    "securitySchemes": {
      "CognitoAuth": {
        "type": "apiKey",
        "name": "Authorization",
        "in": "header"
      }
    }
  },
  "security": [
    {
      "CognitoAuth": []
    }
  ]
}

        # Update the Swagger definition
        swagger_definition_str = json.dumps(swagger_definition)
        swagger_definition_str = swagger_definition_str.replace('"True"', 'true').replace('"False"', 'false')
        swagger_definition = json.loads(swagger_definition_str)

        
        # Swagger integration
        swagger_resource = api.root.add_resource("swagger")
        swagger_resource.add_method("GET", apigateway.MockIntegration(
            integration_responses=[
                {
                    "statusCode": "200",
                    "responseParameters": {
                        "method.response.header.Content-Type": "'application/json'"
                    },
                    "responseTemplates": {
                        "application/json": json.dumps(swagger_definition)
                    }
                }
            ],
            request_templates={
                "application/json": '{"statusCode": 200}'
            }
        ),
            method_responses=[
                {
                    "statusCode": "200",
                    "responseParameters": {
                        "method.response.header.Content-Type": True
                    }
                }
            ]
        )
        
        # Output the API Gateway URL
        CfnOutput(self, "ApiUrl", value=api.url)
        CfnOutput(self, "UserPoolId", value=user_pool.user_pool_id)
        CfnOutput(self, "UserPoolClientId", value=user_pool_client.user_pool_client_id)
