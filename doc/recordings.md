# Accessing recordings

Currently 

- When reordings are made, a log message is created: "Recording: <name>: <url>"
- For operator unavailable messages, name is "Operator"
- To retrive WAV audio, GET URLs
  - no creds are needed for GET?
- To delete, DELETE URLs XXX with a json suffix?
  - HTTP basic auth creds are needed for these
    - creds are found at the front page of the Twilio web console, "Account ID" "Auth Token"
  - example "curl -X DELETE <URL>.json -u '<id>:<password>'"

