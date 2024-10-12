import time
import random
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from pynput import keyboard
import threading
from threading import Lock

#Variables globales
NewProcesses = []  #Procesos en estado Nuevo
ReadyProcesses = []  #Procesos en estado Listo (máximo 5)
BlockedProcesses = []  #Procesos en estado Bloqueado
CompletedProcesses = []  #Procesos en estado Terminado
CurrentProcess = None  #Proceso en Ejecución
TotalTime = 0  #Contador global de tiempo
is_paused = False
pause_event = threading.Event()
pause_event.set()  #Inicialmente no está en pausa
is_interrupted = False
is_error = False
execution_lock = Lock()
process_id_counter = 1  #Contador incremental de procesos

#Generar proceso
def GenerateProcess(ProcessId):
    Operations = ["Suma", "Resta", "Multiplicación", "División", "Modulo"]
    Operation = random.choice(Operations)
    Num1 = random.uniform(1, 100)
    Num2 = random.uniform(1, 100)
    Time = random.randint(5, 20)
    return {
        "Id": str(ProcessId),
        "Operation": Operation,
        "Num1": Num1,
        "Num2": Num2,
        "Time": Time,
        "ElapsedTime": 0,
        "Status": "Nuevo",
        "BlockedTime": 0,
        "ArrivalTime": None,
        "FinishTime": None,
        "ReturnTime": None,
        "ResponseTime": None,
        "WaitTime": 0,
        "ServiceTime": 0,
        "Result": None,
        "IsEjecuted": False,
        "FirstExecutionTime": None
    }

#Realizar operación
def PerformOperation(Operation, Num1, Num2):
    if Operation == "Suma":
        return Num1 + Num2
    elif Operation == "Resta":
        return Num1 - Num2
    elif Operation == "Multiplicación":
        return Num1 * Num2
    elif Operation == "División":
        return Num1 / Num2 if Num2 != 0 else "Error, división por cero"
    elif Operation == "Modulo":
        return Num1 % Num2 if Num2 != 0 else "Error, división por cero"

#Pausar ejecución
def PauseExecution(event=None):
    global is_paused
    is_paused = True
    pause_event.clear()  # Detener la ejecución
    print("Ejecución pausada")

#Continuar ejecución
def ContinueExecution(event=None):
    global is_paused
    is_paused = False
    pause_event.set()  # Reanudar la ejecución
    print("Ejecución continuada")
    
#Crear nuevo proceso con datos aleatorios
def CreateNewProcess():
    global process_id_counter
    NewProcesses.append(GenerateProcess(process_id_counter))
    process_id_counter += 1
    print(f"Nuevo proceso creado con ID: {process_id_counter - 1}")
    if (len(NewProcesses) + len(BlockedProcesses) + 1) < 4:
        MoveToReady()
    
