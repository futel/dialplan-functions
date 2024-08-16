# Testing and monitoring

# Unit test

These test against the local source.

- source venv/bin/activate
- pytest app-dialplan/test
- pytest app-ops/test

# Verify assets

These test against the local source.

- source venv/bin/activate
- PYTHONPATH=app-dialplan python local/check_assets.py

# Smoke API integration test

These test against the current stage deployment. Note that these will cause side effects like log generation.

- source venv/bin/activate
- pytest app-dialplan/itest
- pytest app-ops/test

# Smoke dialplan API client integration test

These manual tests are to be converted to the itest tests.

These test against the current stage deployment. Note that these will cause side effects like log generation.

These should return XML documents and not cause any error logs.

Outgoing IVR
- curl -d "From=sip:test-one@direct-futel-stage.sip.twilio.com&SipDomain=direct-futel-stage.sip.twilio.com" -X POST https://stage.dialplans.phu73l.net/ivr
- curl -d "From=sip:test-one@direct-futel-stage.sip.twilio.com&SipDomain=direct-futel-stage.sip.twilio.com" -X POST "https://stage.dialplans.phu73l.net/ivr?context=outgoing_safe&lang=en&parent=outgoing_safe&Digits=1"
- XXX parent, lang

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

These test against the current stage deployment. Note that these will cause side effects like log generation.

See testplan directory.

If testplan or extensions have changed since last release branch, update google sheet testplan, keeping dates of nonupdated completed tests.

Set up and run acceptance tests as in testplan/setup.md and testplan/readme.md. Emphasize tests which are important or have not been run for a while.

# View logs

- cd app-dialplan # or app-ops
- chalice logs --stage stage --since 10m --follow

# View components in AWS console

- region us-west-2
- AWS Lambda dashboard
