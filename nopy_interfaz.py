# Módulo de Interfaz Gráfica (CustomTkinter) para 'No py, no gain'
# Define la ventana principal y las ventanas secundarias (Toplevel) del sistema.

import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

GRUPOS_MUSCULARES = ["Piernas", "Pecho", "Espalda", "Hombros", "Brazos", "Abdomen"]


# VENTANA 1: GESTIÓN DE EJERCICIOS (CATÁLOGO):

class VentanaEjercicios(ctk.CTkToplevel):
    def __init__(self, parent, fn_obtener_ejercicios, fn_agregar_ejercicio):
        super().__init__(parent)
        self.title("Catálogo de Ejercicios - No py, no gain")
        self.geometry("500x600")
        self.after(100, self.lift)

        self.fn_obtener_ejercicios = fn_obtener_ejercicios
        self.fn_agregar_ejercicio = fn_agregar_ejercicio

        ctk.CTkLabel(self, text="Catálogo de Ejercicios", font=("Arial", 20, "bold")).pack(pady=10)

        # Filtrar por grupo muscular
        ctk.CTkLabel(self, text="Filtrar por Grupo Muscular:", font=("Arial", 12)).pack(pady=(5, 0))
        self.combo_filtro = ctk.CTkOptionMenu(
            self, values=["Todos"] + GRUPOS_MUSCULARES, command=self.filtrar_lista, width=280
        )
        self.combo_filtro.pack(pady=5)

        # Salida de la lista de ejercicios
        self.txt_lista = ctk.CTkTextbox(self, width=440, height=180)
        self.txt_lista.pack(pady=10)

        # Formulario para agregar un ejercicio nuevo
        ctk.CTkLabel(self, text="Agregar Nuevo Ejercicio", font=("Arial", 14, "bold")).pack(pady=(10, 5))
        
        self.ent_nombre = ctk.CTkEntry(self, placeholder_text="Nombre del Ejercicio", width=280)
        self.ent_nombre.pack(pady=3)

        self.combo_grupo = ctk.CTkOptionMenu(self, values=GRUPOS_MUSCULARES, width=280)
        self.combo_grupo.pack(pady=3)

        self.ent_desc = ctk.CTkEntry(self, placeholder_text="Descripción (Opcional)", width=280)
        self.ent_desc.pack(pady=3)

        self.btn_guardar = ctk.CTkButton(self, text="Guardar Ejercicio", command=self.guardar_ejercicio, width=280)
        self.btn_guardar.pack(pady=10)

        self.filtrar_lista("Todos")

    def filtrar_lista(self, grupo):
        self.txt_lista.delete("1.0", "end")
        ejercicios = self.fn_obtener_ejercicios(grupo)
        if not ejercicios:
            self.txt_lista.insert("end", "No se encontraron ejercicios.")
            return
        for ej in ejercicios:
            # ej[1]: nombre, ej[2]: grupo_muscular, ej[3]: descripcion
            self.txt_lista.insert("end", f"• {ej[1].upper()} [{ej[2]}]\n  Desc: {ej[3]}\n\n")

    def guardar_ejercicio(self):
        nom = self.ent_nombre.get().strip().capitalize()
        grupo = self.combo_grupo.get()
        desc = self.ent_desc.get().strip()

        if nom:
            self.fn_agregar_ejercicio(nom, grupo, desc)
            self.ent_nombre.delete(0, "end")
            self.ent_desc.delete(0, "end")
            self.filtrar_lista(self.combo_filtro.get())
        else:
            self.txt_lista.insert("end", "\n⚠ Error: Ingrese un nombre de ejercicio válido.\n")


# VENTANA 2: CREAR RUTINA:

