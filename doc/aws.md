# AWS deployment

Other AWS components which must be set up before deploying, and local setup for them.

# Meta-requirements

First thing, install the aws cli. You should be able to run the command "aws" from the terminal.

You need an AWS access key and matching secret key for things to work. An admin will need to give these to you,
unless you have access to the AWS console. If you do, you can navigate to:
* <Your login name> (Upper  righthand corner)
* Security credentials
* Users (left)
* (Choose the desired user)
* (Choose the "security credentials" tab)
* Choose "Create access key". If it is greyed out, you may already have 2 created and will need to delete one.
* Choose "Local code" for the use case, then Confirm, then Next, then Create Access Key.
* On this screen, you can get your access key and secret key. Once you leave this screen, the secret key cannot be obtained again! <img width="1318" height="412" alt="image" src="https://github.com/user-attachments/assets/f99ab2c2-a539-4c3b-94ae-f4d2bec1068b" />

* Now run `aws configure` and enter the key information

AWS credentials should now be set up, and the `us-west-2` region configured, in `~/.aws/credentials`. The file should look something
like this:

```
[default]
aws_access_key_id = <redacted>
aws_secret_access_key = <redacted>
```

AWS should be set up as described in asteriskserver [README-aws.md](https://github.com/futel/asteriskserver/blob/main/README-aws.md):
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

Populate .env to match .env.sample:
- app-dialplan/chalicelib/environment/.env
- app-ops/chalicelib/environment/.env

- ASSET_HOST dialplan-assets S3 bucket URL
- AWS_DEFAULT_REGION us-west-2
- AWS_LOGS_TOPIC_ARN logs SNS topic ARN
- AWS_METRICS_TOPIC_ARN asterisk-prod-events SNS topic ARN

