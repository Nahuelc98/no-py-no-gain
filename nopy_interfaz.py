"""
Módulo de Interfaz Gráfica (CustomTkinter) para 'No py, no gain'
Diseñado e implementado según el diagrama de flujo oficial del proyecto.
"""

import customtkinter as ctk
from datetime import date

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

GRUPOS_MUSCULARES = ["Piernas", "Pecho", "Espalda", "Hombros", "Brazos", "Abdomen"]
TIPOS_EJERCICIO = ["Libre", "Máquina"]


class VentanaGestionarRutinas(ctk.CTkToplevel):
    def __init__(self, parent, dni_usuario, fn_obtener_ejercicios, fn_agregar_ejercicio, fn_guardar_rutina, fn_obtener_rutinas, fn_eliminar_rutina):
        super().__init__(parent)
        self.title("Gestionar Rutinas - No py, no gain")
        self.geometry("600x850")
        self.after(100, self.lift)

        self.dni_usuario = dni_usuario
        self.fn_obtener_ejercicios = fn_obtener_ejercicios
        self.fn_agregar_ejercicio = fn_agregar_ejercicio
        self.fn_guardar_rutina = fn_guardar_rutina
        self.fn_obtener_rutinas = fn_obtener_rutinas
        self.fn_eliminar_rutina = fn_eliminar_rutina

        self.dias_rutina = []
        self.dia_actual_num = 1
        self.total_dias = 1

        ctk.CTkLabel(self, text="Gestionar Rutinas", font=("Arial", 20, "bold")).pack(pady=10)

        # SECCIÓN: CREAR RUTINA
        ctk.CTkLabel(self, text="Crear Rutina", font=("Arial", 14, "bold")).pack(pady=(5, 0))

        self.ent_nombre_rutina = ctk.CTkEntry(self, placeholder_text="Nombre de rutina (ej: PPL)", width=420)
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

        # 1. CREAR PRIMERO EL MENÚ DE EJERCICIOS PARA EVITAR NULOS EN MEMORIA
        frame_ej = ctk.CTkFrame(self, fg_color="transparent")
        frame_ej.pack(pady=5)
        ctk.CTkLabel(frame_ej, text="Ejercicio:").pack(side="left", padx=5)
        self.combo_ejercicios = ctk.CTkOptionMenu(frame_ej, values=["Cargando..."], width=230)
        self.combo_ejercicios.pack(side="left", padx=5)
        ctk.CTkButton(frame_ej, text="+", command=self.abrir_crear_ejercicio, width=40, fg_color="#8E44AD").pack(side="left", padx=5)

        # 2. LUEGO CREAR EL GRUPO MUSCULAR (ARRIBA)
        frame_grupo = ctk.CTkFrame(self, fg_color="transparent")
        frame_grupo.pack(before=frame_ej, pady=5)
        ctk.CTkLabel(frame_grupo, text="Grupo Muscular:").pack(side="left", padx=5)
        self.combo_grupo_dia = ctk.CTkOptionMenu(frame_grupo, values=["Todos"] + GRUPOS_MUSCULARES, command=self.actualizar_ejercicios_disponibles, width=250)
        self.combo_grupo_dia.set("Todos")
        self.combo_grupo_dia.pack(side="left", padx=5)

        # Cantidad de series (ABAJO de ejercicio)
        frame_series = ctk.CTkFrame(self, fg_color="transparent")
        frame_series.pack(pady=5)
        ctk.CTkLabel(frame_series, text="Cantidad de series:").pack(side="left", padx=5)
        self.ent_series = ctk.CTkEntry(frame_series, placeholder_text="ej: 3", width=120)
        self.ent_series.pack(side="left", padx=5)

        ctk.CTkButton(self, text="Agregar Ejercicio al Día Actual", command=self.agregar_ejercicio_a_dia, width=420, fg_color="#2980B9").pack(pady=8)

        self.txt_resumen = ctk.CTkTextbox(self, width=520, height=120)
        self.txt_resumen.pack(pady=5)

        ctk.CTkButton(self, text="✔ Guardar Rutina Completa", command=self.guardar_todo, width=420, fg_color="#27AE60", hover_color="#2ECC71").pack(pady=8)

        # SECCIÓN: VER TUS RUTINAS
        ctk.CTkLabel(self, text="Ver tus rutinas", font=("Arial", 14, "bold")).pack(pady=(10, 0))
        self.txt_tus_rutinas = ctk.CTkTextbox(self, width=520, height=100)
        self.txt_tus_rutinas.pack(pady=5)

        frame_eliminar = ctk.CTkFrame(self, fg_color="transparent")
        frame_eliminar.pack(pady=5)
        self.ent_id_eliminar = ctk.CTkEntry(frame_eliminar, placeholder_text="ID de rutina", width=120)
        self.ent_id_eliminar.pack(side="left", padx=5)
        ctk.CTkButton(frame_eliminar, text="Eliminar Rutina", command=self.eliminar_rutina, fg_color="#C0392B", width=120).pack(side="left", padx=5)

        self.cambiar_cantidad_dias("3")
        self.actualizar_ejercicios_disponibles("Todos")
        self.cargar_lista_rutinas()

    def abrir_crear_ejercicio(self):
        VentanaCrearEjercicioModal(self, self.fn_agregar_ejercicio, lambda: self.actualizar_ejercicios_disponibles(self.combo_grupo_dia.get()))

    def cambiar_cantidad_dias(self, valor):
        self.total_dias = int(valor)
        opciones_dias = [f"Día {i}" for i in range(1, self.total_dias + 1)]
        self.combo_dia_activo.configure(values=opciones_dias)
        self.combo_dia_activo.set(opciones_dias[0])
        self.dia_actual_num = 1
        self.dias_rutina.clear()
        self.txt_resumen.delete("1.0", "end")

    def seleccionar_dia_activo(self, seleccion):
        if "Día" in seleccion:
            self.dia_actual_num = int(seleccion.replace("Día", "").strip())

    def actualizar_ejercicios_disponibles(self, grupo):
        ejercicios = self.fn_obtener_ejercicios(grupo)
        nombres = [f"{ej[0]} - {ej[1]} ({ej[2]})" for ej in ejercicios] if ejercicios else ["Sin Ejercicios"]
        if hasattr(self, 'combo_ejercicios'):
            self.combo_ejercicios.configure(values=nombres)
            if nombres:
                self.combo_ejercicios.set(nombres[0])

    def agregar_ejercicio_a_dia(self):
        seleccion = self.combo_ejercicios.get()
        series_str = self.ent_series.get().strip()
        if not series_str.isdigit():
            self.txt_resumen.insert("end", "⚠ Ingrese cantidad de series válida.\n")
            return
        if " - " in seleccion:
            id_ej = int(seleccion.split(" - ")[0])
            resto = seleccion.split(" - ")[1]
            nom_ej = resto.split(" (")[0]
            grupo_ej = resto.split(" (")[1].replace(")", "")
            series = int(series_str)
            
            dia_obj = next((d for d in self.dias_rutina if d['numero_dia'] == self.dia_actual_num), None)
            if not dia_obj:
                dia_obj = {'numero_dia': self.dia_actual_num, 'grupo': grupo_ej, 'ejercicios': []}
                self.dias_rutina.append(dia_obj)
            
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
        if nom_rutina and self.dias_rutina:
            exito = self.fn_guardar_rutina(self.dni_usuario, nom_rutina, self.dias_rutina)
            if exito:
                self.txt_resumen.insert("end", f"\n✔ ¡Rutina '{nom_rutina}' guardada con éxito!\n")
                self.cargar_lista_rutinas()
        else:
            self.txt_resumen.insert("end", "\n❌ Falta nombre o configurar al menos un día con ejercicios.\n")

    def cargar_lista_rutinas(self):
        self.txt_tus_rutinas.delete("1.0", "end")
        rutinas = self.fn_obtener_rutinas(self.dni_usuario)
        if not rutinas:
            self.txt_tus_rutinas.insert("end", "No tienes rutinas creadas.")
            return
        for r in rutinas:
            self.txt_tus_rutinas.insert("end", f"ID: {r[0]} | Nombre: {r[1]} ({r[2]} días)\n")

    def eliminar_rutina(self):
        id_str = self.ent_id_eliminar.get().strip()
        if id_str.isdigit():
            if self.fn_eliminar_rutina(int(id_str)):
                self.txt_tus_rutinas.insert("end", f"\n✔ Rutina ID {id_str} eliminada.\n")
                self.cargar_lista_rutinas()


