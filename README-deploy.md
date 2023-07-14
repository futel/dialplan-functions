# AWS deployment

Using AWS Lambda, API Gateway, and whatever the Chalice framework uses.

# Meta-requirements

AWS should be set up as described in README-aws.

An AWS Certificate Manager certificate should be set up as described in README-ssl.

Twilio Programmable Voice should be set up (after this component) as described in twilio-sip-server README-deploy.

# Requirements

Ubuntu 22 box.

# Deploy and development notes

We use stage, prod, and dev instances.

The instance type is determined by which Twilio Programmable Voice components are pointed at them, and by an environment variable. When the relevant Twilio components don't point to it, an instance can be deleted.

---

# Setup

To be done once.

## Set up environment secrets

XXX

Fill app/.env to match .env.sample as described in README-aws. Set the INSTANCE variable to "stage".

## Create deployment virtualenv

- python3 -m venv venv
- source venv/bin/activate
- python3 -m pip install chalice

---

# Create and deploy a new dev or stage instance

## Create or check out branch

If deploying stage or prod, check out or create relevant source branch.

## Update environment secrets

In app/.env, set the INSTANCE variable to "dev", "stage", or "prod".

## Deploy instance

No domains we will be adding later (eg dev.dialplans.phu73l.net) can point to an out of date AWS/cloudfront domain. If we are creating the instance, the domain must not exist, if we are updating, it must not point to an earlier name.

Deploy the instance, eg:

- source venv/bin/activate
- cd app
- chalice deploy --stage dev

Note the AliasDomainName.

## Update domain

Using the DigitalOcean web console, add or update a CNAME record.

- hostname dev.dialplans.phu73l.net (or stage, prod)
- alias: <AliasDomainName>

Wait for DNS to be updated with eg "nslookup dev.dialplans.phu73l.net".

## Update Twilio Programmable Voice stage components to point to URLs

Update the dev, stage, or prod TwiML Application Resources and SIP Domains to point to the domain as in twilio-sip-server README-deploy.

For the SIP domains, the function is "dial_outgoing".

For the Application Resources, the function is "dial_sip_e164".

# Update an existing stage or dev instance

This could be done for prod also, but we don't want to do that.

    chalice deploy --stage dev

Twilio components do not need to be updated, since the URLs have not changed.

# Delete a stage or dev instance

    chalice delete --stage dev

Remove the dev.dialplans.phu73l.net CNAME using the DigitalOcean web console.


---

# Test stage instance

XXX

See README-test. Run the unit tests. Run the smoke tests. Run some part of the integration tests using the Twilio stage installation.

# Smoke test

Receive PSTN call from a prod client. Make an outgoing PSTN call from a prod client. Make outgoing '#' and '0' calls from a prod client.

---

# Create and deploy a new prod instance

XXX

## Test stage instance

## XXX

---

# Add configuration for a new SIP client

XXX

Update the source at twilio/lib/assets/extensions.py.
