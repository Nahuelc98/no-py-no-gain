"""
Módulo de Interfaz Gráfica (CustomTkinter) para 'No py, no gain'.
"""

import os
import calendar
import customtkinter as ctk
from datetime import date
from PIL import Image
# Importamos las clases que usamos dentro de las ventanas
from nopy_clases import Usuario, RegistroEntrenamiento

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

GRUPOS_MUSCULARES = ["Piernas", "Pecho", "Espalda", "Hombros", "Bíceps", "Tríceps", "Abdomen"]
TIPOS_EJERCICIO = ["Libre", "Máquina"]

# Paleta de colores:
verde = "#2BA535"                   
verde_hover = "#3DC94A"             
rojo = "#C0392B"                    
rojo_hover = "#E74C3C"             
azul = "#2980B9"                    
azul_hover = "#3FA3D8"              
azul_claro = "#4B8BBE"              
amarillo = "#EFBA1C"               
amarillo_hover = "#F5CD4F"         
naranja = "#F39C12"                 
naranja_hover = "#F5B942"           
gris = "#555555"                    
gris_hover = "#777777"              
violeta = "#8E44AD"                 
violeta_hover = "#A569BD"           
amarillo_oscuro = "#8A7419"         
amarillo_oscuro_hover = "#A88E22"   

def habilitar_scroll_fluido(ventana, scrollable_frame):
    """
    Vincula recursivamente el evento de la rueda del ratón en todos los widgets hijos
    de un contenedor con scroll. De este modo, aunque el usuario tenga el cursor sobre
    un texto, botón o marco secundario, el scroll se ejecuta de forma suave y sin trabas.
    """
    def _desplazar(event):
        try:
            # Si el puntero está sobre un Textbox interno, dejamos que actúe su propio scroll
            if hasattr(event, "widget") and (str(event.widget).endswith("text") or event.widget.winfo_class() == "Text"):
                return
            delta = int(-1 * (event.delta / 120)) if event.delta else 0
            if delta != 0 and hasattr(scrollable_frame, "_parent_canvas"):
                scrollable_frame._parent_canvas.yview_scroll(delta, "units")
        except Exception:
            pass

    def _desplazar_linux_arriba(event):
        try:
            if hasattr(scrollable_frame, "_parent_canvas"):
                scrollable_frame._parent_canvas.yview_scroll(-1, "units")
        except Exception:
            pass

    def _desplazar_linux_abajo(event):
        try:
            if hasattr(scrollable_frame, "_parent_canvas"):
                scrollable_frame._parent_canvas.yview_scroll(1, "units")
        except Exception:
            pass

    def _vincular_recursivo(widget):
        if not isinstance(widget, ctk.CTkTextbox):
            try:
                widget.bind("<MouseWheel>", _desplazar, add="+")
                widget.bind("<Button-4>", _desplazar_linux_arriba, add="+")
                widget.bind("<Button-5>", _desplazar_linux_abajo, add="+")
            except Exception:
                pass
        for hijo in widget.winfo_children():
            _vincular_recursivo(hijo)

    # Vinculamos los widgets actuales
    _vincular_recursivo(scrollable_frame)
    # Pasada adicional para widgets que tarden unos milisegundos en inicializarse
    ventana.after(150, lambda: _vincular_recursivo(scrollable_frame))


def solo_lectura(cuadro):
    """
    Hace que un cuadro de texto (CTkTextbox) no se pueda modificar con el teclado:
    el usuario puede seleccionar y copiar el texto (Ctrl+C) y moverse con las flechas,
    pero no puede escribir, borrar, cortar ni pegar.
    La aplicación sí puede seguir escribiendo en el cuadro con insert() y delete().
    """
    def bloquear_tecla(evento):
        teclas_permitidas = ["Left", "Right", "Up", "Down", "Home", "End", "Prior", "Next"]
        # evento.state & 4 indica que la tecla Control está apretada (Ctrl+C = copiar)
        es_copiar = (evento.state & 4) and evento.keysym.lower() == "c"
        if es_copiar or evento.keysym in teclas_permitidas:
            return None
        # "break" corta el evento: la tecla no llega a modificar el texto
        return "break"

    cuadro.bind("<Key>", bloquear_tecla)
    # También bloqueamos pegar y cortar (por ejemplo, con el menú o atajos del sistema)
    cuadro.bind("<<Paste>>", lambda evento: "break")
    cuadro.bind("<<Cut>>", lambda evento: "break")


def formato_fecha(fecha_str):
    """
    Convierte una fecha del formato de la base de datos "AAAA-MM-DD" al formato "DD/MM/AAAA".
    Ej: "2026-11-09" -> "09/11/2026" (cortamos el texto: año = [0:4], mes = [5:7], día = [8:10]).
    """
    fecha_str = str(fecha_str)
    return f"{fecha_str[8:10]}/{fecha_str[5:7]}/{fecha_str[0:4]}"


def texto_unico(texto, diccionario):
    """
    Las listas desplegables muestran solo nombres (sin IDs). Si un nombre ya está en el
    diccionario de la lista, le agregamos un número para que no se repita. Ej: 'Push (2)'.
    """
    nuevo_texto = texto
    numero = 2
    while nuevo_texto in diccionario:
        nuevo_texto = f"{texto} ({numero})"
        numero += 1
    return nuevo_texto


def crear_encabezado(contenedor, titulo, comando_volver, tamaño_letra=20, pady=(10, 10)):
    """
    Crea el encabezado de una sección: el botón '◀ Volver' en la esquina superior izquierda
    y el título de la sección a su derecha (centrado).
    """
    frame_encabezado = ctk.CTkFrame(contenedor, fg_color="transparent")
    frame_encabezado.pack(fill="x", pady=pady)

    # Botón para volver al menú principal (a la izquierda del título)
    ctk.CTkButton(frame_encabezado, text="◀ Volver", command=comando_volver, width=75, fg_color=gris, hover_color=gris_hover).pack(side="left", padx=5)

    # Espacio vacío del mismo ancho que el botón (a la derecha) para que el título quede centrado
    ctk.CTkLabel(frame_encabezado, text="", width=75).pack(side="right", padx=5)

    # Título de la sección (si es muy largo se divide en dos líneas)
    ctk.CTkLabel(frame_encabezado, text=titulo, font=("Arial", tamaño_letra, "bold"), wraplength=200).pack(side="left", expand=True)


# Todas las clases "Ventana..." son paneles (CTkFrame) que se muestran dentro
# de la ventana principal, así toda la aplicación funciona en una sola ventana.
# winfo_toplevel() devuelve la ventana principal (App) a la que pertenece el parent.

class VentanaGestionarRutinas(ctk.CTkFrame):
    """
    Sección "Gestionar Rutinas".
    Es un menú que lleva a tres subpantallas: Crear Rutina, Mis Rutinas y Mis Ejercicios.
    """
    def __init__(self, parent, dni_usuario, fn_obtener_ejercicios, fn_agregar_ejercicio, fn_guardar_rutina, fn_obtener_rutinas, fn_eliminar_rutina, fn_obtener_detalle=None, fn_actualizar_rutina=None, fn_obtener_ejercicios_propios=None, fn_actualizar_ejercicio=None, fn_eliminar_ejercicio=None):
        app = parent.winfo_toplevel()
        super().__init__(app, fg_color="transparent")
        self.app = app

        self.dni_usuario = dni_usuario
        self.fn_obtener_ejercicios = fn_obtener_ejercicios
        self.fn_agregar_ejercicio = fn_agregar_ejercicio
        self.fn_guardar_rutina = fn_guardar_rutina
        self.fn_obtener_rutinas = fn_obtener_rutinas
        self.fn_eliminar_rutina = fn_eliminar_rutina
        self.fn_obtener_detalle = fn_obtener_detalle
        self.fn_actualizar_rutina = fn_actualizar_rutina
        # Funciones para gestionar ejercicios propios del usuario
        self.fn_obtener_ejercicios_propios = fn_obtener_ejercicios_propios
        self.fn_actualizar_ejercicio = fn_actualizar_ejercicio
        self.fn_eliminar_ejercicio = fn_eliminar_ejercicio

        # Encabezado: botón '◀ Volver' a la izquierda y el título de la sección
        crear_encabezado(self, "Gestionar Rutinas", self.app.volver_pantalla, pady=(20, 20))

        # Botones que llevan a cada subpantalla
        ctk.CTkButton(
            self, text="Crear Rutina", command=self.abrir_crear_rutina, width=280, height=45,
            font=("Arial", 13, "bold"), fg_color=verde, hover_color=verde_hover
        ).pack(pady=8)

        ctk.CTkButton(
            self, text="Mis Rutinas", command=self.abrir_mis_rutinas, width=280, height=45,
            font=("Arial", 13, "bold"), fg_color=azul, hover_color=azul_hover
        ).pack(pady=8)

        ctk.CTkButton(
            self, text="Mis Ejercicios", command=self.abrir_mis_ejercicios, width=280, height=45,
            font=("Arial", 13, "bold"), fg_color=naranja, hover_color=naranja_hover, text_color="black"
        ).pack(pady=8)

        # Mostramos esta pantalla dentro de la ventana principal
        self.app.abrir_pantalla(self)

    def abrir_crear_rutina(self):
        VentanaCrearRutina(self, self.dni_usuario, self.fn_obtener_ejercicios, self.fn_agregar_ejercicio, fn_guardar_rutina=self.fn_guardar_rutina)

    def abrir_mis_rutinas(self):
        VentanaMisRutinas(
            self, self.dni_usuario, self.fn_obtener_rutinas, self.fn_eliminar_rutina,
            self.fn_obtener_detalle, self.fn_actualizar_rutina,
            self.fn_obtener_ejercicios, self.fn_agregar_ejercicio
        )

    def abrir_mis_ejercicios(self):
        VentanaMisEjercicios(
            self, self.dni_usuario, self.fn_agregar_ejercicio, self.fn_obtener_ejercicios_propios,
            self.fn_actualizar_ejercicio, self.fn_eliminar_ejercicio
        )