class VentanaCrearEjercicioModal(ctk.CTkToplevel):
    def __init__(self, parent, fn_agregar_ejercicio, fn_callback_actualizar):
        super().__init__(parent)
        self.title("Crear Nuevo Ejercicio")
        self.geometry("350x380")
        self.after(100, self.lift)
        self.fn_agregar_ejercicio = fn_agregar_ejercicio
        self.fn_callback_actualizar = fn_callback_actualizar

        ctk.CTkLabel(self, text="Nuevo Ejercicio", font=("Arial", 16, "bold")).pack(pady=10)
        self.ent_nom = ctk.CTkEntry(self, placeholder_text="Nombre ejercicio", width=250)
        self.ent_nom.pack(pady=5)
        self.combo_g = ctk.CTkOptionMenu(self, values=GRUPOS_MUSCULARES, width=250)
        self.combo_g.pack(pady=5)
        self.combo_t = ctk.CTkOptionMenu(self, values=TIPOS_EJERCICIO, width=250)
        self.combo_t.pack(pady=5)
        self.ent_desc = ctk.CTkEntry(self, placeholder_text="Descripción (Opcional)", width=250)
        self.ent_desc.pack(pady=5)

        def guardar():
            if self.ent_nom.get().strip():
                self.fn_agregar_ejercicio(self.ent_nom.get().strip(), self.combo_g.get(), self.combo_t.get(), self.ent_desc.get().strip())
                self.fn_callback_actualizar()
                self.destroy()

        ctk.CTkButton(self, text="Guardar Ejercicio", command=guardar, fg_color="#27AE60", width=250).pack(pady=15)


