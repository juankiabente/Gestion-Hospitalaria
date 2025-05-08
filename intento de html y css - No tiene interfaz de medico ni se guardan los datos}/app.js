const users = {
  "doc123": { password: "admin123", name: "Dr. Juan Pérez", type: "staff" },
  "doc456": { password: "admin456", name: "Dra. María Gómez", type: "staff" }
};

function toggleForm() {
  const type = document.getElementById("user-type").value;
  if (type === "staff") {
    document.getElementById("toggle-text").style.display = "none";
    document.getElementById("register-form").style.display = "none";
    document.getElementById("login-form").style.display = "block";
  } else {
    document.getElementById("toggle-text").style.display = "block";
  }
}

function showRegister() {
  document.getElementById("login-form").style.display = "none";
  document.getElementById("register-form").style.display = "block";
}

function showLogin() {
  document.getElementById("register-form").style.display = "none";
  document.getElementById("login-form").style.display = "block";
}

function register() {
  const name = document.getElementById("name").value.trim();
  const userId = prompt("Ingrese documento (mínimo 8 caracteres):");
  const password = prompt("Ingrese una contraseña:");

  if (userId.length < 8 || !password || !name) {
    showMessage("Todos los campos son obligatorios y el documento debe tener al menos 8 caracteres", true);
    return;
  }

  if (users[userId]) {
    showMessage("El ID ya existe", true);
    return;
  }

  users[userId] = { password, name, type: "patient" };
  showMessage("Registro exitoso");
  showLogin();
}

function login() {
  const userId = document.getElementById("user-id").value.trim();
  const password = document.getElementById("password").value;

  if (!userId || !password) {
    showMessage("Complete todos los campos", true);
    return;
  }

  const user = users[userId];
  if (!user || user.password !== password) {
    showMessage("Credenciales inválidas", true);
    return;
  }
  // Guardar en localStorage
  localStorage.setItem("usuarioLogueado", JSON.stringify({ ...user, user_id: userId }));

  // Redireccionar según tipo
  if (user.type === "patient") {
    window.location.href = "paciente.html";
  } else {
    alert("Interfaz de staff aún no implementada.");
  }
}
  showMessage(`Bienvenido, ${user.name}`, false);


function showMessage(msg, isError = false) {
  const el = document.getElementById("message");
  el.textContent = msg;
  el.style.color = isError ? "red" : "green";
}