class VentanaCrearRutina(ctk.CTkToplevel):
    def __init__(self, parent, dni_usuario, fn_obtener_ejercicios, fn_guardar_rutina):
        super().__init__(parent)
        self.title("Crear Rutina - No py, no gain")
        self.geometry("520x650")
        self.after(100, self.lift)

        self.dni_usuario = dni_usuario
        self.fn_obtener_ejercicios = fn_obtener_ejercicios
        self.fn_guardar_rutina = fn_guardar_rutina
        
        self.dias_rutina = []  # Lista temporal con la estructura creada

        ctk.CTkLabel(self, text="Diseñador de Rutinas", font=("Arial", 20, "bold")).pack(pady=10)

        self.ent_nombre_rutina = ctk.CTkEntry(self, placeholder_text="Nombre de la Rutina (ej: Hipertrofia 3 días)", width=320)
        self.ent_nombre_rutina.pack(pady=5)

        # Configuración por día
        ctk.CTkLabel(self, text="--- Configurar Día de la Rutina ---", font=("Arial", 14, "bold")).pack(pady=10)

        self.combo_grupo_dia = ctk.CTkOptionMenu(
            self, values=GRUPOS_MUSCULARES, command=self.actualizar_ejercicios_disponibles, width=320
        )
        self.combo_grupo_dia.pack(pady=5)

        ctk.CTkLabel(self, text="Seleccionar Ejercicio a Agregar:", font=("Arial", 12)).pack(pady=(5, 0))
        self.combo_ejercicios = ctk.CTkOptionMenu(self, values=["Cargando..."], width=320)
        self.combo_ejercicios.pack(pady=5)

        self.btn_agregar_ej = ctk.CTkButton(self, text="Agregar Ejercicio al Día Actual", command=self.agregar_ejercicio_a_dia, width=320)
        self.btn_agregar_ej.pack(pady=5)

        self.btn_siguiente_dia = ctk.CTkButton(self, text="Cerrar Día / Siguiente Día", command=self.cerrar_dia, width=320, fg_color="#D35400", hover_color="#E67E22")
        self.btn_siguiente_dia.pack(pady=5)

        self.txt_resumen = ctk.CTkTextbox(self, width=460, height=180)
        self.txt_resumen.pack(pady=10)

        self.btn_finalizar = ctk.CTkButton(self, text="✔ Guardar Rutina Completa", command=self.guardar_todo, width=320, fg_color="#27AE60", hover_color="#2ECC71")
        self.btn_finalizar.pack(pady=10)

        self.ejercicios_dia_actual = []
        self.dia_numero = 1
        self.actualizar_ejercicios_disponibles(self.combo_grupo_dia.get())

    def actualizar_ejercicios_disponibles(self, grupo):
        # Filtro estricto por grupo muscular
        self.ejercicios_db = self.fn_obtener_ejercicios(grupo)
        nombres = [f"{ej[0]} - {ej[1]}" for ej in self.ejercicios_db] if self.ejercicios_db else ["Sin Ejercicios"]
        self.combo_ejercicios.configure(values=nombres)
        if nombres:
            self.combo_ejercicios.set(nombres[0])

    def agregar_ejercicio_a_dia(self):
        seleccion = self.combo_ejercicios.get()
        if " - " in seleccion:
            id_ej = int(seleccion.split(" - ")[0])
            nom_ej = seleccion.split(" - ")[1]
            if id_ej not in self.ejercicios_dia_actual:
                self.ejercicios_dia_actual.append(id_ej)
                self.txt_resumen.insert("end", f"Día {self.dia_numero} [{self.combo_grupo_dia.get()}]: + {nom_ej}\n")

    def cerrar_dia(self):
        if self.ejercicios_dia_actual:
            self.dias_rutina.append({
                'numero_dia': self.dia_numero,
                'grupo': self.combo_grupo_dia.get(),
                'ejercicios_ids': list(self.ejercicios_dia_actual)
            })
            self.txt_resumen.insert("end", f"=== DÍA {self.dia_numero} FINALIZADO ===\n\n")
            self.dia_numero += 1
            self.ejercicios_dia_actual.clear()

    def guardar_todo(self):
        nom_rutina = self.ent_nombre_rutina.get().strip()
        if self.ejercicios_dia_actual:
            self.cerrar_dia()

        if nom_rutina and self.dias_rutina:
            self.fn_guardar_rutina(self.dni_usuario, nom_rutina, self.dias_rutina)
            self.txt_resumen.insert("end", f"\n✔ Rutina '{nom_rutina}' guardada correctamente en la Base de Datos!\n")
            self.btn_finalizar.configure(state="disabled")


