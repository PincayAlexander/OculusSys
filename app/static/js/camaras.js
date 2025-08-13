let camaraActiva = null;

async function cargarCamaras() {
  const res = await fetch('/app/camara/listar_camara');
  const data = await res.json();
  const container = document.querySelector('#listaCamaras');
  container.innerHTML = '';

  data.forEach(c => {
    const card = document.createElement('div');
    card.classList.add('camara__item');
    card.innerHTML = `
      
      <div class="camara__item--header">
        <div class="svg-src" data-src="video"></div>
        <h4>${c.nombre}</h4>    
      </div>
      <img class camara__item--video id="camaraImg${c.id}" src="${c.url}/video" alt="Cámara ${c.nombre}">
      <div class="item__btns">
        <button class="btn btn__primary" onclick="abrirModalVistaCamara('${c.url}', ${c.id})">
        <div class="svg-src" data-src="ampliar"></div>
        Ampliar
        </button>
      </div>
    `;
    container.appendChild(card);
  });

  container.querySelectorAll('.svg-src[data-src]').forEach(el => {
    insertarSVG(el.dataset.src, el);
  });
}

function abrirModalVistaCamara(url, idCamara) {
  camaraActiva = idCamara; // Guardar ID de cámara activa
  let modal = document.getElementById('modalVistaCamara');

  if (!modal) {
    // Crear el modal y agregar contenido
    modal = document.createElement('div');
    modal.id = 'modalVistaCamara';
    modal.className = 'modal__background';
    modal.style.display = 'flex';
    modal.setAttribute('aria-hidden', 'false');

    modal.innerHTML = `
      <div class="modal modal--large modal__ampliarcamara">
        <button class="modal__close" onclick="cerrarModalCamara('modalVistaCamara')">
          <div class="svg-src" data-src="cerrar"></div>
        </button>
        <img id="videoAmpliado" width="700px" alt="Vista ampliada" style="border-radius: 5px; border: 1px solid #ccc;">
        <div class="modal__footer">
          <button class="btn btn__primary" onclick="capturarFotoImg(${camaraActiva}, '${url}')">
            <div class="svg-src" data-src="captura"></div>
            Capturar</button>
          <button class="btn btn__secondary" onclick="enviarControl('zoomIn')">
            <div class="svg-src" data-src="mas"></div>
            Zoom
          </button>
          <button class="btn btn__secondary" onclick="enviarControl('zoomOut')">
            <div class="svg-src" data-src="menos"></div>
            Zoom</button>
        </div>
      </div>
    `;

    document.body.appendChild(modal);
  } else {
    // Si ya existe, solo mostrar
    modal.style.display = 'flex';
    modal.setAttribute('aria-hidden', 'false');
  }
  // Actualizar imagen del modal
  const img = document.getElementById('videoAmpliado');
  img.src = `${url}/video`;

  modal.querySelectorAll('.svg-src[data-src]').forEach(el => {
    insertarSVG(el.dataset.src, el);
  });
}


function cerrarModalCamara(id) {
  const modal = document.getElementById(id);
  if (modal) {
    modal.remove();
  }
}

function enviarControl(accion) {
  if (!camaraActiva) {
    console.error('No hay cámara activa');
    return;
  }
  fetch(`/app/camara/control_camara/${camaraActiva}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ accion })
  })
    .then(res => res.json())
    .then(data => {
      if (data.status !== 'ok') {
        console.error('Error en el control de cámara: ' + (data.error || 'Desconocido'));
      }
    })
    .catch(e => console.error('Error en la comunicación con la cámara: ' + e));
}

async function capturarFotoImg(idCamara, urlCamara) {
  try {
    // Hacer fetch directo a la imagen shot.jpg de la cámara IP Webcam
    const res = await fetch(`${urlCamara}/shot.jpg`, { cache: "no-cache" });
    if (!res.ok) throw new Error("No se pudo obtener la imagen");

    // Obtener blob (imagen binaria)
    const blob = await res.blob();

    // Convertir Blob a base64 para enviar por JSON (opcional, o usa FormData)
    const base64 = await blobToBase64(blob);

    // Enviar la imagen base64 a tu backend Flask
    await fetch(`/app/camara/guardar_foto/${idCamara}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ imagen: base64 })
    });

    mostrarFlashMensaje('Foto capturada y guardada exitosamente', 'success');
  } catch (error) {
    console.error("Error al capturar la foto: "+ error);
    mostrarFlashMensaje('Error al capturar la foto', 'error');
  }
}

function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result);  // data:image/jpeg;base64,...
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}


document.addEventListener('DOMContentLoaded', cargarCamaras);
