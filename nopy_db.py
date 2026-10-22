# Módulo de Gestión de Base de Datos para 'No py, no gain'
# Maneja la conexión a MySQL y todas las operaciones CRUD (INSERT, SELECT, DELETE).

import mysql.connector
import customtkinter as ctk

# CONEXIÓN A LA BASE DE DATOS:

def conectar(ip, usuario, puerto, contraseña):
    """Establece la conexión con la base de datos MySQL 'nopy_nogain'."""
    connection = mysql.connector.connect(
        host=ip,
        user=usuario,
        password=contraseña,
        port=puerto,
        database='nopy_nogain'
    )
    print("¡Conectado a la Base de Datos 'nopy_nogain'!\n" + "-" * 40)
    return connection


def pedir_conexion(ip='127.0.0.1', usuario='root', puerto=3306):
    """
    Despliega una ventana gráfica para solicitar la contraseña de MySQL
    y devuelve el objeto de conexión activo.
    """
    conexion_activa = None

    class VentanaLogin(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Acceso BD - No py, no gain")
            self.geometry("320x220")
            ctk.set_appearance_mode("Dark")
            ctk.set_default_color_theme("green")

            self.label = ctk.CTkLabel(self, text="Conectar a Base de Datos", font=("Arial", 16, "bold"))
            self.label.pack(pady=15)

            self.entry_pass = ctk.CTkEntry(self, placeholder_text="Contraseña de MySQL", show="*", width=220)
            self.entry_pass.pack(pady=5)

            self.lbl_error = ctk.CTkLabel(self, text="", text_color="red", font=("Arial", 12))
            self.lbl_error.pack(pady=5)

            self.btn_ingresar = ctk.CTkButton(
                self, text="Ingresar", command=self.validar, 
                width=150, height=35, font=("Arial", 14, "bold")
            )
            self.btn_ingresar.pack(pady=5)

        def validar(self):
            nonlocal conexion_activa
            pwd = self.entry_pass.get()
            try:
                conexion_activa = conectar(ip, usuario, puerto, pwd)
                self.after(100, self.destroy)
            except Exception:
                self.lbl_error.configure(text="Contraseña incorrecta o BD inactiva")

    app_login = VentanaLogin()
    app_login.mainloop()
    return conexion_activa


# 1. OPERACIONES DE USUARIOS:

def buscar_usuario_db(conexion, dni):
    """Busca un usuario por su DNI. Retorna la tupla con los datos o None."""
    cursor = conexion.cursor()
    sql = "SELECT dni, nombre, apellido, altura, peso, sexo FROM usuarios WHERE dni = %s;"
    cursor.execute(sql, (dni,))
    resultado = cursor.fetchone()
    cursor.close()
    return resultado


def registrar_usuario_db(conexion, dni, nombre, apellido, altura, peso, sexo):
    """Inserta un nuevo usuario en la base de datos."""
    cursor = conexion.cursor()
    sql = """INSERT INTO usuarios (dni, nombre, apellido, altura, peso, sexo) 
             VALUES (%s, %s, %s, %s, %s, %s);"""
    cursor.execute(sql, (dni, nombre, apellido, altura, peso, sexo))
    conexion.commit()
    cursor.close()


# 2. OPERACIONES DE EJERCICIOS (CATÁLOGO):

def obtener_ejercicios_por_grupo(conexion, grupo_muscular="Todos"):
    """
    Retorna la lista de ejercicios. Si se especifica un grupo muscular,
    filtra la consulta.
    """
    cursor = conexion.cursor()
    if grupo_muscular == "Todos" or not grupo_muscular:
        sql = "SELECT id_ejercicio, nombre, grupo_muscular, descripcion FROM ejercicios ORDER BY grupo_muscular, nombre;"
        cursor.execute(sql)
    else:
        sql = "SELECT id_ejercicio, nombre, grupo_muscular, descripcion FROM ejercicios WHERE grupo_muscular = %s ORDER BY nombre;"
        cursor.execute(sql, (grupo_muscular,))
    
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def agregar_ejercicio_db(conexion, nombre, grupo_muscular, descripcion=""):
    """Agrega un nuevo ejercicio personalizado al catálogo."""
    cursor = conexion.cursor()
    sql = "INSERT INTO ejercicios (nombre, grupo_muscular, descripcion) VALUES (%s, %s, %s);"
    cursor.execute(sql, (nombre, grupo_muscular, descripcion))
    conexion.commit()
    cursor.close()


# 3. OPERACIONES DE RUTINAS:

def guardar_rutina_completa_db(conexion, dni_usuario, nombre_rutina, estructura_dias):
    """
    Guarda una rutina completa con sus días y ejercicios asociados.
    
    'estructura_dias' debe ser una lista con la estructura de cada día:
    [
        {'numero_dia': 1, 'grupo': 'Piernas', 'ejercicios_ids': [1, 4]},
        {'numero_dia': 2, 'grupo': 'Pecho', 'ejercicios_ids': [5, 6]}
    ]
    """
    cursor = conexion.cursor()

    # 1. Insertar el encabezado de la rutina
    sql_rutina = "INSERT INTO rutinas (dni_usuario, nombre_rutina, cantidad_dias) VALUES (%s, %s, %s);"
    cursor.execute(sql_rutina, (dni_usuario, nombre_rutina, len(estructura_dias)))
    id_rutina = cursor.lastrowid  # Obtiene el ID autogenerado de la rutina

    # 2. Insertar cada día de la rutina y sus ejercicios
    for dia in estructura_dias:
        sql_dia = "INSERT INTO rutina_dias (id_rutina, numero_dia, grupo_muscular) VALUES (%s, %s, %s);"
        cursor.execute(sql_dia, (id_rutina, dia['numero_dia'], dia['grupo']))
        id_rutina_dia = cursor.lastrowid

        # Insertar los ejercicios asignados a este día
        for id_ejercicio in dia['ejercicios_ids']:
            sql_ejercicio = "INSERT INTO rutina_ejercicios (id_rutina_dia, id_ejercicio) VALUES (%s, %s);"
            cursor.execute(sql_ejercicio, (id_rutina_dia, id_ejercicio))

    conexion.commit()
    cursor.close()


def obtener_rutinas_usuario(conexion, dni_usuario):
    """Retorna todas las rutinas creadas por un usuario en específico."""
    cursor = conexion.cursor()
    sql = "SELECT id_rutina, nombre_rutina, cantidad_dias FROM rutinas WHERE dni_usuario = %s;"
    cursor.execute(sql, (dni_usuario,))
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def obtener_dias_de_rutina(conexion, id_rutina):
    """Retorna los días de una rutina junto a su grupo muscular."""
    cursor = conexion.cursor()
    sql = "SELECT id_rutina_dia, numero_dia, grupo_muscular FROM rutina_dias WHERE id_rutina = %s ORDER BY numero_dia;"
    cursor.execute(sql, (id_rutina,))
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def obtener_ejercicios_de_dia(conexion, id_rutina_dia):
    """Retorna los ejercicios asignados a un día de rutina específico."""
    cursor = conexion.cursor()
    sql = """
        SELECT e.id_ejercicio, e.nombre, e.grupo_muscular 
        FROM rutina_ejercicios re
        JOIN ejercicios e ON re.id_ejercicio = e.id_ejercicio
        WHERE re.id_rutina_dia = %s;
    """
    cursor.execute(sql, (id_rutina_dia,))
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


# 4. OPERACIONES DE SEGUIMIENTO Y REGISTRO DE ENTRENAMIENTO:

def registrar_entrenamiento_db(conexion, dni_usuario, id_ejercicio, fecha, asistio, serie_numero=1, peso_kg=0.0, repeticiones=0):
    """Guarda una serie o inasistencia en el historial de entrenamiento."""
    cursor = conexion.cursor()
    sql = """
        INSERT INTO registros_entrenamiento (dni_usuario, id_ejercicio, fecha, asistio, serie_numero, peso_kg, repeticiones)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    cursor.execute(sql, (dni_usuario, id_ejercicio, fecha, asistio, serie_numero, peso_kg, repeticiones))
    conexion.commit()
    cursor.close()


def obtener_historial_usuario(conexion, dni_usuario):
    """Retorna el historial completo de entrenamientos ordenado por fecha."""
    cursor = conexion.cursor()
    sql = """
        SELECT r.fecha, e.nombre, e.grupo_muscular, r.asistio, r.serie_numero, r.peso_kg, r.repeticiones
        FROM registros_entrenamiento r
        JOIN ejercicios e ON r.id_ejercicio = e.id_ejercicio
        WHERE r.dni_usuario = %s
        ORDER BY r.fecha DESC, r.id_registro DESC;
    """
    cursor.execute(sql, (dni_usuario,))
    resultado = cursor.fetchall()
    cursor.close()
    return resultado