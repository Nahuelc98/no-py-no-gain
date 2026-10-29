"""
Módulo de Base de Datos para 'No py, no gain'
Maneja la conexión a MySQL y todas las consultas CRUD del sistema.
"""

import os
from datetime import datetime
import mysql.connector
from mysql.connector import Error

def pedir_conexion(host, user, password, database="nopy_nogain", port=3306):
    """Establece y devuelve la conexión con la base de datos MySQL."""
    try:
        conexion = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        if conexion.is_connected():
            print("[OK] Conexión exitosa a la Base de Datos MySQL.")
            return conexion
    except Error as e:
        print(f"[X] Error al conectar a la Base de Datos: {e}")
        return None

def obtener_ruta_txt(filename="accion_usuario.txt"):
    """Devuelve la ruta absoluta para asegurar que el txt se cree en la carpeta del proyecto."""
    dir_actual = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir_actual, filename)

# # FUNCIÓN ESCRIBIR EN ARCHIVO (Modo append 'a'):
def escribir_archivo(nombre_archivo, texto):
    archivo = open(nombre_archivo, "a", encoding="utf-8")
    archivo.write(texto)
    archivo.close()

# # FUNCIÓN REESCRIBIR ARCHIVO (Modo write 'w'):
def reescribir_archivo(nombre_archivo, lineas):
    archivo = open(nombre_archivo, "w", encoding="utf-8")
    archivo.writelines(lineas)
    archivo.close()

# # FUNCIÓN LEER ARCHIVO (Modo read 'r'):
def leer_archivo(nombre_archivo):
    if not os.path.exists(nombre_archivo):
        return []
    archivo = open(nombre_archivo, "r", encoding="utf-8")
    contenido = archivo.readlines()
    archivo.close()
    return contenido

# FUNCIÓN PARA REGISTRAR EN EL LOG LAS ACCIONES DEL USUARIO
def registrar_accion_usuario(accion, dni="Sin DNI", nombre="Invitado"):
    """Guarda en 'accion_usuario.txt' la acción realizada por el usuario con fecha y hora exacta."""
    try:
        ruta = obtener_ruta_txt("accion_usuario.txt")
        ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        linea = f"[{ahora}] | ACCIÓN: {accion} | DNI: {dni} | Usuario: {nombre}\n"
        escribir_archivo(ruta, linea)
    except Exception as e:
        print(f"Error al registrar accion en txt: {e}")

def buscar_usuario_db(conexion, dni):
    """Busca un usuario por su DNI para el login."""
    try:
        cursor = conexion.cursor()
        sql = "SELECT dni, nombre, apellido, peso, altura, sexo FROM usuarios WHERE dni = %s"
        cursor.execute(sql, (dni,))
        usuario = cursor.fetchone()
        cursor.close()
        return usuario
    except Error as e:
        print(f"Error al buscar usuario: {e}")
        return None

def registrar_usuario_db(conexion, dni, nombre, apellido, peso, altura, sexo):
    """Registra un nuevo usuario en la base de datos."""
    try:
        cursor = conexion.cursor()
        sql = "INSERT INTO usuarios (dni, nombre, apellido, peso, altura, sexo) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (dni, nombre, apellido, peso, altura, sexo))
        conexion.commit()
        cursor.close()
        return True
    except Error as e:
        print(f"Error al registrar usuario: {e}")
        return False

def actualizar_usuario_db(conexion, dni, nombre, apellido, peso, altura, sexo):
    """Actualiza la información personal de un usuario existente."""
    try:
        cursor = conexion.cursor()
        sql = "UPDATE usuarios SET nombre = %s, apellido = %s, peso = %s, altura = %s, sexo = %s WHERE dni = %s"
        cursor.execute(sql, (nombre, apellido, peso, altura, sexo, dni))
        conexion.commit()
        cursor.close()
        return True
    except Error as e:
        print(f"Error al actualizar usuario: {e}")
        return False

def obtener_ejercicios_por_grupo(conexion, grupo="Todos", dni_usuario=None):
    """Devuelve los ejercicios globales (dni_usuario IS NULL) y los propios del usuario."""
    try:
        if not conexion:
            return []
        cursor = conexion.cursor()
        if grupo == "Todos":
            sql = """
                SELECT id_ejercicio, nombre, grupo_muscular, tipo_ejercicio 
                FROM ejercicios 
                WHERE dni_usuario IS NULL OR dni_usuario = %s
                ORDER BY id_ejercicio
            """
            cursor.execute(sql, (dni_usuario,))
        else:
            sql = """
                SELECT id_ejercicio, nombre, grupo_muscular, tipo_ejercicio 
                FROM ejercicios 
                WHERE (dni_usuario IS NULL OR dni_usuario = %s) AND LOWER(grupo_muscular) = LOWER(%s)
                ORDER BY id_ejercicio
            """
            cursor.execute(sql, (dni_usuario, grupo))
        
        resultados = cursor.fetchall()
        cursor.close()
        return resultados
    except Error as e:
        print(f"Error al obtener ejercicios desde BD: {e}")
        return []

