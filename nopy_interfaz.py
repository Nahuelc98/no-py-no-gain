"""
Módulo de Interfaz Gráfica (CustomTkinter) para 'No py, no gain'
Diseñado e implementado según el diagrama de flujo oficial del proyecto.
"""

import os
import customtkinter as ctk
from datetime import date
from PIL import Image

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

GRUPOS_MUSCULARES = ["Piernas", "Pecho", "Espalda", "Hombros", "Bíceps", "Tríceps", "Abdomen"]
TIPOS_EJERCICIO = ["Libre", "Máquina"]

# Colores característicos de la imagen del logo (adaptados para modo oscuro)
COLOR_AZUL_NOPY = "#4B8BBE"
COLOR_AMARILLO_NOPY = "#EFBA1C"

# Colores de botones de la interfaz
COLOR_VERDE_BOTON = "#2BA535"       # Botones de acción positiva (guardar, ingresar, registrar)
COLOR_VERDE_HOVER = "#3DC94A"       # Hover del verde (un poco más claro)
COLOR_ROJO_BOTON = "#C0392B"        # Botones de acción negativa (eliminar, cerrar sesión)
COLOR_ROJO_HOVER = "#E74C3C"        # Hover del rojo (un poco más claro)
COLOR_AZUL_BOTON = "#2980B9"        # Botones de navegación (comenzar entrenar, ver seguimiento)
COLOR_AZUL_HOVER = "#3FA3D8"        # Hover del azul (un poco más claro)
COLOR_NARANJA_BOTON = "#F39C12"     # Botones de edición
COLOR_NARANJA_HOVER = "#F5B942"     # Hover del naranja (un poco más claro)
COLOR_GRIS_BOTON = "#555555"        # Botones secundarios (cerrar ventana, cancelar)
COLOR_GRIS_HOVER = "#777777"        # Hover del gris (un poco más claro)


