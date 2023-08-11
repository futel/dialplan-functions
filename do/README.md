# DigitalOcean Functions for Twilio Programmable Voice

# Overview

We are deploying DigitalOcean functions which will return TwiML to a GET or POST request, with possible side effects. They will be called by Twilio Programmable Voice. Twilio PV Sip Domains will point to the functions for outgoing dialplans for our SIP clients. The Twilio API may also be used to create or update calls by referencing the dialplans.

# Notes

We have separate projects in the same namespace if they are versioned together. Put experiments in their own repo, move them here if they are part of twilio-sip-direct.

Do we need access control, or is the URL secret? If we need access control, we need to implement our own. DO's automagic auth reads a x-require-whisk-auth header containing a secret, but Twilio can't set headers. Twilio will do basic auth, but will DO handle that? The Twilio libs do have a validator thing, hashing the URL and params, and it puts them in an x-twilio-signature header for requests coming from Twilio. We could verify that. The downside is that we would need to set a util to do that for smoke testing from the commandline. https://www.twilio.com/docs/usage/security#validating-requests

https://docs.digitalocean.com/products/functions/

    doctl --config config.yaml serverless functions list
    
    doctl --config config.yaml serverless namespaces list

The repo has a project tree initialized with:

    doctl --config config.yaml serverless init --language python twilio


twilio services
statements-en
statements-es
sounds

create service
update do dns name to point to statements-en-prod.assets.phu73l.net etc
