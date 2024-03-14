># Dialplan function deployment.

Uses AWS Lambda, API Gateway, and whatever the Chalice framework uses to provide
TwiML via HTTP.

# Meta-requirements

AWS credentials should be set up and the us-west-2 region configured, however that is done.

AWS should be set up as described in README-aws.

An AWS Certificate Manager certificate should be set up as described in README-ssl.

Twilio Programmable Voice SIP components should be set up (after this component) as described in twilio-sip-server README-deploy.

# Requirements

- Ubuntu 23 box
- Python3.11, but this should be Python3.10

# Deploy and development notes

We use dev, stage, and prod instances.

The instance type is determined by the domain and related attributes configured for it. The Twilio Programmable Voice components are pointed at URLs on the domain. An instance can be deleted when the relevant Twilio components don't point to it.

---

# Setup

To be done once.

## Set up environment secrets

Fill app/chalicelib/environment/.env to match app/chalicelib/environment/.env.sample as described in README-aws.

## Create deployment virtualenv

- python3 -m venv venv
- source venv/bin/activate
- cd app
- pip install -r requirements.txt
- python3 -m pip install chalice

---

# Create and deploy a new instance

## Create or check out branch

If deploying stage or prod, check out or create relevant release branch.

## Deploy instance

Create a certificate as described in README-ssl. Update the domain_name and certificate_arn for the instance in app/.chalice/config.json.

Deploy the instance:

- source venv/bin/activate
- cd app
- chalice deploy --stage stage

Note the AliasDomainName.

## Update domain

Have the alias domain name, or find it in e.g. app/.chalice/deployed/dev.json.

Using the DigitalOcean web console, add or update a CNAME record in the dialplans.phu73l.net domain.

- hostname stage.dialplans.phu73l.net (or dev, prod)
- alias: <alias domain name>

Wait for DNS to be updated with eg "nslookup stage.dialplans.phu73l.net".

## Update Twilio Programmable Voice stage components to point to URLs

Update the dev, stage, or prod TwiML Application Resources and SIP Domains to point to the URL in the updated domain as in twilio-sip-server README-deploy.

For the SIP domains, the URL path is "/dial_outgoing".

For the Application Resources, the URL path is "/dial_sip_e164".

# Update an existing instance

- source venv/bin/activate
- cd app
- chalice deploy --stage stage

Twilio SIP components and DigitalOcean networking components do not need to be updated, since the URLs have not changed.

# Delete an instance

eg:

- source venv/bin/activate
- cd app
- chalice delete --stage stage

Remove the stage.dialplans.phu73l.net (or dev or prod) CNAME using the DigitalOcean web console.
