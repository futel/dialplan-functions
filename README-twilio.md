# Twilio stage, prod setup

Have the DO function's URL as in README-deploy.md: <host>/api/v1/web/<namespace_id>/<package>/<function>.

XXX record DO function version somewhere secret

XXX point Programmable Voice SIP domain to DO Function URL

# Twilio test setup

- Have the DO function's URL as in README-deploy.md: <host>/api/v1/web/<namespace_id>/<package>/<function>.
- Assume we have a test SIP domain and extension/pw creds with Twilio
- Assume we have a test PSTN number with Twilio

## Set up environment secrets

XXX for twilio call api usage below

## Register SIP client to test SIP domain and creds

sip:<extension>@<Twilio SIP domain>

eg sip:test@experimenter-futel-stage.sip.twilio.com

## Call the SIP client using our server's TWIML

Get the URL as in README-deploy.md: <host>/api/v1/web/<namespace_id>/<package>/<function>.

DO_URL: DO function URL from setup
SERVER_TWIML_URL: https: //<DO_URL>/twiml
FROM_PSTN_NUMBER: <Twilio test PSTN number>
TO_SIP_URL: sip:<extension>@<Twilio SIP domain>

`twilio api:core:calls:create --from="<FROM_PSTN_NUMBER>" --to="<TO_SIP_URI>" --url="<SERVER_TWIML_URL>"`
