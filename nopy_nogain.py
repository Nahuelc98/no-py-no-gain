# Módulo Principal - Punto de Entrada de 'No py, no gain'
# Vincula la base de datos con la interfaz gráfica y ejecuta la aplicación.

from nopy_db import (
    pedir_conexion,
    buscar_usuario_db,
    registrar_usuario_db,
    obtener_ejercicios_por_grupo,
    agregar_ejercicio_db,
    guardar_rutina_completa_db,
    obtener_rutinas_usuario,
    obtener_dias_de_rutina,
    obtener_ejercicios_de_dia,
    registrar_entrenamiento_db
)
import nopy_interfaz as gui

# ------------------------------------------------------------
# 1. PEDIR CONEXIÓN A LA BASE DE DATOS
# ------------------------------------------------------------
conexion = pedir_conexion('127.0.0.1', 'root', 3306)

# ------------------------------------------------------------
# 2. FUNCIONES CONECTORAS ENTRE BD E INTERFAZ
# ------------------------------------------------------------
def fn_login(dni):
    return buscar_usuario_db(conexion, dni)

def fn_registro(dni, nombre, apellido, altura, peso, sexo):
    registrar_usuario_db(conexion, dni, nombre, apellido, altura, peso, sexo)

def fn_obtener_ejercicios(grupo="Todos"):
    return obtener_ejercicios_por_grupo(conexion, grupo)

def fn_agregar_ejercicio(nombre, grupo, descripcion):
    agregar_ejercicio_db(conexion, nombre, grupo, descripcion)

def fn_guardar_rutina(dni_usuario, nombre_rutina, estructura_dias):
    guardar_rutina_completa_db(conexion, dni_usuario, nombre_rutina, estructura_dias)

def fn_obtener_rutinas(dni_usuario):
    return obtener_rutinas_usuario(conexion, dni_usuario)

def fn_obtener_dias(id_rutina):
    return obtener_dias_de_rutina(conexion, id_rutina)

def fn_obtener_ejercicios_dia(id_rutina_dia):
    return obtener_ejercicios_de_dia(conexion, id_rutina_dia)

def fn_registrar_serie(dni_usuario, id_ejercicio, fecha, asistio, serie_num, peso, reps):
    registrar_entrenamiento_db(conexion, dni_usuario, id_ejercicio, fecha, asistio, serie_num, peso, reps)

# ------------------------------------------------------------
# 3. LANZAMIENTO DE VENTANAS TOPLEVEL
# ------------------------------------------------------------
def abrir_ejercicios():
    gui.VentanaEjercicios(
        app, 
        fn_obtener_ejercicios, 
        fn_agregar_ejercicio
    )

def abrir_crear_rutina():
    if app.usuario_actual:
        dni_user = app.usuario_actual[0]  # DNI del usuario logueado
        gui.VentanaCrearRutina(
            app, 
            dni_user, 
            fn_obtener_ejercicios, 
            fn_guardar_rutina
        )

def abrir_seguimiento():
    if app.usuario_actual:
        dni_user = app.usuario_actual[0]
        gui.VentanaSeguimiento(
            app, 
            dni_user, 
            fn_obtener_rutinas, 
            fn_obtener_dias, 
            fn_obtener_ejercicios_dia, 
            fn_registrar_serie
        )

# ------------------------------------------------------------
# 4. EJECUCIÓN DEL SISTEMA
# ------------------------------------------------------------
if conexion:
    # Instanciamos la App principal de CustomTkinter
    app = gui.App(fn_login, fn_registro)

    # Asignamos los comandos a los botones del menú
    app.abrir_ejercicios = abrir_ejercicios
    app.abrir_crear_rutina = abrir_crear_rutina
    app.abrir_seguimiento = abrir_seguimiento

    # Arrancamos el bucle gráfico principal
    app.mainloop()

    # Al cerrar la ventana gráfica, cerramos la conexión a MySQL
    conexion.close()