"""
Módulo Principal - Punto de Entrada de 'No py, no gain'
Vincula la base de datos, la lógica y la interfaz gráfica basada en el diagrama de flujo.
"""

from nopy_db import (
    pedir_conexion,
    buscar_usuario_db,
    registrar_usuario_db,
    actualizar_usuario_db,
    obtener_ejercicios_por_grupo,
    agregar_ejercicio_db,
    guardar_rutina_completa_db,
    obtener_rutinas_usuario,
    eliminar_rutina_db,
    obtener_dias_de_rutina,
    registrar_serie_entrenamiento_db,
    obtener_seguimiento_usuario_db
)
import nopy_interfaz as gui
from claves_nopy import DB_CONTRASEÑA

conexion = pedir_conexion(host='127.0.0.1', user='root', password= DB_CONTRASEÑA, database='nopy_nogain', port=3306)

def fn_login(dni): return buscar_usuario_db(conexion, dni)
def fn_registro(dni, nombre, apellido, peso, altura, sexo): return registrar_usuario_db(conexion, dni, nombre, apellido, peso, altura, sexo)
def fn_actualizar_usuario(dni, nombre, apellido, peso, altura, sexo): return actualizar_usuario_db(conexion, dni, nombre, apellido, peso, altura, sexo)
def fn_obtener_ejercicios(grupo="Todos"): return obtener_ejercicios_por_grupo(conexion, grupo)
def fn_agregar_ejercicio(nombre, grupo_muscular, tipo_ejercicio, descripcion): return agregar_ejercicio_db(conexion, nombre, grupo_muscular, tipo_ejercicio, descripcion)
def fn_guardar_rutina(dni_usuario, nombre_rutina, estructura_dias): return guardar_rutina_completa_db(conexion, dni_usuario, nombre_rutina, estructura_dias)
def fn_obtener_rutinas(dni_usuario): return obtener_rutinas_usuario(conexion, dni_usuario)
def fn_eliminar_rutina(id_rutina): return eliminar_rutina_db(conexion, id_rutina)
def fn_obtener_dias(id_rutina): return obtener_dias_de_rutina(conexion, id_rutina)
def fn_registrar_serie(dni_usuario, id_ejercicio, fecha, asistio, serie_num, peso, reps): 
    return registrar_serie_entrenamiento_db(conexion, dni_usuario, id_ejercicio, fecha, asistio, serie_num, peso, reps)
def fn_obtener_seguimiento(dni_usuario): return obtener_seguimiento_usuario_db(conexion, dni_usuario)

def abrir_gestionar_rutina():
    if app.usuario_actual:
        gui.VentanaGestionarRutinas(
            app, app.usuario_actual[0], 
            fn_obtener_ejercicios, fn_agregar_ejercicio, fn_guardar_rutina, 
            fn_obtener_rutinas, fn_eliminar_rutina
        )

def abrir_realizar_rutina():
    if app.usuario_actual:
        gui.VentanaMenuRealizarRutina(
            app, app.usuario_actual[0], 
            fn_obtener_rutinas, fn_obtener_dias, fn_registrar_serie, fn_obtener_seguimiento
        )

def abrir_informacion_personal():
    if app.usuario_actual:
        gui.VentanaInformacionPersonal(app, app.usuario_actual, fn_actualizar_usuario)

if __name__ == "__main__":
    if conexion:
        app = gui.App(fn_login, fn_registro, fn_actualizar_usuario)
        app.abrir_gestionar_rutina_cmd = abrir_gestionar_rutina
        app.abrir_realizar_rutina_cmd = abrir_realizar_rutina
        app.abrir_informacion_personal_cmd = abrir_informacion_personal

        app.mainloop()
        conexion.close()
        print("✔ Conexión a MySQL cerrada correctamente.")
    else:
        print("❌ No se pudo iniciar la aplicación por un fallo en la conexión a la Base de Datos.")