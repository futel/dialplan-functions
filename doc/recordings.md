# Accessing recordings

# We currently are recording

- messages left on missed operator calls
- mother foucault resident poet project messages

All recordings are taken after notifying the caller, and the caller isn't prompted to share PII, but should be guarded to protect unwise callers from themselves.

# What recordings are there

- Recordings have an "action" label
  - operator
  - mother-foucaults

# How are recordings found

- When recordings are made, a log message is created: "Recording: <name>: <url>"
- Look through the logs as described in test.md
- Lines starting with "Recording:" in the logs indicate recordings
- log line format is "Recording: ", followed by the action and URL
  - eg for operator recordings look for "Recording: operator"

# How are recordings obtained

Get the logs for the desired period eg the most recent month.

```
aws logs tail /aws/lambda/dialplan-prod --since 4w --format short >logs.out
```

Fetch the recordings indicated by the logs.

```
# -d to delete after get
# types are mother-foucaults and operator 
source venv/bin/activate && python3 local/get_recordings.py logs.out mother-foucaults
```

# Notes

- If you are me, store these locally in the projects directory of the futel repo
- To retrieve, GET URLs
  - example "wget <URL>.wav"
  - note that .wav suffix is added, this is not necessary but sets the format and names the downloaded file
- To delete, DELETE URLs
  - HTTP basic auth creds are needed for these
    - creds are found at the front page of the Twilio web console, "Account ID" "Auth Token"
  - example "curl -X DELETE <URL>.json -u '<id>:<password>'"
  - note that .json suffix is added
