"""
Módulo de Clases (POO) para 'No py, no gain'
Define las entidades principales del sistema alineadas con la base de datos 
y el diagrama de flujo.
"""

class Usuario:
    """Clase que representa a un usuario/atleta del sistema."""
    def __init__(self, dni, nombre, apellido, peso, altura, sexo):
        self.dni = dni
        self.nombre = nombre
        self.apellido = apellido
        self.peso = peso
        self.altura = altura
        self.sexo = sexo

    def __str__(self):
        return f"{self.nombre} {self.apellido} (DNI: {self.dni})"


class Ejercicio:
    """Clase que representa un ejercicio del catálogo con su tipo y grupo muscular."""
    def __init__(self, id_ejercicio, nombre, grupo_muscular, tipo_ejercicio, dni_usuario=None):
        self.id_ejercicio = id_ejercicio
        self.dni_usuario = dni_usuario
        self.nombre = nombre
        self.grupo_muscular = grupo_muscular
        self.tipo_ejercicio = tipo_ejercicio

    def __str__(self):
        return f"{self.nombre} [{self.grupo_muscular} - {self.tipo_ejercicio}]"


class Rutina:
    """Clase para gestionar las rutinas creadas por el usuario."""
    def __init__(self, id_rutina, dni_usuario, nombre_rutina, cantidad_dias):
        self.id_rutina = id_rutina
        self.dni_usuario = dni_usuario
        self.nombre_rutina = nombre_rutina
        self.cantidad_dias = cantidad_dias

    def __str__(self):
        return f"Rutina: {self.nombre_rutina} ({self.cantidad_dias} días)"


class RegistroEntrenamiento:
    """Clase para modelar el rendimiento y sobrecarga progresiva en cada serie."""
    def __init__(self, id_registro, dni_usuario, id_ejercicio, fecha, serie_numero, peso_kg, repeticiones):
        self.id_registro = id_registro
        self.dni_usuario = dni_usuario
        self.id_ejercicio = id_ejercicio
        self.fecha = fecha
        self.serie_numero = serie_numero
        self.peso_kg = peso_kg
        self.repeticiones = repeticiones

    def __str__(self):
        return f"Fecha: {self.fecha} | Serie {self.serie_numero}: {self.peso_kg}kg x {self.repeticiones} reps"