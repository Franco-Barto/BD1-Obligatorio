import re
from db import get_connection
from datetime import date

# Chequea que el correo tenga un formato correcto
def validar_correo(correo):
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, correo) is not None

# Solo números y máximo 10 caracteres
def validar_telefono(telefono):
    return telefono.isdigit() and len(telefono) <= 10

# Pregunta con s/n y solo acepta eso
def confirmar_entrada(prompt):
    while True:
        entrada = input(prompt).strip().lower()
        if entrada in ['s', 'n']:
            return entrada
        print("Entrada inválida. Debe ser 's' o 'n'.")

# Chequea si el cliente existe en la DB por ID
def cliente_existe(cursor, id_cliente):
    try:
        id_int = int(id_cliente)
    except ValueError:
        return False
    cursor.execute("SELECT COUNT(*) FROM clientes WHERE id = %s", (id_int,))
    return cursor.fetchone()[0] > 0

# Función para agregar cliente, con validaciones básicas
def agregar_cliente():
    conn = get_connection()
    cursor = conn.cursor()

    # Pide nombre y chequea que no esté vacío ni muy largo
    while True:
        nombre = input("Nombre del cliente: ").strip()
        if len(nombre) == 0:
            print("El nombre no puede estar vacío.")
        elif len(nombre) > 50:
            print("El nombre no puede tener más de 50 caracteres.")
        else:
            break

    # Igual con la dirección, pero chequea que no esté repetida
    while True:
        direccion = input("Dirección: ").strip()
        if len(direccion) == 0:
            print("La dirección no puede estar vacía.")
            continue
        if len(direccion) > 120:
            print("La dirección no puede tener más de 120 caracteres.")
            continue
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE direccion = %s", (direccion,))
        if cursor.fetchone()[0] > 0:
            print("La dirección ya está registrada. Intente con otra.")
            continue
        break

    # Correo, con validación de formato y que no esté repetido
    while True:
        correo = input("Correo: ").strip()
        if len(correo) == 0:
            print("El correo no puede estar vacío.")
            continue
        if len(correo) > 120:
            print("El correo no puede tener más de 120 caracteres.")
            continue
        if not validar_correo(correo):
            print("El correo no tiene un formato válido.")
            continue
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE correo = %s", (correo,))
        if cursor.fetchone()[0] > 0:
            print("El correo ya está registrado. Intente con otro.")
            continue
        break

    # Teléfono es opcional, pero si pone algo, que sean solo números
    while True:
        telefono = input("Teléfono (opcional, solo números, max 20 caracteres): ").strip()
        if telefono == "":
            telefono = None
            break
        if not validar_telefono(telefono):
            print("Teléfono inválido. Debe ser solo números y hasta 20 caracteres.")
            continue
        break

    # Muestra todo lo que se va a guardar y pide confirmación
    print("\nResumen del cliente a agregar:")
    print(f"Nombre: {nombre}")
    print(f"Dirección: {direccion}")
    print(f"Correo: {correo}")
    print(f"Teléfono: {telefono if telefono else '(sin teléfono)'}")

    if confirmar_entrada("Confirmar creación del cliente? (s/n): ") == 's':
        cursor.execute(
            "INSERT INTO clientes (nombre, direccion, correo, telefono) VALUES (%s, %s, %s, %s)",
            (nombre, direccion, correo, telefono)
        )
        conn.commit()
        print("Cliente agregado correctamente.")
    else:
        print("Creación cancelada.")

    cursor.close()
    conn.close()

# Listar clientes con filtro por cualquier campo
def listar_clientes():
    conn = get_connection()
    cursor = conn.cursor()

    filtro = input("Filtrar por texto en nombre, dirección, correo o teléfono (dejar vacío para listar todos): ").strip()

    if filtro:
        filtro_sql = "%" + filtro + "%"
        consulta = """
            SELECT id, nombre, direccion, correo, telefono
            FROM clientes
            WHERE nombre LIKE %s OR direccion LIKE %s OR correo LIKE %s OR telefono LIKE %s
            ORDER BY id
        """
        cursor.execute(consulta, (filtro_sql, filtro_sql, filtro_sql, filtro_sql))
    else:
        consulta = "SELECT id, nombre, direccion, correo, telefono FROM clientes ORDER BY id"
        cursor.execute(consulta)

    clientes = cursor.fetchall()

    if clientes:
        print("\n--- LISTADO DE CLIENTES ---")
        for c in clientes:
            tel = c[4] if c[4] else "(sin teléfono)"
            print(f"ID: {c[0]} | Nombre: {c[1]} | Dirección: {c[2]} | Correo: {c[3]} | Teléfono: {tel}")
    else:
        print("No se encontraron clientes con ese filtro.")

    cursor.close()
    conn.close()