# VENTANA 3: SEGUIMIENTO Y REGISTRO DE ENTRENAMIENTO:

class VentanaSeguimiento(ctk.CTkToplevel):
    def __init__(self, parent, dni_usuario, fn_obtener_rutinas, fn_obtener_dias, fn_obtener_ejercicios_dia, fn_registrar):
        super().__init__(parent)
        self.title("Seguimiento de Entrenamiento - No py, no gain")
        self.geometry("520x650")
        self.after(100, self.lift)

        self.dni_usuario = dni_usuario
        self.fn_obtener_rutinas = fn_obtener_rutinas
        self.fn_obtener_dias = fn_obtener_dias
        self.fn_obtener_ejercicios_dia = fn_obtener_ejercicios_dia
        self.fn_registrar = fn_registrar

        ctk.CTkLabel(self, text="Seguimiento de Sesión", font=("Arial", 20, "bold")).pack(pady=10)

        # Seleccionar Rutina
        rutinas = self.fn_obtener_rutinas(self.dni_usuario)
        lista_rutinas = [f"{r[0]} - {r[1]}" for r in rutinas] if rutinas else ["Sin Rutinas"]

        ctk.CTkLabel(self, text="Seleccionar Rutina:", font=("Arial", 12)).pack(pady=(5, 0))
        self.combo_rutinas = ctk.CTkOptionMenu(self, values=lista_rutinas, command=self.cargar_dias_rutina, width=320)
        self.combo_rutinas.pack(pady=5)

        ctk.CTkLabel(self, text="Seleccionar Día / Sesión:", font=("Arial", 12)).pack(pady=(5, 0))
        self.combo_dias = ctk.CTkOptionMenu(self, values=["Seleccione una rutina primero"], width=320)
        self.combo_dias.pack(pady=5)

        # Pregunta de Asistencia
        ctk.CTkLabel(self, text="¿Asistió a entrenar este día?", font=("Arial", 12, "bold")).pack(pady=(10, 0))
        self.combo_asistencia = ctk.CTkOptionMenu(self, values=["Sí", "No"], width=150)
        self.combo_asistencia.pack(pady=5)

        self.btn_cargar_ej = ctk.CTkButton(self, text="Iniciar Registro del Día", command=self.iniciar_registro, width=320)
        self.btn_cargar_ej.pack(pady=10)

        # Campos para cargar series
        self.txt_salida = ctk.CTkTextbox(self, width=460, height=260)
        self.txt_salida.pack(pady=10)

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

    def iniciar_registro(self):
        asistio = self.combo_asistencia.get() == "Sí"
        seleccion_dia = self.combo_dias.get()

        self.txt_salida.delete("1.0", "end")

        if not asistio:
            self.txt_salida.insert("end", "Inasistencia registrada. El progreso se mantendrá alineado para la próxima sesión.\n")
            return

        if " - " in seleccion_dia:
            id_rutina_dia = int(seleccion_dia.split(" - ")[0])
            ejercicios = self.fn_obtener_ejercicios_dia(id_rutina_dia)
            
            if not ejercicios:
                self.txt_salida.insert("end", "No hay ejercicios asignados a este día.")
                return

            self.txt_salida.insert("end", "=== EJERCICIOS A REALIZAR HOY ===\n\n")
            for ej in ejercicios:
                self.txt_salida.insert("end", f"• [{ej[0]}] {ej[1]} ({ej[2]})\n  Registrado en la BD para seguimiento de sobrecarga progresiva.\n\n")


# VENTANA PRINCIPAL (APP):

