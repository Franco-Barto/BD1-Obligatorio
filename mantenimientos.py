# Realizamos la conexión
import mysql.connector
from datetime import datetime, date, time, timedelta


# Definimos las funciones que implementa nuestro programa

# Formato de fecha y hora, para evitar probblemas con lo que el usuario ingrese
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

# Validación de existencias en la base de datos

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

def maquinas_de_cliente(cursor, admin, id_cliente):
    if admin:
        cursor.execute(f"select id from maquinas")
        maquinas = cursor.fetchall()
    else:
        cursor.execute(f"select id from maquinas where id_cliente = {id_cliente}")
        maquinas = cursor.fetchall()
    lista=[]
    for i in maquinas:
        lista.append(str(i[0]))
    if len(lista)==0:
        lista.append("0")
    return lista


def cliente_existe(cursor, id_cliente):
    try:
        id_int = int(id_cliente)
    except:
        return False
    cursor.execute("SELECT COUNT(*) FROM clientes WHERE id = %s", (id_int,))
    return cursor.fetchone()[0] > 0


def tecnico_disponible(cursor, id_tecnico, fecha, hora):
    # Convierte hora a time si viene como timedelta o str
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
                   WHERE id_tecnico = %s
                     AND dia_semana = %s
                   """, (id_tecnico, dia_semana))
    horario = cursor.fetchone()
    if not horario:
        return False
    hora_ingreso, hora_salida = horario
    if isinstance(hora_ingreso, timedelta):
        hora_ingreso = (datetime.min + hora_ingreso).time()
    if isinstance(hora_salida, timedelta):
        hora_salida = (datetime.min + hora_salida).time()

    limite_salida = (datetime.combine(date.min, hora_salida) - timedelta(minutes=45)).time()
    if not (hora_ingreso <= hora <= limite_salida):
        return False

    inicio = datetime.combine(fecha, hora)
    fin = inicio + timedelta(minutes=45)
    # Se chequea si existe algún mantenimiento que se cruce con el intervalo
    cursor.execute("""
                   SELECT COUNT(*)
                   FROM mantenimientos
                   WHERE id_tecnico = %s
                     AND fecha = %s
                     AND (
                       (hora >= %s AND hora < %s) OR
                       (hora < %s AND ADDTIME(hora, '00:45:00') > %s)
                       )
                   """, (id_tecnico, fecha, hora, fin.time(), hora, hora))
    count = cursor.fetchone()[0]

    return count == 0


# Opcion 1: Consulta de mantenimientos

def consultar_mantenimientos(config, admin, id_cliente):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()

    print("\n--- CONSULTAR MANTENIMIENTOS ---")
    print("Puede aplicar uno o más filtros combinados. Deje vacío para omitir.")

    # Validación de técnico
    while True:
        id_tec = input("ID del técnico: ").strip()
        if id_tec == "":
            id_tec = None
            break
        if tecnico_existe(cursor, id_tec):
            id_tec = int(id_tec)
            break
        print("Técnico no existe. Intente nuevamente.")

    # Validación de máquina
    while True:
        id_maqs = []
        id_maq = input("ID de la máquina: ").strip()
        if id_maq == "":
            id_maqs = maquinas_de_cliente(cursor, admin, id_cliente)
            break
        if maquina_existe(cursor, id_maq) and int(id_maq) in maquinas_de_cliente(cursor, admin, id_cliente):
            id_maqs.append(int(id_maq))
            break
        print("Máquina no existe. Intente nuevamente.")

    # Decidimos permitir seleccionar rangos de fechas
    hoy = date.today()
    while True:
        fecha_desde_raw = input("Fecha desde (DDMMYYYY, vacío para omitir): ").strip()
        if fecha_desde_raw == "":
            fecha_desde = None
            break
        f = formatear_fecha_ddmmyyyy(fecha_desde_raw)
        if not f:
            print("Fecha inválida. Intente nuevamente.")
            continue
        fecha_desde = datetime.strptime(f, "%Y-%m-%d").date()
        if fecha_desde < hoy:
            print("La fecha desde no puede ser anterior a hoy.")
            continue
        break

    while True:
        fecha_hasta_raw = input("Fecha hasta (DDMMYYYY, vacío para omitir): ").strip()
        if fecha_hasta_raw == "":
            fecha_hasta = None
            break
        f = formatear_fecha_ddmmyyyy(fecha_hasta_raw)
        if not f:
            print("Fecha inválida. Intente nuevamente.")
            continue
        fecha_hasta = datetime.strptime(f, "%Y-%m-%d").date()
        if fecha_desde and fecha_hasta < fecha_desde:
            print("La fecha hasta no puede ser anterior a la fecha desde.")
            continue
        break

    # Hora
    while True:
        hora_raw = input("Hora (HHMM, vacío para omitir): ").strip()
        if hora_raw == "":
            hora = None
            break
        h = formatear_hora(hora_raw)
        if not h:
            print("Hora inválida. Intente nuevamente.")
            continue
        hora = datetime.strptime(h, "%H:%M").time()
        break

    # Consulta
    condiciones = []
    valores = []
    maq_str = []

    if id_tec is not None:
        condiciones.append("m.id_tecnico = %s")
        valores.append(id_tec)
    for i in id_maqs:
        maq_str.append("m.id_maquina = %s")
        valores.append(i)
    condiciones.append("(" +" OR ".join(maq_str)+")")
    if fecha_desde is not None:
        condiciones.append("m.fecha >= %s")
        valores.append(fecha_desde)
    if fecha_hasta is not None:
        condiciones.append("m.fecha <= %s")
        valores.append(fecha_hasta)
    if hora is not None:
        condiciones.append("m.hora = %s")
        valores.append(hora)

    query = """
            SELECT m.id, \
                   m.tipo, \
                   m.fecha, \
                   m.hora, \
                   m.observaciones,
                   t.id, \
                   t.nombre, \
                   t.apellido,
                   ma.id, \
                   ma.modelo,
                   c.id, \
                   c.nombre, \
                   c.direccion
            FROM mantenimientos m
                     JOIN tecnicos t ON m.id_tecnico = t.id
                     JOIN maquinas ma ON m.id_maquina = ma.id
                     JOIN clientes c ON ma.id_cliente = c.id \
            """

    if condiciones:
        query += " WHERE " + " AND ".join(condiciones)
    query += " ORDER BY m.fecha, m.hora"

    cursor.execute(query, tuple(valores))
    resultados = cursor.fetchall()
    
# Definimos el output 
    if resultados:
        print("\n--- Resultados encontrados ---")
        for r in resultados:
            (id_m, tipo, fecha, hora_td, obs,
             id_tec, nombre_tec, apellido_tec,
             id_maq, modelo_maq,
             id_cli, nombre_cli, direccion_cli) = r

            fecha_str = fecha.strftime("%d/%m/%Y") if isinstance(fecha, date) else str(fecha)
            hora_str = (datetime.min + hora_td).time().strftime("%H:%M") if isinstance(hora_td, timedelta) else str(
                hora_td)

            print(f"""
