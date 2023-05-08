# Testing and development

# Smoke test stage deployment

    doctl --config config.yaml serverless connect <namespace>

    doctl --config config.yaml serverless functions invoke dialplans/dial_pstn -p 'to_uri:sip:5035551212@direct-futel-nonemergency-stage.sip.twilio.com' -p 'from_uri:sip:test@direct-futel-nonemergency-stage.sip.twilio.com'
    
    doctl --config config.yaml serverless functions invoke dialplans/dial_sip -p to_extension:0 -p 'from_uri:sip:test@direct-futel-nonemergency-stage.sip.twilio.com'
    
    doctl --config config.yaml serverless functions invoke dialplans/metric_dialer_status -p 'From:sip:test@direct-futel-nonemergency-dev.sip.twilio.com' -p DialCallStatus:completed -p 'To:sip:5035551212@direct-futel-nonemergency-dev.sip.twilio.com'

Use the URL found in README-deploy.md.

    curl <host>/api/v1/web/<namespace_id>/<package>/<function>

# Unit test

## Setup

To be done once.

    virtualenv env
    
    source env/bin/activate
    
    cd twilio

    # XXX We are assuming that dial_pstn requirements are a superset of others.
    #     We could instead install all function requirements.
    #     Better would be to create an env for each function and test each.
    pip install -r packages/dialplans/dial_pstn/requirements.txt
        
## Test

    source env/bin/activate
    
    cd twilio
    
    (PYTHONPATH=$PYTHONPATH:lib python3 -m unittest discover -s packages/dialplans/dial_pstn)
    
# Continuously deploy

    doctl serverless watch example-project

# View logs

    doctl --config config.yaml serverless activations logs --follow

    doctl --config config.yaml serverless activations logs --function dialplans/dial_pstn --limit 1
