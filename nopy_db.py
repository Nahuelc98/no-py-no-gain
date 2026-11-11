"""
Módulo de Base de Datos para 'No py, no gain'
Maneja la conexión a MySQL y todas las consultas CRUD del sistema.
"""

import os
from datetime import datetime
import mysql.connector
from mysql.connector import Error
# Importamos las clases para convertir los resultados de la BD en objetos
from nopy_clases import Usuario, Ejercicio, Rutina

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
        if not os.path.exists(ruta) or os.path.getsize(ruta) == 0:
            escribir_archivo(ruta, "=== NO PY, NO GAIN - REGISTRO DE SESIONES ===\n")
        ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        linea = f"DNI: {dni} | Nombre y Apellido: {nombre} | Fecha y Hora: {ahora} | {accion.upper()}\n"
        escribir_archivo(ruta, linea)
    except Exception as e:
        print(f"Error al registrar accion en txt: {e}")

def buscar_usuario_db(conexion, dni):
    """Busca un usuario por su DNI para el login. Devuelve un objeto Usuario o None."""
    try:
        cursor = conexion.cursor()
        sql = "SELECT dni, nombre, apellido, peso, altura, sexo FROM usuarios WHERE dni = %s"
        cursor.execute(sql, (dni,))
        fila = cursor.fetchone()
        cursor.close()
        # Si no se encontró el DNI devolvemos None
        if not fila:
            return None
        # Convertimos la fila (tupla) en un objeto de la clase Usuario
        usuario = Usuario(fila[0], fila[1], fila[2], fila[3], fila[4], fila[5])
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
    """Devuelve los ejercicios globales (dni_usuario IS NULL) y los propios del usuario (solo los activos)."""
    try:
        if not conexion:
            return []
        cursor = conexion.cursor()
        # activo = TRUE: no mostramos los ejercicios dados de baja (baja lógica)
        if grupo == "Todos":
            sql = """
                SELECT id_ejercicio, nombre, grupo_muscular, tipo_ejercicio, dni_usuario
                FROM ejercicios
                WHERE (dni_usuario IS NULL OR dni_usuario = %s) AND activo = TRUE
                ORDER BY id_ejercicio
            """
            cursor.execute(sql, (dni_usuario,))
        else:
            sql = """
                SELECT id_ejercicio, nombre, grupo_muscular, tipo_ejercicio, dni_usuario
                FROM ejercicios
                WHERE (dni_usuario IS NULL OR dni_usuario = %s) AND LOWER(grupo_muscular) = LOWER(%s) AND activo = TRUE
                ORDER BY id_ejercicio
            """
            cursor.execute(sql, (dni_usuario, grupo))

        resultados = cursor.fetchall()
        cursor.close()
        # Convertimos cada fila en un objeto de la clase Ejercicio
        lista_ejercicios = []
        for fila in resultados:
            lista_ejercicios.append(Ejercicio(fila[0], fila[1], fila[2], fila[3], fila[4]))
        return lista_ejercicios
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
        
        return True
    except Error as e:
        print(f"Error al agregar ejercicio: {e}")
        return False

def obtener_ejercicios_propios_db(conexion, dni_usuario):
    """Devuelve solo los ejercicios activos creados por el usuario (no los precargados)."""
    try:
        if not conexion:
            return []
        cursor = conexion.cursor()
        sql = """
            SELECT id_ejercicio, nombre, grupo_muscular, tipo_ejercicio
            FROM ejercicios
            WHERE dni_usuario = %s AND activo = TRUE
            ORDER BY id_ejercicio
        """
        cursor.execute(sql, (dni_usuario,))
        resultados = cursor.fetchall()
        cursor.close()
        # Convertimos cada fila en un objeto Ejercicio (indicando el DNI del dueño)
        lista_ejercicios = []
        for fila in resultados:
            lista_ejercicios.append(Ejercicio(fila[0], fila[1], fila[2], fila[3], dni_usuario))
        return lista_ejercicios
    except Error as e:
        print(f"Error al obtener ejercicios propios: {e}")
        return []