class VentanaMenuRealizarRutina(ctk.CTkToplevel):
    def __init__(self, parent, dni_usuario, fn_obtener_rutinas, fn_obtener_dias, fn_registrar_serie, fn_obtener_seguimiento):
        super().__init__(parent)
        self.title("Realizar Rutina - No py, no gain")
        self.geometry("400x350")
        self.after(100, self.lift)

        self.dni_usuario = dni_usuario
        self.fn_obtener_rutinas = fn_obtener_rutinas
        self.fn_obtener_dias = fn_obtener_dias
        self.fn_registrar_serie = fn_registrar_serie
        self.fn_obtener_seguimiento = fn_obtener_seguimiento

        ctk.CTkLabel(self, text="Entrenamiento y Seguimiento", font=("Arial", 18, "bold")).pack(pady=20)

        ctk.CTkButton(
            self, text="Comenzar a Entrenar", command=self.abrir_entrenar, width=280, height=45, font=("Arial", 14, "bold"), fg_color="#2980B9"
        ).pack(pady=10)

        ctk.CTkButton(
            self, text="Ver Seguimiento (Semanas)", command=self.abrir_seguimiento, width=280, height=45, font=("Arial", 14, "bold"), fg_color="#2980B9"
        ).pack(pady=10)

    def abrir_entrenar(self):
        VentanaComenzarEntrenar(self, self.dni_usuario, self.fn_obtener_rutinas, self.fn_obtener_dias, self.fn_registrar_serie)

    def abrir_seguimiento(self):
        VentanaVerSeguimiento(self, self.dni_usuario, self.fn_obtener_rutinas, self.fn_obtener_seguimiento)


