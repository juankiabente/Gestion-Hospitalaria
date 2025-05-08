import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('sistema_medico.db')
        self.cursor = self.conn.cursor()
        self._crear_tablas()

    def _crear_tablas(self):
        # Tabla de usuarios
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                contraseña TEXT NOT NULL,
                tipo TEXT NOT NULL DEFAULT 'paciente'
            )
        ''')
        
        # Tabla de turnos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS turnos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                especialidad TEXT NOT NULL,
                estado TEXT DEFAULT 'pendiente',
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')
        
        # Tabla de historias clínicas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS historias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                diagnostico TEXT NOT NULL,
                observaciones TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')
        
        # Tabla de recetas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS recetas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                contenido TEXT NOT NULL,
                medico TEXT NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')
        
        self.conn.commit()

    def registrar_usuario(self, usuario, contraseña, tipo='paciente'):
        try:
            self.cursor.execute(
                'INSERT INTO usuarios (usuario, contraseña, tipo) VALUES (?, ?, ?)', 
                (usuario, contraseña, tipo)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def validar_usuario(self, usuario, contraseña):
        self.cursor.execute(
            'SELECT id, tipo FROM usuarios WHERE usuario=? AND contraseña=?', 
            (usuario, contraseña)
        )
        return self.cursor.fetchone()

    def agregar_turno(self, usuario_id, fecha, especialidad):
        self.cursor.execute(
            'INSERT INTO turnos (usuario_id, fecha, especialidad) VALUES (?, ?, ?)',
            (usuario_id, fecha, especialidad)
        )
        self.conn.commit()

    def obtener_turnos(self, usuario_id):
        self.cursor.execute(
            'SELECT fecha, especialidad, estado FROM turnos WHERE usuario_id=?', 
            (usuario_id,)
        )
        return self.cursor.fetchall()

    def agregar_diagnostico(self, usuario_id, diagnostico, observaciones=''):
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute(
            'INSERT INTO historias (usuario_id, fecha, diagnostico, observaciones) VALUES (?, ?, ?, ?)',
            (usuario_id, fecha, diagnostico, observaciones)
        )
        self.conn.commit()

    def obtener_historia(self, usuario_id):
        self.cursor.execute(
            'SELECT fecha, diagnostico, observaciones FROM historias WHERE usuario_id=? ORDER BY fecha DESC', 
            (usuario_id,)
        )
        return self.cursor.fetchall()

    def generar_receta(self, usuario_id, contenido, medico):
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute(
            'INSERT INTO recetas (usuario_id, fecha, contenido, medico) VALUES (?, ?, ?, ?)',
            (usuario_id, fecha, contenido, medico)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def cerrar(self):
        self.conn.close()

class LoginWindow:
    def __init__(self, master, db):
        self.master = master
        self.db = db
        self.master.title("Sistema Médico - Login")
        self.master.geometry("300x250")
        
        tk.Label(self.master, text="Usuario:").pack(pady=5)
        self.entrada_usuario = tk.Entry(self.master)
        self.entrada_usuario.pack()

        tk.Label(self.master, text="Contraseña:").pack(pady=5)
        self.entrada_contraseña = tk.Entry(self.master, show="*")
        self.entrada_contraseña.pack()

        tk.Button(self.master, text="Iniciar Sesión", command=self.iniciar_sesion).pack(pady=10)
        tk.Button(self.master, text="Registrar Usuario", command=self.registrar_usuario).pack()

    def registrar_usuario(self):
        usuario = self.entrada_usuario.get()
        contraseña = self.entrada_contraseña.get()
        
        if not usuario or not contraseña:
            messagebox.showerror("Error", "Usuario y contraseña son obligatorios")
            return
            
        if self.db.registrar_usuario(usuario, contraseña):
            messagebox.showinfo("Registro exitoso", "Usuario registrado correctamente.")
        else:
            messagebox.showerror("Error", "El usuario ya existe.")

    def iniciar_sesion(self):
        usuario = self.entrada_usuario.get()
        contraseña = self.entrada_contraseña.get()
        
        resultado = self.db.validar_usuario(usuario, contraseña)
        
        if resultado:
            usuario_id, tipo = resultado
            messagebox.showinfo("Inicio de sesión", f"Bienvenido, {usuario}")
            self.master.withdraw()
            
            if tipo == 'paciente':
                PanelPacienteWindow(self.master, self.db, usuario_id, usuario)
            else:
                PanelMedicoWindow(self.master, self.db, usuario_id, usuario)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

class PanelPacienteWindow:
    def __init__(self, master, db, usuario_id, usuario):
        self.master = master
        self.db = db
        self.usuario_id = usuario_id
        self.usuario = usuario
        
        self.window = tk.Toplevel(master)
        self.window.title("Panel del Paciente")
        self.window.geometry("500x400")
        self.window.protocol("WM_DELETE_WINDOW", self.cerrar_sesion)
        
        tk.Label(self.window, text=f"Bienvenido, {usuario}", font=("Arial", 14)).pack(pady=10)

        # Frame principal para organizar los botones
        frame_botones = tk.Frame(self.window)
        frame_botones.pack(pady=10)
        
        # Botones del paciente
        tk.Button(frame_botones, text="Reservar Turno", command=self.reservar_turno, width=20).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(frame_botones, text="Ver Mis Turnos", command=self.ver_turnos, width=20).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(frame_botones, text="Ver Historia Clínica", command=self.ver_historia, width=20).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(frame_botones, text="Ver Recetas", command=self.ver_recetas, width=20).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(frame_botones, text="Cerrar Sesión", command=self.cerrar_sesion, width=20).grid(row=2, column=0, columnspan=2, pady=10)

    def reservar_turno(self):
        # Ventana para reservar turno
        ventana_turno = tk.Toplevel(self.window)
        ventana_turno.title("Reservar Turno")
        ventana_turno.geometry("300x200")
        
        tk.Label(ventana_turno, text="Fecha (DD/MM/AAAA):").pack(pady=5)
        entrada_fecha = tk.Entry(ventana_turno)
        entrada_fecha.pack()
        
        tk.Label(ventana_turno, text="Especialidad:").pack(pady=5)
        entrada_especialidad = tk.Entry(ventana_turno)
        entrada_especialidad.pack()
        
        def guardar_turno():
            fecha = entrada_fecha.get()
            especialidad = entrada_especialidad.get()
            
            if fecha and especialidad:
                try:
                    self.db.agregar_turno(self.usuario_id, fecha, especialidad)
                    messagebox.showinfo("Éxito", "Turno reservado correctamente")
                    ventana_turno.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo reservar el turno: {str(e)}")
            else:
                messagebox.showerror("Error", "Todos los campos son obligatorios")
        
        tk.Button(ventana_turno, text="Reservar", command=guardar_turno).pack(pady=10)

    def ver_turnos(self):
        turnos = self.db.obtener_turnos(self.usuario_id)
        
        ventana_turnos = tk.Toplevel(self.window)
        ventana_turnos.title("Mis Turnos")
        ventana_turnos.geometry("500x300")
        
        if not turnos:
            tk.Label(ventana_turnos, text="No tienes turnos reservados").pack(pady=20)
            return
        
        # Crear un frame con scrollbar
        frame = tk.Frame(ventana_turnos)
        frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        lista = tk.Listbox(frame, yscrollcommand=scrollbar.set, width=60)
        for turno in turnos:
            lista.insert(tk.END, f"Fecha: {turno[0]} - Especialidad: {turno[1]} - Estado: {turno[2]}")
        lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=lista.yview)

    def ver_historia(self):
        historias = self.db.obtener_historia(self.usuario_id)
        
        ventana_historia = tk.Toplevel(self.window)
        ventana_historia.title("Historia Clínica")
        ventana_historia.geometry("600x400")
        
        if not historias:
            tk.Label(ventana_historia, text="No hay registros en tu historia clínica").pack(pady=20)
            return
        
        # Crear un frame con scrollbar
        frame = tk.Frame(ventana_historia)
        frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        texto = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        texto.pack(fill=tk.BOTH, expand=True)
        
        for historia in historias:
            texto.insert(tk.END, f"Fecha: {historia[0]}\n")
            texto.insert(tk.END, f"Diagnóstico: {historia[1]}\n")
            if historia[2]:
                texto.insert(tk.END, f"Observaciones: {historia[2]}\n")
            texto.insert(tk.END, "-"*50 + "\n\n")
        
        texto.config(state=tk.DISABLED)
        scrollbar.config(command=texto.yview)

    def ver_recetas(self):
        recetas = self.db.obtener_recetas(self.usuario_id)  # Asegúrate de tener esta función
        ventana_recetas = tk.Toplevel(self.window)
        ventana_recetas.title("Mis Recetas")
        ventana_recetas.geometry("600x400")
        
        if not recetas:
            tk.Label(ventana_recetas, text="No tienes recetas").pack(pady=20)
            return
        
        # Crear un frame con scrollbar
        frame = tk.Frame(ventana_recetas)
        frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        texto = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        texto.pack(fill=tk.BOTH, expand=True)
        
        for receta in recetas:
            texto.insert(tk.END, f"Fecha: {receta[0]}\nContenido: {receta[1]}\nMédico: {receta[2]}\n")
            texto.insert(tk.END, "-"*50 + "\n")
        
        texto.config(state=tk.DISABLED)
        scrollbar.config(command=texto.yview)

    def cerrar_sesion(self):
        self.window.destroy()
        self.master.deiconify()

class PanelMedicoWindow:
    def __init__(self, master, db, usuario_id, usuario):
        self.master = master
        self.db = db
        self.usuario_id = usuario_id
        self.usuario = usuario
        
        self.window = tk.Toplevel(master)
        self.window.title("Panel del Médico")
        self.window.geometry("600x500")
        self.window.protocol("WM_DELETE_WINDOW", self.cerrar_sesion)
        
        tk.Label(self.window, text=f"Bienvenido, Dr. {usuario}", font=("Arial", 14)).pack(pady=10)

        # Frame principal para organizar los botones
        frame_botones = tk.Frame(self.window)
        frame_botones.pack(pady=10)
        
        # Botones del médico
        tk.Button(frame_botones, text="Ver Turnos del Día", command=self.ver_turnos_dia, width=25).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(frame_botones, text="Agregar Diagnóstico", command=self.agregar_diagnostico, width=25).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(frame_botones, text="Generar Receta", command=self.generar_receta, width=25).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(frame_botones, text="Ver Historias Clínicas", command=self.ver_historias, width=25).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(frame_botones, text="Cerrar Sesión", command=self.cerrar_sesion, width=25).grid(row=2, column=0, columnspan=2, pady=10)

    def ver_turnos_dia(self):
        # Implementar la visualización de turnos del día
        messagebox.showinfo("Turnos del Día", "Funcionalidad de turnos del día en desarrollo")

    def agregar_diagnostico(self):
        # Ventana para agregar diagnóstico
        ventana_diag = tk.Toplevel(self.window)
        ventana_diag.title("Agregar Diagnóstico")
        ventana_diag.geometry("400x300")
        
        tk.Label(ventana_diag, text="ID del Paciente:").pack(pady=5)
        entrada_paciente = tk.Entry(ventana_diag)
        entrada_paciente.pack()
        
        tk.Label(ventana_diag, text="Diagnóstico:").pack(pady=5)
        entrada_diagnostico = tk.Text(ventana_diag, height=5, width=40)
        entrada_diagnostico.pack()
        
        tk.Label(ventana_diag, text="Observaciones:").pack(pady=5)
        entrada_observaciones = tk.Text(ventana_diag, height=3, width=40)
        entrada_observaciones.pack()
        
        def guardar_diagnostico():
            paciente_id = entrada_paciente.get()
            diagnostico = entrada_diagnostico.get("1.0", tk.END).strip()
            observaciones = entrada_observaciones.get("1.0", tk.END).strip()
            
            if paciente_id and diagnostico:
                try:
                    self.db.agregar_diagnostico(paciente_id, diagnostico, observaciones)
                    messagebox.showinfo("Éxito", "Diagnóstico agregado correctamente")
                    ventana_diag.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo agregar el diagnóstico: {str(e)}")
            else:
                messagebox.showerror("Error", "ID de paciente y diagnóstico son obligatorios")
        
        tk.Button(ventana_diag, text="Guardar", command=guardar_diagnostico).pack(pady=10)

    def generar_receta(self):
        # Ventana para generar receta
        ventana_receta = tk.Toplevel(self.window)
        ventana_receta.title("Generar Receta Médica")
        ventana_receta.geometry("500x400")
        
        tk.Label(ventana_receta, text="ID del Paciente:").pack(pady=5)
        entrada_paciente = tk.Entry(ventana_receta)
        entrada_paciente.pack()
        
        tk.Label(ventana_receta, text="Contenido de la Receta:").pack(pady=5)
        entrada_contenido = tk.Text(ventana_receta, height=15, width=60)
        entrada_contenido.pack()
        
        def guardar_receta():
            paciente_id = entrada_paciente.get()
            contenido = entrada_contenido.get("1.0", tk.END).strip()
            
            if paciente_id and contenido:
                try:
                    receta_id = self.db.generar_receta(paciente_id, contenido, self.usuario)
                    messagebox.showinfo("Éxito", f"Receta generada con ID: {receta_id}")
                    ventana_receta.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo generar la receta: {str(e)}")
            else:
                messagebox.showerror("Error", "ID de paciente y contenido son obligatorios")
        
        tk.Button(ventana_receta, text="Generar Receta", command=guardar_receta).pack(pady=10)

    def ver_historias(self):
        # Implementar la visualización de historias clínicas
        messagebox.showinfo("Historias Clínicas", "Funcionalidad de ver historias clínicas en desarrollo")

    def cerrar_sesion(self):
        self.window.destroy()
        self.master.deiconify()

def main():
    db = Database()
    
    root = tk.Tk()
    app = LoginWindow(root, db)
    
    try:
        root.mainloop()
    finally:
        db.cerrar()

if __name__ == "__main__":
    main()
