#!/usr/bin/env python3

from aws_cdk import core

from infra.quote_api_stack import QuoteApiStack


app = core.App()
QuoteApiStack(app, "quote-stack", env={'region': 'us-east-1'})

app.synth()
