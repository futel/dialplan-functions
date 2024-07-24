# AWS Serverless for Twilio Programmable Voice

Publishes dialplan documents to drive Twilio Programmable Voice, with side effects.

# Overview

We are deploying Lambda functions which will return TwiML to a POST request, with possible side effects. They will be called by Twilio Programmable Voice. Twilio PV Sip Domains will point to the functions for outgoing dialplans for our SIP clients. The Twilio API may also be used to create or update calls by referencing the dialplans.
