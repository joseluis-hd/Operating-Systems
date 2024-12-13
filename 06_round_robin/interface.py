import tkinter as tk
from tkinter import ttk
from process import *

#Variables globales
elapsed_time = 0
is_paused = False
memory_size = 5
pending_tasks = []
main_memory = []
completed_tasks = []
blocked_tasks = []
simulation_started = False 
num_tasks = 0
quantum = 0  #Quantum para RR

#Update timer
def update_time():
    global elapsed_time, blocked_tasks
    if not is_paused:
        elapsed_time += 1
        time_keeper.config(text=f"Tiempo total transcurrido: {elapsed_time} s")
        process_memory()

        #Actualizar proceso bloqueado
        if blocked_tasks:
            for process in blocked_tasks:
                process.blockedT -= 1

    if pending_tasks or main_memory or blocked_tasks:
        window.after(1000, update_time)  #Actualizar cada segundo
        update_tables()
    else:
        #Generar PCB cuando el programa termine
        generate_PCB()

def update_remaining_tasks():
    global pending_tasks, main_memory
    remaining_tasks.config(text=f"Tareas pendientes: {len(pending_tasks) + len(main_memory)}")

def toggle_pause(event):
    global is_paused
    if event.char.lower() == 'p':
        is_paused = True
    elif event.char.lower() == 'c':
        is_paused = False

#Manejo de interrupciones
def interruption(event):
    global main_memory
    if event.char.lower() == 'i' and main_memory and is_paused == False:
        process = main_memory.pop(0)
        process.blockedT = 7
        process.status = "Bloqueado"
        blocked_tasks.append(process)
        update_tables()

#Manejo de errores
def error(event):
    global main_memory, completed_tasks
    if event.char.lower() == 'e' and main_memory and is_paused == False:
        process = main_memory.pop(0) 
        completed_tasks.append(process)  
        process.service = process.elapsedT                
        process.finalization = elapsed_time                
        process.ret = process.finalization - process.arrive 
        process.wait = process.ret - process.service    
        process.status = "Marcado con error"

        if pending_tasks:
            new_task = pending_tasks.pop(0)
            if new_task.arrive == -1:
                new_task.arrive = elapsed_time
                new_task.status = "Listo"
            main_memory.append(new_task)
            
        update_remaining_tasks()
        update_tables()  

#Proceso nuevo
def new_process(event):
    global main_memory, is_paused, pending_tasks, num_tasks, blocked_tasks
    if event.char.lower() == 'n' and (main_memory or blocked_tasks) and is_paused == False:
        num_tasks += 1
        new_task = generate_processes(1)[0]
        new_task.pid = num_tasks

        if (len(main_memory) + len(blocked_tasks)) < 5:
            new_task.arrive = elapsed_time
            new_task.status = "Listo"
            main_memory.append(new_task)   
        else: 
            pending_tasks.append(new_task)  

        update_remaining_tasks()

def view_PCB(event):
    global main_memory, blocked_tasks, is_paused
    if event.char.lower() == 'b' and (main_memory or blocked_tasks) and not is_paused:
        is_paused = True
        generate_PCB()

#Generar PCBt
def generate_PCB():
    global main_memory, completed_tasks, blocked_tasks, elapsed_time

    PCB_window = tk.Toplevel(window)
    PCB_window.title("Sistemas Operativos: Round Robin --- PCB")
    PCB_window.geometry("1200x600")
    PCB_window.configure(bg="#252525") 

    main_frame = tk.Frame(PCB_window, bg="#2f4f4f")
    main_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

    tk.Label(main_frame, text=":::  Reporte PCB  :::", bg="#2f4f4f", fg="white", font=('Helvetica', 10, 'bold')).grid(row=0, sticky="new")

    PCB_tree = ttk.Treeview(main_frame, columns=('ID', 'Status', 'AT', 'FT', 'ST', 'ResT', 'RetT', 'WT'), show='headings', height=10)
    PCB_tree.heading('ID', text='ID')
    PCB_tree.heading('Status', text='Estatus')
    PCB_tree.heading('AT', text='Tiempo de llegada')
    PCB_tree.heading('FT', text='Tiempo  de finalización')
    PCB_tree.heading('ST', text='Tiempo en servicio')
    PCB_tree.heading('ResT', text='Tiempo de respuesta')
    PCB_tree.heading('RetT', text='Tiempo de retorno')
    PCB_tree.heading('WT', text='Tiempo de espera')

    PCB_tree.grid(row=1,column=0, padx=5, pady=5, sticky="nsew")

    for process in completed_tasks:
        PCB_tree.insert("", tk.END, values=(process.pid, process.status, process.arrive, process.finalization, process.service, process.response, process.ret, process.wait))
    for process in main_memory:
        wait = elapsed_time - process.arrive - process.elapsedT 
        PCB_tree.insert("", tk.END, values=(process.pid, process.status, process.arrive, process.finalization, 
                                            f"{process.elapsedT} *", process.response, process.ret, 
                                            f"{wait} *"))
    for process in blocked_tasks:
        wait = elapsed_time - process.arrive - process.elapsedT
        PCB_tree.insert("", tk.END, values=(process.pid, process.status, process.arrive, process.finalization, 
                                            f"{process.elapsedT} *", process.response, process.ret, 
                                            f"{wait} *"))