ID mantenimiento: {id_m}
Tipo:             {tipo}
Fecha:            {fecha_str}
Hora:             {hora_str}
Observaciones:    {obs or '(sin observaciones)'}
-- Técnico --
ID:               {id_tec}
Nombre:           {nombre_tec} {apellido_tec}
-- Máquina --
ID:               {id_maq}
Modelo:           {modelo_maq}
-- Cliente --
ID:               {id_cli}
Nombre:           {nombre_cli}
Dirección:        {direccion_cli}
------------------------------
""")
    else:
        print("No se encontraron resultados.")

    cnx.close()
    
    
# Opción 2: Edición/cancelamiento de mantenimientos
def editar_mantenimiento(config, admin, id_cliente):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()

    # Pedimos el id del mantenimiento y validamos la existencia
    while True:
        id_m = input("Ingrese ID del mantenimiento a editar: ").strip()
        if not id_m.isdigit():
            print("ID debe ser numérico. Intente nuevamente.")
            continue
        query="""
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
                                JOIN clientes c ON ma.id_cliente = c.id
                       WHERE m.id = %s
                       """
        id_maqs = maquinas_de_cliente(cursor, admin, id_cliente)
        valores = [id_m]
        maq_str = []
        for i in id_maqs:
            maq_str.append("m.id_maquina = %s")
            valores.append(i)
        query+=(" AND (" + " OR ".join(maq_str) + ")")
        cursor.execute(query, tuple(valores))
        mantenimiento = cursor.fetchone()
        if not mantenimiento:
            print("Mantenimiento no encontrado. Intente nuevamente.")
            continue
        break

    (id_m, tipo, fecha, hora_td, obs,
     id_tec, nombre_tec, apellido_tec,
     id_maq, modelo_maq,
     id_cli, nombre_cli, direccion_cli) = mantenimiento

    fecha_str = fecha.strftime("%d/%m/%Y") if isinstance(fecha, date) else str(fecha)
    hora_str = (datetime.min + hora_td).time().strftime("%H:%M") if isinstance(hora_td, timedelta) else str(hora_td)

# Definimos el output
    print(f"""
