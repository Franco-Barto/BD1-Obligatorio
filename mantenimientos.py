from db import get_connection
from datetime import datetime, date, time, timedelta

# Funciones auxiliares para formatear fechas y horas
def formatear_fecha_ddmmyyyy(fecha_str):
    if len(fecha_str) != 8 or not fecha_str.isdigit():
        return None
    return f"{fecha_str[4:8]}-{fecha_str[2:4]}-{fecha_str[0:2]}"

def formatear_hora(hora_str):
    if len(hora_str) != 4 or not hora_str.isdigit():
        return None
    return f"{hora_str[0:2]}:{hora_str[2:4]}"

def timedelta_a_time(td):
    segundos = td.total_seconds()
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    return time(horas, minutos)

# Confirmación estándar para preguntas s/n
def confirmar_entrada(prompt):
    while True:
        entrada = input(prompt).strip().lower()
        if entrada in ['s', 'n']:
            return entrada
        print("Entrada inválida. Debe ser 's' o 'n'.")

# Validaciones básicas de existencia en la base de datos
def tecnico_existe(cursor, id_tecnico):
    try:
        id_int = int(id_tecnico)
    except:
        return False
    cursor.execute("SELECT COUNT(*) FROM tecnicos WHERE id = %s", (id_int,))
    return cursor.fetchone()[0] > 0

def maquina_existe(cursor, id_maquina):
    try:
        id_int = int(id_maquina)
    except:
        return False
    cursor.execute("SELECT COUNT(*) FROM maquinas WHERE id = %s", (id_int,))
    return cursor.fetchone()[0] > 0

def cliente_existe(cursor, id_cliente):
    try:
        id_int = int(id_cliente)
    except:
        return False
    cursor.execute("SELECT COUNT(*) FROM clientes WHERE id = %s", (id_int,))
    return cursor.fetchone()[0] > 0

# Validar disponibilidad del técnico para una fecha y hora
def tecnico_disponible(cursor, id_tecnico, fecha, hora):
    if isinstance(hora, timedelta):
        hora = (datetime.min + hora).time()
    elif isinstance(hora, str):
        try:
            hora = datetime.strptime(hora, "%H:%M").time()
        except:
            return False

    dia_semana = fecha.weekday()
    cursor.execute("""
        SELECT hora_ingreso, hora_salida
        FROM horario_tecnicos
        WHERE id_tecnico = %s AND dia_semana = %s
    """, (id_tecnico, dia_semana))
    horario = cursor.fetchone()
    if not horario:
        return False
    hora_ingreso, hora_salida = horario
    if isinstance(hora_ingreso, timedelta):
        hora_ingreso = timedelta_a_time(hora_ingreso)
    if isinstance(hora_salida, timedelta):
        hora_salida = timedelta_a_time(hora_salida)

    limite_salida = (datetime.combine(date.min, hora_salida) - timedelta(minutes=45)).time()
    if not (hora_ingreso <= hora <= limite_salida):
        return False

    inicio = datetime.combine(fecha, hora)
    fin = inicio + timedelta(minutes=45)

    cursor.execute("""
        SELECT COUNT(*)
        FROM mantenimientos
        WHERE id_tecnico = %s AND fecha = %s AND (
            (hora >= %s AND hora < %s) OR
            (hora < %s AND ADDTIME(hora, '00:45:00') > %s)
        )
    """, (id_tecnico, fecha, hora, fin.time(), hora, hora))
    count = cursor.fetchone()[0]

    return count == 0

