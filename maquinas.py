import mysql.connector
from datetime import date

def confirmar_entrada(prompt):
    while True:
        entrada = input(prompt).strip().lower()
        if entrada in ['s', 'n']:
            return entrada
        print("Entrada inválida. Debe ser 's' o 'n'.")

def listar_maquinas(config):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()

    filtro_texto = input("Filtrar por texto en modelo (vacío para todos): ").strip()
    filtro_disp = None
    while True:
        filtro_disp_input = input("Filtrar por disponibilidad? (s=solo disponibles, n=solo no disponibles, vacío=todos): ").strip().lower()
        if filtro_disp_input in ['s', 'n', '']:
            if filtro_disp_input == 's':
                filtro_disp = True
            elif filtro_disp_input == 'n':
                filtro_disp = False
            else:
                filtro_disp = None
            break
        print("Entrada inválida.")

    sql = "SELECT id, modelo, fecha_compra, disponibilidad FROM maquinas"
    condiciones = []
    params = []

    if filtro_texto:
        condiciones.append("modelo LIKE %s")
        params.append(f"%{filtro_texto}%")

    if filtro_disp is not None:
        condiciones.append("disponibilidad = %s")
        params.append(filtro_disp)

    if condiciones:
        sql += " WHERE " + " AND ".join(condiciones)

    sql += " ORDER BY id"

    cursor.execute(sql, tuple(params))
    maquinas = cursor.fetchall()

    if maquinas:
        print("\n--- Listado de máquinas ---")
        for m in maquinas:
            disp = "Disponible" if m[3] else "No disponible"
            fc = m[2].strftime("%Y-%m-%d") if m[2] else "Sin fecha compra"
            print(f"ID: {m[0]} | Modelo: {m[1]} | Fecha compra: {fc} | {disp}")
    else:
        print("No se encontraron máquinas con ese filtro.")

    cursor.close()
    cnx.close()

def agregar_maquina(confi):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()

    while True:
        modelo = input("Modelo de la máquina (max 45 caracteres): ").strip()
        if 0 < len(modelo) <= 45:
            break
        print("Modelo inválido.")

    while True:
        fecha_str = input("Fecha de compra (YYYY-MM-DD, opcional, dejar vacío si no tiene): ").strip()
        if not fecha_str:
            fecha_compra = None
            break
        try:
            fecha_compra = date.fromisoformat(fecha_str)
            break
        except:
            print("Fecha inválida.")

    try:
        cursor.execute("""
            INSERT INTO maquinas (modelo, fecha_compra, disponibilidad) VALUES (%s, %s, TRUE)
        """, (modelo, fecha_compra))
        cnx.commit()
        print("Máquina agregada correctamente.")
    except Exception as e:
        print("Error al agregar máquina:", e)

    cursor.close()
    cnx.close()

def eliminar_maquina(config):

    listar_maquinas(config)

    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()

    while True:
        id_maquina = input("ID de la máquina a eliminar: ").strip()
        if not id_maquina.isdigit():
            print("ID inválido.")
            continue
        id_maquina = int(id_maquina)
        # Verificar existencia
        cursor.execute("SELECT COUNT(*) FROM maquinas WHERE id = %s", (id_maquina,))
        if cursor.fetchone()[0] == 0:
            print("Máquina no encontrada.")
            continue
        # Verificar si está asignada
        cursor.execute("SELECT COUNT(*) FROM maquinas_alquiler WHERE id_maquina = %s", (id_maquina,))
        if cursor.fetchone()[0] > 0:
            print("No se puede eliminar. La máquina está asignada a un cliente.")
            cursor.close()
            cnx.close()
            return
        break

    confirmar = confirmar_entrada(f"¿Seguro que desea eliminar la máquina {id_maquina}? (s/n): ")
    if confirmar != 's':
        print("Operación cancelada.")
        cursor.close()
        cnx.close()
        return

    try:
        cursor.execute("DELETE FROM maquinas WHERE id = %s", (id_maquina,))
        cnx.commit()
        print("Máquina eliminada correctamente.")
    except Exception as e:
        print("Error al eliminar máquina:", e)

    cursor.close()
    cnx.close()

