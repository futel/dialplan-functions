from twilio.twiml import voice_response
import urllib.parse

from assets import ivrs
import util

menu_iterations = 10
LANG_DESTINATION = []
PARENT_DESTINATION = []


key_prompts = [
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

def swap_lang(lang):
    """
    Return the other language.
    """
    if lang == 'en':
        return 'es'
    return 'en'

def context_dict(c_name):
    """
    Return the context dict for c_name, or None.
    """
    return ivrs.ivrs.get(c_name)

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
        position = int(digits) - 1
        menu_entries = c_dict.get('menu_entries', [])
        try:
            menu_entry = menu_entries[position]
        except IndexError:
            # Invalid digit, repeat context.
            return c_dict['name']
        return menu_entry[1]
    except TypeError:
        # Invalid digit, repeat context.
        return c_dict['name']

def destination_context_dict(c_name, digits, parent_name):
    """
    Return the destination context dict, or LANG_DESTINATION.
    """
    c_dict = context_dict(c_name)
    dest_c_name = destination_context_name(digits, c_dict)
    if dest_c_name == LANG_DESTINATION:
        return dest_c_name
    if dest_c_name == PARENT_DESTINATION:
        return dest_c_name
    return context_dict(dest_c_name)

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

def sound_url(sound_name, lang, directory, env, sound_format='ulaw'):
    """Return the URL for a sound."""
    name = sound_name + '.' + sound_format
    path = lang + "/" + directory + '/' + name
    url = urllib.parse.urlunparse(
        ('https',               # scheme
         env['ASSET_HOST'],     # netloc
         path,                # path
         None,                  # params
         None,                 # query
         None))                 # fragment
    #url = ('https://' + env['ASSET_HOST'] + '/' + 'read' + '/' + lang + '/' + directory + '/' +
    #       sound_name + '.' + sound_format)
    return url

def menu(response, c_dict, lang, parent_c_name, env):
    """
    Add a TwiML response to play a menu and gather a digit
    based on c_dict and lang, sending the next request to the
    same URL.
    """
    util.log('xxx ivr start')
    # Set up the action URL: same DO function that is running
    # us now, sending the ivr context, choice, and others.
    # XXX use function_url
    action = "ivr?context=" + c_dict['name']
    action += "&lang=" + lang
    action += "&parent=" + parent_c_name

    gather = response.gather(
        num_digits=1, timeout=0, action=action)
    # Play the intro statements once.
    for statement in c_dict.get('intro_statements', []):
        gather.play(
            sound_url(
                statement,
                lang,
                c_dict['statement_dir'],
                env))
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
                            env))
                    gather.play(
                        sound_url(
                            key_prompts[e],
                            lang,
                            c_dict['statement_dir'],
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
                            env))
    util.log('xxx ivr end')
    return response

def ivr_context(dest_c_dict, lang, c_name, env):
    """
    Return TwiML to run an IVR context.
    """
    # XXX metric
    response = voice_response.VoiceResponse()
    response = pre_callable(response, dest_c_dict, lang)
    response = menu(response, dest_c_dict, lang, c_name, env)
    # XXX no input, say goodbye, hangup
    return response