class VentanaCrearRutina(ctk.CTkFrame):
    """
    Subpantalla para CREAR una rutina nueva o EDITAR una existente.
    Si recibe el id y el detalle de una rutina, se abre en modo edición con los datos cargados.
    """
    def __init__(self, parent, dni_usuario, fn_obtener_ejercicios, fn_agregar_ejercicio, fn_guardar_rutina=None, id_rutina_editar=None, detalle=None, fn_actualizar_rutina=None, fn_al_guardar=None):
        app = parent.winfo_toplevel()
        super().__init__(app, fg_color="transparent")
        self.app = app

        self.dni_usuario = dni_usuario
        self.fn_obtener_ejercicios = fn_obtener_ejercicios
        self.fn_agregar_ejercicio = fn_agregar_ejercicio
        self.fn_guardar_rutina = fn_guardar_rutina
        self.fn_actualizar_rutina = fn_actualizar_rutina
        # Función que avisa a "Mis Rutinas" que se guardaron cambios (para actualizar su lista)
        self.fn_al_guardar = fn_al_guardar

        # Variables para controlar la rutina y si estamos editando una existente
        self.id_rutina_editando = id_rutina_editar
        self.dias_rutina = []
        self.dia_actual_num = 1
        self.total_dias = 3

        # Diccionarios para las listas desplegables (muestran nombres, sin IDs):
        # {texto de la lista: objeto Ejercicio} y {texto de la lista "Quitar": posición en el día}
        self.mapa_ejercicios = {}
        self.mapa_quitar = {}

        # Encabezado fijo (fuera del scroll) para que el botón '◀ Volver' siempre se vea
        titulo = "Editar Rutina" if id_rutina_editar else "Crear Rutina"
        crear_encabezado(self, titulo, self.app.volver_pantalla)

        # Contenedor con scroll para que la ventana tenga tamaño fijo y todo sea accesible
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=365, height=565)
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.ent_nombre_rutina = ctk.CTkEntry(self.scroll_frame, placeholder_text="Nombre de rutina (ej: Push, Pull, Leg (PPL))", width=340)
        self.ent_nombre_rutina.pack(pady=5)

        # Cantidad de días (1 al 7)
        frame_dias = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        frame_dias.pack(pady=5)
        ctk.CTkLabel(frame_dias, text="Cantidad de días:").pack(side="left", padx=5)
        self.combo_cantidad_dias = ctk.CTkOptionMenu(frame_dias, values=["1", "2", "3", "4", "5", "6", "7"], command=self.cambiar_cantidad_dias, width=100)
        self.combo_cantidad_dias.set("3")
        self.combo_cantidad_dias.pack(side="left", padx=5)

        # Selector de Día Activo dinámico
        frame_selector_dia = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        frame_selector_dia.pack(pady=5)
        ctk.CTkLabel(frame_selector_dia, text="Configurando:").pack(side="left", padx=5)
        self.combo_dia_activo = ctk.CTkOptionMenu(frame_selector_dia, values=["Día 1"], command=self.seleccionar_dia_activo, width=120)
        self.combo_dia_activo.pack(side="left", padx=5)

        # Grupo Muscular (solo grupos específicos, sin la opción "Todos")
        frame_grupo = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        frame_grupo.pack(pady=5)
        ctk.CTkLabel(frame_grupo, text="Grupo Muscular:").pack(side="left", padx=5)
        self.combo_grupo_dia = ctk.CTkOptionMenu(frame_grupo, values=GRUPOS_MUSCULARES, command=self.actualizar_ejercicios_disponibles, width=200)
        self.combo_grupo_dia.set(GRUPOS_MUSCULARES[0])
        self.combo_grupo_dia.pack(side="left", padx=5)

        # Menú de ejercicios (con botón '+' para crear un ejercicio propio)
        frame_ej = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        frame_ej.pack(pady=5)
        ctk.CTkLabel(frame_ej, text="Ejercicio:").pack(side="left", padx=5)
        self.combo_ejercicios = ctk.CTkOptionMenu(frame_ej, values=["Cargando..."], width=220)
        self.combo_ejercicios.pack(side="left", padx=5)
        ctk.CTkButton(frame_ej, text="+", command=self.abrir_crear_ejercicio, width=40, fg_color=azul, hover_color=azul_hover).pack(side="left", padx=5)

        # Cantidad de series por ejercicio (de 1 a 10, con flechas para subir y bajar)
        frame_series = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        frame_series.pack(pady=5)
        ctk.CTkLabel(frame_series, text="Cantidad de series:").pack(side="left", padx=5)
        self.ent_series = ctk.CTkEntry(frame_series, width=60, justify="center")
        self.ent_series.insert(0, "1")
        self.ent_series.pack(side="left", padx=5)
        ctk.CTkButton(frame_series, text="▲", command=self.subir_series, width=32, fg_color=gris, hover_color=gris_hover).pack(side="left", padx=2)
        ctk.CTkButton(frame_series, text="▼", command=self.bajar_series, width=32, fg_color=gris, hover_color=gris_hover).pack(side="left", padx=2)

        ctk.CTkButton(self.scroll_frame, text="Agregar Ejercicio al Día Actual", command=self.agregar_ejercicio_a_dia, width=340, fg_color=azul, hover_color=azul_hover).pack(pady=8)

        # Resumen de la rutina armada (todos los días)
        ctk.CTkLabel(self.scroll_frame, text="Rutina armada:", font=("Arial", 13, "bold")).pack(pady=(5, 0))
        # wrap="word": el texto salta de línea entre palabras completas (no corta palabras a la mitad)
        self.txt_resumen = ctk.CTkTextbox(self.scroll_frame, width=350, height=130, wrap="word")
        solo_lectura(self.txt_resumen)  # el usuario no puede modificar el texto
        self.txt_resumen.pack(pady=5)

        # Quitar un ejercicio del día que se está configurando (por si se agregó por error)
        frame_quitar = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        frame_quitar.pack(pady=5)
        self.combo_quitar = ctk.CTkOptionMenu(frame_quitar, values=["Sin ejercicios en este día"], width=240)
        self.combo_quitar.pack(side="left", padx=5)
        ctk.CTkButton(frame_quitar, text="Quitar", command=self.quitar_ejercicio, width=80, fg_color=rojo, hover_color=rojo_hover).pack(side="left", padx=5)

        # Etiqueta para mostrar avisos y mensajes (separada del resumen)
        self.lbl_msg = ctk.CTkLabel(self.scroll_frame, text="", font=("Arial", 12, "bold"), wraplength=340)
        self.lbl_msg.pack(pady=4)

        # Botón para guardar (sirve tanto para crear como para editar)
        texto_guardar = "✔ Guardar Cambios en Rutina" if id_rutina_editar else "✔ Guardar Rutina"
        color_guardar = naranja if id_rutina_editar else verde
        hover_guardar = naranja_hover if id_rutina_editar else verde_hover
        ctk.CTkButton(self.scroll_frame, text=texto_guardar, command=self.guardar_todo, width=340, fg_color=color_guardar, hover_color=hover_guardar).pack(pady=(4, 10))

        # Si estamos editando, cargamos los datos de la rutina en los controles
        if detalle:
            self.ent_nombre_rutina.insert(0, detalle['nombre_rutina'])
            self.dias_rutina = detalle['dias']
            cant_dias = str(detalle['cantidad_dias'])
            self.combo_cantidad_dias.set(cant_dias)
            self.cambiar_cantidad_dias(cant_dias)
        else:
            self.cambiar_cantidad_dias("3")

        self.actualizar_ejercicios_disponibles(GRUPOS_MUSCULARES[0])

        # Vinculamos scroll fluido en toda la superficie
        habilitar_scroll_fluido(self, self.scroll_frame)

        # Mostramos esta pantalla dentro de la ventana principal
        self.app.abrir_pantalla(self)

    def mostrar_mensaje(self, texto, color):
        """Muestra un aviso en la etiqueta de mensajes."""
        self.lbl_msg.configure(text=texto, text_color=color)

    def buscar_dia(self, numero_dia):
        """Devuelve el diccionario del día buscado, o None si ese día todavía no tiene ejercicios."""
        for dia in self.dias_rutina:
            if dia['numero_dia'] == numero_dia:
                return dia
        return None

    def abrir_crear_ejercicio(self):
        VentanaCrearEjercicioModal(self, self.dni_usuario, self.fn_agregar_ejercicio, lambda: self.actualizar_ejercicios_disponibles(self.combo_grupo_dia.get()))

    def cambiar_cantidad_dias(self, valor):
        self.total_dias = int(valor)
        opciones_dias = [f"Día {i}" for i in range(1, self.total_dias + 1)]
        self.combo_dia_activo.configure(values=opciones_dias)
        self.combo_dia_activo.set(opciones_dias[0])
        self.dia_actual_num = 1

        # Quitamos solo los días que quedaron fuera de la nueva cantidad (lo cargado en los demás días se mantiene)
        dias_que_quedan = []
        dias_quitados = []
        for dia in self.dias_rutina:
            if dia['numero_dia'] <= self.total_dias:
                dias_que_quedan.append(dia)
            else:
                dias_quitados.append(str(dia['numero_dia']))
        self.dias_rutina = dias_que_quedan

        self.actualizar_texto_resumen()
        self.actualizar_lista_quitar()
        if dias_quitados:
            self.mostrar_mensaje(f"⚠ Se quitaron los ejercicios del Día {', '.join(dias_quitados)} porque la rutina ahora tiene {self.total_dias} días.", naranja)

    def seleccionar_dia_activo(self, seleccion):
        if "Día" in seleccion:
            self.dia_actual_num = int(seleccion.replace("Día", "").strip())
            self.actualizar_lista_quitar()

    def actualizar_ejercicios_disponibles(self, grupo):
        ejercicios = self.fn_obtener_ejercicios(grupo, self.dni_usuario)
        # La lista muestra solo el nombre del ejercicio; el objeto Ejercicio queda guardado en el diccionario
        self.mapa_ejercicios = {}
        for ej in ejercicios:
            texto = ej.nombre
            # Si un ejercicio propio tiene el mismo nombre que uno precargado, lo aclaramos
            if texto in self.mapa_ejercicios and ej.dni_usuario:
                texto = f"{ej.nombre} (propio)"
            texto = texto_unico(texto, self.mapa_ejercicios)
            self.mapa_ejercicios[texto] = ej

        nombres = list(self.mapa_ejercicios.keys()) if self.mapa_ejercicios else ["Sin Ejercicios"]
        self.combo_ejercicios.configure(values=nombres)
        self.combo_ejercicios.set(nombres[0])

    def leer_series(self):
        """Devuelve la cantidad de series escrita en el campo (o 1 si no es un número válido)."""
        texto = self.ent_series.get().strip()
        if texto.isdigit():
            return int(texto)
        return 1

    def cambiar_series(self, cantidad):
        """Escribe la cantidad de series en el campo, siempre entre 1 y 10."""
        if cantidad < 1:
            cantidad = 1
        if cantidad > 10:
            cantidad = 10
        self.ent_series.delete(0, "end")
        self.ent_series.insert(0, str(cantidad))

    def subir_series(self):
        """Flecha ▲: suma una serie (máximo 10)."""
        self.cambiar_series(self.leer_series() + 1)

    def bajar_series(self):
        """Flecha ▼: resta una serie (mínimo 1)."""
        self.cambiar_series(self.leer_series() - 1)

    def agregar_ejercicio_a_dia(self):
        seleccion = self.combo_ejercicios.get()
        series_str = self.ent_series.get().strip()
        if not series_str.isdigit() or int(series_str) < 1 or int(series_str) > 10:
            self.mostrar_mensaje("⚠ La cantidad de series debe ser un número entre 1 y 10.", naranja)
            return
        # Buscamos el objeto Ejercicio elegido en el diccionario de la lista
        ejercicio = self.mapa_ejercicios.get(seleccion)
        if not ejercicio:
            self.mostrar_mensaje("⚠ Seleccione un ejercicio válido.", naranja)
            return

        id_ej = ejercicio.id_ejercicio
        nom_ej = ejercicio.nombre
        grupo_ej = ejercicio.grupo_muscular
        series = int(series_str)

        # Buscamos si el día ya existe en la lista de configuración; si no, lo creamos
        dia_obj = self.buscar_dia(self.dia_actual_num)
        if not dia_obj:
            dia_obj = {'numero_dia': self.dia_actual_num, 'grupo': grupo_ej, 'ejercicios': []}
            self.dias_rutina.append(dia_obj)

        # Agregamos el ejercicio a ese día
        dia_obj['ejercicios'].append({'id': id_ej, 'series': series, 'nombre': nom_ej, 'grupo': grupo_ej})

        self.actualizar_texto_resumen()
        self.actualizar_lista_quitar()
        self.mostrar_mensaje(f"✔ {nom_ej} agregado al Día {self.dia_actual_num}.", "#2ECC71")

    def actualizar_texto_resumen(self):
        """Muestra todos los días de la rutina con sus ejercicios (o avisa si un día está vacío)."""
        self.txt_resumen.delete("1.0", "end")
        for numero in range(1, self.total_dias + 1):
            dia = self.buscar_dia(numero)
            self.txt_resumen.insert("end", f"Día {numero}:\n")
            if dia and dia['ejercicios']:
                for ej in dia['ejercicios']:
                    self.txt_resumen.insert("end", f"  • {ej['nombre']} | {ej['series']} Series | {ej['grupo']}\n")
            else:
                self.txt_resumen.insert("end", "  (sin ejercicios)\n")

    def actualizar_lista_quitar(self):
        """Carga en la lista 'Quitar' los ejercicios del día que se está configurando."""
        dia = self.buscar_dia(self.dia_actual_num)
        # {texto de la lista: posición del ejercicio dentro del día}
        self.mapa_quitar = {}
        if dia:
            posicion = 0
            for ej in dia['ejercicios']:
                texto = texto_unico(f"{ej['nombre']} ({ej['series']} series)", self.mapa_quitar)
                self.mapa_quitar[texto] = posicion
                posicion += 1
        opciones = list(self.mapa_quitar.keys()) if self.mapa_quitar else ["Sin ejercicios en este día"]
        self.combo_quitar.configure(values=opciones)
        self.combo_quitar.set(opciones[0])

    def quitar_ejercicio(self):
        """Quita del día actual el ejercicio elegido en la lista (por si se agregó por error)."""
        seleccion = self.combo_quitar.get()
        dia = self.buscar_dia(self.dia_actual_num)
        if not dia or seleccion not in self.mapa_quitar:
            self.mostrar_mensaje("⚠ No hay ejercicios para quitar en este día.", naranja)
            return

        # Buscamos en el diccionario la posición del ejercicio dentro del día
        posicion = self.mapa_quitar[seleccion]
        quitado = dia['ejercicios'].pop(posicion)
        # Si el día quedó sin ejercicios lo sacamos de la rutina
        if not dia['ejercicios']:
            self.dias_rutina.remove(dia)

        self.actualizar_texto_resumen()
        self.actualizar_lista_quitar()
        self.mostrar_mensaje(f"Se quitó {quitado['nombre']} del Día {self.dia_actual_num}.", naranja)

    def guardar_todo(self):
        nom_rutina = self.ent_nombre_rutina.get().strip()
        if not nom_rutina:
            self.mostrar_mensaje("⚠ Falta ponerle un nombre a la rutina.", naranja)
            return

        # Verificamos que TODOS los días tengan al menos un ejercicio
        dias_vacios = []
        for numero in range(1, self.total_dias + 1):
            dia = self.buscar_dia(numero)
            if not dia or not dia['ejercicios']:
                dias_vacios.append(str(numero))
        if dias_vacios:
            self.mostrar_mensaje(f"⚠ Faltan ejercicios en el Día {', '.join(dias_vacios)}.", naranja)
            return

        # El grupo muscular de cada día se arma con los grupos de sus ejercicios (ej: "Pecho, Tríceps")
        for dia in self.dias_rutina:
            grupos = []
            for ej in dia['ejercicios']:
                if ej['grupo'] not in grupos:
                    grupos.append(ej['grupo'])
            dia['grupo'] = ", ".join(grupos)

        # Ordenamos los días por número antes de guardar
        self.dias_rutina.sort(key=lambda d: d['numero_dia'])

        # Si estamos editando una rutina existente:
        if self.id_rutina_editando:
            exito = False
            if self.fn_actualizar_rutina:
                exito = self.fn_actualizar_rutina(self.id_rutina_editando, self.dni_usuario, nom_rutina, self.dias_rutina)
            if exito:
                # Avisamos a "Mis Rutinas" y volvemos a esa pantalla
                if self.fn_al_guardar:
                    self.fn_al_guardar()
                self.app.volver_pantalla()
            else:
                self.mostrar_mensaje("❌ No se pudo actualizar la rutina.", rojo_hover)
        else:
            # Si estamos creando una rutina nueva:
            exito = False
            if self.fn_guardar_rutina:
                exito = self.fn_guardar_rutina(self.dni_usuario, nom_rutina, self.dias_rutina)
            if exito:
                # Limpiamos el formulario para poder crear otra rutina
                self.ent_nombre_rutina.delete(0, "end")
                self.dias_rutina = []
                self.cambiar_cantidad_dias(self.combo_cantidad_dias.get())
                self.mostrar_mensaje(f"✔ ¡Rutina '{nom_rutina}' creada con éxito! La podés ver en 'Mis Rutinas'.", "#2ECC71")
            else:
                self.mostrar_mensaje("❌ No se pudo guardar la rutina.", rojo_hover)


