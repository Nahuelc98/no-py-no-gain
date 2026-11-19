# NO PY, NO GAIN

Trabajo integrador para la **Academia de Desarrollo 2026** (Programación en Python).

**NO PY, NO GAIN** es una aplicación para el gimnasio. Sirve para armar tus rutinas, anotar lo que levantás en cada serie, ver tu progreso en un calendario y pedirle a una Inteligencia Artificial (Google Gemini) un análisis de tu entrenamiento.

---

## Qué necesitás

- **Python 3.13** o superior.
- **MySQL** (por ejemplo, con MySQL Workbench).
- **Internet**, solo para el análisis con IA.
- Las librerías del proyecto, que se instalan con:

```bash
pip install customtkinter pillow mysql-connector-python google-genai
```

---

## Cómo ponerla en marcha

**1. Crear la base de datos:** abrí MySQL Workbench y ejecutá el archivo `nopy-nogain.sql`. Crea la base de datos con sus tablas, 44 ejercicios ya cargados y dos usuarios de prueba.

**2. Crear el archivo de claves:** en la carpeta del proyecto creá un archivo llamado `claves_nopy.py` con esto:

```python
DB_CONTRASEÑA = "tu_contraseña_de_mysql"
API_NOPY = "tu_api_key_de_gemini"   # Se obtiene gratis en https://aistudio.google.com/
```

Este archivo no se sube a GitHub para que las claves queden privadas.

**3. Abrir la aplicación:**

```bash
python nopy_nogain.py
```

---

## Cómo se usa

Todo pasa en una sola ventana. En cada pantalla, el botón **◀ Volver** te lleva a la anterior.

**Ingresar:** escribí tu DNI y tocá **INGRESAR**. Si es la primera vez, tocá **Regístrate aquí** y completá tus datos.

Una vez adentro, el menú tiene cinco botones:

1. **Gestionar Rutina**
   - **Crear Rutina:** le ponés un nombre, elegís cuántos días tiene y, para cada día, agregás ejercicios con su cantidad de series. Con el botón **+** podés crear un ejercicio que no esté en la lista.
   - **Mis Rutinas:** ves tus rutinas y podés editarlas o eliminarlas.
   - **Mis Ejercicios:** creás, editás o eliminás tus propios ejercicios.
2. **Empezar Rutina:** elegís la rutina y la app te sugiere el día que te toca. Para cada serie anotás el peso y las repeticiones y tocás **Guardar Registro**. La app te muestra en qué serie vas y qué hiciste la última vez. Para ejercicios sin peso (como dominadas) poné 0 kg.
3. **Ver Seguimiento:**
   - **Calendario:** los días que entrenaste aparecen en verde.
   - **Comparar dos días:** elegí una **Fecha 1** y una **Fecha 2** del mismo día de tu rutina y tocá **Comparar Fecha 1 con Fecha 2** para ver si mejoraste.
   - **Analizar Rendimiento:** la IA lee tus datos y tus entrenamientos y te da conclusiones, puntos fuertes, puntos débiles y consejos. Tu DNI no se le envía.
4. **Mi Perfil:** ves y editás tus datos (nombre, peso, altura, sexo) y tu IMC.
5. **Cerrar Sesión:** volvés a la pantalla de inicio.

Cada vez que alguien inicia sesión, cierra sesión o se registra, queda anotado en `accion_usuario.txt`. La app lee ese archivo para mostrarte, debajo de **Cerrar Sesión**, la fecha y hora de tu último ingreso (la primera vez dice "es tu primer ingreso").

---

## Usuarios de prueba

Para ver la app con datos sin cargar nada a mano, ingresá con alguno de estos DNI. Tienen tres meses de entrenamientos ficticios (del 01/09/2026 al 14/11/2026).

| Usuario | DNI | Fechas para comparar en Ver Seguimiento |
|---|---|---|
| Martín Prueba | `40123123` | 02/09/2026 y 11/11/2026 |
| Agustina Prueba | `40321321` | 04/09/2026 y 09/11/2026 |

Para borrarlos con todos sus datos:

```sql
DELETE FROM usuarios WHERE dni IN ('40123123', '40321321');
```

---

## Archivos del proyecto

- `nopy_nogain.py`: archivo principal, el que se ejecuta.
- `nopy_interfaz.py`: las pantallas de la aplicación.
- `nopy_db.py`: la conexión con la base de datos.
- `nopy_clases.py`: las clases (Usuario, Ejercicio, Rutina y RegistroEntrenamiento).
- `nopy_api.py`: la conexión con la IA.
- `nopy-nogain.sql`: crea la base de datos.

---

## Autor
Nahuel Cuello — Academia de Desarrollo 2026.
