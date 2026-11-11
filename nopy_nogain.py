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
    obtener_ejercicios_propios_db,
    actualizar_ejercicio_db,
    eliminar_ejercicio_db,
    guardar_rutina_completa_db,
    obtener_rutinas_usuario,
    eliminar_rutina_db,
    obtener_dias_de_rutina,
    obtener_ejercicios_de_dia,
    obtener_detalle_rutina,
    actualizar_rutina_completa_db,
    registrar_serie_entrenamiento_db,
    obtener_series_ejercicio_fecha_db,
    obtener_ultima_fecha_ejercicio_db,
    obtener_seguimiento_usuario_db,
    obtener_fechas_entrenadas_db,
    obtener_registros_por_fecha_db,
    registrar_accion_usuario
)
import nopy_interfaz as gui
from claves_nopy import DB_CONTRASEÑA
from nopy_api import analizar_rendimiento_usuario

# Conexión con MySQL utilizando las credenciales protegidas
conexion = pedir_conexion(host='127.0.0.1', user='root', password=DB_CONTRASEÑA, database='nopy_nogain', port=3306)

# Funciones simples para comunicar la interfaz con la base de datos y la IA
def fn_login(dni): return buscar_usuario_db(conexion, dni)
def fn_registro(dni, nombre, apellido, peso, altura, sexo): return registrar_usuario_db(conexion, dni, nombre, apellido, peso, altura, sexo)
def fn_actualizar_usuario(dni, nombre, apellido, peso, altura, sexo): return actualizar_usuario_db(conexion, dni, nombre, apellido, peso, altura, sexo)
def fn_obtener_ejercicios(grupo="Todos", dni=None): return obtener_ejercicios_por_grupo(conexion, grupo, dni)
def fn_agregar_ejercicio(dni, nombre, grupo_muscular, tipo_ejercicio): return agregar_ejercicio_db(conexion, dni, nombre, grupo_muscular, tipo_ejercicio)
def fn_obtener_ejercicios_propios(dni): return obtener_ejercicios_propios_db(conexion, dni)
def fn_actualizar_ejercicio(id_ejercicio, dni, nombre, grupo, tipo): return actualizar_ejercicio_db(conexion, id_ejercicio, dni, nombre, grupo, tipo)
def fn_eliminar_ejercicio(id_ejercicio, dni): return eliminar_ejercicio_db(conexion, id_ejercicio, dni)
def fn_guardar_rutina(dni_usuario, nombre_rutina, estructura_dias): return guardar_rutina_completa_db(conexion, dni_usuario, nombre_rutina, estructura_dias)
def fn_actualizar_rutina(id_rutina, dni_usuario, nombre_rutina, estructura_dias): return actualizar_rutina_completa_db(conexion, id_rutina, dni_usuario, nombre_rutina, estructura_dias)
def fn_obtener_rutinas(dni_usuario): return obtener_rutinas_usuario(conexion, dni_usuario)
def fn_obtener_detalle_rutina(id_rutina, dni_usuario): return obtener_detalle_rutina(conexion, id_rutina, dni_usuario)
def fn_eliminar_rutina(id_rutina, dni_usuario): return eliminar_rutina_db(conexion, id_rutina, dni_usuario)
def fn_obtener_dias(id_rutina): return obtener_dias_de_rutina(conexion, id_rutina)
def fn_obtener_ejercicios_dia(id_rutina_dia): return obtener_ejercicios_de_dia(conexion, id_rutina_dia)
def fn_registrar_serie(dni_usuario, id_ejercicio, fecha, serie_num, peso, reps): 
    return registrar_serie_entrenamiento_db(conexion, dni_usuario, id_ejercicio, fecha, serie_num, peso, reps)
