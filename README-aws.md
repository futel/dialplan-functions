# AWS requirements

Other AWS components which must be set up before deploying, and local setup for them.

# AWS Setup

Have AWS configuration as described in asteriskserver README-aws:
- IAM user and groups
- SNS topic and SQS queue for asterisk events
  - note that we just have one topic/queue for prod and other deployments, even though it is currenly named 'asterisk-prod-events'.

Have AWS configuration as described in dialplan-assets README-aws:
- IAM user and groups
- S3 bucket for assets
  - note that we don't version S3, it must always contain prod content.

# Setup

Populate .env:
- AWS_TOPIC_ARN
- ASSET_HOST
