const turnos = JSON.parse(localStorage.getItem("turnos")) || [];

const user = JSON.parse(localStorage.getItem("usuarioLogueado"));
if (!user || user.type !== "patient") {
  alert("Acceso denegado");
  location.href = "index.html";
}

document.getElementById("nombre-usuario").textContent = user.name;
document.getElementById("doc-usuario").textContent = user.user_id;

function solicitarTurno() {
  const prioridad = parseInt(document.getElementById("prioridad").value);
  const ahora = new Date().toISOString();

  // Evitar duplicados
  if (turnos.some(t => t.patient_id === user.user_id)) {
    alert("Ya tiene un turno en espera");
    return;
  }

  turnos.push({
    patient_id: user.user_id,
    name: user.name,
    prioridad,
    timestamp: ahora
  });

  localStorage.setItem("turnos", JSON.stringify(turnos));
  mostrarTurnos();
}

function mostrarTurnos() {
  const cuerpo = document.getElementById("tabla-turnos");
  cuerpo.innerHTML = "";

  const ordenados = [...turnos].sort((a, b) => {
    if (a.prioridad !== b.prioridad) return a.prioridad - b.prioridad;
    return new Date(a.timestamp) - new Date(b.timestamp);
  });

  for (const turno of ordenados) {
    const fila = document.createElement("tr");
    fila.innerHTML = `
      <td>${turno.patient_id}</td>
      <td>${turno.name}</td>
      <td>${nombrePrioridad(turno.prioridad)}</td>
      <td>${new Date(turno.timestamp).toLocaleTimeString()}</td>
    `;
    cuerpo.appendChild(fila);
  }
}

function nombrePrioridad(p) {
  switch (p) {
    case 1: return "Crítico";
    case 2: return "Urgente";
    case 3: return "Regular";
    default: return "-";
  }
}

function logout() {
  localStorage.removeItem("usuarioLogueado");
  location.href = "index.html";
}

mostrarTurnos();
