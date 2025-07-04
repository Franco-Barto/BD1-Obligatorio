import mysql.connector
import Login

def es_bisiesto(año):
  if (año % 4 == 0 and año % 100 != 0) or (año % 400 == 0):
    return True
  else:
    return False

def max_dia(año,mes):
    if mes==2:
        if es_bisiesto(año):
            return 29
        else:
            return 28
    elif mes in [1,3,5,7,8,10,12]:
        return 31
    else:
        return 30

def tot_mensual(año,mes,config):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()
    query=f"Select c.*,sum(m.costo_alquiler_mensual+ifnull(precio_unitario,0)*ifnull(cantidad_usada,0)) as gastos_mensuales from (select * from registro_consumo where fecha between '{año}-{mes}-01' and '{año}-{mes}-{max_dia(año,mes)}') as rc right join (select * from maquinas_alquiler where fecha_alquiler<'{año}-{mes}-01') as m on rc.id_maquina = m.id_maquina left join insumos as i on i.id = rc.id_insumo join clientes as c on c.id = m.id_cliente group by id_cliente"
    cursor.execute(query)
    tot=cursor.fetchall()
    cnx.close()
    return tot

def top_insumos(config,cantidad=1,order_by='consumos',año=0,mes=0):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()
    if mes:
        query = f"select i.id, sum(ifnull(cantidad_usada,0)) as consumos, sum(ifnull(cantidad_usada,0)*precio_unitario) as costos from insumos as i left join registro_consumo as rc on i.id = rc.id_insumo where fecha between '{año}-{mes}-01' and '{año}-{mes}-{max_dia(año,mes)}' group by i.id order by {order_by} limit {cantidad}"
    elif año:
        query = f"select i.id, sum(ifnull(cantidad_usada,0)) as consumos, sum(ifnull(cantidad_usada,0)*precio_unitario) as costos from insumos as i left join registro_consumo as rc on i.id = rc.id_insumo where fecha between '{año}-01-01' and '{año}-12-31' group by i.id order by {order_by} limit {cantidad}"
    else:
        query=f"select i.id, sum(ifnull(cantidad_usada,0)) as consumos, sum(ifnull(cantidad_usada,0)*precio_unitario) as costos from insumos as i left join registro_consumo as rc on i.id = rc.id_insumo group by i.id order by {order_by} limit {cantidad}"
    cursor.execute(query)
    top=cursor.fetchall()
    cnx.close()
    return top

def top_tecnicos(config,catidad=1,año=0,mes=0):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()
    if mes:
        query = f"select t.*, cantidad from tecnicos as t join (select id_tecnico, count(*) as cantidad from mantenimientos group by id_tecnico where fecha between '{año}-{mes}-01' and '{año}-{mes}-{max_dia(año, mes)}' order by cantidad desc limit {catidad}) as ma on t.id = ma.id_tecnico"
    elif año:
        query = f"select t.*, cantidad from tecnicos as t join (select id_tecnico, count(*) as cantidad from mantenimientos where fecha between '{año}-01-01' and '{año}-12-31' group by id_tecnico order by cantidad desc limit {catidad}) as ma on t.id = ma.id_tecnico"
    else:
        query = f"select t.*, cantidad from tecnicos as t join (select id_tecnico, count(*) as cantidad from mantenimientos group by id_tecnico order by cantidad desc limit {catidad}) as ma on t.id = ma.id_tecnico"
    cursor.execute(query)
    top=cursor.fetchall()
    cnx.close()
    return top

def top_clientes(config,cantidad=1):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()
    query = f"select clientes.*,cantidad from clientes join (select id_cliente, count(*) as cantidad from maquinas_alquiler group by id_cliente order by cantidad desc limit {cantidad}) as s on clientes.id = s.id_cliente"
    cursor.execute(query)
    top=cursor.fetchall()
    cnx.close()
    return top

def menu_inf(config,admin):
    if  admin:
        print("Solo admins tienen acceso.")
        while True:
            print("""
        --- Gestión de Máquinas ---
        1. Total mensual a cobrar
        2. Top insumo
        3. Técnico con más mantenimientos
        4. Cliente con mayor cantidad de maquinas
        5. Salir
        """)
            opcion = input("Seleccione una opción: ").strip()
            if opcion == '1':
                año=int(input("Año:"))
                mes=int(input("Mes:"))
                tot_mensual(año,mes,config)
            elif opcion == '2':
                top_insumos(config)
            elif opcion == '3':
                top_tecnicos(config)
            elif opcion == '4':
                top_clientes(config)
            elif opcion == '5':
                print("Saliendo...")
                break
            else:
                print("Opción inválida.")
    else:
        print("Solo admins tienen acceso.")

if __name__ == '__main__':
    config, admin, id_cliente = Login.login("juan.perez@gmail.com","contrasena123")
    tot=tot_mensual(2025,8,config)
    print(tot)
    top=top_insumos(config,2)
    print(top)
    top=top_clientes(config,2)
    print(top)
    top=top_tecnicos(config,2)
    print(top)

