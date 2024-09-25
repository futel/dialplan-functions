# Tests

Outgoing extension tests for each extension
- callerid on outgoing dialtone is correct
- emergency service on outgoing dialtone is correct
  - dial 933
- top level extension is correct
  - dial # from linphone, off hook from ata
- callerid on menu dialtone is correct
- emergency service on menu dialtone is correct
  - dial 933
- first asterisk context reached is correct
  - check voicemail and get mailbox prompt

Incoming call tests for each extension configured to take stage incoming call
- extension rings

General context tests, once for all contexts
- # repeats context if top level
- # plays previous context if not top level
- * switches language

Specific context tests
- outgoing operator
  - XXX
- dialtone
  - domestic PSTN numbers (10 digit prefixed by 1, +1, 0111, or nothing)
  - international PSTN numbers (12 digit prefixed by 52 or 01152)
  - valid 3 digit numbers (933, 211, 988, ...XXX)
  - 0 sends to operator
  - valid versions of 5035551212, 8005551212, 5555551212 send to operator
  - # sends to default context
- top level emergency call when enabled by extension
  - 9 from top level plays silence then timeout
  - 1 from next level plays silence then timeout
  - 1 from next level announces, calls emergency (don't let the call happen!)
- top level emergency call when disabled by extension
  - 9 from top level restarts menu

Context tests for each context
- each listed entry goes to appropriate context
- each unlisted entry goes to appropriate context
- each unavailable entry repeats context
