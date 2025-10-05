"""
Asset population checker.
"""

# XXX Also check for the universals if a menu: press-one etc.


import pathlib

from chalicelib import env_util
from chalicelib import ivrs

sound_format = 'ulaw'
langs = ['en', 'es']

def paths(i_dicts):
    """Yield paths required by ivr config dicts."""
    for lang in langs:
        for i_dict in i_dicts.values():
            # XXX We are not checking intro_sounds.
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
            paths = [statement_to_path(s, i_dict['statement_dir'], lang)
                          for s in statements]
            for p in paths:
                yield(p)


def missing_paths(paths, base):
    """Yield missing paths."""
    for path in paths:
        print('xxx', path)
        path = '/'.join([base, path])
        print('xxx', path)
        if not pathlib.Path(path).is_file():
             yield path

if __name__ == '__main__':
    base = '../dialplan-assets/assets'
    i_dicts = env_util._get_ivrs()
    i_dicts = {'xxx':list(i_dicts.values())[0]}
    for p in set(missing_paths(paths(i_dicts), base)):
        print(p)
