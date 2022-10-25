from tabulate import tabulate

#python -m pip install tabulate

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
        global carlos
        global cola_memoria
        global so
        global cpu
        proc_asignados = []

        for n in range(0,len(carlos)):
            if not (self.particiones[1].Disponible()) and not (self.particiones[2].Disponible()) and not (self.particiones[3].Disponible()):
                break
            else:
                proc = carlos[n]
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

        if len(carlos) > 0:
            for p in range(1,len(self.particiones)):
                if self.particiones[p].Disponible():
                        self.particiones[p].fragExterna()

        for i in proc_asignados:
            carlos.remove(i)


class Proceso:

    def __init__(self, idProceso, tamano, ti, ta):
        self.idProceso = idProceso
        self.tamano = tamano
        self.ti = ti
        self.ta = ta

    def ejecutar(self):
        self.ti = self.ti - 1

    def terminar(self):
        global cola_plan_ejec
        global carlos
        global cola_memoria
        global memoria
        global cpu
        global proc_terminados

        #Elimina de todas las colas al proceso
        if self in cola_plan_ejec:
            cola_plan_ejec.remove(self)
        if self in carlos:
            carlos.remove(self)
        if self in cola_memoria:
            cola_memoria.remove(self)

        if self not in proc_terminados:
            proc_terminados.append(self)
        memoria.liberarParticion(self.idProceso)
        #Cuando un proceso se termina de ejecutar, imprimimos por pantalla ese evento, después, en el mismo instante imprimimos la entrada de un nuevo proceso a memoria
        

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
        global cola_plan_ejec
        global so

        if len(cola_plan_ejec) > 0:
            proceso = cola_plan_ejec[0]
            if proceso not in cola_memoria:
                so.PlanificadorMP(proceso)
            if self.proc_ejec == None:
                self.proc_ejec = proceso
                so.obtenerEvento()
                so.imprimirEventoConsola()
            if self.proc_ejec.ti == 0:
                so.obtenerEvento()
                so.imprimirEventoConsola()
                self.terminarProceso()
            if self.proc_ejec != None:
                self.proc_ejec.ejecutar()  

    def terminarProceso(self):
        self.proc_ejec.terminar()
        self.proc_ejec = None

