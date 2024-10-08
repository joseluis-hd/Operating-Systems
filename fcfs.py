import time
import random
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from pynput import keyboard
import threading


NewProcesses = []  #Procesos en estado Nuevo
ReadyProcesses = []  #Procesos en estado Listo (máximo 5)
BlockedProcesses = []  #Procesos en estado Bloqueado
CompletedProcesses = []  #Procesos en estado Terminado
CurrentProcess = None  #Proceso en Ejecución
TotalTime = 0  #Contador global de tiempo
is_paused = False
pause_event = threading.Event()
pause_event.set()  
is_interrupted = False
is_error = False

#Generar proceso
def GenerateProcess(ProcessId):
    Operations = ["Suma", "Resta", "Multiplicación", "División", "Modulo"]
    Operation = random.choice(Operations)
    Num1 = random.uniform(1, 100)
    Num2 = random.uniform(1, 100)
    Time = random.randint(5, 18) 
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
        "Result": None
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
    pause_event.clear()  
    print("Ejecución pausada")

#Continuar ejecución
def ContinueExecution(event=None):
    global is_paused
    is_paused = False
    pause_event.set()  #Reanudar la ejecución
    print("Ejecución continuada")

def InterruptProcess(event=None, root=None, ReadyText=None, BlockedText=None, ExecutionText=None, CompletedText=None, NewText=None, TimeText=None, ProgressBar=None):
    global is_interrupted, CurrentProcess
    if CurrentProcess:
        is_interrupted = True
        CurrentProcess["Status"] = "Bloqueado"
        CurrentProcess["BlockedTime"] = TotalTime
        BlockedProcesses.append(CurrentProcess)
        print(f"Proceso {CurrentProcess['Id']} interrumpido y movido a bloqueados")
        CurrentProcess = None  #Limpiar el proceso actual

        #Actualizar la interfaz inmediatamente después de la interrupción
        UpdateDisplay(ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root)

        #Programar la reanudación del proceso bloqueado
        root.after(8000, lambda: ResumeBlockedProcess(root, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar))  # Reanudar en 8 segundos
        
        #Verifica si hay más procesos listos para ejecutar
        if ReadyProcesses:
            root.after(1000, ExecuteNextProcess, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root)

def ResumeBlockedProcess(root, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar):
    global BlockedProcesses
    if BlockedProcesses:  
        process = BlockedProcesses.pop(0)  
        process["Status"] = "Listo"
        process["BlockedTime"] = 0  
        ReadyProcesses.append(process) 
        print(f"Proceso {process['Id']} reanudado y movido a listos")

        UpdateDisplay(ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root)

        if ReadyProcesses:
            root.after(1000, ExecuteNextProcess, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root)

#Marcar proceso como error
def ErrorProcess(event=None, root=None, ReadyText=None, BlockedText=None, ExecutionText=None, CompletedText=None, NewText=None, TimeText=None, ProgressBar=None):
    global is_error, CurrentProcess
    if CurrentProcess:
        CalculateProcessTimes(CurrentProcess, final=True)  
        CurrentProcess["Status"] = "Error"
        CurrentProcess["Result"] = "Error en la operación"
        CompletedProcesses.append(CurrentProcess)
        print(f"Proceso {CurrentProcess['Id']} marcado como error")
        
        UpdateDisplay(ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root)
        
        CurrentProcess = None  
        is_error = True
        
        if ReadyProcesses:
            root.after(1000, ExecuteNextProcess, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root)
        else:
            ShowFinalResults()

#Listener de teclado
def on_press(key, root, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar):
    try:
        if key.char == 'p':
            PauseExecution()
        elif key.char == 'c':
            ContinueExecution()
        elif key.char == 'i':
            InterruptProcess(root=root, ReadyText=ReadyText, BlockedText=BlockedText, ExecutionText=ExecutionText, CompletedText=CompletedText, NewText=NewText, TimeText=TimeText, ProgressBar=ProgressBar)
        elif key.char == 'w': 
            ErrorProcess(root=root, ReadyText=ReadyText, BlockedText=BlockedText, ExecutionText=ExecutionText, CompletedText=CompletedText, NewText=NewText, TimeText=TimeText, ProgressBar=ProgressBar)
    except AttributeError:
        pass

#Iniciar listener de teclado
def start_keyboard_listener(root, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar):
    listener = keyboard.Listener(on_press=lambda key: on_press(key, root, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar))
    listener.start()

#Calcular tiempos
def CalculateProcessTimes(process, final=False):
    global TotalTime
    if process is None:
        return  

    if final:  #Proceso ha finalizado normalmente o con error
        process["FinishTime"] = TotalTime  #Tiempo en el que finaliza el proceso
    else:
        process["FinishTime"] = process["BlockedTime"] if process["Status"] == "Bloqueado" else TotalTime

    process["ReturnTime"] = process["FinishTime"] - process["ArrivalTime"]
    
    if process["ResponseTime"] is None:
        process["ResponseTime"] = TotalTime - process["ArrivalTime"]
    
    process["ServiceTime"] = process["ElapsedTime"]
    process["WaitTime"] = process["ReturnTime"] - process["ServiceTime"]

