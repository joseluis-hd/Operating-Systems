import random
import tkinter as tk

# Tamaño del buffer
BUFFER_SIZE = 20
buffer = [None] * BUFFER_SIZE
in_index = 0
out_index = 0
count = 0
simulacion_activa = True  # Bandera para controlar la ejecución
turno_productor = True  # Para alternar entre productor y consumidor

# Ventana principal de la GUI
root = tk.Tk()
root.title("Productor-Consumidor")
text_area = tk.Text(root, height=15, width=50)
text_area.pack()

# Configurar colores para el texto del productor (azul) y consumidor (rojo)
text_area.tag_configure("productor", foreground="blue")
text_area.tag_configure("consumidor", foreground="red")

# Etiquetas para mostrar los estados
estado_productor_label = tk.Label(root, text="Estado del Productor: Inactivo")
estado_productor_label.pack()
estado_consumidor_label = tk.Label(root, text="Estado del Consumidor: Inactivo")
estado_consumidor_label.pack()

# Etiqueta para mostrar el buffer
buffer_label = tk.Label(root, text=f"Buffer: {buffer}")
buffer_label.pack()

def actualizar_texto(mensaje, tag=None):
    # Insertar texto con la etiqueta especificada (para color)
    text_area.insert(tk.END, mensaje + "\n", tag)
    text_area.see(tk.END)

def actualizar_estado_productor(estado):
    estado_productor_label.config(text=f"Estado del Productor: {estado}")

def actualizar_estado_consumidor(estado):
    estado_consumidor_label.config(text=f"Estado del Consumidor: {estado}")

def actualizar_buffer(color):
    # Cambiar el texto del buffer y su color
    buffer_label.config(text=f"Buffer: {buffer}", fg=color)

def productor(elementos_restantes):
    global in_index, count

    if elementos_restantes > 0 and count < BUFFER_SIZE:
        # Producir un ítem
        item = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        buffer[in_index] = item
        mensaje = f"Productor produjo: {item} en posición {in_index}"
        actualizar_texto(mensaje, "productor")  # Texto en azul
        in_index = (in_index + 1) % BUFFER_SIZE  # Buffer circular
        count += 1
        actualizar_buffer("blue")  # Cambiar color del buffer a azul

        # Esperar 500 ms antes de producir el siguiente ítem
        root.after(500, productor, elementos_restantes - 1)
    else:
        actualizar_estado_productor("Esperando...")
        root.after(1000, ciclo_principal)  # Volver al ciclo principal después de 1 segundo

def consumidor(elementos_restantes):
    global out_index, count

    if elementos_restantes > 0 and count > 0:
        # Consumir un ítem
        item = buffer[out_index]
        buffer[out_index] = None
        mensaje = f"Consumidor consumió: {item} de posición {out_index}"
        actualizar_texto(mensaje, "consumidor")  # Texto en rojo
        out_index = (out_index + 1) % BUFFER_SIZE  # Buffer circular
        count -= 1
        actualizar_buffer("red")  # Cambiar color del buffer a rojo

        # Esperar 500 ms antes de consumir el siguiente ítem
        root.after(500, consumidor, elementos_restantes - 1)
    else:
        actualizar_estado_consumidor("Esperando...")
        root.after(1000, ciclo_principal)  # Volver al ciclo principal después de 1 segundo

def ciclo_principal():
    global turno_productor

    if simulacion_activa:
        if turno_productor:
            actualizar_estado_productor("Produciendo...")
            actualizar_estado_consumidor("Esperando...")
            elementos_a_producir = random.randint(4, 7)
            productor(elementos_a_producir)  # Iniciar producción
        else:
            actualizar_estado_consumidor("Consumiendo...")
            actualizar_estado_productor("Esperando...")
            elementos_a_consumir = random.randint(4, 7)
            consumidor(elementos_a_consumir)  # Iniciar consumo
        
        turno_productor = not turno_productor  # Alternar turno

def detener_simulacion(event):
    global simulacion_activa
    simulacion_activa = False  # Detener la simulación cuando se presiona 'Esc'
    root.quit()  # Cerrar la aplicación

# Asignar la tecla 'Esc' para detener la simulación
root.bind('<Escape>', detener_simulacion)

# Iniciar el ciclo principal de la simulación
root.after(1000, ciclo_principal)  # Iniciar después de 1 segundo

# Iniciar el bucle principal de la GUI
root.mainloop()