class VentanaGestionarRutinas(ctk.CTkToplevel):
    def __init__(self, parent, dni_usuario, fn_obtener_ejercicios, fn_agregar_ejercicio, fn_guardar_rutina, fn_obtener_rutinas, fn_eliminar_rutina, fn_obtener_detalle=None, fn_actualizar_rutina=None):
        super().__init__(parent)
        self.title("Gestionar Rutinas - No py, no gain")
        self.geometry("600x880")
        self.after(100, self.lift)

        self.dni_usuario = dni_usuario
        self.fn_obtener_ejercicios = fn_obtener_ejercicios
        self.fn_agregar_ejercicio = fn_agregar_ejercicio
        self.fn_guardar_rutina = fn_guardar_rutina
        self.fn_obtener_rutinas = fn_obtener_rutinas
        self.fn_eliminar_rutina = fn_eliminar_rutina
        self.fn_obtener_detalle = fn_obtener_detalle
        self.fn_actualizar_rutina = fn_actualizar_rutina

        # Variables para controlar la rutina y si estamos editando una existente
        self.id_rutina_editando = None
        self.dias_rutina = []
        self.dia_actual_num = 1
        self.total_dias = 1

        ctk.CTkLabel(self, text="Gestionar Rutinas", font=("Arial", 20, "bold")).pack(pady=10)

        # SECCIÓN: CREAR O EDITAR RUTINA
        self.lbl_modo = ctk.CTkLabel(self, text="Crear Rutina", font=("Arial", 14, "bold"), text_color="#2ECC71")
        self.lbl_modo.pack(pady=(5, 0))

        self.ent_nombre_rutina = ctk.CTkEntry(self, placeholder_text="Nombre de rutina (ej: Push, Pull, Leg (PPL))", width=420)
        self.ent_nombre_rutina.pack(pady=5)

        # Cantidad de días (1 al 7)
        frame_dias = ctk.CTkFrame(self, fg_color="transparent")
        frame_dias.pack(pady=5)
        ctk.CTkLabel(frame_dias, text="Cantidad de días:").pack(side="left", padx=5)
        self.combo_cantidad_dias = ctk.CTkOptionMenu(frame_dias, values=["1", "2", "3", "4", "5", "6", "7"], command=self.cambiar_cantidad_dias, width=100)
        self.combo_cantidad_dias.set("3")
        self.combo_cantidad_dias.pack(side="left", padx=5)

        # Selector de Día Activo dinámico
        frame_selector_dia = ctk.CTkFrame(self, fg_color="transparent")
        frame_selector_dia.pack(pady=5)
        ctk.CTkLabel(frame_selector_dia, text="Configurando:").pack(side="left", padx=5)
        self.combo_dia_activo = ctk.CTkOptionMenu(frame_selector_dia, values=["Día 1"], command=self.seleccionar_dia_activo, width=120)
        self.combo_dia_activo.pack(side="left", padx=5)

        # Menú de ejercicios
        frame_ej = ctk.CTkFrame(self, fg_color="transparent")
        frame_ej.pack(pady=5)
        ctk.CTkLabel(frame_ej, text="Ejercicio:").pack(side="left", padx=5)
        self.combo_ejercicios = ctk.CTkOptionMenu(frame_ej, values=["Cargando..."], width=230)
        self.combo_ejercicios.pack(side="left", padx=5)
        ctk.CTkButton(frame_ej, text="+", command=self.abrir_crear_ejercicio, width=40, fg_color=COLOR_AZUL_BOTON, hover_color=COLOR_AZUL_HOVER).pack(side="left", padx=5)

        # Filtro de Grupo Muscular
        frame_grupo = ctk.CTkFrame(self, fg_color="transparent")
        frame_grupo.pack(before=frame_ej, pady=5)
        ctk.CTkLabel(frame_grupo, text="Grupo Muscular:").pack(side="left", padx=5)
        self.combo_grupo_dia = ctk.CTkOptionMenu(frame_grupo, values=["Todos"] + GRUPOS_MUSCULARES, command=self.actualizar_ejercicios_disponibles, width=250)
        self.combo_grupo_dia.set("Todos")
        self.combo_grupo_dia.pack(side="left", padx=5)

        # Cantidad de series por ejercicio
        frame_series = ctk.CTkFrame(self, fg_color="transparent")
        frame_series.pack(pady=5)
        ctk.CTkLabel(frame_series, text="Cantidad de series:").pack(side="left", padx=5)
        self.ent_series = ctk.CTkEntry(frame_series, placeholder_text="ej: 3", width=120)
        self.ent_series.pack(side="left", padx=5)

        ctk.CTkButton(self, text="Agregar Ejercicio al Día Actual", command=self.agregar_ejercicio_a_dia, width=420, fg_color=COLOR_AZUL_BOTON, hover_color=COLOR_AZUL_HOVER).pack(pady=8)

        self.txt_resumen = ctk.CTkTextbox(self, width=520, height=120)
        self.txt_resumen.pack(pady=5)

        # Botón para guardar (sirve tanto para crear como para editar)
        self.btn_guardar_rutina = ctk.CTkButton(self, text="✔ Guardar Rutina Completa", command=self.guardar_todo, width=420, fg_color=COLOR_VERDE_BOTON, hover_color=COLOR_VERDE_HOVER)
        self.btn_guardar_rutina.pack(pady=6)

        # Botón para cancelar edición si el usuario estaba editando
        self.btn_cancelar_edicion = ctk.CTkButton(self, text="Cancelar Edición (Volver a Crear)", command=self.limpiar_modo_edicion, width=420, fg_color=COLOR_GRIS_BOTON, hover_color=COLOR_GRIS_HOVER)

        # SECCIÓN: VER TUS RUTINAS
        ctk.CTkLabel(self, text="Ver tus rutinas", font=("Arial", 14, "bold")).pack(pady=(10, 0))
        self.txt_tus_rutinas = ctk.CTkTextbox(self, width=520, height=100)
        self.txt_tus_rutinas.pack(pady=5)

        # Acciones sobre rutinas existentes: Editar o Eliminar
        frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        frame_acciones.pack(pady=5)
        self.ent_id_rutina_accion = ctk.CTkEntry(frame_acciones, placeholder_text="ID de rutina", width=120)
        self.ent_id_rutina_accion.pack(side="left", padx=5)

        ctk.CTkButton(frame_acciones, text="Editar Rutina", command=self.cargar_para_editar, fg_color=COLOR_NARANJA_BOTON, hover_color=COLOR_NARANJA_HOVER, text_color="black", width=120).pack(side="left", padx=5)
        ctk.CTkButton(frame_acciones, text="Eliminar Rutina", command=self.eliminar_rutina, fg_color=COLOR_ROJO_BOTON, hover_color=COLOR_ROJO_HOVER, width=120).pack(side="left", padx=5)

        # Botón para cerrar la ventana como indica el diagrama
        ctk.CTkButton(self, text="Cerrar ventana", command=self.destroy, fg_color=COLOR_GRIS_BOTON, hover_color=COLOR_GRIS_HOVER, width=200).pack(pady=(5, 10))

        self.cambiar_cantidad_dias("3")
        self.actualizar_ejercicios_disponibles("Todos")
        self.cargar_lista_rutinas()

    def abrir_crear_ejercicio(self):
        VentanaCrearEjercicioModal(self, self.dni_usuario, self.fn_agregar_ejercicio, lambda: self.actualizar_ejercicios_disponibles(self.combo_grupo_dia.get()))

    def cambiar_cantidad_dias(self, valor):
        self.total_dias = int(valor)
        opciones_dias = [f"Día {i}" for i in range(1, self.total_dias + 1)]
        self.combo_dia_activo.configure(values=opciones_dias)
        self.combo_dia_activo.set(opciones_dias[0])
        self.dia_actual_num = 1
        # Si no estamos editando, limpiamos la lista
        if not self.id_rutina_editando:
            self.dias_rutina.clear()
            self.txt_resumen.delete("1.0", "end")

    def seleccionar_dia_activo(self, seleccion):
        if "Día" in seleccion:
            self.dia_actual_num = int(seleccion.replace("Día", "").strip())

    def actualizar_ejercicios_disponibles(self, grupo):
        ejercicios = self.fn_obtener_ejercicios(grupo, self.dni_usuario)
        nombres = [f"{ej[0]} - {ej[1]} ({ej[2]})" for ej in ejercicios] if ejercicios else ["Sin Ejercicios"]
        if hasattr(self, 'combo_ejercicios'):
            self.combo_ejercicios.configure(values=nombres)
            if nombres:
                self.combo_ejercicios.set(nombres[0])

    def agregar_ejercicio_a_dia(self):
        seleccion = self.combo_ejercicios.get()
        series_str = self.ent_series.get().strip()
        if not series_str.isdigit():
            self.txt_resumen.insert("end", "⚠ Ingrese una cantidad de series válida (número entero).\n")
            return
        if " - " in seleccion:
            id_ej = int(seleccion.split(" - ")[0])
            resto = seleccion.split(" - ")[1]
            nom_ej = resto.split(" (")[0]
            grupo_ej = resto.split(" (")[1].replace(")", "")
            series = int(series_str)
            
            # Buscamos si el día ya existe en la lista de configuración
            dia_obj = next((d for d in self.dias_rutina if d['numero_dia'] == self.dia_actual_num), None)
            if not dia_obj:
                dia_obj = {'numero_dia': self.dia_actual_num, 'grupo': grupo_ej, 'ejercicios': []}
                self.dias_rutina.append(dia_obj)
            
            # Agregamos el ejercicio a ese día
            dia_obj['ejercicios'].append({'id': id_ej, 'series': series, 'nombre': nom_ej, 'grupo': grupo_ej})
            
            self.actualizar_texto_resumen()
            self.ent_series.delete(0, "end")

    def actualizar_texto_resumen(self):
        self.txt_resumen.delete("1.0", "end")
        for dia in sorted(self.dias_rutina, key=lambda x: x['numero_dia']):
            self.txt_resumen.insert("end", f"Día {dia['numero_dia']}:\n")
            for ej in dia['ejercicios']:
                self.txt_resumen.insert("end", f"  • {ej['nombre']} | {ej['series']} Series | {ej['grupo']}\n")

    def guardar_todo(self):
        nom_rutina = self.ent_nombre_rutina.get().strip()
        if not nom_rutina or not self.dias_rutina:
            self.txt_resumen.insert("end", "\n❌ Falta poner un nombre o agregar ejercicios a los días.\n")
            return

        # Si estamos editando una rutina existente:
        if self.id_rutina_editando and self.fn_actualizar_rutina:
            exito = self.fn_actualizar_rutina(self.id_rutina_editando, nom_rutina, self.dias_rutina)
            if exito:
                self.txt_resumen.insert("end", f"\n✔ ¡Rutina '{nom_rutina}' (ID: {self.id_rutina_editando}) actualizada con éxito!\n")
                self.limpiar_modo_edicion()
                self.cargar_lista_rutinas()
        else:
            # Si estamos creando una rutina nueva:
            exito = self.fn_guardar_rutina(self.dni_usuario, nom_rutina, self.dias_rutina)
            if exito:
                self.txt_resumen.insert("end", f"\n✔ ¡Rutina '{nom_rutina}' creada y guardada con éxito!\n")
                self.limpiar_modo_edicion()
                self.cargar_lista_rutinas()

    def cargar_para_editar(self):
        """Carga los datos de una rutina existente para poder editarla."""
        id_str = self.ent_id_rutina_accion.get().strip()
        if not id_str.isdigit():
            self.txt_resumen.insert("end", "⚠ Ingrese un ID de rutina válido para editar.\n")
            return

        id_rutina = int(id_str)
        if not self.fn_obtener_detalle:
            self.txt_resumen.insert("end", "⚠ La función de edición no está disponible.\n")
            return

        detalle = self.fn_obtener_detalle(id_rutina)
        if not detalle:
            self.txt_resumen.insert("end", f"❌ No se encontró la rutina con ID {id_rutina}.\n")
            return

        # Cargamos los datos en los controles de la interfaz
        self.id_rutina_editando = id_rutina
        self.lbl_modo.configure(text=f"Editando Rutina (ID: {id_rutina})", text_color="#F39C12")
        self.ent_nombre_rutina.delete(0, "end")
        self.ent_nombre_rutina.insert(0, detalle['nombre_rutina'])
        
        cant_dias = str(detalle['cantidad_dias'])
        self.combo_cantidad_dias.set(cant_dias)
        self.cambiar_cantidad_dias(cant_dias)

        self.dias_rutina = detalle['dias']
        self.actualizar_texto_resumen()

        self.btn_guardar_rutina.configure(text="✔ Guardar Cambios en Rutina", fg_color=COLOR_NARANJA_BOTON, hover_color=COLOR_NARANJA_HOVER)
        self.btn_cancelar_edicion.pack(pady=4)

    def limpiar_modo_edicion(self):
        """Vuelve la ventana al modo normal de creación de rutina."""
        self.id_rutina_editando = None
        self.lbl_modo.configure(text="Crear Rutina", text_color="#2ECC71")
        self.ent_nombre_rutina.delete(0, "end")
        self.dias_rutina.clear()
        self.txt_resumen.delete("1.0", "end")
        self.btn_guardar_rutina.configure(text="✔ Guardar Rutina Completa", fg_color=COLOR_VERDE_BOTON, hover_color=COLOR_VERDE_HOVER)
        self.btn_cancelar_edicion.pack_forget()

    def cargar_lista_rutinas(self):
        self.txt_tus_rutinas.delete("1.0", "end")
        rutinas = self.fn_obtener_rutinas(self.dni_usuario)
        if not rutinas:
            self.txt_tus_rutinas.insert("end", "No tienes rutinas creadas.")
            return
        for r in rutinas:
            self.txt_tus_rutinas.insert("end", f"ID: {r[0]} | Nombre: {r[1]} ({r[2]} días)\n")

    def eliminar_rutina(self):
        id_str = self.ent_id_rutina_accion.get().strip()
        if id_str.isdigit():
            if self.fn_eliminar_rutina(int(id_str)):
                self.txt_tus_rutinas.insert("end", f"\n✔ Rutina ID {id_str} eliminada.\n")
                if self.id_rutina_editando == int(id_str):
                    self.limpiar_modo_edicion()
                self.cargar_lista_rutinas()


