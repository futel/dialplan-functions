# AWS deployment

Other AWS components which must be set up before deploying, and local setup for them.

# Meta-requirements

AWS credentials should be set up, and the us-west-2 region configured, in ~/.aws/credentials.

AWS should be set up as described in asteriskserver README-aws:
- IAM user "asteriskmanager" and related policy
- SNS topic "asterisk-prod-events" for metric events

AWS should be set up as described in dialplan-assets README-aws:
- S3 bucket "dialplan-assets" for assets

# Setup

## Set up topic and queue

Using the AWS console:
- be in us-west-2 region
- create SNS topic
  - type standard
  - name logs
- (note ARN)
- create SQS queue
  - type standard
  - name logs
- subscribe SQS queue to SNS topic

## Set up environment secrets

Populate app/chalicelib/environment/.env:
- ASSET_HOST dialplan-assets S3 bucket URL
- AWS_DEFAULT_REGION us-west-2
- AWS_LOGS_TOPIC_ARN logs SNS topic ARN
- AWS_METRICS_TOPIC_ARN asterisk-prod-events SNS topic ARN