# Opción 1: Consultar mantenimientos con filtros
def consultar_mantenimientos():
    conn = get_connection()
    cursor = conn.cursor()

    print("\n--- CONSULTAR MANTENIMIENTOS ---")
    print("Puede aplicar uno o más filtros combinados. Deje vacío para omitir.")

    while True:
        id_tec = input("ID del técnico: ").strip()
        if id_tec == "":
            id_tec = None
            break
        elif tecnico_existe(cursor, id_tec):
            id_tec = int(id_tec)
            break
        else:
            print("Técnico no existe. Intente nuevamente.")

    while True:
        id_maq = input("ID de la máquina: ").strip()
        if id_maq == "":
            id_maq = None
            break
        elif maquina_existe(cursor, id_maq):
            id_maq = int(id_maq)
            break
        else:
            print("Máquina no existe. Intente nuevamente.")

    while True:
        fecha_desde_raw = input("Fecha desde (DDMMYYYY, vacío para omitir): ").strip()
        if fecha_desde_raw == "":
            fecha_desde = None
            break
        fecha_desde = formatear_fecha_ddmmyyyy(fecha_desde_raw)
        if fecha_desde:
            try:
                fecha_desde = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
                break
            except ValueError:
                print("Fecha inválida.")
        else:
            print("Fecha inválida.")

    while True:
        fecha_hasta_raw = input("Fecha hasta (DDMMYYYY, vacío para omitir): ").strip()
        if fecha_hasta_raw == "":
            fecha_hasta = None
            break
        fecha_hasta = formatear_fecha_ddmmyyyy(fecha_hasta_raw)
        if fecha_hasta:
            try:
                fecha_hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d").date()
                if fecha_desde and fecha_hasta < fecha_desde:
                    print("Fecha hasta no puede ser anterior a fecha desde.")
                    continue
                break
            except ValueError:
                print("Fecha inválida.")
        else:
            print("Fecha inválida.")

    while True:
        hora_raw = input("Hora (HHMM, vacío para omitir): ").strip()
        if hora_raw == "":
            hora = None
            break
        hora_formateada = formatear_hora(hora_raw)
        if hora_formateada:
            try:
                hora = datetime.strptime(hora_formateada, "%H:%M").time()
                break
            except ValueError:
                print("Hora inválida.")
        else:
            print("Hora inválida.")

    condiciones = []
    valores = []

    if id_tec is not None:
        condiciones.append("m.id_tecnico = %s")
        valores.append(id_tec)
    if id_maq is not None:
        condiciones.append("m.id_maquina = %s")
        valores.append(id_maq)
    if fecha_desde and fecha_hasta:
        condiciones.append("m.fecha BETWEEN %s AND %s")
        valores.extend([fecha_desde, fecha_hasta])
    elif fecha_desde:
        condiciones.append("m.fecha >= %s")
        valores.append(fecha_desde)
    elif fecha_hasta:
        condiciones.append("m.fecha <= %s")
        valores.append(fecha_hasta)
    if hora is not None:
        condiciones.append("m.hora = %s")
        valores.append(hora)

    query = """
        SELECT m.id, m.tipo, m.fecha, m.hora, m.observaciones,
               t.id, t.nombre, t.apellido,
               ma.id, ma.modelo,
               c.id, c.nombre, c.direccion
        FROM mantenimientos m
        JOIN tecnicos t ON m.id_tecnico = t.id
        JOIN maquinas ma ON m.id_maquina = ma.id
        JOIN maquinas_alquiler ma_alq ON ma_alq.id_maquina = ma.id
        JOIN clientes c ON ma_alq.id_cliente = c.id
    """

    if condiciones:
        query += " WHERE " + " AND ".join(condiciones)
    query += " ORDER BY m.fecha, m.hora"

    cursor.execute(query, tuple(valores))
    resultados = cursor.fetchall()

    if resultados:
        print("\n--- Resultados encontrados ---")
        for r in resultados:
            (id_m, tipo, fecha, hora_td, obs,
             id_tec, nom_tec, ape_tec,
             id_maq, modelo,
             id_cli, nom_cli, dir_cli) = r

            fecha_str = fecha.strftime("%d/%m/%Y") if isinstance(fecha, date) else str(fecha)
            hora_str = (datetime.min + hora_td).time().strftime("%H:%M") if isinstance(hora_td, timedelta) else str(hora_td)

            print(f"""
ID mantenimiento: {id_m}
Técnico:           {id_tec} - {nom_tec} {ape_tec}
Máquina:           {id_maq} - {modelo}
Cliente:           {id_cli} - {nom_cli} ({dir_cli})
Tipo:              {tipo}
Fecha:             {fecha_str}
Hora:              {hora_str}
Observaciones:     {obs or '(sin observaciones)'}
------------------------------""")
    else:
        print("No se encontraron resultados.")

    cursor.close()
    conn.close()

