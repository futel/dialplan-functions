# AWS Serverless for Twilio Programmable Voice

# Overview

We are deploying Lambda functions which will return TwiML to a GET or POST request, with possible side effects. They will be called by Twilio Programmable Voice. Twilio PV Sip Domains will point to the functions for outgoing dialplans for our SIP clients. The Twilio API may also be used to create or update calls by referencing the dialplans.
