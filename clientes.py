import re
import mysql.connector
from datetime import date

# --- Validaciones básicas ---

def validar_correo(correo):
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, correo) is not None

def validar_telefono(telefono):
    return telefono.isdigit() and len(telefono) <= 20

def confirmar_entrada(prompt):
    while True:
        entrada = input(prompt).strip().lower()
        if entrada in ['s', 'n']:
            return entrada
        print("Entrada inválida. Debe ser 's' o 'n'.")

# --- Cliente existe ---

def cliente_existe(cursor, id_cliente):
    try:
        id_int = int(id_cliente)
    except ValueError:
        return False
    cursor.execute("SELECT COUNT(*) FROM clientes WHERE id = %s", (id_int,))
    return cursor.fetchone()[0] > 0

# --- Dirección existe ---

def direccion_existe(cursor, id_direccion, id_cliente=None):
    if id_cliente:
        cursor.execute("SELECT COUNT(*) FROM direcciones WHERE id = %s AND id_cliente = %s", (id_direccion, id_cliente))
    else:
        cursor.execute("SELECT COUNT(*) FROM direcciones WHERE id = %s", (id_direccion,))
    return cursor.fetchone()[0] > 0

# --- Agregar cliente ---

def agregar_cliente(config):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()

    while True:
        nombre = input("Nombre del cliente: ").strip()
        if 0 < len(nombre) <= 50:
            break
        print("Nombre inválido.")

    while True:
        correo = input("Correo: ").strip()
        if len(correo) == 0 or len(correo) > 120 or not validar_correo(correo):
            print("Correo inválido.")
            continue
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE correo = %s", (correo,))
        if cursor.fetchone()[0] > 0:
            print("Correo ya registrado.")
            continue
        break

    while True:
        telefono = input("Teléfono (opcional): ").strip()
        if telefono == "" or validar_telefono(telefono):
            telefono = telefono if telefono else None
            break
        print("Teléfono inválido.")

    print(f"\nResumen:\nNombre: {nombre}\nCorreo: {correo}\nTeléfono: {telefono or '(sin teléfono)'}")
    if confirmar_entrada("¿Confirmar creación del cliente? (s/n): ") != 's':
        print("Creación cancelada.")
        cursor.close()
        cnx.close()
        return

    cursor.execute("INSERT INTO clientes (nombre, correo, telefono) VALUES (%s, %s, %s)", (nombre, correo, telefono))
    cnx.commit()
    id_cliente = cursor.lastrowid
    print(f"Cliente creado con ID {id_cliente}.")

    agregar_direcciones_cliente(cursor, cnx, id_cliente)

    cursor.close()
    cnx.close()

def agregar_direcciones_cliente(cursor, cnx, id_cliente):
    while True:
        agregar = input("¿Desea agregar una dirección para este cliente? (s/n): ").strip().lower()
        if agregar == 's':
            while True:
                direccion = input("Ingrese la dirección (max 120 caracteres): ").strip()
                if 0 < len(direccion) <= 120:
                    break
                print("Dirección inválida.")
            cursor.execute("INSERT INTO direcciones (id_cliente, direccion) VALUES (%s, %s)", (id_cliente, direccion))
            cnx.commit()
            print("Dirección agregada.")
        elif agregar == 'n':
            break
        else:
            print("Entrada inválida.")

# --- Listar clientes ---

def listar_clientes(config):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()

    filtro = input("Filtrar por texto en nombre, correo o teléfono (vacío para todos): ").strip()
    if filtro:
        filtro_sql = "%" + filtro + "%"
        cursor.execute("""
            SELECT id, nombre, correo, telefono FROM clientes
            WHERE nombre LIKE %s OR correo LIKE %s OR telefono LIKE %s
            ORDER BY id
        """, (filtro_sql, filtro_sql, filtro_sql))
    else:
        cursor.execute("SELECT id, nombre, correo, telefono FROM clientes ORDER BY id")

    clientes = cursor.fetchall()
    if clientes:
        print("\n--- LISTADO DE CLIENTES ---")
        for c in clientes:
            tel = c[3] if c[3] else "(sin teléfono)"
            print(f"ID: {c[0]} | Nombre: {c[1]} | Correo: {c[2]} | Teléfono: {tel}")
            cursor.execute("SELECT id, direccion FROM direcciones WHERE id_cliente = %s", (c[0],))
            direcciones = cursor.fetchall()
            if direcciones:
                for d in direcciones:
                    print(f"   Dirección ID: {d[0]} | Dirección: {d[1]}")
            else:
                print("   (Sin direcciones)")
    else:
        print("No se encontraron clientes.")

    cursor.close()
    cnx.close()

# --- Editar cliente ---