# Opción 2: Editar o cancelar mantenimientos
def editar_mantenimiento():
    conn = get_connection()
    cursor = conn.cursor()

    while True:
        id_m = input("Ingrese ID del mantenimiento a editar: ").strip()
        if not id_m.isdigit():
            print("ID debe ser numérico. Intente nuevamente.")
            continue
        cursor.execute("""
                       SELECT m.id,
                              m.tipo,
                              m.fecha,
                              m.hora,
                              m.observaciones,
                              t.id,
                              t.nombre,
                              t.apellido,
                              ma.id,
                              ma.modelo,
                              c.id,
                              c.nombre,
                              c.direccion
                       FROM mantenimientos m
                                JOIN tecnicos t ON m.id_tecnico = t.id
                                JOIN maquinas ma ON m.id_maquina = ma.id
                                JOIN maquinas_alquiler ma_alq ON ma_alq.id_maquina = ma.id
                                JOIN clientes c ON ma_alq.id_cliente = c.id
                       WHERE m.id = %s
                       """, (id_m,))
        mantenimiento = cursor.fetchone()
        if not mantenimiento:
            print("Mantenimiento no encontrado. Intente nuevamente.")
            continue
        break

    (id_m, tipo, fecha, hora_td, obs,
     id_tec, nom_tec, ape_tec,
     id_maq, modelo_maq,
     id_cli, nom_cli, dir_cli) = mantenimiento

    fecha_str = fecha.strftime("%d/%m/%Y") if isinstance(fecha, date) else str(fecha)
    hora_str = (datetime.min + hora_td).time().strftime("%H:%M") if isinstance(hora_td, timedelta) else str(hora_td)

    print(f"""
Datos del mantenimiento seleccionado:
ID: {id_m}
Tipo: {tipo}
Fecha: {fecha_str}
Hora: {hora_str}
Observaciones: {obs or '(sin observaciones)'}
Técnico: {nom_tec} {ape_tec} (ID: {id_tec})
Máquina: {modelo_maq} (ID: {id_maq})
Cliente: {nom_cli}, {dir_cli} (ID: {id_cli})
""")

    print("--- Opciones ---")
    print("1. Cambiar técnico")
    print("2. Cambiar fecha y hora")
    print("3. Cancelar mantenimiento")

    while True:
        opcion = input("Seleccione: ").strip()
        if opcion in ['1','2','3']:
            break
        print("Opción inválida. Intente de nuevo.")

    if opcion == '1':
        intentos = 0
        max_intentos = 3  # por ejemplo, 3 intentos para elegir técnico disponible

        while intentos < max_intentos:
            nuevo_id = input("Nuevo ID de técnico (o 'salir' para cancelar): ").strip()
            if nuevo_id.lower() == 'salir':
                print("Cambio de técnico cancelado.")
                break
            if not tecnico_existe(cursor, nuevo_id):
                print("Técnico no existe. Intente nuevamente.")
                intentos += 1
                continue
            nuevo_id_int = int(nuevo_id)

            # obtener hora del mantenimiento actual
            if isinstance(hora_td, timedelta):
                hora_val = (datetime.min + hora_td).time()
            elif isinstance(hora_td, time):
                hora_val = hora_td
            else:
                try:
                    hora_val = datetime.strptime(str(hora_td), "%H:%M:%S").time()
                except:
                    print("Hora del mantenimiento inválida.")
                    return

            if not tecnico_disponible(cursor, nuevo_id_int, fecha, hora_val):
                print("Técnico no está disponible en la fecha y hora actuales.")
                intentos += 1
                continue

            if confirmar_entrada("Confirmar cambio de técnico? (s/n): ") == 's':
                cursor.execute("UPDATE mantenimientos SET id_tecnico = %s WHERE id = %s", (nuevo_id_int, id_m))
                conn.commit()
                print("Técnico actualizado correctamente.")
                break
            else:
                print("Cambio cancelado.")
                break

        else:
            print("Se alcanzó el número máximo de intentos. Operación cancelada.")


    elif opcion == '2':
        hoy = date.today()
        while True:
            fecha_nueva_raw = input("Nueva fecha (DDMMYYYY): ").strip()
            f = formatear_fecha_ddmmyyyy(fecha_nueva_raw)
            if not f:
                print("Fecha inválida. Intente nuevamente.")
                continue
            fecha_nueva = datetime.strptime(f, "%Y-%m-%d").date()
            if fecha_nueva < hoy:
                print("La fecha no puede ser anterior a hoy.")
                continue
            break

        while True:
            hora_nueva_raw = input("Nueva hora (HHMM): ").strip()
            h = formatear_hora(hora_nueva_raw)
            if not h:
                print("Hora inválida. Intente nuevamente.")
                continue
            hora_nueva = datetime.strptime(h, "%H:%M").time()
            break

        if not tecnico_disponible(cursor, id_tec, fecha_nueva, hora_nueva):
            print("El técnico no está disponible en la nueva fecha y hora.")
            return

        if confirmar_entrada("Confirmar cambio de fecha y hora? (s/n): ") == 's':
            cursor.execute("UPDATE mantenimientos SET fecha = %s, hora = %s WHERE id = %s",
                           (fecha_nueva, hora_nueva, id_m))
            conn.commit()
            print("Fecha y hora actualizadas correctamente.")
        else:
            print("Cambio cancelado.")

    elif opcion == '3':
        if confirmar_entrada("¿Seguro que desea cancelar? (s/n): ") == 's':
            cursor.execute("DELETE FROM mantenimientos WHERE id = %s", (id_m,))
            conn.commit()
            print("Mantenimiento cancelado.")
        else:
            print("Cancelación rechazada.")

    cursor.close()
    conn.close()

