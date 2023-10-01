# AWS Serverless for Twilio Programmable Voice

Publishes dialplan documents to drive Twilio Programmable Voice, with side effects.

# Overview

We are deploying Lambda functions which will return TwiML to a POST request, with possible side effects. They will be called by Twilio Programmable Voice. Twilio PV Sip Domains will point to the functions for outgoing dialplans for our SIP clients. The Twilio API may also be used to create or update calls by referencing the dialplans.

# Notes

https://aws.github.io/chalice/main.html

is twilio downloading all sounds before starting audio?
are the s3 not being cached?

is the twilio edge correct for the api gateway edge?
global low latency edge?
twilio interconnect?

twilio edge location/region:
Ashburn (us1)
We recommend hosting your media in AWS S3 in us-east-1, eu-west-1, or ap-southeast-2 depending on which Twilio Region you are using.
METRICS (SIP Edge)
Codec
pcmu

is there sound format conversion?
codec? opus/g.729

logs/calls/call details says start time and end time
each sound file takes 2-300ms
downloaded one at a time
combine them?
move to twilio assets?
ensure cache at s3?

