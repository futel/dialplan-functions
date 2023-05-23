# Handler for a Dial status callback.
# Publishes metrics to SNS, returns TwiML to continue call, or not.

from twilio.twiml.voice_response import VoiceResponse

import sns_client
import util

extensions = util.get_extensions()

def event_to_events(event):
    """Return sequence of sns_client events from DO event."""
    extension_uri = event['From']
    to_number = event['To']
    dial_call_status = event['DialCallStatus']
    dial_event = None
    dial_status_event_base = None

    extension = util.sip_to_extension(extension_uri)
    if extension:
        # Outgoing from Twilio SIP Domain,
        # extension_uri is SIP URI to extension.
        endpoint = extension
        dial_user_event = "outgoing_call"
        dial_status_user_event_base = "outgoing_dialstatus_"
    else:
        # Incoming to Twilio phone number,
        # extensionUri is E.164 of caller.
        endpoint = util.e164_to_extension(to_number, extensions)
        dial_user_event = "incoming_call"
        dial_status_user_event_base = "incoming_dialstatus_"

    dial_status_user_event = dial_status_user_event_base + dial_call_status + '_' + endpoint;
    dial_event = {
        'channel': endpoint,
        'user_event': dial_user_event};
    dial_status_event = {
        'channel': endpoint,
        'user_event': dial_status_user_event};
    return (dial_event, dial_status_event)


def metric_dialer_status(event, context, env):
    """
    Metric the dial status callback attributes from event,
    and return TwiML.
    """
    util.log('metric_dialer_status')
    for e in event_to_events(event):
        sns_client.publish(e['channel'], e['user_event'], env)

    response = VoiceResponse()
    if event['DialCallStatus'] == 'failed':
        response.say("We're sorry, your call cannot be completed as dialed. Please try again later.")
    else:
        # If the first interation on handset pickup is a local menu, we want to return to that.
        # If the first interation is a SIP call to a remote menu, we want to SIP it again if that
        # call hung up due to a user hitting the back key from the top, otherwise we want to end.
        # If the first interation is a dialtone, we want to end.
        response.hangup()

    return util.twiml_response(response)
