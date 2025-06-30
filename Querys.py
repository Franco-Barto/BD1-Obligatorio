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
    query=f"Select c.*,sum(costo_alquiler_mensual+precio_unitario*ifnull(cantidad_usada,0)) as gastos_mensuales from (select * from registro_consumo where fecha between '{año}-{mes}-01' and '{año}-{mes}-{max_dia(año,mes)}') as rc right join maquinas as m on rc.id_maquina = m.id left join insumos as i on i.id = rc.id_insumo join clientes as c on c.id = m.id_cliente group by id_cliente"
    print(query)
    cursor.execute(query)
    return cursor.fetchall()

def top_insumos(cantidad,order_by='consumos',config):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()
    query=f"select i.id, sum(ifnull(cantidad_usada,0)) as consumos, sum(ifnull(cantidad_usada,0)*precio_unitario) as costos from insumos as i left join registro_consumo as rc on i.id = rc.id_insumo group by i.id order by {order_by} limit {cantidad}"
    cursor.execute(query)
    return cursor.fetchall()

config = Login.login("juan.perez@gmail.com","contrasena123")
tot=tot_mensual(2025,7,config)
print(tot)
top=top_insumos(20,config)
print(top)
