import random
import time

def generate_processes (n):
    processes = []

    for i in range (1, n+1):
        max_time = random.randint(1, 10)
        process = Process(i, max_time, generate_operation())
        processes.append(process)

    return processes

def generate_operation ():
    operator = random.randint(1, 5)
    a, b, c = random.randint(-100, 100), random.randint(-100, 100), random.randint(1, 100)

    if operator == 1:      
        operation = str(a) + "+" + str(b)
    elif operator == 2:   
        operation = str(a) + "-" + str(b)
    elif operator == 3:     
        operation = str(a) + "*" + str(b)
    elif operator == 4:     
        operation = str(a) + "/" + str(c)
    elif operator == 5:     
        operation = str(a) + "%" + str(c)
    return operation

class Process:
    def __init__(self, pid=0, maxT=0, op=""):
        self.pid = pid
        self.maxT = maxT
        self.elapsedT = 0
        self.remainingT = maxT
        self.op = op
        self.result = ""

        self.blockedT = 0

        #PCB
        self.arrive = -1
        self.response = -1
        self.finalization = -1
        self.ret = -1
        self.service = -1
        self.wait = -1

        self.status = ""

    #Class methods
    def update_time(self):
        self.elapsedT += 1
        self.remainingT -= 1

    def solve(self):
        try:
            self.result = str(eval(self.op))
        except ZeroDivisionError:
            self.result = "Error (div by 0)"
        except Exception as e:
            self.result = f"Error ({str(e)})"

    def get_PCB_string(self):
        PCB = f"Process ID: {self.pid} \n"
        PCB += f"Hora de llegada: {self.arrive} \n"
        PCB += f"Tiempo de finalizacion: {self.finalization} \n"
        PCB += f"Tiempo de servicio: {self.service} \n"
        PCB += f"Tiempo de respuesta: {self.response} \n"
        PCB += f"Tiempo de retorno: {self.ret} \n"
        PCB += f"Tiempo de espera: {self.wait} \n"

        return PCB
