# Módulo de Clases (POO) para 'No py, no gain'
# Define las entidades principales del sistema: Usuario, Ejercicio y Rutina.

class Usuario:
    """Clase que representa a un usuario/atleta del gimnasio."""
    def __init__(self, dni, nombre, apellido, altura, peso, sexo):
        self.dni = dni
        self.nombre = nombre
        self.apellido = apellido
        self.altura = altura
        self.peso = peso
        self.sexo = sexo

    def __str__(self):
        return f"{self.nombre} {self.apellido} (DNI: {self.dni})"


class Ejercicio:
    """Clase que representa un ejercicio del catálogo."""
    def __init__(self, id_ejercicio, nombre, grupo_muscular, descripcion=""):
        self.id_ejercicio = id_ejercicio
        self.nombre = nombre
        self.grupo_muscular = grupo_muscular
        self.descripcion = descripcion

    def __str__(self):
        return f"{self.nombre} [{self.grupo_muscular}]"


class Rutina:
    """Clase para gestionar las rutinas de los usuarios."""
    def __init__(self, id_rutina, dni_usuario, nombre_rutina, cantidad_dias):
        self.id_rutina = id_rutina
        self.dni_usuario = dni_usuario
        self.nombre_rutina = nombre_rutina
        self.cantidad_dias = cantidad_dias

    def __str__(self):
        return f"Rutina: {self.nombre_rutina} ({self.cantidad_dias} días)"