class VentanaMisRutinas(ctk.CTkFrame):
    """Subpantalla para VER, EDITAR o ELIMINAR las rutinas del usuario (elegidas de una lista)."""
    def __init__(self, parent, dni_usuario, fn_obtener_rutinas, fn_eliminar_rutina, fn_obtener_detalle, fn_actualizar_rutina, fn_obtener_ejercicios, fn_agregar_ejercicio):
        app = parent.winfo_toplevel()
        super().__init__(app, fg_color="transparent")
        self.app = app

        self.dni_usuario = dni_usuario
        self.fn_obtener_rutinas = fn_obtener_rutinas
        self.fn_eliminar_rutina = fn_eliminar_rutina
        self.fn_obtener_detalle = fn_obtener_detalle
        self.fn_actualizar_rutina = fn_actualizar_rutina
        self.fn_obtener_ejercicios = fn_obtener_ejercicios
        self.fn_agregar_ejercicio = fn_agregar_ejercicio

        # Guarda el ID de la rutina que se está por eliminar (para pedir confirmación)
        self.id_para_confirmar = None
        # Diccionario de la lista desplegable (muestra nombres, sin IDs): {texto: id_rutina}
        self.mapa_rutinas = {}

        # Encabezado: botón '◀ Volver' a la izquierda y el título de la sección
        crear_encabezado(self, "Mis Rutinas", self.app.volver_pantalla)

        ctk.CTkLabel(self, text="Seleccioná una rutina:", font=("Arial", 12, "bold")).pack(pady=(5, 0))
        self.combo_rutinas = ctk.CTkOptionMenu(self, values=["Cargando..."], command=self.mostrar_detalle, width=340)
        self.combo_rutinas.pack(pady=5)

        # Detalle de la rutina elegida (días y ejercicios)
        self.txt_detalle = ctk.CTkTextbox(self, width=350, height=300, wrap="word")
        solo_lectura(self.txt_detalle)  # el usuario no puede modificar el texto
        self.txt_detalle.pack(pady=5)

        # Acciones sobre la rutina elegida: Editar o Eliminar
        frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        frame_acciones.pack(pady=5)
        ctk.CTkButton(frame_acciones, text="Editar Rutina", command=self.editar_rutina, fg_color=naranja, hover_color=naranja_hover, text_color="black", width=160).pack(side="left", padx=5)
        self.btn_eliminar = ctk.CTkButton(frame_acciones, text="Eliminar Rutina", command=self.eliminar_rutina, fg_color=rojo, hover_color=rojo_hover, width=160)
        self.btn_eliminar.pack(side="left", padx=5)

        # Etiqueta para mostrar avisos y mensajes
        self.lbl_msg = ctk.CTkLabel(self, text="", font=("Arial", 12, "bold"), wraplength=340)
        self.lbl_msg.pack(pady=5)

        self.cargar_rutinas()

        # Mostramos esta pantalla dentro de la ventana principal
        self.app.abrir_pantalla(self)

    def mostrar_mensaje(self, texto, color):
        """Muestra un aviso en la etiqueta de mensajes."""
        self.lbl_msg.configure(text=texto, text_color=color)

    def obtener_id_seleccionado(self):
        """Devuelve el ID de la rutina elegida en la lista (buscándolo en el diccionario), o None."""
        return self.mapa_rutinas.get(self.combo_rutinas.get())

    def cargar_rutinas(self):
        """Carga en la lista solo las rutinas del usuario."""
        rutinas = self.fn_obtener_rutinas(self.dni_usuario)
        # Cada rutina es un objeto Rutina: la lista muestra su nombre y el ID queda en el diccionario
        self.mapa_rutinas = {}
        for r in rutinas:
            # texto_dias() de la clase Rutina devuelve "1 día" o "N días"
            texto = texto_unico(f"{r.nombre_rutina} ({r.texto_dias()})", self.mapa_rutinas)
            self.mapa_rutinas[texto] = r.id_rutina
        opciones = list(self.mapa_rutinas.keys()) if self.mapa_rutinas else ["No tenés rutinas creadas"]
        self.combo_rutinas.configure(values=opciones)
        self.combo_rutinas.set(opciones[0])
        self.mostrar_detalle(opciones[0])

    def mostrar_detalle(self, seleccion):
        """Muestra los días y ejercicios de la rutina elegida."""
        # Si cambia la rutina elegida, se cancela cualquier confirmación de eliminación pendiente
        self.id_para_confirmar = None
        self.btn_eliminar.configure(text="Eliminar Rutina")
        self.mostrar_mensaje("", "#FFFFFF")

        self.txt_detalle.delete("1.0", "end")
        id_rutina = self.obtener_id_seleccionado()
        if id_rutina is None:
            self.txt_detalle.insert("end", "Todavía no creaste ninguna rutina.\nCreala desde 'Crear Rutina'.")
            return

        detalle = self.fn_obtener_detalle(id_rutina, self.dni_usuario)
        if not detalle:
            self.txt_detalle.insert("end", "No se pudo cargar la rutina.")
            return

        # "1 día" en singular y "N días" en plural
        texto_dias = "1 día" if detalle['cantidad_dias'] == 1 else f"{detalle['cantidad_dias']} días"
        self.txt_detalle.insert("end", f"{detalle['nombre_rutina']} ({texto_dias})\n\n")
        for dia in detalle['dias']:
            self.txt_detalle.insert("end", f"Día {dia['numero_dia']} ({dia['grupo']}):\n")
            for ej in dia['ejercicios']:
                self.txt_detalle.insert("end", f"  • {ej['nombre']} | {ej['series']} Series\n")
            self.txt_detalle.insert("end", "\n")

    def editar_rutina(self):
        """Abre la subpantalla de Crear Rutina con los datos de la rutina elegida (modo edición)."""
        id_rutina = self.obtener_id_seleccionado()
        if id_rutina is None:
            self.mostrar_mensaje("⚠ No hay ninguna rutina para editar.", naranja)
            return
        detalle = self.fn_obtener_detalle(id_rutina, self.dni_usuario)
        if not detalle:
            self.mostrar_mensaje("❌ No se pudo cargar la rutina.", rojo_hover)
            return
        VentanaCrearRutina(
            self, self.dni_usuario, self.fn_obtener_ejercicios, self.fn_agregar_ejercicio,
            id_rutina_editar=id_rutina, detalle=detalle,
            fn_actualizar_rutina=self.fn_actualizar_rutina, fn_al_guardar=self.rutina_editada
        )

    def rutina_editada(self):
        """Se ejecuta cuando se guardan los cambios de una rutina: actualiza la lista y avisa."""
        self.cargar_rutinas()
        self.mostrar_mensaje("✔ Rutina actualizada con éxito.", "#2ECC71")

    def eliminar_rutina(self):
        """Elimina la rutina elegida. Pide confirmación tocando el botón dos veces."""
        id_rutina = self.obtener_id_seleccionado()
        if id_rutina is None:
            self.mostrar_mensaje("⚠ No hay ninguna rutina para eliminar.", naranja)
            return

        # Primer clic: pedimos confirmación
        if self.id_para_confirmar != id_rutina:
            self.id_para_confirmar = id_rutina
            self.btn_eliminar.configure(text="Confirmar eliminación")
            self.mostrar_mensaje("⚠ ¿Seguro? Tocá 'Confirmar eliminación' para borrar la rutina. Tu historial de entrenamiento no se borra.", naranja)
            return

        # Segundo clic: eliminamos (la función de DB valida que la rutina sea del usuario)
        if self.fn_eliminar_rutina(id_rutina, self.dni_usuario):
            self.cargar_rutinas()
            self.mostrar_mensaje("✔ Rutina eliminada.", "#2ECC71")
        else:
            self.mostrar_mensaje("❌ No se pudo eliminar la rutina.", rojo_hover)


class VentanaMisEjercicios(ctk.CTkFrame):
    """
    Subpantalla para CREAR, EDITAR o ELIMINAR los ejercicios propios del usuario.
    Los ejercicios precargados no aparecen acá porque no se pueden editar ni eliminar.
    """
    def __init__(self, parent, dni_usuario, fn_agregar_ejercicio, fn_obtener_ejercicios_propios, fn_actualizar_ejercicio, fn_eliminar_ejercicio):
        app = parent.winfo_toplevel()
        super().__init__(app, fg_color="transparent")
        self.app = app

        self.dni_usuario = dni_usuario
        self.fn_agregar_ejercicio = fn_agregar_ejercicio
        self.fn_obtener_ejercicios_propios = fn_obtener_ejercicios_propios
        self.fn_actualizar_ejercicio = fn_actualizar_ejercicio
        self.fn_eliminar_ejercicio = fn_eliminar_ejercicio

        # Lista de objetos Ejercicio del usuario y el ID que se está por eliminar (confirmación)
        self.ejercicios = []
        self.id_para_confirmar = None
        # Diccionario de la lista desplegable (muestra nombres, sin IDs): {texto: objeto Ejercicio}
        self.mapa_ejercicios = {}

        # Encabezado: botón '◀ Volver' a la izquierda y el título de la sección
        crear_encabezado(self, "Mis Ejercicios", self.app.volver_pantalla)

        ctk.CTkButton(self, text="+ Crear Ejercicio Nuevo", command=self.crear_ejercicio, width=340, fg_color=verde, hover_color=verde_hover).pack(pady=5)

        ctk.CTkLabel(self, text="Seleccioná un ejercicio:", font=("Arial", 12, "bold")).pack(pady=(10, 0))
        self.combo_ejercicios = ctk.CTkOptionMenu(self, values=["Cargando..."], command=self.cambiar_seleccion, width=340)
        self.combo_ejercicios.pack(pady=5)

        # Acciones sobre el ejercicio elegido: Editar o Eliminar
        frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        frame_acciones.pack(pady=5)
        ctk.CTkButton(frame_acciones, text="Editar", command=self.editar_ejercicio, fg_color=naranja, hover_color=naranja_hover, text_color="black", width=160).pack(side="left", padx=5)
        self.btn_eliminar = ctk.CTkButton(frame_acciones, text="Eliminar", command=self.eliminar_ejercicio, fg_color=rojo, hover_color=rojo_hover, width=160)
        self.btn_eliminar.pack(side="left", padx=5)

        # Etiqueta para mostrar avisos y mensajes
        self.lbl_msg = ctk.CTkLabel(self, text="", font=("Arial", 12, "bold"), wraplength=340)
        self.lbl_msg.pack(pady=5)

        # Lista de todos los ejercicios propios
        ctk.CTkLabel(self, text="Tus ejercicios personalizados:", font=("Arial", 12, "bold")).pack(pady=(5, 0))
        self.txt_lista = ctk.CTkTextbox(self, width=350, height=220, wrap="word")
        solo_lectura(self.txt_lista)  # el usuario no puede modificar el texto
        self.txt_lista.pack(pady=5)

        self.cargar_ejercicios()

        # Mostramos esta pantalla dentro de la ventana principal
        self.app.abrir_pantalla(self)

    def mostrar_mensaje(self, texto, color):
        """Muestra un aviso en la etiqueta de mensajes."""
        self.lbl_msg.configure(text=texto, text_color=color)

    def cargar_ejercicios(self):
        """Carga en la lista y en el cuadro de texto los ejercicios creados por el usuario."""
        self.ejercicios = self.fn_obtener_ejercicios_propios(self.dni_usuario) if self.fn_obtener_ejercicios_propios else []
        # La lista muestra solo el nombre; el objeto Ejercicio queda guardado en el diccionario
        self.mapa_ejercicios = {}
        for ej in self.ejercicios:
            texto = texto_unico(ej.nombre, self.mapa_ejercicios)
            self.mapa_ejercicios[texto] = ej
        opciones = list(self.mapa_ejercicios.keys()) if self.mapa_ejercicios else ["No tenés ejercicios propios"]
        self.combo_ejercicios.configure(values=opciones)
        self.combo_ejercicios.set(opciones[0])
        self.cambiar_seleccion(opciones[0])

        self.txt_lista.delete("1.0", "end")
        if not self.ejercicios:
            self.txt_lista.insert("end", "Todavía no creaste ejercicios propios.\nLos ejercicios precargados no se pueden editar ni eliminar.")
            return
        # Cada ejercicio es un objeto Ejercicio, mostramos su __str__
        for ej in self.ejercicios:
            self.txt_lista.insert("end", f"• {ej}\n")

    def cambiar_seleccion(self, seleccion):
        """Si cambia el ejercicio elegido, se cancela cualquier confirmación de eliminación pendiente."""
        self.id_para_confirmar = None
        self.btn_eliminar.configure(text="Eliminar")

    def buscar_ejercicio_seleccionado(self):
        """Devuelve el objeto Ejercicio elegido en la lista (buscándolo en el diccionario), o None."""
        return self.mapa_ejercicios.get(self.combo_ejercicios.get())

    def crear_ejercicio(self):
        VentanaCrearEjercicioModal(self, self.dni_usuario, self.fn_agregar_ejercicio, self.ejercicio_creado)

    def ejercicio_creado(self):
        self.cargar_ejercicios()
        self.mostrar_mensaje("✔ Ejercicio creado.", "#2ECC71")

    def editar_ejercicio(self):
        """Abre la pantalla para editar el ejercicio elegido (con sus datos ya cargados)."""
        ejercicio = self.buscar_ejercicio_seleccionado()
        if not ejercicio:
            self.mostrar_mensaje("⚠ No hay ningún ejercicio para editar.", naranja)
            return
        VentanaEditarEjercicioModal(self, ejercicio.id_ejercicio, self.dni_usuario, self.fn_actualizar_ejercicio, self.ejercicio_editado, ejercicio)

    def ejercicio_editado(self):
        self.cargar_ejercicios()
        self.mostrar_mensaje("✔ Ejercicio actualizado.", "#2ECC71")

    def eliminar_ejercicio(self):
        """Elimina (baja lógica) el ejercicio elegido. Pide confirmación tocando el botón dos veces."""
        ejercicio = self.buscar_ejercicio_seleccionado()
        if not ejercicio:
            self.mostrar_mensaje("⚠ No hay ningún ejercicio para eliminar.", naranja)
            return

        # Primer clic: pedimos confirmación
        if self.id_para_confirmar != ejercicio.id_ejercicio:
            self.id_para_confirmar = ejercicio.id_ejercicio
            self.btn_eliminar.configure(text="Confirmar")
            self.mostrar_mensaje(f"⚠ ¿Seguro? '{ejercicio.nombre}' se va a quitar de tus rutinas, pero tu historial de entrenamiento se conserva. Tocá 'Confirmar'.", naranja)
            return

        # Segundo clic: eliminamos (la función de DB valida que el ejercicio sea del usuario)
        if self.fn_eliminar_ejercicio(ejercicio.id_ejercicio, self.dni_usuario):
            self.cargar_ejercicios()
            self.mostrar_mensaje(f"✔ '{ejercicio.nombre}' eliminado.", "#2ECC71")
        else:
            self.mostrar_mensaje("❌ No se pudo eliminar. Solo podés eliminar ejercicios propios.", rojo_hover)


