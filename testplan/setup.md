installation setup
- Have stage installation of dialplan-functions and asteriskserver.

outgoing call setup
- Register client to Twilio SIP Domain as in twilio-sip-server README-client. Registration details will determine whether emergency calls are enabled.

incoming call setup
- Register client to Twilio SIP Domain as in twilio-sip-server README-client.
- Register to a stage domain. If the extension enables emergency calls, register to the emergency stage domain. If the extension disables emergency calls, register to the nonemergency stage domain.
- All extensions should receive the appropriate SIP calls, for example through the stage dialplan-functions dialplan or the stage ops-functions exerciser.
- Extensions receive PSTN calls if twilio-sip-server directs them to a stage instance of dialplan-functions. With the web console, Numbers...active numbers... should be configured XXX in a way documented here.
