import time
import random
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from pynput import keyboard
import threading

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
    
#Variables globales para manejo de pausa y reanudación
is_paused = False
pause_event = threading.Event()
pause_event.set()
    
def PauseExecution(event=None):
    global is_paused
    is_paused = True
    pause_event.clear()  #Detener la ejecución
    print("Ejecución pausada")

def ContinueExecution(event=None):
    global is_paused
    is_paused = False
    pause_event.set()  #Reanudar la ejecución
    print("Ejecución continuada")

def on_press(key):
    try:
        if key.char == 'p':  #Tecla "p" para pausar
            PauseExecution()
        elif key.char == 'c':  #Tecla "c" para continuar
            ContinueExecution()
    except AttributeError:
        pass  #Ignorar teclas especiales que no tienen char

def on_release(key):
    if key == keyboard.Key.esc:
        return False  #Detener el listener con la tecla Esc

def start_keyboard_listener():
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    
is_interrupted = False
is_error = False

    
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
        "ElapsedTime": 0,  #Nuevo campo para el tiempo transcurrido
        "Result": None,
        "Status": "Pending"
    }

#Ejecutar lote
def ExecuteBatchWindow(Batch, BatchNumber, PendingBatches, CompletedProcesses, Window, TotalTime):
    ExecutionWindow = tk.Toplevel(Window)
    ExecutionWindow.title("Simulación de Lote con Multiprogramación")
    ExecutionWindow.geometry("800x800")

    CurrentBatchText = tk.Label(ExecutionWindow, text="", anchor="w", justify="left")
    CurrentBatchText.grid(row=1, column=0, padx=5, pady=5, sticky="nw")
    ExecutionText = tk.Label(ExecutionWindow, text="", anchor="w", justify="left")
    ExecutionText.grid(row=1, column=1, padx=5, pady=5, sticky="nw")
    CompletedText = tk.Label(ExecutionWindow, text="", anchor="w", justify="left")
    CompletedText.grid(row=1, column=2, padx=5, pady=5, sticky="nw")
    PendingBatchesText = tk.Label(ExecutionWindow, text="", anchor="w")
    PendingBatchesText.grid(row=2, column=0, padx=5, pady=5, sticky="sw")

    ProgressBar = ttk.Progressbar(ExecutionWindow, orient="horizontal", length=200, mode="determinate")
    ProgressBar.grid(row=2, column=1, padx=5, pady=5, sticky="n")

    def UpdateDisplay():
        CurrentBatchText.config(text="Lote actual:\n" + "\n\n".join(
            f"ID: {p['Id']}\nOperación: {p['Operation']}\nTiempo total: {p['Time']}\nTiempo transcurrido: {p['ElapsedTime']}" 
            for p in Batch))
        CompletedText.config(text="Terminados:\n" + "\n\n".join(
            f"ID: {p['Id']}\nOperación: {p['Operation']}\nResultado: {p['Result']}\nEstado: {p['Status']}" 
            for p in CompletedProcesses))
        PendingBatchesText.config(text=f"Lotes pendientes: {PendingBatches} | Contador global: {TotalTime} segundos")
        ExecutionWindow.update()

    def InterruptProcess(event=None):
        global is_interrupted
        is_interrupted = True  #Activar la interrupción
        print("Proceso interrumpido y movido al final de la cola")
            
    def ErrorProcess(event=None):
        global is_error
    
        if Batch:  #Asegurarse de que hay un proceso en ejecución
        
            Process = Batch.pop(0)  #Extraer el proceso actual
            Process["Result"] = "ERROR"  #Marcar el resultado como ERROR
            Process["Status"] = "Error"  #Actualizar el estado a Error
            CompletedProcesses.append(Process)  #Moverlo a la lista de procesos terminados
            is_error = True  #Activar la bandera de error
            print(f"Proceso con ID {Process['Id']} ha sido marcado como Error.")
            UpdateDisplay()  #Actualizar la interfaz gráfica
        
    ExecutionWindow.bind("<Key-i>", InterruptProcess)
    ExecutionWindow.bind("<Key-e>", ErrorProcess)
    ExecutionWindow.bind("<Key-p>", PauseExecution)
    ExecutionWindow.bind("<Key-c>", ContinueExecution)

    ExecutionWindow.focus_set()  #Asegurarse de que la ventana esté enfocada

    def ExecuteNextProcess():
        nonlocal TotalTime
        global is_interrupted, is_error

        if not Batch:  #Si no hay más procesos en el lote
            return

        Process = Batch[0]  #Tomar el primer proceso del lote
        ProgressBar["maximum"] = Process["Time"]
        ProgressBar["value"] = Process["ElapsedTime"]  #Comenzar desde el tiempo transcurrido

        for ElapsedTime in range(Process["ElapsedTime"], int(Process["Time"])):
            if is_paused:
                pause_event.wait()  #Esperar hasta que se reanude
            
            if is_interrupted:
                is_interrupted = False  #Resetear la bandera de interrupción
                Process["ElapsedTime"] = ElapsedTime  #Guardar el tiempo transcurrido hasta la interrupción
                Batch.append(Batch.pop(0))  #Mover proceso interrumpido al final del lote
                UpdateDisplay()
                ExecuteNextProcess()  #Ejecutar el siguiente proceso inmediatamente
                return
        
            if is_error:  #Verificar si hay un error
                is_error = False  #Resetear la bandera de error
                UpdateDisplay()
                if Batch:
                    ExecuteNextProcess()
                return
                    
            ExecutionText.config(text=f"Ejecución:\nID: {Process['Id']}\nOperación: {Process['Operation']}\nResultado parcial: {PerformOperation(Process['Operation'], Process['Num1'], Process['Num2']):.2f}\nTiempo transcurrido: {ElapsedTime}\nTiempo restante: {Process['Time'] - ElapsedTime - 1}")
            ProgressBar["value"] = ElapsedTime + 1
            TotalTime += 1
            UpdateDisplay()
            time.sleep(1)

        #Proceso completado
        Result = PerformOperation(Process["Operation"], Process["Num1"], Process["Num2"])
        Process["Result"] = Result
        Process["Status"] = "Completado"
        CompletedProcesses.append(Process)
        Batch.pop(0)
        UpdateDisplay()

        if Batch:
            ExecutionWindow.after(1000, ExecuteNextProcess)  #Ejecutar siguiente proceso tras 1 segundo

    ExecuteNextProcess()

    tk.Button(ExecutionWindow, text="Finalizar", command=ExecutionWindow.destroy).grid(row=3, column=1, padx=5, pady=10)
    ExecutionWindow.mainloop()
    
