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

    def nombre_completo(self):
        """Devuelve el nombre y apellido juntos (se usa en la bienvenida, el txt y la IA)."""
        return f"{self.nombre} {self.apellido}"

    def calcular_imc(self):
        """Calcula el Índice de Masa Corporal (IMC = peso / altura²)."""
        try:
            peso = float(self.peso)
            altura = float(self.altura)
            # Si la altura se cargó en centímetros (ej: 175) la pasamos a metros (1.75)
            if altura > 3:
                altura = altura / 100
            if altura <= 0:
                return 0
            return round(peso / (altura * altura), 1)
        except (ValueError, TypeError):
            # Si el peso o la altura no son números válidos devolvemos 0
            return 0


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

    def calcular_volumen(self):
        """Calcula el volumen de la serie (peso x repeticiones)."""
        return self.peso_kg * self.repeticiones