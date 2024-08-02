from aws_cdk import core
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_cognito as cognito

class ApiGatewayWithAcordSchemaStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a new Cognito User Pool
        user_pool = cognito.UserPool(self, "UserPool",
                                     self_sign_up_enabled=True,
                                     auto_verify=cognito.AutoVerifiedAttrs(email=True))

        # Create a Cognito User Pool Client
        user_pool_client = cognito.UserPoolClient(self, "UserPoolClient",
                                                  user_pool=user_pool)

        # Create a new Lambda function
        my_lambda = _lambda.Function(self, "MyFunction",
                                     runtime=_lambda.Runtime.PYTHON_3_8,
                                     handler="handler.handler",
                                     code=_lambda.Code.from_asset("lambda"))

        # Create the API Gateway with Swagger
        api = apigateway.LambdaRestApi(self, "MyApi",
                                       handler=my_lambda,
                                       proxy=False,
                                       deploy_options=apigateway.StageOptions(stage_name="dev"))

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
                                                            "RqUID": {"type": "string"},
                                                            "TransactionRequestDt": {"type": "string", "format": "date"},
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
                                                                                    "EffectiveDt": {"type": "string", "format": "date"},
                                                                                    "ExpirationDt": {"type": "string", "format": "date"}
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
        api.root.add_method("ANY", apigateway.MockIntegration(
            integration_responses=[
                {
                    "statusCode": "200",
                    "responseTemplates": {
                        "application/json": swagger_definition
                    }
                }
            ],
            request_templates={
                "application/json": '{"statusCode": 200}'
            }
        ))

        # Output the API Gateway URL
        core.CfnOutput(self, "ApiUrl", value=api.url)

app = core.App()
ApiGatewayWithAcordSchemaStack(app, "ApiGatewayWithAcordSchemaStack")
app.synth()