def agregar_ejercicio_db(conexion, dni_usuario, nombre, grupo_muscular, tipo_ejercicio):
    """Agrega un nuevo ejercicio personalizado para el usuario actual."""
    try:
        cursor = conexion.cursor()
        sql = "INSERT INTO ejercicios (dni_usuario, nombre, grupo_muscular, tipo_ejercicio) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (dni_usuario, nombre, grupo_muscular, tipo_ejercicio))
        conexion.commit()
        cursor.close()
        
        # Guardamos la acción en el archivo de texto accion_usuario.txt
        registrar_accion_usuario(f"Creó nuevo ejercicio: '{nombre}' ({grupo_muscular})", dni=dni_usuario)
        return True
    except Error as e:
        print(f"Error al agregar ejercicio: {e}")
        return False

def guardar_rutina_completa_db(conexion, dni_usuario, nombre_rutina, estructura_dias):
    """Guarda una rutina completa con sus días y ejercicios asociados."""
    try:
        cursor = conexion.cursor()
        sql_rutina = "INSERT INTO rutinas (dni_usuario, nombre_rutina, cantidad_dias) VALUES (%s, %s, %s)"
        cursor.execute(sql_rutina, (dni_usuario, nombre_rutina, len(estructura_dias)))
        id_rutina = cursor.lastrowid

        for dia in estructura_dias:
            sql_dia = "INSERT INTO rutina_dias (id_rutina, numero_dia, grupo_muscular) VALUES (%s, %s, %s)"
            cursor.execute(sql_dia, (id_rutina, dia['numero_dia'], dia['grupo']))
            id_rutina_dia = cursor.lastrowid

            for ej in dia['ejercicios']:
                sql_ej = "INSERT INTO rutina_ejercicios (id_rutina_dia, id_ejercicio, cantidad_series) VALUES (%s, %s, %s)"
                cursor.execute(sql_ej, (id_rutina_dia, ej['id'], ej['series']))

        conexion.commit()
        cursor.close()
        return True
    except Error as e:
        conexion.rollback()
        print(f"Error al guardar la rutina completa: {e}")
        return False

def obtener_rutinas_usuario(conexion, dni_usuario):
    """Obtiene todas las rutinas creadas por un usuario."""
    try:
        cursor = conexion.cursor()
        sql = "SELECT id_rutina, nombre_rutina, cantidad_dias FROM rutinas WHERE dni_usuario = %s"
        cursor.execute(sql, (dni_usuario,))
        resultado = cursor.fetchall()
        cursor.close()
        return resultado
    except Error as e:
        print(f"Error al obtener rutinas: {e}")
        return []

def eliminar_rutina_db(conexion, id_rutina):
    """Elimina una rutina de la base de datos."""
    try:
        cursor = conexion.cursor()
        sql = "DELETE FROM rutinas WHERE id_rutina = %s"
        cursor.execute(sql, (id_rutina,))
        conexion.commit()
        cursor.close()
        return True
    except Error as e:
        print(f"Error al eliminar rutina: {e}")
        return False

def obtener_dias_de_rutina(conexion, id_rutina):
    """Obtiene los días y grupos musculares asociados a una rutina."""
    try:
        cursor = conexion.cursor()
        sql = "SELECT id_rutina_dia, numero_dia, grupo_muscular FROM rutina_dias WHERE id_rutina = %s"
        cursor.execute(sql, (id_rutina,))
        resultado = cursor.fetchall()
        cursor.close()
        return resultado
    except Error as e:
        print(f"Error al obtener días de la rutina: {e}")
        return []

