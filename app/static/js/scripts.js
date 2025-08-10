document.addEventListener('DOMContentLoaded', () => {
  // Cargar SVGs iniciales
  const svgContainers = document.querySelectorAll('.svg-inline[data-src]');

  svgContainers.forEach(container => {
    loadSVG(container);

    // Si es un toggle de contraseña, añadir los event listeners
    if (container.classList.contains('password__toggle')) {
      setupPasswordToggle(container);
    }
  });

  // FLASH MESSAGES
  if (Array.isArray(window.flaskMessages)) {
    window.flaskMessages.forEach(([category, message]) => {
      console.log(message);
      mostrarFlashMensaje(message, category);
    });
  }

  // Selecciona todos los dropdowns
  const dropdowns = document.querySelectorAll(".dropdown");

  dropdowns.forEach(dropdown => {
    const toggle = dropdown.querySelector(".dropdown__toggle");
    const menu = dropdown.querySelector(".dropdown__menu");

    toggle.addEventListener("click", (e) => {
      e.stopPropagation(); // evita que se cierre inmediatamente

      // Cierra otros dropdowns abiertos
      document.querySelectorAll(".dropdown__menu").forEach(m => {
        if (m !== menu) {
          m.classList.remove("show");
        }
      });

      // Alternar visibilidad del dropdown actual
      menu.classList.toggle("show");
    });
  });

  // Cierra dropdowns si haces clic fuera
  document.addEventListener("click", () => {
    document.querySelectorAll(".dropdown__menu").forEach(menu => {
      menu.classList.remove("show");
    });
  });

});

// Función para cargar SVGs
function loadSVG(container) {
  const src = container.getAttribute('data-src');
  if (!src) return;

  fetch(src)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.text();
    })
    .then(svg => {
      container.innerHTML = svg;
      container.classList.add('svg-loaded');
    })
    .catch(error => {
      console.error('Error al cargar el SVG:', src, error);
    });
}

// Configurar el toggle de contraseña
function setupPasswordToggle(toggle) {
  // Guardar las rutas base de los iconos
  toggle.setAttribute('data-icon-off', toggle.getAttribute('data-src'));
  toggle.setAttribute('data-icon-on', toggle.getAttribute('data-src').replace('visibility_off.svg', 'visibility_on.svg'));

  // Manejar click
  toggle.addEventListener('click', function () {
    const input = this.previousElementSibling.previousElementSibling;
    togglePasswordVisibility(input, this);
  });

  // Manejar tecla Enter/Espacio para accesibilidad
  toggle.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      const input = this.previousElementSibling.previousElementSibling;
      togglePasswordVisibility(input, this);
    }
  });
}

// Alternar visibilidad de contraseña
function togglePasswordVisibility(input, toggle) {
  const isPassword = input.type === 'password';
  input.type = isPassword ? 'text' : 'password';
  toggle.classList.toggle('active', !isPassword);

  // Cambiar entre SVG específicos usando las rutas guardadas
  const newSrc = isPassword ? toggle.getAttribute('data-icon-on') : toggle.getAttribute('data-icon-off');
  toggle.setAttribute('data-src', newSrc);

  // Actualizar accesibilidad
  toggle.setAttribute('aria-label', isPassword ? 'Ocultar contraseña' : 'Mostrar contraseña');

  // Recargar el SVG
  loadSVG(toggle);
}

// Funcion para mostrar mensajes flash
function mostrarFlashMensaje(mensaje, categoria="info", duracion = 4000) {
  const flashContainer = document.getElementById("flash-message");
  if (!flashContainer) return;

  const flashDiv = document.createElement("div");
  flashDiv.classList.add("flash", categoria);
  flashDiv.textContent = mensaje;

  // Crear el botón de cierre manual
  const closeButton = document.createElement("button");
  closeButton.setAttribute("type", "button");
  closeButton.classList.add("close");
  closeButton.innerHTML = "&times;";
  closeButton.onclick = function () {
    cerrarAlert(closeButton);
  };

  // Agregar el botón al div de alerta
  flashDiv.appendChild(closeButton);

  // Agregar el mensaje al contenedor
  flashContainer.appendChild(flashDiv);

  // Remover automáticamente después del tiempo indicado
  setTimeout(() => {
    flashDiv.remove();
  }, duracion);
}

function cerrarAlert(boton) {
  const alerta = boton.closest('.flash');
  if (alerta) {
    alerta.remove();
  }
}