def ShowBCP(root, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar):
    global is_paused
    
    #Crear una nueva ventana para el BCP
    bcp_window = tk.Toplevel(root)
    bcp_window.title("BCP - Bloque de Control de Procesos")
    
    #Crear un frame que contendrá el Text y la Scrollbar
    frame = tk.Frame(bcp_window)
    frame.pack(fill=tk.BOTH, expand=True)
    
    #Crear el widget de Text
    bcp_text = tk.Text(frame, wrap=tk.WORD, width=100, height=40)
    
    #Crear la barra de desplazamiento vertical
    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=bcp_text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Configurar el Text para que utilice la barra de desplazamiento
    bcp_text.config(yscrollcommand=scrollbar.set)
    bcp_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    #Mostrar la información de cada proceso
    for process in NewProcesses + ReadyProcesses + BlockedProcesses + CompletedProcesses + ([CurrentProcess] if CurrentProcess else []):
        bcp_text.insert(tk.END, f"ID: {process['Id']}\n")
        bcp_text.insert(tk.END, f"Estado: {process['Status']}\n")
        bcp_text.insert(tk.END, f"Operación: {process['Operation']}, Operando 1: {process['Num1']}, Operando 2: {process['Num2']}\n")
        
        #Estado: Nuevo
        if process["Status"] == "Nuevo":
            # Solo muestra el ID, estado, operación y operandos
            bcp_text.insert(tk.END, "-" * 40 + "\n")
            continue

        #Estado: Listo
        if process["Status"] == "Listo":
            CalculateProcessTimes(process, final=False)
            bcp_text.insert(tk.END, f"Tiempo de llegada: {process['ArrivalTime']}\n")
            bcp_text.insert(tk.END, f"Tiempo de espera: {process['WaitTime']}\n")
            bcp_text.insert(tk.END, f"Tiempo de servicio: {process['ServiceTime']}\n")
            bcp_text.insert(tk.END, f"Tiempo restante en CPU: {process['Time'] - process['ServiceTime']}\n")
            bcp_text.insert(tk.END, f"Tiempo de respuesta: {process['ResponseTime']}\n")
            
        #Estado: Ejecución
        elif process["Status"] == "Ejecución":
            CalculateProcessTimes(process, final=False)
            bcp_text.insert(tk.END, f"Tiempo de llegada: {process['ArrivalTime']}\n")
            bcp_text.insert(tk.END, f"Tiempo de espera: {process['WaitTime']}\n")
            bcp_text.insert(tk.END, f"Tiempo de servicio: {process['ServiceTime']}\n")
            bcp_text.insert(tk.END, f"Tiempo restante en CPU: {process['Time'] - process['ServiceTime']}\n")
            bcp_text.insert(tk.END, f"Tiempo de respuesta: {process['ResponseTime']}\n")

        #Estado: Bloqueado
        elif process["Status"] == "Bloqueado":
            CalculateProcessTimes(process, final=False)
            bcp_text.insert(tk.END, f"Tiempo de llegada: {process['ArrivalTime']}\n")
            bcp_text.insert(tk.END, f"Tiempo de espera: {process['WaitTime']}\n")
            bcp_text.insert(tk.END, f"Tiempo de servicio: {process['ServiceTime']}\n")
            bcp_text.insert(tk.END, f"Tiempo bloqueado restante: {7 - (TotalTime - process['BlockedTime'])} segundos\n")
            bcp_text.insert(tk.END, f"Tiempo restante en CPU: {process['Time'] - process['ServiceTime']}\n")
            bcp_text.insert(tk.END, f"Tiempo de respuesta: {process['ResponseTime']}\n")

        #Estado: Terminado
        elif process["Status"] == "Terminado" or process["Status"] == "Error":
            CalculateProcessTimes(process, final=True)
            bcp_text.insert(tk.END, f"Resultado: {process['Result']}\n")
            bcp_text.insert(tk.END, f"Tiempo de llegada: {process['ArrivalTime']}\n")
            bcp_text.insert(tk.END, f"Tiempo de finalización: {process['FinishTime']}\n")
            bcp_text.insert(tk.END, f"Tiempo de retorno: {process['ReturnTime']}\n")
            bcp_text.insert(tk.END, f"Tiempo de espera: {process['WaitTime']}\n")
            bcp_text.insert(tk.END, f"Tiempo de servicio: {process['ServiceTime']}\n")
            bcp_text.insert(tk.END, f"Tiempo de respuesta: {process['ResponseTime']}\n")

        bcp_text.insert(tk.END, "-" * 40 + "\n")
    
    is_paused = True
    pause_event.clear()
    
    #Esperar a que se presione la tecla 'C' para cerrar la ventana de BCP
    def close_bcp(event=None):
        bcp_window.destroy()  #Cerrar la ventana del BCP
        ContinueExecution()   #Reanudar la ejecución
    
    #Asignar la tecla 'C' para cerrar la ventana de BCP
    bcp_window.bind('c', close_bcp)  # Enlazar la tecla 'C' en la ventana BCP
    
    #Esperar a que se cierre la ventana para continuar con la ejecución
    bcp_window.wait_window()
    
