import collections
from twilio.twiml.voice_response import VoiceResponse
import urllib

from . import util


menu_iterations = 10
LANG_DESTINATION = []
PARENT_DESTINATION = []

KEY_PROMPTS = [
    "press-zero",
    "press-one",
    "press-two",
    "press-three",
    "press-four",
    "press-five",
    "press-six",
    "press-seven",
    "press-eight",
    "press-nine"]


# next_value is cruft.
Stanza = collections.namedtuple('Stanza', ['value', 'next_value'])
INTRO_STANZA = Stanza(value='intro', next_value='menu')
MENU_STANZA = Stanza(value='menu', next_value='menu')
STANZAS = [INTRO_STANZA, MENU_STANZA]


def get_stanza(value):
    """Return the stanza for value."""
    try:
        return [stanza for stanza in STANZAS if stanza.value == value].pop()
    except IndexError:
        return INTRO_STANZA

def swap_lang(lang):
    """
    Return the other language.
    """
    if lang == 'en':
        return 'es'
    return 'en'

def context_dict(ivrs, c_name):
    """
    Return the context dict for c_name, or None.
    """
    return ivrs.get(c_name)

def destination_context_name(digits, c_dict):
    """
    Return the name of the IVR context indicated by c_dict with digits,
    or None.
    """
    if digits == '*':
        return LANG_DESTINATION
    if digits == '#':
        return PARENT_DESTINATION
    try:
        position = int(digits)
        if position == 0:
            # Kluge for the only valid key.
            other_menu_entries = c_dict.get('other_menu_entries', [])
            try:
                menu_entry = [
                    entry for entry in other_menu_entries
                    if entry[1] == 0][0]
            except IndexError:
                # Invalid digit, repeat context.
                return c_dict['name']
            return menu_entry[2]
        else:
            # Humans start with 1 when not calling the operator.
            position -= 1
            menu_entries = c_dict.get('menu_entries', [])
            try:
                menu_entry = menu_entries[position]
            except IndexError:
                # Invalid digit, repeat context.
                return c_dict['name']
            return menu_entry[1]
    except (AttributeError, TypeError):
        # Invalid digit, repeat context.
        return c_dict['name']

# def destination_context_dict(c_name, digits, parent_name):
#     """
#     Return the destination context dict, or LANG_DESTINATION.
#     """
#     c_dict = context_dict(c_name)
#     dest_c_name = destination_context_name(digits, c_dict)
#     if dest_c_name == LANG_DESTINATION:
#         return dest_c_name
#     if dest_c_name == PARENT_DESTINATION:
#         return dest_c_name
#     return context_dict(dest_c_name)

def friction(response, c_name):
    # Note that this is the first interaction on handset pickup, so
    # friction should not be configured to block or ignore possible
    # 911 digits.
    return response

def pre_callable(response, c_dict, lang):
    """
    Perform side effects, if any.
    Return TwiML to preface the context TwiML, or None.
    """
    # Friction, bounce for maintenance, play random, etc.
    if c_dict.get('pre_callable'):
        return friction(response, c_dict['name'])
    return response

def sound_url(
        sound_name, lang, directory, request, env, sound_format='ulaw'):
    """Return the URL for a sound."""
    name = sound_name + '.' + sound_format
    path = lang + "/" + directory + '/' + name
    host = env['ASSET_HOST']
    url = urllib.parse.urlunparse(
        ('https',               # scheme
         host,                # netloc
         path,                # path
         None,                  # params
         None,                 # query
         None))                 # fragment
    return url

def add_gather_stanza(c_dict, lang, parent_c_name, request, response):
    """
    Append a gather to the TwiML Response, and return the gather.
    """
    action_url = util.function_url(
        request,
        'ivr',
        {'context': c_dict['name'],
         'lang': lang,
         'parent': parent_c_name,
         'stanza': MENU_STANZA.value}) # Next stanza is always menu stanza.
    gather = response.gather(
        num_digits=1, timeout=0, finish_on_key='', action=action_url)
    # After the gather we always send the call to the same action.
    _redirect = response.redirect(action_url)
    # We should return the response instead.
    return gather

def add_intro_stanza(response, c_dict, lang, parent_c_name, request, env):
    """
    Add a TwiML stanza to play intro and gather a digit
    based on c_dict and lang, sending the next request to the
    destination URL. Return response.
    """
    gather = add_gather_stanza(
        c_dict, lang, parent_c_name, request, response)
    # Play the intro statements once.
    for statement in c_dict.get('intro_statements', []):
        gather.play(
            sound_url(
                statement,
                lang,
                c_dict['statement_dir'],
                request,
                env))
    return response

def add_menu_stanza(response, c_dict, lang, parent_c_name, iteration, request, env):
    """
    Add a TwiML stanza to play a menu and gather a digit
    based on c_dict and lang, sending the next request to the
    destination URL. Return response.
    """
    gather = add_gather_stanza(
        c_dict, lang, parent_c_name, request, response)
    # Play the menu statements with key prompts repeatedly.
    for i in range(menu_iterations):
        for (e, menu_entry) in enumerate(
                c_dict.get('menu_entries', []), start=1):
            if menu_entry:
                (statement, _dest) = menu_entry
                if statement:
                    gather.play(
                        sound_url(
                            statement,
                            lang,
                            c_dict['statement_dir'],
                            request,
                            env))
                    gather.play(
                        sound_url(
                            KEY_PROMPTS[e],
                            lang,
                            c_dict['statement_dir'],
                            request,
                            env))
        for menu_entry in c_dict.get('other_menu_entries', []):
            if menu_entry:
                (statement, key, _dest) = menu_entry
                if statement:
                    gather.play(
                        sound_url(
                            statement,
                            lang,
                            c_dict['statement_dir'],
                            request,
                            env))
                    # We happen to know that it is 0 because that's
                    # the only value in other_menu_entries.
                    gather.play(
                        sound_url(
                            KEY_PROMPTS[key],
                            lang,
                            c_dict['statement_dir'],
                            request,
                            env))
    return response

def ivr_context(dest_c_dict, lang, c_name, stanza, iteration, request, env):
    """
    Return TwiML to run an IVR context.
    """
    response = VoiceResponse()
    if stanza is INTRO_STANZA:
        response = pre_callable(response, dest_c_dict, lang)
        # We should notice friction here and stop.
        response = add_intro_stanza(
            response, dest_c_dict, lang, c_name, request, env)
    elif stanza is MENU_STANZA:
        response = add_menu_stanza(
            response, dest_c_dict, lang, c_name, iteration, request, env)
    # We hope one of the stanza choices updated the response!
    return response
