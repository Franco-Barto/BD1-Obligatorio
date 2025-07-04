import mysql.connector

invalid_characters="-' "

def login(Correo, Contraseña):
    config = {
        'user': 'login',
        'password': 'password',
        'host': '127.0.0.1',
        'database': 'obligatorio'
    }
    admin = False
    id_cliente = 0
    for char in invalid_characters:
        if (char in Correo) or (char in Contraseña):
            print("Correo y/o Contraseña incorrectos")
            return config
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()
    query = "SELECT * FROM login WHERE (correo = '{}' AND contraseña = (SELECT sha2('{}',224)))".format(Correo, Contraseña)
    cursor.execute(query)
    usuario = cursor.fetchone()
    if usuario:
        query = "SELECT * FROM admins WHERE correo = '{}'".format(Correo)
        cursor.execute(query)
        es_admin = cursor.fetchone()
        if es_admin:
            config.update({'user':'admin','password':'blablabla'})
            admin = True
        else:
            config.update({'user':'noadmin','password':'blebleble'})
        cnx.close()
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        query = f"SELECT id FROM clientes WHERE (correo = '{Correo}')"
        cursor.execute(query)
        id_querry = cursor.fetchone()
        if id_querry:
            id_cliente = id_querry[0]
    else:
        print("Correo y/o Contraseña incorrectos")
    cnx.close()
    return config, admin, id_cliente

def crear_usuario(Correo, Contraseña):
    config = {
        'user': 'login',
        'password': 'password',
        'host': '127.0.0.1',
        'database': 'obligatorio'
    }
    for char in invalid_characters:
        if (char in Correo) or (char in Contraseña):
            print("Correo y/o Contraseña no pueden tener espacios, guiones o apóstrofos")
            return config
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    query = "SELECT * FROM login WHERE (correo = '{}')".format(Correo)
    cursor.execute(query)
    usuario = cursor.fetchone()
    if usuario:
        print("Usuario existente")
        return config
    query = f"INSERT INTO login VALUES ('{Correo}',(SELECT sha2('{Contraseña}',224)))"
    cursor.execute(query)
    cnx.commit()
    cnx.close()
    return login(Correo, Contraseña)

def menu_login():
    while True:
        print("""
--- MÓDULO DE LOGIN ---
1. Ingresar usuario
2. Crear usuario
3. Salir
""")
        opcion = input("Seleccione una opción: ").strip()
        if opcion == '1':
            Correo = input("Ingresar correo: ").strip()
            Contraseña = input("Ingresar contraseña: ")
            config, admin, id_cliente = login(Correo,Contraseña)
        elif opcion == '2':
            Correo = input("Ingresar correo: ").strip()
            Contraseña = input("Ingresar contraseña: ")
            config, admin, id_cliente = crear_usuario(Correo,Contraseña)
        elif opcion == '3':
            print("Saliendo del módulo de login.")
            return config, admin, id_cliente
        else:
            print("Opción inválida. Intente nuevamente.")

if __name__ == "__main__":
    config = login("juan.perez@gmail.com","contrasena123")
    print(config)
    config = login("juan.perez@gmail.com","jijija")
    print(config)
    config = login("juan.perez@gmaila.com","jijija")
    print(config)
    config = login("ana.morales@gmail.com","pass789")
    print(config)
    config = login("ana.m orales@gmail.com","pass789")
    print(config)
    print(crear_usuario("prueba6","puntoycoma"))