def InterruptProcess(event=None, root=None, ReadyText=None, BlockedText=None, ExecutionText=None, CompletedText=None, NewText=None, TimeText=None, ProgressBar=None):
    global is_interrupted, CurrentProcess
    
    if is_paused:
        print("El programa esta pausado, no es posible hacer interrupciones")
        return
    
    if CurrentProcess:
        is_interrupted = True
        CurrentProcess["Status"] = "Bloqueado"
        CurrentProcess["BlockedTime"] = TotalTime
        BlockedProcesses.append(CurrentProcess)
        CurrentProcess = None
        print("Proceso interrumpido y movido a bloqueados")

        #Actualizar la interfaz inmediatamente después de la interrupción
        UpdateDisplay(ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root)

        #Reanudar ejecución del siguiente proceso si existe
        if ReadyProcesses:
            root.after(1000, ExecuteNextProcess, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root)
        else:
            root.after(1000, ResumeBlockedProcess, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root)
            
        root.after(7000, lambda: ResumeBlockedProcess(root, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar))  #Reanudar en 8 seg

def ResumeBlockedProcess(root, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar):
    global BlockedProcesses, ReadyProcesses, TotalTime, CurrentProcess
    
    if is_paused:  
        root.after(100, ResumeBlockedProcess, root, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar)
        return 
    
    if BlockedProcesses:  #Si hay procesos bloqueados
        process_to_resume = None  #Para almacenar el proceso a reanudar

        #Recorrer los procesos bloqueados, pero sin modificar la lista dentro del bucle
        for process in BlockedProcesses:
            #Verificar si el proceso ha estado bloqueado al menos 7 segundos
            if TotalTime - process["BlockedTime"] >= 7:
                process_to_resume = process
                break

        if process_to_resume:
            BlockedProcesses.remove(process_to_resume)  #Remover el proceso de la lista de bloqueados
            process_to_resume["Status"] = "Listo"
            process_to_resume["BlockedTime"] = 0  #Reiniciar el tiempo bloqueado
            ReadyProcesses.append(process_to_resume)  #Mover a listos
            print(f"Proceso {process_to_resume['Id']} reanudado y movido a listos")

            # Actualizar la interfaz después de reanudar el proceso
            UpdateDisplay(ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root)

            # Si no hay un proceso en ejecución, ejecutar el siguiente proceso en la cola de listos
            if not CurrentProcess and ReadyProcesses:
                root.after(100, ExecuteNextProcess, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root)

        else:
            TotalTime += 1  # Incrementar el tiempo global en cada iteración
            print("Ningún proceso ha cumplido el tiempo de bloqueo de 7 segundos. Verificando de nuevo en 1 segundo.")
            root.after(500, ResumeBlockedProcess, root, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar)
    
    else:
        print("No hay procesos bloqueados.")
        # Si no hay un proceso en ejecución, ejecutar el siguiente proceso en la cola de listos
        if not CurrentProcess and ReadyProcesses:
            root.after(1000, ExecuteNextProcess, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root)
 
# Marcar proceso como error
def ErrorProcess(event=None, root=None, ReadyText=None, BlockedText=None, ExecutionText=None, CompletedText=None, NewText=None, TimeText=None, ProgressBar=None):
    global is_error, CurrentProcess
    
    if is_paused:
        print("El programa esta pausado, no es posible marcar procesos como error")
        return
    
    if CurrentProcess is None:  # Verificar si no hay proceso en ejecución
        print("No hay ningún proceso en ejecución para marcar como error.")
        return
    
    if CurrentProcess:
        CalculateProcessTimes(CurrentProcess, final=True)  # Calcular tiempos con error
        CurrentProcess["Status"] = "Error"
        CurrentProcess["Result"] = "Error en la operación"
        CompletedProcesses.append(CurrentProcess)
        print(f"Proceso {CurrentProcess['Id']} marcado como error")
        
        # Actualizar la interfaz
        UpdateDisplay(ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root)
        
        CurrentProcess = None  # Eliminar el proceso actual de ejecución
        is_error = True

        MoveToReady()
        
        # Ejecutar el siguiente proceso en la cola de listos si lo hay
        if ReadyProcesses:
            root.after(1000, ExecuteNextProcess, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root)
        else:
            ShowFinalResults()

