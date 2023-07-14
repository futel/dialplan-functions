# AWS requirements

Have AWS configuration as described in asteriskserver README-aws:
- IAM user and groups
- SNS topic and SQS queue for asterisk events
  - note that we just have one topic/queue for prod and other deployments, even though it is currenly named 'asterisk-prod-events'.

Have AWS configuration as described in dialplan-assets README-aws:
- IAM user and groups
- S3 bucket for assets
  - note that we don't version S3, it must always contain prod content.

Populate .env:
- AWS_TOPIC_ARN
- AWS_ACCESS_KEY
- AWS_SECRET_ACCESS_KEY
- ASSET_HOST
