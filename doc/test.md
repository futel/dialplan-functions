# Testing and monitoring

# Unit test

- source venv/bin/activate
- cd app
- pytest test

# Verify assets

- source venv/bin/activate
- PYTHONPATH=app python local/check_assets.py

# Smoke API integration test

Note that these will cause side effects like log generation.

- source venv/bin/activate
- cd app
- pytest itest

# Smoke API client integration test

These manual tests are waitng to be converted to the itest tests.

Note that these will cause side effects like log generation.

These should return XML documents and not cause any error logs.

Outgoing IVR
- curl -d "From=sip:test-one@direct-futel-stage.sip.twilio.com&SipDomain=direct-futel-stage.sip.twilio.com" -X POST https://stage.dialplans.phu73l.net/ivr
- curl -d "From=sip:test-one@direct-futel-stage.sip.twilio.com&SipDomain=direct-futel-stage.sip.twilio.com" -X POST "https://stage.dialplans.phu73l.net/ivr?context=outgoing_safe&lang=en&parent=outgoing_safe&Digits=1"
- XXX parent, lang

Incoming
- curl -d "To=19713512383&From=5035551212&SipDomain=direct-futel-stage.sip.twilio.com" -X POST https://stage.dialplans.phu73l.net/dial_sip_e164

Resources which are redirected to by dial_outgoing and/or dial_sip_e164
- curl -d "From=sip:dome-booth@direct-futel-stage.sip.twilio.com&SipDomain=direct-futel-stage.sip.twilio.com&To=sip:5035551212&DialCallStatus=busy@direct-futel-stage.sip.twilio.com" -X POST https://stage.dialplans.phu73l.net/metric_dialer_status
- curl -d "From=sip:dome-booth@direct-futel-stage.sip.twilio.com&SipDomain=direct-futel-stage.sip.twilio.com&To=sip:5035551212&DialCallStatus=busy@direct-futel-stage.sip.twilio.com" -X POST https://stage.dialplans.phu73l.net/metric_dialer_status
- XXX more status for metric_dialer_status

XXX todo
IVR
- doctl --config config.yaml serverless functions invoke dialers/ivr \
  -p 'To:sip:outgoing_portland@direct-futel-stage.sip.twilio.com' \
  -p 'From:sip:test-one@direct-futel-stage.sip.twilio.com'
- XXX Digits context parent

# Acceptance test

See testplan directory.

If testplan or extensions have changed since last release branch, update google sheet testplan, keeping dates of nonupdated completed tests.

Set up and run acceptance tests as in testplan/setup.md and testplan/readme.md. Emphasize tests which are important or have not been run for a while.

# View logs

    chalice logs --stage stage --since 10m --follow

# View components in AWS console

- region us-west-2
- AWS Lambda dashboard
