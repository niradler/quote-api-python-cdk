#!/usr/bin/env python3

from aws_cdk import core

from infra.infra_stack import InfraStack


app = core.App()
InfraStack(app, "infra", env={'region': 'us-west-2'})

app.synth()
