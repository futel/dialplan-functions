# How to read the metrics

This document was out of date the moment it was written, so the less simple it is, the less it should be trusted.

There are sources of metric events other than this component, sometimes commemorating similar events, which can be confusing.

# What can the metrics tell us?

Has the first interaction of a call happened?
- This will be a dial_outgoing request that does the initial interaction
- If the extension plays a local context first, this will be ivr or outgoing_operator_caller
- If the extension plays a remote context first, this will be dial_sip_asterisk
- If the extension plays a dialtone first, this will be dial_pstn, reject, or rarely outgoing_operator_caller or ivr
- The extension is configured in extensions.json.
- We can't distinguish the first request of a SIP interaction from another which does the same thing as the first would

Have PSTN calls been made?
- outgoing-dialstatus-(status)-(endpoint)
- interesting statuses are completed, failed, no-answer, busy

Have calls to extensions been received?
- incoming-dialstatus-(status)-(endpoint)
- interesting statuses are completed, failed, no-answer, busy

Has a healthy set of requests happened for an extension?
- For dialtone extensions this will be outgoing-dialstatus-(completed,no-answer-busy)-(endpoint)
- For extensions that hit ivrs that are implemented before dialing the asterisk this is a varied set of contexts (not just the first context)
- For extensions that dial the asterisk first or early, there isn't a good way to tell without looking at metrics produced by asterisk

# Metric events

dialplan_functions does only one thing to directly affect the SIP interaction, for every request from Programmable Voice, it responds with document. Everything else is a side effect that happens before the response is returned.

Every request goes through an app handler, which calls a function in chalicelib.dialers. All metrics are called from dialers. There will be one dialer function per response, but there could be many requests and responses per SIP interaction.

initial interaction
- dial_outgoing
  - outgoing_operator_caller
  - dial_sip_asterisk
  - ivr
    - (and related)
  - dial_pstn
  - reject
  
each ivr stanza/iteration
- (there will be several per SIP interaction)
- ivr
  - (context)
  - (destination function)
  - dial_sip_asterisk

Call status
- (to outgoing PSTN, SIP client, or the asterisk)
- metric_dialer_status
  - (outgoing,incoming)_call
  - (outgoing,incoming)_dialstatus_(status)_(endpoint)

incoming
- dial_sip_e164
  - reject
  
other
- various operator interactions

# Notes

Some metrics tell us bad things, we could make a monitor, just show the last N of them?
- (outgoing,incoming)-dialstatus-failed-(endpoint)

We could show what the variety is for each extension
- like a pie chart for each extension showing metrics emitted

