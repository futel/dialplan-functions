# DigitalOcean Functions deployment

# Requirements

Ubuntu 22 box.

doctl >= 1.93.1

# Set up access token

To be done once.

Create auth token in DigitalOcean web interface with read/write permissions. Note the token string.

    doctl --config config.yaml auth init --access-token <access-token> --interactive false

# Create new namespace

Check out or create relevant source branch <branch>. Namespace is twilio_<branch>.

    doctl --config config.yaml serverless namespaces create --label <namespace> --region sfo3

# Create a new stage or dev deployment, or update an existing one

    doctl --config config.yaml serverless connect <namespace>
    
    doctl --config config.yaml serverless deploy twilio

# Get the URL

Get the namespace ID and host URL components:

    doctl --config config.yaml serverless namespaces list

The package and function components are as in the directory tree:

- e.g. twilio/packages/<package>/<function>
- e.g. dialplans/dialer and dialplans/outgoing

The URL is <host>/api/v1/web/<namespace_id>/<package>/<function>.

XXX record the namespaces being used by Twilio stage and prod somewhere here and in Twilio source. Eventually this would selfdocument in the build, either Ansible or scripts?

Update Twilio Programmable Voice components to point to URL.

XXX This is TBD. Could be stage or dev emergency and nonemergency SIP domains, could be environment or variables used by the PV Services.

# Promote the stage deployment to production

XXX record the namespaces being used by Twilio stage and prod somewhere here and in Twilio source. Eventually this would selfdocument in the build, either Ansible or scripts?

XXX Add a 'prod' component to config and remove it from current prod. Do this in the deployment step so it isn't in src.

Update Twilio Programmable Voice components to point to URL.

XXX This is TBD. Could be stage or dev emergency and nonemergency SIP domains, could be environment or variables used by the PV Services.

Delete unused deployments.

# Delete deployment

    doctl --config config.yaml serverless connect <namespace>

    doctl --config config.yaml serverless undeploy --all