# Editar cliente, valida ID, muestra datos actuales y valida cambios
def editar_cliente():
    conn = get_connection()
    cursor = conn.cursor()

    while True:
        id_cliente = input("ID del cliente a editar: ").strip()
        if not id_cliente.isdigit():
            print("ID inválido, debe ser un número.")
            continue
        if not cliente_existe(cursor, id_cliente):
            print("Cliente no encontrado. Intente nuevamente.")
            continue
        break

    cursor.execute("SELECT nombre, direccion, correo, telefono FROM clientes WHERE id = %s", (id_cliente,))
    cliente = cursor.fetchone()
    print("\n--- Datos actuales del cliente ---")
    print(f"Nombre: {cliente[0]}")
    print(f"Dirección: {cliente[1]}")
    print(f"Correo: {cliente[2]}")
    print(f"Teléfono: {cliente[3] if cliente[3] else '(sin teléfono)'}")

    while True:
        nombre = input("Nuevo nombre (dejar vacío para no cambiar): ").strip()
        if not nombre:
            nombre = None
            break
        if len(nombre) > 50:
            print("El nombre no puede tener más de 50 caracteres.")
        else:
            break

    while True:
        direccion = input("Nueva dirección (dejar vacío para no cambiar): ").strip()
        if not direccion:
            direccion = None
            break
        if len(direccion) > 120:
            print("La dirección no puede tener más de 120 caracteres.")
            continue
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE direccion = %s AND id != %s", (direccion, id_cliente))
        if cursor.fetchone()[0] > 0:
            print("La dirección ya está registrada por otro cliente.")
            continue
        break

    while True:
        correo = input("Nuevo correo (dejar vacío para no cambiar): ").strip()
        if not correo:
            correo = None
            break
        if len(correo) > 120:
            print("El correo no puede tener más de 120 caracteres.")
            continue
        if not validar_correo(correo):
            print("El correo no tiene un formato válido.")
            continue
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE correo = %s AND id != %s", (correo, id_cliente))
        if cursor.fetchone()[0] > 0:
            print("El correo ya está en uso por otro cliente.")
            continue
        break

    while True:
        telefono = input("Nuevo teléfono (dejar vacío para no cambiar): ").strip()
        if not telefono:
            telefono = None
            break
        if len(telefono) > 20 or not telefono.isdigit():
            print("Teléfono inválido. Debe contener solo números y máximo 20 caracteres.")
            continue
        break

    campos = []
    valores = []

    if nombre:
        campos.append("nombre = %s")
        valores.append(nombre)
    if direccion:
        campos.append("direccion = %s")
        valores.append(direccion)
    if correo:
        campos.append("correo = %s")
        valores.append(correo)
    if telefono is not None:
        campos.append("telefono = %s")
        valores.append(telefono)

    if not campos:
        print("No se modificó ningún dato.")
        conn.close()
        return

    query = f"UPDATE clientes SET {', '.join(campos)} WHERE id = %s"
    valores.append(id_cliente)

    try:
        cursor.execute(query, tuple(valores))
        conn.commit()
        print("Cliente actualizado correctamente.")
    except Exception as e:
        print("Error inesperado al actualizar el cliente:", e)

    cursor.close()
    conn.close()

# Borrar cliente con chequeos para no borrar si tiene máquinas asignadas
def borrar_cliente():
    conn = get_connection()
    cursor = conn.cursor()

    while True:
        id_cliente = input("ID del cliente a borrar: ").strip()
        if not id_cliente.isdigit():
            print("ID inválido, debe ser un número.")
            continue
        if not cliente_existe(cursor, id_cliente):
            print("Cliente no encontrado. Intente nuevamente.")
            continue
        break

    cursor.execute("SELECT nombre, direccion, correo, telefono FROM clientes WHERE id = %s", (id_cliente,))
    cliente = cursor.fetchone()
    print("\n--- Datos del cliente ---")
    print(f"Nombre: {cliente[0]}")
    print(f"Dirección: {cliente[1]}")
    print(f"Correo: {cliente[2]}")
    print(f"Teléfono: {cliente[3] if cliente[3] else '(sin teléfono)'}")

    cursor.execute("SELECT COUNT(*) FROM maquinas_alquiler WHERE id_cliente = %s", (id_cliente,))
    cantidad = cursor.fetchone()[0]
    if cantidad > 0:
        print(f"\nEste cliente tiene {cantidad} máquina(s) asignada(s). No se puede eliminar hasta liberar esas máquinas.")
        cursor.close()
        conn.close()
        return

    while True:
        confirm = input(f"\n¿Seguro que desea borrar el cliente {id_cliente}? (s/n): ").strip().lower()
        if confirm in ['s', 'n']:
            break
        print("Entrada inválida. Debe ser 's' o 'n'.")

    if confirm != 's':
        print("Operación cancelada.")
        cursor.close()
        conn.close()
        return

    try:
        cursor.execute("DELETE FROM clientes WHERE id = %s", (id_cliente,))
        conn.commit()
        print("Cliente borrado correctamente.")
    except Exception as e:
        print("Error al borrar el cliente:", e)

    cursor.close()
    conn.close()