# Opción 3: Asignar nuevo mantenimiento
def obtener_fecha_hora_y_tecnicos(cursor):
    hoy = date.today()
    limite_anual = hoy + timedelta(days=365)
    while True:
        while True:
            fecha_raw = input("\nFecha (DDMMYYYY, sin guiones): ").strip()
            fecha_formateada = formatear_fecha_ddmmyyyy(fecha_raw)
            if fecha_formateada is None:
                print("Formato inválido. Use DDMMYYYY.")
                continue
            try:
                fecha = datetime.strptime(fecha_formateada, "%Y-%m-%d").date()
                if not (hoy <= fecha <= limite_anual):
                    print(f"Fecha fuera del rango permitido ({hoy} a {limite_anual}).")
                    continue
                break
            except ValueError:
                print("Fecha inválida.")

        while True:
            hora_raw = input("Hora (HHMM, sin dos puntos): ").strip()
            hora_formateada = formatear_hora(hora_raw)
            if hora_formateada is None:
                print("Formato inválido. Use HHMM.")
                continue
            try:
                hora = datetime.strptime(hora_formateada, "%H:%M").time()
                if fecha == hoy and hora <= datetime.now().time():
                    print("La hora debe ser futura si la fecha es hoy.")
                    continue
                break
            except ValueError:
                print("Hora inválida.")

        inicio_nuevo = datetime.combine(fecha, hora)
        fin_bloqueo = inicio_nuevo + timedelta(minutes=45)

        cursor.execute("""
            SELECT t.id, t.nombre, t.apellido, ht.hora_ingreso, ht.hora_salida
            FROM tecnicos t
            JOIN horario_tecnicos ht ON t.id = ht.id_tecnico
            WHERE ht.dia_semana = %s
        """, (fecha.weekday(),))
        tecnicos = cursor.fetchall()

        disponibles = []
        for t in tecnicos:
            id_tec, nombre, apellido, ingreso, salida = t
            if isinstance(ingreso, timedelta):
                ingreso = timedelta_a_time(ingreso)
            if isinstance(salida, timedelta):
                salida = timedelta_a_time(salida)
            hora_limite = (datetime.combine(date(2000,1,1), salida) - timedelta(minutes=45)).time()
            if not (ingreso <= hora <= hora_limite):
                continue

            cursor.execute("""
                SELECT COUNT(*)
                FROM mantenimientos
                WHERE id_tecnico = %s AND fecha = %s AND (
                    (hora >= %s AND hora < %s) OR
                    (hora < %s AND ADDTIME(hora, '00:45:00') > %s)
                )
            """, (id_tec, fecha, hora, fin_bloqueo.time(), hora, hora))
            if cursor.fetchone()[0] == 0:
                disponibles.append((id_tec, nombre, apellido))

        if disponibles:
            return fecha, hora, disponibles
        else:
            print("\nNo hay técnicos disponibles en ese horario. Ingrese otra fecha y hora.")

