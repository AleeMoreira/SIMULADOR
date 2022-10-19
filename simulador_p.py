class Memoria:
    tamano: 530
    
    def __init__(self):
        self.particiones = []

    def setParticiones(self, particion):
        (self.particiones).append(particion)

    def asignarParticion(self):
        global cola_nuevos
        #global cola_memoria

        while [True]:
            if not (self.particiones[1].Disponible()) and not (self.particiones[2].Disponible()) and not (self.particiones[3].Disponible()):
                break
            else:
                #NO TIENE RECORRIDO DE COLA
                proc = cola_nuevos[0]
                worst = 0
                for i in range(1,len(self.particiones)):
                    if self.particiones[i].Disponible():
                        if proc.tamano > self.particiones[i].tamano:
                            no_entro = i         #Para aplicar en la FE, no está terminado todavía
                        else:
                            dif = self.particiones[i].tamano - proc.tamano 
                            if (dif >= worst):
                                worst = dif
                                num_p = i
                                no_entro = None

                if no_entro == None:
                    self.particiones[num_p].asignarProceso(proc, worst)
                    #cola_memoria.append(proc)
                else:
                    self.particiones[no_entro].fragExterna()  #No está terminado


class Proceso:

    def __init__(self, idProceso, tamano, ti, ta):
        self.idProceso = idProceso
        self.tamano = tamano
        self.ti = ti
        self.ta = ta

    def ejecutar(self):
        self.ti = self.ti - 1
        if self.ti == 0:
            self.terminar()

    def terminar(self):
        global cola_listos
        global cola_nuevos
        #global cola_memoria
        
        #Elimina de todas las colas al proceso
        if self in cola_listos:
            cola_listos.remove(self)
        if self in cola_nuevos:
            cola_nuevos.remove(self)
        """ if self in cola_memoria:
            cola_memoria.remove(self) """
        

# 1,2,3,4,5

class Particion:

    def __init__(self, idParticion, dirInicio, tamano, idProcAsig, fi, fe):
        self.idParticion = idParticion
        self.dirInicio = dirInicio
        self.tamano = tamano
        self.idProcAsig = idProcAsig
        self.fi = fi
        self.fe = fe

    def Disponible(self):
        if self.idProcAsig == None:
            return(True)
        else:
            return(False)

    def asignarProceso(self, proceso, fragin):

        self.idProcAsig = proceso.idProceso
        self.fi = fragin

    def fragExterna(self):

        self.fe = True

class CPU:

    def __init__(self, proc_ejec):
        self.proc_ejec = proc_ejec

    def ejecutar(self, proceso):
        #global cola_memoria
        global so
        global memoria

        control = 0
        for i in range(1, memoria.particiones):
            if proceso.idProceso == memoria.particiones[i].idProcAsig:
                proceso.ejecutar()
                break
            else:
                control = control + 1
        
        if control == 3:
            so.PlanificadorMP(proceso)
        

class SistemaOperativo:

    tamano: 100

    def __init__(self, instante):
        self.instante = instante

    def incrementarInstante(self):
        self.instante = self.instante + 1

    def PlanificadorLP(self):
        global cola_nuevos
        #global cola_memoria
        global proc_na

        for p in range(0,len(proc_na)):
            if (len(cola_nuevos) + len(cola_memoria)) == 5: # NIVEL DE MULTIPROGRAMACIÓN
                break                 # Si se supera el nivel de multiprogramación, no se cargan más procesos a la cola de nuevos
            if proc_na[p].ta == self.instante: #Si el instante actual coincide con un TA de un proceso, se lo carga a la cola
                cola_nuevos.append(proc_na[p])
                proc_na[p].ta = -1

    def PlanificadorMP(self, proceso):
        global cola_nuevos
        #global cola_memoria
        global memoria

        #cola_nuevos.remove(proceso)  #Sale de la cola de nuevos (listos y suspendidos) el proceso a cargar en memoria

        worst = 0
        for i in range(1,len(memoria.particiones)):  #Se hace un swap-out del proceso que está en la partición que cumple con el worst-fit, para colocar ahí, el proceso que se debe ejecutar
            dif = memoria.particiones[i].tamano - proceso.tamano 
            if (dif >= worst):
                worst = dif
                num_p = i
        
        cambiar = object
        id_c = memoria.particiones[num_p].idProcAsig  #Se guarda el id del proceso que estaba antes en la partición seleccionada
        for proc in cola_memoria:
            if proc.idProceso == id_c:   #Encontramos en la cola_memoria el proceso que corresponde al id
                cambiar = proc
                break

        #cola_memoria.remove(cambiar)  #Sacamos de la cola_memoria el proceso que va a ser reemplazado
        #cola_memoria.append(proceso)    #Ponemos en memoria el proceso que se tiene que ejecutar

        memoria.particiones[num_p].asignarProceso(proceso, worst)  #Se hace el swap-in del proceso a ejecutar
        
    
    def OrdenarSJF(self):
        global cola_listos
        #global cola_memoria
        global cola_nuevos

        cola_listos = cola_nuevos #+ cola_memoria
        for i in range(1,len(cola_listos)):
            clave = cola_listos[i]
            j = i-1
            while (j >= 0 and cola_listos[j].ti > clave.ti):
                cola_listos[j+1] = cola_listos[j]
                j = j-1
            cola_listos[j+1] = clave



def leerArchivo():
    archivo = open("lista_de_procesos.txt")
    lista_p = []

    for linea in archivo:
        atr = []
        n = ''
        j = 0

        while (j < len(linea)):
            if linea[j] != '(' and linea[j] != ',' and linea[j] != ')' and linea[j] != '\n':
                if linea[j+1] != ',' and linea[j+1] != ')':
                    while (linea[j+1] != ',' and linea[j+1] != ')'):
                        n = n + linea[j]
                        j = j + 1
                    n = n + linea[j]
                else:
                    n = linea[j]
                atr.append(n)
                n = ''
            j += 1

        lista_p.append(Proceso(int(atr[0]), int(atr[1]), int(atr[2]), int(atr[3])))

    return(lista_p)

#Empieza el simulador de asignación de memoria
so = SistemaOperativo(2)
part1 = Particion(1, 101, 250, None, None, False)
part2 = Particion(2, 251, 120, None, None, False)
part3 = Particion(3, 371, 60, None, None, False)
memoria = Memoria()
memoria.setParticiones(so)
memoria.setParticiones(part1)
memoria.setParticiones(part2)
memoria.setParticiones(part3)
cpu = CPU(None)
proc_na = leerArchivo()  #Procesos que no existen todavía en el SO
cola_nuevos = []
cola_memoria = []  #Acá se guarda el PCB de los procesos que están en MP
cola_listos = []    #Acá están los de la cola_nuevos y cola_memoria ordenados según SJF

while [True]:
    so.PlanificadorLP()
    memoria.asignarParticion()
    so.OrdenarSJF()   #Este método sería el PlanificadorCP
    cpu.ejecutar(cola_listos[0])
    so.incrementarInstante()