class VentanaCrearEjercicioModal(ctk.CTkFrame):
    def __init__(self, parent, dni_usuario, fn_agregar_ejercicio, fn_callback_actualizar):
        app = parent.winfo_toplevel()
        super().__init__(app, fg_color="transparent")
        self.app = app
        self.dni_usuario = dni_usuario
        self.fn_agregar_ejercicio = fn_agregar_ejercicio
        self.fn_callback_actualizar = fn_callback_actualizar

        ctk.CTkLabel(self, text="Nuevo Ejercicio", font=("Arial", 16, "bold")).pack(pady=10)
        self.ent_nom = ctk.CTkEntry(self, placeholder_text="Nombre ejercicio", width=250)
        self.ent_nom.pack(pady=5)
        self.combo_g = ctk.CTkOptionMenu(self, values=GRUPOS_MUSCULARES, width=250)
        self.combo_g.pack(pady=5)
        self.combo_t = ctk.CTkOptionMenu(self, values=TIPOS_EJERCICIO, width=250)
        self.combo_t.pack(pady=5)

        def guardar():
            nombre_ej = self.ent_nom.get().strip()
            if nombre_ej:
                self.fn_agregar_ejercicio(self.dni_usuario, nombre_ej, self.combo_g.get(), self.combo_t.get())
                self.fn_callback_actualizar()
                # Volvemos a la pantalla anterior
                self.app.volver_pantalla()

        ctk.CTkButton(self, text="Guardar Ejercicio", command=guardar, fg_color=verde, hover_color=verde_hover, width=250).pack(pady=15)
        ctk.CTkButton(self, text="Volver", command=self.app.volver_pantalla, fg_color=gris, hover_color=gris_hover, width=250).pack(pady=5)

        # Mostramos esta pantalla dentro de la ventana principal
        self.app.abrir_pantalla(self)


class VentanaEditarEjercicioModal(ctk.CTkFrame):
    def __init__(self, parent, id_ejercicio, dni_usuario, fn_actualizar_ejercicio, fn_callback_actualizar, ejercicio=None):
        app = parent.winfo_toplevel()
        super().__init__(app, fg_color="transparent")
        self.app = app
        self.id_ejercicio = id_ejercicio
        self.dni_usuario = dni_usuario
        self.fn_actualizar_ejercicio = fn_actualizar_ejercicio
        self.fn_callback_actualizar = fn_callback_actualizar

        ctk.CTkLabel(self, text="Editar Ejercicio", font=("Arial", 16, "bold")).pack(pady=10)
        ctk.CTkLabel(self, text="Nuevo nombre:", font=("Arial", 11)).pack()
        self.ent_nom = ctk.CTkEntry(self, placeholder_text="Nombre del ejercicio", width=250)
        self.ent_nom.pack(pady=5)
        self.combo_g = ctk.CTkOptionMenu(self, values=GRUPOS_MUSCULARES, width=250)
        self.combo_g.pack(pady=5)
        self.combo_t = ctk.CTkOptionMenu(self, values=TIPOS_EJERCICIO, width=250)
        self.combo_t.pack(pady=5)

        # Si recibimos el objeto Ejercicio, cargamos sus datos actuales para editarlos
        if ejercicio:
            self.ent_nom.insert(0, ejercicio.nombre)
            self.combo_g.set(ejercicio.grupo_muscular)
            self.combo_t.set(ejercicio.tipo_ejercicio)

        self.lbl_msg = ctk.CTkLabel(self, text="", text_color="#E74C3C", font=("Arial", 11))
        self.lbl_msg.pack(pady=2)

        def guardar():
            nombre_ej = self.ent_nom.get().strip().title()
            if not nombre_ej:
                self.lbl_msg.configure(text="⚠ El nombre no puede estar vacío.")
                return
            # La función de DB valida que el ejercicio le pertenezca al usuario
            if self.fn_actualizar_ejercicio(self.id_ejercicio, self.dni_usuario, nombre_ej, self.combo_g.get(), self.combo_t.get()):
                self.fn_callback_actualizar()
                # Volvemos a la pantalla anterior
                self.app.volver_pantalla()
            else:
                self.lbl_msg.configure(text="❌ No se pudo editar. Solo podés editar ejercicios propios.")

        ctk.CTkButton(self, text="Guardar Cambios", command=guardar, fg_color=verde, hover_color=verde_hover, width=250).pack(pady=10)
        ctk.CTkButton(self, text="Cancelar", command=self.app.volver_pantalla, fg_color=gris, hover_color=gris_hover, width=250).pack(pady=5)

        # Mostramos esta pantalla dentro de la ventana principal
        self.app.abrir_pantalla(self)


