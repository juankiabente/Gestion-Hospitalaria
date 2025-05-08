import heapq
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# --- Constantes ---
USER_DB_FILE = "users.json"
STAFF_DB_FILE = "staff.json"

# --- Backend ---

class UserType(Enum):
    PATIENT = "Paciente"
    STAFF = "Personal de Salud"

class PriorityLevel(Enum):
    CRITICAL = 1
    URGENT = 2
    REGULAR = 3

class PatientStatus(Enum):
    PENDING = "Pendiente"
    IN_PROGRESS = "En atención"
    COMPLETED = "Atendido"
    CANCELLED = "Cancelado"

@dataclass(order=True)
class MedicalTurn:
    patient_id: str
    name: str
    priority: PriorityLevel
    status: PatientStatus = PatientStatus.PENDING
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not isinstance(self.priority, PriorityLevel):
            raise ValueError("Prioridad debe ser instancia de PriorityLevel")
        if len(self.patient_id) < 8:
            raise ValueError("ID de paciente debe tener al menos 8 caracteres")

class HospitalQueue:
    def __init__(self):
        self._queue = []
        self._patient_index = {}
        
    def add_patient(self, patient: MedicalTurn) -> None:
        if patient.patient_id in self._patient_index:
            raise ValueError("Paciente ya en cola")
        
        entry = (patient.priority.value, patient.timestamp.timestamp(), patient)
        heapq.heappush(self._queue, entry)
        self._patient_index[patient.patient_id] = patient
        
    def next_patient(self) -> Optional[MedicalTurn]:
        if not self._queue:
            return None
            
        _, _, patient = heapq.heappop(self._queue)
        self._patient_index.pop(patient.patient_id, None)
        patient.status = PatientStatus.IN_PROGRESS
        return patient
        
    def cancel_turn(self, patient_id: str) -> bool:
        patient = self._patient_index.get(patient_id)
        if not patient:
            return False
            
        patient.status = PatientStatus.CANCELLED
        return True
        
    def get_queue_status(self) -> List[Dict]:
        return [
            {
                "patient_id": p.patient_id,
                "name": p.name,
                "priority": p.priority.name,
                "status": p.status.value,
                "timestamp": p.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            for _, _, p in sorted(self._queue)
        ]
        
    def __len__(self) -> int:
        return len(self._queue)

class AuthSystem:
    @staticmethod
    def load_db(filename: str) -> Dict:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return {}
    
    @staticmethod
    def save_db(data: Dict, filename: str) -> None:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def register_patient(cls, user_id: str, password: str, name: str) -> Tuple[bool, str]:
        users = cls.load_db(USER_DB_FILE)
        
        if user_id in users:
            return False, "El ID de usuario ya existe"
        
        users[user_id] = {
            "password": password,
            "name": name,
            "type": UserType.PATIENT.value
        }
        
        cls.save_db(users, USER_DB_FILE)
        return True, "Registro exitoso"
    
    @classmethod
    def login(cls, user_id: str, password: str, is_staff: bool = False) -> Tuple[bool, str, Optional[Dict]]:
        db_file = STAFF_DB_FILE if is_staff else USER_DB_FILE
        users = cls.load_db(db_file)
        
        if user_id not in users:
            return False, "Usuario no encontrado", None
        
        if users[user_id]["password"] != password:
            return False, "Contraseña incorrecta", None
            
        user_data = users[user_id].copy()
        user_data["user_id"] = user_id
        return True, "Inicio de sesión exitoso", user_data

# --- Frontend ---

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Hospitalario - Login")
        self.root.geometry("500x400")
        
        # Inicializar bases de datos si no existen
        self.init_dbs()
        
        # Variables de control
        self.user_type = tk.StringVar(value=UserType.PATIENT.value)
        self.showing_register = False
        
        # UI
        self.setup_ui()
    
    def init_dbs(self):
        # Crear DB de personal si no existe (datos de ejemplo)
        if not os.path.exists(STAFF_DB_FILE):
            staff_db = {
                "doc123": {
                    "password": "admin123",
                    "name": "Dr. Juan Pérez",
                    "type": UserType.STAFF.value,
                    "role": "Médico"
                },
                "doc456": {
                    "password": "admin456",
                    "name": "Dra. María Gómez",
                    "type": UserType.STAFF.value,
                    "role": "Enfermera Jefe"
                }
            }
            AuthSystem.save_db(staff_db, STAFF_DB_FILE)
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="Sistema de Gestión Hospitalaria", 
                 font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # Selector de tipo de usuario
        user_type_frame = ttk.Frame(main_frame)
        user_type_frame.pack(pady=10)
        
        ttk.Label(user_type_frame, text="Tipo de usuario:").pack(side=tk.LEFT)
        
        ttk.Radiobutton(
            user_type_frame, 
            text=UserType.PATIENT.value,
            variable=self.user_type,
            value=UserType.PATIENT.value,
            command=self.toggle_user_type
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Radiobutton(
            user_type_frame, 
            text=UserType.STAFF.value,
            variable=self.user_type,
            value=UserType.STAFF.value,
            command=self.toggle_user_type
        ).pack(side=tk.LEFT)
        
        # Formulario de login/register
        self.form_frame = ttk.Frame(main_frame)
        self.form_frame.pack(fill=tk.X, pady=20)
        
        self.setup_login_form()
        
        # Botón para cambiar entre login/register (solo pacientes)
        self.toggle_form_btn = ttk.Button(
            main_frame,
            text="Registrarse como nuevo paciente",
            command=self.toggle_form
        )
        self.toggle_form_btn.pack(pady=10)
    
    def setup_login_form(self):
        # Limpiar frame
        for widget in self.form_frame.winfo_children():
            widget.destroy()
        
        # Campos del formulario
        ttk.Label(self.form_frame, text="Documento:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.user_id_entry = ttk.Entry(self.form_frame)
        self.user_id_entry.grid(row=0, column=1, pady=5, padx=5, sticky=tk.EW)
        
        ttk.Label(self.form_frame, text="Contraseña:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(self.form_frame, show="*")
        self.password_entry.grid(row=1, column=1, pady=5, padx=5, sticky=tk.EW)
        
        # Solo mostrar campo de nombre en registro
        if self.showing_register:
            ttk.Label(self.form_frame, text="Nombre completo:").grid(row=2, column=0, sticky=tk.W, pady=5)
            self.name_entry = ttk.Entry(self.form_frame)
            self.name_entry.grid(row=2, column=1, pady=5, padx=5, sticky=tk.EW)
        
        # Botón de acción
        btn_text = "Registrarse" if self.showing_register else "Iniciar sesión"
        action_btn = ttk.Button(
            self.form_frame,
            text=btn_text,
            command=self.login_or_register
        )
        action_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Configurar grid
        self.form_frame.columnconfigure(1, weight=1)
    
    def setup_register_form(self):
        self.showing_register = True
        self.toggle_form_btn.config(text="Volver a inicio de sesión")
        self.setup_login_form()
    
    def toggle_form(self):
        if self.showing_register:
            self.showing_register = False
            self.toggle_form_btn.config(text="Registrarse como nuevo paciente")
        else:
            if self.user_type.get() == UserType.STAFF.value:
                messagebox.showinfo("Información", "El personal de salud no necesita registrarse")
                return
            self.showing_register = True
            self.toggle_form_btn.config(text="Volver a inicio de sesión")
        
        self.setup_login_form()
    
    def toggle_user_type(self):
        if self.user_type.get() == UserType.STAFF.value and self.showing_register:
            self.showing_register = False
            self.toggle_form_btn.config(text="Registrarse como nuevo paciente")
        self.setup_login_form()
    
    def login_or_register(self):
        user_id = self.user_id_entry.get()
        password = self.password_entry.get()
        
        if not user_id or not password:
            messagebox.showerror("Error", "Documento y contraseña son requeridos")
            return
        
        if self.showing_register:
            if self.user_type.get() == UserType.STAFF.value:
                messagebox.showerror("Error", "El personal de salud no puede registrarse aquí")
                return
            
            name = self.name_entry.get()
            if not name:
                messagebox.showerror("Error", "Nombre completo es requerido")
                return
            
            success, msg = AuthSystem.register_patient(user_id, password, name)
            if success:
                messagebox.showinfo("Éxito", msg)
                self.toggle_form()
            else:
                messagebox.showerror("Error", msg)
        else:
            is_staff = self.user_type.get() == UserType.STAFF.value
            success, msg, user_data = AuthSystem.login(user_id, password, is_staff)
            
            if success:
                messagebox.showinfo("Éxito", msg)
                self.open_main_app(user_data)
            else:
                messagebox.showerror("Error", msg)
    
    def open_main_app(self, user_data):
        self.root.destroy()
        
        root = tk.Tk()
        if user_data["type"] == UserType.STAFF.value:
            app = StaffApp(root, user_data)
        else:
            app = PatientApp(root, user_data)
        root.mainloop()

class PatientApp:
    def __init__(self, root, user_data):
        self.root = root
        self.user_data = user_data
        self.root.title(f"Turnos Hospitalarios - Paciente: {user_data['name']}")
        self.root.geometry("800x600")
        
        self.queue = HospitalQueue()
        
        self.setup_ui()
        self.refresh_queue()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Panel de información del usuario
        user_frame = ttk.LabelFrame(main_frame, text="Información del Paciente", padding=10)
        user_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(user_frame, text=f"Nombre: {self.user_data['name']}").pack(anchor=tk.W)
        ttk.Label(user_frame, text=f"Documento: {self.user_data['user_id']}").pack(anchor=tk.W)
        
        # Panel de solicitud de turno
        turn_frame = ttk.LabelFrame(main_frame, text="Solicitar Turno", padding=10)
        turn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(turn_frame, text="Nivel de Urgencia:").pack(anchor=tk.W)
        self.priority_combobox = ttk.Combobox(turn_frame, values=[
            "Crítico (Dificultad respiratoria severa)", 
            "Urgente (Fiebre alta persistente)", 
            "Regular (Síntomas leves)"
        ], state="readonly")
        self.priority_combobox.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            turn_frame,
            text="Solicitar Turno",
            command=self.request_turn
        ).pack(pady=5)
        
        # Panel de cola de espera
        queue_frame = ttk.LabelFrame(main_frame, text="Cola de Espera", padding=10)
        queue_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        columns = ("id", "name", "priority", "status", "time")
        self.queue_tree = ttk.Treeview(queue_frame, columns=columns, show="headings")
        
        self.queue_tree.heading("id", text="Documento")
        self.queue_tree.heading("name", text="Nombre")
        self.queue_tree.heading("priority", text="Prioridad")
        self.queue_tree.heading("status", text="Estado")
        self.queue_tree.heading("time", text="Hora Registro")
        
        for col in columns:
            self.queue_tree.column(col, width=120, anchor=tk.W)
        
        self.queue_tree.pack(fill=tk.BOTH, expand=True)
        
        # Configurar tags para colores
        self.queue_tree.tag_configure("critical", background="#dc3545", foreground="white")
        self.queue_tree.tag_configure("urgent", background="#fd7e14")
        self.queue_tree.tag_configure("regular", background="#ffc107")
        
        # Barra de estado
        self.status_var = tk.StringVar()
        ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN).pack(fill=tk.X)
    
    def request_turn(self):
        priority_text = self.priority_combobox.get()
        
        if not priority_text:
            messagebox.showwarning("Error", "Seleccione un nivel de urgencia")
            return
        
        # Mapear selección a PriorityLevel
        if "Crítico" in priority_text:
            priority = PriorityLevel.CRITICAL
        elif "Urgente" in priority_text:
            priority = PriorityLevel.URGENT
        else:
            priority = PriorityLevel.REGULAR
            
        try:
            patient = MedicalTurn(
                patient_id=self.user_data['user_id'],
                name=self.user_data['name'],
                priority=priority
            )
            self.queue.add_patient(patient)
            messagebox.showinfo("Éxito", "Turno registrado correctamente")
            self.refresh_queue()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def refresh_queue(self):
        for item in self.queue_tree.get_children():
            self.queue_tree.delete(item)
            
        patients = self.queue.get_queue_status()
        
        for patient in patients:
            priority = patient["priority"]
            tags = ()
            
            if priority == "CRITICAL":
                tags = ("critical",)
            elif priority == "URGENT":
                tags = ("urgent",)
            else:
                tags = ("regular",)
            
            self.queue_tree.insert("", tk.END, 
                values=(
                    patient["patient_id"],
                    patient["name"],
                    patient["priority"],
                    patient["status"],
                    patient["timestamp"]
                ),
                tags=tags
            )
        
        self.status_var.set(f"Pacientes en espera: {len(self.queue)} | Última actualización: {datetime.now().strftime('%H:%M:%S')}")

class StaffApp:
    def __init__(self, root, user_data):
        self.root = root
        self.user_data = user_data
        self.root.title(f"Gestión Hospitalaria - {user_data['name']} ({user_data.get('role', 'Staff')})")
        self.root.geometry("1000x700")
        
        self.queue = HospitalQueue()
        
        self.setup_ui()
        self.refresh_queue()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Panel de información del staff
        staff_frame = ttk.LabelFrame(main_frame, text="Información del Personal", padding=10)
        staff_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(staff_frame, text=f"Nombre: {self.user_data['name']}").pack(anchor=tk.W)
        ttk.Label(staff_frame, text=f"Documento: {self.user_data['user_id']}").pack(anchor=tk.W)
        ttk.Label(staff_frame, text=f"Rol: {self.user_data.get('role', 'No especificado')}").pack(anchor=tk.W)
        
        # Panel de control
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            control_frame,
            text="Atender Siguiente Paciente",
            command=self.attend_next
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="Actualizar Cola",
            command=self.refresh_queue
        ).pack(side=tk.LEFT, padx=5)
        
        # Panel de cola de espera
        queue_frame = ttk.LabelFrame(main_frame, text="Cola de Pacientes", padding=10)
        queue_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        columns = ("id", "name", "priority", "status", "time")
        self.queue_tree = ttk.Treeview(queue_frame, columns=columns, show="headings")
        
        self.queue_tree.heading("id", text="Documento")
        self.queue_tree.heading("name", text="Nombre")
        self.queue_tree.heading("priority", text="Prioridad")
        self.queue_tree.heading("status", text="Estado")
        self.queue_tree.heading("time", text="Hora Registro")
        
        for col in columns:
            self.queue_tree.column(col, width=150, anchor=tk.W)
        
        self.queue_tree.pack(fill=tk.BOTH, expand=True)
        
        # Configurar tags para colores
        self.queue_tree.tag_configure("critical", background="#dc3545", foreground="white")
        self.queue_tree.tag_configure("urgent", background="#fd7e14")
        self.queue_tree.tag_configure("regular", background="#ffc107")
        
        # Barra de estado
        self.status_var = tk.StringVar()
        ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN).pack(fill=tk.X)
    
    def attend_next(self):
        if len(self.queue) == 0:
            messagebox.showinfo("Info", "No hay pacientes en espera")
            return
            
        patient = self.queue.next_patient()
        messagebox.showinfo(
            "Paciente Atendido", 
            f"Atendiendo a:\n\n"
            f"Nombre: {patient.name}\n"
            f"Documento: {patient.patient_id}\n"
            f"Prioridad: {patient.priority.name}\n"
            f"Hora registro: {patient.timestamp.strftime('%H:%M:%S')}"
        )
        self.refresh_queue()
    
    def refresh_queue(self):
        for item in self.queue_tree.get_children():
            self.queue_tree.delete(item)
            
        patients = self.queue.get_queue_status()
        
        for patient in patients:
            priority = patient["priority"]
            tags = ()
            
            if priority == "CRITICAL":
                tags = ("critical",)
            elif priority == "URGENT":
                tags = ("urgent",)
            else:
                tags = ("regular",)
            
            self.queue_tree.insert("", tk.END, 
                values=(
                    patient["patient_id"],
                    patient["name"],
                    patient["priority"],
                    patient["status"],
                    patient["timestamp"]
                ),
                tags=tags
            )
        
        self.status_var.set(f"Pacientes en espera: {len(self.queue)} | Última actualización: {datetime.now().strftime('%H:%M:%S')} | Rol: {self.user_data.get('role', 'Staff')}")

# --- Punto de entrada ---

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()