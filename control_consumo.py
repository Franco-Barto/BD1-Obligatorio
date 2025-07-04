
import mysql.connector
from datetime import datetime

def validar_largo(texto, campo, max_len):
    if len(texto) > max_len:
        print(f"Error: {campo} excede el largo máximo de {max_len} caracteres.")
        return False
    return True

def confirmar_entrada(prompt):
    while True:
        entrada = input(prompt).strip().lower()
        if entrada in ['s', 'n']:
            return entrada
        print("Entrada inválida. Debe ser 's' o 'n'.")

def pedir_entero(mensaje, campo_nombre):
    while True:
        entrada = input(mensaje).strip()
        if entrada.isdigit():
            return int(entrada)
        print(f"Por favor, ingrese un número entero válido para {campo_nombre}.")

def pedir_decimal(mensaje, campo_nombre):
    while True:
        entrada = input(mensaje).strip().replace(",", ".")
        try:
            valor = float(entrada)
            if valor < 0:
                print(f"{campo_nombre} debe ser un número positivo.")
            else:
                return valor
        except ValueError:
            print(f"Ingrese un número válido para {campo_nombre}.")

def pedir_fecha():
    while True:
        entrada = input("Fecha (DDMMYYYY): ").strip()
        try:
            fecha = datetime.strptime(entrada, "%d%m%Y").date()
            return fecha
        except ValueError:
            print("Fecha inválida. Ingrese en formato DDMMYYYY.")

def listar_consumos():
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    print("Filtros opcionales:")
    id_maquina = input("ID de máquina (Enter para omitir): ").strip()
    id_insumo = input("ID de insumo (Enter para omitir): ").strip()

    condiciones = []
    valores = []

    if id_maquina.isdigit():
        condiciones.append("id_maquina = %s")
        valores.append(int(id_maquina))
    elif id_maquina:
        print("ID de máquina inválido. Se ignorará ese filtro.")

    if id_insumo.isdigit():
        condiciones.append("id_insumo = %s")
        valores.append(int(id_insumo))
    elif id_insumo:
        print("ID de insumo inválido. Se ignorará ese filtro.")

    sql = "SELECT id, id_maquina, id_insumo, fecha, cantidad_usada, precio FROM registro_consumo"
    if condiciones:
        sql += " WHERE " + " AND ".join(condiciones)
    sql += " ORDER BY fecha DESC"

    cursor.execute(sql, valores)
    filas = cursor.fetchall()

    if filas:
        print("\n--- Registro de Consumo ---")
        for fila in filas:
            print(f"ID: {fila[0]} | Máquina: {fila[1]} | Insumo: {fila[2]} | Fecha: {fila[3]} | Cantidad: {fila[4]} | Precio: {fila[5]}")
    else:
        print("No hay registros de consumo para los filtros ingresados.")

    cursor.close()
    cnx.close()

def agregar_consumo():
    id_maquina = pedir_entero("ID de máquina: ", "ID de máquina")
    id_insumo = pedir_entero("ID de insumo: ", "ID de insumo")
    fecha = pedir_fecha()
    cantidad = pedir_decimal("Cantidad usada: ", "Cantidad usada")
    precio = pedir_decimal("Precio: ", "Precio")

    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    sql = "INSERT INTO registro_consumo (id_maquina, id_insumo, fecha, cantidad_usada, precio) VALUES (%s, %s, %s, %s, %s)"
    valores = (id_maquina, id_insumo, fecha, cantidad, precio)

    try:
        cursor.execute(sql, valores)
        cnx.commit()
        print("Registro agregado correctamente.")
    except Exception as e:
        print("Error al agregar registro:", e)
    finally:
        cursor.close()
        cnx.close()

def modificar_consumo():
    listar_consumos()
    id_registro = pedir_entero("ID del registro a modificar: ", "ID del registro")

    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM registro_consumo WHERE id = %s", (id_registro,))
    fila = cursor.fetchone()

    if not fila:
        print("No se encontró el registro con ese ID.")
        cursor.close()
        cnx.close()
        return

    print("Valores actuales:")
    print(f"Máquina: {fila[1]}, Insumo: {fila[2]}, Fecha: {fila[3]}, Cantidad: {fila[4]}, Precio: {fila[5]}")

    nueva_maquina = input("Nuevo ID de máquina (Enter para mantener): ").strip()
    nueva_maquina = int(nueva_maquina) if nueva_maquina.isdigit() else fila[1]

    nuevo_insumo = input("Nuevo ID de insumo (Enter para mantener): ").strip()
    nuevo_insumo = int(nuevo_insumo) if nuevo_insumo.isdigit() else fila[2]

    print("Fecha actual:", fila[3].strftime("%d/%m/%Y"))
    fecha = pedir_fecha()

    cantidad = pedir_decimal("Nueva cantidad usada: ", "Cantidad usada")
    precio = pedir_decimal("Nuevo precio: ", "Precio")

    print("\nResumen de modificación:")
    print(f"Máquina: {nueva_maquina}, Insumo: {nuevo_insumo}, Fecha: {fecha}, Cantidad: {cantidad}, Precio: {precio}")
    if confirmar_entrada("¿Confirmar modificación? (s/n): ") == 's':
        try:
            sql = """
                UPDATE registro_consumo
                SET id_maquina = %s, id_insumo = %s, fecha = %s, cantidad_usada = %s, precio = %s
                WHERE id = %s
            """
            cursor.execute(sql, (nueva_maquina, nuevo_insumo, fecha, cantidad, precio, id_registro))
            cnx.commit()
            print("Registro modificado correctamente.")
        except Exception as e:
            print("Error al modificar:", e)
    else:
        print("Modificación cancelada.")

    cursor.close()
    cnx.close()

def eliminar_consumo():
    listar_consumos()
    id_registro = pedir_entero("ID del registro a eliminar: ", "ID del registro")

    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM registro_consumo WHERE id = %s", (id_registro,))
    fila = cursor.fetchone()

    if not fila:
        print("No se encontró el registro con ese ID.")
        cursor.close()
        cnx.close()
        return

    print(f"Registro a eliminar: Máquina {fila[1]} | Insumo {fila[2]} | Fecha {fila[3]} | Cantidad {fila[4]} | Precio {fila[5]}")
    if confirmar_entrada("¿Confirma la eliminación? (s/n): ") == 's':
        try:
            cursor.execute("DELETE FROM registro_consumo WHERE id = %s", (id_registro,))
            cnx.commit()
            print("Registro eliminado correctamente.")
        except Exception as e:
            print("Error al eliminar:", e)
    else:
        print("Eliminación cancelada.")

    cursor.close()
    cnx.close()

def menu_consumo():
    while True:
        print("\n--- Control de Consumo ---")
        print("1. Listar consumos")
        print("2. Agregar consumo")
        print("3. Modificar consumo")
        print("4. Eliminar consumo")
        print("5. Salir")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            listar_consumos()
        elif opcion == "2":
            agregar_consumo()
        elif opcion == "3":
            modificar_consumo()
        elif opcion == "4":
            eliminar_consumo()
        elif opcion == "5":
            break
        else:
            print("Opción inválida. Seleccione una opción del 1 al 5.")