# Sección "Empezar Rutina": se abre desde el menú principal para entrenar y registrar series
class VentanaComenzarEntrenar(ctk.CTkFrame):
    def __init__(self, parent, dni_usuario, fn_obtener_rutinas, fn_obtener_dias, fn_registrar_serie, fn_obtener_ejercicios_dia=None, fn_obtener_series_fecha=None, fn_obtener_ultima_fecha=None, fn_obtener_ultimo_dia=None):
        app = parent.winfo_toplevel()
        super().__init__(app, fg_color="transparent")
        self.app = app

        self.dni_usuario = dni_usuario
        self.fn_obtener_rutinas = fn_obtener_rutinas
        self.fn_obtener_dias = fn_obtener_dias
        self.fn_registrar_serie = fn_registrar_serie
        self.fn_obtener_ejercicios_dia = fn_obtener_ejercicios_dia
        # Funciones para ver las series de hoy y lo que hizo la última vez en cada ejercicio
        self.fn_obtener_series_fecha = fn_obtener_series_fecha
        self.fn_obtener_ultima_fecha = fn_obtener_ultima_fecha
        # Función para saber qué día de la rutina entrenó por última vez (para sugerir el día de hoy)
        self.fn_obtener_ultimo_dia = fn_obtener_ultimo_dia

        # Diccionario con la cantidad de series planificadas de cada ejercicio del día {id_ejercicio: series}
        self.series_planificadas = {}
        # Máximo de series del ejercicio elegido (límite del campo N° de serie)
        self.max_series_actual = 10
        # Diccionarios de las listas desplegables (muestran nombres, sin IDs):
        # rutinas {texto: id_rutina}, días {texto: id_rutina_dia} y ejercicios {texto: (id_ejercicio, nombre)}
        self.mapa_rutinas = {}
        self.mapa_dias = {}
        self.mapa_ejercicios_dia = {}
        # Número de cada día de la lista {texto: numero_dia} (se guarda junto con cada serie)
        self.numero_de_dia = {}

        # Encabezado fijo (fuera del scroll) para que el botón '◀ Volver' siempre se vea
        crear_encabezado(self, "Empezar Rutina", self.app.volver_pantalla)

        # Contenedor con scroll para asegurar que todos los campos sean visibles
        scroll_c = ctk.CTkScrollableFrame(self, width=365, height=565)
        scroll_c.pack(fill="both", expand=True, padx=5, pady=5)

        # 1. SELECCIONAR RUTINA
        rutinas = self.fn_obtener_rutinas(self.dni_usuario)
        # Cada rutina es un objeto Rutina: la lista muestra su nombre y el ID queda en el diccionario
        for r in rutinas:
            texto = texto_unico(r.nombre_rutina, self.mapa_rutinas)
            self.mapa_rutinas[texto] = r.id_rutina
        lista_rutinas = list(self.mapa_rutinas.keys()) if self.mapa_rutinas else ["Sin Rutinas"]

        # Si el usuario no tiene rutinas, le indicamos dónde crearlas
        if not rutinas:
            ctk.CTkLabel(
                scroll_c, text="⚠ Todavía no tenés rutinas creadas.\nCreá una desde 'Gestionar Rutina' en el menú principal.",
                font=("Arial", 12, "bold"), text_color=naranja, wraplength=340
            ).pack(pady=(5, 10))

        ctk.CTkLabel(scroll_c, text="1. Seleccionar Rutina:", font=("Arial", 12, "bold")).pack(pady=(5, 0))
        self.combo_rutinas = ctk.CTkOptionMenu(scroll_c, values=lista_rutinas, command=self.cargar_dias_rutina, width=340)
        self.combo_rutinas.pack(pady=5)

        # 2. SELECCIONAR DÍA DE LA RUTINA
        ctk.CTkLabel(scroll_c, text="2. Seleccionar Día de la Rutina:", font=("Arial", 12, "bold")).pack(pady=(5, 0))
        self.combo_dias = ctk.CTkOptionMenu(scroll_c, values=["Seleccione rutina primero"], command=self.cargar_ejercicios_del_dia, width=340)
        self.combo_dias.pack(pady=5)

        # 3. SELECCIONAR EJERCICIO DEL DÍA
        ctk.CTkLabel(scroll_c, text="3. Ejercicio asignado para hoy:", font=("Arial", 12, "bold")).pack(pady=(5, 0))
        self.combo_ejercicios_dia = ctk.CTkOptionMenu(scroll_c, values=["Seleccione día primero"], command=self.seleccionar_ejercicio, width=340)
        self.combo_ejercicios_dia.pack(pady=5)

        # Información del ejercicio elegido: serie actual, lo que hizo hoy y la última vez
        self.lbl_serie_actual = ctk.CTkLabel(scroll_c, text="", font=("Arial", 14, "bold"), text_color=amarillo, wraplength=340)
        self.lbl_serie_actual.pack(pady=(8, 0))
        self.lbl_hoy = ctk.CTkLabel(scroll_c, text="", font=("Arial", 11), text_color="#CCCCCC", wraplength=340)
        self.lbl_hoy.pack()
        self.lbl_ultima_vez = ctk.CTkLabel(scroll_c, text="", font=("Arial", 11), text_color="#A0A0A0", wraplength=340)
        self.lbl_ultima_vez.pack()

        # 4. REGISTRAR SERIE (PESO Y REPETICIONES)
        ctk.CTkLabel(scroll_c, text="Anotar peso y repeticiones por serie:", font=("Arial", 13, "bold"), text_color="#2ECC71").pack(pady=10)

        # Cada campo tiene su etiqueta a la izquierda (así se entiende aunque el campo ya tenga un número)
        frame_serie = ctk.CTkFrame(scroll_c, fg_color="transparent")
        frame_serie.pack(pady=3)
        ctk.CTkLabel(frame_serie, text="N° de serie:", width=110, anchor="w").pack(side="left", padx=5)
        self.ent_serie_num = ctk.CTkEntry(frame_serie, placeholder_text="ej: 1", width=148)
        self.ent_serie_num.pack(side="left", padx=5)
        # Flechas para subir y bajar el número de serie (de 1 hasta las series planificadas del ejercicio)
        ctk.CTkButton(frame_serie, text="▲", command=self.subir_serie, width=32, fg_color=gris, hover_color=gris_hover).pack(side="left", padx=2)
        ctk.CTkButton(frame_serie, text="▼", command=self.bajar_serie, width=32, fg_color=gris, hover_color=gris_hover).pack(side="left", padx=2)

        frame_peso = ctk.CTkFrame(scroll_c, fg_color="transparent")
        frame_peso.pack(pady=3)
        ctk.CTkLabel(frame_peso, text="Peso (kg):", width=110, anchor="w").pack(side="left", padx=5)
        self.ent_peso = ctk.CTkEntry(frame_peso, placeholder_text="ej: 80 (0 = peso corporal)", width=220)
        self.ent_peso.pack(side="left", padx=5)

        frame_reps = ctk.CTkFrame(scroll_c, fg_color="transparent")
        frame_reps.pack(pady=3)
        ctk.CTkLabel(frame_reps, text="Repeticiones:", width=110, anchor="w").pack(side="left", padx=5)
        self.ent_reps = ctk.CTkEntry(frame_reps, placeholder_text="ej: 12", width=220)
        self.ent_reps.pack(side="left", padx=5)

        ctk.CTkButton(scroll_c, text="✔ Guardar Registro", command=self.guardar_serie, width=340, fg_color=verde, hover_color=verde_hover).pack(pady=10)

        self.txt_salida = ctk.CTkTextbox(scroll_c, width=350, height=120, wrap="word")
        solo_lectura(self.txt_salida)  # el usuario no puede modificar el texto
        self.txt_salida.pack(pady=5)

        if lista_rutinas and lista_rutinas[0] != "Sin Rutinas":
            self.cargar_dias_rutina(lista_rutinas[0])

        # Vinculamos scroll fluido en toda la superficie
        habilitar_scroll_fluido(self, scroll_c)

        # Mostramos esta pantalla dentro de la ventana principal
        self.app.abrir_pantalla(self)

    def cargar_dias_rutina(self, seleccion_rutina):
        """Carga los días que componen la rutina elegida."""
        id_rutina = self.mapa_rutinas.get(seleccion_rutina)
        if id_rutina:
            dias = self.fn_obtener_dias(id_rutina)
            # La lista muestra "Día 1 (Pecho)" y el ID del día queda en el diccionario
            self.mapa_dias = {}
            self.numero_de_dia = {}
            for d in dias:
                texto = texto_unico(f"Día {d[1]} ({d[2]})", self.mapa_dias)
                self.mapa_dias[texto] = d[0]
                self.numero_de_dia[texto] = d[1]
            opciones = list(self.mapa_dias.keys()) if self.mapa_dias else ["Sin Días"]
            self.combo_dias.configure(values=opciones)
            if opciones[0] != "Sin Días":
                # Elegimos automáticamente el día que le toca hoy
                dia_sugerido = self.sugerir_dia(id_rutina, dias, opciones)
                self.combo_dias.set(dia_sugerido)
                self.cargar_ejercicios_del_dia(dia_sugerido)
            else:
                self.combo_dias.set(opciones[0])
                self.combo_ejercicios_dia.configure(values=["Sin Ejercicios"])
                self.combo_ejercicios_dia.set("Sin Ejercicios")
                self.seleccionar_ejercicio("")

    def cargar_ejercicios_del_dia(self, seleccion_dia):
        """Carga los ejercicios programados para el día seleccionado."""
        id_dia = self.mapa_dias.get(seleccion_dia)
        if id_dia and self.fn_obtener_ejercicios_dia:
            ejercicios = self.fn_obtener_ejercicios_dia(id_dia)
            # Guardamos cuántas series tiene planificadas cada ejercicio y armamos la lista
            # (muestra "Nombre (3 Series)" y el ID y nombre del ejercicio quedan en el diccionario)
            self.series_planificadas = {}
            self.mapa_ejercicios_dia = {}
            for ej in ejercicios:
                self.series_planificadas[ej[0]] = ej[3]
                texto = texto_unico(f"{ej[1]} ({ej[3]} Series)", self.mapa_ejercicios_dia)
                self.mapa_ejercicios_dia[texto] = (ej[0], ej[1])
            if ejercicios:
                opciones = list(self.mapa_ejercicios_dia.keys())
                self.combo_ejercicios_dia.configure(values=opciones)
                self.combo_ejercicios_dia.set(opciones[0])
                self.seleccionar_ejercicio(opciones[0])
            else:
                self.combo_ejercicios_dia.configure(values=["Sin ejercicios asignados a este día"])
                self.combo_ejercicios_dia.set("Sin ejercicios asignados a este día")
                self.seleccionar_ejercicio("")

    def sugerir_dia(self, id_rutina, dias, opciones):
        """
        Devuelve el texto del día que le toca entrenar hoy:
        - Si nunca entrenó esta rutina: el Día 1.
        - Si hoy ya entrenó: el mismo día (para seguir cargando series).
        - Si no: el día siguiente al último que entrenó (después del último vuelve al Día 1).
        """
        ultimo = None
        if self.fn_obtener_ultimo_dia:
            ultimo = self.fn_obtener_ultimo_dia(self.dni_usuario, id_rutina)

        # Lista con los números de día de la rutina (ej: [1, 2, 3])
        numeros = []
        for d in dias:
            numeros.append(d[1])

        if not ultimo:
            # Nunca entrenó esta rutina: empieza por el primer día
            numero_sugerido = numeros[0]
        else:
            numero_ultimo, fecha_ultima = ultimo
            if fecha_ultima == date.today():
                # Hoy ya entrenó: sigue con el mismo día
                numero_sugerido = numero_ultimo
            else:
                # Buscamos el día siguiente al último entrenado (si era el último, volvemos al primero)
                numero_sugerido = numeros[0]
                for numero in numeros:
                    if numero > numero_ultimo:
                        numero_sugerido = numero
                        break

        # Buscamos el texto de la lista que corresponde al día sugerido
        for texto in opciones:
            if texto.startswith(f"Día {numero_sugerido} "):
                return texto
        return opciones[0]

    def texto_series(self, series):
        """Arma un texto corto con una lista de series. Ej: 'S1: 80.0kg x 10 | S2: 80.0kg x 9'."""
        partes = []
        for serie in series:
            # Si el peso es 0, es un ejercicio con peso corporal: mostramos solo las repeticiones
            if serie[1] == 0:
                partes.append(f"S{serie[0]}: {serie[2]} reps")
            else:
                partes.append(f"S{serie[0]}: {serie[1]}kg x {serie[2]}")
        return " | ".join(partes)

    def seleccionar_ejercicio(self, seleccion_ej):
        """
        Al elegir un ejercicio: sugiere el número de la próxima serie, muestra 'Serie X de N',
        las series que ya hizo hoy y lo que hizo la última vez en ese ejercicio.
        """
        if seleccion_ej not in self.mapa_ejercicios_dia:
            self.lbl_serie_actual.configure(text="")
            self.lbl_hoy.configure(text="")
            self.lbl_ultima_vez.configure(text="")
            return

        # Buscamos en el diccionario el ID del ejercicio elegido
        id_ej = self.mapa_ejercicios_dia[seleccion_ej][0]
        hoy = date.today()
        total_series = self.series_planificadas.get(id_ej, 0)
        # El N° de serie solo puede ir de 1 hasta las series planificadas de este ejercicio
        self.max_series_actual = total_series if total_series > 0 else 10

        # Series que ya registró HOY en este ejercicio
        series_hoy = []
        if self.fn_obtener_series_fecha:
            series_hoy = self.fn_obtener_series_fecha(self.dni_usuario, id_ej, hoy)

        # La próxima serie es la mayor registrada hoy + 1 (si no hizo ninguna, es la 1)
        siguiente = 1
        for serie in series_hoy:
            if serie[0] >= siguiente:
                siguiente = serie[0] + 1

        if siguiente <= self.max_series_actual:
            self.lbl_serie_actual.configure(text=f"Serie {siguiente} de {total_series}")
        else:
            # Ya completó todas las series: el campo queda en la última (si la vuelve a cargar, se reemplaza)
            siguiente = self.max_series_actual
            self.lbl_serie_actual.configure(text=f"✔ Completaste las {total_series} series")
        self.ent_serie_num.delete(0, "end")
        self.ent_serie_num.insert(0, str(siguiente))

        if series_hoy:
            self.lbl_hoy.configure(text=f"Hoy: {self.texto_series(series_hoy)}")
        else:
            self.lbl_hoy.configure(text="Hoy todavía no registraste series de este ejercicio.")

        # Lo que hizo la ÚLTIMA VEZ (antes de hoy) en este ejercicio
        ultima_fecha = None
        if self.fn_obtener_ultima_fecha:
            ultima_fecha = self.fn_obtener_ultima_fecha(self.dni_usuario, id_ej, hoy)
        if ultima_fecha and self.fn_obtener_series_fecha:
            series_ultima = self.fn_obtener_series_fecha(self.dni_usuario, id_ej, ultima_fecha)
            self.lbl_ultima_vez.configure(text=f"Última vez ({ultima_fecha.strftime('%d/%m/%Y')}): {self.texto_series(series_ultima)}")
        else:
            self.lbl_ultima_vez.configure(text="Es la primera vez que registrás este ejercicio.")

    def guardar_serie(self):
        """Valida y guarda la serie realizada en la base de datos (si ya existía, la reemplaza)."""
        seleccion_ej = self.combo_ejercicios_dia.get()
        if seleccion_ej not in self.mapa_ejercicios_dia:
            self.txt_salida.insert("end", "⚠ Debe seleccionar un ejercicio válido.\n")
            return

        try:
            # Buscamos en el diccionario el ID y el nombre del ejercicio elegido
            id_ej = self.mapa_ejercicios_dia[seleccion_ej][0]
            nom_ej = self.mapa_ejercicios_dia[seleccion_ej][1]
            s_num = int(self.ent_serie_num.get().strip())
            peso = float(self.ent_peso.get().strip())
            reps = int(self.ent_reps.get().strip())
            hoy = date.today()

            if s_num < 1 or reps < 1 or peso < 0:
                self.txt_salida.insert("end", "⚠ La serie y las repeticiones deben ser mayores a 0 y el peso no puede ser negativo.\n")
                return

            # El N° de serie no puede superar las series planificadas del ejercicio
            if s_num > self.max_series_actual:
                self.txt_salida.insert("end", f"⚠ Este ejercicio tiene {self.max_series_actual} series: elegí una serie entre 1 y {self.max_series_actual}.\n")
                self.txt_salida.see("end")
                return

            # Creamos un objeto RegistroEntrenamiento con los datos de la serie
            # (el id_registro es None porque lo genera la base de datos)
            registro = RegistroEntrenamiento(None, self.dni_usuario, id_ej, hoy, s_num, peso, reps)

            # Guardamos también qué rutina y qué día se está entrenando (para poder comparar días iguales)
            id_rutina = self.mapa_rutinas.get(self.combo_rutinas.get())
            numero_dia = self.numero_de_dia.get(self.combo_dias.get())

            resultado = self.fn_registrar_serie(registro.dni_usuario, registro.id_ejercicio, registro.fecha, registro.serie_numero, registro.peso_kg, registro.repeticiones, id_rutina, numero_dia)
            # Usamos el __str__ y el método calcular_volumen() de la clase
            # (si el peso es 0 es un ejercicio con peso corporal y no tiene volumen en kg)
            texto_volumen = "Peso corporal" if peso == 0 else f"Volumen: {registro.calcular_volumen():.1f} kg"
            if resultado == "reemplazada":
                self.txt_salida.insert("end", f"🔄 {nom_ej} -> {registro} | {texto_volumen} (serie reemplazada)\n")
            elif resultado:
                self.txt_salida.insert("end", f"✔ {nom_ej} -> {registro} | {texto_volumen} (guardada)\n")
            else:
                self.txt_salida.insert("end", "❌ Error al guardar la serie en la base de datos.\n")

            if resultado:
                # Actualizamos la información y sugerimos la siguiente serie
                self.seleccionar_ejercicio(seleccion_ej)
                # Si con esta serie completó las series planificadas, pasamos solos al siguiente ejercicio
                if resultado == "nueva" and s_num == self.series_planificadas.get(id_ej, 0):
                    self.pasar_al_siguiente_ejercicio(seleccion_ej)
            self.txt_salida.see("end")
        except ValueError:
            self.txt_salida.insert("end", "⚠ Ingrese números válidos para serie, peso y repeticiones.\n")

    def cambiar_numero_serie(self, cambio):
        """Suma o resta 1 al número de serie (siempre entre 1 y las series planificadas del ejercicio)."""
        texto = self.ent_serie_num.get().strip()
        numero = int(texto) if texto.isdigit() else 1
        numero = numero + cambio
        if numero < 1:
            numero = 1
        if numero > self.max_series_actual:
            numero = self.max_series_actual
        self.ent_serie_num.delete(0, "end")
        self.ent_serie_num.insert(0, str(numero))

    def subir_serie(self):
        """Flecha ▲: suma una serie (máximo: las series planificadas del ejercicio)."""
        self.cambiar_numero_serie(1)

    def bajar_serie(self):
        """Flecha ▼: resta una serie (mínimo 1)."""
        self.cambiar_numero_serie(-1)

    def pasar_al_siguiente_ejercicio(self, seleccion_actual):
        """Al terminar las series de un ejercicio, elige automáticamente el siguiente ejercicio del día."""
        opciones = list(self.mapa_ejercicios_dia.keys())
        posicion = opciones.index(seleccion_actual)
        if posicion + 1 < len(opciones):
            siguiente = opciones[posicion + 1]
            self.combo_ejercicios_dia.set(siguiente)
            # Limpiamos peso y repeticiones porque es otro ejercicio
            self.ent_peso.delete(0, "end")
            self.ent_reps.delete(0, "end")
            self.seleccionar_ejercicio(siguiente)
            self.txt_salida.insert("end", f"➡ Terminaste las series. Siguiente ejercicio: {self.mapa_ejercicios_dia[siguiente][1]}\n")
        else:
            self.txt_salida.insert("end", "🏁 ¡Terminaste todos los ejercicios del día! Buen entrenamiento.\n")


