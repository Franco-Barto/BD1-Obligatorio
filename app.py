from flask import Flask, render_template, request, redirect, flash
from mantenimiento_app import asignar_mantenimiento_form
from db import get_connection

app = Flask(__name__)
app.secret_key = "clave_secreta"


@app.route("/", methods=["GET", "POST"])
def asignar():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, modelo FROM maquinas")
    maquinas = cursor.fetchall()

    cursor.execute("SELECT id, nombre, apellido FROM tecnicos")
    tecnicos = cursor.fetchall()

    if request.method == "POST":
        resultado = asignar_mantenimiento_form(request.form, conn)
        if resultado["status"] == "ok":
            flash("Mantenimiento asignado correctamente")
        else:
            flash(f"⚠️ {resultado['error']}")
        return redirect("/")

    return render_template("asignar.html", maquinas=maquinas, tecnicos=tecnicos)

if __name__ == "__main__":
    app.run(debug=True)