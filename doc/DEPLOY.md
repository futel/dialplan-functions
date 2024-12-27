# Dialplan function deployment

Uses AWS Lambda, AWS API Gateway, and whatever else the Chalice framework creates to provide TwiML via HTTP.

# Meta-requirements

AWS credentials should be set up, and the us-west-2 region configured, in ~/.aws/credentials.

AWS should be set up as described in aws.md.

An AWS Certificate Manager certificate should be set up as described in ssl.md.

Domains should be created with DigitalOcean:
- dialplans.phu73l.net
- ops.phu73l.net

# Requirements

- debian box (trixie, ubuntu 23)
- Python 3.11-3.12, but this should be Python 3.10

# Deploy and development docs

We use dev, stage, and prod instances. We will document stage here.

The instance type is determined by the domain and related attributes configured for it. The Twilio Programmable Voice components are pointed at URLs on the domain. An instance can be deleted when the relevant Twilio components don't point to it.

---

# Setup

To be done once.

## Set up environment secrets

Populate .env to match .env.sample as described in aws.md:

- app-dialplan/chalicelib/environment/.env
- app-ops/chalicelib/environment/.env

## Create deployment virtualenv

- python3 -m venv venv
- source venv/bin/activate
- cd app-dialplan
- pip install -r requirements.txt
- python3 -m pip install chalice pytest

---

# Create and deploy new instances

## Create or check out branch

If deploying stage or prod, check out or create relevant release branch.

## Test

See test.md. Run the local tests.

## Update certificates in config

If the certificate has been changed in the meta-requrements, update the certificate_arn for the instances to match the certificate:

- app-dialplan/.chalice/config.json
- app-ops/.chalice/config.json

## Deploy instances

Deploy the instances:

- source venv/bin/activate
- (cd app-dialplan && chalice deploy --stage stage)
- (cd app-ops && chalice deploy --stage stage)

Note the AliasDomainNames.

## Update domain

Find the alias_domain_name:
- app-dialplan/.chalice/deployed/stage.json
- app-ops/.chalice/deployed/stage.json

Using the DigitalOcean network web console, add or update CNAME records for domains:
- dialplans.phu73l.net
  - hostname stage.dialplans.phu73l.net
  - alias: <alias domain name>
- ops.phu73l.net
  - hostname stage.ops.phu73l.net
  - alias: <alias domain name>

Wait for DNS to be updated:

- nslookup stage.dialplans.phu73l.net
- nslookup stage.ops.phu73l.net

## Update Twilio Programmable Voice stage components to point to dialplan URLs

Update the stage TwiML Application Resources and SIP Domains to point to the dialplan URL in the updated domain as in twilio-sip-server deploy.md.

For the SIP domains, the URL path is "/dial_outgoing".

For the Application Resources, the URL path is "/dial_sip_e164".

## Test

If stage, see test.md. Run the tests against the deployed instance.

# Update an existing instance

## Test

See test.md. Run the local tests.

## Update certificates in config

If the certificate has been changed in the meta-requrements, update the certificate_arn for the instances to match the certificate:

- app-dialplan/.chalice/config.json
- app-ops/.chalice/config.json

## Deploy instances

- source venv/bin/activate
- (cd app-dialplan && chalice deploy --stage stage)
- (cd app-ops && chalice deploy --stage stage)

Twilio SIP components and DigitalOcean networking components do not need to be updated, since the URLs have not changed.

## Test

If stage, see test.md. Run the tests against the deployed instance.

# Delete instances

- source venv/bin/activate
- (cd app-dialplan && chalice delete --stage stage)
- (cd app-ops && chalice delete --stage stage)

Using the DigitalOcean network web console, remove CNAME records for domains:
- dialplans.phu73l.net
- ops.phu73l.net
