"""class Proceso:

    def __init__(self, id, ti):
        self.id = id
        self.ti = ti

    def __del__(self):
        pass

    def ejecutar(self):
        self.ti = self.ti - 1
        if self.ti == 0:
            self.terminar()

    def terminar(self):
        global lista
        global listeta
        global liston

        lista.remove(self)
        listeta.remove(self)
        liston.remove(self)
        
        del self

proc1 = Proceso(0, 2)
proc2 = Proceso(1, 3)
proc3 = Proceso(2, 3)
proc4 = Proceso(3, 4)
proc5 = Proceso(4, 4)

lista = []
listeta = []
liston = []
lista.append(proc1)
lista.append(proc2)
listeta.append(proc4)
listeta.append(proc1)
listeta.append(proc3)
liston.append(proc5)
liston.append(proc1)

lista[0].ejecutar()
lista[0].ejecutar()

#print(lista)
#print(listeta)
print(proc1)"""
lista=[]
liju=[9,'o']
for i in lista:
    liju.remove(lista)
    print('hola')
print(len(lista))