def process_memory():
    global main_memory, completed_tasks, pending_tasks, quantum

    if main_memory:
        process = main_memory[0] 
        if process.response == -1:
            if process.pid == 1:
                process.response = 0
            else:
                process.response = elapsed_time - process.arrive
        process.update_time()  
        process.quantum_elapsed += 1  
        update_tables()

        if process.remainingT <= 0:
            process.service = process.elapsedT
            process.finalization = elapsed_time
            process.ret = process.finalization - process.arrive
            process.wait = process.ret - process.service
            process.status = "Completado con éxito"
            completed_tasks.append(main_memory.pop(0))
            
            if pending_tasks:
                process = pending_tasks.pop(0)
                if process.arrive == -1:
                    process.arrive = elapsed_time
                    process.status = "Listo"
                main_memory.append(process)
            update_remaining_tasks()
            update_tables()
        elif process.quantum_elapsed >= quantum:
            process.quantum_elapsed = 0  
            main_memory.append(main_memory.pop(0))  

def update_tables():
    for row in ready_tree.get_children():
        ready_tree.delete(row)
    for process in main_memory[1:]:
        ready_tree.insert("", tk.END, values=(process.pid, process.maxT, process.elapsedT))
    
    for row in process_tree.get_children():
        process_tree.delete(row)
    if main_memory:
        process = main_memory[0]
        process.status = "En proceso"
        process_tree.insert("", tk.END, values=(process.pid, process.maxT, process.elapsedT, process.remainingT, process.op))
    
    for row in blocked_tree.get_children():
        blocked_tree.delete(row)
    for process in blocked_tasks:
        if process.blockedT >= 0:
            blocked_tree.insert("", tk.END, values=(process.pid, process.maxT, process.elapsedT, process.blockedT))
        else: 
            process.status = "Listo"
            main_memory.append(process)
            blocked_tasks.remove(process)

    for row in completed_tree.get_children():
        completed_tree.delete(row)
    for process in completed_tasks:
        process.solve()
        if process.maxT != process.elapsedT:
            completed_tree.insert("", tk.END, values=(process.pid, process.op, "Error"))
        elif process.maxT == process.elapsedT:
            completed_tree.insert("", tk.END, values=(process.pid, process.op, process.result))

def start_simulation():
    global pending_tasks, main_memory, simulation_started, num_tasks, quantum
    
    if simulation_started:
        return
    
    try:
        num_tasks = int(task_entry.get())
        quantum = int(quantum_entry.get())
        if num_tasks <= 0 or quantum <= 0:
            raise ValueError("Debe de ser mayor a 0.")
    except ValueError as e:
        print(f"Entrada inválida: {e}")
        return

    pending_tasks = generate_processes(num_tasks)
    update_remaining_tasks()
    main_memory = pending_tasks[:memory_size]
    for task in main_memory:
        task.arrive = elapsed_time
    pending_tasks = pending_tasks[memory_size:]
    
    update_tables()
    start_button.config(state=tk.DISABLED)
    task_entry.config(state=tk.DISABLED)
    quantum_entry.config(state=tk.DISABLED)
    simulation_started = True
    update_time()

window = tk.Tk()
window.title("Sistemas Operativos: Round Robin")
window.geometry("1200x600")
window.configure(bg="#252525")

window.bind("<Key>", toggle_pause)
window.bind("<Key-i>", interruption)
window.bind("<Key-e>", error)  
window.bind("<Key-n>", new_process)
window.bind("<Key-b>", view_PCB)   

ready_frame = tk.Frame(window, bg="#2f4f4f")
ready_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

process_frame = tk.Frame(window, bg="#2f4f4f")
process_frame.grid(row=0, column=1, pady=5, sticky="nsew")

