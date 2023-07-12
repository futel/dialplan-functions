# Testing and development

# Smoke test dev or stage deployment

    doctl --config config.yaml serverless connect <namespace>

Outgoing PSTN
- doctl --config config.yaml serverless functions invoke dialers/dial_outgoing -p 'To:sip:5035551212@direct-futel-nonemergency-stage.sip.twilio.com' -p 'From:sip:test@direct-futel-nonemergency-stage.sip.twilio.com'

Outgoing extension
- doctl --config config.yaml serverless functions invoke dialers/dial_outgoing -p 'To:sip:%23@direct-futel-nonemergency-stage.sip.twilio.com' -p 'From:sip:test@direct-futel-nonemergency-stage.sip.twilio.com'
- doctl --config config.yaml serverless functions invoke dialers/dial_outgoing -p 'To:sip:0@direct-futel-nonemergency-stage.sip.twilio.com' -p 'From:sip:test@direct-futel-nonemergency-stage.sip.twilio.com'

Incoming
- doctl --config config.yaml serverless functions invoke dialers/dial_sip_e164 -p 'To:+19713512383' -p 'From:5035551212'

Resources which are redirected to by dial_outgoing and/or dial_sip_e164
- doctl --config config.yaml serverless functions invoke dialers/dial_pstn -p 'to_uri:sip:5035551212@direct-futel-nonemergency-stage.sip.twilio.com' -p 'from_uri:sip:test@direct-futel-nonemergency-stage.sip.twilio.com'
- doctl --config config.yaml serverless functions invoke dialers/dial_sip -p 'to_uri:sip:0@direct-futel-nonemergency-stage.sip.twilio.com' -p 'from_uri:sip:test@direct-futel-nonemergency-stage.sip.twilio.com'
- doctl --config config.yaml serverless functions invoke dialers/metric_dialer_status -p 'From:sip:test@direct-futel-nonemergency-dev.sip.twilio.com' -p DialCallStatus:completed -p 'To:sip:5035551212@direct-futel-nonemergency-dev.sip.twilio.com'
- doctl --config config.yaml serverless functions invoke dialers/metric_dialer_status -p 'From:sip:test@direct-futel-nonemergency-dev.sip.twilio.com' -p DialCallStatus:busy -p 'To:sip:5035551212@direct-futel-nonemergency-dev.sip.twilio.com'
- XXX metric_dialer_status should be invoked as for outgoing and incoming, and for all DialCallStatus

Use the URL found in README-deploy.md.

    wget --post-data 'To=sip:5035551212@direct-futel-nonemergency-stage.sip.twilio.com&From=sip:test@direct-futel-nonemergency-stage.sip.twilio.com' <host>/api/v1/web/<namespace_id>/dialers/dial_outgoing

# Unit test

## Setup

To be done once.

    virtualenv env
    
    source env/bin/activate
    
    cd twilio

    # XXX We install these and hope it is a superset.
    #     We could instead install all function requirements.
    #     Better would be to create an env for each function and test each.
    pip install -r packages/dialers/dial_pstn/requirements.txt
    pip install -r packages/dialers/metric_dialer_status/requirements.txt

## Test

    source env/bin/activate
    
    cd twilio

    for i in packages/dialers/* lib; do (PYTHONPATH=$PYTHONPATH:lib:test_lib python3 -m unittest discover -s $i); done
    
# Integration test

If testplan has changed since last release branch, update google sheet testplan, keeping dates of nonupdated completed tests.

Test stage against google sheet testplan. Emphasize tests which are important or have not been run for a while.

# Continuously deploy

    doctl serverless watch example-project

# View logs

    doctl --config config.yaml serverless activations logs --follow

    doctl --config config.yaml serverless activations logs --function dialers/dial_pstn --limit 1
