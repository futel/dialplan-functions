"""
Asset population checker.
"""

import pathlib

from chalicelib import env_util
from chalicelib import ivrs

sound_format = 'ulaw'
langs = ['en', 'es']

def paths(i_dicts):
    """Yield paths required by ivr config dicts."""
    for lang in langs:
        for i_dict in i_dicts.values():
            statements = i_dict.get('intro_statements', [])
            statements += [e.pop(0) for e in i_dict.get('menu_entries', []) if e]
            statements += [e.pop(0) for e in i_dict.get('other_menu_entries', []) if e]
            statements = [s for s in statements if s]
            statements = [s + '.' + sound_format for s in statements]
            paths = [lang + "/" + i_dict['statement_dir'] + '/' + s for s in statements]
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
    i_dicts = env_util.get_ivrs()
    for p in missing_paths(paths(i_dicts), base):
        print(p)