#Main
def RunProgram():
    InitialWindow = tk.Tk()
    InitialWindow.title("Simulación de Procesamiento por Lotes")
    InitialWindow.geometry("500x500")
    InitialWindow.withdraw()

    ProcessCount = simpledialog.askinteger("Número de Procesos", "¿Cuántos procesos deseas crear?", minvalue=1, parent=InitialWindow)

    if not ProcessCount:
        messagebox.showwarning("Error", "Número de procesos no válido.")
        InitialWindow.destroy()
        return

    InitialWindow.destroy()

    ExecutionWindow = tk.Tk()
    ExecutionWindow.title("Ejecución del Programa")
    ExecutionWindow.geometry("300x100")
    Batches = []
    CompletedProcesses = []
    TotalTime = 0

    for i in range(ProcessCount):
        Process = GenerateProcess(i + 1)
        if not Batches or len(Batches[-1]) >= 5:
            Batches.append([])
        Batches[-1].append(Process)

    def ExecuteBatches():
        nonlocal TotalTime
        if not Batches:
            messagebox.showwarning("Advertencia", "No hay lotes pendientes.")
            return
        while Batches:
            Batch = Batches.pop(0)
            TotalTime = ExecuteBatchWindow(Batch, len(Batches) + 1, len(Batches), CompletedProcesses, ExecutionWindow, TotalTime)

    ExecuteButton = tk.Button(ExecutionWindow, text="Ejecutar lotes", command=ExecuteBatches)
    ExecuteButton.pack(pady=10)

    ExecutionWindow.mainloop()

if __name__ == "__main__":
    #Iniciar el listener de teclado en un hilo separado
    keyboard_thread = threading.Thread(target=start_keyboard_listener, daemon=True)
    keyboard_thread.start()
    
    RunProgram()
