"""
Módulo de Integración con IA para 'No py, no gain'
Procesa los registros de entrenamiento del usuario y genera un análisis de rendimiento.
"""

import os
from google import genai  # Importamos librería de gemini ia.
from google.genai import types  # Para configurar el tiempo máximo de espera
# Asegúrate de crear este archivo con tu clave o importarla de donde corresponda
from claves_nopy import API_NOPY

# Modelos de Gemini que se prueban en orden. Si uno no responde (Google lo dio de baja
# o está saturado), se intenta con el siguiente:
# - "gemini-flash-lite-latest": versión liviana y la más rápida (escribe el informe en unos 5 segundos).
# - "gemini-3.5-flash": más completo, pero más lento cuando hay mucha demanda.
# - "gemini-flash-latest": siempre apunta al modelo Flash más nuevo (no se vence cuando Google retira modelos).
MODELOS_IA = ["gemini-flash-lite-latest", "gemini-3.5-flash", "gemini-flash-latest"]

# Tiempo máximo de espera por cada modelo (en milisegundos). Si no responde en ese tiempo,
# pasamos al siguiente modelo en lugar de dejar la aplicación esperando varios minutos.
TIEMPO_MAXIMO_IA = 30000

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
            # Estructura típica: (fecha, nombre_ejercicio, serie_numero, peso_kg, repeticiones)
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

    try:
        client = genai.Client(api_key=API_NOPY, http_options=types.HttpOptions(timeout=TIEMPO_MAXIMO_IA))
    except Exception as e:
        error_msg = f"[!] No se pudo conectar con la Inteligencia Artificial (revisá la API key en claves_nopy.py).\nDetalle: {e}"
        print(error_msg)
        return error_msg

    # Probamos los modelos en orden: si uno falla, intentamos con el siguiente
    ultimo_error = None
    for modelo in MODELOS_IA:
        try:
            # Solicitud al modelo de Gemini
            response = client.models.generate_content(
                model=modelo,
                contents=prompt
            )

            print(f"[OK] Respuesta generada con el modelo '{modelo}'.")
            print(response.text)

            # Escribimos la respuesta de la IA en un archivo .txt local
            # Limpiamos los símbolos de formato (**, #, $...) para que se lea bien en la interfaz
            respuesta = limpiar_formato(str(response.text))
            # El archivo se guarda en la carpeta del proyecto (no importa desde dónde se ejecute la app)
            dir_actual = os.path.dirname(os.path.abspath(__file__))
            nombre_archivo = f"analisis_{nombre_usuario.lower().replace(' ', '_')}.txt"
            ruta_archivo = os.path.join(dir_actual, nombre_archivo)
            with open(ruta_archivo, "w", encoding="utf-8") as archivo_txt:
                archivo_txt.write(respuesta)

            print(f"\n[OK] Análisis guardado exitosamente en '{nombre_archivo}'.")
            return respuesta
        except Exception as e:
            # Guardamos el error y seguimos con el próximo modelo de la lista
            print(f"[!] El modelo '{modelo}' no respondió: {e}")
            ultimo_error = e

    # Si ningún modelo respondió, devolvemos un mensaje claro para mostrar en la interfaz
    error_msg = (
        "[!] No se pudo conectar con la Inteligencia Artificial.\n"
        "Puede ser un problema de conexión a internet o que los servidores de Google estén saturados. "
        "Probá de nuevo en unos minutos.\n"
        f"Detalle: {ultimo_error}"
    )
    print(error_msg)
    return error_msg