Datos del mantenimiento seleccionado:
ID: {id_m}
Tipo: {tipo}
Fecha: {fecha_str}
Hora: {hora_str}
Observaciones: {obs or '(sin observaciones)'}
Técnico: {nombre_tec} {apellido_tec} (ID: {id_tec})
Máquina: {modelo_maq} (ID: {id_maq})
Cliente: {nombre_cli}, {direccion_cli} (ID: {id_cli})
""")

    print("--- Opciones ---")
    print("1. Cambiar técnico")
    print("2. Cambiar fecha y hora")
    print("3. Cancelar mantenimiento")

    while True:
        opcion = input("Seleccione: ").strip()
        if opcion not in ['1', '2', '3']:
            print("Opción inválida. Intente de nuevo.")
            continue
        break

    if opcion == "1":
        # Cambiar técnico
        while True:
            nuevo_id = input("Nuevo ID de técnico: ").strip()
            if not tecnico_existe(cursor, nuevo_id):
                print("Técnico no existe. Intente nuevamente.")
                continue
            nuevo_id_int = int(nuevo_id)

            # Formato de hora para evitar incosistencias
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
                
            # Validamos la disponibilidad del técnico
            if not tecnico_disponible(cursor, nuevo_id_int, fecha, hora_val):
                print("Técnico no está disponible en la fecha y hora actuales.")
                continue

            confirm = input("Confirmar cambio de técnico? (s/n): ").strip().lower()
            if confirm == 's':
                cursor.execute("UPDATE mantenimientos SET id_tecnico = %s WHERE id = %s", (nuevo_id_int, id_m))
                cnx.commit()
                print("Técnico actualizado correctamente.")
                break
            else:
                print("Cambio cancelado.")
                break

    elif opcion == "2":
        # Cambiar fecha y hora
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

        # Validamos que el técnico esté disponible en la fecha y hora nuevas
        if not tecnico_disponible(cursor, id_tec, fecha_nueva, hora_nueva):
            print("El técnico no está disponible en la nueva fecha y hora.")
            return

        confirm = input("Confirmar cambio de fecha y hora? (s/n): ").strip().lower()
        if confirm == 's':
            cursor.execute("UPDATE mantenimientos SET fecha = %s, hora = %s WHERE id = %s",
                           (fecha_nueva, hora_nueva, id_m))
            cnx.commit()
            print("Fecha y hora actualizadas correctamente.")
        else:
            print("Cambio cancelado.")

# Cancelar mantenimientos
    
    elif opcion == "3":

        while True:

            confirm = input("¿Seguro que desea cancelar? (s/n): ").strip().lower()

            if confirm == 's':

                cursor.execute("DELETE FROM mantenimientos WHERE id = %s", (id_m,))

                print("Mantenimiento cancelado.")

                cnx.commit()

                cursor.close()

                cnx.close()

                return

            elif confirm == 'n':

                print("Cancelación rechazada.")

                cursor.close()

                cnx.close()

                return

            else:

                print("Entrada inválida. Ingrese 's' o 'n'.")
    cnx.commit()
    print("Actualización realizada.")
    cnx.close()
    
# Opción 3: Asignación de mantenimientos

def obtener_fecha_hora_y_tecnicos(cursor):
    hoy = date.today()
    limite_anual = hoy + timedelta(days=365)
    while True:
        # Fecha
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

        # Hora
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

        # Buscamos técnicos disponibles en ese día y horario
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
            hora_limite = (datetime.combine(date(2000, 1, 1), salida) - timedelta(minutes=45)).time()
            if not (ingreso <= hora <= hora_limite):
                continue

            # Verificamos que no tenga mantenimiento que se superponga
            cursor.execute("""
                           SELECT COUNT(*)
                           FROM mantenimientos
                           WHERE id_tecnico = %s
                             AND fecha = %s
                             AND (
                               (hora >= %s AND hora < %s) OR
                               (hora < %s AND ADDTIME(hora, '00:45:00') > %s)
                               )
                           """, (id_tec, fecha, hora, fin_bloqueo.time(), hora, hora))
            if cursor.fetchone()[0] == 0:
                disponibles.append((id_tec, nombre, apellido))

        if disponibles:
            return fecha, hora, disponibles
        else:
            print("\n No hay técnicos disponibles en ese horario. Ingrese otra fecha y hora.")


def asignar_mantenimiento(config, admin, id_cliente):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()

    print("\n--- Asignación de mantenimiento ---")

    fecha, hora, disponibles = obtener_fecha_hora_y_tecnicos(cursor)

    print("\nTécnicos disponibles:")
    for t in disponibles:
        print(f"ID: {t[0]} | Nombre: {t[1]} {t[2]}")

    # Mostrar máquinas
    query="SELECT id, modelo FROM maquinas"
    id_maqs = maquinas_de_cliente(cursor, admin, id_cliente)
    maq_str = []
    valores = []
    for i in id_maqs:
        maq_str.append("id = %s")
        valores.append(i)
    query += (" WHERE (" + " OR ".join(maq_str) + ")")
    cursor.execute(query, tuple(valores))
    maquinas = cursor.fetchall()
    if not maquinas:
        print("No hay máquinas registradas.")
        return

    print("\nMáquinas disponibles:")
    for m in maquinas:
        print(f"ID: {m[0]} | Modelo: {m[1]}")

    while True:
        id_maquina_str = input("Ingrese ID de la máquina: ").strip()
        if not id_maquina_str.isdigit():
            print("ID máquina debe ser numérico.")
            continue
        if id_maquina_str not in id_maqs:
            print("ID máquina debe ser de una de las maquinas disponibles.")
        id_maquina = int(id_maquina_str)
        cursor.execute("SELECT COUNT(*) FROM maquinas WHERE id = %s", (id_maquina,))
        if cursor.fetchone()[0] == 0:
            print("Máquina no existe. Intente nuevamente.")
            continue
        break

    while True:
        id_tecnico_str = input("Ingrese ID del técnico: ").strip()
        if not id_tecnico_str.isdigit():
            print("ID técnico debe ser numérico.")
            continue
        id_tecnico = int(id_tecnico_str)
        if not any(t[0] == id_tecnico for t in disponibles):
            print("Técnico no está disponible en ese horario.")
            continue
        break

    tipo = input("Tipo de mantenimiento (preventivo/correctivo/predictivo): ").strip().lower()
    while tipo not in ["preventivo", "correctivo", "predictivo"]:
        print("Tipo inválido. Debe ser 'preventivo','correctivo' o 'predictivo'.")
        tipo = input("Tipo de mantenimiento (preventivo/correctivo/predictivo): ").strip().lower()

    observaciones = input("Observaciones (opcional): ").strip()

    print(f"\nConfirme asignación:")
    print(f"Fecha: {fecha.strftime('%d/%m/%Y')}")
    print(f"Hora: {hora.strftime('%H:%M')}")
    print(f"Técnico ID: {id_tecnico}")
    print(f"Máquina ID: {id_maquina}")
    print(f"Tipo: {tipo}")
    print(f"Observaciones: {observaciones or '(ninguna)'}")

    confirmar = input("¿Guardar mantenimiento? (s/n): ").strip().lower()
    if confirmar == 's':
        cursor.execute("""
                       INSERT INTO mantenimientos (id_maquina, id_tecnico, tipo, fecha, hora, observaciones)
                       VALUES (%s, %s, %s, %s, %s, %s)
                       """, (id_maquina, id_tecnico, tipo, fecha, hora, observaciones or None))
        cnx.commit()
        print("Mantenimiento asignado correctamente.")
    else:
        print("Asignación cancelada.")

    cnx.close()
    
# Menú principal
def main(config, admin, id_cliente):
    while True:
        print("\n--- MENÚ DE MANTENIMIENTOS ---")
        print("1. Consultar mantenimientos")
        print("2. Editar / cancelar mantenimiento")
        print("3. Asignar nuevo mantenimiento")
        print("4. Salir")
        op = input("Seleccione opción: ").strip()

        if op == "1":
            consultar_mantenimientos(config, admin, id_cliente)
        elif op == "2":
            editar_mantenimiento(config, admin, id_cliente)
        elif op == "3":
            asignar_mantenimiento(config, admin, id_cliente)
        elif op == "4":
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    config = {
        'user': 'login',
        'password': 'password',
        'host': '127.0.0.1',
        'database': 'obligatorio'
    }
    config.update({'user': 'admin', 'password': 'blablabla'})
    main(config, False, 1)
