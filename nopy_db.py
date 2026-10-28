"""
Módulo de Base de Datos para 'No py, no gain'
Maneja la conexión a MySQL y todas las consultas CRUD del sistema.
"""

import os
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
            print("✔ Conexión exitosa a la Base de Datos MySQL.")
            return conexion
    except Error as e:
        print(f"❌ Error al conectar a la Base de Datos: {e}")
        return None

def obtener_ruta_txt(filename="nopy_ejercicios.txt"):
    """Devuelve la ruta absoluta para asegurar que el txt se cree en la carpeta del proyecto."""
    dir_actual = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir_actual, filename)

# # FUNCIÓN ESCRIBIR EN ARCHIVO:
def escribir_archivo(nombre_archivo, texto):
    archivo = open(nombre_archivo, "a", encoding="utf-8")
    archivo.write(texto)
    archivo.close()

# # FUNCIÓN REESCRIBIR ARCHIVO:
def reescribir_archivo(nombre_archivo, lineas):
    archivo = open(nombre_archivo, "w", encoding="utf-8")
    archivo.writelines(lineas)
    archivo.close()

# # FUNCIÓN LEER ARCHIVO:
def leer_archivo(nombre_archivo):
    if not os.path.exists(nombre_archivo):
        return []
    archivo = open(nombre_archivo, "r", encoding="utf-8")
    contenido = archivo.readlines()
    archivo.close()
    return contenido

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

def obtener_ejercicios_por_grupo(conexion, grupo="Todos", filename="nopy_ejercicios.txt"):
    """Devuelve los ejercicios filtrados por grupo muscular."""
    path = obtener_ruta_txt(filename)
    try:
        if conexion:
            cursor = conexion.cursor()
            sql = "SELECT id_ejercicio, nombre, grupo_muscular, tipo_ejercicio, descripcion FROM ejercicios"
            cursor.execute(sql)
            resultados = cursor.fetchall()
            cursor.close()
            
            lineas = []
            for ej in resultados:
                lineas.append(f"{ej[0]}|{ej[1]}|{ej[2]}|{ej[3]}|{ej[4]}\n")
            reescribir_archivo(path, lineas)
    except Exception as e:
        print(f"Error al sincronizar txt desde BD: {e}")

    ejercicios = []
    lineas_txt = leer_archivo(path)
    for linea in lineas_txt:
        parts = linea.strip().split("|")
        if len(parts) >= 4:
            id_ej = int(parts[0])
            nombre = parts[1]
            grupo_musc = parts[2]
            tipo = parts[3]
            desc = parts[4] if len(parts) > 4 else ""
            if grupo == "Todos" or grupo_musc.strip().lower() == grupo.strip().lower():
                ejercicios.append((id_ej, nombre, grupo_musc, tipo, desc))
    return ejercicios

def agregar_ejercicio_db(conexion, nombre, grupo_muscular, tipo_ejercicio, descripcion=""):
    """Agrega un nuevo ejercicio personalizado al catálogo."""
    path = obtener_ruta_txt("nopy_ejercicios.txt")
    try:
        cursor = conexion.cursor()
        sql = "INSERT INTO ejercicios (nombre, grupo_muscular, tipo_ejercicio, descripcion) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (nombre, grupo_muscular, tipo_ejercicio, descripcion))
        conexion.commit()
        id_ej = cursor.lastrowid
        cursor.close()
        
        nueva_linea = f"{id_ej}|{nombre}|{grupo_muscular}|{tipo_ejercicio}|{descripcion}\n"
        escribir_archivo(path, nueva_linea)
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
        return []

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

def registrar_serie_entrenamiento_db(conexion, dni_usuario, id_ejercicio, fecha, asistio, serie_numero, peso_kg, repeticiones):
    """Registra el desempeño de una serie específica en el entrenamiento."""
    try:
        cursor = conexion.cursor()
        sql = """
            INSERT INTO registros_entrenamiento (dni_usuario, id_ejercicio, fecha, asistio, serie_numero, peso_kg, repeticiones)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (dni_usuario, id_ejercicio, fecha, asistio, serie_numero, peso_kg, repeticiones))
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