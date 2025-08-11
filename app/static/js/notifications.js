async function cargarNotificaciones() {
  try {
    const res = await fetch('/app/notificaciones/get_user_notification/?limit=10');
    if (!res.ok) throw new Error("Error al obtener notificaciones");
    const notificaciones = await res.json();
    const menu = document.querySelector('.dropdown__menu--notifications');
    if (!menu) return;

    menu.innerHTML = ''; // limpiar contenido anterior

    notificaciones.forEach(notif => {
      let icono = '';
      switch (notif.tipo) {
        case 'info': icono = '🔔'; break;
        case 'warning': icono = '📊'; break;
        case 'error': icono = '❓'; break;
        case 'success': icono = '✅'; break;
        default: icono = '📌';
      }

      const fecha = new Date(notif.fecha).toLocaleString('es-EC', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
      });

      const item = document.createElement('div');
      item.classList.add('dropdown__item', 'dropdown__item--notification');
      if (notif.leido) item.classList.add('notificacion--leida');

      item.innerHTML = `
        <div class="notif__content">
          <div class="notif__title">${icono} ${notif.titulo}</div>
          <div class="notif__fecha">${fecha}</div>
        </div>
        ${!notif.leido ? `<button class="notif__leido-btn" title="Marcar como leído" onclick="markAsRead(${notif.idNotificacion})">✔</button>` : ''}
      `;

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
      }
    });
}

document.addEventListener('DOMContentLoaded', () => {
  const notifButton = document.querySelector('.nav__notifications-button');
  if (notifButton) {
    notifButton.addEventListener('click', cargarNotificaciones);
  }
});
