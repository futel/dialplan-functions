# DigitalOcean Functions deployment

# Meta-requirements

Twilio Programmable Voice should be set up as for twilio-sip-server.

AWS should be set up as described in README-aws.

# Requirements

Ubuntu 22 box.

doctl >= 1.93.1

# Deploy and development notes

We create stage namespaces. We turn them into prod by pointing the Twilio Programmable Voice components at them.

XXX What makes a namespace stage or prod? Twilio stage or prod pointing to it, and an attibute, either from environment or from the Twilio calls?

We don't replace namespaces and they don't have a 'stage' or 'prod' address, Twilio Programmable Voice must know the correct namespace to call. When the relevant Twilio components don't point to them, they can be deleted.

# Setup

To be done once.

## Set up environment secrets

Fill .env to match .env.sample as described in README-aws.

## Set up access token

Create auth token in DigitalOcean web interface with read/write permissions. Note the token string.

    doctl --config config.yaml auth init --access-token <access-token> --interactive false

# XXX

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

## Promote the stage deployment to production

Promote the Twilio Programmable Voice service to prod.

XXX We need a way for a component to tell whether it is prod, stage, dev. Do this in the deployment step so it isn't in src. A newly created stage namespace should have stage, a newly created dev namespace should have dev, a promoted stage namespace should have prod. Or maybe a namespace don't know it is stage or prod, Twilio tells it?

Delete unused deployments.

# Update an existing stage or dev deployment

This could be done for prod also, but we don't want to do that.

    doctl --config config.yaml serverless connect <namespace>
    
    doctl --config config.yaml serverless deploy twilio

# Delete deployment

    doctl --config config.yaml serverless connect <namespace>

    doctl --config config.yaml serverless undeploy --all
