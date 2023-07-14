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

---

# Setup

To be done once.

## Set up environment

Populate src/.env to match .env.sample as described in README-aws. Set the INSTANCE variable to "stage".

## Configure AWS CLI

Populate ~/.aws/credentials or whatever.

## Create Python environment

- python3.11 -m venv env
- source env/bin/activate
- pip install -r requirements.txt
- deactivate

## Create roles

Create a role for the functions to execute lambdas and access S3.

- aws iam create-role --role-name dialplan --assume-role-policy-document '{"Version": "2012-10-17","Statement": [{ "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}'

Note ARN.

Attach policies to the role.

- aws iam attach-role-policy --role-name dialplan --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
- aws iam attach-role-policy --role-name dialplan --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

Create a role for the API to log.

- aws iam create-role --role-name api-log --assume-role-policy-document '{"Version": "2012-10-17","Statement": [{ "Effect": "Allow", "Principal": {"Service": "apigateway.amazonaws.com"}, "Action": "sts:AssumeRole"}]}'

Note ARN.

Attach policies to the role.

- aws iam attach-role-policy --role-name api-log --policy-arn arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs

---

# Create and deploy a new stage instance

## Create or check out branch

Create a release branch rN and another branch rN_stage.

## Package source

- rm build/package.zip
- cd env/lib/python3.11/site-packages
- zip -r ../../../../build/package.zip .
- cd ../../../../src/
- zip -r ../build/package.zip assets *.py
- cd ..

## Deploy stage instance

If this is the first deployment, have the ARN of the execution role, and create the function:

    aws lambda create-function \
    --region us-west-2 \
    --function-name reject \
    --description "dialplan reject" \
    --runtime python3.11 \
    --handler lambda_function.lambda_handler \
    --role <ARN> \
    --zip-file "fileb://build/package.zip"

Note the ARN of the function.

Add a permission for any API gateway service to invoke the function.

    aws lambda add-permission \
    --region us-west-2 \
    --function-name reject \
    --statement-id apigateway \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com
        

If the function has been deployed, update the function:

    aws lambda update-function-code \
    --region us-west-2 \
    --function-name reject \
    --description "dialplan reject" \
    --zip-file "fileb://build/package.zip"

Update the environment variables:

    aws lambda update-function-configuration \
    --region us-west-2 \
    --function-name reject \
    --environment "`deploy/environment_string.py`"

## Create stage alias

Publish the version.

    aws lambda publish-version \
    --region us-west-2 \
    --function-name reject

Note the Version attribute.

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

XXX do we want this with the API gateway? Is it used?

If the stage URL has not been created, create it with the web console for the stage alias. Visit aliases:stage:configuration. Select "Create function URL". Select "Auth type: NONE" and save. Note the URL.

This can be done with the CLI, maybe not with version 1.

After creation, the Twilio Programmable Voice stage components must be updated as described in twilio-sip-server README-deploy. XXX

## Create stage API gateway

To be done once. XXX creation and update differernces

https://docs.aws.amazon.com/cli/latest/reference/apigateway/put-integration.html
https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html

Have the ARN of the stage function alias.

Create the API.

    aws apigateway create-rest-api \
     --region us-west-2 \
    --name 'dialer'

Note the API id attribute.

In the web console, visit Amazon API Gateway : Settings. Set "CloudWatch log role ARN" to the ARN of the api-log role created earlier.

Get the root resource.

    aws apigateway get-resources \
    --region us-west-2 \
    --rest-api-id <API-ID>

Note the root resource id attribute.

Create a child resource for any path.

    aws apigateway create-resource \
    --region us-west-2 \
    --rest-api-id <API-ID> \
    --parent-id <ROOT-ID> \
    --path-part {proxy+}

Note the child resource id attribute.

Create a method for any HTTP verb on the child resource.

    aws apigateway put-method \
    --region us-west-2 \
    --rest-api-id <API-ID> \
    --resource-id <CHILD-ID> \
    --http-method ANY \
    --authorization-type "NONE"

Create the integration for the method and stage function alias.

    aws apigateway put-integration \
    --region us-west-2 \
    --rest-api-id <API-ID> \
    --resource-id <CHILD-ID> \
    --http-method ANY \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri arn:aws:apigateway:us-west-2:lambda:path/2015-03-31/functions/<ARN>:stage/invocations

Create the deployment resource to make the API REST accessible from a stage URL.

    aws apigateway create-deployment \
    --region us-west-2 \
    --rest-api-id <API-ID> \
    --stage-name stage \
    --stage-description "deployment for stage dialplan"

After creation, the Twilio Programmable Voice stage components must be updated as described in twilio-sip-server README-deploy. XXX

XXX how to do this for dev prod etc? put-integration create-deployment each?

XXX If the alias changes, we need a new deployment. When an alias or API is not used, we need to delete the old deployment. If we need to update any part of the API, we need a new deployment.

---

# Create and deploy a prod instance

## Check out branch

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

## Deploy prod instance

Update the function:

    aws lambda update-function-code \
    --region us-west-2 \
    --function-name reject \
    --description "dialplan reject" \
    --zip-file "fileb://build/package.zip"

In src/.env, set the INSTANCE variable to "prod".

Update the environment variables:

    aws lambda update-function-configuration \
    --region us-west-2 \
    --function-name reject \
    --environment "`deploy/environment_string.py`"

## Create prod alias

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

XXX do we want this with the API gateway? Is it used?

If the prod URL has not been created, create it with the web console for the prod alias. Visit aliases:prod:configuration. Select "Create function URL". Select "Auth type: NONE" and save. Note the URL.

This can be done with the CLI, maybe not with version 1.

After creation, the Twilio Programmable Voice prod components must be updated as described in twilio-sip-server README-deploy. XXX

## Create prod API gateway

To be done once. XXX creation and update differences

XXX need to create a new resource, that's our only handle

Create the deployment resource to make the API REST accessible from a prod URL.

    aws apigateway create-deployment \
    --region us-west-2 \
    --rest-api-id <API-ID> \
    --stage-name stage \
    --stage-description "deployment for stage dialplan"

The URL is "https://<API-ID>.execute-api.us-west-2.amazonaws.com/prod".

After creation, the Twilio Programmable Voice stage components must be updated as described in twilio-sip-server README-deploy. XXX

XXX how to do this for dev prod etc? put-integration create-deployment each?

XXX If the alias changes, we need a new deployment. When an alias or API is not used, we need to delete the old deployment. If we need to update any part of the API, we need a new deployment.


---

# More testing and monitoring

XXX manual SIP client

## View logs

XXX
