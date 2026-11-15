# NO PY, NO GAIN

Trabajo integrador para la **Academia de Desarrollo 2026** (Programación en Python).

**NO PY, NO GAIN** es una aplicación de escritorio para planificar rutinas de gimnasio y hacer el seguimiento del entrenamiento. Permite armar rutinas por días con ejercicios precargados o propios, registrar el peso y las repeticiones de cada serie mientras entrenás (la app te guía: qué día toca, en qué serie vas y qué hiciste la última vez), ver el progreso en un calendario, comparar dos sesiones del mismo día de la rutina y pedir un análisis hecho por Inteligencia Artificial (Google Gemini).

---

## Requisitos del sistema

- **Python 3.13** (o superior).
- **MySQL Server 8** (por ejemplo, con MySQL Workbench).
- **Conexión a internet** (solo para el análisis con IA).
- Librerías externas de Python:

| Librería | Para qué se usa |
|---|---|
| `customtkinter` | Interfaz gráfica |
| `pillow` | Mostrar el logo de la aplicación |
| `mysql-connector-python` | Conexión con la base de datos MySQL |
| `google-genai` | Conexión con la API de Google Gemini |

Se instalan todas juntas con:

```bash
pip install customtkinter pillow mysql-connector-python google-genai
```

Librerías estándar usadas (vienen con Python): `os`, `datetime`, `calendar`.

---

## Instalación y configuración

### 1. Crear la base de datos
Abrir MySQL Workbench (o la consola de MySQL) y ejecutar el script `nopy-nogain.sql` (está en la carpeta del proyecto).
Esto crea la base de datos `nopy_nogain`, sus 6 tablas (`usuarios`, `ejercicios`, `rutinas`, `rutina_dias`, `rutina_ejercicios`, `registros_entrenamiento`) y carga 44 ejercicios iniciales.

> La conexión está configurada en `nopy_nogain.py` con: host `127.0.0.1`, usuario `root`, puerto `3306` y base de datos `nopy_nogain`. Si tu MySQL usa otros datos, modificalos en esa línea.

#### ¿Ya tenías la base creada con una versión anterior?
El script usa `CREATE TABLE IF NOT EXISTS`, así que no modifica tablas que ya existen. Si tu base es de una versión anterior, ejecutá además estas líneas (agregan las columnas y reglas nuevas, sin borrar datos):

```sql
USE nopy_nogain;

-- Baja lógica de ejercicios (al eliminar un ejercicio se conserva su historial)
ALTER TABLE ejercicios ADD COLUMN activo BOOLEAN DEFAULT TRUE AFTER tipo_ejercicio;

-- Una misma serie no puede repetirse el mismo día (si ya tenés series duplicadas, borralas antes)
ALTER TABLE registros_entrenamiento
ADD UNIQUE KEY serie_unica (dni_usuario, id_ejercicio, fecha, serie_numero);

-- Rutina y día que se estaba entrenando en cada serie (para comparar días iguales)
ALTER TABLE registros_entrenamiento
ADD COLUMN id_rutina INT DEFAULT NULL AFTER id_ejercicio,
ADD COLUMN numero_dia INT DEFAULT NULL AFTER id_rutina,
ADD FOREIGN KEY (id_rutina) REFERENCES rutinas(id_rutina) ON DELETE SET NULL;
```

Si alguna de estas columnas ya existe, MySQL avisa con un error y no cambia nada; se puede seguir con la siguiente.

### 2. Crear el archivo de claves
Por seguridad las contraseñas **no se suben a GitHub** (el archivo está en `.gitignore`).
Hay que crear un archivo llamado `claves_nopy.py` en la misma carpeta que el proyecto con este contenido:

```python
# Contraseña del usuario root de MySQL
DB_CONTRASEÑA = "tu_contraseña_de_mysql"

# Clave de la API de Google Gemini (se obtiene en https://aistudio.google.com/)
API_NOPY = "tu_api_key_de_gemini"
```