class VentanaComenzarEntrenar(ctk.CTkToplevel):
    def __init__(self, parent, dni_usuario, fn_obtener_rutinas, fn_obtener_dias, fn_registrar_serie):
        super().__init__(parent)
        self.title("Comenzar a Entrenar")
        self.geometry("520x620")
        self.after(100, self.lift)

        self.dni_usuario = dni_usuario
        self.fn_obtener_rutinas = fn_obtener_rutinas
        self.fn_obtener_dias = fn_obtener_dias
        self.fn_registrar_serie = fn_registrar_serie

        ctk.CTkLabel(self, text="Sesión Activa de Entrenamiento", font=("Arial", 20, "bold")).pack(pady=10)

        rutinas = self.fn_obtener_rutinas(self.dni_usuario)
        lista_rutinas = [f"{r[0]} - {r[1]}" for r in rutinas] if rutinas else ["Sin Rutinas"]

        ctk.CTkLabel(self, text="Seleccionar Rutina:", font=("Arial", 12)).pack(pady=(5, 0))
        self.combo_rutinas = ctk.CTkOptionMenu(self, values=lista_rutinas, command=self.cargar_dias_rutina, width=320)
        self.combo_rutinas.pack(pady=5)

        ctk.CTkLabel(self, text="Seleccionar Día:", font=("Arial", 12)).pack(pady=(5, 0))
        self.combo_dias = ctk.CTkOptionMenu(self, values=["Seleccione rutina primero"], width=320)
        self.combo_dias.pack(pady=5)

        ctk.CTkLabel(self, text="Registrar Serie (Peso y Reps)", font=("Arial", 14, "bold")).pack(pady=10)
        self.ent_id_ejercicio = ctk.CTkEntry(self, placeholder_text="ID de Ejercicio", width=320)
        self.ent_id_ejercicio.pack(pady=3)
        self.ent_serie_num = ctk.CTkEntry(self, placeholder_text="Número de serie (ej: 1)", width=320)
        self.ent_serie_num.pack(pady=3)
        self.ent_peso = ctk.CTkEntry(self, placeholder_text="Peso en kg (ej: 80)", width=320)
        self.ent_peso.pack(pady=3)
        self.ent_reps = ctk.CTkEntry(self, placeholder_text="Repeticiones (ej: 12)", width=320)
        self.ent_reps.pack(pady=3)

        ctk.CTkButton(self, text="Guardar Serie en BD", command=self.guardar_serie, width=320, fg_color="#27AE60").pack(pady=10)

        self.txt_salida = ctk.CTkTextbox(self, width=460, height=120)
        self.txt_salida.pack(pady=5)

        if lista_rutinas and lista_rutinas[0] != "Sin Rutinas":
            self.cargar_dias_rutina(lista_rutinas[0])

    def cargar_dias_rutina(self, seleccion_rutina):
        if " - " in seleccion_rutina:
            id_rutina = int(seleccion_rutina.split(" - ")[0])
            dias = self.fn_obtener_dias(id_rutina)
            opciones = [f"{d[0]} - Día {d[1]} ({d[2]})" for d in dias] if dias else ["Sin Días"]
            self.combo_dias.configure(values=opciones)
            if opciones:
                self.combo_dias.set(opciones[0])

    def guardar_serie(self):
        try:
            id_ej = int(self.ent_id_ejercicio.get().strip())
            s_num = int(self.ent_serie_num.get().strip())
            peso = float(self.ent_peso.get().strip())
            reps = int(self.ent_reps.get().strip())
            hoy = date.today()

            exito = self.fn_registrar_serie(self.dni_usuario, id_ej, hoy, 1, s_num, peso, reps)
            if exito:
                self.txt_salida.insert("end", f"✔ Serie {s_num} guardada: {peso}kg x {reps} reps\n")
            else:
                self.txt_salida.insert("end", "❌ Error al guardar serie.\n")
        except ValueError:
            self.txt_salida.insert("end", "⚠ Verifique que los campos numéricos sean correctos.\n")


class VentanaVerSeguimiento(ctk.CTkToplevel):
    def __init__(self, parent, dni_usuario, fn_obtener_rutinas, fn_obtener_seguimiento):
        super().__init__(parent)
        self.title("Seguimiento por Semana")
        self.geometry("500x480")
        self.after(100, self.lift)
        self.dni_usuario = dni_usuario
        self.fn_obtener_rutinas = fn_obtener_rutinas
        self.fn_obtener_seguimiento = fn_obtener_seguimiento

        ctk.CTkLabel(self, text="Historial de Registros", font=("Arial", 18, "bold")).pack(pady=10)

        rutinas = self.fn_obtener_rutinas(self.dni_usuario)
        lista_rutinas = [f"{r[0]} - {r[1]}" for r in rutinas] if rutinas else ["Sin Rutinas"]

        self.combo_rutinas = ctk.CTkOptionMenu(self, values=lista_rutinas, command=self.cargar_seguimiento, width=320)
        self.combo_rutinas.pack(pady=5)

        self.txt_seguimiento = ctk.CTkTextbox(self, width=440, height=280)
        self.txt_seguimiento.pack(pady=10)

        if lista_rutinas and lista_rutinas[0] != "Sin Rutinas":
            self.cargar_seguimiento(lista_rutinas[0])

    def cargar_seguimiento(self, seleccion):
        self.txt_seguimiento.delete("1.0", "end")
        if " - " in seleccion:
            registros = self.fn_obtener_seguimiento(self.dni_usuario)
            if not registros:
                self.txt_seguimiento.insert("end", "No hay registros de entrenamiento aún.")
                return
            for reg in registros:
                self.txt_seguimiento.insert("end", f"[{reg[0]}] {reg[1]} - Serie {reg[2]}: {reg[3]}kg x {reg[4]} reps\n")


