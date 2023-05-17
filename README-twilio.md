# Twilio setup

Twilio components to be set up and deployed.

# Twilio component setup

The twilio-sip-server project is assumed to be set up, with prod and stage installations deployed, and any optional installations such as dev.

# Update Twilio stage

The Twilio installation must point to the relevant DigitalOcean Function URLs.

Have the URLs as in README-deploy: <host>/api/v1/web/<namespace_id>/<package>/<function>.

In twilio-sip-server, add the host and namespace to the Twilio .env DO_HOST and DO_NAMESPACE values. Deploy to stage.

XXX in twilio-sip-server, update every phone number to point to URL.

# Promote Twilio stage to prod

Promote stage to prod as in twilio-sip-server README-deploy.
