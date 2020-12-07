import os
import subprocess
from aws_cdk import (
    core,
    aws_lambda,
    aws_apigateway
)

integration_responses = [
    {
        'statusCode': '200',
        'responseParameters': {
            'method.response.header.Access-Control-Allow-Origin': "'*'",
        }
    }
]

method_responses = [{
    'statusCode': '200',
    'responseParameters': {
        'method.response.header.Access-Control-Allow-Origin': True,
    }
}
]


class QuoteApiStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.dependencies_layer = self.create_dependencies_layer(
            self.stack_name)

        # api = aws_apigateway.SpecRestApi(self, "books-api",
        #     api_definition=aws_apigateway.ApiDefinition.from_asset("./stacks/quote_api.json"),
        #     endpoint_types=[aws_apigateway.EndpointType.PRIVATE]
        # )
        base_api = aws_apigateway.RestApi(self, 'quote_api',
                                          rest_api_name='quote_api')

        self.add_resource(base_api, 'quote', 'GET',
                          'app.handler_get_quote', 'get_quote')
        self.add_resource(base_api, 'languages', 'GET',
                          'app.handler_get_languages', 'get_languages')

        admin_api_key = aws_apigateway.ApiKey(
            self,
            id="quote-admin-api-key",
            api_key_name="quote-admin",
            description="quote-admin",
            enabled=True
        )

        usage_plan = aws_apigateway.UsagePlan(self,
                                              name="quote-admin",
                                              id="quote-admin-usage-plan",
                                              api_key=admin_api_key,
                                              api_stages=[
                                                  {"api": base_api, "stage": base_api.deployment_stage}],
                                              throttle={"burst_limit": 500, "rate_limit": 1000}, quota={"limit": 10000000, "period": aws_apigateway.Period("MONTH")}
                                              )

    def add_resource(self, base, resource, method, handler, name):
        lambda_function = aws_lambda.Function(self, name,
                                              handler=handler,
                                              runtime=aws_lambda.Runtime.PYTHON_3_8,
                                              code=aws_lambda.Code.asset(
                                                  'handlers/quote'),
                                              layers=[
                                                  self.dependencies_layer
                                              ]
                                              )
        api_entity = base.root.add_resource(resource)
        entity_lambda_integration = aws_apigateway.LambdaIntegration(
            lambda_function,
            proxy=True,
            integration_responses=integration_responses
        )
        api_entity.add_method(
            method,
            entity_lambda_integration,
            api_key_required=True,
            method_responses=method_responses,
        )

        self.add_cors_options(api_entity)

    def add_cors_options(self, apigw_resource):
        apigw_resource.add_method('OPTIONS', aws_apigateway.MockIntegration(
            integration_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                    'method.response.header.Access-Control-Allow-Origin': "'*'",
                    'method.response.header.Access-Control-Allow-Methods': "'GET,OPTIONS'"
                }
            }
            ],
            passthrough_behavior=aws_apigateway.PassthroughBehavior.WHEN_NO_MATCH,
            request_templates={"application/json": "{\"statusCode\":200}"}
        ),
            method_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Headers': True,
                    'method.response.header.Access-Control-Allow-Methods': True,
                    'method.response.header.Access-Control-Allow-Origin': True,
                }
            }
        ],
        )

    def create_dependencies_layer(self, project_name) -> aws_lambda.LayerVersion:
        requirements_file = f'./handlers/requirements.txt'
        output_dir = f'./.build/packages'

        if not os.environ.get('SKIP_PIP'):
            subprocess.check_call(
                f'pip install -r {requirements_file} -t {output_dir}/python'.split()
            )

        layer_id = f'{project_name}-dependencies'
        layer_code = aws_lambda.Code.from_asset(output_dir)

        return aws_lambda.LayerVersion(self, layer_id, code=layer_code)