completed_frame = tk.Frame(window, bg="#2f4f4f")
completed_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

control_frame = tk.Frame(window, bg="#2f4f4f")
control_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=(0,5), sticky="nsew")

tk.Label(ready_frame, text=":::  Listo  :::", bg="#2f4f4f", fg="white", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, sticky="ew")
ready_tree = ttk.Treeview(ready_frame, columns=('ID', 'MT', 'ET'), show='headings', height=10)
ready_tree.heading('ID', text='ID')
ready_tree.heading('MT', text='Tiempo máximo')
ready_tree.heading('ET', text='Tiempo transcurrido')
ready_tree.grid(row=1, padx=5, pady=5, sticky="nsew")

tk.Label(process_frame, text=":::  Tarea en proceso  :::", bg="#2f4f4f", fg="white", font=('Helvetica', 10, 'bold')).grid(row=0, sticky="new")
process_tree = ttk.Treeview(process_frame, columns=('ID', 'MT', 'ET', 'RT', 'OP'), show='headings', height=10)
process_tree.heading('ID', text='ID')
process_tree.heading('MT', text='Tiempo máximo')
process_tree.heading('ET', text='Tiempo transcurrido')
process_tree.heading('RT', text='Tiempo restante')
process_tree.heading('OP', text='Operación')
process_tree.grid(row=1, padx=5, pady=5, sticky="nsew")

tk.Label(process_frame, text=":::  Bloqueados  :::", bg="#2f4f4f", fg="white", font=('Helvetica', 10, 'bold')).grid(row=2, sticky="new")
blocked_tree = ttk.Treeview(process_frame, columns=('ID', 'MT', 'ET', 'BRT'), show='headings', height=10)
blocked_tree.heading('ID', text='ID')
blocked_tree.heading('MT', text='Tiempo máximo')
blocked_tree.heading('ET', text='Elapsed Time')
blocked_tree.heading('BRT', text='Tiempo restante de bloqueo')
blocked_tree.grid(row=3, padx=5, pady=5, sticky="nsew")

tk.Label(completed_frame, text=":::  Tareas completadas  :::", bg="#2f4f4f", fg="white", font=('Helvetica', 10, 'bold')).grid(row=0, sticky="new")
completed_tree = ttk.Treeview(completed_frame, columns=('ID', 'OP', 'RES'), show='headings', height=10)
completed_tree.heading('ID', text='ID')
completed_tree.heading('OP', text='Operación')
completed_tree.heading('RES', text='Resultado')
completed_tree.grid(row=1, padx=5, pady=5, sticky="nsew")

tk.Label(control_frame, text=":::  P - Pausar  :::  C - Continuar  :::  I - Interrumpir  :::  E - Error  :::  N - Proceso nuevo  :::  B - BCP  :::", bg="#2f4f4f", fg="white", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky="w")
remaining_tasks = tk.Label(control_frame, text="Tareas pendientes: ", bg="#2f4f4f", fg="white")
remaining_tasks.grid(row=1, column=0, padx=10, pady=5, sticky="w")
time_keeper = tk.Label(control_frame, text="Tiempo total transcurrido: 0 s", bg="#2f4f4f", fg="white")
time_keeper.grid(row=2, column=0, padx=10, pady=5, sticky="w")
tk.Label(control_frame, text="Tareas totales: ", bg="#2f4f4f", fg="white").grid(row=3, column=0, padx=10, pady=5, sticky="w")

task_entry = tk.Entry(control_frame, width=15)
task_entry.grid(row=3, column=1, padx=5, pady=5)

tk.Label(control_frame, text="Quantum: ", bg="#2f4f4f", fg="white").grid(row=4, column=0, padx=10, pady=5, sticky="w")
quantum_entry = tk.Entry(control_frame, width=15)
quantum_entry.grid(row=4, column=1, padx=5, pady=5)

start_button = tk.Button(control_frame, text="Iniciar", bg="#46548e", fg="white", relief="flat", overrelief="flat", command=start_simulation)
start_button.grid(row=3, column=2, padx=10, pady=5)

window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)
window.grid_columnconfigure(2, weight=1)
ready_frame.grid_rowconfigure(1, weight=1)
ready_frame.grid_columnconfigure(0, weight=1)
process_frame.grid_rowconfigure(1, weight=1)
process_frame.grid_columnconfigure(0, weight=1)
completed_frame.grid_rowconfigure(1, weight=1)
completed_frame.grid_columnconfigure(0, weight=1)

window.mainloop()
