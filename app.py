#!/usr/bin/env python3
import aws_cdk as cdk
from api_gateway_with_acord_schema_stack import ApiGatewayWithAcordSchemaStack

app = cdk.App()
ApiGatewayWithAcordSchemaStack(app, "ApiGatewayWithAcordSchemaStack")

app.synth()

