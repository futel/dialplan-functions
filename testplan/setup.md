installation setup
- Have stage installation of dialplan-functions and asteriskserver.

outgoing call setup
- Register client to Twilio SIP Domain as in twilio-sip-server README-client. Registration details will determine whether emergency calls are enabled.

incoming call setup
- Register client to Twilio SIP Domain as in twilio-sip-server README-client. Register an extension which receives phone calls from a number which is configured to send calls to stage.
