# AWS requirements

Have AWS configuration as described in asteriskserver repo:
- AWS user with appropriate policy 
- SNS topic for asterisk events
  - note that we just have one topic for prod and other deployments, even though it is currenly named 'asterisk-prod-events'.

Populate .env:
- AWS_TOPIC_ARN
- AWS_ACCESS_KEY
- AWS_SECRET_ACCESS_KEY
