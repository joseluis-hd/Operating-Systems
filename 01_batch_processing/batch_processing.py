import time
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk

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

#Crear proceso
def CreateProcessWindow(Window, ExistingIds):
    Process = {}
    ProcessWindow = tk.Toplevel(Window)
    ProcessWindow.title("CREAR LOTE")
    ProcessWindow.geometry("500x500")

    tk.Label(ProcessWindow, text="Nombre del programador:").pack(pady=5)
    NameEntry = tk.Entry(ProcessWindow)
    NameEntry.pack(pady=5)
    tk.Label(ProcessWindow, text="ID:").pack(pady=5)
    IdEntry = tk.Entry(ProcessWindow)
    IdEntry.pack(pady=5)
    tk.Label(ProcessWindow, text="Operación:").pack(pady=5)
    Operations = ["Suma", "Resta", "Multiplicación", "División", "Modulo"]
    OperationVar = tk.StringVar(ProcessWindow)
    OperationVar.set(Operations[0])
    OperationMenu = tk.OptionMenu(ProcessWindow, OperationVar, *Operations)
    OperationMenu.pack(pady=5)
    tk.Label(ProcessWindow, text="Dato 1:").pack(pady=5)
    Num1Entry = tk.Entry(ProcessWindow)
    Num1Entry.pack(pady=5)
    tk.Label(ProcessWindow, text="Dato 2:").pack(pady=5)
    Num2Entry = tk.Entry(ProcessWindow)
    Num2Entry.pack(pady=5)
    tk.Label(ProcessWindow, text="Tiempo de ejecución en segundos:").pack(pady=5)
    TimeEntry = tk.Entry(ProcessWindow)
    TimeEntry.pack(pady=5)

    #Confirmar proceso
    def ConfirmProcess():
        Name = NameEntry.get().strip()
        ProcessId = IdEntry.get().strip()
        Operation = OperationVar.get()
        try:
            Num1 = float(Num1Entry.get().strip())
            Num2 = float(Num2Entry.get().strip())
            Time = float(TimeEntry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Ingresa números válidos.")
            return

        if not Name or not ProcessId or ProcessId in ExistingIds or Time <= 0:
            messagebox.showerror("Error", "Datos inválidos o ID ya existente.")
        else:
            Process.update(
            {
                "Name": Name,
                "Id": ProcessId,
                "Operation": Operation,
                "Num1": Num1,
                "Num2": Num2,
                "Time": Time
            })
            ExistingIds.append(ProcessId)
            ProcessWindow.destroy()

    tk.Button(ProcessWindow, text="Confirmar", command=ConfirmProcess).pack(pady=10)
    ProcessWindow.transient(Window)
    ProcessWindow.wait_window(ProcessWindow)

    return Process

#Ejecutar lote
def ExecuteBatchWindow(Batch, BatchNumber, PendingBatches, CompletedProcesses, Window, TotalTime):
    ExecutionWindow = tk.Toplevel(Window)
    ExecutionWindow.title("PROGRAMA 1. SISTEMAS OPERATIVOS")
    ExecutionWindow.geometry("800x800")

    CurrentBatchText = tk.Label(ExecutionWindow, text="", anchor="w", justify="left")
    CurrentBatchText.grid(row=1, column=0, padx=5, pady=5, sticky="nw")
    ExecutionText = tk.Label(ExecutionWindow, text="", anchor="w", justify="left")
    ExecutionText.grid(row=1, column=1, padx=5, pady=5, sticky="nw")
    CompletedText = tk.Label(ExecutionWindow, text="", anchor="w", justify="left")
    CompletedText.grid(row=1, column=2, padx=5, pady=5, sticky="nw")
    PendingBatchesText = tk.Label(ExecutionWindow, text="", anchor="w")
    PendingBatchesText.grid(row=2, column=0, padx=5, pady=5, sticky="sw")

    #Barra de progreso
    ProgressBar = ttk.Progressbar(ExecutionWindow, orient="horizontal", length=200, mode="determinate")
    ProgressBar.grid(row=2, column=1, padx=5, pady=5, sticky="n")

    CurrentBatchText.config(text=f"Lote actual:\n" + "\n\n".join(f"ID: {p['Id']}\nNombre: {p['Name']}\nTiempo: {p['Time']}" for p in Batch))
    CompletedText.config(text="Terminados:\n" + "\n\n".join(f"ID: {p['Id']}\nNombre: {p['Name']}\nOperación: {p['Operation']}\nResultado: {p['Resultado']}\nLote: {p['BatchNumber']}" for p in CompletedProcesses))
    PendingBatchesText.config(text=f"Lotes pendientes: {PendingBatches} | Contador global: {TotalTime} segundos")
    ExecutionWindow.update()
    time.sleep(5)

    while Batch:
        Process = Batch[0]
        ProgressBar["maximum"] = Process["Time"]
        ProgressBar["value"] = 0

        for ElapsedTime in range(int(Process["Time"])):
            CurrentBatchText.config(text=f"Lote actual:\n" + "\n\n".join(f"ID: {p['Id']}\nNombre: {p['Name']}\nTiempo: {p['Time']}" for p in Batch[1:]))
            ExecutionText.config(text=f"Ejecución:\nID: {Process['Id']}\nNombre: {Process['Name']}\nOperación: {Process['Operation']}\nResultado parcial: {PerformOperation(Process['Operation'], Process['Num1'], Process['Num2'])}\nTiempo inicial: {ElapsedTime}\nTiempo restante: {Process['Time'] - ElapsedTime - 1}")
            CompletedText.config(text="Terminados:\n" + "\n\n".join(f"ID: {p['Id']}\nNombre: {p['Name']}\nOperación: {p['Operation']}\nResultado: {p['Resultado']}\nLote: {p['BatchNumber']}" for p in CompletedProcesses))
            PendingBatchesText.config(text=f"Lotes pendientes: {PendingBatches} | Contador global: {TotalTime} segundos")
            ProgressBar["value"] = ElapsedTime + 1
            ExecutionWindow.update()
            time.sleep(1)
            TotalTime += 1

        #Proceso completado
        Result = PerformOperation(Process["Operation"], Process["Num1"], Process["Num2"])
        Process["Resultado"] = Result
        Process["BatchNumber"] = BatchNumber
        CompletedProcesses.append(Process)
        Batch.pop(0)

        #Actualizar GUI
        CurrentBatchText.config(text=f"Lote actual:\n" + "\n\n".join(f"ID: {p['Id']}\nNombre: {p['Name']}\nTiempo: {p['Time']}" for p in Batch))
        ExecutionText.config(text="Ejecución:")
        CompletedText.config(text="Terminados:\n" + "\n\n".join(f"ID: {p['Id']}\nNombre: {p['Name']}\nOperación: {p['Operation']}\nResultado: {p['Resultado']}\nLote: {p['BatchNumber']}" for p in CompletedProcesses))
        ExecutionWindow.update()

    #Botón de finalizar
    tk.Button(ExecutionWindow, text="Finalizar", command=ExecutionWindow.destroy).grid(row=3, column=1, padx=5, pady=10)

    ExecutionWindow.mainloop()
    return TotalTime

#Main
def RunProgram():
    #Ventana inicial
    InitialWindow = tk.Tk()
    InitialWindow.title("PROGRAMA 1. SISTEMAS OPERATIVOS")
    InitialWindow.geometry("500x500")
    InitialWindow.withdraw()
    ProcessCount = simpledialog.askinteger("Número de Procesos", "¿Cuántos procesos deseas crear?", minvalue=1, parent=InitialWindow)

    if not ProcessCount:
        messagebox.showwarning("Error", "Número de procesos no válido.")
        InitialWindow.destroy()
        return

    InitialWindow.destroy()

    #GUI de ejecución
    ExecutionWindow = tk.Tk()
    ExecutionWindow.title("EJECUCIÓN DEL PROGRAMA")
    ExecutionWindow.geometry("300x100")
    Batches = []
    ExistingIds = []
    CompletedProcesses = []
    TotalTime = 0

    for _ in range(ProcessCount):
        Process = CreateProcessWindow(ExecutionWindow, ExistingIds)
        if Process:
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

RunProgram()