# Listar máquinas disponibles para asignar
def listar_maquinas_disponibles(cursor):
    cursor.execute("""
        SELECT m.id, m.modelo 
        FROM maquinas m 
        LEFT JOIN maquinas_alquiler ma ON m.id = ma.id_maquina
        WHERE ma.id_maquina IS NULL
        ORDER BY m.id
    """)
    maquinas = cursor.fetchall()
    if maquinas:
        print("\nMáquinas disponibles:")
        for m in maquinas:
            print(f"ID: {m[0]} | Modelo: {m[1]}")
    else:
        print("No hay máquinas disponibles.")
    return maquinas

# Asignar máquina a cliente, con confirmación
def asignar_maquina_a_cliente():
    conn = get_connection()
    cursor = conn.cursor()

    while True:
        id_cliente = input("ID del cliente a asignar máquina: ").strip()
        if not id_cliente.isdigit():
            print("ID inválido, debe ser un número.")
            continue
        if not cliente_existe(cursor, id_cliente):
            print("Cliente no encontrado. Intente nuevamente.")
            continue
        break

    maquinas = listar_maquinas_disponibles(cursor)
    if not maquinas:
        cursor.close()
        conn.close()
        return

    while True:
        id_maquina = input("ID de la máquina a asignar: ").strip()
        if not id_maquina.isdigit():
            print("ID máquina debe ser numérico.")
            continue
        id_maquina = int(id_maquina)
        if id_maquina not in [m[0] for m in maquinas]:
            print("Máquina no disponible. Elija otra.")
            continue
        break

    while True:
        costo_str = input("Costo mensual del alquiler (en pesos): ").strip().replace(",", ".")
        try:
            costo = float(costo_str)
            if costo <= 0:
                print("El costo debe ser mayor a cero.")
                continue
            break
        except:
            print("Debe ingresar un número válido para el costo.")

    fecha_hoy = date.today()

    print(f"\nResumen de asignación:")
    print(f"Cliente ID: {id_cliente}")
    print(f"Máquina ID: {id_maquina}")
    print(f"Costo mensual: ${costo:.2f}")
    print(f"Fecha alquiler: {fecha_hoy}")
    while True:
        confirmar = input("¿Confirmar asignación? (s/n): ").strip().lower()
        if confirmar in ('s', 'n'):
            break
        print("Entrada inválida. Debe ser 's' o 'n'.")

    if confirmar != 's':
        print("Asignación cancelada.")
        cursor.close()
        conn.close()
        return

    try:
        cursor.execute("""
            INSERT INTO maquinas_alquiler (id_maquina, id_cliente, costo_alquiler_mensual, fecha_alquiler)
            VALUES (%s, %s, %s, %s)
        """, (id_maquina, id_cliente, costo, fecha_hoy))
        conn.commit()
        print(f"Máquina {id_maquina} asignada al cliente {id_cliente} correctamente.")
    except Exception as e:
        print("Error al asignar la máquina:", e)

    cursor.close()
    conn.close()

# Menú para gestionar clientes
def menu_clientes():
    while True:
        print("""
--- Gestión de Clientes ---
1. Listar clientes
2. Agregar cliente
3. Editar cliente
4. Borrar cliente
5. Asignar máquina a cliente
6. Salir
        """)
        opcion = input("Seleccione una opción: ").strip()
        if opcion == '1':
            listar_clientes()
        elif opcion == '2':
            agregar_cliente()
        elif opcion == '3':
            editar_cliente()
        elif opcion == '4':
            borrar_cliente()
        elif opcion == '5':
            asignar_maquina_a_cliente()
        elif opcion == '6':
            print("Saliendo...")
            break
        else:
            print("Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
    menu_clientes()