class VentanaInformacionPersonal(ctk.CTkToplevel):
    def __init__(self, parent, usuario_actual, fn_actualizar_usuario):
        super().__init__(parent)
        self.title("Información Personal")
        self.geometry("380x480")
        self.after(100, self.lift)
        self.usuario_actual = usuario_actual
        self.fn_actualizar_usuario = fn_actualizar_usuario

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

        ctk.CTkButton(self, text="Guardar Cambios", command=self.guardar_cambios, fg_color="#27AE60", width=250).pack(pady=15)

    def guardar_cambios(self):
        dni = self.usuario_actual[0]
        nom = self.ent_nom.get().strip()
        ape = self.ent_ape.get().strip()
        try:
            peso = float(self.ent_peso.get().strip())
            alt = float(self.ent_alt.get().strip())
            mapa_sexo = {"Masculino": "M", "Femenino": "F", "Otros": "Otro"}
            sexo = mapa_sexo.get(self.combo_sexo.get(), "Otros")

            if self.fn_actualizar_usuario(dni, nom, ape, peso, alt, sexo):
                self.lbl_msg.configure(text="✔ Cambios guardados con éxito.", text_color="#2ECC71")
                self.usuario_actual = (dni, nom, ape, peso, alt, sexo)
            else:
                self.lbl_msg.configure(text="❌ Error al actualizar.", text_color="#C0392B")
        except ValueError:
            self.lbl_msg.configure(text="⚠ Peso y altura deben ser números.", text_color="#E67E22")