class VentanaCrearEjercicioModal(ctk.CTkToplevel):
    def __init__(self, parent, dni_usuario, fn_agregar_ejercicio, fn_callback_actualizar):
        super().__init__(parent)
        self.title("Crear Nuevo Ejercicio")
        self.geometry("350x320")
        self.after(100, self.lift)
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
                self.destroy()

        ctk.CTkButton(self, text="Guardar Ejercicio", command=guardar, fg_color=COLOR_VERDE_BOTON, hover_color=COLOR_VERDE_HOVER, width=250).pack(pady=15)


class VentanaMenuRealizarRutina(ctk.CTkToplevel):
    def __init__(self, parent, dni_usuario, fn_obtener_rutinas, fn_obtener_dias, fn_registrar_serie, fn_obtener_seguimiento, fn_obtener_ejercicios_dia=None, fn_analizar_ia=None, nombre_usuario="Atleta"):
        super().__init__(parent)
        self.title("Empezar Rutina - No py, no gain")
        self.geometry("400x380")
        self.after(100, self.lift)

        self.dni_usuario = dni_usuario
        self.fn_obtener_rutinas = fn_obtener_rutinas
        self.fn_obtener_dias = fn_obtener_dias
        self.fn_registrar_serie = fn_registrar_serie
        self.fn_obtener_seguimiento = fn_obtener_seguimiento
        self.fn_obtener_ejercicios_dia = fn_obtener_ejercicios_dia
        self.fn_analizar_ia = fn_analizar_ia
        self.nombre_usuario = nombre_usuario

        ctk.CTkLabel(self, text="Empezar Rutina", font=("Arial", 20, "bold")).pack(pady=20)

        # Botón para comenzar a entrenar (cargar series de hoy)
        ctk.CTkButton(
            self, text="Comenzar a Entrenar", command=self.abrir_entrenar, width=280, height=45, font=("Arial", 14, "bold"), fg_color=COLOR_AZUL_BOTON, hover_color=COLOR_AZUL_HOVER
        ).pack(pady=10)

        # Botón para ver el historial y análisis con IA
        ctk.CTkButton(
            self, text="Ver Seguimiento", command=self.abrir_seguimiento, width=280, height=45, font=("Arial", 14, "bold"), fg_color=COLOR_AZUL_BOTON, hover_color=COLOR_AZUL_HOVER
        ).pack(pady=10)

        # Botón para cerrar la ventana como indica el diagrama
        ctk.CTkButton(self, text="Cerrar ventana", command=self.destroy, fg_color=COLOR_GRIS_BOTON, hover_color=COLOR_GRIS_HOVER, width=200).pack(pady=20)

    def abrir_entrenar(self):
        VentanaComenzarEntrenar(self, self.dni_usuario, self.fn_obtener_rutinas, self.fn_obtener_dias, self.fn_registrar_serie, self.fn_obtener_ejercicios_dia)

    def abrir_seguimiento(self):
        VentanaVerSeguimiento(self, self.dni_usuario, self.fn_obtener_rutinas, self.fn_obtener_seguimiento, self.fn_analizar_ia, self.nombre_usuario)


