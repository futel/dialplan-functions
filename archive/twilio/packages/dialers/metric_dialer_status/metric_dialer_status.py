"""
Handler for a Dial status callback.
Publishes metrics to SNS, returns TwiML to continue call, or not.
"""

from twilio.twiml.voice_response import VoiceResponse

import metric
import sns_client
import util

extensions = util.get_extensions()

def event_to_events(event):
    """Return sequence of sns_client events from DO event."""
    from_uri = event['From']
    to_uri = event['To']
    dial_call_status = event['DialCallStatus']
    dial_event = None
    dial_status_event_base = None

    endpoint = metric.event_to_endpoint(event)

    extension = util.sip_to_extension(from_uri)
    if extension:
        # Outgoing from Twilio SIP Domain,
        # from_uri is SIP URI to extension.
        dial_user_event = "outgoing_call"
        dial_status_user_event_base = "outgoing_dialstatus_"
    else:
        # Incoming to Twilio phone number,
        # to_uri is E.164 of caller.
        dial_user_event = "incoming_call"
        dial_status_user_event_base = "incoming_dialstatus_"

    dial_status_user_event = dial_status_user_event_base + dial_call_status + '_' + endpoint;
    dial_event = {
        'endpoint': endpoint,
        'user_event': dial_user_event};
    dial_status_event = {
        'endpoint': endpoint,
        'user_event': dial_status_user_event};
    return (dial_event, dial_status_event)

def metric_dialer_status(event, context, env):
    """
    Metric the dial status callback attributes from event,
    and return TwiML.
    """
    # Perform the side effects.
    metric.publish('metric_dialer_status', event, env)
    for e in event_to_events(event):
        sns_client.publish(e['endpoint'], e['user_event'], env)

    # Return TwiML.
    response = VoiceResponse()
    if event['DialCallStatus'] == 'failed':
        response.say(
            "We're sorry, your call cannot be completed as dialed. "
            "Please try again later.")
    if event['DialCallStatus'] == 'busy':
        response.reject(reason='busy')
    if event['DialCallStatus'] == 'no-answer':
        # This could be no pickup or not registered.
        # We should care about not registered, metric something,
        # it would be nice to fast busy also.
        # The context should have this for not registered:
        # ErrorCode "32009"
        # ErrorMessage "Your TwiML tried to Dial a Twilio SIP Registered User that is not currently registered"
        response.reject(reason='busy')
    else:
        # If the first interation on handset pickup is a local menu, we want to return to that.
        # If the first interation is a SIP call to a remote menu, we want to SIP it again if that
        # call hung up due to a user hitting the back key from the top, otherwise we want to end.
        # If the first interation is a dialtone, we want to end.
        response.hangup()
    return util.twiml_response(response)
