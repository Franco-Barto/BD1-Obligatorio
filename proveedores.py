import mysql.connector

def validar_largo(texto, campo, max_len):
    if len(texto) > max_len:
        print(f"Error: {campo} excede el largo máximo de {max_len} caracteres ({max_len}).")
        return False
    return True

def pedir_entero(mensaje, campo_nombre):
    while True:
        entrada = input(mensaje).strip()
        if entrada.isdigit():
            return int(entrada)
        print(f"Por favor, ingrese un número entero válido para {campo_nombre}.")

def confirmar_entrada(prompt):
    while True:
        entrada = input(prompt).strip().lower()
        if entrada in ['s', 'n']:
            return entrada
        print("Entrada inválida. Debe ser 's' o 'n'.")

def listar_proveedores(filtro_nombre=None):
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        if filtro_nombre:
            sql = "SELECT id, nombre, direccion, telefono FROM proveedores WHERE nombre LIKE %s ORDER BY id"
            cursor.execute(sql, (f"%{filtro_nombre}%",))
        else:
            sql = "SELECT id, nombre, direccion, telefono FROM proveedores ORDER BY id"
            cursor.execute(sql)
        proveedores = cursor.fetchall()
        if proveedores:
            print("\n--- Lista de Proveedores ---")
            for p in proveedores:
                print(f"ID: {p[0]} | Nombre: {p[1]} | Dirección: {p[2]} | Teléfono: {p[3]}")
        else:
            print("No hay proveedores registrados.")
    except Error as e:
        print("Error al listar proveedores:", e)
    finally:
        cursor.close()
        cnx.close()

def proveedor_existe(id_proveedor):
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        cursor.execute("SELECT COUNT(*) FROM proveedores WHERE id = %s", (id_proveedor,))
        existe = cursor.fetchone()[0] > 0
        return existe
    except Error as e:
        print("Error al verificar proveedor:", e)
        return False
    finally:
        cursor.close()
        cnx.close()

def agregar_proveedor(nombre, direccion, telefono):
    if not nombre.strip():
        print("Error: El nombre es obligatorio.")
        return
    if not validar_largo(nombre, "nombre", 100):
        return
    if not validar_largo(direccion, "dirección", 200):
        return
    if not validar_largo(telefono, "teléfono", 20):
        return

    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        sql = "INSERT INTO proveedores (nombre, direccion, telefono) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nombre, direccion, telefono))
        cnx.commit()
        print("Proveedor agregado con éxito.")
    except Error as e:
        print("Error al agregar proveedor:", e)
    finally:
        cursor.close()
        cnx.close()

def modificar_proveedor(id_proveedor):
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        cursor.execute("SELECT nombre, direccion, telefono FROM proveedores WHERE id = %s", (id_proveedor,))
        fila = cursor.fetchone()
        if not fila:
            print(f"No se encontró un proveedor con ID {id_proveedor}.")
            return

        nombre_actual, direccion_actual, telefono_actual = fila
        print("Datos actuales:")
        print(f"Nombre: {nombre_actual}")
        print(f"Dirección: {direccion_actual}")
        print(f"Teléfono: {telefono_actual}")

        nuevo_nombre = input("Nuevo nombre (Enter para mantener actual): ").strip()
        if not nuevo_nombre:
            nuevo_nombre = nombre_actual
        elif not validar_largo(nuevo_nombre, "nombre", 100):
            return

        nueva_direccion = input("Nueva dirección (Enter para mantener actual): ").strip()
        if not nueva_direccion:
            nueva_direccion = direccion_actual
        elif not validar_largo(nueva_direccion, "dirección", 200):
            return

        nuevo_telefono = input("Nuevo teléfono (Enter para mantener actual): ").strip()
        if not nuevo_telefono:
            nuevo_telefono = telefono_actual
        elif not validar_largo(nuevo_telefono, "teléfono", 20):
            return

        print("\nDatos a modificar:")
        print(f"Nombre: {nuevo_nombre}")
        print(f"Dirección: {nueva_direccion}")
        print(f"Teléfono: {nuevo_telefono}")

        confirmar = confirmar_entrada("¿Confirma la modificación? (s/n): ")
        if confirmar != 's':
            print("Modificación cancelada.")
            return

        sql = "UPDATE proveedores SET nombre = %s, direccion = %s, telefono = %s WHERE id = %s"
        cursor.execute(sql, (nuevo_nombre, nueva_direccion, nuevo_telefono, id_proveedor))
        cnx.commit()
        print("Proveedor modificado correctamente.")
    except Error as e:
        print("Error al modificar proveedor:", e)
    finally:
        cursor.close()
        cnx.close()

def eliminar_proveedor(id_proveedor):
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        cursor.execute("SELECT nombre FROM proveedores WHERE id = %s", (id_proveedor,))
        fila = cursor.fetchone()
        if not fila:
            print(f"No se encontró proveedor con ID {id_proveedor}.")
            return
        print(f"Vas a eliminar el proveedor: {fila[0]} (ID: {id_proveedor})")
        confirmar = confirmar_entrada("¿Confirma la eliminación? (s/n): ")
        if confirmar != 's':
            print("Eliminación cancelada.")
            return
        cursor.execute("DELETE FROM proveedores WHERE id = %s", (id_proveedor,))
        cnx.commit()
        print("Proveedor eliminado correctamente.")
    except Error as e:
        print("Error al eliminar proveedor:", e)
    finally:
        cursor.close()
        cnx.close()

# Menú interactivo
def menu():
    while True:
        print("\n--- MENÚ DE PROVEEDORES ---")
        print("1. Listar proveedores")
        print("2. Agregar proveedor")
        print("3. Modificar proveedor")
        print("4. Eliminar proveedor")
        print("5. Salir")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == '1':
            filtro = input("Filtrar por nombre (Enter para listar todos): ").strip()
            if filtro == "":
                filtro = None
            listar_proveedores(filtro)
        elif opcion == '2':
            nombre = input("Nombre: ").strip()
            direccion = input("Dirección: ").strip()
            telefono = input("Teléfono: ").strip()
            agregar_proveedor(nombre, direccion, telefono)
        elif opcion == '3':
            id_mod = pedir_entero("ID del proveedor a modificar: ", "ID del proveedor")
            modificar_proveedor(id_mod)
        elif opcion == '4':
            id_del = pedir_entero("ID del proveedor a eliminar: ", "ID del proveedor")
            eliminar_proveedor(id_del)
        elif opcion == '5':
            print("Saliendo...")
            break
        else:
            print("Opción inválida. Seleccione un número entre 1 y 5.")

if __name__ == "__main__":
    menu()