class SistemaOperativo:

    tamano = 100
    instante = 1

    def incrementarInstante(self):
        self.instante = self.instante + 1

    def PlanificadorLP(self):
        global carlos
        global cola_memoria
        global cola_all_process
        global cola_nuevos

        for p in range(0,len(cola_all_process)):
            if (len(carlos) + len(cola_memoria)) == 5: # NIVEL DE MULTIPROGRAMACIÓN
                for r in range(p,len(cola_all_process)):     #Luego de cumplir el NM, el programa se queda buscando si hay algún proceso remanente
                    if cola_all_process[r].ta == self.instante:
                        if cola_all_process[r] not in cola_nuevos:
                            cola_nuevos.append(cola_all_process[r])
                break                 # Si se supera el nivel de multiprogramación, no se cargan más procesos a la cola de nuevos
            if len(cola_nuevos) > 0:
                r = cola_nuevos[0]
                cola_nuevos.pop(0)
                carlos.append(r)
            elif cola_all_process[p].ta == self.instante: #Si el instante actual coincide con un TA de un proceso, se lo carga a la cola
                carlos.append(cola_all_process[p])
                cola_all_process[p].ta = -1

    def PlanificadorMP(self, proceso):
        global carlos
        global cola_memoria
        global memoria

        carlos.remove(proceso)  #Sale de la cola de nuevos (listos y suspendidos) el proceso a cargar en memoria
        
        id_c = memoria.particiones[1].idProcAsig  #Se guarda el id del proceso que estaba antes en la partición seleccionada
        fragin = memoria.particiones[1].tamano - proceso.tamano
        for i in range(0,len(cola_memoria)):
            if cola_memoria[i].idProceso == id_c:
                cambiar = cola_memoria[i]
                break

        cola_memoria.remove(cambiar)  #Sacamos de la cola_memoria el proceso que va a ser reemplazado
        cola_memoria.append(proceso)    #Ponemos en memoria el proceso que se tiene que ejecutar
        carlos.append(cambiar)     #Ponemos en la cola de nuevos (listos y suspendidos) el proceso que sufrió el swap-out

        memoria.particiones[1].asignarProceso(proceso, fragin)  #Se hace el swap-in del proceso a ejecutar
        
    
    def OrdenarSJF(self):
        global cola_plan_ejec
        global cola_memoria
        global carlos

        cola_plan_ejec = carlos + cola_memoria
        if len(cola_plan_ejec) > 0:
            for i in range(1,len(cola_plan_ejec)):
                clave = cola_plan_ejec[i]
                j = i-1
                while (j >= 0 and cola_plan_ejec[j].ti > clave.ti):
                    cola_plan_ejec[j+1] = cola_plan_ejec[j]
                    j = j-1
                cola_plan_ejec[j+1] = clave

    def controlarEjecucion(self):
        global carlos
        global cola_memoria
        global cola_plan_ejec
        global memoria
        global cola_all_process

        '''for i in cola_all_process:
            print('sj')
            if i.ta != -1:
                return(False)'''

        if memoria.particiones[1].Disponible() and memoria.particiones[2].Disponible() and memoria.particiones[3].Disponible():
            if len(cola_plan_ejec) <= 0 and len(cola_memoria) <= 0 and len(carlos) <= 0:
                return(True)
        else:
            return(False)

    def obtenerEvento(self):
        global cola_plan_ejec
        global cola_memoria
        global carlos
        global memoria
        global cpu
        global cola_all_process
        global cola_nuevos

        global OE_instante
        global OE_proceso_ejec
        global OE_procesos_listos
        global OE_procesos_listos_susp
        global OE_procesos_nuevos
        global OE_procesos_sin_arribar
        global OE_procesos_terminados

        OE_instante = self.instante
        
        #OE_proceso_ejec
        if cpu.proc_ejec != None:
            OE_proceso_ejec = cpu.proc_ejec
        else:
            OE_proceso_ejec = None

        #OE_procesos_listos
        OE_procesos_listos = []
        if cola_memoria != []:
            for p in range(0,len(cola_memoria)):
                if cola_memoria[p] != cpu.proc_ejec:
                    OE_procesos_listos.append(cola_memoria[p])
        
        #OE_procesos_listos_susp
        OE_procesos_listos_susp = []
        if carlos != []:
            for p in carlos:
                OE_procesos_listos_susp.append(p)
        
        #OE_procesos_nuevos
        OE_procesos_nuevos = []
        if cola_nuevos != []:    
            for p in cola_nuevos:
                OE_procesos_nuevos.append(p)

        #OE_procesos_sin_arribar
        OE_procesos_sin_arribar = []
        if cola_all_process != []:
            for p in cola_all_process: 
                if p not in cola_memoria and p not in carlos and p not in cola_nuevos and p not in proc_terminados:
                    OE_procesos_sin_arribar.append(p)

        #OE_procesos_terminados
        OE_procesos_terminados = []
        if proc_terminados != []:
            for p in proc_terminados: 
                OE_procesos_terminados.append(p)

    def imprimirEventoConsola(self):
        global OE_instante
        global OE_proceso_ejec
        global OE_procesos_listos
        global OE_procesos_listos_susp
        global OE_procesos_nuevos
        global OE_procesos_sin_arribar
        global OE_procesos_terminados
        global memoria

        print(f'INSTANTE: {OE_instante}')
        
        print(f'ESTADOS DE LOS PROCESOS:')
        
        print(' - EJECUTANDOSE: ', end='')
        if OE_proceso_ejec == None:
            print('No hay procesos ejecutandose')
        else: 
            print(f'P{OE_proceso_ejec.idProceso}')
        
        print(' - LISTOS: ', end='')
        if OE_procesos_listos != []:
            print(f'P{OE_procesos_listos[0].idProceso}', end='')
            for p in range(1,len(OE_procesos_listos)):
                if OE_procesos_listos[p] != cpu.proc_ejec:
                    print(f', P{OE_procesos_listos[p].idProceso}', end='')

        print('\n - LISTOS Y SUSPENDIDOS: ', end='')
        if OE_procesos_listos_susp != []:
            print(f'P{OE_procesos_listos_susp[0].idProceso}', end='')
            for p in range(1,len(OE_procesos_listos_susp)):
                print(f', P{OE_procesos_listos_susp[p].idProceso}', end='')
        
        print('\n - NO ADMITIDOS: ', end='') 
        if OE_procesos_nuevos != []:    
            print(f'P{OE_procesos_nuevos[0].idProceso}', end='')
            for p in range(1,len(OE_procesos_nuevos)):
                print(f', P{OE_procesos_nuevos[p].idProceso}', end='')

        print('\n - SIN ARRIBAR: ', end='') 
        if OE_procesos_sin_arribar != []:
            print(f'P{OE_procesos_sin_arribar[0].idProceso}', end='')
            for p in range(1,len(OE_procesos_sin_arribar)):
                print(f', P{OE_procesos_sin_arribar[p].idProceso}', end='')

        print('\n - TERMINADOS: ', end='') 
        if OE_procesos_terminados != []:
            print(f'P{OE_procesos_terminados[0].idProceso}', end='')
            for p in range(1,len(OE_procesos_terminados)):
                print(f', P{OE_procesos_terminados[p].idProceso}', end='')

        particiones = []
        fragmentaciones = []
        for p in range(1,len(memoria.particiones)):
            if memoria.particiones[p].idProcAsig == None:
                particiones.append('-')
                if memoria.particiones[p].fe:
                    fragmentaciones.append(f'FE: {memoria.particiones[p].tamano}K')
                else:
                    fragmentaciones.append('Espacio Libre')
            else:
                particiones.append(f'P{memoria.particiones[p].idProcAsig}({memoria.particiones[p].tamano - memoria.particiones[p].fi}K)')
                fragmentaciones.append(f'FI: {memoria.particiones[p].fi}K')

        print('\n')
        tabla_memoria=[['PARTICIÓN', 'CONTENIDO', 'TAMAÑO PARTICIÓN', 'FI/FE/EL'],
                       [0, 'Sistema operativo', f'{memoria.particiones[0].tamano}K', 'FI: 0K'],
                       [1, particiones[0], f'{memoria.particiones[1].tamano}K', fragmentaciones[0]],
                       [2, particiones[1], f'{memoria.particiones[2].tamano}K', fragmentaciones[1]],
                       [3, particiones[2], f'{memoria.particiones[3].tamano}K', fragmentaciones[2]]]

        print(tabulate(tabla_memoria, tablefmt='fancy_grid', stralign='center'))

        n = input('\n\nPRESIONE ENTER PARA CONTINUAR \n')

    def GestorAsignacionMemoria(self):
        global carlos
        global cola_memoria #Acá están los procesos cargados en memoria
        global cola_plan_ejec
        global cola_all_process
        global cola_nuevos
        global memoria
        global cpu
        global proc_terminados
        global OE_instante
        global OE_proceso_ejec
        global OE_procesos_listos
        global OE_procesos_listos_susp
        global OE_procesos_nuevos
        global OE_procesos_sin_arribar
        global OE_procesos_terminados

        part1 = Particion(1, 101, 250, None, None, False)
        part2 = Particion(2, 251, 120, None, None, False)
        part3 = Particion(3, 371, 60, None, None, False)
        memoria = Memoria()
        memoria.setParticiones(so)
        memoria.setParticiones(part1)
        memoria.setParticiones(part2)
        memoria.setParticiones(part3)
        cpu = CPU(None)
        cola_all_process = leerArchivo()  #Procesos que no existen todavía en el SO ; NO ADMITIDO <> NO ARRIBADO
        carlos = []
        cola_memoria = []  #Acá se guarda el PCB de los procesos que están en MP
        cola_plan_ejec = []    #Acá están los de la carlos y cola_memoria ordenados según SJF
        cola_nuevos = []     #Procesos que cumplían con el instante actual del SO pero que no pudieron ingresar al sistema por el nivel de multiprogramación
        proc_terminados = []
        fin_asignacion = False
        OE_instante = so.instante
        OE_proceso_ejec = None
        OE_procesos_listos = []
        OE_procesos_listos_susp = []
        OE_procesos_nuevos = []
        OE_procesos_sin_arribar = cola_all_process
        OE_procesos_terminados = []
        
        so.imprimirEventoConsola()
        so.incrementarInstante()
        while[True]:
            so.PlanificadorLP()
            memoria.asignarParticion()
            so.OrdenarSJF()   #Este método sería el PlanificadorCP
            cpu.ejecutar()
            if cpu.proc_ejec != None:
                so.incrementarInstante()
            fin_asignacion = so.controlarEjecucion()
            if fin_asignacion:
                so.imprimirEventoConsola()
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