class VentanaComenzarEntrenar(ctk.CTkToplevel):
    def __init__(self, parent, dni_usuario, fn_obtener_rutinas, fn_obtener_dias, fn_registrar_serie, fn_obtener_ejercicios_dia=None):
        super().__init__(parent)
        self.title("Comenzar a Entrenar")
        self.geometry("540x680")
        self.after(100, self.lift)

        self.dni_usuario = dni_usuario
        self.fn_obtener_rutinas = fn_obtener_rutinas
        self.fn_obtener_dias = fn_obtener_dias
        self.fn_registrar_serie = fn_registrar_serie
        self.fn_obtener_ejercicios_dia = fn_obtener_ejercicios_dia

        ctk.CTkLabel(self, text="Sesión de Entrenamiento", font=("Arial", 20, "bold")).pack(pady=10)

        # 1. SELECCIONAR RUTINA
        rutinas = self.fn_obtener_rutinas(self.dni_usuario)
        lista_rutinas = [f"{r[0]} - {r[1]}" for r in rutinas] if rutinas else ["Sin Rutinas"]

        ctk.CTkLabel(self, text="1. Seleccionar Rutina:", font=("Arial", 12, "bold")).pack(pady=(5, 0))
        self.combo_rutinas = ctk.CTkOptionMenu(self, values=lista_rutinas, command=self.cargar_dias_rutina, width=350)
        self.combo_rutinas.pack(pady=5)

        # 2. SELECCIONAR DÍA DE LA RUTINA
        ctk.CTkLabel(self, text="2. Seleccionar Día de la Rutina:", font=("Arial", 12, "bold")).pack(pady=(5, 0))
        self.combo_dias = ctk.CTkOptionMenu(self, values=["Seleccione rutina primero"], command=self.cargar_ejercicios_del_dia, width=350)
        self.combo_dias.pack(pady=5)

        # 3. SELECCIONAR EJERCICIO DEL DÍA
        ctk.CTkLabel(self, text="3. Ejercicio asignado para hoy:", font=("Arial", 12, "bold")).pack(pady=(5, 0))
        self.combo_ejercicios_dia = ctk.CTkOptionMenu(self, values=["Seleccione día primero"], width=350)
        self.combo_ejercicios_dia.pack(pady=5)

        # 4. REGISTRAR SERIE (PESO Y REPETICIONES)
        ctk.CTkLabel(self, text="Anotar peso y repeticiones por serie:", font=("Arial", 13, "bold"), text_color="#2ECC71").pack(pady=10)
        
        self.ent_serie_num = ctk.CTkEntry(self, placeholder_text="Número de serie (ej: 1)", width=350)
        self.ent_serie_num.pack(pady=3)
        self.ent_peso = ctk.CTkEntry(self, placeholder_text="Peso en kg (ej: 80)", width=350)
        self.ent_peso.pack(pady=3)
        self.ent_reps = ctk.CTkEntry(self, placeholder_text="Repeticiones (ej: 12)", width=350)
        self.ent_reps.pack(pady=3)

        ctk.CTkButton(self, text="✔ Guardar Registro en BD", command=self.guardar_serie, width=350, fg_color=COLOR_VERDE_BOTON, hover_color=COLOR_VERDE_HOVER).pack(pady=10)

        self.txt_salida = ctk.CTkTextbox(self, width=480, height=120)
        self.txt_salida.pack(pady=5)

        # Botón para cerrar la ventana
        ctk.CTkButton(self, text="Cerrar ventana", command=self.destroy, fg_color=COLOR_GRIS_BOTON, hover_color=COLOR_GRIS_HOVER, width=200).pack(pady=(5, 10))

        if lista_rutinas and lista_rutinas[0] != "Sin Rutinas":
            self.cargar_dias_rutina(lista_rutinas[0])

    def cargar_dias_rutina(self, seleccion_rutina):
        """Carga los días que componen la rutina elegida."""
        if " - " in seleccion_rutina:
            id_rutina = int(seleccion_rutina.split(" - ")[0])
            dias = self.fn_obtener_dias(id_rutina)
            opciones = [f"{d[0]} - Día {d[1]} ({d[2]})" for d in dias] if dias else ["Sin Días"]
            self.combo_dias.configure(values=opciones)
            if opciones and opciones[0] != "Sin Días":
                self.combo_dias.set(opciones[0])
                self.cargar_ejercicios_del_dia(opciones[0])
            else:
                self.combo_ejercicios_dia.configure(values=["Sin Ejercicios"])

    def cargar_ejercicios_del_dia(self, seleccion_dia):
        """Carga los ejercicios programados para el día seleccionado."""
        if " - " in seleccion_dia and self.fn_obtener_ejercicios_dia:
            id_dia = int(seleccion_dia.split(" - ")[0])
            ejercicios = self.fn_obtener_ejercicios_dia(id_dia)
            if ejercicios:
                opciones = [f"{ej[0]} - {ej[1]} ({ej[3]} Series)" for ej in ejercicios]
                self.combo_ejercicios_dia.configure(values=opciones)
                self.combo_ejercicios_dia.set(opciones[0])
            else:
                self.combo_ejercicios_dia.configure(values=["Sin ejercicios asignados a este día"])

    def guardar_serie(self):
        """Valida y guarda la serie realizada en la base de datos."""
        seleccion_ej = self.combo_ejercicios_dia.get()
        if " - " not in seleccion_ej:
            self.txt_salida.insert("end", "⚠ Debe seleccionar un ejercicio válido.\n")
            return

        try:
            id_ej = int(seleccion_ej.split(" - ")[0])
            s_num = int(self.ent_serie_num.get().strip())
            peso = float(self.ent_peso.get().strip())
            reps = int(self.ent_reps.get().strip())
            hoy = date.today()

            exito = self.fn_registrar_serie(self.dni_usuario, id_ej, hoy, s_num, peso, reps)
            if exito:
                nom_ej = seleccion_ej.split(" - ")[1].split(" (")[0]
                self.txt_salida.insert("end", f"✔ {nom_ej} -> Serie {s_num}: {peso}kg x {reps} reps guardada.\n")
                # Limpiamos los campos y sugerimos la siguiente serie
                self.ent_serie_num.delete(0, "end")
                self.ent_serie_num.insert(0, str(s_num + 1))
            else:
                self.txt_salida.insert("end", "❌ Error al guardar la serie en la base de datos.\n")
        except ValueError:
            self.txt_salida.insert("end", "⚠ Ingrese números válidos para serie, peso y repeticiones.\n")