#Mover procesos a listo (límite de 5 procesos en memoria)
def MoveToReady():
    while len(ReadyProcesses) < 5 and NewProcesses:
        process = NewProcesses.pop(0)
        process["Status"] = "Listo"
        process["ArrivalTime"] = TotalTime
        ReadyProcesses.append(process)

#Actualizar cola de bloqueados
def UpdateBlockedProcesses():
    for process in BlockedProcesses:
        if TotalTime - process["BlockedTime"] >= 7:
            process["Status"] = "Listo"
            process["BlockedTime"] = 0
            ReadyProcesses.append(process)
            BlockedProcesses.remove(process)

#Mostrar resultados finales
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

#Actualizar interfaz gráfica
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

def ExecuteNextProcess(ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root):
    global TotalTime, CurrentProcess, is_paused, is_interrupted, is_error

    if not ReadyProcesses and not BlockedProcesses and CurrentProcess is None:
        ShowFinalResults()  #Mostrar resultados finales si no quedan procesos
        return

    if ReadyProcesses:
        CurrentProcess = ReadyProcesses.pop(0)
        CurrentProcess["Status"] = "Ejecución"
        print(f"Proceso {CurrentProcess['Id']} en ejecución")

        while CurrentProcess["ElapsedTime"] < CurrentProcess["Time"]:
            if is_paused:
                pause_event.wait()  

            if is_interrupted: 
                is_interrupted = False
                CalculateProcessTimes(CurrentProcess)  
                BlockedProcesses.append(CurrentProcess)  
                CurrentProcess = None
                UpdateDisplay(ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root)
                return

            if is_error:  #Proceso con error
                is_error = False
                CalculateProcessTimes(CurrentProcess, final=True)  # Calcular tiempos al finalizar con error
                CurrentProcess["Result"] = "Error en la operación"
                CompletedProcesses.append(CurrentProcess)
                CurrentProcess = None
                UpdateDisplay(ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root)
                return

            CurrentProcess["ElapsedTime"] += 1
            TotalTime += 1

            UpdateDisplay(ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root)

            time.sleep(1)  

        #Proceso completado
        CalculateProcessTimes(CurrentProcess, final=True)  
        CurrentProcess["Result"] = PerformOperation(CurrentProcess["Operation"], CurrentProcess["Num1"], CurrentProcess["Num2"])
        CompletedProcesses.append(CurrentProcess)  
        print(f"Proceso {CurrentProcess['Id']} completado y movido a terminados")

        # ¿Actualizar la interfaz después de que el proceso se complete
        CurrentProcess = None  # Limpiar proceso en ejecución
        UpdateDisplay(ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root)

        #Mover nuevos procesos a listos si hay espacio
        MoveToReady()

    #Verificar si quedan procesos para ejecutar o bloquear
    if ReadyProcesses or BlockedProcesses:
        root.after(1000, ExecuteNextProcess, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root)
    else:
        #Si no hay más procesos en listos o bloqueados, mostrar resultados finales
        ShowFinalResults()



#Función  para ejecutar el programa
def RunProgram():
    InitialWindow = tk.Tk()
    InitialWindow.title("Simulación FCFS")
    InitialWindow.geometry("300x150")
    ProcessCount = simpledialog.askinteger("Número de Procesos", "¿Cuántos procesos deseas crear?", minvalue=1, parent=InitialWindow)
    if not ProcessCount:
        messagebox.showwarning("Error", "Número de procesos no válido.")
        InitialWindow.destroy()
        return

    InitialWindow.destroy()

    #Crear procesos
    for i in range(ProcessCount):
        NewProcesses.append(GenerateProcess(i + 1))

    #Ventana de ejecución
    root = tk.Tk()
    root.title("Simulación FCFS")
    root.geometry("1000x600")

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

    ProgressBar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    ProgressBar.grid(row=3, column=2, padx=10, pady=10)

    CompletedLabel = tk.Label(root, text="Terminado", font=("Arial", 12))
    CompletedLabel.grid(row=0, column=3, padx=10, pady=10)
    CompletedText = tk.Label(root, text="", font=("Arial", 10))
    CompletedText.grid(row=1, column=3, padx=10, pady=10)

    NewText = tk.Label(root, text="Procesos nuevos: 0", font=("Arial", 12))
    NewText.grid(row=4, column=2, padx=10, pady=10, sticky="e")

    TimeText = tk.Label(root, text="Tiempo total: 0s", font=("Arial", 12))
    TimeText.grid(row=5, column=2, padx=10, pady=10, sticky="e")

    MoveToReady()
    if ReadyProcesses:
        root.after(1000, ExecuteNextProcess, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar, root)

    start_keyboard_listener(root, ReadyText, BlockedText, ExecutionText, CompletedText, NewText, TimeText, ProgressBar)

    root.mainloop()

#Ejecutar el programa
if __name__ == "__main__":
    RunProgram()
