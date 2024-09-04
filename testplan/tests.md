# Tests

Tests can be better organized, we can test each context separately instead of each for each extension. Extension only needs to test identity of first context, outgoing asterisk, outgoing dialtone ID, outgoing operator ID, all contexts can be added here when reachable.

## Top level tests

outgoing dialtone tests
- notes
  - this is the dialtone provided by the client
- do dialtone tests for input received from the first client send, eg #, 0, pstn numbers

outgoing # destination tests
- notes
  - first client send is #, so this is the first context experienced
  - ATAs send this on pickup, SIP clients send # as the first destination
- first local context after client send (if applicable) is appropriate
- all contexts work (contexts before client is sent to asterisk (if applicable))
  - outgoing top ivr tests
  - outgoing ivr tests
  - dialtone tests
  - outgoing operator tests
- relevant asterisk contexts work after client is sent to asterisk
  - outgoing asterisk tests

outgoing operator tests
- notes
  - this is the operator reached from the dialtone provided by the client
  - enter 0 to navigate to operator from first menu
  - the real operators are really called
    - I hang up as soon as I know the callerid if I don't have to know more
    - I answer quickly for tests that need an operator
    - I enlist someone else or use 2 phones for tests that need several callers or operators
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

outgoing asterisk tests
- notes
  - each extension gets tranferred to asterisk differently, tester needs to know when the dialplan has called asterisk
- verify first context heard
- can call PSTN with correct callerID after navigating to dialtone

## Subtests

dialtone tests
- notes
  - valid numbers are
    - domestic PSTN numbers (10 digit prefixed by 1, +1, 0111, or nothing)
    - international PSTN numbers (12 digit prefixed by 52 or 01152)
    - valid 3 digit numbers (933, 211, 988, ...XXX)
  - there are several ways to get to or send from a dialtone
    - local dialplan dialtone
    - asterisk dialtone (navigating to dialtone after being sent to asterisk)
    - client dialtone (initial send after client-provided dialtone)
  - dial 933 to test emergency calls, do not dial 911!
- domestic PSTN numbers call (10 digit prefixed by 1, +1, 0111, or nothing)
- international PSTN numbers call (12 digit prefixed by 52 or 01152)
- 933 acts appropriately for an emergency call (call destination or notify)
- valid 3 digit numbers (933, 211, 988, ...XXX)
- other valid 3 digit calls call their destinations
- 0 sends to operator from dialtone
- valid versions of 5035551212, 8005551212, 5555551212 send to operator
- caller ID is appropriate
- # from dialtone sends to default context
- call terminates correctly after timeout XXX when?

outgoing ivr tests
- notes
  - any extension can be used
- intro plays once, then menu repeats
- all defined entries can be chosen, including unannounced ones
- undefined entries restart menu
- * toggles Spanish/English and restarts menu
- # goes to parent menu
- 0 restarts menu
- no action terminates correctly after XXX iterations

outgoing top ivr tests
- intro is spanish selection
- if enable_emergency is true
  - 9 is an unannounced entry
  - 9 emits silence and eventually times out
  - 9 and then 1 emits silence and eventually times out
  - 9 and then anything else fails
  - 9 and then 1 and then anything else fails
  - do not enter 9 1 1 from top ivr! Test this only on a modified installation which calls 933 instead of 911!
  - If modified for testing, 9 1 1  announces and then calls emergency
- if enable_emergency is false
  - 9 is an undefined entry
- # restarts menu
- 0 chooses operator
- outgoing ivr tests that don't conflict with top ivr tests pass

## Other tests

To be implemented or at least described.

- incoming call tests
  - Call test number from PSTN. Experience call.
- metrics are generated from twilio
- metrics are generated from asterisk
