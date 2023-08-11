"""
Return TwiML to play an IVR context.
"""

from twilio.twiml.voice_response import VoiceResponse

import dialplan
import metric
import util

extensions = util.get_extensions()

def ivr(event, context, env):
    """Return TwiML to play IVR context with attributes from event."""
    metric.publish('ivr', event, env)
    from_uri = event['From']
    to_uri = event['To']
    digits = event.get('Digits')
    c_name = event.get('context')
    parent_name = event.get('parent') # Should use a session.
    lang = event.get('lang', 'en')

    # Find the destination ivr context dict.
    from_extension = util.sip_to_extension(from_uri)
    if not c_name:
        # Presumably this is the first interaction.
        c_name = extensions[from_extension]['outgoing']
        dest_c_dict = dialplan.context_dict(c_name)
    else:
        # User entered a digit.
        c_dict = dialplan.context_dict(c_name)
        dest_c_name = dialplan.destination_context_name(digits, c_dict)
        if dest_c_name == dialplan.LANG_DESTINATION:
            dest_c_dict = c_dict # Same context.
            lang = dialplan.swap_lang(lang)
        elif dest_c_name == dialplan.PARENT_DESTINATION:
            dest_c_dict = dialplan.context_dict(parent_name)
        else:
            dest_c_dict = dialplan.context_dict(c_name)
        if not dest_c_dict:
            # We don't know this context, so it's on the Asterisk server.
            to_extension = dest_c_name
            # XXX we lose lang! Hopefully user remembers to hit *.
            response = util.dial_sip_futel(
                to_extension, from_extension, context, env)
            return util.twiml_response(response)

    response = dialplan.ivr_context(dest_c_dict, lang, c_name, env)
    return util.twiml_response(response)