class App(ctk.CTk):
    def __init__(self, fn_login, fn_registro):
        super().__init__()
        self.title("No py, no gain - Menú Principal")
        self.geometry("400x520")

        self.fn_login = fn_login
        self.fn_registro = fn_registro
        self.usuario_actual = None

        self.label_titulo = ctk.CTkLabel(self, text="NO PY, NO GAIN", font=("Arial", 26, "bold"))
        self.label_titulo.pack(pady=30)

        # Panel Login por DNI
        self.frame_login = ctk.CTkFrame(self)
        self.frame_login.pack(pady=10, padx=20, fill="both")

        ctk.CTkLabel(self.frame_login, text="Ingresar con DNI", font=("Arial", 14, "bold")).pack(pady=10)
        self.ent_dni = ctk.CTkEntry(self.frame_login, placeholder_text="Número de Documento", width=250)
        self.ent_dni.pack(pady=5)

        self.btn_ingresar = ctk.CTkButton(self, text="Ingresar", command=self.ingresar_usuario, width=250)
        self.btn_ingresar.pack(pady=10)

        self.lbl_estado = ctk.CTkLabel(self, text="", text_color="yellow")
        self.lbl_estado.pack(pady=5)

    def ingresar_usuario(self):
        dni = self.ent_dni.get().strip()
        if dni:
            u = self.fn_login(dni)
            if u:
                self.usuario_actual = u
                self.lbl_estado.configure(text=f"Bienvenido/a {u[1]} {u[2]}", text_color="#2ECC71")
                self.habilitar_menu()
            else:
                self.lbl_estado.configure(text="DNI no encontrado. Registrese.", text_color="#E74C3C")
                self.mostrar_registro_rapido(dni)

    def mostrar_registro_rapido(self, dni):
        # Formulario básico para registrar nuevo usuario si no existe
        top = ctk.CTkToplevel(self)
        top.title("Registro de Usuario")
        top.geometry("350x420")
        top.after(100, top.lift)

        ctk.CTkLabel(top, text="Registro Nuevo Usuario", font=("Arial", 16, "bold")).pack(pady=10)
        
        ent_nom = ctk.CTkEntry(top, placeholder_text="Nombre", width=250)
        ent_nom.pack(pady=5)
        ent_ape = ctk.CTkEntry(top, placeholder_text="Apellido", width=250)
        ent_ape.pack(pady=5)
        ent_alt = ctk.CTkEntry(top, placeholder_text="Altura (m/cm)", width=250)
        ent_alt.pack(pady=5)
        ent_peso = ctk.CTkEntry(top, placeholder_text="Peso (kg)", width=250)
        ent_peso.pack(pady=5)
        combo_sexo = ctk.CTkOptionMenu(top, values=["M", "F", "Otro"], width=250)
        combo_sexo.pack(pady=5)

        def guardar():
            nom, ape = ent_nom.get().strip(), ent_ape.get().strip()
            alt, peso = ent_alt.get().strip(), ent_peso.get().strip()
            if nom and ape and alt and peso:
                self.fn_registro(dni, nom, ape, float(alt), float(peso), combo_sexo.get())
                top.destroy()
                self.ingresar_usuario()

        ctk.CTkButton(top, text="Registrarse", command=guardar, width=250).pack(pady=15)

    def habilitar_menu(self):
        self.frame_login.pack_forget()

        self.btn_ejercicios = ctk.CTkButton(self, text="Catálogo Ejercicios", command=self.abrir_ejercicios, width=260, height=40, font=("Arial", 14, "bold"))
        self.btn_ejercicios.pack(pady=10)

        self.btn_rutinas = ctk.CTkButton(self, text="Crear Rutina", command=self.abrir_crear_rutina, width=260, height=40, font=("Arial", 14, "bold"))
        self.btn_rutinas.pack(pady=10)

        self.btn_seguimiento = ctk.CTkButton(self, text="Seguimiento / Registro", command=self.abrir_seguimiento, width=260, height=40, font=("Arial", 14, "bold"))
        self.btn_seguimiento.pack(pady=10)

        self.btn_salir = ctk.CTkButton(self, text="Cerrar Sesión", command=self.destroy, width=260, height=40, font=("Arial", 14, "bold"), fg_color="#C0392B", hover_color="#E74C3C")
        self.btn_salir.pack(pady=10)

    def abrir_ejercicios(self):
        pass

    def abrir_crear_rutina(self):
        pass

    def abrir_seguimiento(self):
        pass