### 3. Ejecutar la aplicación
Desde la carpeta del proyecto ejecutar el archivo principal:

```bash
python nopy_nogain.py
```

Si la conexión con MySQL es correcta, en la consola aparece `[OK] Conexión exitosa a la Base de Datos MySQL.` y se abre la ventana principal.

---

## Usuarios de prueba

El script `nopy-nogain.sql` también carga **dos usuarios de prueba con datos ficticios**. Los creé para que se pueda ver cómo funciona la interfaz con muchos registros (calendario, comparaciones, "Última vez" e informe de la IA) sin tener que cargar entrenamientos a mano. Tienen **tres meses de uso simulado, del 01/09/2026 al 14/11/2026**, con progreso, algunos estancamientos y días sin entrenar, como una persona real.

| Usuario | DNI para ingresar | Rutinas | Ejercicios propios | Registros |
|---|---|---|---|---|
| **Martín Prueba** | `40123123` | Push Pull Legs (3 días) y Full Body (viaje) (2 días) | Remo en máquina Hammer, Press de pecho en máquina Hammer | 28 días entrenados (431 series) |
| **Agustina Prueba** | `40321321` | Torso / Pierna (4 días) y Glúteos y Abdomen (extra) (1 día) | Hip thrust con barra, Patada de glúteo en polea | 42 días entrenados (667 series) |

Ideas para probar en **Ver Seguimiento** (Fecha 1 en septiembre y Fecha 2 en noviembre, mismo día de la rutina):
- **Martín:** Fecha 1 = **02/09/2026** y Fecha 2 = **11/11/2026** (Día 1 de Push Pull Legs).
- **Agustina:** Fecha 1 = **04/09/2026** y Fecha 2 = **09/11/2026** (Día 3 de Torso / Pierna).

Si la base de datos ya estaba creada antes, ejecutá solo la sección **"USUARIOS DE PRUEBA"** del script (para no duplicar los ejercicios precargados). Para borrar los usuarios de prueba y todos sus datos:

```sql
DELETE FROM usuarios WHERE dni IN ('40123123', '40321321');
```

---

## Cómo usar la aplicación

Toda la aplicación funciona en **una sola ventana** de tamaño fijo: al tocar un botón, la pantalla cambia sin abrir ventanas nuevas. En cada sección, el botón **◀ Volver** (arriba a la izquierda, siempre visible) vuelve a la pantalla anterior. Los avisos y errores se muestran dentro de la misma pantalla y las fechas se muestran en formato **dd/mm/aaaa**. Los cuadros de texto (por ejemplo, "Rutina armada" o el informe de la IA) son solo para leer: su texto se puede seleccionar y copiar, pero no modificar.

### Ventana inicial
- **Ingresar con Documento:** escribir el DNI (se puede escribir con puntos, ej: `30.123.456`) y presionar **INGRESAR**. Si el DNI no está registrado se muestra un aviso.
- **¿No estás registrado? Regístrate aquí:** abre la pantalla **Regístrate** (DNI, nombre, apellido, peso, altura y sexo). El DNI debe tener entre 7 y 8 números y el peso y la altura deben ser números. Los nombres se guardan con mayúscula inicial. Al guardar, vuelve al inicio con el DNI ya cargado.
- **Cerrar No py, no gain:** cierra la aplicación.

### Menú principal
Al ingresar aparece un saludo con el nombre del usuario y cinco botones:

#### 1. Gestionar Rutina
Tiene tres opciones:
- **Crear Rutina:**
  - Ponerle un nombre y elegir la cantidad de días (1 a 7).
  - Para cada día: elegir el **grupo muscular**, el **ejercicio** (la lista muestra solo los ejercicios de ese grupo, por su nombre) y la **cantidad de series** (de 1 a 10, con las flechas ▲ ▼ o escribiendo el número). Presionar **Agregar Ejercicio al Día Actual**.
  - Con el botón **+** se puede crear un ejercicio propio sin salir de la pantalla.
  - Si te equivocaste, elegí el ejercicio en la lista de abajo y tocá **Quitar**.
  - Si cambiás la cantidad de días, no se borra lo cargado: solo se quitan los días que quedan afuera (y se avisa).
  - Al final, **Guardar Rutina**. Todos los días deben tener al menos un ejercicio.
