import collections
import copy
from twilio.twiml.voice_response import VoiceResponse
import urllib

from . import ivr_destinations
from . import util


MENU_ITERATIONS = 10
LANG_DESTINATION = '*'
PARENT_DESTINATION = '#'

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
                # Invalid digit.
                return None
            return menu_entry[2]
        else:
            # Humans start with 1 when not calling the operator.
            position -= 1
            menu_entries = c_dict.get('menu_entries', [])
            try:
                menu_entry = menu_entries[position]
            except IndexError:
                # Invalid digit.
                return None
            return menu_entry[1]
    except (AttributeError, TypeError):
        # Invalid digit.
        return None

def _pre_callable(c_dict, request, env):
    """
    Perform side effects, if any. Return TwiML, or None.
    """
    # Friction, bounce for maintenance, play random, etc.
    function_name = c_dict.get('pre_callable')
    if function_name:
        destination = ivr_destinations.get_destination(function_name)
        return destination(request, env)

def _intro_sounds(c_name, c_dict, lang, iteration, request, env):
    """
    Return TwiML to play sounds, or None.
    """
    intro_sounds = c_dict.get('intro_sounds')
    if intro_sounds:
        # The context has an intro stanza. Play that, which will then redirect
        # to the next context.
        next_name = c_dict.get('next_context')
        if not next_name:
            # XXX This will repeat infinitely. We should instead validate.
            next_name = c_name
        response = VoiceResponse()
        gather = _add_gather_stanza(
            next_name,
            lang,
            iteration=0,
            timeout=0,
            request=request,
            response=response)
        # Play the intro statements once.
        for name in intro_sounds:
            gather.play(
                sound_url(
                    name,
                    'sound',
                    c_dict['statement_dir'],
                    env))
        return response

def _intro_statements(c_name, c_dict, lang, iteration, request, env):
    """
    Return TwiML to play statements, or None.
    """
    intro_statements = c_dict.get('intro_statements')
    if intro_statements:
        # The context has an intro stanza. Play that, which will then redirect
        # to the next context.
        next_name = c_dict.get('next_context')
        if not next_name:
            # XXX This will repeat infinitely. We should instead validate.
            next_name = c_name
        response = VoiceResponse()
        gather = _add_gather_stanza(
            next_name,
            lang,
            iteration=0,
            timeout=0,
            request=request,
            response=response)
        # Play the intro statements once.
        for statement in intro_statements:
            gather.play(
                sound_url(
                    statement,
                    lang,
                    c_dict['statement_dir'],
                    env))
        return response

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
        lang,
        iteration,
        timeout,
        request,
        response):
    """
    Append a gather and redirect to the TwiML Response, and return the gather.
    """
    path = "/ivr/{}".format(c_name)
    url_params = [('lang', lang)]
    if iteration:
        url_params.append(('iteration', iteration))
    if timeout is None:
        timeout = 2

    # Create the URL that the gather will send the user to on digit entry.
    gather_url_params = list(url_params)
    action_url = util.function_url(
        path,
        gather_url_params)
    gather = response.gather(
        num_digits=1, timeout=timeout, finish_on_key='', action=action_url)

    # Create the URL that the redirect will send the user to on no digit entry.
    redirect_url_params = list(url_params)
    action_url = util.function_url(
        path,
        redirect_url_params)
    _redirect = response.redirect(action_url)
    # We should return the response instead.
    return gather

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

def _add_menu_stanza(c_name, c_dict, lang, iteration, request, env):
    """
    Add a TwiML stanza to play a menu and gather a digit
    based on c_dict and lang, sending the next request to the
    destination URL. Return response.
    """
    response = VoiceResponse()
    # The next stanza after menu is another menu, with another iteration.
    gather = _add_gather_stanza(
        c_name,
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

def ivr_context(c_name, c_dict, lang, iteration, request, env):
    """
    Return TwiML to play an IVR context based on c_dict.
    """
    response = _pre_callable(c_dict, request, env)
    if response:
        # The context has a pre callable. Play that, which will then redirect
        # or hang up.
        return str(response)

    response = _intro_sounds(
        c_name, c_dict, lang, iteration, request, env)
    if response:
        # The context has intro sounds. Play that, which will then redirect
        # to the next context.
        return str(response)

    response = _intro_statements(
        c_name, c_dict, lang, iteration, request, env)
    if response:
        # The context has an intro stanza. Play that, which will then redirect
        # to the next context.
        return str(response)

    # Play the menu stanza, which will then redirect to the same context
    # or hang up.
    iteration += 1
    if iteration > MENU_ITERATIONS:
        response = VoiceResponse()
        response.hangup()
        return response
    else:
        return _add_menu_stanza(c_name, c_dict, lang, iteration, request, env)