class VentanaVerSeguimiento(ctk.CTkFrame):
    """
    Pantalla de Ver Seguimiento.
    Incluye:
    1. Calendario interactivo con formato semanal (L M M J V S D) y navegación de meses.
    2. Selección de Fecha 1 y Fecha 2.
    3. Visualización de los entrenamientos de ambas fechas.
    4. Comparativa de rendimiento entre Fecha 1 y Fecha 2.
    5. Análisis inteligente con IA (Gemini) sobre estadísticas, puntos fuertes, débiles y consejos.
    """
    def __init__(self, parent, dni_usuario, fn_obtener_seguimiento, fn_obtener_fechas_entrenadas=None, fn_obtener_registros_fecha=None, fn_analizar_ia=None, nombre_usuario="Atleta", fn_obtener_dias_por_fecha=None, fn_obtener_grupos_por_fecha=None):
        app = parent.winfo_toplevel()
        super().__init__(app, fg_color="transparent")
        self.app = app

        self.dni_usuario = dni_usuario
        self.fn_obtener_seguimiento = fn_obtener_seguimiento
        self.fn_obtener_fechas_entrenadas = fn_obtener_fechas_entrenadas
        self.fn_obtener_registros_fecha = fn_obtener_registros_fecha
        self.fn_analizar_ia = fn_analizar_ia
        self.nombre_usuario = nombre_usuario

        # Rutina y día entrenado en cada fecha {fecha: (id_rutina, numero_dia, nombre_rutina)}
        # Se usa para saber qué días se pueden comparar (misma rutina y mismo día)
        self.dias_por_fecha = {}
        if fn_obtener_dias_por_fecha:
            self.dias_por_fecha = fn_obtener_dias_por_fecha(self.dni_usuario)

        # Grupos musculares entrenados en cada fecha {fecha: "Pecho, Tríceps"} (según los ejercicios registrados)
        self.grupos_por_fecha = {}
        if fn_obtener_grupos_por_fecha:
            self.grupos_por_fecha = fn_obtener_grupos_por_fecha(self.dni_usuario)

        # Fechas seleccionadas para comparar
        self.fecha_seleccionada = None
        self.fecha_1 = None
        self.fecha_2 = None

        # Fecha actual para el calendario
        hoy = date.today()
        self.año_cal = hoy.year
        self.mes_cal = hoy.month

        # Cargamos las fechas donde el usuario tiene entrenamientos registrados
        self.fechas_con_registro = set()
        if self.fn_obtener_fechas_entrenadas:
            self.fechas_con_registro = set(self.fn_obtener_fechas_entrenadas(self.dni_usuario))
        else:
            todos = self.fn_obtener_seguimiento(self.dni_usuario)
            if todos:
                for r in todos:
                    f_str = r[0].strftime("%Y-%m-%d") if hasattr(r[0], "strftime") else str(r[0])
                    self.fechas_con_registro.add(f_str)

        # Encabezado fijo (fuera del scroll) para que el botón '◀ Volver' siempre se vea
        crear_encabezado(self, "Seguimiento de Entrenamiento", self.app.volver_pantalla, pady=(5, 2))

        # Contenedor principal con scroll
        self.scroll_c = ctk.CTkScrollableFrame(self, width=365, height=555)
        self.scroll_c.pack(fill="both", expand=True, padx=5, pady=5)

        # Diccionario con los botones de los días del mes {fecha: botón} para poder pintarlos
        self.botones_dias = {}

        ctk.CTkLabel(self.scroll_c, text="Calendario interactivo, comparativa de sesiones y análisis con IA", font=("Arial", 12), text_color="#A0A0A0", wraplength=340).pack(pady=(0, 10))

        # SECCIÓN 1: CALENDARIO INTERACTIVO (L M M J V S D)
        self.frame_cal_contenedor = ctk.CTkFrame(self.scroll_c, fg_color="#1E1E1E", corner_radius=10)
        self.frame_cal_contenedor.pack(pady=5, padx=5, fill="x")

        frame_nav = ctk.CTkFrame(self.frame_cal_contenedor, fg_color="transparent")
        frame_nav.pack(pady=8, fill="x", padx=10)

        ctk.CTkButton(frame_nav, text="◀ Mes Ant.", width=90, height=28, command=self.mes_anterior, fg_color=gris, hover_color=gris_hover).pack(side="left")
        self.lbl_mes_año = ctk.CTkLabel(frame_nav, text="", font=("Arial", 14, "bold"), text_color=amarillo)
        self.lbl_mes_año.pack(side="left", expand=True)
        ctk.CTkButton(frame_nav, text="Mes Sig. ▶", width=90, height=28, command=self.mes_siguiente, fg_color=gris, hover_color=gris_hover).pack(side="right")

        frame_dias_sem = ctk.CTkFrame(self.frame_cal_contenedor, fg_color="transparent")
        frame_dias_sem.pack(pady=(2, 4), padx=10)
        dias_letras = ["L", "M", "M", "J", "V", "S", "D"]
        for col_idx, letra in enumerate(dias_letras):
            # Mismo ancho que los botones de los días para que queden alineados
            lbl_dia = ctk.CTkLabel(frame_dias_sem, text=letra, width=38, font=("Arial", 12, "bold"), text_color=azul_claro)
            lbl_dia.grid(row=0, column=col_idx, padx=2, pady=2)

        self.frame_grilla_dias = ctk.CTkFrame(self.frame_cal_contenedor, fg_color="transparent")
        self.frame_grilla_dias.pack(pady=(0, 4), padx=10)

        self.actualizar_vista_calendario()

        # Referencia de colores del calendario
        ctk.CTkLabel(
            self.frame_cal_contenedor,
            text="Verde: día entrenado  |  Azul: Fecha 1  |  Amarillo: Fecha 2\nAmarillo oscuro: días comparables con la Fecha 1\nBorde blanco: día seleccionado",
            font=("Arial", 10), text_color="#A0A0A0"
        ).pack(pady=(0, 4))

        # Texto con los días que se pueden comparar con la Fecha 1 (misma rutina y mismo día)
        self.lbl_comparables = ctk.CTkLabel(
            self.frame_cal_contenedor, text="Elegí la Fecha 1 para ver con qué días se puede comparar.",
            font=("Arial", 11), text_color=amarillo, wraplength=340
        )
        self.lbl_comparables.pack(pady=(0, 6))

        frame_sel_botones = ctk.CTkFrame(self.frame_cal_contenedor, fg_color="transparent")
        frame_sel_botones.pack(pady=(0, 10), padx=10, fill="x")

        self.lbl_fecha_activa = ctk.CTkLabel(frame_sel_botones, text="Hacé clic en un día del calendario.", font=("Arial", 12, "bold"), wraplength=340)
        self.lbl_fecha_activa.pack(pady=3)

        frame_fijar = ctk.CTkFrame(frame_sel_botones, fg_color="transparent")
        frame_fijar.pack(pady=3)

        ctk.CTkButton(
            frame_fijar, text="Seleccionar Fecha 1", command=self.fijar_fecha_1,
            fg_color=azul, hover_color=azul_hover, font=("Arial", 12, "bold"), width=160
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            frame_fijar, text="Seleccionar Fecha 2", command=self.fijar_fecha_2,
            fg_color=amarillo, hover_color=amarillo_hover, text_color="black", font=("Arial", 12, "bold"), width=160
        ).pack(side="left", padx=4)

        # SECCIÓN 2: CARDS DE FECHA 1 Y FECHA 2 (una debajo de la otra para que entren en la ventana)
        frame_cards = ctk.CTkFrame(self.scroll_c, fg_color="transparent")
        frame_cards.pack(pady=8, padx=5, fill="x")

        self.card_f1 = ctk.CTkFrame(frame_cards, fg_color="#262626", corner_radius=8)
        self.card_f1.pack(fill="x", pady=4)
        self.lbl_titulo_f1 = ctk.CTkLabel(self.card_f1, text="Fecha 1: (No seleccionada)", font=("Arial", 13, "bold"), text_color=azul_hover, wraplength=330)
        self.lbl_titulo_f1.pack(pady=5)
        self.txt_card_f1 = ctk.CTkTextbox(self.card_f1, width=340, height=110, wrap="word")
        solo_lectura(self.txt_card_f1)  # el usuario no puede modificar el texto
        self.txt_card_f1.pack(pady=5, padx=8)

        self.card_f2 = ctk.CTkFrame(frame_cards, fg_color="#262626", corner_radius=8)
        self.card_f2.pack(fill="x", pady=4)
        self.lbl_titulo_f2 = ctk.CTkLabel(self.card_f2, text="Fecha 2: (No seleccionada)", font=("Arial", 13, "bold"), text_color=amarillo, wraplength=330)
        self.lbl_titulo_f2.pack(pady=5)
        self.txt_card_f2 = ctk.CTkTextbox(self.card_f2, width=340, height=110, wrap="word")
        solo_lectura(self.txt_card_f2)  # el usuario no puede modificar el texto
        self.txt_card_f2.pack(pady=5, padx=8)

        ctk.CTkButton(
            self.scroll_c, text="Comparar Fecha 1 con Fecha 2", command=self.comparar_fechas,
            fg_color=verde, hover_color=verde_hover, width=340, height=35, font=("Arial", 13, "bold")
        ).pack(pady=6)

        self.txt_resultado_comparativa = ctk.CTkTextbox(self.scroll_c, width=350, height=130, wrap="word")
        solo_lectura(self.txt_resultado_comparativa)  # el usuario no puede modificar el texto
        self.txt_resultado_comparativa.pack(pady=5)

        # SECCIÓN 3: INTELIGENCIA ARTIFICIAL (GEMINI)
        ctk.CTkLabel(self.scroll_c, text="Análisis Inteligente", font=("Arial", 14, "bold"), text_color=azul_claro, wraplength=340).pack(pady=(12, 4))

        self.btn_ia = ctk.CTkButton(
            self.scroll_c, text="Analizar Rendimiento", command=self.pedir_analisis_ia,
            fg_color=azul, hover_color=azul_hover, width=340, height=38, font=("Arial", 13, "bold")
        )
        self.btn_ia.pack(pady=5)

        self.txt_ia = ctk.CTkTextbox(self.scroll_c, width=350, height=260, wrap="word")
        solo_lectura(self.txt_ia)  # el usuario no puede modificar el texto
        self.txt_ia.pack(pady=5)

        # Vinculamos scroll fluido en toda la superficie
        habilitar_scroll_fluido(self, self.scroll_c)

        # Mostramos esta pantalla dentro de la ventana principal
        self.app.abrir_pantalla(self)

    def actualizar_vista_calendario(self):
        for widget in self.frame_grilla_dias.winfo_children():
            widget.destroy()

        nombres_meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.lbl_mes_año.configure(text=f"{nombres_meses[self.mes_cal]} {self.año_cal}")

        primer_dia_sem, total_dias = calendar.monthrange(self.año_cal, self.mes_cal)

        self.botones_dias = {}
        fila = 0
        col = primer_dia_sem
        for dia in range(1, total_dias + 1):
            fecha_str = f"{self.año_cal:04d}-{self.mes_cal:02d}-{dia:02d}"
            tiene_registro = fecha_str in self.fechas_con_registro

            btn_dia = ctk.CTkButton(
                self.frame_grilla_dias, text=str(dia), width=38, height=30,
                font=("Arial", 11, "bold" if tiene_registro else "normal"),
                command=lambda f=fecha_str: self.seleccionar_dia_calendario(f)
            )
            btn_dia.grid(row=fila, column=col, padx=2, pady=2)
            # Guardamos el botón para poder cambiarle el color después
            self.botones_dias[fecha_str] = btn_dia

            col += 1
            if col > 6:
                col = 0
                fila += 1

        self.pintar_calendario()
        habilitar_scroll_fluido(self, self.frame_grilla_dias)

    def pintar_calendario(self):
        """
        Pinta cada día del calendario según su estado:
        Azul = Fecha 1, Amarillo = Fecha 2, Amarillo oscuro = días comparables con la Fecha 1,
        Verde = día entrenado, Gris = sin registro. El día seleccionado se marca con un borde blanco.
        """
        comparables = self.dias_comparables()
        for fecha_str, btn_dia in self.botones_dias.items():
            if fecha_str == self.fecha_1:
                btn_color, hover_color, txt_color = azul, azul_hover, "#FFFFFF"
            elif fecha_str == self.fecha_2:
                btn_color, hover_color, txt_color = amarillo, amarillo_hover, "black"
            elif fecha_str in comparables:
                btn_color, hover_color, txt_color = amarillo_oscuro, amarillo_oscuro_hover, "#FFFFFF"
            elif fecha_str in self.fechas_con_registro:
                btn_color, hover_color, txt_color = verde, verde_hover, "#FFFFFF"
            else:
                btn_color, hover_color, txt_color = "#2E2E2E", "#444444", "#CCCCCC"

            # Borde blanco solo en el día que está seleccionado
            borde = 2 if fecha_str == self.fecha_seleccionada else 0
            btn_dia.configure(fg_color=btn_color, hover_color=hover_color, text_color=txt_color, border_width=borde, border_color="#FFFFFF")

    def mes_anterior(self):
        if self.mes_cal == 1:
            self.mes_cal = 12
            self.año_cal -= 1
        else:
            self.mes_cal -= 1
        self.actualizar_vista_calendario()

    def mes_siguiente(self):
        if self.mes_cal == 12:
            self.mes_cal = 1
            self.año_cal += 1
        else:
            self.mes_cal += 1
        self.actualizar_vista_calendario()

    def texto_dia_rutina(self, fecha_str):
        """Devuelve un texto con la rutina y el día entrenado en esa fecha. Ej: 'Día 3 de Push Pull Legs'."""
        if fecha_str in self.dias_por_fecha:
            id_rutina, numero_dia, nombre_rutina = self.dias_por_fecha[fecha_str]
            return f"Día {numero_dia} de {nombre_rutina}"
        return ""

    def es_mismo_dia_de_rutina(self, fecha_str):
        """Devuelve True si en esa fecha se entrenó la MISMA rutina y el MISMO día que en la Fecha 1."""
        if not self.fecha_1 or self.fecha_1 not in self.dias_por_fecha or fecha_str not in self.dias_por_fecha:
            return False
        id_rutina_1, numero_dia_1, nombre_rutina_1 = self.dias_por_fecha[self.fecha_1]
        datos = self.dias_por_fecha[fecha_str]
        return datos[0] == id_rutina_1 and datos[1] == numero_dia_1

    def dias_comparables(self):
        """
        Devuelve la lista de fechas que se pueden comparar con la Fecha 1:
        las fechas POSTERIORES a la Fecha 1 en las que se entrenó la misma rutina y el mismo día.
        (Las fechas en formato "AAAA-MM-DD" se pueden comparar como texto: "2026-11-10" > "2026-11-03")
        """
        comparables = []
        # Si todavía no hay Fecha 1 elegida, no hay días comparables
        if not self.fecha_1:
            return comparables
        for fecha_str in self.dias_por_fecha:
            if fecha_str > self.fecha_1 and self.es_mismo_dia_de_rutina(fecha_str):
                comparables.append(fecha_str)
        comparables.sort()
        return comparables

    def actualizar_texto_comparables(self):
        """Muestra debajo del calendario con qué días se puede comparar la Fecha 1."""
        if not self.fecha_1:
            texto = "Elegí la Fecha 1 para ver con qué días se puede comparar."
        elif self.fecha_1 not in self.dias_por_fecha:
            texto = "⚠ La Fecha 1 no tiene guardado qué rutina se entrenó (registro antiguo o día sin entrenamientos): no se puede comparar."
        else:
            comparables = self.dias_comparables()
            if comparables:
                # Mostramos las fechas en formato dd/mm/aaaa
                fechas_cortas = []
                for f in comparables:
                    fechas_cortas.append(formato_fecha(f))
                texto = f"Días comparables ({self.texto_dia_rutina(self.fecha_1)}): {', '.join(fechas_cortas)}"
            else:
                texto = f"Todavía no hay otro {self.texto_dia_rutina(self.fecha_1)} posterior a esta fecha para comparar."
        self.lbl_comparables.configure(text=texto)

    def seleccionar_dia_calendario(self, fecha_str):
        self.fecha_seleccionada = fecha_str
        # Ej: "11/11/2026: Registra entrenamiento (Piernas)" o "10/11/2026: No registra entrenamiento"
        if fecha_str in self.fechas_con_registro:
            grupos = self.grupos_por_fecha.get(fecha_str, "")
            texto = f"{formato_fecha(fecha_str)}: Registra entrenamiento"
            if grupos:
                texto += f" ({grupos})"
        else:
            texto = f"{formato_fecha(fecha_str)}: No registra entrenamiento"
        self.lbl_fecha_activa.configure(text=texto)
        # Marcamos el día elegido en el calendario
        self.pintar_calendario()

    def fijar_fecha_1(self):
        if not self.fecha_seleccionada:
            self.lbl_fecha_activa.configure(text="⚠ Hacé clic primero en un día del calendario.")
            return
        self.establecer_f1(self.fecha_seleccionada)

    def fijar_fecha_2(self):
        if not self.fecha_seleccionada:
            self.lbl_fecha_activa.configure(text="⚠ Hacé clic primero en un día del calendario.")
            return
        if not self.fecha_1:
            self.lbl_fecha_activa.configure(text="⚠ Primero elegí la Fecha 1.")
            return
        if self.fecha_1 not in self.dias_por_fecha:
            self.lbl_fecha_activa.configure(text="⚠ La Fecha 1 no tiene guardado qué rutina se entrenó: no se puede comparar.")
            return
        # La Fecha 2 tiene que ser posterior a la Fecha 1 (así la comparativa va de la más vieja a la más nueva)
        if self.fecha_seleccionada <= self.fecha_1:
            self.lbl_fecha_activa.configure(text="⚠ La Fecha 2 tiene que ser posterior a la Fecha 1. Elegí un día en amarillo oscuro.")
            return
        # Solo se puede elegir como Fecha 2 un día comparable (misma rutina y mismo día)
        if self.fecha_seleccionada not in self.dias_comparables():
            self.lbl_fecha_activa.configure(text=f"⚠ Ese día no es comparable. Elegí un día en amarillo oscuro ({self.texto_dia_rutina(self.fecha_1)}).")
            return
        self.establecer_f2(self.fecha_seleccionada)

    def limpiar_fecha_2(self):
        """Borra la Fecha 2 (se usa cuando cambia la Fecha 1 y la Fecha 2 deja de ser comparable)."""
        self.fecha_2 = None
        self.lbl_titulo_f2.configure(text="Fecha 2: (No seleccionada)")
        self.txt_card_f2.delete("1.0", "end")
        self.txt_resultado_comparativa.delete("1.0", "end")

    def obtener_registros_de_fecha(self, fecha_str):
        if self.fn_obtener_registros_fecha:
            return self.fn_obtener_registros_fecha(self.dni_usuario, fecha_str)
        todos = self.fn_obtener_seguimiento(self.dni_usuario)
        filtrados = []
        for r in todos:
            f = r[0].strftime("%Y-%m-%d") if hasattr(r[0], "strftime") else str(r[0])
            if f == fecha_str:
                filtrados.append(r)
        return filtrados

    def establecer_f1(self, fecha_str):
        self.fecha_1 = fecha_str
        # Si la Fecha 2 ya no es comparable con la nueva Fecha 1, la borramos
        if self.fecha_2 and self.fecha_2 not in self.dias_comparables():
            self.limpiar_fecha_2()
        self.pintar_calendario()
        self.actualizar_texto_comparables()
        dia_rutina = self.texto_dia_rutina(fecha_str)
        self.lbl_titulo_f1.configure(text=f"Fecha 1: {formato_fecha(fecha_str)}" + (f" ({dia_rutina})" if dia_rutina else ""))
        self.txt_card_f1.delete("1.0", "end")
        regs = self.obtener_registros_de_fecha(fecha_str)
        if not regs:
            self.txt_card_f1.insert("end", "Sin registros guardados en esta fecha.")
            return
        for r in regs:
            self.txt_card_f1.insert("end", f"• {r[1]} | Serie {r[2]}: {r[3]}kg x {r[4]} reps\n")

    def establecer_f2(self, fecha_str):
        self.fecha_2 = fecha_str
        self.pintar_calendario()
        dia_rutina = self.texto_dia_rutina(fecha_str)
        self.lbl_titulo_f2.configure(text=f"Fecha 2: {formato_fecha(fecha_str)}" + (f" ({dia_rutina})" if dia_rutina else ""))
        self.txt_card_f2.delete("1.0", "end")
        regs = self.obtener_registros_de_fecha(fecha_str)
        if not regs:
            self.txt_card_f2.insert("end", "Sin registros guardados en esta fecha.")
            return
        for r in regs:
            self.txt_card_f2.insert("end", f"• {r[1]} | Serie {r[2]}: {r[3]}kg x {r[4]} reps\n")

    def comparar_fechas(self):
        self.txt_resultado_comparativa.delete("1.0", "end")
        if not self.fecha_1 or not self.fecha_2:
            self.txt_resultado_comparativa.insert("end", "⚠ Debes seleccionar Fecha 1 y Fecha 2 para comparar.")
            return

        # Ordenamos las fechas solas: la comparativa siempre va de la más vieja a la más nueva
        fecha_vieja = self.fecha_1
        fecha_nueva = self.fecha_2
        if fecha_vieja > fecha_nueva:
            fecha_vieja, fecha_nueva = fecha_nueva, fecha_vieja

        regs_1 = self.obtener_registros_de_fecha(fecha_vieja)
        regs_2 = self.obtener_registros_de_fecha(fecha_nueva)

        if not regs_1 and not regs_2:
            self.txt_resultado_comparativa.insert("end", "Ninguna de las dos fechas tiene registros guardados.")
            return

        volumen_1 = sum(float(r[3]) * int(r[4]) for r in regs_1)
        volumen_2 = sum(float(r[3]) * int(r[4]) for r in regs_2)
        # Total de repeticiones (sirve también para los ejercicios con peso corporal, que no suman volumen)
        reps_1 = sum(int(r[4]) for r in regs_1)
        reps_2 = sum(int(r[4]) for r in regs_2)

        self.txt_resultado_comparativa.insert("end", f"=== COMPARATIVA: {formato_fecha(fecha_vieja)} ➔ {formato_fecha(fecha_nueva)} ===\n\n")
        self.txt_resultado_comparativa.insert("end", f"• Volumen Total Levantado (kg × reps):\n")
        self.txt_resultado_comparativa.insert("end", f"   Fecha 1: {volumen_1:.1f} kg | Fecha 2: {volumen_2:.1f} kg\n")

        dif_vol = volumen_2 - volumen_1
        signo = "+" if dif_vol >= 0 else ""
        self.txt_resultado_comparativa.insert("end", f"   Diferencia de volumen: {signo}{dif_vol:.1f} kg\n")
        self.txt_resultado_comparativa.insert("end", f"• Repeticiones totales:\n   Fecha 1: {reps_1} | Fecha 2: {reps_2} ({reps_2 - reps_1:+d})\n\n")

        ej_1 = {}
        for r in regs_1:
            ej_1.setdefault(r[1], []).append((float(r[3]), int(r[4])))
        ej_2 = {}
        for r in regs_2:
            ej_2.setdefault(r[1], []).append((float(r[3]), int(r[4])))

        comunes = set(ej_1.keys()).intersection(set(ej_2.keys()))
        if comunes:
            self.txt_resultado_comparativa.insert("end", "• Ejercicios realizados en ambas fechas (mejor serie):\n")
            for nombre_ej in sorted(comunes):
                # Comparamos la mejor serie de cada fecha: primero por peso y, si es igual, por repeticiones
                peso_1, rep_1 = self.mejor_serie(ej_1[nombre_ej])
                peso_2, rep_2 = self.mejor_serie(ej_2[nombre_ej])
                if peso_2 > peso_1:
                    prog = f"↗ Progreso +{peso_2 - peso_1:.1f}kg"
                elif peso_2 < peso_1:
                    prog = f"↘ Menor carga {peso_2 - peso_1:.1f}kg"
                elif rep_2 > rep_1:
                    prog = f"↗ Progreso +{rep_2 - rep_1} reps"
                elif rep_2 < rep_1:
                    prog = f"↘ {rep_2 - rep_1} reps"
                else:
                    prog = "= Igual"
                self.txt_resultado_comparativa.insert("end", f"   - {nombre_ej}: {self.texto_peso(peso_1)} x {rep_1} ➔ {self.texto_peso(peso_2)} x {rep_2} ({prog})\n")
        else:
            self.txt_resultado_comparativa.insert("end", "• No se repitieron los mismos ejercicios entre estas dos fechas.\n")

    def mejor_serie(self, series):
        """Devuelve la mejor serie (peso, repeticiones): la de mayor peso y, si hay empate, la de más repeticiones."""
        mejor_peso, mejor_reps = series[0]
        for peso, reps in series:
            if peso > mejor_peso or (peso == mejor_peso and reps > mejor_reps):
                mejor_peso, mejor_reps = peso, reps
        return mejor_peso, mejor_reps

    def texto_peso(self, peso):
        """Muestra el peso de una serie. Si es 0 kg es un ejercicio con peso corporal."""
        if peso == 0:
            return "peso corporal"
        return f"{peso}kg"

    def pedir_analisis_ia(self):
        if not self.fn_analizar_ia:
            self.txt_ia.insert("end", "\n⚠ La función de Inteligencia Artificial no está configurada.\n")
            return

        registros = self.fn_obtener_seguimiento(self.dni_usuario)
        if not registros:
            self.txt_ia.insert("end", "\n⚠ Necesitas tener al menos una serie registrada para que la IA pueda analizar tu progreso.\n")
            return

        # Mientras la IA responde: bloqueamos el botón (para que no se toque dos veces),
        # cambiamos su texto y ponemos el cursor de espera, así el usuario sabe que está trabajando
        self.btn_ia.configure(state="disabled", text="⏳ Analizando... (unos segundos)")
        self.app.configure(cursor="watch")
        self.txt_ia.delete("1.0", "end")
        self.txt_ia.insert("end", "⏳ Analizando tu rendimiento con la IA de Gemini...\nEsto suele tardar menos de 10 segundos (puede tardar más si los servidores de Google están saturados). La ventana va a quedar quieta mientras tanto, no la cierres.\n\n")
        self.update()

        informe_ia = self.fn_analizar_ia(registros, self.nombre_usuario)

        # Volvemos el botón y el cursor a la normalidad
        self.btn_ia.configure(state="normal", text="Analizar Rendimiento")
        self.app.configure(cursor="")

        self.txt_ia.delete("1.0", "end")
        # Si la IA devolvió un error (empieza con [!]) lo mostramos sin el título del informe
        if informe_ia.startswith("[!]"):
            self.txt_ia.insert("end", informe_ia)
            return
        self.txt_ia.insert("end", "=== ANÁLISIS DE RENDIMIENTO GENERADO POR IA ===\n\n")
        self.txt_ia.insert("end", informe_ia)


