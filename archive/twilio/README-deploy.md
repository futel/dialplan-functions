# Deploying components for the Twilio SIP server.

This document covers initial deployment, deployment of the client components of the server, updating of the client components of the serer, promotion, and redeployment.

# Requirements

- Twilio CLI package 5.3.2 eg twilio-5.3.2.deb
- serverless toolkit plugin for twilio
    twilio plugins:install @twilio-labs/plugin-serverless
- Twilio profile or other way to use creds

# Deploy and development notes

We will set up a service with a stage environment, and other components for the stage and prod servers. For components other than the service, the stage and prod components are identical except for which other components they reference.

The initial deploy process is to create the stage components and at least one SIP credential, then promote the stage service to prod. We expect to add more SIP credentials as clients are added.

When we develop, we will redeploy the stage service with the serverless toolkit. When ready, the stage service is again promoted to prod. We shouldn't have to redeploy or change any other components, but nothing gets promoted except the service. If we change anything other than the service, we will presumably be changing the stage components, then changing the prod components to match stage when we promote the stage service to prod.

The stage and prod deployments communicate with the corresponding deployments on the Asterisk side. We develop on stage, it would be more correct to have a separate dev deployment.

For most of the Twilio API calls, a 400 response because the resource already exists is OK.

---

# Set up stage and prod server components

This setup process should only need to be done once. After this is done, the expected process is:

- Update th service by creating a release branch, deploying to stage, then promoting to prod
- Add a new SIP client by creating a phone number and credential, and updating the credential list

Those processes are outlined in later sections.

If changes are made to other components, some of the processes here will be repeated. But note that the elements of this setup process do not have releases, we don't track changes.

## Set up environment secrets

Fill .env to match .env.sample as described in README-aws.

## Deploy the service to the initial stage and prod environments

We need to deploy to either environment if they don't exist yet. If we are starting out, we need to create stage and prod. Normally, both environments will always exist from then on, but if for some reason we have destroyed either, we will need to recreate them. It is not an error to deploy to an existing enviroment, this is how we update stage during development, but we normally don't want to deploy to prod, we only want to promote stage to prod.

All serverless toolkit commands are executed in the dialer directory. Api commands can be executed in any directory.

Deploy to stage.

    twilio serverless:deploy --environment=stage

Deploy to prod. Don't do this if prod is in use except in emergencies!

    twilio serverless:deploy --environment=prod

Note that if we are creating a service (instead of updating an existing one), SIP domains and phone numbers pointing to the service must be updated.

## Get the outgoing SIP function URLs

List the environments to find the environment URL.

    twilio serverless:list environments

The outgoing SIP function URLs are https://<environment URL>/sip-outgoing, e.g. https://dialer-1780-stage.twil.io/sip-outgoing.

## Create new stage and prod emergency and nonemergency SIP domains

    twilio api:core:sip:domains:create --domain-name direct-futel-stage.sip.twilio.com --friendly-name direct-futel-stage --sip-registration --emergency-calling-enabled --voice-method GET --voice-url '<STAGE FUNCTION URL>'

    twilio api:core:sip:domains:create --domain-name direct-futel-nonemergency-stage.sip.twilio.com --friendly-name direct-futel-nonemergency-stage --sip-registration --voice-method GET --voice-url '<STAGE FUNCTION URL>'

    twilio api:core:sip:domains:create --domain-name direct-futel-prod.sip.twilio.com --friendly-name direct-futel-prod --sip-registration --emergency-calling-enabled --voice-method GET --voice-url '<PROD FUNCTION URL>'

    twilio api:core:sip:domains:create --domain-name direct-futel-nonemergency-prod.sip.twilio.com --friendly-name direct-futel-nonemergency-prod --sip-registration --voice-method GET --voice-url '<PROD FUNCTION URL>'

Use the SIP function URLs found in the previous step.

Note that if the SIP domain already exists, this will fail instead of updating the domain. The web GUI must be used to make changes, if that is necessary.

## List the SIP domains to get the created SID

If we created a new SIP domain in the last step, the SID was listed there. Otherwise:

    twilio api:core:sip:domains:list

## Create the credential list

    twilio api:core:sip:credential-lists:create --friendly-name sip-direct

## List the credential lists to get the created SID (unless it was visible in the last step)

    twilio api:core:sip:credential-lists:list

## Create an auth registrations credential list mapping for stage and prod emergency and nonemergency SIP domains

Use the SIDs of the domains and credential list found in the previous steps.

    twilio api:core:sip:domains:auth:registrations:credential-list-mappings:create --domain-sid <STAGE EMERGENCY DOMAIN SID> --credential-list-sid <CREDENTIAL LIST SID>

    twilio api:core:sip:domains:auth:registrations:credential-list-mappings:create --domain-sid <STAGE NONEMERGENCY DOMAIN SID> --credential-list-sid <CREDENTIAL LIST SID>

    twilio api:core:sip:domains:auth:registrations:credential-list-mappings:create --domain-sid <PROD EMERGENCY DOMAIN SID> --credential-list-sid <CREDENTIAL LIST SID>

    twilio api:core:sip:domains:auth:registrations:credential-list-mappings:create --domain-sid <PROD NONEMERGENCY DOMAIN SID> --credential-list-sid <CREDENTIAL LIST SID>

## Set voice authentication credentials for stage and prod SIP domains

Visit the GUI for the stage and prod sip domains and add the same "sip-direct" credential list to "voice authentication", then save.

There doesn't seem to be any other way to do this.

---

# Create a new stage deployment, or update an existing one

Create or check out release branch.

Redeploy the stage service. Other components won't change (but see notes above).

    twilio serverless:deploy --environment=stage

# Promote the stage deployment to the production environment

    twilio serverless:promote --source-environment=stage --environment=prod

---

# Delete a service

To delete an environment, eg stage or dev:

    twilio api:serverless:v1:services:environments:remove --service-sid <SID> --sid <SID>

Don't delete prod!

---

# Add configuration for a new SIP client

To add a new SIP client, we create a Twilo phone number, create a credential in the Twilio credential list, and update the extensions asset source in the Twilio Service. If there is an unused phone number, credential, and asset item, they can be re-used instead of creating a new one.

## Create a phone number

Use the web GUI; the APIs may allow us to do this, but maybe not.

Create new phone number
- friendly name: (client)
- emergency calling: (client address)
- voice configuration:
    - accept incoming: voice calls
    - configure with: Webhook, TwiML Bin, Function, Studio Flow, Proxy Service
    - a call comes in: Function
    - service: dialer
    - environment: prod-environment (or stage-environment)
    - function path: /sip-incoming
- messaging configuation:
    - a message comes in: webhook
    - URL: blank

## Create credential

List the credential lists to get the SID of "sip-direct".

    twilio api:core:sip:credential-lists:list

Create a new credential in the credential list. Use the SID found in the previous step.

    twilio api:core:sip:credential-lists:credentials:create --credential-list-sid <SID> --username '<USERNAME>' --password '<PASSWORD>'

## Update extensions asset

Add entry in assets/extensions.private.json. Deploy/promote.

# Delete configuration for a SIP client

Delete the phone number, delete the credential from the credential list, delete the entry in extensions.private.json.

## Delete phone number

Use the web GUI.

## Update extensions asset

Delete entry in assets/extensions.private.json.

## Delete credential

Use the web gui.

# Notes

todo:
  - use the cli to remove a credential
  - use the cli to CRUD a phone number
  - use the cli to update a SIP Domain
  - needs a maintenance/verification process
    - sip-direct credential list is associated with the expected sip domains
    - extensions.private.json credentials are associated with the sip-direct credential list
