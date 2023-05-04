# DigitalOcean Functions for Twilio Programmable Voice

# Overview

We are deploying DigitalOcean functions which will return TwiML to a GET or POST request, with possible side effects. They will be called by Twilio Programmable Voice. Twilio PV Sip Domains will point to the functions for outgoing dialplans for our SIP clients. The Twilio API may also be used to create or update calls by referencing the dialplans.

# Notes

We have separate projects in the same namespace if they are versioned together. Put experiments in their own repo, move them here if they are part of twilio-sip-direct.

Do we need access control, or is the URL secret? If we do, we include an X-Function-Auth header containing a secret, or:

- https://www.twilio.com/docs/usage/security#http-authentication
- https://www.twilio.com/docs/usage/tutorials/how-to-secure-your-flask-app-by-validating-incoming-twilio-requests

https://docs.digitalocean.com/products/functions/

    doctl --config config.yaml serverless functions list
    
    doctl --config config.yaml serverless namespaces list

The repo has a project tree initialized with:

    doctl --config config.yaml serverless init --language python twilio

    doctl serverless watch example-project

To view logs:

- doctl --config config.yaml serverless activations logs --follow
- doctl --config config.yaml serverless activations logs --function dialplans/dialer --limit 1

    doctl serverless activations get ...