class VentanaInformacionPersonal(ctk.CTkFrame):
    def __init__(self, parent, usuario_actual, fn_actualizar_usuario, fn_callback_actualizar=None):
        app = parent.winfo_toplevel()
        super().__init__(app, fg_color="transparent")
        self.app = app
        self.usuario_actual = usuario_actual
        self.fn_actualizar_usuario = fn_actualizar_usuario
        # Guardamos el callback para avisarle a la ventana principal cuando se guarden cambios
        self.fn_callback_actualizar = fn_callback_actualizar

        # Encabezado: botón '◀ Volver' a la izquierda y el título de la sección
        crear_encabezado(self, "Mi Perfil", self.app.volver_pantalla, tamaño_letra=18)
        # usuario_actual es un objeto Usuario, por eso usamos sus atributos
        ctk.CTkLabel(self, text=f"DNI (No editable): {usuario_actual.dni}", font=("Arial", 12)).pack(pady=2)

        # Mostramos el IMC calculado con el método de la clase Usuario
        self.lbl_imc = ctk.CTkLabel(self, text=f"IMC actual: {usuario_actual.calcular_imc()}", font=("Arial", 12, "bold"), text_color=amarillo)
        self.lbl_imc.pack(pady=2)

        self.ent_nom = ctk.CTkEntry(self, width=250)
        self.ent_nom.insert(0, usuario_actual.nombre)
        self.ent_nom.pack(pady=5)

        self.ent_ape = ctk.CTkEntry(self, width=250)
        self.ent_ape.insert(0, usuario_actual.apellido)
        self.ent_ape.pack(pady=5)

        self.ent_peso = ctk.CTkEntry(self, width=250)
        self.ent_peso.insert(0, str(usuario_actual.peso))
        self.ent_peso.pack(pady=5)

        self.ent_alt = ctk.CTkEntry(self, width=250)
        self.ent_alt.insert(0, str(usuario_actual.altura))
        self.ent_alt.pack(pady=5)

        frame_sexo = ctk.CTkFrame(self, fg_color="transparent")
        frame_sexo.pack(pady=5)
        ctk.CTkLabel(frame_sexo, text="Sexo:").pack(side="left", padx=5)
        
        sexo_texto = "Masculino" if usuario_actual.sexo == "M" else ("Femenino" if usuario_actual.sexo == "F" else "Otros")
        self.combo_sexo = ctk.CTkOptionMenu(frame_sexo, values=["Masculino", "Femenino", "Otros"], width=160)
        self.combo_sexo.set(sexo_texto)
        self.combo_sexo.pack(side="left", padx=5)

        self.lbl_msg = ctk.CTkLabel(self, text="", text_color="yellow")
        self.lbl_msg.pack(pady=2)

        ctk.CTkButton(self, text="Guardar Cambios", command=self.guardar_cambios, fg_color=verde, hover_color=verde_hover, width=250).pack(pady=10)

        # Mostramos esta pantalla dentro de la ventana principal
        self.app.abrir_pantalla(self)

    def guardar_cambios(self):
        dni = self.usuario_actual.dni
        nom = self.ent_nom.get().strip().title()
        ape = self.ent_ape.get().strip().title()
        try:
            peso = float(self.ent_peso.get().strip())
            alt = float(self.ent_alt.get().strip())
            mapa_sexo = {"Masculino": "M", "Femenino": "F", "Otros": "Otros"}
            sexo = mapa_sexo.get(self.combo_sexo.get(), "Otros")

            if self.fn_actualizar_usuario(dni, nom, ape, peso, alt, sexo):
                self.lbl_msg.configure(text="✔ Cambios guardados con éxito.", text_color="#2ECC71")
                # Creamos un nuevo objeto Usuario con los datos actualizados
                self.usuario_actual = Usuario(dni, nom, ape, peso, alt, sexo)
                # Actualizamos el IMC mostrado con los nuevos datos
                self.lbl_imc.configure(text=f"IMC actual: {self.usuario_actual.calcular_imc()}")
                # Avisamos a la ventana principal para que actualice sus datos del usuario
                if self.fn_callback_actualizar:
                    self.fn_callback_actualizar(self.usuario_actual)
            else:
                self.lbl_msg.configure(text="❌ Error al actualizar.", text_color="#C0392B")
        except ValueError:
            self.lbl_msg.configure(text="⚠ Peso y altura deben ser números.", text_color="#E67E22")