# Función para mostrar el BCP en un hilo separado
def ShowBCPInThread(root, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar):
    # Crear un hilo separado para manejar la ventana del BCP
    threading.Thread(target=ShowBCP, args=(root, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar)).start()

# Listener de teclado
def on_press(key, root, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar):
    try:
        if key.char == 'p':
            PauseExecution()
        elif key.char == 'c':
            ContinueExecution()
        elif key.char == 'i':
            InterruptProcess(root=root, ReadyText=ReadyText, BlockedText=BlockedText, ExecutionText=ExecutionText, CompletedText=CompletedText, NewText=NewText, TimeText=TimeText, ProgressBar=ProgressBar)
        elif key.char == 'e':
            ErrorProcess(root=root, ReadyText=ReadyText, BlockedText=BlockedText, ExecutionText=ExecutionText, CompletedText=CompletedText, NewText=NewText, TimeText=TimeText, ProgressBar=ProgressBar)
        elif key.char == 'b':
            ShowBCPInThread(root, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar) 
        elif key.char == 'n':
            CreateNewProcess()
    except AttributeError:
        pass

# Iniciar listener de teclado
def start_keyboard_listener(root, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar):
    listener = keyboard.Listener(on_press=lambda key: on_press(key, root, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar))
    listener.start()

# Calcular tiempos
def CalculateProcessTimes(process, final=False):
    global TotalTime

    if process["Status"] == "Nuevo":
        # Si el estado es Nuevo, no realizar cálculos ya que los tiempos son indefinidos.
        return

    # Proceso en estado Listo o Bloqueado
    if process["Status"] in ["Listo", "Bloqueado", "Ejecución"]:
        if process["ArrivalTime"] is None:
            process["ArrivalTime"] = TotalTime  # El tiempo en que pasó de Nuevo a Listo

        # El tiempo de servicio es el tiempo efectivo que ha estado en ejecución
        process["ServiceTime"] = process["ElapsedTime"]
        
        process["ReturnTime"] = TotalTime - process["ArrivalTime"]

        # El tiempo de espera es el tiempo total - el tiempo en servicio
        process["WaitTime"] = process["ReturnTime"] - process["ServiceTime"]

        # El tiempo de respuesta se calcula solo cuando el proceso ha ejecutado al menos una vez
        if process["FirstExecutionTime"] is not None:
            process["ResponseTime"] = process["FirstExecutionTime"] - process["ArrivalTime"]
        else:
            # Si el proceso nunca ha sido ejecutado, el tiempo de respuesta es 0
            process["ResponseTime"] = 0

    # Proceso en estado Terminado
    if final and process["Status"] in ["Terminado", "Error"]:
        process["FinishTime"] = TotalTime  # Tiempo en el que finaliza el proceso
        process["ReturnTime"] = process["FinishTime"] - process["ArrivalTime"]  # Tiempo de retorno = fin - llegada
        
        process["ServiceTime"] = process["ElapsedTime"]

        # El tiempo de espera es el tiempo total - el tiempo en servicio
        process["WaitTime"] = process["ReturnTime"] - process["ServiceTime"]

        # El tiempo de respuesta ya se ha calculado cuando el proceso entró por primera vez en ejecución
        if process["FirstExecutionTime"] is not None:
            process["ResponseTime"] = process["FirstExecutionTime"] - process["ArrivalTime"]
        else:
            process["ResponseTime"] = 0
            
# Mover procesos a listo
def MoveToReady():
    
    while len(ReadyProcesses) < 5 and NewProcesses:
        process = NewProcesses.pop(0)
        process["Status"] = "Listo"
        process["ArrivalTime"] = TotalTime
        ReadyProcesses.append(process)