- **Mis Rutinas:** elegí una rutina de la lista para ver sus días (con los grupos musculares de cada uno) y sus ejercicios. Desde ahí se puede **Editar Rutina** (abre la rutina con sus datos cargados) o **Eliminar Rutina** (hay que tocarlo dos veces para confirmar). Cada usuario solo ve y modifica sus propias rutinas.
- **Mis Ejercicios:** crear, editar (con sus datos ya cargados) o eliminar ejercicios propios. Los ejercicios precargados no se pueden modificar. Al eliminar un ejercicio se quita de las rutinas, pero **su historial de entrenamiento se conserva** (baja lógica).

#### 2. Empezar Rutina
- Elegir la rutina: la aplicación **sugiere el día que te toca** (el siguiente al último que entrenaste) y lo deja elegido. Si hoy ya entrenaste, sugiere el mismo día para seguir cargando series.
- Para cada ejercicio se muestra **"Serie X de N"**, las series que ya hiciste hoy y **lo que hiciste la última vez** en ese ejercicio.
- El **N° de serie** se completa solo y tiene flechas ▲ ▼: solo va de 1 hasta las series planificadas para ese ejercicio.
- Anotar el **peso (kg)** y las **repeticiones** y presionar **Guardar Registro**. La serie se guarda con la fecha de hoy y se muestra su volumen (peso × repeticiones).
- Para ejercicios con peso corporal (ej: dominadas) se carga **0 kg** y se registran las repeticiones.
- Cada serie se registra una sola vez por día: si cargás de nuevo una serie que ya existe (por ejemplo, para corregir un error), **se reemplaza**.
- Al completar las series de un ejercicio, **pasa solo al siguiente ejercicio** del día. Al terminar el último, avisa que terminaste el día.

#### 3. Ver Seguimiento
- **Calendario interactivo:** se puede cambiar de mes. Al tocar un día aparece, por ejemplo:
  - `09/11/2026: Registra entrenamiento (Pecho, Hombros, Tríceps)` (los grupos musculares que entrenaste ese día).
  - `10/11/2026: No registra entrenamiento`.
- **Colores del calendario:**

| Color | Significado |
|---|---|
| Verde | Día con entrenamiento registrado |
| Azul | Fecha 1 |
| Amarillo oscuro | Días comparables con la Fecha 1 |
| Amarillo | Fecha 2 |
| Borde blanco | Día seleccionado |

- **Seleccionar Fecha 1 y Fecha 2:** tocar un día y presionar **Seleccionar Fecha 1**. Se marcan en amarillo oscuro los días comparables: los días **posteriores** en que entrenaste **la misma rutina y el mismo día de esa rutina** (no tiene sentido comparar un día de piernas con uno de pecho). Elegí uno de esos días y presioná **Seleccionar Fecha 2**. Se muestran los ejercicios realizados en cada fecha.
- **Comparar Fecha 1 con Fecha 2:** muestra la diferencia de volumen total, las repeticiones totales y, para cada ejercicio repetido, la mejor serie de cada fecha (progreso por peso o, si el peso es el mismo, por repeticiones). La comparativa siempre va de la fecha más vieja a la más nueva.
- Las series registradas antes de que existiera esta función no tienen guardada la rutina y el día, así que se ven en verde pero no se pueden comparar.
- **Análisis Inteligente → Analizar Rendimiento:**
  - La IA lee los **datos personales** del usuario (nombre, sexo, peso, altura e IMC; **el DNI no se envía**) y **todos sus registros de entrenamiento**.
  - Devuelve un informe con: **conclusiones generales, puntos fuertes, puntos débiles, consejos para mejorar y una conclusión final**, basado solo en esos datos.
  - Suele tardar menos de 10 segundos (la ventana queda quieta mientras tanto). Si un modelo de Gemini no responde en 30 segundos o fue dado de baja, la aplicación prueba automáticamente con otro (`gemini-flash-lite-latest`, `gemini-3.5-flash` y `gemini-flash-latest`).
  - El informe también se guarda en un archivo `analisis_<nombre>.txt` en la carpeta del proyecto (este archivo no se sube a GitHub).

