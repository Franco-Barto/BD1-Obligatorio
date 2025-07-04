import mysql.connector
from datetime import datetime, date, time, timedelta

def confirmar_entrada(prompt):
    while True:
        entrada = input(prompt).strip().lower()
        if entrada in ['s', 'n']:
            return entrada
        print("Entrada inválida. Debe ser 's' o 'n'.")

def formatear_hora(hora_str):
    if len(hora_str) != 4 or not hora_str.isdigit():
        return None
    return f"{hora_str[0:2]}:{hora_str[2:4]}"


def nuevo_tecnico(config):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()

    while True:
        cedula = int(input("Nombre del cliente: ").strip())
        if 0 < cedula < 100000000:
            break
        print("Cédula inválida.")

    while True:
        nombre = input("Nombre del cliente: ").strip()
        if 0 < len(nombre) <= 45:
            break
        print("Nombre inválido.")

    while True:
        apellido = input("Apellido del cliente: ").strip()
        if 0 < len(nombre) <= 50:
            break
        print("Apellido inválido.")

    while True:
        telefono = input("Teléfono (opcional): ").strip()
        if telefono == "" or validar_telefono(telefono):
            telefono = telefono if telefono else None
            break
        print("Teléfono inválido.")

    print(f"\nResumen:\nNombre: {nombre}\nCorreo: {correo}\nCédula: {cedula}\nTeléfono: {telefono or '(sin teléfono)'}")
    if confirmar_entrada("¿Confirmar creación del Técnico? (s/n): ") != 's':
        print("Creación cancelada.")
        cursor.close()
        cnx.close()
        return

    cursor.execute("INSERT INTO tecnicos (ci, nombre, apellido, telefono) VALUES (%i, %s, %s, %s)", (cedula,nombre, correo, telefono))
    cnx.commit()
    id_cliente = cursor.lastrowid
    print(f"Cliente creado con ID {id_cliente}.")
    cursor.close()
    cnx.close()

def nuevo_horario(config):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()

    while True:
        querry="select id_tecnico from horario_tecnicos"
        cursor.execute(querry)
        tecnicos = cursor.fetchall()
        id = int(input("Nombre del cliente: ").strip())
        if  id not in tecnicos:
            break
        print("No hay técnico con esa id.")

    while True:
        dia = int(input("Día a asignar (del 0 al 6): ").strip())
        if -1 < dia < 7:
            print("El día debe estar entre 0 y 6.")
            continue
        querry=f"select * from horario_tecnicos where id_tecnico={id} and dia_semana={dia}"
        cursor.execute(querry)
        test = cursor.fetchall()
        if test:
            print("Ese día ya está asignado")
            continue
        break

    while True:
        hora_i_raw = input("Hora de llegada (HHMM, sin dos puntos): ").strip()
        hora_i_formateada = formatear_hora(hora_i_raw)
        if hora_i_formateada is None:
            print("Formato inválido. Use HHMM.")
            continue
        if int(hora_i_raw)<2301:
            print("Hora debe ser antes que 23:00.")
            continue
        try:
            hora_i = datetime.strptime(hora_i_formateada, "%H:%M").time()
            break
        except ValueError:
            print("Hora inválida.")

    while True:
        hora_s_raw = input("Hora de salida (HHMM, sin dos puntos): ").strip()
        hora_s_formateada = formatear_hora(hora_s_raw)
        if hora_s_formateada is None:
            print("Formato inválido. Use HHMM.")
            continue
        if int(hora_s_raw)>59:
            print("Hora debe ser después que 1:00.")
            continue
        if int(hora_s_raw)>int(hora_i_raw):
            print("Hora debe ser después que hora de llegada.")
            continue
        try:
            hora_i = datetime.strptime(hora_i_formateada, "%H:%M").time()
            break
        except ValueError:
            print("Hora inválida.")

    querry=f"insert into INSERT INTO horario_tecnicos (id_tecnico, dia_semana, hora_ingreso, hora_salida) VALUES ({id},{dia},{hora_i_formateada},{hora_s_formateada})"
    cursor.execute(querry)
    cnx.commit()
    cursor.close()
    cnx.close()

def obtener_tecnicos(config):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()
    query = f"select * from tecnicos"
    cursor.execute(query)
    tecnicos = cursor.fetchall()
    for tecnico in tecnicos:
        print(f"{tecnico[0]}: {tecnico[1]}: {tecnico[2]}: {tecnico[3]}: {tecnico[4]}")
    cursor.close()
    cnx.close()

def obtener_horario(config):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()
    while True:
        querry="select id_tecnico from horario_tecnicos"
        cursor.execute(querry)
        tecnicos = cursor.fetchall()
        id = int(input("Nombre del cliente: ").strip())
        if  id not in tecnicos:
            break
        print("No hay técnico con esa id.")
    query = f"select * from horario_tecnicos where id_tecnico = {id}"
    cursor.execute(query)
    horarios = cursor.fetchall()
    if horarios:
        print(f"Horarios de {horario[0][0]}:")
    for horario in horarios:
        print(f"{horario[1]}: llegada:{horario[2]}, salida:{horario[3]}")

def menu_técnicos(config):
    while True:
        print("""
--- Gestión de Máquinas ---
1. Agregar técnicos
2. Agregar horarios
3. Consulta técnicos
4. Consulta horarios
5. Salir
""")
        opcion = input("Seleccione una opción: ").strip()
        if opcion == '1':
            nuevo_tecnico(config)
        elif opcion == '2':
            nuevo_horario(config)
        elif opcion == '3':
            obtener_tecnicos(config)
        elif opcion == '4':
            obtener_tecnicos(config)
        elif opcion == '5':
            print("Saliendo...")
            break
        else:
            print("Opción inválida.")