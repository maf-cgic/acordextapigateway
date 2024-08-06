import json
from aws_cdk import (
    Stack,
    aws_apigateway as apigateway,
    aws_lambda as _lambda,
    aws_cognito as cognito,
    CfnOutput,
)
from constructs import Construct

class ApiGatewayWithAcordSchemaStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a new Cognito User Pool
        user_pool = cognito.UserPool(self, "UserPool",
                                     self_sign_up_enabled=True,
                                     auto_verify=cognito.AutoVerifiedAttrs(email=True))

        # Create a Cognito User Pool Client
        user_pool_client = cognito.UserPoolClient(self, "UserPoolClient",
                                                  user_pool=user_pool)

        # Create a new Lambda function with X-Ray tracing enabled
        my_lambda = _lambda.Function(self, "MyFunction",
                                     runtime=_lambda.Runtime.PYTHON_3_8,
                                     handler="handler.handler",
                                     code=_lambda.Code.from_asset("lambda"),
                                     tracing=_lambda.Tracing.ACTIVE)

        # Create the API Gateway with X-Ray tracing enabled
        api = apigateway.RestApi(self, "MyApi",
                                 deploy_options=apigateway.StageOptions(
                                     stage_name="dev",
                                     tracing_enabled=True,
                                     logging_level=apigateway.MethodLoggingLevel.INFO,
                                     data_trace_enabled=True
                                 ))

        # Define the /applications resource
        applications_resource = api.root.add_resource("applications")

        # Add POST method to /applications resource
        applications_resource.add_method("POST", apigateway.LambdaIntegration(my_lambda), 
                                         authorization_type=apigateway.AuthorizationType.COGNITO,
                                         authorizer=apigateway.CognitoUserPoolsAuthorizer(self, "UserPoolAuthorizer",
                                                                                         cognito_user_pools=[user_pool]),
                                         api_key_required=True,
                                         method_responses=[
                                             apigateway.MethodResponse(
                                                 status_code="201",
                                                 response_parameters={
                                                     "method.response.header.Access-Control-Allow-Headers": True,
                                                     "method.response.header.Access-Control-Allow-Methods": True,
                                                     "method.response.header.Access-Control-Allow-Origin": True
                                                 },
                                                 response_models={
                                                     "application/json": apigateway.Model.EMPTY_MODEL,
                                                     "application/xml": apigateway.Model.EMPTY_MODEL
                                                 }
                                             ),
                                             apigateway.MethodResponse(
                                                 status_code="400",
                                                 response_parameters={
                                                     "method.response.header.Access-Control-Allow-Headers": True,
                                                     "method.response.header.Access-Control-Allow-Methods": True,
                                                     "method.response.header.Access-Control-Allow-Origin": True
                                                 },
                                                 response_models={
                                                     "application/json": apigateway.Model.EMPTY_MODEL,
                                                     "application/xml": apigateway.Model.EMPTY_MODEL
                                                 }
                                             ),
                                             apigateway.MethodResponse(
                                                 status_code="500",
                                                 response_parameters={
                                                     "method.response.header.Access-Control-Allow-Headers": True,
                                                     "method.response.header.Access-Control-Allow-Methods": True,
                                                     "method.response.header.Access-Control-Allow-Origin": True
                                                 },
                                                 response_models={
                                                     "application/json": apigateway.Model.EMPTY_MODEL,
                                                     "application/xml": apigateway.Model.EMPTY_MODEL
                                                 }
                                             )
                                         ])

        # Enable CORS for the applications resource
        applications_resource.add_cors_preflight(
            allow_origins=["*"],
            allow_methods=["POST", "OPTIONS"],
            allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key", "X-Amz-Security-Token"]
        )

        # Define the API structure using Swagger/OpenAPI with ACORD schema
        swagger_definition = {
            "openapi": "3.0.1",
            "info": {
                "title": "Insurance API",
                "description": "API for insurance application processing",
                "version": "1.0.0"
            },
            "paths": {
                "/applications": {
                    "post": {
                        "summary": "Submit a new insurance application",
                        "operationId": "submitApplication",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "ACORD": {
                                                "type": "object",
                                                "properties": {
                                                    "InsuranceSvcRq": {
                                                        "type": "object",
                                                        "properties": {
                                                            "RqUID": {"type": "string", "description": "Request unique identifier"},
                                                            "TransactionRequestDt": {"type": "string", "format": "date", "description": "Date of the transaction request"},
                                                            "NewBusiness": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "PersPkgPolicy": {
                                                                        "type": "object",
                                                                        "properties": {
                                                                            "LOBCd": {"type": "string", "description": "Line of business code"},
                                                                            "ContractTerm": {
                                                                                "type": "object",
                                                                                "properties": {
                                                                                    "EffectiveDt": {"type": "string", "format": "date", "description": "Effective date"},
                                                                                    "ExpirationDt": {"type": "string", "format": "date", "description": "Expiration date"}
                                                                                }
                                                                            },
                                                                            "InsuredOrPrincipal": {
                                                                                "type": "object",
                                                                                "properties": {
                                                                                    "GeneralPartyInfo": {
                                                                                        "type": "object",
                                                                                        "properties": {
                                                                                            "NameInfo": {
                                                                                                "type": "object",
                                                                                                "properties": {
                                                                                                    "PersonName": {
                                                                                                        "type": "object",
                                                                                                        "properties": {
                                                                                                            "GivenName": {"type": "string", "description": "Given name"},
                                                                                                            "Surname": {"type": "string", "description": "Surname"}
                                                                                                        }
                                                                                                    }
                                                                                                }
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                }
                                                                            }
                                                                        }
                                                                    }
                                                                },
                                                                "required": ["PersPkgPolicy"]
                                                            }
                                                        },
                                                        "required": ["RqUID", "TransactionRequestDt", "NewBusiness"]
                                                    }
                                                },
                                                "required": ["InsuranceSvcRq"]
                                            }
                                        },
                                        "required": ["ACORD"]
                                    }
                                },
                                "application/xml": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "ACORD": {
                                                "type": "object",
                                                "properties": {
                                                    "InsuranceSvcRq": {
                                                        "type": "object",
                                                        "properties": {
                                                            "RqUID": {"type": "string"},
                                                            "TransactionRequestDt": {"type": "string"},
                                                            "NewBusiness": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "PersPkgPolicy": {
                                                                        "type": "object",
                                                                        "properties": {
                                                                            "LOBCd": {"type": "string"},
                                                                            "ContractTerm": {
                                                                                "type": "object",
                                                                                "properties": {
                                                                                    "EffectiveDt": {"type": "string"},
                                                                                    "ExpirationDt": {"type": "string"}
                                                                                }
                                                                            },
                                                                            "InsuredOrPrincipal": {
                                                                                "type": "object",
                                                                                "properties": {
                                                                                    "GeneralPartyInfo": {
                                                                                        "type": "object",
                                                                                        "properties": {
                                                                                            "NameInfo": {
                                                                                                "type": "object",
                                                                                                "properties": {
                                                                                                    "PersonName": {
                                                                                                        "type": "object",
                                                                                                        "properties": {
                                                                                                            "GivenName": {"type": "string"},
                                                                                                            "Surname": {"type": "string"}
                                                                                                        }
                                                                                                    }
                                                                                                }
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                }
                                                                            }
                                                                        }
                                                                    }
                                                                },
                                                                "required": ["PersPkgPolicy"]
                                                            }
                                                        },
                                                        "required": ["RqUID", "TransactionRequestDt", "NewBusiness"]
                                                    }
                                                },
                                                "required": ["InsuranceSvcRq"]
                                            }
                                        },
                                        "required": ["ACORD"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "201": {
                                "description": "Application submitted successfully",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "RqUID": {"type": "string"},
                                                "StatusCd": {"type": "string"},
                                                "StatusDesc": {"type": "string"}
                                            }
                                        }
                                    },
                                    "application/xml": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "RqUID": {"type": "string"},
                                                "StatusCd": {"type": "string"},
                                                "StatusDesc": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            },
                            "400": {
                                "description": "Invalid input, missing required fields",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "error": {"type": "string"},
                                                "message": {"type": "string"}
                                            }
                                        }
                                    },
                                    "application/xml": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "error": {"type": "string"},
                                                "message": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            },
                            "500": {
                                "description": "Internal server error",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "error": {"type": "string"},
                                                "message": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
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

        # Add the Swagger definition to the API Gateway
        swagger_resource = api.root.add_resource("swagger")
        swagger_integration = apigateway.MockIntegration(
            integration_responses=[
                {
                    "statusCode": "200",
                    "responseTemplates": {
                        "application/json": json.dumps(swagger_definition),
                        "application/xml": json.dumps(swagger_definition)
                    }
                }
            ],
            request_templates={
                "application/json": '{"statusCode": 200}',
                "application/xml": '{"statusCode": 200}'
            }
        )

        swagger_resource.add_method("GET", swagger_integration,
                                    method_responses=[apigateway.MethodResponse(
                                        status_code="200",
                                        response_parameters={
                                            "method.response.header.Access-Control-Allow-Headers": True,
                                            "method.response.header.Access-Control-Allow-Methods": True,
                                            "method.response.header.Access-Control-Allow-Origin": True
                                        }
                                    )])

        # Enable CORS for the Swagger resource
        swagger_resource.add_cors_preflight(
            allow_origins=["*"],
            allow_methods=["GET", "OPTIONS"],
            allow_headers=["Content-Type"]
        )

        # Output the API Gateway URL
        CfnOutput(self, "ApiUrl", value=api.url)
        CfnOutput(self, "UserPoolId", value=user_pool.user_pool_id)
        CfnOutput(self, "UserPoolClientId", value=user_pool_client.user_pool_client_id)

