const dataPlagas = {
  1: {
    titulo: "Broca del café",
    ubicacion: {
      provincia: "Manabí",
      finca: "Los Ajos",
      plantacion: "Sección de Café 001",
      bloque: "Bloque B",
      coordenadas: "-1.223, -91.03"
    },
    plaga: {
      nombre: "Broca del café",
      cientifico: "Hypothenemus hampei",
      descripcion: "Insecto que perfora el grano de café y afecta la calidad de la cosecha.",
      fecha: "2025-08-13",
      hora: "09:30 AM"
    },
    afectacion: [
      "Perforación de granos visibles.",
      "Presencia de galerías internas en semillas.",
      "Reducción de rendimiento de la cosecha."
    ],
    imagen: "broca.jpg"
  },
  2: {
    titulo: "Roya del café",
    ubicacion: {
      provincia: "Manabí",
      finca: "Los Ajos",
      plantacion: "Sección de Café 002",
      bloque: "Bloque A",
      coordenadas: "-1.22445, -91.02"
    },
    plaga: {
      nombre: "Roya del café",
      cientifico: "Hemileia vastatrix",
      descripcion: "Hongo que provoca manchas amarillas en hojas y reduce la fotosíntesis.",
      fecha: "2025-08-13",
      hora: "09:40 AM"
    },
    afectacion: [
      "Manchas amarillas en el haz de las hojas.",
      "Bordes anaranjados en infecciones avanzadas.",
      "Pérdida progresiva de hojas y debilitamiento de plantas."
    ],
    imagen: "roya.png"
  },
  3: {
    titulo: "Minador de hojas",
    ubicacion: {
      provincia: "Manabí",
      finca: "La Fortuna",
      plantacion: "Sección de Café 003",
      bloque: "Bloque C",
      coordenadas: "-1.225, -91.01"
    },
    plaga: {
      nombre: "Minador de hojas",
      cientifico: "Leucoptera coffeella",
      descripcion: "Insecto que excava galerías dentro de las hojas.",
      fecha: "2025-08-13",
      hora: "10:00 AM"
    },
    afectacion: [
      "Hojas con galerías lineales.",
      "Pérdida de capacidad fotosintética.",
      "Daño progresivo si no se controla."
    ],
    imagen: "minador.png"
  },
  4: {
    titulo: "Ojo de gallo",
    ubicacion: {
      provincia: "Manabí",
      finca: "La Fortuna",
      plantacion: "Sección de Café 004",
      bloque: "Bloque D",
      coordenadas: "-1.226, -91.00"
    },
    plaga: {
      nombre: "Ojo de gallo",
      cientifico: "Cercospora coffeicola",
      descripcion: "Hongo que provoca manchas circulares en hojas y reduce la producción.",
      fecha: "2025-08-13",
      hora: "10:15 AM"
    },
    afectacion: [
      "Manchas circulares con centro gris.",
      "Reducción de la superficie foliar activa.",
      "Debilitamiento de brotes jóvenes."
    ],
    imagen: "ojo_gallo.png"
  },
  5: {
    titulo: "Mal de hilachas",
    ubicacion: {
      provincia: "Manabí",
      finca: "Los Ajos",
      plantacion: "Sección de Café 005",
      bloque: "Bloque E",
      coordenadas: "-1.227, -91.04"
    },
    plaga: {
      nombre: "Mal de hilachas",
      cientifico: "Physalospora theae",
      descripcion: "Enfermedad que provoca pérdida de follaje y debilitamiento de la planta.",
      fecha: "2025-08-13",
      hora: "10:30 AM"
    },
    afectacion: [
      "Pérdida de hojas jóvenes.",
      "Debilitamiento de ramas y brotes.",
      "Reducción de la capacidad de producción de la planta."
    ],
    imagen: "hilachas.png"
  }
};

// Función para renderizar las cards dinámicamente
document.querySelectorAll(".plaga__item").forEach(item => {
  item.addEventListener("click", () => {
    // Resalta el item activo
    document.querySelectorAll(".plaga__item").forEach(el => el.classList.remove("active"));
    item.classList.add("active");

    const id = item.getAttribute("data-id");
    const detalle = dataPlagas[id];

    if (detalle) {
      // Generar las tres cards
      document.getElementById("descripcion-container").innerHTML = `
        <div class="side__card">
          <!-- Card 1: Ubicación -->
          <div class="card">
            <h5 style="font-family: 'Oswald', sans-serif;">Ubicación de la detección</h5>
            <div class="card__contenido">
              <div><strong>Provincia:</strong> ${detalle.ubicacion.provincia}</div>
              <div><strong>Finca:</strong> ${detalle.ubicacion.finca}</div>
              <div><strong>Plantación:</strong> ${detalle.ubicacion.plantacion}</div>
              <div><strong>Bloque:</strong> ${detalle.ubicacion.bloque}</div>
              <div><strong>Coordenadas:</strong> ${detalle.ubicacion.coordenadas}</div>
            </div>
          </div>

          <!-- Card 2: Plaga detectada -->
          <div class="card">
            <h5 style="font-family: 'Oswald', sans-serif;">Plaga detectada</h5>
            <div class="card__contenido">
              <div><strong>Nombre común:</strong> ${detalle.plaga.nombre}</div>
              <div><strong>Nombre científico:</strong> ${detalle.plaga.cientifico}</div>
              <div><strong>Descripción:</strong> ${detalle.plaga.descripcion}</div>
              <div><strong>Fecha de detección:</strong> ${detalle.plaga.fecha}</div>
              <div><strong>Hora de detección:</strong> ${detalle.plaga.hora}</div>
            </div>
          </div>

          <!-- Card 3: Grado de afectación -->
          <div class="card">
            <h5 style="font-family: 'Oswald', sans-serif;">Grado de afectación</h5>
            <ul class="format__lista">
              ${detalle.afectacion.map(item => `<li>${item}</li>`).join('')}
            </ul>
          </div>
        </div>
      `;

      // Imagen de la plaga
      document.getElementById("imagen-container").innerHTML = `
        <div class="imagen__header">
          <h5 style="font-family: 'Oswald', sans-serif;">Evidencia de ${detalle.titulo}</h5>
        </div>
        <img src="/static/image/other/${detalle.imagen}" alt="${detalle.titulo}">
      `;
    }
  });
});
