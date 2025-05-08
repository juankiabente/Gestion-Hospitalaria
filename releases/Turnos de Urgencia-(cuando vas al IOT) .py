import heapq
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# --- Backend --- (Sigue buenas prácticas de estructuración)

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

# --- Frontend con Tkinter --- (Patrón MVC simplificado)

class HospitalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión Hospitalaria - Turnos")
        self.root.geometry("1000x600")
        
        # Modelo
        self.queue = HospitalQueue()
        
        # Estilo
        self.setup_styles()
        
        # UI
        self.setup_ui()
        
        # Carga inicial
        self.refresh_queue()
    
    def setup_styles(self):
        style = ttk.Style()
        style.configure("TFrame", padding=6)
        style.configure("TLabel", padding=4, font=('Helvetica', 10))
        style.configure("TButton", padding=6, font=('Helvetica', 10))
        style.configure("Critical.TLabel", foreground="white", background="#dc3545")
        style.configure("Urgent.TLabel", background="#fd7e14")
        style.configure("Regular.TLabel", background="#ffc107")
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel izquierdo (Formulario)
        form_frame = ttk.LabelFrame(main_frame, text="Solicitar Turno", padding=10)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        ttk.Label(form_frame, text="ID de Paciente:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.patient_id_entry = ttk.Entry(form_frame)
        self.patient_id_entry.grid(row=0, column=1, pady=2, padx=5)
        
        ttk.Label(form_frame, text="Nombre Completo:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.patient_name_entry = ttk.Entry(form_frame)
        self.patient_name_entry.grid(row=1, column=1, pady=2, padx=5)
        
        ttk.Label(form_frame, text="Nivel de Urgencia:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.priority_combobox = ttk.Combobox(form_frame, values=[
            "Crítico (Dificultad respiratoria severa)", 
            "Urgente (Fiebre alta persistente)", 
            "Regular (Síntomas leves)"
        ], state="readonly")
        self.priority_combobox.grid(row=2, column=1, pady=2, padx=5)
        
        submit_btn = ttk.Button(form_frame, text="Solicitar Turno", command=self.submit_turn)
        submit_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Panel derecho (Cola de pacientes)
        queue_frame = ttk.LabelFrame(main_frame, text="Cola de Pacientes", padding=10)
        queue_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # Controles de cola
        controls_frame = ttk.Frame(queue_frame)
        controls_frame.pack(fill=tk.X, pady=5)
        
        self.next_btn = ttk.Button(controls_frame, text="Atender Siguiente", command=self.attend_next)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = ttk.Button(controls_frame, text="Actualizar", command=self.refresh_queue)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Treeview para mostrar la cola
        self.queue_tree = ttk.Treeview(queue_frame, columns=("id", "name", "priority", "status", "time"), show="headings")
        self.queue_tree.heading("id", text="ID Paciente")
        self.queue_tree.heading("name", text="Nombre")
        self.queue_tree.heading("priority", text="Prioridad")
        self.queue_tree.heading("status", text="Estado")
        self.queue_tree.heading("time", text="Hora Registro")
        
        self.queue_tree.column("id", width=120)
        self.queue_tree.column("name", width=150)
        self.queue_tree.column("priority", width=100)
        self.queue_tree.column("status", width=100)
        self.queue_tree.column("time", width=150)
        
        self.queue_tree.pack(fill=tk.BOTH, expand=True)
        
        # Barra de estado
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X)
    
    def submit_turn(self):
        patient_id = self.patient_id_entry.get()
        patient_name = self.patient_name_entry.get()
        priority_text = self.priority_combobox.get()
        
        if not patient_id or not patient_name or not priority_text:
            messagebox.showwarning("Campos incompletos", "Por favor complete todos los campos")
            return
        
        try:
            # Mapear selección a PriorityLevel
            if "Crítico" in priority_text:
                priority = PriorityLevel.CRITICAL
            elif "Urgente" in priority_text:
                priority = PriorityLevel.URGENT
            else:
                priority = PriorityLevel.REGULAR
                
            patient = MedicalTurn(patient_id, patient_name, priority)
            self.queue.add_patient(patient)
            
            messagebox.showinfo("Éxito", "Turno registrado correctamente")
            self.patient_id_entry.delete(0, tk.END)
            self.patient_name_entry.delete(0, tk.END)
            self.priority_combobox.set('')
            
            self.refresh_queue()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def attend_next(self):
        if len(self.queue) == 0:
            messagebox.showinfo("Cola vacía", "No hay pacientes en espera")
            return
            
        patient = self.queue.next_patient()
        messagebox.showinfo("Paciente atendido", f"Atendiendo a: {patient.name}\nPrioridad: {patient.priority.name}")
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
        
        # Configurar tags para colores
        self.queue_tree.tag_configure("critical", background="#dc3545", foreground="white")
        self.queue_tree.tag_configure("urgent", background="#fd7e14")
        self.queue_tree.tag_configure("regular", background="#ffc107")
        
        self.status_var.set(f"Pacientes en espera: {len(self.queue)} | Última actualización: {datetime.now().strftime('%H:%M:%S')}")

# --- Punto de entrada ---

if __name__ == "__main__":
    root = tk.Tk()
    app = HospitalApp(root)
    root.mainloop()


