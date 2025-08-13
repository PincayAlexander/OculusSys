// ====================
// Página de Notificaciones
// ====================

async function cargarTodasNotificaciones() {
  try {
    const res = await fetch('/app/notificaciones/get_user_notification/');
    if (!res.ok) throw new Error("Error al obtener notificaciones");
    const data = await res.json();

    renderResumen(data.notificaciones);
  } catch (err) {
    console.error(err);
  }
}

function renderResumen(notificaciones) {
  const resumen = document.getElementById('notifResumen');
  resumen.innerHTML = '';

  notificaciones.forEach(notif => {
    let icono = getIcono(notif.tipo);
    const fecha = formatFecha(notif.fecha);

    const item = document.createElement('div');
    item.classList.add('notificacion__item');
    if (notif.leido) item.classList.add('notificacion--leida');

    item.innerHTML = `
      <div class="notificacion__resumen--content">
        <div class="notificacion__resumen--titulo">${icono} ${notif.titulo}</div>
        <div class="notificacion__resumen--fecha">${fecha}</div>
      </div>
      ${notif.leido
        ? `<button class="btn__notif__noLeido" title="Marcar como no leído" onclick="markAsUnreadDetalle(${notif.idNotificacion})">\u{1F441}\u{200D}\u{1F5E8}</button>`
        : `<button class="btn__notif__leido" title="Marcar como leído" onclick="markAsReadDetalle(${notif.idNotificacion})">✔</button>`}
`;

    // Click para mostrar detalle específico
    item.addEventListener('click', () => mostrarDetalleUnico(notif));

    resumen.appendChild(item);
  });
}

function markAsUnreadDetalle(id) {
  fetch(`/app/notificaciones/notificaciones/${id}/no-leido`, { method: 'POST' })
    .then(res => {
      if (res.status === 204) {
        cargarTodasNotificaciones();
        if (notificacionActual && notificacionActual.idNotificacion === id) {
          notificacionActual.leido = false;
          mostrarDetalleUnico(notificacionActual);
        }
        cargarNotificaciones();
      }
    });
}

let notificacionActual = null;

function mostrarDetalleUnico(notif) {
  notificacionActual = notif;
  const detalle = document.getElementById('notifDetalle');
  detalle.innerHTML = '';
  detalle.style.overflowY = 'auto';

  const fecha = formatFecha(notif.fecha);

  const item = document.createElement('div');
  item.classList.add('notif-detalle-item');

  if (notif.leido) item.classList.add('notificacion--leida');

  item.innerHTML = `
    <div class="notificaciones__detalle--header">
      <h3>${notif.titulo}</h3>
      <div class="header-buttons">
        ${!notif.leido
      ? `<button class="btn__notif__leido" onclick="markAsReadDetalle(${notif.idNotificacion})" title="Marcar como leído">✔ Marcar como leido</button>`
      : `<button class="btn__notif__noLeido" onclick="markAsUnreadDetalle(${notif.idNotificacion})" title="Marcar como no leído">\u{1F441}\u{200D}\u{1F5E8} Marcar como no leido</button>`}
        <button class="btn__notif__borrar" onclick="deleteNotificacion(${notif.idNotificacion})" title="Borrar">
          <img src="/static/image/icons/delete.svg" alt="Borrar" />
           Borrar Notificación
        </button>
      </div>
    </div>
    <div class="notificaciones__detalle--texto">
      <div><strong>ID:</strong> ${notif.idNotificacion}</div>
      <div><strong>Mensaje:</strong> ${notif.mensaje}</div>
      <div><strong>Tipo:</strong> ${notif.tipo}</div>
      <div class="contenido-resaltado" style="margin-top: 2rem;"><strong>Fecha de registro:</strong> ${fecha}</div>
      <div class="contenido-resaltado"><strong></strong> ${notif.leido ? 'Leído' : 'No Leído'}</div>
    </div>
  `;

  detalle.appendChild(item);
}

function markAsReadDetalle(id) {
  fetch(`/app/notificaciones/notificaciones/${id}/leido`, { method: 'POST' })
    .then(res => {
      if (res.status === 204) {
        cargarTodasNotificaciones();
        if (notificacionActual && notificacionActual.idNotificacion === id) {
          notificacionActual.leido = true;
          mostrarDetalleUnico(notificacionActual);
        }
        cargarNotificaciones();
      }
    });
}

function deleteNotificacion(id) {
  if (!confirm("¿Seguro que quieres eliminar esta notificación?")) return;
  fetch(`/app/notificaciones/notificaciones/${id}/delete`, { method: 'DELETE' })
    .then(res => {
      if (res.status === 204) {
        cargarTodasNotificaciones();
        cargarNotificaciones();
      }
    });
}

document.addEventListener('DOMContentLoaded', () => {
  cargarTodasNotificaciones();
  cargarNotificaciones();
});