class VentanaVerSeguimiento(ctk.CTkToplevel):
    def __init__(self, parent, dni_usuario, fn_obtener_rutinas, fn_obtener_seguimiento, fn_analizar_ia=None, nombre_usuario="Atleta"):
        super().__init__(parent)
        self.title("Seguimiento y Análisis con IA - No py, no gain")
        self.geometry("560x650")
        self.after(100, self.lift)

        self.dni_usuario = dni_usuario
        self.fn_obtener_rutinas = fn_obtener_rutinas
        self.fn_obtener_seguimiento = fn_obtener_seguimiento
        self.fn_analizar_ia = fn_analizar_ia
        self.nombre_usuario = nombre_usuario

        ctk.CTkLabel(self, text="Seguimiento de Entrenamiento", font=("Arial", 20, "bold")).pack(pady=10)

        # 1. SELECCIONAR RUTINA (COMO EN EL DIAGRAMA)
        rutinas = self.fn_obtener_rutinas(self.dni_usuario)
        lista_rutinas = [f"{r[0]} - {r[1]}" for r in rutinas] if rutinas else ["Sin Rutinas"]

        ctk.CTkLabel(self, text="Seleccionar Rutina:", font=("Arial", 12)).pack(pady=(5, 0))
        self.combo_rutinas = ctk.CTkOptionMenu(self, values=lista_rutinas, command=self.cargar_seguimiento, width=350)
        self.combo_rutinas.pack(pady=5)

        # Botón para pedir análisis a la IA de Gemini
        self.btn_ia = ctk.CTkButton(
            self, text="✨ Analizar Rendimiento con IA (Gemini)", 
            command=self.pedir_analisis_ia, fg_color=COLOR_AZUL_BOTON, hover_color=COLOR_AZUL_HOVER, width=350, height=35, font=("Arial", 13, "bold")
        )
        self.btn_ia.pack(pady=8)

        # Cuadro de texto donde se muestra el historial o las conclusiones de la IA
        ctk.CTkLabel(self, text="Registros y Conclusiones:", font=("Arial", 12, "bold")).pack(pady=(5, 0))
        self.txt_seguimiento = ctk.CTkTextbox(self, width=500, height=340)
        self.txt_seguimiento.pack(pady=5)

        # Botón para cerrar la ventana
        ctk.CTkButton(self, text="Cerrar ventana", command=self.destroy, fg_color=COLOR_GRIS_BOTON, hover_color=COLOR_GRIS_HOVER, width=200).pack(pady=(5, 10))

        if lista_rutinas and lista_rutinas[0] != "Sin Rutinas":
            self.cargar_seguimiento(lista_rutinas[0])

    def cargar_seguimiento(self, seleccion):
        """Carga y muestra el historial de entrenamientos del usuario."""
        self.txt_seguimiento.delete("1.0", "end")
        registros = self.fn_obtener_seguimiento(self.dni_usuario)
        if not registros:
            self.txt_seguimiento.insert("end", "Aún no tienes registros de series guardadas en la base de datos.\nEntrena y anota tus series para ver tu progreso.")
            return

        self.txt_seguimiento.insert("end", "--- HISTORIAL DE ENTRENAMIENTO ---\n\n")
        for reg in registros:
            # Estructura: (fecha, nombre_ejercicio, serie_numero, peso_kg, repeticiones)
            self.txt_seguimiento.insert("end", f"• [{reg[0]}] {reg[1]} | Serie {reg[2]}: {reg[3]} kg x {reg[4]} reps\n")

    def pedir_analisis_ia(self):
        """Envía el historial de entrenamientos a la IA de Gemini y muestra el informe."""
        if not self.fn_analizar_ia:
            self.txt_seguimiento.insert("end", "\n⚠ La función de Inteligencia Artificial no está configurada.\n")
            return

        registros = self.fn_obtener_seguimiento(self.dni_usuario)
        if not registros:
            self.txt_seguimiento.insert("end", "\n⚠ Necesitas tener al menos una serie registrada para que la IA pueda analizar tu progreso.\n")
            return

        self.txt_seguimiento.delete("1.0", "end")
        self.txt_seguimiento.insert("end", "⏳ Analizando tu rendimiento con la IA de Gemini... Por favor espera unos segundos...\n\n")
        self.update()

        # Llamamos a la función de nopy_api.py
        informe_ia = self.fn_analizar_ia(registros, self.nombre_usuario)
        
        self.txt_seguimiento.delete("1.0", "end")
        self.txt_seguimiento.insert("end", "=== ANÁLISIS DE RENDIMIENTO GENERADO POR IA ===\n\n")
        self.txt_seguimiento.insert("end", informe_ia)
        self.txt_seguimiento.insert("end", "\n\n(El informe también se guardó automáticamente en tu archivo de texto local).")



