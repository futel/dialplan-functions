# Testing and development

# Unit test

- source venv/bin/activate
- cd app
- pytest test

# Verify assets

- source venv/bin/activate
- PYTHONPATH=app python local/check_assets.py

# Smoke integration test

Using a SIP client, receive PSTN call, make outgoing PSTN, make outgoing '#' and '0' calls.

# Integration test

If testplan has changed since last release branch, update google sheet testplan, keeping dates of nonupdated completed tests.

Using a SIP client, test stage against google sheet testplan. Emphasize tests which are important or have not been run for a while.

# Smoke test dev or stage deployment

Outgoing PSTN
- curl -d "To=sip:5035551212@direct-futel-nonemergency-stage.sip.twilio.com&From=sip:test@direct-futel-nonemergency-stage.sip.twilio.com&SipDomain=direct-futel-nonemergency-dev.sip.twilio.com" -X POST https://dev.dialplans.phu73l.net/dial_outgoing

Outgoing extension
- curl -d "To=sip:%23@direct-futel-nonemergency-stage.sip.twilio.com&From=sip:test@direct-futel-nonemergency-stage.sip.twilio.com&SipDomain=direct-futel-nonemergency-dev.sip.twilio.com" -X POST https://dev.dialplans.phu73l.net/dial_outgoing
- curl -d "To=sip:0@direct-futel-nonemergency-stage.sip.twilio.com&From=sip:test@direct-futel-nonemergency-stage.sip.twilio.com&SipDomain=direct-futel-nonemergency-dev.sip.twilio.com" -X POST https://dev.dialplans.phu73l.net/dial_outgoing
- XXX also remote outgoing on #

Outgoing IVR
- curl -d "From=sip:test@direct-futel-nonemergency-stage.sip.twilio.com&SipDomain=direct-futel-nonemergency-dev.sip.twilio.com" -X POST https://dev.dialplans.phu73l.net/ivr
- curl -d "From=sip:test@direct-futel-nonemergency-stage.sip.twilio.com&SipDomain=direct-futel-nonemergency-dev.sip.twilio.com" -X POST "https://dev.dialplans.phu73l.net/ivr?context=outgoing_safe&lang=en&parent=outgoing_safe&Digits=1"

- parent lang

Incoming
- curl -d "To=19713512383&From=5035551212&SipDomain=direct-futel-nonemergency-dev.sip.twilio.com" -X POST https://dev.dialplans.phu73l.net/dial_sip_e164

Resources which are redirected to by dial_outgoing and/or dial_sip_e164
- curl -d "From=sip:dome-booth@direct-futel-nonemergency-dev.sip.twilio.com&SipDomain=direct-futel-nonemergency-dev.sip.twilio.com&To=sip:5035551212&DialCallStatus=busy@direct-futel-nonemergency-stage.sip.twilio.com" -X POST https://dev.dialplans.phu73l.net/metric_dialer_status
- curl -d "From=sip:dome-booth@direct-futel-nonemergency-dev.sip.twilio.com&SipDomain=direct-futel-nonemergency-dev.sip.twilio.com&To=sip:5035551212&DialCallStatus=busy@direct-futel-nonemergency-stage.sip.twilio.com" -X POST https://dev.dialplans.phu73l.net/metric_dialer_status
- XXX more status for metric_dialer_status

XXX todo
IVR
- doctl --config config.yaml serverless functions invoke dialers/ivr \
  -p 'To:sip:outgoing_portland@direct-futel-nonemergency-stage.sip.twilio.com' \
  -p 'From:sip:test@direct-futel-nonemergency-stage.sip.twilio.com'
- XXX Digits context parent

# View logs

    chalice logs --stage stage --since 10m --follow

# View components in AWS console

- region us-west-2
- AWS Lambda dashboard