# Actualizar cola de bloqueados
def UpdateBlockedProcesses():
    for process in BlockedProcesses:
        if TotalTime - process["BlockedTime"] >= 7:
            process["Status"] = "Listo"
            process["BlockedTime"] = 0
            ReadyProcesses.append(process)
            BlockedProcesses.remove(process)

# Mostrar resultados finales
def ShowFinalResults():
    result_window = tk.Toplevel()
    result_window.title("Resultados Finales")
    result_text = tk.Text(result_window)
    result_text.pack()

    for process in CompletedProcesses:
        result = f"ID: {process['Id']},\n Estado: {'Error' if process['Status'] == 'Error' else 'Normal'},\n "
        result += f"Tiempo de llegada: {process['ArrivalTime']},\n "
        result += f"Tiempo de finalización: {process['FinishTime']},\n "
        result += f"Tiempo de retorno: {process['ReturnTime']},\n "
        result += f"Tiempo de respuesta: {process['ResponseTime']},\n "
        result += f"Tiempo de espera: {process['WaitTime']},\n "
        result += f"Tiempo de servicio: {process['ServiceTime']}\n"
        result_text.insert(tk.END, result)

# Actualizar interfaz gráfica
def UpdateDisplay(ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root):
    ReadyText.config(text="\n".join([f"ID: {p['Id']} | Tiempo: {p['Time']} | Tiempo transcurrido: {p['ElapsedTime']}" for p in ReadyProcesses]))
    BlockedText.config(text="\n".join([f"ID: {p['Id']} | Bloqueado por {TotalTime - p['BlockedTime']}s" for p in BlockedProcesses]))
    if CurrentProcess:
        ExecutionText.config(text=f"ID: {CurrentProcess['Id']} | Operación: {CurrentProcess['Operation']} | Resultado parcial: {PerformOperation(CurrentProcess['Operation'], CurrentProcess['Num1'], CurrentProcess['Num2']):.2f}\nTiempo transcurrido: {CurrentProcess['ElapsedTime']}/{CurrentProcess['Time']}")
        ProgressBar['value'] = (CurrentProcess["ElapsedTime"] / CurrentProcess["Time"]) * 100  # Actualizar la barra de progreso
    else:
        ExecutionText.config(text="No hay procesos en ejecución")
        ProgressBar['value'] = 0  # Resetear la barra de progreso
    CompletedText.config(text="\n".join([f"ID: {p['Id']} | Operación: {p['Operation']} | Resultado: {p['Result']}" for p in CompletedProcesses]))
    NewText.config(text=f"Procesos nuevos: {len(NewProcesses)}")
    TimeText.config(text=f"Tiempo total: {TotalTime}s")
    root.update()

# Ejecutar proceso siguiente
def ExecuteNextProcess(ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root):
    global TotalTime, CurrentProcess, is_paused, is_interrupted, is_error

    if not ReadyProcesses:  # Si no hay procesos en la cola de listos
        return

    # Intentar adquirir el lock antes de comenzar la ejecución de un proceso
    if not execution_lock.acquire(blocking=False):  
        print("Un proceso ya está en ejecución, esperando...")
        return  # Si otro proceso está en ejecución, salir de la función

    CurrentProcess = ReadyProcesses.pop(0)
    CurrentProcess["Status"] = "Ejecución"
    
    if CurrentProcess["IsEjecuted"] == False:
        CurrentProcess["IsEjecuted"] = True
        CurrentProcess["FirstExecutionTime"] = TotalTime
        
    for ElapsedTime in range(CurrentProcess["ElapsedTime"], CurrentProcess["Time"]):
        if is_paused:
            pause_event.wait()  # Esperar hasta que se reanude

        if is_interrupted:  # Proceso bloqueado
            is_interrupted = False
            execution_lock.release()  # Liberar el lock si el proceso es interrumpido
            UpdateBlockedProcesses()
            return

        if is_error:  # Proceso con error
            execution_lock.release()  # Liberar el lock si hay error
            is_error = False
            CalculateProcessTimes(CurrentProcess, final=True)  # Calcular tiempos al finalizar con error
            MoveToReady()
            return

        CurrentProcess["ElapsedTime"] = ElapsedTime + 1
        TotalTime += 1

        # Actualizar la interfaz en cada ciclo de ejecución
        UpdateDisplay(ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root)

        time.sleep(1)  # Simulación del paso de tiempo

    # Proceso completado
    CalculateProcessTimes(CurrentProcess, final=True)  # Calcular tiempos al finalizar
    CurrentProcess["Status"] = "Terminado"
    CurrentProcess["Result"] = PerformOperation(CurrentProcess["Operation"], CurrentProcess["Num1"], CurrentProcess["Num2"])
    CompletedProcesses.append(CurrentProcess)
    CurrentProcess = None
    execution_lock.release()  # Liberar el lock al terminar la ejecución
    MoveToReady()

    # Verificar si hay más procesos listos para ejecutar
    if ReadyProcesses:
        root.after(1000, ExecuteNextProcess, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root)
    else:
        ShowFinalResults()


