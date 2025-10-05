"""
Asset population checker.
"""

# XXX Also check for the universals if a menu: press-one etc.


import pathlib

from chalicelib import env_util
from chalicelib import ivrs

sound_format = 'ulaw'
langs = ['en', 'es']


def statement_to_path(statement, statement_dir, lang):
    """Return path for statement name."""
    path = statement + '.' + sound_format
    path = statement_dir + '/' + path
    path = lang + "/" + path
    return path

def paths(i_dicts):
    """Yield paths required by ivr config dicts."""
    for i_dict in i_dicts.values():
        for lang in langs:
            # intro_statements are lists of strings.
            statements = i_dict.get('intro_statements', [])
            # menu_entries are lists of tuples or nulls.
            # Ignore null entries, which are placeholders.
            statements += [e[0] for e in i_dict.get('menu_entries', []) if e]
            # other_menu_entries are lists of tuples or nulls.
            # Ignore null entries, which are placeholders.
            statements += [e[0] for e in i_dict.get('other_menu_entries', []) if e]
            # Ignore tuples with initial nulls, which have no statement.
            statements = [s for s in statements if s]
            paths = [
                statement_to_path(s, i_dict['statement_dir'], lang)
                for s in statements]
            for p in paths:
                yield(p)
        # intro_sounds are lists of strings.
        sounds = i_dict.get('intro_sounds', [])
        paths = [
            statement_to_path(s, i_dict['statement_dir'], 'sound')
            for s in sounds]
        for p in paths:
            yield(p)

def missing_paths(paths, base):
    """Yield missing paths."""
    for path in paths:
        path = '/'.join([base, path])
        if not pathlib.Path(path).is_file():
            yield path

if __name__ == '__main__':
    base = '../dialplan-assets/assets'
    i_dicts = env_util._get_ivrs()
    for p in set(missing_paths(paths(i_dicts), base)):
        print(p)
