# Accessing recordings

We currently are recording:
- messages left on missed operator calls
- mother foucault resident poet project messages

All recordings are taken after notifying the caller, and the caller isn't prompted to share PII, but should be guarded to protect unwise callers from themselves.

What recordings are there?
- Recordings have an "action" label
  - operator
  - mother-foucaults

How are recordings found?
- Recording existence is indicated by log lines. Each 
- Look through the logs as described in test.md
- Lines starting with "Recording:" in the logs indicate recordings
- log line format is "Recording: ", followed by the action and URL
  - eg for operator recordings look for "Recording: operator"

How are recordings obtained?

Currently 

- When reordings are made, a log message is created: "Recording: <name>: <url>"
- To retrieve WAV audio, GET URLs
  - No creds are needed for GET?
  - If you are me, store these locally in the project directory
- To delete, DELETE URLs XXX with a json suffix?
  - HTTP basic auth creds are needed for these
    - creds are found at the front page of the Twilio web console, "Account ID" "Auth Token"
  - example "curl -X DELETE <URL>.json -u '<id>:<password>'"

