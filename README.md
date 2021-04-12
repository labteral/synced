# synced
Work with disk-synced objects in Python (dict, list &amp; primitive types).


> By default, data is stored under `./synced-data`. You can change this behaviour by setting the `path` parameter in the constructor. Note that this path can be shared by all the defined variables if their id is unique.

## Primitive types
```python
from synced import svalue

svar = svalue('id1')
svar.set(1)
svar.get()
```

## List
```python
from synced import slist

svar = slist('id2')
svar.append(1)
svar.extend([2, 3])

len(svar)

for value in svar:
  print(value)
```

## Dict
```python
from synced import sdict

svar = sdict('id2')
svar['1'] = 'one'
svar.update({'2': 'two', '3': 'three'})

len(svar)

for key, value in svar.items():
  print(key, value)
```

## Common methods
```python
svar.clear() # void content
svar.reload() # reinstantiate from disk
svar.begin() # begin an atomic transaction
svar.commit() # commit an atomic transaction
```