def fn_obtener_series_fecha(dni_usuario, id_ejercicio, fecha): return obtener_series_ejercicio_fecha_db(conexion, dni_usuario, id_ejercicio, fecha)
def fn_obtener_ultima_fecha(dni_usuario, id_ejercicio, fecha_actual): return obtener_ultima_fecha_ejercicio_db(conexion, dni_usuario, id_ejercicio, fecha_actual)
def fn_obtener_seguimiento(dni_usuario): return obtener_seguimiento_usuario_db(conexion, dni_usuario)
def fn_obtener_fechas_entrenadas(dni_usuario): return obtener_fechas_entrenadas_db(conexion, dni_usuario)
def fn_obtener_registros_fecha(dni_usuario, fecha): return obtener_registros_por_fecha_db(conexion, dni_usuario, fecha)
def fn_analizar_ia(registros, nombre_usuario): return analizar_rendimiento_usuario(registros, nombre_usuario)
def fn_registrar_accion(accion, dni="Sin DNI", nombre="Invitado"): registrar_accion_usuario(accion, dni, nombre)

def abrir_gestionar_rutina():
    """Abre la ventana para crear, editar o eliminar rutinas y ejercicios propios."""
    if app.usuario_actual:
        gui.VentanaGestionarRutinas(
            app, app.usuario_actual.dni,
            fn_obtener_ejercicios, fn_agregar_ejercicio, fn_guardar_rutina,
            fn_obtener_rutinas, fn_eliminar_rutina,
            fn_obtener_detalle_rutina, fn_actualizar_rutina,
            fn_obtener_ejercicios_propios, fn_actualizar_ejercicio, fn_eliminar_ejercicio
        )

def abrir_realizar_rutina():
    """Abre la ventana de Empezar Rutina (para entrenar y registrar series)."""
    if app.usuario_actual:
        # Abre directo la sesión de entrenamiento (sin pantalla intermedia)
        gui.VentanaComenzarEntrenar(
            app, app.usuario_actual.dni,
            fn_obtener_rutinas, fn_obtener_dias, fn_registrar_serie,
            fn_obtener_ejercicios_dia,
            fn_obtener_series_fecha, fn_obtener_ultima_fecha
        )

def abrir_ver_seguimiento():
    """Abre la ventana de Ver Seguimiento (calendario interactivo, comparativa de fechas y análisis con IA)."""
    if app.usuario_actual:
        # usuario_actual es un objeto Usuario, usamos su método nombre_completo()
        nombre_completo = app.usuario_actual.nombre_completo()
        gui.VentanaVerSeguimiento(
            app, app.usuario_actual.dni,
            fn_obtener_seguimiento, fn_obtener_fechas_entrenadas, fn_obtener_registros_fecha,
            fn_analizar_ia, nombre_completo
        )

def abrir_informacion_personal():
    """Abre la ventana para consultar y editar información personal."""
    if app.usuario_actual:
        # Esta función se llama cuando el usuario guarda cambios en la ventana
        # y actualiza los datos del usuario en la ventana principal sin cerrar la app
        def actualizar_usuario_en_app(nuevo_usuario):
            app.usuario_actual = nuevo_usuario
        gui.VentanaInformacionPersonal(app, app.usuario_actual, fn_actualizar_usuario, actualizar_usuario_en_app)

if __name__ == "__main__":
    if conexion:
        # Iniciamos la aplicación gráfica vinculando las funciones y el registro de acciones txt
        app = gui.App(fn_login, fn_registro, fn_actualizar_usuario, fn_registrar_accion)
        app.abrir_gestionar_rutina_cmd = abrir_gestionar_rutina
        app.abrir_realizar_rutina_cmd = abrir_realizar_rutina
        app.abrir_ver_seguimiento_cmd = abrir_ver_seguimiento
        app.abrir_informacion_personal_cmd = abrir_informacion_personal

        app.mainloop()
        conexion.close()
        print("[OK] Conexión a MySQL cerrada correctamente.")
    else:
        print("[X] No se pudo iniciar la aplicación por un fallo en la conexión a la Base de Datos.")