# Función principal para ejecutar el programa
def RunProgram():
    global process_id_counter
    # Ventana inicial
    InitialWindow = tk.Tk()
    InitialWindow.title("Simulación FCFS")
    InitialWindow.geometry("300x150")
    ProcessCount = simpledialog.askinteger("Número de Procesos", "¿Cuántos procesos deseas crear?", minvalue=1, parent=InitialWindow)
    if not ProcessCount:
        messagebox.showwarning("Error", "Número de procesos no válido.")
        InitialWindow.destroy()
        return

    InitialWindow.destroy()

    # Crear procesos
    for i in range(ProcessCount):
        NewProcesses.append(GenerateProcess(i + 1))
        process_id_counter += 1

    # Ventana de ejecución
    root = tk.Tk()
    root.title("Simulación FCFS")
    root.geometry("1000x600")

    # Crear etiquetas para cada columna
    ReadyLabel = tk.Label(root, text="Listo", font=("Arial", 12))
    ReadyLabel.grid(row=0, column=0, padx=10, pady=10)
    ReadyText = tk.Label(root, text="", font=("Arial", 10))
    ReadyText.grid(row=1, column=0, padx=10, pady=10)

    BlockedLabel = tk.Label(root, text="Bloqueado", font=("Arial", 12))
    BlockedLabel.grid(row=0, column=1, padx=10, pady=10)
    BlockedText = tk.Label(root, text="", font=("Arial", 10))
    BlockedText.grid(row=1, column=1, padx=10, pady=10)

    ExecutionLabel = tk.Label(root, text="Ejecución", font=("Arial", 12))
    ExecutionLabel.grid(row=0, column=2, padx=10, pady=10)
    ExecutionText = tk.Label(root, text="", font=("Arial", 10))
    ExecutionText.grid(row=1, column=2, padx=10, pady=10)

    # Barra de progreso
    ProgressBar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    ProgressBar.grid(row=3, column=2, padx=10, pady=10)

    CompletedLabel = tk.Label(root, text="Terminado", font=("Arial", 12))
    CompletedLabel.grid(row=0, column=3, padx=10, pady=10)
    CompletedText = tk.Label(root, text="", font=("Arial", 10))
    CompletedText.grid(row=1, column=3, padx=10, pady=10)

    # Etiquetas para procesos en estado nuevo y tiempo total
    NewText = tk.Label(root, text="Procesos nuevos: 0", font=("Arial", 12))
    NewText.grid(row=4, column=2, padx=10, pady=10, sticky="e")

    TimeText = tk.Label(root, text="Tiempo total: 0s", font=("Arial", 12))
    TimeText.grid(row=5, column=2, padx=10, pady=10, sticky="e")

    # Iniciar ejecución de procesos inmediatamente
    MoveToReady()
    if ReadyProcesses:
        root.after(1000, ExecuteNextProcess, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root)

    # Iniciar el listener de teclado pasando los widgets
    start_keyboard_listener(root, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar)

    root.mainloop()

# Ejecutar el programa
if __name__ == "__main__":
    RunProgram()
