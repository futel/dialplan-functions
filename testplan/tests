outgoing dialtone tests
- notes
  - valid numbers are
    - domestic PSTN numbers (10 digit prefixed by 1, +1, 0111, or nothing)
    - international PSTN numbers (12 digit prefixed by 52 or 01152)
    - valid 3 digit numbers (933, 211, ...XXX)
  - this is the dialtone on the dialplan side
    - first client send is #
    - ATAs send this on pickup, SIP clients send # as the first destination
      - first context is either dialtone or user navigates to dialtone
  - dial 933 to test emergency calls, do not dial 911!
- 0 sends to operator from dialtone
- valid versions of 5035551212, 8005551212, 5555551212 send to operator
- 933 acts appropriately for an emergency call (call destination or notify)
- other valid 3 digit calls call their destinations
- caller ID is appropriate
- # from dialtone sends to default context
- call terminates correctly after timeout XXX when?

client-provided (but still dialplan) outgoing dialtone tests
- notes
  - notice that there are no tests
  - because there are no active endpoints doing this
  - you may stop reading this section now
  - this is the dialtone on the client side  
      - first client send is number
- nop

outgoing # destination tests
- notes
  - first client send is #, so this is the first context experienced
  - ATAs send this on pickup, SIP clients send # as the first destination
- first context after client send is appropriate

outgoing operator tests
- notes
  - enter 0 to navigate to operator from first menu
- calling operator plays intro, then music while operators are called
- calling operator dials all operators
- answering operator call plays operator menu
- accepting operator call connects caller with operator if one or more callers are waiting
- accepting operator call plays message if no callers are waiting
- accepting operator call terminates all ringing operators if no other callers are waiting
- accepting operator call plays message for all operator menus if no other callers are waiting
- accepting operator has no effect on other calls if other callers are waiting
- denying operator call hangs up on operator
- denying operator call does not affect caller
- denying operator call does not affect ringing operators
- denying operator call does not affect other operators hearing menu
- caller gets operator voicemail if no operator accepts before timeout
- caller gets hangup after voicemail ends
- caller gets hangup after operator hangup
- operator gets hangup after caller hangup

outgoing ivr tests
- notes
  - any extension can be used
- intro plays once, then menu repeats
- all defined entries can be chosen, including unannounced ones
- undefined entries restart menu
- top menu starts with language choice intro
- * restarts menu in Spanish
- # at top menu restarts menu
- # at non-top menu goes to parent menu
- 0 at top menu chooses operator
- 0 at non-top menu restarts menu
- no action terminates correctly after XXX iterations

outgoing top ivr tests
- notes
  - if this is not a top ivr for an extension, proceed to the next test
  - any extension can be used
- intro is spanish selection
- 9 emits silence and eventually times out
- 9 and then 1 emits silence and eventually times out
- 9 and then anything else fails
- 9 and then 1 and then anything else fails
- do not enter 9 1 1 from top ivr! Test this only on a modified installation which calls 933 instead of 911!
  - If modified for testing, 9 1 1  announces and then calls emergency

incoming call tests
- Call test number from PSTN. Experience call.

asterisk tests
- notes
  - each extension gets tranfered to asterisk differently, either immediately, or when it hits a context not implemented by the dialplan
- verify first context being heard
- perform outgoing dialtone tests after navigating to dialtone

other tests
- metrics are generated from twilio
- metrics are generated from asterisk
