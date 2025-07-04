import mysql.connector

def validar_largo(texto, campo, max_len):
    if len(texto) > max_len:
        print(f"Error: {campo} excede el largo máximo de {max_len} caracteres.")
        return False
    return True
def listar_insumos(config):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()
    cursor.execute("SELECT id, descripcion, tipo, precio_unitario, id_proveedor FROM insumos ORDER BY id")
    insumos = cursor.fetchall()
    if insumos:
        print("\n--- Lista de Insumos ---")
        for i in insumos:
            print(f"ID: {i[0]} | Descripción: {i[1]} | Tipo: {i[2]} | Precio unitario: {i[3]} | ID Proveedor: {i[4]}")
    else:
        print("No hay insumos registrados.")
    cursor.close()
    cnx.close()


def pedir_id_proveedor():
    while True:
        id_prov = pedir_entero("ID del proveedor: ", "ID del proveedor")
        if proveedor_existe(id_prov):
            return id_prov
        print(f"Error: El proveedor con ID {id_prov} no existe.")

def pedir_precio_unitario():
    while True:
        entrada = input("Precio unitario: ").strip().replace(",", ".")
        try:
            precio = float(entrada)
            if precio < 0:
                print("El precio debe ser un número positivo.")
            else:
                return precio
        except ValueError:
            print("Por favor, ingrese un número válido para el precio.")

def pedir_entero(mensaje, campo_nombre):
    while True:
        entrada = input(mensaje).strip()
        if entrada.isdigit():
            return int(entrada)
        print(f"Por favor, ingrese un número entero válido para {campo_nombre}.")

def pedir_id_insumo(config):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()

    while True:
        entrada = input("ID del insumo a modificar (Enter para cancelar): ").strip()
        if entrada == "":
            cursor.close()
            cnx.close()
            return None
        if not entrada.isdigit():
            print("Por favor, ingrese un número entero válido para el ID del insumo.")
            continue

        id_insumo = int(entrada)
        cursor.execute("SELECT COUNT(*) FROM insumos WHERE id = %s", (id_insumo,))
        if cursor.fetchone()[0] == 0:
            print(f"No se encontró un insumo con ID {id_insumo}.")
            continue
        cursor.close()
        cnx.close()
        return id_insumo

def proveedor_existe(config,id_proveedor):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()
    cursor.execute("SELECT COUNT(*) FROM proveedores WHERE id = %s", (id_proveedor,))
    existe = cursor.fetchone()[0] > 0
    cursor.close()
    cnx.close()
    return existe

def confirmar_entrada(prompt):
    while True:
        entrada = input(prompt).strip().lower()
        if entrada in ['s', 'n']:
            return entrada
        print("Entrada inválida. Debe ser 's' o 'n'.")

def agregar_insumo(descripcion, tipo, precio_unitario, id_proveedor,config):
    if not descripcion or len(descripcion.strip()) == 0:
        print("Error: La descripción es obligatoria.")
        return
    if not validar_largo(tipo, "tipo", 50):
        return
    if not proveedor_existe(id_proveedor):
        print(f"Error: El proveedor con ID {id_proveedor} no existe.")
        return

    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()
    sql = """
        INSERT INTO insumos (descripcion, tipo, precio_unitario, id_proveedor)
        VALUES (%s, %s, %s, %s)
    """
    valores = (descripcion, tipo, precio_unitario, id_proveedor)
    try:
        cursor.execute(sql, valores)
        conexion.commit()
        print("Insumo agregado con éxito.")
    except Exception as e:
        print("Error al agregar insumo:", e)
    finally:
        cursor.close()
        cnx.close()

def modificar_insumo(id_insumo):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()

    # Consultar datos actuales
    cursor.execute("SELECT descripcion, tipo, precio_unitario, id_proveedor FROM insumos WHERE id = %s", (id_insumo,))
    fila = cursor.fetchone()

    if not fila:
        print(f"No se encontró un insumo con ID {id_insumo}.")
        cursor.close()
        cnx.close()
        return

    descripcion_actual, tipo_actual, precio_actual, proveedor_actual = fila
    print("Datos actuales:")
    print(f"Descripción: {descripcion_actual}")
    print(f"Tipo: {tipo_actual}")
    print(f"Precio unitario: {precio_actual:.2f}")
    print(f"ID proveedor: {proveedor_actual}")

    # Pedir nuevos datos, permitiendo mantener los actuales
    nueva_descripcion = input("Nueva descripción (Enter para mantener actual): ").strip()
    if not nueva_descripcion:
        nueva_descripcion = descripcion_actual

    nuevo_tipo = input("Nuevo tipo (Enter para mantener actual): ").strip()
    if not nuevo_tipo:
        nuevo_tipo = tipo_actual
    elif len(nuevo_tipo) > 50:
        print("Error: tipo excede el largo máximo de 50 caracteres.")
        cursor.close()
        cnx.close()
        return

    # Precio: validar input o mantener actual
    while True:
        entrada_precio = input("Nuevo precio unitario (Enter para mantener actual): ").strip().replace(",", ".")
        if not entrada_precio:
            nuevo_precio = precio_actual
            break
        try:
            nuevo_precio = float(entrada_precio)
            if nuevo_precio < 0:
                print("El precio debe ser un número positivo.")
            else:
                break
        except ValueError:
            print("Precio inválido. Ingrese un número válido.")

    # ID proveedor: validar existencia o mantener actual
    while True:
        entrada_prov = input("Nuevo ID del proveedor (Enter para mantener actual): ").strip()
        if not entrada_prov:
            nuevo_proveedor = proveedor_actual
            break
        if not entrada_prov.isdigit():
            print("Por favor, ingrese un número entero válido para ID del proveedor.")
            continue
        nuevo_proveedor = int(entrada_prov)

        # Validar que exista el proveedor
        cursor.execute("SELECT COUNT(*) FROM proveedores WHERE id = %s", (nuevo_proveedor,))
        if cursor.fetchone()[0] == 0:
            print(f"Error: El proveedor con ID {nuevo_proveedor} no existe.")
        else:
            break

    # Mostrar resumen antes de confirmar
    print("\nDatos a modificar:")
    print(f"Descripción: {nueva_descripcion}")
    print(f"Tipo: {nuevo_tipo}")
    print(f"Precio unitario: {nuevo_precio:.2f}")
    print(f"ID proveedor: {nuevo_proveedor}")

    confirmacion = confirmar_entrada("¿Confirma la modificación? (s/n): ")
    if confirmacion == 's':
        # proceder con la modificación
        print("Modificación confirmada.")
    else:
        print("Modificación cancelada.")

    # Ejecutar actualización
    try:
        sql = """
        UPDATE insumos
        SET descripcion = %s, tipo = %s, precio_unitario = %s, id_proveedor = %s
        WHERE id = %s
        """
        cursor.execute(sql, (nueva_descripcion, nuevo_tipo, nuevo_precio, nuevo_proveedor, id_insumo))
        cnx.commit()
        print("Insumo modificado correctamente.")
    except Exception as e:
        print("Error al modificar insumo:", e)
    finally:
        cursor.close()
        cnx.close()

