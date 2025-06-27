import mysql.connector

config = {
  'user': 'login',
  'password': 'password',
  'host': '127.0.0.1',
  'database': 'obligatorio'
}

def login(Correo, Contraseña):
    cnx = mysql.connector.connect(**config)
    cursor =cnx.cursor()
    query = "SELECT * FROM login WHERE (correo = '{}' AND contraseña = (SELECT sha2('{}',224)))".format(Correo, Contraseña)
    cursor.execute(query)
    usuario = cursor.fetchone()
    if usuario:
        if usuario[2]:
            config.update({'user':'admin','password':'blablabla'})
        else:
            config.update({'user':'noadmin','password':'blebleble'})
    else:
        config.update({'user':'login','password':'password'})
    cnx.close()

#Correo = input("Correo: ")
#Contraseña = input("Contraseña: ")
#login(Correo, Contraseña)
#print(config)

login("juan.perez@gmail.com","contrasena123")
print(config)
login("juan.perez@gmail.com","jijija")
print(config)
login("juan.perez@gmaila.com","jijija")
print(config)
login("ana.morales@gmail.com","pass789")
print(config)
