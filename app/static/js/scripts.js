// Cache global para los SVGs
const svgCache = {};

// Precarga un SVG y guarda en cache
async function precargarSVG(nombre, url) {
  if (svgCache[nombre]) return svgCache[nombre];
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Error cargando SVG ${nombre}: ${res.status}`);
    const svgText = await res.text();
    svgCache[nombre] = svgText;
    return svgText;
  } catch (e) {
    console.error(e);
    return null;
  }
}

async function precargarTodosSVG() {
  const nombres = [
    'account',  'ajuste', 'ayuda', 'calendar', 'camara', 'cerrar',
    'delete', 'deteccion', 'edit', 'error', 'exportar', 'filter',
    'Facebook', 'Google', 'inicio', 'logout', 'notifications',
    'password', 'reporte', 'search', 'tasks', 'user', 'video', 
    'visibility_off', 'visibility_on', 'warning', 'ampliar',
    'captura', 'mas', 'menos', 'añadir'
  ];
  const basePath = '/static/image/icons/';

  await Promise.all([
    ...nombres.map(nombre => precargarSVG(nombre, `${basePath}${nombre}.svg`)),
    precargarSVG('logo', '/static/image/logo.svg')
  ]);

}


async function insertarSVG(nombre, contenedorSelector) {
  const svgText = svgCache[nombre];
  if (!svgText) {
    console.warn(`SVG '${nombre}' no precargado`);
    return;
  }
  const contenedor = typeof contenedorSelector === 'string'
    ? document.querySelector(contenedorSelector)
    : contenedorSelector;

  if (!contenedor) {
    console.warn(`Contenedor no encontrado: ${contenedorSelector}`);
    return;
  }

  contenedor.innerHTML = svgText;
}


// Insertar SVG de cache en el contenedor toggle
function loadSVG(toggle) {
  const src = toggle.getAttribute('data-src-name');
  if (!src) return;

  const svg = svgCache[src];
  if (svg) {
    toggle.innerHTML = svg;
    toggle.classList.add('svg-loaded');
  } else {
    toggle.innerHTML = '';
  }
}

// Setup toggle
function setupPasswordToggle(toggle) {
  // Guardar los nombres clave de los iconos, no la ruta completa
  const iconOff = 'visibility_off';
  const iconOn = 'visibility_on';

  toggle.setAttribute('data-icon-off', iconOff);
  toggle.setAttribute('data-icon-on', iconOn);

  // Inicializar atributo para el svg que debe mostrar ahora (off al inicio)
  toggle.setAttribute('data-src-name', iconOff);
  loadSVG(toggle);

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

// Alternar visibilidad de contraseña con cache de svg
function togglePasswordVisibility(input, toggle) {
  const isPassword = input.type === 'password';
  input.type = isPassword ? 'text' : 'password';
  toggle.classList.toggle('active', !isPassword);

  // Cambiar entre nombres de iconos
  const newIcon = isPassword ? toggle.getAttribute('data-icon-on') : toggle.getAttribute('data-icon-off');
  toggle.setAttribute('data-src-name', newIcon);

  // Actualizar accesibilidad
  toggle.setAttribute('aria-label', isPassword ? 'Ocultar contraseña' : 'Mostrar contraseña');

  // Recargar el SVG desde cache
  loadSVG(toggle);
}



// Funcion para mostrar mensajes flash
function mostrarFlashMensaje(mensaje, categoria = "info", duracion = 4000) {
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

async function cargarNotificaciones() {
  try {
    const res = await fetch('/app/notificaciones/get_user_notification/?limit=10');
    if (!res.ok) throw new Error("Error al obtener notificaciones");
    const data = await res.json();

    // data.notificaciones -> las últimas 10
    // data.total_no_leidas -> conteo real de no leídas

    const badge = document.getElementById('notifBadge');
    if (badge) {
      if (data.total_no_leidas > 0) {
        badge.textContent = data.total_no_leidas;
        badge.style.display = 'inline';
      } else {
        badge.style.display = 'none';
      }
    }

    const menu = document.querySelector('.dropdown__menu--notifications');
    if (!menu) return;

    menu.innerHTML = ''; // limpiar contenido anterior

    data.notificaciones.forEach(notif => {
      const icono = getIcono(notif.tipo);
      const fecha = formatFecha(notif.fecha);

      const item = document.createElement('div');
      item.classList.add('dropdown__item', 'dropdown__item--notification');
      if (notif.leido) item.classList.add('notificacion--leida');

      item.innerHTML = `
        <div class="notif__content">
          <div class="notif__title">${icono} ${notif.titulo}</div>
          <div class="notif__fecha">${fecha}</div>
        </div>
        ${!notif.leido ? `<button class="notif__leido-btn" title="Marcar como leído" onclick="markAsRead(${notif.idNotificacion})">✔</button>` : ''}`;

      menu.appendChild(item);
    });

  } catch (err) {
    console.error(err);
  }
}


function markAsRead(id) {
  fetch(`/app/notificaciones/notificaciones/${id}/leido`, { method: 'POST' })
    .then(res => {
      if (res.status === 204) {
        const notifElem = document.querySelector(`button[onclick="markAsRead(${id})"]`).closest('.dropdown__item');
        notifElem.classList.add('notificacion--leida');
        const btn = notifElem.querySelector('.notif__leido-btn');
        if (btn) btn.remove();

        cargarNotificaciones();
      }
    });
}

function markAllAsRead() {
  fetch(`/app/notificaciones/notificaciones/all/leido`, { method: 'POST' })
    .then(res => {
      if (res.status === 204) {
        document.querySelectorAll('.dropdown__item--notification').forEach(el => {
          el.classList.add('notificacion--leida');
          const btn = el.querySelector('.notif__leido-btn');
          if (btn) btn.remove();
        });

        cargarNotificaciones();
      }
    });

}

function getIcono(tipo) {
  switch (tipo) {
    case 'info': return '🔔';
    case 'warning': return '📊';
    case 'error': return '❓';
    case 'success': return '✅';
    default: return '📌';
  }
}

function formatFecha(fechaStr) {
  return new Date(fechaStr).toLocaleString('es-EC', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
}




document.addEventListener('DOMContentLoaded', async () => {
  // 1. Precargar todos los SVGs que definiste
  await precargarTodosSVG();

  // 2. Insertar en todos los contenedores con clase "svg-src" el SVG cacheado según su data-src
  const svgContainers = document.querySelectorAll('.svg-src[data-src]');
  svgContainers.forEach(container => {
    const nombreSVG = container.getAttribute('data-src');
    if (nombreSVG) {
      insertarSVG(nombreSVG, container);
    }
  });

  // 3. Inicializar toggles de contraseña
  document.querySelectorAll('.password__toggle').forEach(toggle => {
    setupPasswordToggle(toggle);
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

  // Cargar notificaciones
  cargarNotificaciones();

  const notifButton = document.querySelector('.nav__notifications-button');
  if (notifButton) {
    notifButton.addEventListener('click', cargarNotificaciones);
  }

});