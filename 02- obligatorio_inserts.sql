
Use obligatorio;

INSERT INTO login (correo, contraseña, es_administrador) VALUES
('juan.perez@gmail.com', Sha2('contrasena123',224), TRUE),
('maria.lopez@gmail.com', Sha2('clave456',224), FALSE),
('ana.morales@gmail.com', Sha2('pass789',224), FALSE);


INSERT INTO proveedores (nombre, contacto, tipo) VALUES
('Soluciones Industriales S.A.', '091234567', 'maquinaria'),
('Insumos VerdeMar', '092345678', 'insumo'),
('Servicios Técnicos Montevideo', '093456789', 'servicio');


INSERT INTO insumos (id,descripcion, tipo, precio_unitario, id_proveedor) VALUES
(1,'Aceite lubricante', 'lubricante', 1250, 1),
(2,'Bolsa de tornillos', 'material', 450, 2),
(3,'Filtros de aire ', 'repuesto', 780, 2);


INSERT INTO clientes (nombre, direccion, telefono, correo) VALUES
('Constructora El Faro', 'Av. de las Artes 2345', '094567890', 'contacto.elfaro@gmail.com'),
('Empresa Textil La Estrella', 'Bulevar Sarandí 1120', '095678901', 'ventas.laestrella@gmail.com'),
('Logística Rápida', 'Callejón del Viento 657', '096789012', 'info.logistica@gmail.com');


INSERT INTO maquinas (modelo, id_cliente, ubicacion_cliente, costo_alquiler_mensual) VALUES
('X-100', 1, 'Planta Central, Av. de las Artes 2345', 35000),
('R-3000', 2, 'Sucursal Norte, Bulevar Sarandí 1120', 28000),
('M-200', 3, 'Depósito Principal, Callejón del Viento 657', 32000);


INSERT INTO registro_consumo (id_maquina, id_insumo, fecha, cantidad_usada) VALUES
(1, 1, '2025-06-01', 16),
(2, 2, '2025-06-05', 200),
(3, 3, '2025-06-10', 5);


INSERT INTO tecnicos (id, ci, nombre, apellido, telefono) VALUES
(1,52645678, 'Carlos', 'González', '099123456'),
(2,57654321, 'Lucía', 'Fernández', '098234567'),
(3,51223344, 'Marcos', 'Silva', '097345678');

INSERT INTO horario_tecnicos (id_tecnico, dia_semana, hora_ingreso, hora_salida) VALUES
(1, 0, '09:00', '18:00'),
(1, 1, '09:00', '18:00'),
(1, 2, '09:00', '18:00'),
(1, 3, '09:00', '18:00'),
(1, 4, '09:00', '18:00'),
(2, 1, '10:00', '16:00'),
(2, 2, '10:00', '16:00'),
(2, 3, '10:00', '16:00'),
(2, 4, '10:00', '16:00'),
(2, 5, '10:00', '16:00'),
(3, 0, '08:00', '14:00'),
(3, 2, '08:00', '14:00'),
(3, 4, '08:00', '14:00');


INSERT INTO mantenimientos (id_maquina, id_tecnico, tipo, fecha, hora, observaciones) VALUES
(1, 1, 'preventivo', '2025-06-15', '09:30:00', 'Cambio de aceite y revisión general.'),
(2, 2, 'correctivo', '2025-06-20' ,'14:00:00', 'Reparación del motor principal.'),
(3, 3, 'preventivo', '2025-06-22','11:15:00', 'Limpieza y ajuste de piezas móviles.');


