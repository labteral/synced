from synced import svalue
from shutil import rmtree
from os import remove

path = './synced-test'
name = 'test'
try:
    rmtree(path)
except FileNotFoundError:
    pass

svar = svalue(name, path=path)

assert svar.value is None

svar.set('value')
svar.reload()
assert svar.value == 'value'

svar.clear()
assert svar.value is None
svar.reload()
assert svar.value is None

svar.set([1, 2, 3, 4])
svar.reload()
assert svar.value == [1, 2, 3, 4]

print('[OK] svalue')
