from synced import slist
from shutil import rmtree
from os import remove

path = './synced-test'
name = 'test'
try:
    rmtree(path)
except FileNotFoundError:
    pass

svar = slist(name, path=path)

# append
assert svar == []
svar.append(1)
svar.append(2)
assert svar == [1, 2]
svar.reload()
assert svar == [1, 2]

# extend
svar.extend([3, 4])
assert svar == [1, 2, 3, 4]
svar.reload()
assert svar == [1, 2, 3, 4]

# clear
assert len(svar)
svar.clear()
assert svar == []
svar.reload()
assert svar == []

# batch
svar.clear()
svar.begin()
svar.append(1)
svar.append(2)
svar.reload()
assert svar == []
svar.begin()
svar.append(1)
svar.append(2)
svar.commit()
svar.reload()
assert svar == [1, 2]

print('[OK] slist')
