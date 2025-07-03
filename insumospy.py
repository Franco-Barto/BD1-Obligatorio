import mysql.connector

# Conexión a la base de datos
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="obligatorio"
)
cursor = conexion.cursor()

# Función para validar el largo máximo de texto
def validar_largo(campo, nombre_campo, max_largo):
    if len(campo) > max_largo:
        print(f"Error: el campo '{nombre_campo}' no puede tener más de {max_largo} caracteres. Lo que ingresaste tiene {len(campo)}.")
        return False
    return True

# Función para agregar un insumo
def agregar_insumo(descripcion, tipo, precio_unitario, id_proveedor):
    if not validar_largo(tipo, "tipo", 50):
        return

    sql = "INSERT INTO insumos (descripcion, tipo, precio_unitario, id_proveedor) VALUES (%s, %s, %s, %s)"
    valores = (descripcion, tipo, precio_unitario, id_proveedor)
    cursor.execute(sql, valores)
    conexion.commit()
    print("Insumo agregado con éxito.")

# Función para modificar un insumo
def modificar_insumo(id_insumo, nueva_descripcion, nuevo_tipo, nuevo_precio_unitario):
    if not validar_largo(nuevo_tipo, "tipo", 50):
        return

    sql = "UPDATE insumos SET descripcion = %s, tipo = %s, precio_unitario = %s WHERE id = %s"
    valores = (nueva_descripcion, nuevo_tipo, nuevo_precio_unitario, id_insumo)
    cursor.execute(sql, valores)
    conexion.commit()
    print("Insumo modificado correctamente.")

# Función para eliminar un insumo
def eliminar_insumo(id_insumo):
    sql = "DELETE FROM insumos WHERE id = %s"
    cursor.execute(sql, (id_insumo,))
    conexion.commit()
    print("Insumo eliminado correctamente.")

# Menú interactivo por consola
while True:
    print("\n--- MENÚ DE INSUMOS ---")
    print("1. Agregar insumo")
    print("2. Modificar insumo")
    print("3. Eliminar insumo")
    print("4. Salir")
    opcion = input("Elegí una opción: ")

    if opcion == "1":
        desc = input("Descripción: ")
        tipo = input("Tipo: ")
        precio = float(input("Precio unitario: "))
        proveedor = int(input("ID del proveedor: "))
        agregar_insumo(desc, tipo, precio, proveedor)

    elif opcion == "2":
        id_mod = int(input("ID del insumo a modificar: "))
        nueva_desc = input("Nueva descripción: ")
        nuevo_tipo = input("Nuevo tipo: ")
        nuevo_precio = float(input("Nuevo precio unitario: "))
        modificar_insumo(id_mod, nueva_desc, nuevo_tipo, nuevo_precio)

    elif opcion == "3":
        id_borrar = int(input("ID del insumo a eliminar: "))
        eliminar_insumo(id_borrar)

    elif opcion == "4":
        print("Saliendo del programa...")
        break

    else:
        print("Opción inválida. Elegí entre 1 y 4.")

# Cierre de conexión
cursor.close()
conexion.close()