def actualizar_ejercicio_db(conexion, id_ejercicio, dni_usuario, nuevo_nombre, nuevo_grupo, nuevo_tipo):
    """Edita un ejercicio del usuario. Solo permite editar si el ejercicio le pertenece al usuario."""
    try:
        cursor = conexion.cursor()
        sql = """
            UPDATE ejercicios
            SET nombre = %s, grupo_muscular = %s, tipo_ejercicio = %s
            WHERE id_ejercicio = %s AND dni_usuario = %s
        """
        cursor.execute(sql, (nuevo_nombre, nuevo_grupo, nuevo_tipo, id_ejercicio, dni_usuario))
        conexion.commit()
        filas = cursor.rowcount
        cursor.close()
        # Si filas es 0, el ejercicio no le pertenece al usuario o no existe
        return filas > 0
    except Error as e:
        print(f"Error al actualizar ejercicio: {e}")
        return False

def eliminar_ejercicio_db(conexion, id_ejercicio, dni_usuario):
    """
    Elimina un ejercicio del usuario con BAJA LÓGICA: no se borra de la tabla, se marca activo = FALSE.
    Así se conserva el historial de entrenamiento (las series registradas siguen en el seguimiento).
    Solo permite eliminar si el ejercicio le pertenece al usuario.
    """
    try:
        cursor = conexion.cursor()
        # 1. Marcamos el ejercicio como inactivo (solo si es del usuario y todavía está activo)
        sql = "UPDATE ejercicios SET activo = FALSE WHERE id_ejercicio = %s AND dni_usuario = %s AND activo = TRUE"
        cursor.execute(sql, (id_ejercicio, dni_usuario))
        filas = cursor.rowcount
        # Si filas es 0, el ejercicio no le pertenece al usuario o no existe
        if filas == 0:
            cursor.close()
            return False

        # 2. Lo quitamos de las rutinas donde estaba asignado (las rutinas y el historial se conservan)
        cursor.execute("DELETE FROM rutina_ejercicios WHERE id_ejercicio = %s", (id_ejercicio,))
        conexion.commit()
        cursor.close()
        return True
    except Error as e:
        conexion.rollback()
        print(f"Error al eliminar ejercicio: {e}")
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
    """Obtiene todas las rutinas creadas por un usuario (como objetos Rutina)."""
    try:
        cursor = conexion.cursor()
        sql = "SELECT id_rutina, nombre_rutina, cantidad_dias FROM rutinas WHERE dni_usuario = %s"
        cursor.execute(sql, (dni_usuario,))
        resultado = cursor.fetchall()
        cursor.close()
        # Convertimos cada fila en un objeto de la clase Rutina
        lista_rutinas = []
        for fila in resultado:
            lista_rutinas.append(Rutina(fila[0], dni_usuario, fila[1], fila[2]))
        return lista_rutinas
    except Error as e:
        print(f"Error al obtener rutinas: {e}")
        return []

def eliminar_rutina_db(conexion, id_rutina, dni_usuario):
    """Elimina una rutina de la base de datos. Solo permite eliminar si la rutina le pertenece al usuario."""
    try:
        cursor = conexion.cursor()
        sql = "DELETE FROM rutinas WHERE id_rutina = %s AND dni_usuario = %s"
        cursor.execute(sql, (id_rutina, dni_usuario))
        conexion.commit()
        filas = cursor.rowcount
        cursor.close()
        # Si filas es 0, la rutina no le pertenece al usuario o no existe
        return filas > 0
    except Error as e:
        print(f"Error al eliminar rutina: {e}")
        return False

