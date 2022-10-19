class Memoria:
    tamano = 530
    
    def __init__(self):
        self.particiones = []

    def setParticiones(self, particion):
        (self.particiones).append(particion)

    def liberarParticion(self, idp):
        #Libera la partición del proceso que terminó
        for part in range(1,len(self.particiones)):
            if self.particiones[part].idProcAsig == idp:
                self.particiones[part].liberarProceso()
                break

    def asignarParticion(self):
        global cola_nuevos
        global cola_memoria
        global so
        proc_asignados = []

        for n in range(0,len(cola_nuevos)):
            if not (self.particiones[1].Disponible()) and not (self.particiones[2].Disponible()) and not (self.particiones[3].Disponible()):
                break
            else:
                proc = cola_nuevos[n]
                worst = 0
                entro = False
                for i in range(1,len(self.particiones)):
                    if self.particiones[i].Disponible():
                        if proc.tamano > self.particiones[i].tamano:
                            entro = False 
                        else:
                            dif = self.particiones[i].tamano - proc.tamano 
                            if (dif >= worst):
                                worst = dif
                                num_p = i
                                entro = True

                if entro:
                    self.particiones[num_p].asignarProceso(proc, worst)
                    cola_memoria.append(proc)
                    proc_asignados.append(proc)

        if len(cola_nuevos) > 0:
            for p in range(1,len(self.particiones)):
                if self.particiones[p].Disponible():
                        self.particiones[p].fragExterna()

        for i in proc_asignados:
            cola_nuevos.remove(i)

        so.imprimirEvento()


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
        global cola_memoria
        global memoria
        global cpu
        
        #Elimina de todas las colas al proceso
        if self in cola_listos:
            cola_listos.remove(self)
        if self in cola_nuevos:
            cola_nuevos.remove(self)
        if self in cola_memoria:
            cola_memoria.remove(self)

        memoria.liberarParticion(self.idProceso)
        cpu.terminarProceso()
        

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
        #Asigna un proceso a la partición
        self.idProcAsig = proceso.idProceso
        self.fi = fragin
        if self.fe:
            self.fe = False

    def liberarProceso(self):
        #Libera el proceso actual que está en la partición
        self.idProcAsig = None
        self.fi = None

    def fragExterna(self):
        self.fe = True

class CPU:

    def __init__(self, proc_ejec):
        self.proc_ejec = proc_ejec

    def ejecutar(self):
        global cola_memoria
        global cola_listos
        global so

        if len(cola_listos) > 0:
            proceso = cola_listos[0]
            if proceso not in cola_memoria:
                so.PlanificadorMP(proceso)
            if self.proc_ejec == None:
                self.proc_ejec = proceso
            proceso.ejecutar()

    def terminarProceso(self):
        self.proc_ejec = None
        

class SistemaOperativo:

    tamano = 100
    instante = 2

    def incrementarInstante(self):
        self.instante = self.instante + 1

    def PlanificadorLP(self):
        global cola_nuevos
        global cola_memoria
        global proc_na
        global remanentes

        for p in range(0,len(proc_na)):
            if (len(cola_nuevos) + len(cola_memoria)) == 5: # NIVEL DE MULTIPROGRAMACIÓN
                for r in range(p,len(proc_na)):     #Luego de cumplir el NM, el programa se queda buscando si hay algún proceso remanente
                    if proc_na[r].ta == self.instante:
                        remanentes.append(proc_na[r])
                break                 # Si se supera el nivel de multiprogramación, no se cargan más procesos a la cola de nuevos
            if len(remanentes) > 0:
                cola_nuevos.append(remanentes.pop(0))
            elif proc_na[p].ta == self.instante: #Si el instante actual coincide con un TA de un proceso, se lo carga a la cola
                cola_nuevos.append(proc_na[p])
                proc_na[p].ta = -1

    def PlanificadorMP(self, proceso):
        global cola_nuevos
        global cola_memoria
        global memoria

        cola_nuevos.remove(proceso)  #Sale de la cola de nuevos (listos y suspendidos) el proceso a cargar en memoria
        
        id_c = memoria.particiones[1].idProcAsig  #Se guarda el id del proceso que estaba antes en la partición seleccionada
        fragin = memoria.particiones[1].tamano - proceso.tamano
        for i in range(0,len(cola_memoria)):
            if cola_memoria[i].idProceso == id_c:
                cambiar = cola_memoria[i]
                break

        cola_memoria.remove(cambiar)  #Sacamos de la cola_memoria el proceso que va a ser reemplazado
        cola_memoria.append(proceso)    #Ponemos en memoria el proceso que se tiene que ejecutar
        cola_nuevos.append(cambiar)     #Ponemos en la cola de nuevos (listos y suspendidos) el proceso que sufrió el swap-out

        memoria.particiones[1].asignarProceso(proceso, fragin)  #Se hace el swap-in del proceso a ejecutar
        
    
    def OrdenarSJF(self):
        global cola_listos
        global cola_memoria
        global cola_nuevos

        cola_listos = cola_nuevos + cola_memoria
        for i in range(1,len(cola_listos)):
            clave = cola_listos[i]
            j = i-1
            while (j >= 0 and cola_listos[j].ti > clave.ti):
                cola_listos[j+1] = cola_listos[j]
                j = j-1
            cola_listos[j+1] = clave

    def controlarEjecucion(self):
        global cola_nuevos
        global cola_memoria
        global cola_listos
        global memoria

        if memoria.particiones[1].Disponible() and memoria.particiones[2].Disponible() and memoria.particiones[3].Disponible():
            if len(cola_listos) <= 0 and len(cola_memoria) <= 0 and len(cola_nuevos) <= 0:
                return(True)
        else:
            return(False)

    def imprimirEvento(self):
        global cola_listos
        global cola_memoria
        global cola_nuevos
        global memoria
        global cpu
        global proc_na

        print('ESTADOS DE LOS PROCESOS:')
        print(f'EJECUTANDOSE: \n P{cpu.proc_ejec}')
        print('LISTOS:')
        listos = f'P{cola_memoria[0].idProceso}'
        for p in range(1,len(cola_memoria)):
            listos = listos + f', P{cola_memoria[p].idProceso}'
        print(listos)
        print('LISTOS Y SUSPENDIDOS:')
        for p in cola_nuevos:
            print(f"P{p.idProceso}")
        print('NUEVOS:')
        for p in proc_na:
            if p not in cola_memoria and p not in cola_nuevos:
                print(f"P{p.idProceso}")

        n = input('PRESIONE ENTER PARA CONTINUAR')

        #Después de mostrar todos los estados de los procesos, vendría la memoria con las particiones


    def GestorAsignacionMemoria(self):
        global cola_nuevos
        global cola_memoria
        global cola_listos
        global proc_na
        global remanentes
        global memoria
        global cpu

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
        remanentes = []     #Procesos que cumplían con el instante actual del SO pero que no pudieron ingresar al sistema por el nivel de multiprogramación
        fin_asignacion = False

        while[True]:
            so.PlanificadorLP()
            memoria.asignarParticion()
            so.OrdenarSJF()   #Este método sería el PlanificadorCP
            cpu.ejecutar()
            so.incrementarInstante()
            fin_asignacion = so.controlarEjecucion()
            if fin_asignacion:
                break

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
if __name__ == '__main__':
    so = SistemaOperativo()
    so.GestorAsignacionMemoria()