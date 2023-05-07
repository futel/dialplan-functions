# Testing and development

# Smoke test stage deployment

    doctl --config config.yaml serverless connect <namespace>

    doctl --config config.yaml serverless functions invoke dialplans/dial_pstn -p number:number -p caller_id:caller_id
    
    doctl --config config.yaml serverless functions invoke dialplans/metric_dialer_status -p 'From:sip:test@direct-futel-nonemergency-dev.sip.twilio.com' -p DialCallStatus:completed -p 'To:sip:5035551212@direct-futel-nonemergency-dev.sip.twilio.com'

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
    
    (PYTHONPATH=$PYTHONPATH:twilio/lib python3 -m unittest discover -s twilio/packages/dialplans/dial_pstn)
    
# Continuously deploy

    doctl serverless watch example-project

# View logs

    doctl --config config.yaml serverless activations logs --follow

    doctl --config config.yaml serverless activations logs --function dialplans/dial_pstn --limit 1
