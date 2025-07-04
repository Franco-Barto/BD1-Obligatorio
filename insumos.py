def listar_insumos():
    print("\n--- Listar Insumos ---")
    filtro_desc = input("Filtrar por descripción (Enter para no filtrar): ").strip()
    filtro_tipo = input("Filtrar por tipo (Enter para no filtrar): ").strip()

    # Bucle para pedir ID de proveedor válido o vacío
    while True:
        filtro_proveedor = input("Filtrar por ID de proveedor (Enter para no filtrar): ").strip()
        if filtro_proveedor == "":
            filtro_proveedor = None
            break
        elif filtro_proveedor.isdigit():
            filtro_proveedor = int(filtro_proveedor)
            break
        else:
            print("ID de proveedor inválido. Debe ser un número entero o dejar vacío.")

    condiciones = []
    parametros = []

    if filtro_desc:
        condiciones.append("descripcion LIKE %s")
        parametros.append(f"%{filtro_desc}%")
    if filtro_tipo:
        condiciones.append("tipo LIKE %s")
        parametros.append(f"%{filtro_tipo}%")
    if filtro_proveedor is not None:
        condiciones.append("id_proveedor = %s")
        parametros.append(filtro_proveedor)

    sql = "SELECT id, descripcion, tipo, precio_unitario, id_proveedor FROM insumos"
    if condiciones:
        sql += " WHERE " + " AND ".join(condiciones)
    sql += " ORDER BY id"

    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute(sql, tuple(parametros))
    insumos = cursor.fetchall()

    if insumos:
        print("\n--- Insumos encontrados ---")
        for i in insumos:
            print(f"ID: {i[0]} | Descripción: {i[1]} | Tipo: {i[2]} | Precio unitario: {i[3]} | ID Proveedor: {i[4]}")
    else:
        print("No se encontraron insumos con esos filtros.")
    cursor.close()
    conexion.close()
