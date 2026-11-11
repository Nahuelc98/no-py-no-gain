# NO PY, NO GAIN

Trabajo integrador para la **Academia de Desarrollo 2026** (Programación en Python).

**NO PY, NO GAIN** es una aplicación de escritorio para gestionar y hacer el seguimiento del entrenamiento en el gimnasio. Permite crear y personalizar rutinas por días, usar un catálogo de ejercicios precargados o crear ejercicios propios, registrar el peso y las repeticiones de cada serie en tiempo real y ver el progreso con un calendario interactivo, comparativas entre fechas y un análisis hecho por Inteligencia Artificial (Google Gemini).

---

## Requisitos del sistema

- **Python 3.13** (o superior).
- **MySQL Server** (por ejemplo MySQL 8 con MySQL Workbench).
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
Abrir MySQL Workbench (o la consola de MySQL) y ejecutar el script `nopy-nogain.sql`.
Esto crea la base de datos `nopy_nogain`, sus tablas (`usuarios`, `ejercicios`, `rutinas`, `rutina_dias`, `rutina_ejercicios`, `registros_entrenamiento`) y carga los ejercicios iniciales.

> La conexión está configurada en `nopy_nogain.py` con: host `127.0.0.1`, usuario `root`, puerto `3306` y base de datos `nopy_nogain`. Si tu MySQL usa otros datos, modificalos en esa línea.

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

## Cómo usar la aplicación

### Ventana inicial
- **Ingresar con documento:** escribir el DNI y presionar **INGRESAR**. Si el DNI no está registrado se muestra un aviso.
- **¿No estás registrado? Regístrate aquí:** abre el formulario de registro (DNI, nombre, apellido, peso, altura y sexo). El DNI debe tener entre 7 y 8 números.
- **Cerrar No py, no gain:** cierra la aplicación.

### Menú principal
Al ingresar aparece un saludo con el nombre del usuario y estas opciones:

#### 1. Gestionar Rutina
Tiene tres opciones:
- **Crear Rutina:** ponerle un nombre, elegir la cantidad de días (1 a 7) y, para cada día, filtrar por grupo muscular, elegir el ejercicio, indicar la cantidad de series y presionar **Agregar Ejercicio al Día Actual**. Si te equivocaste, elegí el ejercicio en la lista de abajo y tocá **Quitar**. Al final, **Guardar Rutina Completa** (todos los días deben tener al menos un ejercicio). Con el botón **+** se puede crear un ejercicio propio sin salir de la pantalla.
- **Mis Rutinas:** elegí una rutina de la lista para ver sus días y ejercicios. Desde ahí se puede **Editar** (abre la rutina con sus datos cargados) o **Eliminar** (pide confirmación). Cada usuario solo ve y modifica sus propias rutinas.
- **Mis Ejercicios:** crear, editar o eliminar ejercicios propios (los ejercicios precargados no se pueden modificar). Al eliminar un ejercicio se quita de las rutinas, pero **su historial de entrenamiento se conserva** (baja lógica).

#### 2. Empezar Rutina
- Seleccionar la rutina, el día y el ejercicio.
- La aplicación sugiere el número de la próxima serie, muestra **"Serie X de N"**, las series que ya hiciste hoy y **lo que hiciste la última vez** en ese ejercicio.
- Anotar el peso (kg) y las repeticiones, y presionar **Guardar Registro en BD**. Se guarda con la fecha de hoy y se muestra el volumen de la serie (peso × repeticiones).
- Cada serie se registra una sola vez por día: si cargás de nuevo una serie que ya existe (por ejemplo, para corregir un error), **se reemplaza**.

#### 3. Ver Seguimiento
- **Calendario interactivo:** los días entrenados aparecen en verde. Se puede cambiar de mes.
- **Seleccionar Fecha 1 y Fecha 2:** hacer clic en un día del calendario (queda marcado con borde blanco) y fijarlo como Fecha 1 (naranja) o Fecha 2 (violeta). Se muestran los ejercicios realizados en cada fecha.
- **Comparar Fecha 1 con Fecha 2:** muestra la diferencia de volumen total y el progreso de peso en los ejercicios repetidos.
- **Analizar Rendimiento con IA:** la IA de Google Gemini analiza todo el historial y devuelve estadísticas, puntos fuertes, puntos débiles, consejos y una conclusión. El informe también se guarda en un archivo `analisis_<nombre>.txt`.

#### 4. Información Personal
- Ver y editar nombre, apellido, peso, altura y sexo (el DNI no se puede editar).
- Muestra el **IMC** (Índice de Masa Corporal) calculado con el peso y la altura.

#### 5. Cerrar Sesión
- Vuelve a la ventana inicial.

### Registro de acciones (archivo .txt)
Cada vez que un usuario inicia sesión, cierra sesión o se registra, se guarda una línea en `accion_usuario.txt` con el DNI, el nombre y la fecha y hora.

---

## Estructura del proyecto

| Archivo | Descripción |
|---|---|
| `nopy_nogain.py` | **Archivo principal.** Conecta la base de datos, la interfaz y la IA, e inicia la aplicación. |
| `nopy_interfaz.py` | Interfaz gráfica con CustomTkinter (todas las ventanas). |
| `nopy_db.py` | Conexión a MySQL, consultas (crear, leer, actualizar y eliminar) y manejo de archivos .txt. |
| `nopy_clases.py` | Clases del sistema: `Usuario`, `Ejercicio`, `Rutina` y `RegistroEntrenamiento`. |
| `nopy_api.py` | Conexión con la API de Google Gemini para el análisis de rendimiento. |
| `claves_nopy.py` | Contraseña de MySQL y API key (**no se sube a GitHub**, se crea a mano). |
| `accion_usuario.txt` | Registro de acciones de los usuarios. |
| `nopy-nogain.png` | Logo de la aplicación. |

---

## Autor
Nahuel Cuello — Academia de Desarrollo 2026.
