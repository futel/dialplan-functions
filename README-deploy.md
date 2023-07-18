# DigitalOcean Functions deployment

# Meta-requirements

AWS should be set up as described in README-aws.

Twilio Programmable Voice should be set up (after this component) as described in README-twilio.

# Requirements

Ubuntu 22 box.

doctl >= 1.93.1

# Deploy and development notes

An instance is a DigitalOcean Function namespace. We use stage, prod, and dev instances. We create stage and dev instances, and we promote stage instances to prod.

The instance type is determined by which Twilio Programmable Voice components are pointed at them, and by an environment variable. We don't replace specific instances after creation and they don't have a descriptive address, Twilio components must know the correct instance URLs. When the relevant Twilio components don't point to them, they can be deleted.

We normally don't want to create prod instances or do anything to them after promotion except delete them when they become obsolete.

---

# Setup

To be done once.

## Set up environment secrets

Fill twilio/.env to match .env.sample as described in README-aws. Set the INSTANCE variable to "stage".

## Set up access token

Create auth token in DigitalOcean web interface with read/write permissions. Note the token string. Initialize doctl with the token string.

    doctl --config config.yaml auth init --access-token <token> --interactive false

---

# Create and deploy a new instance

We create a dev or stage instance by creating and deploying a namespace.

## Create or check out branch

Check out or create relevant source branch <branch>. <branch> may be main or anything for a dev branch, but should be a release branch for stage, and only stage and prod should be on a release branch.

## Create namespace

Label is twilio_<branch>.

    doctl --config config.yaml serverless namespaces create --label <label> --region sfo3

## Deploy dev or stage instance

In .env, set the INSTANCE variable to "stage" or "dev". Deploy the namespace.

    doctl --config config.yaml serverless connect <namespace-label>
    
    doctl --config config.yaml serverless deploy twilio

## Get the URLs

Get the namespace ID and host URL components:

    doctl --config config.yaml serverless namespaces list

Note that the URLs are secrets!

The package and function can be found from the directory tree. The package is "dialers".

- twilio/packages/<package>/<function>
- e.g. dialers/dial_pstn and dialers/dial_outgoing

The URLs are <host>/api/v1/web/<namespace_id>/dialers/<function>. Note that <host> is misnamed because it also includes the protocol declaration.

## Update Twilio Programmable Voice stage components to point to URLs

Update the dev or stage TwiML Application Resources and SIP Domains to point to the instance as in twilio-sip-server README-deploy.

For the SIP domains, the function is "dial_outgoing".

For the Application Resources, the function is "dial_sip_e164".


---

# Promote a stage instance to production

We promote a stage instance to prod by updating an environment variable, pointing the Twilio Programmable Voice prod components to it, and no longer pointing the Twilio stage components to it.

## Test stage instance

See README-test. Run the unit tests. Run the smoke tests. Run some part of the integration tests using the Twilio stage installation.

## Update and deploy stage instance

In twilio/.env, set the INSTANCE variable to "prod".

Deploy the instance.

    doctl --config config.yaml serverless connect <namespace>
    
    doctl --config config.yaml serverless deploy twilio

In .env, set the INSTANCE variable back to "stage".

Continue the rest of promotion immediately, so we don't remain connected to prod. Don't deploy or update this instance again without reverting .env.

## Get the URLs

Get the namespace ID and host URL components:

    doctl --config config.yaml serverless namespaces list

Note that the URLs are secrets!

The package and function can be found from the directory tree:

- twilio/packages/<package>/<function>
- e.g. dialers/dial_pstn and dialers/dial_outgoing

The URLs are <host>/api/v1/web/<namespace_id>/dialers/<function>. Note that <host> is misnamed because it also includes the protocol declaration.

## Update Twilio Programmable Voice prod and stage components to point to URLs

Update the stage TwiML Application Resources and SIP Domains to point to the instance as in twilio-sip-server README-deploy.

For the SIP domains, the function is "dial_outgoing".

For the Application Resources, the function is "dial_sip_e164".

## Smoke test

Receive PSTN call from a prod client. Make an outgoing PSTN call from a prod client. Make outgoing '#' and '0' calls from a prod client.

## Tear down old instances.

We should probably have recorded the previous instance.

    doctl --config config.yaml serverless namespaces list
    
Any release (twilio_r*) branches except the most recent should be deletable.

Delete the prod instance which is no longer pointed to by Twilio.

    doctl --config config.yaml serverless namespace delete <namespace>

---

# Update an existing stage or dev instance

This could be done for prod also, but we don't want to do that.

    doctl --config config.yaml serverless connect <namespace>

If there are items which have been removed, they must first be undeployed.

    doctl --config config.yaml serverless undeploy --all

Deploy the current checked out source.

    doctl --config config.yaml serverless deploy twilio

Twilio components do not need to be updated, since the namespace has not changed.

# Delete a stage or dev instance

    doctl --config config.yaml serverless namespace delete <namespace>

---

# Add configuration for a new SIP client

Update the source at twilio/lib/assets/extensions.py.

---

# Todo

How do we tell which namespace we are connected to? Just connect to it, I guess? Would be good to combine a doctl command assembler with a sanity check e.g. the sources idea of which instance does not match the label of the namespace.