def asignar_maquina(config):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()

    from clientes import cliente_existe, direccion_existe  # Asumiendo que tienes esas funciones

    while True:
        id_cliente = input("ID del cliente para asignar máquina: ").strip()
        if not id_cliente.isdigit() or not cliente_existe(cursor, id_cliente):
            print("Cliente inválido o no existe.")
            continue
        break

    # Listar direcciones del cliente
    cursor.execute("SELECT id, direccion FROM direcciones WHERE id_cliente = %s", (id_cliente,))
    direcciones = cursor.fetchall()
    if not direcciones:
        print("El cliente no tiene direcciones.")
        cursor.close()
        cnx.close()
        return

    print("Direcciones disponibles:")
    for d in direcciones:
        print(f"ID: {d[0]} | Dirección: {d[1]}")

    while True:
        id_direccion = input("ID de dirección para asignar la máquina: ").strip()
        if id_direccion.isdigit() and any(int(id_direccion) == d[0] for d in direcciones):
            id_direccion = int(id_direccion)
            break
        print("Dirección inválida o no pertenece al cliente.")

    # Listar máquinas disponibles
    cursor.execute("SELECT id, modelo FROM maquinas WHERE disponibilidad = TRUE ORDER BY id")
    maquinas = cursor.fetchall()
    if not maquinas:
        print("No hay máquinas disponibles para asignar.")
        cursor.close()
        cnx.close()
        return

    print("Máquinas disponibles:")
    for m in maquinas:
        print(f"ID: {m[0]} | Modelo: {m[1]}")

    while True:
        id_maquina = input("ID de la máquina a asignar: ").strip()
        if id_maquina.isdigit() and int(id_maquina) in [m[0] for m in maquinas]:
            id_maquina = int(id_maquina)
            break
        print("Máquina inválida o no disponible.")

    while True:
        costo_str = input("Costo mensual del alquiler (ej: 1000.50): ").strip().replace(',', '.')
        try:
            costo = float(costo_str)
            if costo > 0:
                break
            print("Debe ser mayor a cero.")
        except:
            print("Costo inválido.")

    fecha_alquiler = date.today()

    confirmar = confirmar_entrada(f"Confirmar asignar máquina {id_maquina} al cliente {id_cliente} en dirección {id_direccion} con costo ${costo:.2f}? (s/n): ")
    if confirmar != 's':
        print("Asignación cancelada.")
        cursor.close()
        cnx.close()
        return

    try:
        cursor.execute("""
            INSERT INTO maquinas_alquiler (id_maquina, id_cliente, id_direccion, costo_alquiler_mensual, fecha_alquiler)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_maquina, id_cliente, id_direccion, costo, fecha_alquiler))
        cursor.execute("UPDATE maquinas SET disponibilidad = FALSE WHERE id = %s", (id_maquina,))
        cnx.commit()
        print("Máquina asignada correctamente.")
    except Exception as e:
        print("Error al asignar máquina:", e)

    cursor.close()
    cnx.close()

def desasignar_maquina(config):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()

    # Listar máquinas asignadas
    cursor.execute("""
        SELECT ma.id_maquina, m.modelo, ma.id_cliente, ma.id_direccion
        FROM maquinas_alquiler ma
        JOIN maquinas m ON ma.id_maquina = m.id
        ORDER BY ma.id_maquina
    """)
    asignadas = cursor.fetchall()
    if not asignadas:
        print("No hay máquinas asignadas.")
        cursor.close()
        cnx.close()
        return

    print("\nMáquinas asignadas:")
    for a in asignadas:
        print(f"ID Máquina: {a[0]} | Modelo: {a[1]} | Cliente ID: {a[2]} | Dirección ID: {a[3]}")

    while True:
        id_maquina = input("ID de la máquina a desasignar: ").strip()
        if id_maquina.isdigit() and int(id_maquina) in [a[0] for a in asignadas]:
            id_maquina = int(id_maquina)
            break
        print("ID inválido o máquina no asignada.")

    confirmar = confirmar_entrada(f"Confirmar desasignar máquina {id_maquina}? (s/n): ")
    if confirmar != 's':
        print("Operación cancelada.")
        cursor.close()
        cnx.close()
        return

    try:
        cursor.execute("DELETE FROM maquinas_alquiler WHERE id_maquina = %s", (id_maquina,))
        cursor.execute("UPDATE maquinas SET disponibilidad = TRUE WHERE id = %s", (id_maquina,))
        cnx.commit()
        print("Máquina desasignada correctamente.")
    except Exception as e:
        print("Error al desasignar máquina:", e)

    cursor.close()
    cnx.close()

def menu_maquinas(config):
    while True:
        print("""
--- Gestión de Máquinas ---
1. Listar máquinas
2. Agregar máquina
3. Eliminar máquina
4. Asignar máquina a cliente
5. Desasignar máquina
6. Salir
""")
        opcion = input("Seleccione una opción: ").strip()
        if opcion == '1':
            listar_maquinas(config)
        elif opcion == '2':
            agregar_maquina(config)
        elif opcion == '3':
            eliminar_maquina(config)
        elif opcion == '4':
            asignar_maquina(config)
        elif opcion == '5':
            desasignar_maquina(config)
        elif opcion == '6':
            print("Saliendo...")
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    menu_maquinas(config)