def editar_cliente(config):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()

    while True:
        id_cliente = input("ID del cliente a editar: ").strip()
        if not id_cliente.isdigit() or not cliente_existe(cursor, id_cliente):
            print("Cliente no válido.")
            continue
        break

    cursor.execute("SELECT nombre, correo, telefono FROM clientes WHERE id = %s", (id_cliente,))
    cliente = cursor.fetchone()
    print(f"\nDatos actuales: Nombre: {cliente[0]}, Correo: {cliente[1]}, Teléfono: {cliente[2] or '(sin teléfono)'}")

    nombre = input("Nuevo nombre (vacío para no cambiar): ").strip() or None
    correo = input("Nuevo correo (vacío para no cambiar): ").strip() or None
    telefono = input("Nuevo teléfono (vacío para no cambiar): ").strip() or None

    campos, valores = [], []

    if nombre:
        if len(nombre) > 50:
            print("Nombre demasiado largo.")
            return
        campos.append("nombre = %s")
        valores.append(nombre)

    if correo:
        if len(correo) > 120 or not validar_correo(correo):
            print("Correo inválido.")
            return
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE correo = %s AND id != %s", (correo, id_cliente))
        if cursor.fetchone()[0] > 0:
            print("Correo ya en uso.")
            return
        campos.append("correo = %s")
        valores.append(correo)

    if telefono:
        if not validar_telefono(telefono):
            print("Teléfono inválido.")
            return
        campos.append("telefono = %s")
        valores.append(telefono)

    if not campos:
        print("No se realizaron cambios.")
        return

    query = f"UPDATE clientes SET {', '.join(campos)} WHERE id = %s"
    valores.append(id_cliente)
    cursor.execute(query, tuple(valores))
    cnx.commit()
    print("Cliente actualizado.")

    cursor.close()
    cnx.close()

# --- Borrar cliente ---

def borrar_cliente(config):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()

    id_cliente = input("ID del cliente a borrar: ").strip()
    if not id_cliente.isdigit() or not cliente_existe(cursor, id_cliente):
        print("ID inválido o cliente no existe.")
        return

    cursor.execute("SELECT COUNT(*) FROM maquinas_alquiler WHERE id_cliente = %s", (id_cliente,))
    if cursor.fetchone()[0] > 0:
        print("Cliente tiene máquinas alquiladas. No se puede borrar.")
        return

    confirmar = input("¿Confirmar borrado? (s/n): ").strip().lower()
    if confirmar != 's':
        print("Operación cancelada.")
        return

    cursor.execute("DELETE FROM direcciones WHERE id_cliente = %s", (id_cliente,))
    cursor.execute("DELETE FROM clientes WHERE id = %s", (id_cliente,))
    cnx.commit()
    print("Cliente y direcciones eliminados.")

    cursor.close()
    cnx.close()

# --- Gestión de direcciones ---

def agregar_direccion_cliente(config):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()

    id_cliente = input("ID del cliente: ").strip()
    if not id_cliente.isdigit() or not cliente_existe(cursor, id_cliente):
        print("Cliente no válido.")
        return

    direccion = input("Nueva dirección (máx 120 caracteres): ").strip()
    if len(direccion) > 120:
        print("Dirección muy larga.")
        return

    cursor.execute("INSERT INTO direcciones (id_cliente, direccion) VALUES (%s, %s)", (id_cliente, direccion))
    cnx.commit()
    print("Dirección agregada.")

    cursor.close()
    cnx.close()

def editar_direccion_cliente(config):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()

    id_direccion = input("ID de la dirección: ").strip()
    nueva_direccion = input("Nueva dirección: ").strip()

    cursor.execute("UPDATE direcciones SET direccion = %s WHERE id = %s", (nueva_direccion, id_direccion))
    cnx.commit()
    print("Dirección actualizada.")

    cursor.close()
    cnx.close()

def borrar_direccion_cliente(config):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()

    id_direccion = input("ID de la dirección: ").strip()

    cursor.execute("SELECT COUNT(*) FROM maquinas_alquiler WHERE id_direccion = %s", (id_direccion,))
    if cursor.fetchone()[0] > 0:
        print("No se puede borrar. Dirección asignada a máquina.")
        return

    cursor.execute("DELETE FROM direcciones WHERE id = %s", (id_direccion,))
    cnx.commit()
    print("Dirección eliminada.")

    cursor.close()
    cnx.close()


# --- Menú principal ---

def menu_clientes(config):
    while True:
        print("""
--- Gestión de Clientes ---
1. Listar clientes y direcciones
2. Agregar cliente
3. Editar cliente
4. Borrar cliente
5. Agregar dirección a cliente
6. Editar dirección
7. Borrar dirección
8. Salir
""")
        opcion = input("Seleccione una opción: ").strip()
        if opcion == '1':
            listar_clientes(config)
        elif opcion == '2':
            agregar_cliente(config)
        elif opcion == '3':
            editar_cliente(config)
        elif opcion == '4':
            borrar_cliente(config)
        elif opcion == '5':
            agregar_direccion_cliente(config)
        elif opcion == '6':
            editar_direccion_cliente(config)
        elif opcion == '7':
            borrar_direccion_cliente(config)
        elif opcion == '8':
            print("Saliendo...")
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    menu_clientes()