def obtener_dias_de_rutina(conexion, id_rutina):
    """
    Obtiene los días de una rutina y TODOS los grupos musculares de cada día.
    Los grupos se arman con los ejercicios que tiene asignados cada día (ej: "Pecho, Hombros, Tríceps"),
    así siempre coinciden con lo que realmente se entrena ese día.
    """
    try:
        cursor = conexion.cursor()
        sql = "SELECT id_rutina_dia, numero_dia, grupo_muscular FROM rutina_dias WHERE id_rutina = %s ORDER BY numero_dia"
        cursor.execute(sql, (id_rutina,))
        dias = cursor.fetchall()

        resultado = []
        for dia in dias:
            id_dia, num_dia, grupo_guardado = dia
            # Buscamos los grupos musculares de los ejercicios de ese día (en el orden en que se agregaron)
            sql_grupos = """
                SELECT e.grupo_muscular
                FROM rutina_ejercicios re
                JOIN ejercicios e ON re.id_ejercicio = e.id_ejercicio
                WHERE re.id_rutina_dia = %s
                ORDER BY re.id_rutina_ejercicio
            """
            cursor.execute(sql_grupos, (id_dia,))
            grupos = []
            for fila in cursor.fetchall():
                if fila[0] not in grupos:
                    grupos.append(fila[0])
            # Si el día no tiene ejercicios, usamos el grupo que estaba guardado
            texto_grupos = ", ".join(grupos) if grupos else grupo_guardado
            resultado.append((id_dia, num_dia, texto_grupos))

        cursor.close()
        return resultado
    except Error as e:
        print(f"Error al obtener días de la rutina: {e}")
        return []

