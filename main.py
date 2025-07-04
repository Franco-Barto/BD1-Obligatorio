import Login
import clientes
#import insumospy
import maquinas
import mantenimientos
import Querys
import Técnicos
from Login import menu_login

config = {
        'user': 'login',
        'password': 'password',
        'host': '127.0.0.1',
        'database': 'obligatorio'
    }
admin = False
id_cliente = 0

if __name__ == '__main__':
    while True:
        print("""
        --- MENU PRINCIPAL ---
        1. LOGIN
        2. CLIENTES
        3. MAQUINAS
        4. MANTENIMIENTOS
        5. TECNICOS
        6. INFORMES
        """)
        opcion = input("Seleccione una opción: ").strip()
        if opcion == '1':
            config,admin,id_cliente = Login.menu_login()
        elif opcion == '2':
            clientes.menu_clientes(config)
        elif opcion == '3':
            maquinas.menu_maquinas(config)
        elif opcion == '4':
            mantenimientos.menu_mantenimientos(config,admin,id_cliente)
        elif opcion == '5':
            Técnicos.menu_técnicos(config)
        elif opcion == '6':
            Querys.menu_inf(config,admin)
        else:
            print("Opción inválida.")