# Other requirements

Deploy asteriskserver and dialplan-assets projects.

Have AWS configuration as described in asteriskserver README-aws:
- IAM user and groups
- SNS topic and SQS queue for asterisk events
  - note that we just have one topic/queue for prod and other deployments, even though it is currenly named 'asterisk-prod-events'.

# Setup

Populate .env:
- AWS_TOPIC_ARN
- ASSET_HOST

Populate extensions.py.

# Bonus VOIP.ms setup

XXX

When a phone number is added, verify the CallerID with voip.ms.
