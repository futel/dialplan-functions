# voip.ms deployment

# Setup

Should need to be done once.

## Create Sub Account
- protocol sip
- authentication type user/password
- username 185060_test
- password
- device type ata device
- dialing mode use main account setting
- callerid number Use one of my DIDs
  - hot leet
  - XXX
- NAT yes
- Encrypted SIP Traffic yes
- Max Expiry 3600
  - XXX

## Also

hot-leet should be set up for asteriskserver and should not change.

- Manage DID Numbers
  - 503.468.1337
    - routing 185060_prod-foo or 185060_prod-bar
      - this is a subaccount
      - should register to the current asterisk server prod
- Manage Sub Accounts
  - 185060_prod-foo
    - set up for asterisk
  - 185060_prod-bar
    - set up for asterisk


## Notes

Asteriskserver stages will register against the appropriate subaccount.
Incoming calls to 503 468 1337 will SIP call the prod asteriskserver.

### Linphone


sip address: sip:185060_test@voip.ms
<sip:sip.seattle.voip.ms;transport=udp>
transport: udp

# XXX may need to be enabled first

sip server address: <sip:sip.seattle.voip.ms;transport=tls>
transport: tls

create did
point of presence seattle1.voip.ms


create sip uri
sip uri: sip:clinton@direct-futel-stage.sip.twilio.com
callerid override: hot leet xxx should be system?
callerid e164: disabled