#### 4. Información Personal
- Ver y editar nombre, apellido, peso, altura y sexo (el DNI no se puede editar).
- Muestra el **IMC** (Índice de Masa Corporal) calculado con el peso y la altura.

#### 5. Cerrar Sesión
- Vuelve a la ventana inicial.

### Registro de acciones (archivo .txt)
Cada vez que un usuario inicia sesión, cierra sesión o se registra, se guarda una línea en `accion_usuario.txt` con el DNI, el nombre y la fecha y hora.

---

## Base de datos

| Tabla | Para qué sirve |
|---|---|
| `usuarios` | Datos de cada usuario (DNI, nombre, apellido, peso, altura, sexo). |
| `ejercicios` | Catálogo de ejercicios. `dni_usuario` en `NULL` = precargado; con un DNI = ejercicio propio. `activo` permite la baja lógica. |
| `rutinas` | Rutinas de cada usuario (nombre y cantidad de días). |
| `rutina_dias` | Días de cada rutina. |
| `rutina_ejercicios` | Ejercicios y cantidad de series de cada día. |
| `registros_entrenamiento` | Cada serie realizada (fecha, serie, peso, repeticiones) y qué rutina y día se estaba entrenando (`id_rutina`, `numero_dia`). |

Reglas importantes:
- **`serie_unica`:** una misma serie de un ejercicio no puede repetirse el mismo día (si se vuelve a cargar, se reemplaza).
- **Baja lógica (`activo`):** al eliminar un ejercicio propio no se borra su historial.
- **`ON DELETE SET NULL`:** si se elimina una rutina, las series registradas se conservan.

---

## Estructura del proyecto

| Archivo | Descripción |
|---|---|
| `nopy_nogain.py` | **Archivo principal.** Conecta la base de datos, la interfaz y la IA, e inicia la aplicación. |
| `nopy_interfaz.py` | Interfaz gráfica con CustomTkinter: la ventana principal (`App`), la navegación entre pantallas y una clase por cada pantalla. |
| `nopy_db.py` | Conexión a MySQL, consultas (crear, leer, actualizar y eliminar) y manejo de archivos .txt. |
| `nopy_clases.py` | Clases del sistema: `Usuario`, `Ejercicio`, `Rutina` y `RegistroEntrenamiento`. |
| `nopy_api.py` | Conexión con la API de Google Gemini: arma los datos del usuario, prueba los modelos en orden y limpia el texto del informe. |
| `claves_nopy.py` | Contraseña de MySQL y API key (**no se sube a GitHub**, se crea a mano). |
| `accion_usuario.txt` | Registro de acciones de los usuarios. |
| `nopy-nogain.png` | Logo de la aplicación. |
| `.gitignore` | Archivos que no se suben a GitHub (claves, caché de Python e informes de la IA). |
| `nopy-nogain.sql` | Script que crea la base de datos, sus tablas y los ejercicios precargados. |

---

## Limitaciones conocidas

- El ingreso es solo con el DNI, sin contraseña.
- Mientras la IA genera el informe, la ventana queda quieta unos segundos.
- La IA es un modelo de lenguaje y puede equivocarse en algún detalle del informe.
- Se necesita MySQL instalado en la computadora y conexión a internet para el análisis con IA.

---

## Autor
Nahuel Cuello — Academia de Desarrollo 2026.