def eliminar_insumo(id_insumo,config):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()

    cursor.execute("SELECT descripcion FROM insumos WHERE id = %s", (id_insumo,))
    fila = cursor.fetchone()
    if not fila:
        print("No se encontró el insumo con ese ID.")
        cursor.close()
        conexion.close()
        return

    print(f"Vas a eliminar el insumo: {fila[0]} (ID: {id_insumo})")

    confirmar = confirmar_entrada("¿Confirma la eliminación? (s/n): ")
    if confirmar != "s":
        print("Eliminación cancelada.")
        cursor.close()
        cnx.close()
        return

    try:
        cursor.execute("DELETE FROM insumos WHERE id = %s", (id_insumo,))
        cnx.commit()
        print("Insumo eliminado correctamente.")
    except Exception as e:
        print("Error al eliminar insumo:", e)
    finally:
        cursor.close()
        cnx.close()


def listar_insumos(config):
    print("\n--- Listar Insumos ---")
    filtro_desc = input("Filtrar por descripción (Enter para no filtrar): ").strip()
    filtro_tipo = input("Filtrar por tipo (Enter para no filtrar): ").strip()

    # Bucle para pedir ID de proveedor válido o vacío
    while True:
        filtro_proveedor = input("Filtrar por ID de proveedor (Enter para no filtrar): ").strip()
        if filtro_proveedor == "":
            filtro_proveedor = None
            break
        elif filtro_proveedor.isdigit():
            filtro_proveedor = int(filtro_proveedor)
            break
        else:
            print("ID de proveedor inválido. Debe ser un número entero o dejar vacío.")

    condiciones = []
    parametros = []

    if filtro_desc:
        condiciones.append("descripcion LIKE %s")
        parametros.append(f"%{filtro_desc}%")
    if filtro_tipo:
        condiciones.append("tipo LIKE %s")
        parametros.append(f"%{filtro_tipo}%")
    if filtro_proveedor is not None:
        condiciones.append("id_proveedor = %s")
        parametros.append(filtro_proveedor)

    sql = "SELECT id, descripcion, tipo, precio_unitario, id_proveedor FROM insumos"
    if condiciones:
        sql += " WHERE " + " AND ".join(condiciones)
    sql += " ORDER BY id"

    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()
    cursor.execute(sql, tuple(parametros))
    insumos = cursor.fetchall()

    if insumos:
        print("\n--- Insumos encontrados ---")
        for i in insumos:
            print(f"ID: {i[0]} | Descripción: {i[1]} | Tipo: {i[2]} | Precio unitario: {i[3]} | ID Proveedor: {i[4]}")
    else:
        print("No se encontraron insumos con esos filtros.")
    cursor.close()
    cnx.close()


# Menú interactivo
def menu_insumos(config):
    while True:
        print("\n--- MENÚ DE INSUMOS ---")
        print("1. Agregar insumo")
        print("2. Modificar insumo")
        print("3. Eliminar insumo")
        print("4. Listar insumos")
        print("5. Salir")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            desc = input("Descripción: ").strip()
            tipo = input("Tipo: ").strip()
            precio = pedir_precio_unitario()
            proveedor = pedir_id_proveedor()
            agregar_insumo(desc, tipo, precio, proveedor,config)

        if opcion == "2":
             id_mod = pedir_id_insumo(config)
             if id_mod is not None:
                 modificar_insumo(id_mod,config)
             else:
               print("Modificación cancelada por el usuario.")

        elif opcion == "3":
            listar_insumos(config)
            id_borrar = pedir_entero("ID del insumo a eliminar: ", "ID del insumo")
            eliminar_insumo(id_borrar,config)

        elif opcion == "4":
           listar_insumos(config)

        elif opcion == "5":

           print("Saliendo...")
           break

        else:
            print("Opción inválida. Seleccione un número entre 1 y 5.")
