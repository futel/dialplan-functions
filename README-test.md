# Testing and development

# Smoke test stage deployment

XXX test dial_outgoing with #/0 also

    doctl --config config.yaml serverless connect <namespace>

    doctl --config config.yaml serverless functions invoke dialplans/dial_outgoing -p 'To:sip:5035551212@direct-futel-nonemergency-stage.sip.twilio.com' -p 'From:sip:test@direct-futel-nonemergency-stage.sip.twilio.com'
    
    doctl --config config.yaml serverless functions invoke dialplans/dial_outgoing -p 'To:sip:0@direct-futel-nonemergency-stage.sip.twilio.com' -p 'From:sip:test@direct-futel-nonemergency-stage.sip.twilio.com'

    doctl --config config.yaml serverless functions invoke dialplans/dial_pstn -p 'to_uri:sip:5035551212@direct-futel-nonemergency-stage.sip.twilio.com' -p 'from_uri:sip:test@direct-futel-nonemergency-stage.sip.twilio.com'
    
    doctl --config config.yaml serverless functions invoke dialplans/dial_sip -p 'to_uri:sip:0@direct-futel-nonemergency-stage.sip.twilio.com' -p 'from_uri:sip:test@direct-futel-nonemergency-stage.sip.twilio.com'

    doctl --config config.yaml serverless functions invoke dialplans/dial_sip_e164 -p 'To:+19713512383' -p 'From:5035551212'

    doctl --config config.yaml serverless functions invoke dialplans/metric_dialer_status -p 'From:sip:test@direct-futel-nonemergency-dev.sip.twilio.com' -p DialCallStatus:completed -p 'To:sip:5035551212@direct-futel-nonemergency-dev.sip.twilio.com'

Use the URL found in README-deploy.md.

    curl <host>/api/v1/web/<namespace_id>/<package>/<function>

# Unit test

## Setup

To be done once.

    virtualenv env
    
    source env/bin/activate
    
    cd twilio

    # XXX We install these and hope it is a superset.
    #     We could instead install all function requirements.
    #     Better would be to create an env for each function and test each.
    pip install -r packages/dialplans/dial_pstn/requirements.txt
    pip install -r packages/dialplans/metric_dialer_status/requirements.txt

## Test

    source env/bin/activate
    
    cd twilio

    (PYTHONPATH=$PYTHONPATH:lib python3 -m unittest discover -s packages/dialplans/dial_outgoing)
    (PYTHONPATH=$PYTHONPATH:lib python3 -m unittest discover -s packages/dialplans/dial_pstn)
    (PYTHONPATH=$PYTHONPATH:lib python3 -m unittest discover -s packages/dialplans/dial_sip)
    (PYTHONPATH=$PYTHONPATH:lib python3 -m unittest discover -s packages/dialplans/dial_sip_e164)
    (PYTHONPATH=$PYTHONPATH:lib python3 -m unittest discover -s packages/dialplans/metric_dialer_status)
    (PYTHONPATH=$PYTHONPATH:lib python3 -m unittest discover -s packages/dialplans/reject)
    
# Integration test

Run tests in testplan. Emphasize tests which are important or have not been run for a while.

# Continuously deploy

    doctl serverless watch example-project

# View logs

    doctl --config config.yaml serverless activations logs --follow

    doctl --config config.yaml serverless activations logs --function dialplans/dial_pstn --limit 1