class VentanaInformacionPersonal(ctk.CTkToplevel):
    def __init__(self, parent, usuario_actual, fn_actualizar_usuario, fn_callback_actualizar=None):
        super().__init__(parent)
        self.title("Información Personal")
        self.geometry("380x480")
        self.after(100, self.lift)
        self.usuario_actual = usuario_actual
        self.fn_actualizar_usuario = fn_actualizar_usuario
        # Guardamos el callback para avisarle a la ventana principal cuando se guarden cambios
        self.fn_callback_actualizar = fn_callback_actualizar

        ctk.CTkLabel(self, text="Mi Perfil", font=("Arial", 18, "bold")).pack(pady=10)
        ctk.CTkLabel(self, text=f"DNI (No editable): {usuario_actual[0]}", font=("Arial", 12)).pack(pady=2)

        self.ent_nom = ctk.CTkEntry(self, width=250)
        self.ent_nom.insert(0, usuario_actual[1])
        self.ent_nom.pack(pady=5)

        self.ent_ape = ctk.CTkEntry(self, width=250)
        self.ent_ape.insert(0, usuario_actual[2])
        self.ent_ape.pack(pady=5)

        self.ent_peso = ctk.CTkEntry(self, width=250)
        self.ent_peso.insert(0, str(usuario_actual[3]))
        self.ent_peso.pack(pady=5)

        self.ent_alt = ctk.CTkEntry(self, width=250)
        self.ent_alt.insert(0, str(usuario_actual[4]))
        self.ent_alt.pack(pady=5)

        frame_sexo = ctk.CTkFrame(self, fg_color="transparent")
        frame_sexo.pack(pady=5)
        ctk.CTkLabel(frame_sexo, text="Sexo:").pack(side="left", padx=5)
        
        sexo_texto = "Masculino" if usuario_actual[5] == "M" else ("Femenino" if usuario_actual[5] == "F" else "Otros")
        self.combo_sexo = ctk.CTkOptionMenu(frame_sexo, values=["Masculino", "Femenino", "Otros"], width=160)
        self.combo_sexo.set(sexo_texto)
        self.combo_sexo.pack(side="left", padx=5)

        self.lbl_msg = ctk.CTkLabel(self, text="", text_color="yellow")
        self.lbl_msg.pack(pady=2)

        ctk.CTkButton(self, text="Guardar Cambios", command=self.guardar_cambios, fg_color=COLOR_VERDE_BOTON, hover_color=COLOR_VERDE_HOVER, width=250).pack(pady=10)
        ctk.CTkButton(self, text="Cerrar ventana", command=self.destroy, fg_color=COLOR_GRIS_BOTON, hover_color=COLOR_GRIS_HOVER, width=200).pack(pady=5)

    def guardar_cambios(self):
        dni = self.usuario_actual[0]
        nom = self.ent_nom.get().strip().title()
        ape = self.ent_ape.get().strip().title()
        try:
            peso = float(self.ent_peso.get().strip())
            alt = float(self.ent_alt.get().strip())
            mapa_sexo = {"Masculino": "M", "Femenino": "F", "Otros": "Otro"}
            sexo = mapa_sexo.get(self.combo_sexo.get(), "Otros")

            if self.fn_actualizar_usuario(dni, nom, ape, peso, alt, sexo):
                self.lbl_msg.configure(text="✔ Cambios guardados con éxito.", text_color="#2ECC71")
                self.usuario_actual = (dni, nom, ape, peso, alt, sexo)
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
        self.title("No py, no gain - Menú Principal")
        self.geometry("420x620")

        self.fn_login = fn_login
        self.fn_registro = fn_registro
        self.fn_actualizar_usuario = fn_actualizar_usuario
        self.fn_registrar_accion = fn_registrar_accion
        self.usuario_actual = None

        # Buscamos la imagen del logo en la carpeta del proyecto
        dir_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_logo = os.path.join(dir_actual, "nopy-nogain.png")

        # Si la imagen existe la mostramos como logo con un tamaño más destacado
        if os.path.exists(ruta_logo):
            img_pil = Image.open(ruta_logo)
            self.logo_app = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(165, 165))
            self.label_titulo = ctk.CTkLabel(self, image=self.logo_app, text="")
            self.label_titulo.pack(pady=(15, 0))
        else:
            self.label_titulo = ctk.CTkLabel(self, text="NO PY, NO GAIN", font=("Arial", 26, "bold"))
            self.label_titulo.pack(pady=20)

        # Contenedor transparente para el slogan de bienvenida
        self.frame_slogan = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_slogan.pack(pady=(4, 10))

        ctk.CTkLabel(
            self.frame_slogan, 
            text="Lleva tu entrenamiento al ", 
            text_color=COLOR_AZUL_NOPY, 
            font=("Arial", 15, "bold")
        ).pack(side="left", padx=(5, 0), pady=2)

        ctk.CTkLabel(
            self.frame_slogan, 
            text="siguiente nivel", 
            text_color=COLOR_AMARILLO_NOPY, 
            font=("Arial", 15, "bold")
        ).pack(side="left", padx=(0, 5), pady=2)

        self.frame_login = ctk.CTkFrame(self)
        self.frame_login.pack(pady=10, padx=20, fill="both")

        ctk.CTkLabel(self.frame_login, text="Ingresar con Documento", font=("Arial", 16, "bold")).pack(pady=10)
        self.ent_dni = ctk.CTkEntry(self.frame_login, placeholder_text="Número de DNI", width=250)
        self.ent_dni.pack(pady=5)

        ctk.CTkButton(self.frame_login, text="INGRESAR", command=self.ingresar_usuario, width=250, text_color="#FFFFFF"
                      , fg_color=COLOR_VERDE_BOTON, hover_color=COLOR_VERDE_HOVER).pack(pady=8)
        ctk.CTkButton(
            self.frame_login, text="¿No estás registrado? Regístrate aquí", command=self.abrir_formulario_registro, 
            width=250, fg_color="transparent", border_width=1, text_color="#EEFF00"
        ).pack(pady=8)

        ctk.CTkButton(
            self.frame_login, text="Cerrar No py, no gain", command=self.cerrar_aplicacion, width=250, height=35,
            font=("Arial", 12, "bold"), fg_color=COLOR_ROJO_BOTON, hover_color=COLOR_ROJO_HOVER
        ).pack(pady=(5, 10))

        self.lbl_estado = ctk.CTkLabel(self, text="", text_color="yellow")
        self.lbl_estado.pack(pady=5)

    def cerrar_aplicacion(self):
        """Registra la salida en el archivo de texto y cierra la aplicación."""
        if self.fn_registrar_accion:
            self.fn_registrar_accion("Cierre de la Interfaz", "N/A", "Usuario")
        self.destroy()

    def mostrar_mensaje(self, titulo, mensaje, color_boton="#27AE60"):
        popup = ctk.CTkToplevel(self)
        popup.title(titulo)
        popup.geometry("320x160")
        popup.after(100, popup.lift)
        ctk.CTkLabel(popup, text=mensaje, font=("Arial", 13, "bold"), wraplength=280).pack(pady=25)
        ctk.CTkButton(popup, text="Aceptar", command=popup.destroy, width=120, fg_color=color_boton).pack(pady=5)

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
                self.fn_registrar_accion("Inicio de Sesión", u[0], f"{u[1]} {u[2]}")
            self.habilitar_menu()
        else:
            self.mostrar_mensaje("Usuario no encontrado", f"El DNI {dni} no está registrado.", color_boton="#C0392B")

    def abrir_formulario_registro(self):
        dni_inicial = self.ent_dni.get().strip()
        top = ctk.CTkToplevel(self)
        top.title("Registrate a No py, no gain")
        top.geometry("350x520")
        top.after(100, top.lift)

        ctk.CTkLabel(top, text="Registro de Nuevo Usuario", font=("Arial", 16, "bold")).pack(pady=10)
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
                        self.fn_registrar_accion("Registro de Nuevo Usuario", d_val, f"{nom} {ape}")
                    top.destroy()
                    self.mostrar_mensaje("¡Éxito!", "Usuario registrado con éxito.", color_boton="#27AE60")
                    self.ent_dni.delete(0, "end")
                    self.ent_dni.insert(0, d_val)
            except ValueError:
                lbl_msg.configure(text="⚠ Peso y altura numéricos.")

        ctk.CTkButton(top, text="Guardar Registro", command=guardar, width=250, fg_color=COLOR_VERDE_BOTON, hover_color=COLOR_VERDE_HOVER).pack(pady=10)
        ctk.CTkButton(top, text="Cerrar Registro", command=top.destroy, width=200, fg_color=COLOR_ROJO_BOTON, hover_color=COLOR_ROJO_HOVER).pack(pady=5)

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
            text_color=COLOR_AZUL_NOPY, 
            font=("Arial", 15, "bold")
        ).pack(side="left", padx=(5, 0), pady=1)

        # Verificamos que haya un usuario activo antes de acceder a sus datos
        if not self.usuario_actual:
            return
        nombre_completo = f"{self.usuario_actual[1]} {self.usuario_actual[2]}"
        ctk.CTkLabel(
            self.frame_bienvenida, 
            text=nombre_completo, 
            text_color=COLOR_AMARILLO_NOPY, 
            font=("Arial", 15, "bold")
        ).pack(side="left", padx=(0, 5), pady=1)

        if hasattr(self, 'frame_menu') and self.frame_menu:
            self.frame_menu.destroy()

        # Subimos el contenedor del menú para que quede más cerca de la bienvenida
        self.frame_menu = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_menu.pack(after=self.frame_bienvenida, pady=(2, 5))

        ctk.CTkButton(
            self.frame_menu, text="Gestionar Rutina", command=self.abrir_gestionar_rutina_cmd, 
            width=280, height=45, font=("Arial", 13, "bold"), fg_color=COLOR_AZUL_BOTON, hover_color=COLOR_AZUL_HOVER
        ).pack(pady=5)

        ctk.CTkButton(
            self.frame_menu, text="Empezar Rutina", command=self.abrir_realizar_rutina_cmd, 
            width=280, height=45, font=("Arial", 13, "bold"), fg_color=COLOR_AZUL_BOTON, hover_color=COLOR_AZUL_HOVER
        ).pack(pady=5)

        ctk.CTkButton(
            self.frame_menu, text="Información Personal", command=self.abrir_informacion_personal_cmd, 
            width=280, height=45, font=("Arial", 13, "bold"), fg_color=COLOR_NARANJA_BOTON, hover_color=COLOR_NARANJA_HOVER, text_color="black"
        ).pack(pady=5)

        ctk.CTkButton(
            self.frame_menu, text="Cerrar Sesión", command=self.cerrar_sesion, 
            width=280, height=45, font=("Arial", 13, "bold"), fg_color=COLOR_ROJO_BOTON, hover_color=COLOR_ROJO_HOVER
        ).pack(pady=5)

    def cerrar_sesion(self):
        if self.fn_registrar_accion and self.usuario_actual:
            self.fn_registrar_accion("Cierre de Sesión", self.usuario_actual[0], f"{self.usuario_actual[1]} {self.usuario_actual[2]}")
        self.usuario_actual = None
        if hasattr(self, 'frame_menu') and self.frame_menu:
            self.frame_menu.destroy()
        if hasattr(self, 'frame_bienvenida') and self.frame_bienvenida:
            self.frame_bienvenida.destroy()
        self.ent_dni.delete(0, "end")
        # Volvemos a mostrar el slogan y la caja de login anclados tras el logo
        self.frame_slogan.pack(after=self.label_titulo, pady=(4, 10))
        self.frame_login.pack(after=self.frame_slogan, pady=10, padx=20, fill="both")

    def abrir_gestionar_rutina_cmd(self): pass
    def abrir_realizar_rutina_cmd(self): pass
    def abrir_informacion_personal_cmd(self): pass