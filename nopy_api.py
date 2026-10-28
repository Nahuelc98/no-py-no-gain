"""
Módulo de Integración con IA para 'No py, no gain'
Procesa los registros de entrenamiento del usuario y genera un análisis de rendimiento.
"""

from google import genai  # Importamos librería de gemini ia.
# Asegúrate de crear este archivo con tu clave o importarla de donde corresponda
from claves_nopy import API_NOPY 

def analizar_rendimiento_usuario(registros_entrenamiento, nombre_usuario="Atleta"):
    """
    Envía los registros de entrenamiento a la IA para obtener un análisis completo,
    puntos fuertes, débiles, consejos y conclusión.
    """
    client = genai.Client(api_key=API_NOPY)
    
    print("   --- ANALIZANDO RENDIMIENTO CON IA ---   ")
    print("-" * 40)

    # Convertimos los registros obtenidos de la BD en un texto legible para la IA
    historial_texto = ""
    if registros_entrenamiento:
        for reg in registros_entrenamiento:
            # Estructura típica: (fecha, nombre_ejercicio, serie_numero, peso_kg, repeticiones)
            fecha, ejercicio, serie, peso, reps = reg
            historial_texto += f"- Fecha: {fecha} | Ejercicio: {ejercicio} | Serie {serie}: {peso}kg x {reps} reps\n"
    else:
        historial_texto = "El usuario aún no registra entrenamientos en la base de datos."

    # Prompt estructurado, claro y conciso
    prompt = f"""
    Actúa como un entrenador personal experto en ciencias del deporte, hipertrofia y sobrecarga progresiva.
    Analiza el siguiente historial de entrenamiento del usuario {nombre_usuario}:

    {historial_texto}

    Por favor, genera un informe estructurado que contenga estrictamente lo siguiente:
    1. **Estadísticas y Análisis de Progreso**: Evalúa la evolución de los pesos y repeticiones a lo largo del tiempo.
    2. **Puntos Fuertes**: Identifica en qué ejercicios o rangos muestra mayor solidez.
    3. **Puntos Débiles**: Detecta estancamientos o áreas de mejora (ej. falta de frecuencia o progresión en ciertos grupos).
    4. **Consejos para Mejorar**: Brinda recomendaciones prácticas y directas para optimizar sus rutinas y ganancias musculares.
    5. **Conclusión**: Una síntesis motivadora y profesional de su estado actual.

    Mantén un tono profesional, claro y directo.
    """

    # Solicitud al modelo de Gemini
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt
    )
    
    print(response.text)

    # Escribimos la respuesta de la IA en un archivo .txt local
    respuesta = str(response.text)
    nombre_archivo = f"analisis_{nombre_usuario.lower().replace(' ', '_')}.txt"
    with open(nombre_archivo, "w", encoding="utf-8") as archivo_txt:
        archivo_txt.write(respuesta)
    
    print(f"\n✔ Análisis guardado exitosamente en '{nombre_archivo}'.")
    return respuesta