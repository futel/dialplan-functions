# DigitalOcean Functions deployment

# Meta-requirements

Twilio Programmable Voice should be set up as for twilio-sip-server.

AWS should be set up as described in README-aws.

# Requirements

Ubuntu 22 box.

doctl >= 1.93.1

# Deploy and development notes

A namespace is an instance. We use stage, prod, probably dev and others.

We create stage namespaces. We turn them into prod by pointing the Twilio Programmable Voice components at them. We normally don't want to create prod namespaces or do anything to them after promotion except delete them when they become obsolete.

We don't replace specific namespace instances after creation and they don't have a 'stage' or 'prod' address, Twilio Programmable Voice must know the correct namespace to call. When the relevant Twilio components don't point to them, they can be deleted.

# Setup

To be done once.

## Set up environment secrets

Fill .env to match .env.sample as described in README-aws.

## Set up access token

Create auth token in DigitalOcean web interface with read/write permissions. Note the token string.

    doctl --config config.yaml auth init --access-token <access-token> --interactive false

# Create new namespace

## Create branch

Check out or create relevant source branch <branch>. Namespace is twilio_<branch>.

    doctl --config config.yaml serverless namespaces create --label <namespace> --region sfo3

## Create a new stage or dev deployment

    doctl --config config.yaml serverless connect <namespace>
    
    doctl --config config.yaml serverless deploy twilio

## Get the URL components

Get the namespace ID and host URL components:

    doctl --config config.yaml serverless namespaces list

The package and function components are as in the directory tree:

- twilio/packages/<package>/<function>
- e.g. dialplans/dial_pstn and dialplans/outgoing

The URL is <host>/api/v1/web/<namespace_id>/<package>/<function>, but we only need that for manual testing.

## Update Twilio Programmable Voice stage components to point to URL

Update DO_HOST and DO_NAMESPACE in the .env file for the Twilio Programmable Voice service, and deploy to stage.

# Promote the stage instance to production

Promote the Twilio Programmable Voice service to prod.

XXX A component tells whether it is prod, stage, dev in util.get_instance(). Update that. Do this in the deployment step so it isn't in src.
XXX or have twilio tell us during a call

## Update Twilio Programamble Voice stage environment

Update DO_HOST and DO_NAMESPACE in the environment file for the "dialer" Twilio Service, and deploy it to stage.

## Test stage instance

See README-test. Run the unit tests and some part of the integration and smoke tests.

## Promote Twilio Programamble Voice

Promote the "dialer" Twilio Service to prod.

## Test prod

Run some part of the integration tests.

## Tear down old prod

Delete unused instances.

# Update an existing stage or dev instance

This could be done for prod also, but we don't want to do that.

    doctl --config config.yaml serverless connect <namespace>
    
    doctl --config config.yaml serverless deploy twilio

# Delete a stage or dev instance

    doctl --config config.yaml serverless connect <namespace>

    doctl --config config.yaml serverless undeploy --all
