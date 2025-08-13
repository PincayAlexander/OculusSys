// modal.js
function abrirModal(modalId) {
  const modalBg = document.querySelector(`#${modalId}`);
  if (!modalBg) return;
  modalBg.style.display = "flex";
  modalBg.setAttribute("aria-hidden", "false");

  // Foco en primer input
  const primerInput = modalBg.querySelector('input, textarea, select');
  if (primerInput) setTimeout(() => primerInput.focus(), 100);
}

function cerrarModal(modalId) {
  const modalBg = document.querySelector(`#${modalId}`);
  if (!modalBg) return;
  modalBg.style.display = "none";
  modalBg.setAttribute("aria-hidden", "true");

  // Si hay form, lo resetea
  const form = modalBg.querySelector("form");
  if (form) form.reset();
}

// Detecta click fuera del modal para cerrar
document.addEventListener("click", (e) => {
  if (e.target.classList.contains("modal__background")) {
    e.target.style.display = "none";
    e.target.setAttribute("aria-hidden", "true");
  }
});
