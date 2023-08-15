#!/usr/bin/env python3

env_path = 'src/.env'

out = ','.join(open(env_path, 'r').read().splitlines())
out = 'Variables={' + out + '}'
print(out)


