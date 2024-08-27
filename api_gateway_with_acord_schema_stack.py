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
                                                  user_pool=user_pool)

        # SQS Queues for each Lambda
        sqs_queue_103 = sqs.Queue(self, "Acord103Queue", fifo=True)
        sqs_queue_1125 = sqs.Queue(self, "Acord1125Queue", fifo=True)
        sqs_queue_203 = sqs.Queue(self, "Acord203Queue", fifo=True)

        # Lambda functions for each ACORD code
        lambda_103 = _lambda.Function(self, "Acord103Function",
                                      runtime=_lambda.Runtime.PYTHON_3_8,
                                      handler="handler_acord_103.handler",
                                      code=_lambda.Code.from_asset("lambda/acord_103"))

        lambda_1125 = _lambda.Function(self, "Acord1125Function",
                                       runtime=_lambda.Runtime.PYTHON_3_8,
                                       handler="handler_acord_1125.handler",
                                       code=_lambda.Code.from_asset("lambda/acord_1125"))

        lambda_203 = _lambda.Function(self, "Acord203Function",
                                      runtime=_lambda.Runtime.PYTHON_3_8,
                                      handler="handler_acord_203.handler",
                                      code=_lambda.Code.from_asset("lambda/acord_203"))

        # Attach SQS as Event Source
        lambda_103.add_event_source(event_sources.SqsEventSource(sqs_queue_103))
        lambda_1125.add_event_source(event_sources.SqsEventSource(sqs_queue_1125))
        lambda_203.add_event_source(event_sources.SqsEventSource(sqs_queue_203))

        # API Gateway setup
        api = apigateway.RestApi(self, "MyApi",
                                 deploy_options=apigateway.StageOptions(stage_name="dev"))

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


        # CORS Preflight
        applications_103.add_cors_preflight(
            allow_origins=["*"],
            allow_methods=["POST", "OPTIONS"],
            allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key", "X-Amz-Security-Token"]
        )

        applications_1125.add_cors_preflight(
            allow_origins=["*"],
            allow_methods=["PUT", "OPTIONS"],
            allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key", "X-Amz-Security-Token"]
        )

        applications_203.add_cors_preflight(
            allow_origins=["*"],
            allow_methods=["POST", "OPTIONS"],
            allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key", "X-Amz-Security-Token"]
        )

        # Swagger integration
        swagger_definition = {
        		"openapi": "3.0.1",
        		"info": {
        			"title": "Insurance API",
        			"description": "API for insurance application processing",
        			"version": "1.0.0"
        		},
        		"paths": {
        			"/acord/103": {
        				"post": {
        					"summary": "Submit ACORD 103",
        					"operationId": "submitAcord103",
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
        														"RqUID": {
        															"type": "string"
        														},
        														"TransactionRequestDt": {
        															"type": "string",
        															"format": "date"
        														},
        														"NewBusiness": {
        															"type": "object",
        															"properties": {
        																"PersPkgPolicy": {
        																	"type": "object",
        																	"properties": {
        																		"LOBCd": {
        																			"type": "string"
        																		},
        																		"ContractTerm": {
        																			"type": "object",
        																			"properties": {
        																				"EffectiveDt": {
        																					"type": "string",
        																					"format": "date"
        																				},
        																				"ExpirationDt": {
        																					"type": "string",
        																					"format": "date"
        																				}
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
        																										"GivenName": {
        																											"type": "string"
        																										},
        																										"Surname": {
        																											"type": "string"
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
        													"RqUID": {
        														"type": "string"
        													},
        													"TransactionRequestDt": {
        														"type": "string"
        													},
        													"NewBusiness": {
        														"type": "object",
        														"properties": {
        															"PersPkgPolicy": {
        																"type": "object",
        																"properties": {
        																	"LOBCd": {
        																		"type": "string"
        																	},
        																	"ContractTerm": {
        																		"type": "object",
        																		"properties": {
        																			"EffectiveDt": {
        																				"type": "string"
        																			},
        																			"ExpirationDt": {
        																				"type": "string"
        																			}
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
        																									"GivenName": {
        																										"type": "string"
        																									},
        																									"Surname": {
        																										"type": "string"
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
        											"RqUID": {
        												"type": "string"
        											},
        											"StatusCd": {
        												"type": "string"
        											},
        											"StatusDesc": {
        												"type": "string"
        											}
        										}
        									}
        								},
        								"application/xml": {
        									"schema": {
        										"type": "object",
        										"properties": {
        											"RqUID": {
        												"type": "string"
        											},
        											"StatusCd": {
        												"type": "string"
        											},
        											"StatusDesc": {
        												"type": "string"
        											}
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
        											"error": {
        												"type": "string"
        											},
        											"message": {
        												"type": "string"
        											}
        										}
        									}
        								},
        								"application/xml": {
        									"schema": {
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
        											"error": {
        												"type": "string"
        											},
        											"message": {
        												"type": "string"
        											}
        										}
        									}
        								},
        								"application/xml": {
        									"schema": {
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
        								}
        							}
        						}
        					}
        				}
        			},
        			"/acord/1125": {
        				"put": {
        					"summary": "Submit ACORD 1125",
        					"operationId": "submitAcord1125",
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
        														"RqUID": {
        															"type": "string"
        														},
        														"TransactionRequestDt": {
        															"type": "string",
        															"format": "date"
        														},
        														"NewBusiness": {
        															"type": "object",
        															"properties": {
        																"PersPkgPolicy": {
        																	"type": "object",
        																	"properties": {
        																		"LOBCd": {
        																			"type": "string"
        																		},
        																		"ContractTerm": {
        																			"type": "object",
        																			"properties": {
        																				"EffectiveDt": {
        																					"type": "string",
        																					"format": "date"
        																				},
        																				"ExpirationDt": {
        																					"type": "string",
        																					"format": "date"
        																				}
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
        																										"GivenName": {
        																											"type": "string"
        																										},
        																										"Surname": {
        																											"type": "string"
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
        													"RqUID": {
        														"type": "string"
        													},
        													"TransactionRequestDt": {
        														"type": "string"
        													},
        													"NewBusiness": {
        														"type": "object",
        														"properties": {
        															"PersPkgPolicy": {
        																"type": "object",
        																"properties": {
        																	"LOBCd": {
        																		"type": "string"
        																	},
        																	"ContractTerm": {
        																		"type": "object",
        																		"properties": {
        																			"EffectiveDt": {
        																				"type": "string"
        																			},
        																			"ExpirationDt": {
        																				"type": "string"
        																			}
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
        																									"GivenName": {
        																										"type": "string"
        																									},
        																									"Surname": {
        																										"type": "string"
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
        										"RqUID": {
        											"type": "string"
        										},
        										"StatusCd": {
        											"type": "string"
        										},
        										"StatusDesc": {
        											"type": "string"
        										}
        									}
        								}
        							},
        							"application/xml": {
        								"schema": {
        									"type": "object",
        									"properties": {
        										"RqUID": {
        											"type": "string"
        										},
        										"StatusCd": {
        											"type": "string"
        										},
        										"StatusDesc": {
        											"type": "string"
        										}
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
        										"error": {
        											"type": "string"
        										},
        										"message": {
        											"type": "string"
        										}
        									}
        								}
        							},
        							"application/xml": {
        								"schema": {
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
        										"error": {
        											"type": "string"
        										},
        										"message": {
        											"type": "string"
        										}
        									}
        								}
        							},
        							"application/xml": {
        								"schema": {
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
        							}
        						}
        					}
        				}
        			},
        		  "/acord/203": {
        			"post": {
        				"summary": "Submit ACORD 203",
        				"operationId": "submitAcord203",
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
        													"RqUID": {
        														"type": "string"
        													},
        													"TransactionRequestDt": {
        														"type": "string",
        														"format": "date"
        													},
        													"NewBusiness": {
        														"type": "object",
        														"properties": {
        															"PersPkgPolicy": {
        																"type": "object",
        																"properties": {
        																	"LOBCd": {
        																		"type": "string"
        																	},
        																	"ContractTerm": {
        																		"type": "object",
        																		"properties": {
        																			"EffectiveDt": {
        																				"type": "string",
        																				"format": "date"
        																			},
        																			"ExpirationDt": {
        																				"type": "string",
        																				"format": "date"
        																			}
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
        																									"GivenName": {
        																										"type": "string"
        																									},
        																									"Surname": {
        																										"type": "string"
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
        												"RqUID": {
        													"type": "string"
        												},
        												"TransactionRequestDt": {
        													"type": "string"
        												},
        												"NewBusiness": {
        													"type": "object",
        													"properties": {
        														"PersPkgPolicy": {
        															"type": "object",
        															"properties": {
        																"LOBCd": {
        																	"type": "string"
        																},
        																"ContractTerm": {
        																	"type": "object",
        																	"properties": {
        																		"EffectiveDt": {
        																			"type": "string"
        																		},
        																		"ExpirationDt": {
        																			"type": "string"
        																		}
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
        																								"GivenName": {
        																									"type": "string"
        																								},
        																								"Surname": {
        																									"type": "string"
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
        										"RqUID": {
        											"type": "string"
        										},
        										"StatusCd": {
        											"type": "string"
        										},
        										"StatusDesc": {
        											"type": "string"
        										}
        									}
        								}
        							},
        							"application/xml": {
        								"schema": {
        									"type": "object",
        									"properties": {
        										"RqUID": {
        											"type": "string"
        										},
        										"StatusCd": {
        											"type": "string"
        										},
        										"StatusDesc": {
        											"type": "string"
        										}
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
        										"error": {
        											"type": "string"
        										},
        										"message": {
        											"type": "string"
        										}
        									}
        								}
        							},
        							"application/xml": {
        								"schema": {
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
        										"error": {
        											"type": "string"
        										},
        										"message": {
        											"type": "string"
        										}
        									}
        								}
        							},
        							"application/xml": {
        								"schema": {
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
        	"security": [{
        		"CognitoAuth": []
        	}]
        }
    
        # Add the Swagger definition to the API Gateway
        api.root.add_method("ANY", apigateway.MockIntegration(
            integration_responses=[
                {
                    "statusCode": "200",
                    "responseTemplates": {
                        "application/json": json.dumps(swagger_definition)
                    }
                }
            ],
            request_templates={
                "application/json": '{"statusCode": 200}'
            }
        ))
        
        # Output the API Gateway URL
        CfnOutput(self, "ApiUrl", value=api.url)
        CfnOutput(self, "UserPoolId", value=user_pool.user_pool_id)
        CfnOutput(self, "UserPoolClientId", value=user_pool_client.user_pool_client_id)


