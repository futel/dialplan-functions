# Testing and development

# Smoke test stage deployment

    doctl --config config.yaml serverless connect <namespace>

    doctl --config config.yaml serverless functions invoke dialplans/outgoing
    
    doctl --config config.yaml serverless functions invoke dialplans/dialer

Use the URL found in README-deploy.md.

    curl <host>/api/v1/web/<namespace_id>/<package>/<function>

# Unit test

## Setup

To be done once.

    virtualenv env
    
    source env/bin/activate
    
    pip install -r requirements.txt
        
## Test

    source env/bin/activate
    
    python3 -m unittest discover -s twilio/packages/dialplans/outgoing
    
    python3 -m unittest discover -s twilio/packages/dialplans/dialer

# Continuously deploy

    doctl serverless watch example-project

# View logs

    doctl --config config.yaml serverless activations logs --follow

    doctl --config config.yaml serverless activations logs --function dialplans/dialer --limit 1
