from synced import svalue, slist, sdict
from os import environ

path = environ['path']

valor = svalue('valor', path=path)
valor.set('elvalor')
print(valor)
del valor
valor = svalue('valor', path=path)
print(valor)
print()

lista = slist('lista', path=path)
lista.append(1)
lista.append(2)
lista.append(3)
print(lista)
del lista
lista = slist('lista', path=path)
print(lista)
print()

dic = sdict('dic', path=path)
dic['1'] = 'uno'
dic['2'] = 'dos'
dic['3'] = 'tres'
print(dic)
del dic
dic = sdict('dic', path=path)
print(dic)