class App(ctk.CTk):
    def __init__(self, fn_login, fn_registro, fn_actualizar_usuario=None):
        super().__init__()
        self.title("No py, no gain - Menú Principal")
        self.geometry("400x520")

        self.fn_login = fn_login
        self.fn_registro = fn_registro
        self.fn_actualizar_usuario = fn_actualizar_usuario
        self.usuario_actual = None

        self.label_titulo = ctk.CTkLabel(self, text="NO PY, NO GAIN", font=("Arial", 26, "bold"))
        self.label_titulo.pack(pady=20)

        self.frame_login = ctk.CTkFrame(self)
        self.frame_login.pack(pady=10, padx=20, fill="both")

        ctk.CTkLabel(self.frame_login, text="Ingresar con Documento", font=("Arial", 14, "bold")).pack(pady=10)
        self.ent_dni = ctk.CTkEntry(self.frame_login, placeholder_text="Número de DNI", width=250)
        self.ent_dni.pack(pady=5)

        ctk.CTkButton(self.frame_login, text="Ingresar", command=self.ingresar_usuario, width=250).pack(pady=8)
        ctk.CTkButton(
            self.frame_login, text="¿No estás registrado? Regístrate aquí", command=self.abrir_formulario_registro, 
            width=250, fg_color="transparent", border_width=1, text_color="#2ECC71"
        ).pack(pady=8)

        ctk.CTkButton(
            self.frame_login, text="Cerrar No py, no gain", command=self.destroy, width=250, height=35,
            font=("Arial", 12, "bold"), fg_color="#C0392B", hover_color="#E74C3C"
        ).pack(pady=(5, 10))

        self.lbl_estado = ctk.CTkLabel(self, text="", text_color="yellow")
        self.lbl_estado.pack(pady=5)

    def mostrar_mensaje(self, titulo, mensaje, color_boton="#27AE60"):
        popup = ctk.CTkToplevel(self)
        popup.title(titulo)
        popup.geometry("320x160")
        popup.after(100, popup.lift)
        ctk.CTkLabel(popup, text=mensaje, font=("Arial", 13, "bold"), wraplength=280).pack(pady=25)
        ctk.CTkButton(popup, text="Aceptar", command=popup.destroy, width=120, fg_color=color_boton).pack(pady=5)

    def ingresar_usuario(self):
        dni = self.ent_dni.get().strip()
        if not dni:
            self.mostrar_mensaje("Atención", "Por favor, ingrese un número de DNI.", color_boton="#E67E22")
            return
        u = self.fn_login(dni)
        if u:
            self.usuario_actual = u
            self.habilitar_menu()
        else:
            self.mostrar_mensaje("Usuario no encontrado", f"El DNI {dni} no está registrado.", color_boton="#C0392B")

    def abrir_formulario_registro(self):
        dni_inicial = self.ent_dni.get().strip()
        top = ctk.CTkToplevel(self)
        top.title("Registrate a No py, no gain")
        top.geometry("350x520")
        top.after(100, top.lift)

        ctk.CTkLabel(top, text="Registro de Nuevo Usuario", font=("Arial", 15, "bold")).pack(pady=10)
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
            d_val = ent_dni.get().strip()
            nom = ent_nom.get().strip()
            ape = ent_ape.get().strip()
            p_val = ent_peso.get().strip()
            a_val = ent_alt.get().strip()
            
            if not d_val or not nom or not ape or not p_val or not a_val:
                lbl_msg.configure(text="⚠ Faltan campos por completar.")
                return
            if self.fn_login(d_val):
                lbl_msg.configure(text="⚠ Este DNI ya está registrado.")
                return

            try:
                mapa_sexo = {"Masculino": "M", "Femenino": "F", "Otros": "Otros"}
                if self.fn_registro(d_val, nom, ape, float(p_val), float(a_val), mapa_sexo.get(combo_sexo.get(), "Otros")):
                    top.destroy()
                    self.mostrar_mensaje("¡Éxito!", "Usuario registrado con éxito.", color_boton="#27AE60")
                    self.ent_dni.delete(0, "end")
                    self.ent_dni.insert(0, d_val)
            except ValueError:
                lbl_msg.configure(text="⚠ Peso y altura numéricos.")

        ctk.CTkButton(top, text="Guardar Registro", command=guardar, width=250, fg_color="#27AE60").pack(pady=10)

    def habilitar_menu(self):
        self.frame_login.pack_forget()
        self.lbl_estado.configure(text=f"Bienvenido/a {self.usuario_actual[1]} {self.usuario_actual[2]}", text_color="#2ECC71")

        if hasattr(self, 'frame_menu') and self.frame_menu:
            self.frame_menu.destroy()

        self.frame_menu = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_menu.pack(pady=10)

        ctk.CTkButton(
            self.frame_menu, text="Gestionar Rutina", command=self.abrir_gestionar_rutina_cmd, 
            width=280, height=45, font=("Arial", 13, "bold"), fg_color="#2980B9"
        ).pack(pady=8)

        ctk.CTkButton(
            self.frame_menu, text="Realizar Rutina", command=self.abrir_realizar_rutina_cmd, 
            width=280, height=45, font=("Arial", 13, "bold"), fg_color="#2980B9"
        ).pack(pady=8)

        ctk.CTkButton(
            self.frame_menu, text="Información Personal", command=self.abrir_informacion_personal_cmd, 
            width=280, height=45, font=("Arial", 13, "bold"), fg_color="#F39C12", hover_color="#F1C40F", text_color="black"
        ).pack(pady=8)

        ctk.CTkButton(
            self.frame_menu, text="Cerrar Sesión", command=self.cerrar_sesion, 
            width=280, height=45, font=("Arial", 13, "bold"), fg_color="#C0392B", hover_color="#E74C3C"
        ).pack(pady=8)

    def cerrar_sesion(self):
        self.usuario_actual = None
        if hasattr(self, 'frame_menu') and self.frame_menu:
            self.frame_menu.destroy()
        self.lbl_estado.configure(text="")
        self.ent_dni.delete(0, "end")
        self.frame_login.pack(pady=10, padx=20, fill="both")

    def abrir_gestionar_rutina_cmd(self): pass
    def abrir_realizar_rutina_cmd(self): pass
    def abrir_informacion_personal_cmd(self): pass