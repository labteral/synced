from synced import sdict
from shutil import rmtree
from os import remove

path = './synced-test'
name = 'test'
try:
    rmtree(path)
except FileNotFoundError:
    pass

svar = sdict(name, path=path)

assert svar == {}
svar['1'] = 'one'
svar['2'] = 'two'
svar['3'] = 'three'

svar.reload()
assert len(svar) == 3
assert svar['1'] == 'one'
assert svar['2'] == 'two'
assert svar['3'] == 'three'

print('[OK] sdict')