def registrar_serie_entrenamiento_db(conexion, dni_usuario, id_ejercicio, fecha, serie_numero, peso_kg, repeticiones):
    """
    Registra el desempeño de una serie específica en el entrenamiento (asistencia implícita).
    Cada serie se puede cargar una sola vez por día: si ya existe, se REEMPLAZA con los datos nuevos.
    Devuelve "nueva" si se cargó por primera vez, "reemplazada" si se actualizó, o False si hubo un error.
    """
    try:
        cursor = conexion.cursor()
        # 1. Buscamos si esa serie ya fue registrada hoy para ese ejercicio
        sql_buscar = """
            SELECT id_registro FROM registros_entrenamiento
            WHERE dni_usuario = %s AND id_ejercicio = %s AND fecha = %s AND serie_numero = %s
        """
        cursor.execute(sql_buscar, (dni_usuario, id_ejercicio, fecha, serie_numero))
        existente = cursor.fetchone()

        if existente:
            # 2a. Si ya existe, la reemplazamos (actualizamos peso y repeticiones)
            sql = "UPDATE registros_entrenamiento SET peso_kg = %s, repeticiones = %s WHERE id_registro = %s"
            cursor.execute(sql, (peso_kg, repeticiones, existente[0]))
            resultado = "reemplazada"
        else:
            # 2b. Si no existe, la insertamos como serie nueva
            sql = """
                INSERT INTO registros_entrenamiento (dni_usuario, id_ejercicio, fecha, serie_numero, peso_kg, repeticiones)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (dni_usuario, id_ejercicio, fecha, serie_numero, peso_kg, repeticiones))
            resultado = "nueva"

        conexion.commit()
        cursor.close()
        return resultado
    except Error as e:
        print(f"Error al registrar serie: {e}")
        return False

def obtener_series_ejercicio_fecha_db(conexion, dni_usuario, id_ejercicio, fecha):
    """Devuelve las series (número, peso, repeticiones) de un ejercicio registradas en una fecha."""
    try:
        cursor = conexion.cursor()
        sql = """
            SELECT serie_numero, peso_kg, repeticiones
            FROM registros_entrenamiento
            WHERE dni_usuario = %s AND id_ejercicio = %s AND fecha = %s
            ORDER BY serie_numero
        """
        cursor.execute(sql, (dni_usuario, id_ejercicio, fecha))
        resultado = cursor.fetchall()
        cursor.close()
        return resultado
    except Error as e:
        print(f"Error al obtener series del ejercicio: {e}")
        return []

def obtener_ultima_fecha_ejercicio_db(conexion, dni_usuario, id_ejercicio, fecha_actual):
    """Devuelve la última fecha (anterior a hoy) en la que el usuario hizo ese ejercicio, o None."""
    try:
        cursor = conexion.cursor()
        sql = """
            SELECT MAX(fecha) FROM registros_entrenamiento
            WHERE dni_usuario = %s AND id_ejercicio = %s AND fecha < %s
        """
        cursor.execute(sql, (dni_usuario, id_ejercicio, fecha_actual))
        fila = cursor.fetchone()
        cursor.close()
        # MAX devuelve None si nunca hizo el ejercicio antes
        return fila[0] if fila else None
    except Error as e:
        print(f"Error al obtener la última fecha del ejercicio: {e}")
        return None

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

def obtener_fechas_entrenadas_db(conexion, dni_usuario):
    """Devuelve las fechas únicas en las que el usuario tiene entrenamientos registrados."""
    try:
        if not conexion:
            return []
        cursor = conexion.cursor()
        sql = """
            SELECT DISTINCT fecha
            FROM registros_entrenamiento
            WHERE dni_usuario = %s
            ORDER BY fecha DESC
        """
        cursor.execute(sql, (dni_usuario,))
        filas = cursor.fetchall()
        cursor.close()
        fechas = []
        for f in filas:
            val = f[0]
            fechas.append(val.strftime("%Y-%m-%d") if hasattr(val, 'strftime') else str(val))
        return fechas
    except Error as e:
        print(f"Error al obtener fechas entrenadas: {e}")
        return []

def obtener_registros_por_fecha_db(conexion, dni_usuario, fecha):
    """Devuelve los registros de entrenamiento de un usuario para una fecha específica."""
    try:
        if not conexion:
            return []
        cursor = conexion.cursor()
        sql = """
            SELECT r.fecha, e.nombre, r.serie_numero, r.peso_kg, r.repeticiones
            FROM registros_entrenamiento r
            JOIN ejercicios e ON r.id_ejercicio = e.id_ejercicio
            WHERE r.dni_usuario = %s AND r.fecha = %s
            ORDER BY e.nombre, r.serie_numero
        """
        cursor.execute(sql, (dni_usuario, fecha))
        filas = cursor.fetchall()
        cursor.close()
        return filas
    except Error as e:
        print(f"Error al obtener registros por fecha: {e}")
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
def obtener_detalle_rutina(conexion, id_rutina, dni_usuario):
    """Devuelve el nombre de la rutina y la lista de sus días con sus ejercicios (solo si es del usuario)."""
    try:
        cursor = conexion.cursor()
        # 1. Buscamos el nombre y cantidad de días de la rutina (verificando que sea del usuario)
        cursor.execute("SELECT nombre_rutina, cantidad_dias FROM rutinas WHERE id_rutina = %s AND dni_usuario = %s", (id_rutina, dni_usuario))
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
            grupos = []
            for ej in ejercicios_raw:
                lista_ejercicios.append({
                    'id': ej[0],
                    'nombre': ej[1],
                    'grupo': ej[2],
                    'series': ej[3]
                })
                # Juntamos todos los grupos musculares del día (sin repetir)
                if ej[2] not in grupos:
                    grupos.append(ej[2])

            # El grupo del día se arma con los grupos de sus ejercicios (ej: "Pecho, Hombros, Tríceps")
            if grupos:
                grupo = ", ".join(grupos)

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
def actualizar_rutina_completa_db(conexion, id_rutina, dni_usuario, nombre_rutina, estructura_dias):
    """Actualiza el nombre, los días y los ejercicios de una rutina ya creada (solo si es del usuario)."""
    try:
        cursor = conexion.cursor()
        # 0. Verificamos que la rutina le pertenezca al usuario
        cursor.execute("SELECT id_rutina FROM rutinas WHERE id_rutina = %s AND dni_usuario = %s", (id_rutina, dni_usuario))
        if not cursor.fetchone():
            cursor.close()
            return False

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