class App(ctk.CTk):
    def __init__(self, fn_login, fn_registro, fn_actualizar_usuario=None, fn_registrar_accion=None):
        super().__init__()
        self.title("NO PY, NO GAIN")
        self.geometry("420x680")
        self.resizable(False, False)

        self.fn_login = fn_login
        self.fn_registro = fn_registro
        self.fn_actualizar_usuario = fn_actualizar_usuario
        self.fn_registrar_accion = fn_registrar_accion
        self.usuario_actual = None

        # Lista de pantallas abiertas dentro de la ventana (la última es la que se ve).
        # Así navegamos por la interfaz sin abrir ventanas nuevas.
        self.pantallas = []

        # Buscamos la imagen del logo en la carpeta del proyecto
        dir_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_logo = os.path.join(dir_actual, "nopy-nogain.png")

        # Si la imagen existe la mostramos como logo con un tamaño más destacado
        if os.path.exists(ruta_logo):
            img_pil = Image.open(ruta_logo)
            self.logo_app = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(165, 165))
            self.label_titulo = ctk.CTkLabel(self, image=self.logo_app, text="")
            self.pady_logo = (15, 0)
        else:
            self.label_titulo = ctk.CTkLabel(self, text="NO PY, NO GAIN", font=("Arial", 26, "bold"))
            self.pady_logo = 20
        # Guardamos el espacio del logo para volver a mostrarlo igual al regresar al menú
        self.label_titulo.pack(pady=self.pady_logo)

        # Contenedor transparente para el slogan de bienvenida
        self.frame_slogan = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_slogan.pack(pady=(4, 10))

        ctk.CTkLabel(
            self.frame_slogan, 
            text="Lleva tu entrenamiento al ", 
            text_color=azul_claro, 
            font=("Arial", 15, "bold")
        ).pack(side="left", padx=(5, 0), pady=2)

        ctk.CTkLabel(
            self.frame_slogan, 
            text="siguiente nivel", 
            text_color=amarillo, 
            font=("Arial", 15, "bold")
        ).pack(side="left", padx=(0, 5), pady=2)

        self.frame_login = ctk.CTkFrame(self)
        self.frame_login.pack(pady=10, padx=20, fill="both")

        ctk.CTkLabel(self.frame_login, text="Ingresar con Documento", font=("Arial", 16, "bold")).pack(pady=10)
        self.ent_dni = ctk.CTkEntry(self.frame_login, placeholder_text="Número de DNI", width=250)
        self.ent_dni.pack(pady=5)

        ctk.CTkButton(self.frame_login, text="INGRESAR", command=self.ingresar_usuario, width=250, text_color="#FFFFFF"
                      , fg_color=verde, hover_color=verde_hover).pack(pady=8)
        ctk.CTkButton(
            self.frame_login, text="¿No estás registrado? Regístrate aquí", command=self.abrir_formulario_registro, 
            width=250, fg_color="transparent", border_width=1, text_color="#EEFF00"
        ).pack(pady=8)

        ctk.CTkButton(
            self.frame_login, text="Cerrar No py, no gain", command=self.cerrar_aplicacion, width=250, height=35,
            font=("Arial", 12, "bold"), fg_color=rojo, hover_color=rojo_hover
        ).pack(pady=(5, 10))

        self.lbl_estado = ctk.CTkLabel(self, text="", text_color="yellow")
        self.lbl_estado.pack(pady=5)

    def cerrar_aplicacion(self):
        """Cierra la aplicación sin registrar eventos en el archivo de texto."""
        self.destroy()

    def mostrar_mensaje(self, titulo, mensaje, color_boton="#27AE60"):
        """Muestra un aviso como texto debajo del login."""
        self.lbl_estado.configure(text=f"{titulo}\n{mensaje}", text_color=color_boton, font=("Arial", 13, "bold"), wraplength=360)

    def abrir_pantalla(self, pantalla):
        """Muestra una pantalla dentro de la misma ventana, ocultando lo que se veía antes."""
        if self.pantallas:
            # Si ya había una pantalla abierta la ocultamos (queda guardada para poder volver)
            self.pantallas[-1].pack_forget()
        else:
            # Si venimos del login o del menú, ocultamos el logo y esos contenedores
            self.label_titulo.pack_forget()
            self.frame_slogan.pack_forget()
            self.frame_login.pack_forget()
            self.lbl_estado.pack_forget()
            if hasattr(self, 'frame_bienvenida') and self.frame_bienvenida:
                self.frame_bienvenida.pack_forget()
            if hasattr(self, 'frame_menu') and self.frame_menu:
                self.frame_menu.pack_forget()
        # Agregamos la pantalla nueva a la lista y la mostramos
        self.pantallas.append(pantalla)
        pantalla.pack(fill="both", expand=True, padx=5, pady=5)

    def volver_pantalla(self):
        """Cierra la pantalla actual y vuelve a la anterior (otra pantalla, el menú o el login)."""
        if self.pantallas:
            pantalla = self.pantallas.pop()
            pantalla.destroy()

        if self.pantallas:
            # Volvemos a mostrar la pantalla anterior
            self.pantallas[-1].pack(fill="both", expand=True, padx=5, pady=5)
        elif self.usuario_actual:
            # Si hay sesión iniciada volvemos al menú principal (con los datos actualizados)
            self.label_titulo.pack(pady=self.pady_logo)
            self.habilitar_menu()
        else:
            # Si no hay sesión volvemos al login
            self.label_titulo.pack(pady=self.pady_logo)
            self.frame_slogan.pack(pady=(4, 10))
            self.frame_login.pack(pady=10, padx=20, fill="both")
            self.lbl_estado.pack(pady=5)

    def ingresar_usuario(self):
        # Limpiamos puntos y espacios por si el usuario escribió el DNI con formato (ej: 30.300.333)
        dni = self.ent_dni.get().strip().replace(".", "").replace(" ", "")
        if not dni:
            self.mostrar_mensaje("Atención", "Por favor, ingrese un número de DNI.", color_boton="#E67E22")
            return
        u = self.fn_login(dni)
        if u:
            self.usuario_actual = u
            if self.fn_registrar_accion:
                self.fn_registrar_accion("INICIÓ SESIÓN", u.dni, u.nombre_completo())
            self.habilitar_menu()
        else:
            self.mostrar_mensaje("Usuario no encontrado", f"El DNI {dni} no está registrado.", color_boton="#C0392B")

    def abrir_formulario_registro(self):
        dni_inicial = self.ent_dni.get().strip()
        # Abrimos la pantalla de registro dentro de la misma ventana
        top = ctk.CTkFrame(self, fg_color="transparent")

        # Mostramos el mismo logo que en la pantalla principal (si la imagen existe).
        # Usamos 10 de espacio arriba porque la pantalla ya tiene 5 propios (5 + 10 = 15, igual que el logo principal)
        if hasattr(self, 'logo_app'):
            ctk.CTkLabel(top, image=self.logo_app, text="").pack(pady=(10, 0))

        ctk.CTkLabel(top, text="Regístrate", font=("Arial", 16, "bold")).pack(pady=10)
        ent_dni = ctk.CTkEntry(top, placeholder_text="Documento (DNI)", width=250)
        if dni_inicial: ent_dni.insert(0, dni_inicial)
        ent_dni.pack(pady=5)

        ent_nom = ctk.CTkEntry(top, placeholder_text="Nombre", width=250)
        ent_nom.pack(pady=5)
        ent_ape = ctk.CTkEntry(top, placeholder_text="Apellido", width=250)
        ent_ape.pack(pady=5)
        ent_peso = ctk.CTkEntry(top, placeholder_text="Peso en kg", width=250)
        ent_peso.pack(pady=5)
        ent_alt = ctk.CTkEntry(top, placeholder_text="Altura en metros", width=250)
        ent_alt.pack(pady=5)
        
        frame_sexo = ctk.CTkFrame(top, fg_color="transparent")
        frame_sexo.pack(pady=5)
        ctk.CTkLabel(frame_sexo, text="Sexo:").pack(side="left", padx=5)
        combo_sexo = ctk.CTkOptionMenu(frame_sexo, values=["Masculino", "Femenino", "Otros"], width=180)
        combo_sexo.pack(side="left", padx=5)

        lbl_msg = ctk.CTkLabel(top, text="", text_color="#E74C3C", font=("Arial", 11))
        lbl_msg.pack(pady=2)

        def guardar():
            # Limpiamos puntos y espacios por si el usuario escribió el DNI con formato (ej: 30.300.333)
            d_val = ent_dni.get().strip().replace(".", "").replace(" ", "")
            nom = ent_nom.get().strip().title()
            ape = ent_ape.get().strip().title()
            p_val = ent_peso.get().strip()
            a_val = ent_alt.get().strip()

            # Validamos que el DNI tenga solo números y entre 7 y 8 dígitos (formato argentino)
            if not d_val.isdigit() or not (7 <= len(d_val) <= 8):
                lbl_msg.configure(text="⚠ El DNI debe tener entre 7 y 8 dígitos numéricos.")
                return

            if not d_val or not nom or not ape or not p_val or not a_val:
                lbl_msg.configure(text="⚠ Faltan campos por completar.")
                return
            if self.fn_login(d_val):
                lbl_msg.configure(text="⚠ Este DNI ya está registrado.")
                return

            try:
                mapa_sexo = {"Masculino": "M", "Femenino": "F", "Otros": "Otros"}
                if self.fn_registro(d_val, nom, ape, float(p_val), float(a_val), mapa_sexo.get(combo_sexo.get(), "Otros")):
                    if self.fn_registrar_accion:
                        self.fn_registrar_accion("USUARIO NUEVO", d_val, f"{nom} {ape}")
                    # Cerramos la pantalla de registro y volvemos al login
                    self.volver_pantalla()
                    self.mostrar_mensaje("¡Éxito!", "Usuario registrado con éxito.", color_boton="#27AE60")
                    self.ent_dni.delete(0, "end")
                    self.ent_dni.insert(0, d_val)
            except ValueError:
                lbl_msg.configure(text="⚠ Peso y altura numéricos.")

        ctk.CTkButton(top, text="Guardar Registro", command=guardar, width=250, fg_color=verde, hover_color=verde_hover).pack(pady=10)
        ctk.CTkButton(top, text="Cerrar Registro", command=self.volver_pantalla, width=200, fg_color=rojo, hover_color=rojo_hover).pack(pady=5)

        # Mostramos la pantalla de registro en lugar del login
        self.abrir_pantalla(top)

    def habilitar_menu(self):
        # Ocultamos la caja de login, el slogan inicial y la etiqueta de estado previa
        self.frame_login.pack_forget()
        self.frame_slogan.pack_forget()
        self.lbl_estado.pack_forget()

        # Si ya existía un cartel de bienvenida anterior lo destruimos
        if hasattr(self, 'frame_bienvenida') and self.frame_bienvenida:
            self.frame_bienvenida.destroy()

        # Contenedor para la bienvenida colocado inmediatamente después del logo
        self.frame_bienvenida = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_bienvenida.pack(after=self.label_titulo, pady=(2, 4))

        ctk.CTkLabel(
            self.frame_bienvenida, 
            text="Bienvenido/a ", 
            text_color=azul_claro, 
            font=("Arial", 15, "bold")
        ).pack(side="left", padx=(5, 0), pady=1)

        # Verificamos que haya un usuario activo antes de acceder a sus datos
        if not self.usuario_actual:
            return
        nombre_completo = self.usuario_actual.nombre_completo()
        ctk.CTkLabel(
            self.frame_bienvenida, 
            text=nombre_completo, 
            text_color=amarillo, 
            font=("Arial", 15, "bold")
        ).pack(side="left", padx=(0, 5), pady=1)

        if hasattr(self, 'frame_menu') and self.frame_menu:
            self.frame_menu.destroy()

        # Subimos el contenedor del menú para que quede más cerca de la bienvenida
        self.frame_menu = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_menu.pack(after=self.frame_bienvenida, pady=(2, 5))

        ctk.CTkButton(
            self.frame_menu, text="Gestionar Rutina", command=self.abrir_gestionar_rutina_cmd, 
            width=280, height=45, font=("Arial", 13, "bold"), fg_color=azul, hover_color=azul_hover
        ).pack(pady=5)

        ctk.CTkButton(
            self.frame_menu, text="Empezar Rutina", command=self.abrir_realizar_rutina_cmd, 
            width=280, height=45, font=("Arial", 13, "bold"), fg_color=azul, hover_color=azul_hover
        ).pack(pady=5)

        ctk.CTkButton(
            self.frame_menu, text="Ver Seguimiento", command=self.abrir_ver_seguimiento_cmd, 
            width=280, height=45, font=("Arial", 13, "bold"), fg_color=azul, hover_color=azul_hover
        ).pack(pady=5)

        ctk.CTkButton(
            self.frame_menu, text="Mi Perfil", command=self.abrir_informacion_personal_cmd,
            width=280, height=45, font=("Arial", 13, "bold"), fg_color=naranja, hover_color=naranja_hover, text_color="black"
        ).pack(pady=5)

        ctk.CTkButton(
            self.frame_menu, text="Cerrar Sesión", command=self.cerrar_sesion, 
            width=280, height=45, font=("Arial", 13, "bold"), fg_color=rojo, hover_color=rojo_hover
        ).pack(pady=5)

    def cerrar_sesion(self):
        if self.fn_registrar_accion and self.usuario_actual:
            self.fn_registrar_accion("CERRÓ SESIÓN", self.usuario_actual.dni, self.usuario_actual.nombre_completo())
        self.usuario_actual = None
        if hasattr(self, 'frame_menu') and self.frame_menu:
            self.frame_menu.destroy()
            self.frame_menu = None
        if hasattr(self, 'frame_bienvenida') and self.frame_bienvenida:
            self.frame_bienvenida.destroy()
            self.frame_bienvenida = None
        self.ent_dni.delete(0, "end")
        # Volvemos a mostrar el slogan y la caja de login anclados tras el logo
        self.frame_slogan.pack(after=self.label_titulo, pady=(4, 10))
        self.frame_login.pack(after=self.frame_slogan, pady=10, padx=20, fill="both")
        # Volvemos a mostrar la etiqueta de avisos (vacía) debajo del login
        self.lbl_estado.configure(text="")
        self.lbl_estado.pack(after=self.frame_login, pady=5)

    def abrir_gestionar_rutina_cmd(self): pass
    def abrir_realizar_rutina_cmd(self): pass
    def abrir_ver_seguimiento_cmd(self): pass
    def abrir_informacion_personal_cmd(self): pass