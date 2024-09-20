import collections
import copy
from twilio.twiml.voice_response import VoiceResponse
import urllib

from . import ivr_destinations
from . import util


MENU_ITERATIONS = 10
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


Stanza = collections.namedtuple('Stanza', ['value'])
INTRO_STANZA = Stanza(value='intro')
MENU_STANZA = Stanza(value='menu')
NEXT_CONTEXT_STANZA = Stanza(value='next_context')
STANZAS = [INTRO_STANZA, MENU_STANZA, NEXT_CONTEXT_STANZA]


def get_stanza(value):
    """Deserialize value into a stanza and return it."""
    try:
        return [stanza for stanza in STANZAS if stanza.value == value].pop()
    except IndexError:
        return INTRO_STANZA

def get_iteration(value):
    """Deserialize value into an iteration value and return it."""
    try:
        return int(value)
    except Exception:
        return 0

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

def pre_callable(c_dict, request, env):
    """
    Perform side effects, if any.
    Return TwiML to preface the context TwiML, or None.
    """
    # Friction, bounce for maintenance, play random, etc.
    function_name = c_dict.get('pre_callable')
    if function_name:
        destination = ivr_destinations.get_destination(function_name)
        return destination(request, env)

def sound_url(
        sound_name, lang, directory, env, sound_format='ulaw'):
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

def _add_gather_stanza(
        c_name,
        parent_c_name,
        lang,
        iteration,
        timeout,
        request,
        response):
    """
    Append a gather and redirect to the TwiML Response, and return the gather.
    """
    path = "/ivr/{}".format(c_name)
    url_params = {
        'parent': parent_c_name,
        'lang': lang,
        'iteration': iteration}
    if timeout is None:
        timeout = 2

    # Create the URL that the gather will send the user to on digit entry.
    gather_url_params = copy.copy(url_params)
    # If a digit was entered, the user should hear the intro.
    gather_url_params['stanza'] = INTRO_STANZA.value
    action_url = util.function_url(
        path,
        gather_url_params)
    gather = response.gather(
        num_digits=1, timeout=timeout, finish_on_key='', action=action_url)

    # Create the URL that the redirect will send the user to on no digit entry.
    redirect_url_params = copy.copy(url_params)
    # Menu and intro both redirect to menu stanza if no digit.
    redirect_url_params['stanza'] = MENU_STANZA.value
    action_url = util.function_url(
        path,
        redirect_url_params)
    _redirect = response.redirect(action_url)
    # We should return the response instead.
    return gather

def _add_intro_stanza(response, c_dict, lang, parent_c_name, iteration, request, env):
    """
    Add a TwiML stanza to play intro and gather a digit
    based on c_dict and lang, sending the next request to the
    destination URL. Return response.
    """
    gather = _add_gather_stanza(
        c_dict['name'],
        parent_c_name,
        lang,
        iteration,
        timeout=0,
        request=request,
        response=response)
    # Play the intro statements once.
    for statement in c_dict.get('intro_statements', []):
        gather.play(
            sound_url(
                statement,
                lang,
                c_dict['statement_dir'],
                env))
    return response

def _add_menu_entry_stanza(statement, e, gather, c_dict, lang, request, env):
    """
    Add TwiML play stanzas to gather, if appropriate. Return gather.
    """
    if statement:
        gather.play(
            sound_url(
                statement,
                lang,
                c_dict['statement_dir'],
                env))
        gather.play(
            sound_url(
                KEY_PROMPTS[e],
                lang,
                c_dict['statement_dir'],
                env))
    return gather

def _add_menu_stanza(
        response, c_dict, lang, parent_c_name, iteration, request, env):
    """
    Add a TwiML stanza to play a menu and gather a digit
    based on c_dict and lang, sending the next request to the
    destination URL. Return response.
    """
    # The next stanza after menu is another menu, with another iteration.
    gather = _add_gather_stanza(
        c_dict['name'],
        parent_c_name,
        lang,
        iteration,
        timeout=None,
        request=request,
        response=response)
    # Play the menu entries which have key prompt statements.
    for (e, menu_entry) in enumerate(
            c_dict.get('menu_entries', []), start=1):
        if menu_entry:
            (statement, _dest) = menu_entry
            gather = _add_menu_entry_stanza(
                statement, e, gather, c_dict, lang, request, env)
    for menu_entry in c_dict.get('other_menu_entries', []):
        if menu_entry:
            (statement, key, _dest) = menu_entry
            gather = _add_menu_entry_stanza(
                statement, key, gather, c_dict, lang, request, env)
    return response

def _has_menu_stanza(c_dict):
    return any(c_dict.get(k) for k in ('menu_entries', 'other_menu_entries'))

def _has_intro_stanza(c_dict):
    return c_dict.get('intro_statements')

def _has_next_context_stanza(c_dict):
    return c_dict.get('next_context')

def _add_next_context_stanza(
        response, c_dict, lang, parent_c_name, request, env):
    next_context = c_dict['next_context']
    path = "/ivr/{}".format(next_context)
    action_url = util.function_url(
        path,
        {'lang': lang,
         'parent': parent_c_name,
         'stanza': INTRO_STANZA.value}) # First stanza is always intro stanza.
    response.redirect(action_url)
    return response

def ivr_context(dest_c_dict, lang, c_name, stanza, iteration, request, env):
    """
    Return TwiML to run an IVR context.
    """
    response = VoiceResponse()
    #if dest_c_dict is None:
    #    dest_c_dict = context_dict(env['ivrs'], dest_c_name)
    if stanza is None:
        stanza = get_stanza(stanza)
    if stanza is INTRO_STANZA:
        pre_response = pre_callable(dest_c_dict, request, env)
        if pre_response:
            # XXX Continue to normalize and push up stringification.
            return str(pre_response)
        if _has_intro_stanza(dest_c_dict):
            return _add_intro_stanza(
                response, dest_c_dict, lang, c_name, iteration, request, env)
    if stanza is not NEXT_CONTEXT_STANZA:
        if _has_menu_stanza(dest_c_dict):
            iteration += 1
            if iteration > MENU_ITERATIONS:
                response.hangup()
                return response
            else:
                return _add_menu_stanza(
                    response, dest_c_dict, lang, c_name, iteration, request, env)
    if _has_next_context_stanza(dest_c_dict):
        return _add_next_context_stanza(
            response, dest_c_dict, lang, c_name, request, env)
    # XXX Is this an expected state, do we want to survive this?
    response.hangup()
    return response
