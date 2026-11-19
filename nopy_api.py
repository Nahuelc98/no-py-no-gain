"""
Módulo de Integración con IA para 'No py, no gain'
Procesa los registros de entrenamiento del usuario y genera un análisis de rendimiento.
"""

import time  # Para esperar unos segundos entre un intento y otro.
from google import genai  # Importamos librería de gemini ia.
from claves_nopy import API_NOPY  # Traemos la variable con la clave de la api de gemini.

# Modelo de Gemini: "gemini-3.5-flash-lite"
MODELO_IA = "gemini-3.5-flash-lite"

# Tiempo máximo de espera (en milisegundos): 90 segundos. 
# Si no responde en ese tiempo, se muestra un mensaje de error para no dejar la aplicación esperando.
TIEMPO_MAXIMO_IA = 90000

# Cantidad de veces que le pedimos el informe a la IA si Google está saturado,
# y segundos que esperamos entre un intento y otro.
CANTIDAD_INTENTOS = 3
SEGUNDOS_ENTRE_INTENTOS = 5

def limpiar_formato(texto):
    """
    Quita los símbolos de formato (Markdown y fórmulas) que devuelve la IA, como ** para negrita,
    # para títulos o $\\rightarrow$ para flechas, porque el cuadro de texto de la interfaz no los interpreta.
    """
    texto = texto.replace("**", "")
    # Flechas escritas como fórmulas matemáticas: las cambiamos por flechas comunes
    texto = texto.replace("$\\rightarrow$", "→").replace("$\\to$", "→").replace("\\rightarrow", "→")
    texto = texto.replace("$\\leftarrow$", "←").replace("\\leftarrow", "←")
    texto = texto.replace("$", "")
    lineas_limpias = []
    for linea in texto.split("\n"):
        # Si la línea empieza con # (título), sacamos los # del principio
        if linea.strip().startswith("#"):
            linea = linea.strip().lstrip("#").strip()
        # Si la línea es una viñeta con * la cambiamos por •
        elif linea.strip().startswith("* "):
            sangria = linea[:len(linea) - len(linea.lstrip())]
            linea = sangria + "• " + linea.strip()[2:].strip()
        # Las líneas de separación "---" las dejamos vacías
        elif linea.strip() == "---":
            linea = ""
        # Los * que quedan son de texto en cursiva (*texto*): los sacamos
        linea = linea.replace("*", "")
        lineas_limpias.append(linea)
    return "\n".join(lineas_limpias)

def armar_datos_personales(usuario, nombre_usuario):
    """
    Arma el texto con los datos personales del usuario que se le envían a la IA:
    nombre, sexo, peso, altura e IMC (el DNI NO se envía porque no hace falta para el análisis).
    """
    if not usuario:
        return f"- Nombre: {nombre_usuario}\n- (No hay más datos personales disponibles)"
    textos_sexo = {"M": "Masculino", "F": "Femenino"}
    sexo = textos_sexo.get(usuario.sexo, "Otro")
    texto = f"- Nombre: {usuario.nombre_completo()}\n"
    texto += f"- Sexo: {sexo}\n"
    # Usamos el método calcular_imc() de la clase Usuario
    texto += f"- Peso: {usuario.peso} kg | Altura: {usuario.altura} m | IMC: {usuario.calcular_imc()}"
    return texto

def analizar_rendimiento_usuario(registros_entrenamiento, nombre_usuario="Atleta", usuario=None):
    """
    Envía los datos personales del usuario (objeto Usuario) y sus registros de entrenamiento a la IA
    para obtener un informe con conclusiones, puntos fuertes, puntos débiles y consejos.
    """
    print("   --- ANALIZANDO RENDIMIENTO CON IA ---   ")
    print("-" * 40)

    # 1. Datos personales del usuario (nombre, sexo, peso, altura e IMC)
    datos_personales = armar_datos_personales(usuario, nombre_usuario)

    # 2. Convertimos los registros obtenidos de la BD en un texto legible para la IA
    historial_texto = ""
    if registros_entrenamiento:
        for reg in registros_entrenamiento:
            # Cada registro tiene: (fecha, nombre_ejercicio, serie_numero, peso_kg, repeticiones)
            fecha, ejercicio, serie, peso, reps = reg
            historial_texto += f"- Fecha: {fecha} | Ejercicio: {ejercicio} | Serie {serie}: {peso}kg x {reps} reps\n"
    else:
        historial_texto = "El usuario aún no registra entrenamientos en la base de datos."

    # 3. Prompt fijo: la IA solo analiza los datos del usuario y devuelve el informe
    prompt = f"""
Analizá la información de un usuario de una aplicación de seguimiento de gimnasio.

DATOS PERSONALES:
{datos_personales}

REGISTROS DE ENTRENAMIENTO (fecha, ejercicio, serie, peso y repeticiones; 0 kg = peso corporal):
{historial_texto}

Con esa información, escribí un informe con estas secciones:
1. Conclusiones generales
2. Puntos fuertes
3. Puntos débiles
4. Consejos para mejorar
5. Conclusión final

Reglas:
- Basate SOLO en los datos personales y los registros de arriba. No inventes información que no esté ahí.
- En cada conclusión mencioná los datos en los que te basás (ejercicio, fechas, pesos o repeticiones).
- Los consejos tienen que ser concretos y surgir de los registros y del perfil del usuario.
- No agregues explicaciones científicas generales ni temas que no sean el entrenamiento de este usuario.
- Escribí en español, de forma clara y breve, sin símbolos de formato como **, # o $.
- Usá la ortografía correcta del español, con todas sus tildes (por ejemplo: días, comenzó, débiles).
"""

    # Si Google está saturado la IA puede no responder, así que lo intentamos hasta 3 veces
    ultimo_error = None
    for intento in range(1, CANTIDAD_INTENTOS + 1):
        try:
            # Conectamos con Gemini usando la clave de la API y el tiempo máximo de espera
            client = genai.Client(api_key=API_NOPY, http_options={"timeout": TIEMPO_MAXIMO_IA})

            # Solicitud al modelo de Gemini
            response = client.models.generate_content(
                model=MODELO_IA,  # Elegir el modelo de LLM
                contents=prompt
            )
            print(response.text)

            # Limpiamos los símbolos de formato (**, #, $...) para que se lea bien en la interfaz
            # y devolvemos el informe para mostrarlo en pantalla
            respuesta = limpiar_formato(str(response.text))
            return respuesta
        except Exception as e:
            # Guardamos el error para mostrarlo si fallan todos los intentos
            ultimo_error = e
            print(f"[!] Intento {intento} de {CANTIDAD_INTENTOS}: la IA no respondió. Detalle: {e}")
            # Si quedan intentos, esperamos unos segundos antes de volver a probar
            if intento < CANTIDAD_INTENTOS:
                time.sleep(SEGUNDOS_ENTRE_INTENTOS)

    # Si la IA no respondió en ningún intento, devolvemos un mensaje claro para mostrar en la interfaz
    error_msg = (
        "[!] No se pudo conectar con la Inteligencia Artificial.\n"
        "Puede ser un problema de conexión a internet, de la API key en claves_nopy.py "
        "o que los servidores de Google estén saturados. Probá de nuevo en unos minutos.\n"
        f"Detalle: {ultimo_error}"
    )
    print(error_msg)
    return error_msg