
# AWS Lambda deployment

## Meta-requriements

The AWS S3 service in the dialplan-assets project must be set up as described in README-aws.

The AWS SQS service in the asteriskserver project must be set up as described in README-aws.

## Requirements

Ubuntu 22 box.

- awscli
- python3.11
- python3.11-venv
- python3-pytest
- zip

--

# Setup

To be done once.

## Set up environment

Populate src/.env to match .env.sample as described in README-aws. Set the INSTANCE variable to "stage".

## Configure AWS CLI

Populate ~/.aws/credentials or whatever.

## Create Python environment

This must be done whenever the requirements are changed.

- python3.11 -m venv env
- source env/bin/activate
- pip install -r requirements.txt
- deactivate

## Create role in AWS console

This should be figured out with the CLI.

trusted entity type: AWS service
use case: Lambda
permissions policies:
- s3-get-put-delete
- s3-list-bucket-content
role name: dialplan-functions

Note ARN.

# Create and deploy a new stage instance

## Create or check out branch

XXX we need to know which revision stage is using, tag a branch eg r4_stage?

## Package source

- cd env/lib/python3.11/site-packages
- zip -r ../../../../build/package.zip .
- cd ../../../../src/
- zip -r ../build/package.zip assets *.py
- cd ..

## Deploy instance

XXX these need a description option

If this is the first deployment, have the ARN of the role, and create the function:

    aws lambda create-function \
    --region us-west-2 \
    --function-name reject \
    --runtime python3.11 \
    --handler lambda_function.lambda_handler \
    --role <ARN> \
    --zip-file "fileb://build/package.zip"

If the function has been deployed, update the function:

    aws lambda update-function-code \
    --region us-west-2 \
    --function-name reject \
    --zip-file "fileb://build/package.zip"

Update the environment variables:

    aws lambda update-function-configuration \
    --region us-west-2 \
    --function-name reject \
    --environment "`deploy/environment_string.py`"

XXX Need permission to log, see the monitor tab in the web console for the function.

## Create alias

Publish the version.

    aws lambda publish-version \
    --region us-west-2 \
    --function-name reject

Note the version attribute.

If the stage alias has not been created, create the alias.

    aws lambda create-alias \
    --function-name reject \
    --name stage \
    --region us-west-2 \
    --function-version <VERSION> \
    --description "stage dialplan"

If the stage alias been created, update the alias.

    aws lambda update-alias \
    --function-name reject \
    --region us-west-2 \
    --name stage \
    --function-version <VERSION> \
    --description "stage dialplan"

## Create stage URL

If the stage URL has not been created, create it with the web console for the stage alias. Visit aliases:stage:configuration. Select "Create function URL". Select "Auth type: NONE" and save. Note the URL.

This can be done with the CLI, maybe not with version 1.

After creation, the Twilio Programmable Voice stage components must be updated as described in twilio-sip-server README-deploy. XXX

---

# Create a prod instance

Check out the branch used by the stage instance.

## Test stage instance

Visit the URL.

Unit test.

XXX this puts test packages in the shipped site-packages
    solution use a test env?

- source env/bin/activate
- pip install pytest
- pip install python-dotenv
- pytest
- deactivate

## Deploy instance

Update the function:

    aws lambda update-function-code \
    --region us-west-2 \
    --function-name reject \
    --zip-file "fileb://build/package.zip"

In src/.env, set the INSTANCE variable to "prod".

Update the environment variables:

    aws lambda update-function-configuration \
    --region us-west-2 \
    --function-name reject \
    --environment "`deploy/environment_string.py`"

## Create alias

If the prod alias has not been created, create the alias.

    aws lambda create-alias \
    --function-name reject \
    --name prod \
    --region us-west-2 \
    --function-version <VERSION> \
    --description "prod dialplan"

If the prod alias been created, update the alias.

    aws lambda update-alias \
    --function-name reject \
    --region us-west-2 \
    --name prod \
    --function-version <VERSION> \
    --description "prod dialplan"

In src/.env, set the INSTANCE variable back to "stage".

## Create prod URL

If the prod URL has not been created, create it with the web console for the prod alias. Visit aliases:prod:configuration. Select "Create function URL". Select "Auth type: NONE" and save. Note the URL.

This can be done with the CLI, maybe not with version 1.

After creation, the Twilio Programmable Voice prod components must be updated as described in twilio-sip-server README-deploy. XXX

---

# More testing and monitoring

XXX manual SIP client

## View logs

XXX