def asignar_mantenimiento():
    conn = get_connection()
    cursor = conn.cursor()

    print("\n--- Asignación de mantenimiento ---")

    fecha, hora, disponibles = obtener_fecha_hora_y_tecnicos(cursor)

    print("\nTécnicos disponibles:")
    for t in disponibles:
        print(f"ID: {t[0]} | Nombre: {t[1]} {t[2]}")

    cursor.execute("SELECT id, modelo FROM maquinas")
    maquinas = cursor.fetchall()
    if not maquinas:
        print("No hay máquinas registradas.")
        cursor.close()
        conn.close()
        return

    print("\nMáquinas disponibles:")
    for m in maquinas:
        print(f"ID: {m[0]} | Modelo: {m[1]}")

    while True:
        id_maquina_str = input("Ingrese ID de la máquina: ").strip()
        if not id_maquina_str.isdigit():
            print("ID máquina debe ser numérico.")
            continue
        id_maquina = int(id_maquina_str)
        if not maquina_existe(cursor, id_maquina):
            print("Máquina no existe. Intente nuevamente.")
            continue
        break

    while True:
        id_tecnico_str = input("Ingrese ID del técnico: ").strip()
        if not id_tecnico_str.isdigit():
            print("ID técnico debe ser numérico.")
            continue
        id_tecnico = int(id_tecnico_str)
        if id_tecnico not in [t[0] for t in disponibles]:
            print("Técnico no está disponible. Elija otro.")
            continue
        break

    tipos_validos = ['preventivo', 'correctivo', 'predictivo']

    while True:
        tipo = input("Tipo de mantenimiento (preventivo, correctivo, predictivo): ").strip().lower()
        if tipo in tipos_validos:
            break
        print("Tipo inválido. Debe ser 'preventivo', 'correctivo' o 'predictivo'.")

    while True:
        observaciones = input("Observaciones (máx 100 caracteres, opcional): ").strip()
        if len(observaciones) <= 100:
            break
        print("Observaciones demasiado largas.")

    print("\nResumen del mantenimiento a asignar:")
    print(f"Fecha: {fecha.strftime('%d/%m/%Y')}")
    print(f"Hora: {hora.strftime('%H:%M')}")
    print(f"Técnico: {id_tecnico}")
    print(f"Máquina: {id_maquina}")
    print(f"Tipo: {tipo}")
    print(f"Observaciones: {observaciones or '(sin observaciones)'}")

    if confirmar_entrada("Confirmar asignación? (s/n): ") == 's':
        cursor.execute("""
            INSERT INTO mantenimientos (tipo, fecha, hora, observaciones, id_tecnico, id_maquina)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (tipo, fecha, hora, observaciones if observaciones else None, id_tecnico, id_maquina))
        conn.commit()
        print("Mantenimiento asignado correctamente.")
    else:
        print("Asignación cancelada.")

    cursor.close()
    conn.close()

# Función principal para menú
def menu():
    while True:
        print("\n--- Gestión de Mantenimientos ---")
        print("1. Consultar mantenimientos")
        print("2. Editar o cancelar mantenimiento")
        print("3. Asignar mantenimiento")
        print("4. Salir")

        opcion = input("Seleccione una opción: ").strip()
        if opcion == '1':
            consultar_mantenimientos()
        elif opcion == '2':
            editar_mantenimiento()
        elif opcion == '3':
            asignar_mantenimiento()
        elif opcion == '4':
            print("Saliendo...")
            break
        else:
            print("Opción inválida. Intente nuevamente.")

if __name__ == "__main__":
    menu()