def registrar_serie_entrenamiento_db(conexion, dni_usuario, id_ejercicio, fecha, serie_numero, peso_kg, repeticiones):
    """Registra el desempeño de una serie específica en el entrenamiento (asistencia implícita)."""
    try:
        cursor = conexion.cursor()
        sql = """
            INSERT INTO registros_entrenamiento (dni_usuario, id_ejercicio, fecha, serie_numero, peso_kg, repeticiones)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (dni_usuario, id_ejercicio, fecha, serie_numero, peso_kg, repeticiones))
        conexion.commit()
        cursor.close()
        return True
    except Error as e:
        print(f"Error al registrar serie: {e}")
        return False

def obtener_seguimiento_usuario_db(conexion, dni_usuario):
    """Obtiene el historial de registros de entrenamiento del usuario."""
    try:
        cursor = conexion.cursor()
        sql = """
            SELECT r.fecha, e.nombre, r.serie_numero, r.peso_kg, r.repeticiones
            FROM registros_entrenamiento r
            JOIN ejercicios e ON r.id_ejercicio = e.id_ejercicio
            WHERE r.dni_usuario = %s
            ORDER BY r.fecha DESC
        """
        cursor.execute(sql, (dni_usuario,))
        resultado = cursor.fetchall()
        cursor.close()
        return resultado
    except Error as e:
        print(f"Error al obtener seguimiento: {e}")
        return []

# FUNCIÓN PARA TRAER LOS EJERCICIOS QUE PERTENECEN A UN DÍA DE ENTRENAMIENTO
def obtener_ejercicios_de_dia(conexion, id_rutina_dia):
    """Devuelve la lista de ejercicios y series configurados para un día de la rutina."""
    try:
        cursor = conexion.cursor()
        # Unimos con JOIN para obtener el nombre del ejercicio y las series programadas
        sql = """
            SELECT e.id_ejercicio, e.nombre, e.grupo_muscular, re.cantidad_series
            FROM rutina_ejercicios re
            JOIN ejercicios e ON re.id_ejercicio = e.id_ejercicio
            WHERE re.id_rutina_dia = %s
        """
        cursor.execute(sql, (id_rutina_dia,))
        resultado = cursor.fetchall()
        cursor.close()
        return resultado
    except Error as e:
        print(f"Error al obtener ejercicios del día: {e}")
        return []

# FUNCIÓN PARA OBTENER TODOS LOS DATOS DE UNA RUTINA (PARA PODER EDITARLA)
def obtener_detalle_rutina(conexion, id_rutina):
    """Devuelve el nombre de la rutina y la lista de sus días con sus ejercicios."""
    try:
        cursor = conexion.cursor()
        # 1. Buscamos el nombre y cantidad de días de la rutina
        cursor.execute("SELECT nombre_rutina, cantidad_dias FROM rutinas WHERE id_rutina = %s", (id_rutina,))
        rutina_info = cursor.fetchone()
        if not rutina_info:
            cursor.close()
            return None

        # 2. Buscamos los días asignados a esa rutina
        cursor.execute("SELECT id_rutina_dia, numero_dia, grupo_muscular FROM rutina_dias WHERE id_rutina = %s ORDER BY numero_dia", (id_rutina,))
        dias = cursor.fetchall()

        estructura_dias = []
        for dia in dias:
            id_dia, num_dia, grupo = dia
            # 3. Buscamos los ejercicios de cada día
            sql_ej = """
                SELECT e.id_ejercicio, e.nombre, e.grupo_muscular, re.cantidad_series
                FROM rutina_ejercicios re
                JOIN ejercicios e ON re.id_ejercicio = e.id_ejercicio
                WHERE re.id_rutina_dia = %s
            """
            cursor.execute(sql_ej, (id_dia,))
            ejercicios_raw = cursor.fetchall()

            lista_ejercicios = []
            for ej in ejercicios_raw:
                lista_ejercicios.append({
                    'id': ej[0],
                    'nombre': ej[1],
                    'grupo': ej[2],
                    'series': ej[3]
                })

            estructura_dias.append({
                'numero_dia': num_dia,
                'grupo': grupo,
                'ejercicios': lista_ejercicios
            })

        cursor.close()
        return {
            'nombre_rutina': rutina_info[0],
            'cantidad_dias': rutina_info[1],
            'dias': estructura_dias
        }
    except Error as e:
        print(f"Error al obtener detalle de la rutina: {e}")
        return None

# FUNCIÓN PARA ACTUALIZAR UNA RUTINA EXISTENTE (EDITAR RUTINA)
def actualizar_rutina_completa_db(conexion, id_rutina, nombre_rutina, estructura_dias):
    """Actualiza el nombre, los días y los ejercicios de una rutina ya creada."""
    try:
        cursor = conexion.cursor()
        # 1. Actualizamos el nombre y la cantidad de días en la tabla rutinas
        sql_update = "UPDATE rutinas SET nombre_rutina = %s, cantidad_dias = %s WHERE id_rutina = %s"
        cursor.execute(sql_update, (nombre_rutina, len(estructura_dias), id_rutina))

        # 2. Borramos los días anteriores (por el ON DELETE CASCADE se borran también los ejercicios viejos)
        cursor.execute("DELETE FROM rutina_dias WHERE id_rutina = %s", (id_rutina,))

        # 3. Insertamos la nueva distribución de días y ejercicios
        for dia in estructura_dias:
            sql_dia = "INSERT INTO rutina_dias (id_rutina, numero_dia, grupo_muscular) VALUES (%s, %s, %s)"
            cursor.execute(sql_dia, (id_rutina, dia['numero_dia'], dia['grupo']))
            id_rutina_dia = cursor.lastrowid

            for ej in dia['ejercicios']:
                sql_ej = "INSERT INTO rutina_ejercicios (id_rutina_dia, id_ejercicio, cantidad_series) VALUES (%s, %s, %s)"
                cursor.execute(sql_ej, (id_rutina_dia, ej['id'], ej['series']))

        conexion.commit()
        cursor.close()
        return True
    except Error as e:
        conexion.rollback()
        print(f"Error al actualizar la rutina: {e}")
        return False
