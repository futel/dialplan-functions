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

XXX record the namespaces being used by Twilio stage and prod somewhere here and in Twilio source. Eventually this would selfdocument in the ansible build?

    doctl --config config.yaml serverless connect <namespace>
    
    doctl --config config.yaml serverless deploy twilio

# Get the URL

Get the host, package, and function URL components:

    doctl --config config.yaml serverless namespaces list

The URL is <host>/api/v1/web/<namespace_id>/<package>/<function>.

Update Twilio stage or dev emergency and nonemergency SIP domains to point to URL.

# Promote the stage deployment to production

XXX record the namespaces being used by Twilio stage and prod somewhere here and in Twilio source. Eventually this would selfdocument in the ansible build?

Update Twilio prod emergency and nonemergency SIP domains to point to the URL of the namespace to promote.

Delete unused deployments.

# Delete deployment

    doctl --config config.yaml serverless connect <namespace>

    doctl --config config.yaml serverless undeploy --all
