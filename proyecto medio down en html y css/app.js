const patientsDB = {}; // Simulación de base de datos de pacientes
const staffDB = {
    "doc123": { password: "admin123", name: "Dr. Juan Pérez", role: "Médico" },
    "doc456": { password: "admin456", name: "Dra. María Gómez", role: "Enfermera Jefe" }
};

function showMessage(message, isError = false) {
    const msgDiv = document.getElementById("message");
    msgDiv.textContent = message;
    msgDiv.style.color = isError ? "red" : "green";
    setTimeout(() => {
        msgDiv.textContent = "";
    }, 5000);
}

function toggleForm() {
    const userType = document.getElementById("user-type").value;
    if (userType === "patient") {
        document.getElementById("login-form").style.display = "block";
        document.getElementById("register-form").style.display = "none";
        document.getElementById("toggle-text").style.display = "block";
    } else {
        document.getElementById("login-form").style.display = "block";
        document.getElementById("register-form").style.display = "none";
        document.getElementById("toggle-text").style.display = "none"; // no registrar staff
    }
}

function toggleRegister() {
    document.getElementById("login-form").style.display = "none";
    document.getElementById("register-form").style.display = "block";
    document.getElementById("toggle-text").style.display = "none";
}

function toggleLogin() {
    document.getElementById("login-form").style.display = "block";
    document.getElementById("register-form").style.display = "none";
    document.getElementById("toggle-text").style.display = "block";
}

function register() {
    const userId = document.getElementById("user-id").value.trim();
    const password = document.getElementById("password").value;
    const name = document.getElementById("name").value.trim();

    if (!userId || !password || !name) {
        showMessage("Por favor, complete todos los campos.", true);
        return;
    }
    if (patientsDB[userId] || staffDB[userId]) {
        showMessage("El ID de usuario ya existe.", true);
        return;
    }
    if (userId.length < 8) {
        showMessage("El documento debe tener al menos 8 caracteres.", true);
        return;
    }
    patientsDB[userId] = { password, name, type: "Paciente" };
    showMessage("Registro exitoso. Ahora puede iniciar sesión.");
    toggleLogin();
}

function login() {
    const userType = document.getElementById("user-type").value;
    const userId = document.getElementById("user-id").value.trim();
    const password = document.getElementById("password").value;

    if (!userId || !password) {
        showMessage("Por favor, complete todos los campos.", true);
        return;
    }

    let user = null;

    if (userType === "patient") {
        user = patientsDB[userId];
        if (!user) {
            showMessage("Usuario no encontrado.", true);
            return;
        }
    } else {
        user = staffDB[userId];
        if (!user) {
            showMessage("Personal de salud no encontrado.", true);
            return;
        }
    }

    if (user.password !== password) {
        showMessage("Contraseña incorrecta.", true);
        return;
    }

    showMessage(`Inicio de sesión exitoso. Bienvenido, ${user.name}.`);
    // Aquí podrías redirigir a otra sección o mostrar la interfaz principal.
    // Por ejemplo, ocultar el formulario y mostrar un mensaje o dashboard
    document.getElementById("form-container").innerHTML = `
        <h2>Bienvenido, ${user.name}</h2>
        <p>Tipo de usuario: ${userType === "patient" ? "Paciente" : "Personal de Salud"}</p>
        <button onclick="logout()">Cerrar sesión</button>
    `;
}

function logout() {
    location.reload();
}

// Inicialización
window.onload = () => {
    toggleForm();
};
</content>
</create_file>
