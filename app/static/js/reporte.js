const deteccionesEl = document.getElementById("detecciones");
const controladoEl = document.getElementById("controlado");

const dataSets = {
  "enero-julio": {
    labels: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul"],
    detecciones: [400, 370, 480, 420, 410, 450, 430],
    controlado: [250, 260, 280, 300, 310, 320, 340],
    tipos: [70, 25, 15, 10],
  },
  "marzo-junio": {
    labels: ["Mar", "Abr", "May", "Jun"],
    detecciones: [480, 420, 410, 450],
    controlado: [280, 300, 310, 320],
    tipos: [60, 30, 20, 10],
  },
  "mayo-julio": {
    labels: ["May", "Jun", "Jul"],
    detecciones: [410, 450, 430],
    controlado: [310, 320, 340],
    tipos: [50, 35, 25, 5],
  }
};

const ctxLine = document.getElementById("lineChart").getContext("2d");
const ctxGauge1 = document.getElementById("gaugeControlado").getContext("2d");
const ctxGauge2 = document.getElementById("gaugeSinControlar").getContext("2d");
const ctxBar = document.getElementById("barChart").getContext("2d");

const lineChart = new Chart(ctxLine, {
  type: "line",
  data: {
    labels: [],
    datasets: [
      {
        label: "Detecciones",
        borderColor: "red",
        data: [],
        fill: false,
      },
      {
        label: "Controlado",
        borderColor: "green",
        data: [],
        fill: false,
      },
    ],
  },
});

const gaugeControlado = new Chart(ctxGauge1, {
  type: 'doughnut',
  data: {
    labels: ['Controlado', 'Restante'],
    datasets: [{
      data: [75, 25],
      backgroundColor: ['#4caf50', '#e0e0e0'],
      borderWidth: 0
    }]
  },
  options: {
    cutout: '80%',
    plugins: {
      tooltip: { enabled: false },
      legend: { display: false },
    }
  }
});

const gaugeSinControlar = new Chart(ctxGauge2, {
  type: 'doughnut',
  data: {
    labels: ['Sin Control', 'Controlado'],
    datasets: [{
      data: [25, 75],
      backgroundColor: ['#f44336', '#e0e0e0'],
      borderWidth: 0
    }]
  },
  options: {
    cutout: '80%',
    plugins: {
      tooltip: { enabled: false },
      legend: { display: false },
    }
  }
});

const barChart = new Chart(ctxBar, {
  type: 'bar',
  data: {
    labels: ['La Roya', 'Mildiu', 'Ojo de gallo', 'Mancha de hierro'],
    datasets: [{
      label: 'Detecciones',
      data: [],
      backgroundColor: '#2196f3'
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { display: false }
    }
  }
});

function updateCharts(range) {
  const data = dataSets[range];
  lineChart.data.labels = data.labels;
  lineChart.data.datasets[0].data = data.detecciones;
  lineChart.data.datasets[1].data = data.controlado;
  lineChart.update();

  const totalDetecciones = data.detecciones.reduce((a, b) => a + b, 0);
  const totalControlado = data.controlado.reduce((a, b) => a + b, 0);
  const porcentaje = Math.round((totalControlado / totalDetecciones) * 100);
  const restante = 100 - porcentaje;

  deteccionesEl.textContent = totalDetecciones;
  controladoEl.textContent = totalControlado;

  gaugeControlado.data.datasets[0].data = [porcentaje, restante];
  gaugeSinControlar.data.datasets[0].data = [restante, porcentaje];
  gaugeControlado.update();
  gaugeSinControlar.update();

  barChart.data.datasets[0].data = data.tipos;
  barChart.update();
}

document.getElementById("dateRange").addEventListener("change", (e) => {
  updateCharts(e.target.value);
});

updateCharts("enero-julio");

// --- Lógica para abrir/cerrar el modal de descarga ---
const modal = document.getElementById("modalDescarga");
const abrirModalBtn = document.getElementById("abrirModal");
const cerrarModalBtn = document.getElementById("cerrarModal");
const cancelarBtn = document.getElementById("cancelarDescarga");

abrirModalBtn.onclick = () => modal.style.display = 'block';
cerrarModalBtn.onclick = () => modal.style.display = 'none';
cancelarBtn.onclick = () => modal.style.display = 'none';

window.onclick = function (event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
};

document.querySelectorAll(".formato").forEach(btn => {
  btn.addEventListener("click", () => {
    const formato = btn.classList.contains("ppt") ? "ppt" :
                    btn.classList.contains("pdf") ? "pdf" : null;

    if (!formato) return;

    const nombreArchivo = document.querySelector('#modalDescarga input[type="text"]').value.trim();
    const nombreFinal = nombreArchivo !== "" ? nombreArchivo : "informe";

    // Captura los gráficos en canvas como imágenes
    const charts = [
      { id: "lineChart", titulo: "Gráfico Línea" },
      { id: "gaugeControlado", titulo: "Controlado" },
      { id: "gaugeSinControlar", titulo: "Sin Controlar" },
      { id: "barChart", titulo: "Gráfico Barras" },
    ];

    const capturas = charts.map(({ id, titulo }) => {
      const canvas = document.getElementById(id);
      return {
        titulo,
        dataUrl: canvas.toDataURL("image/png", 1.0),
        width: canvas.width,
        height: canvas.height,
      };
    });

    if (formato === "pdf") {
      const { jsPDF } = window.jspdf;
      const pdf = new jsPDF("p", "pt", "a4");

      let y = 40;
      capturas.forEach(({ titulo, dataUrl }, index) => {
        if (index > 0) pdf.addPage();
        pdf.text(titulo, 40, y);
        pdf.addImage(dataUrl, "PNG", 40, y + 20, 500, 300);
      });

      pdf.save(`${nombreFinal}.pdf`);
    }

    if (formato === "ppt") {
      const pptx = new PptxGenJS();
      capturas.forEach(({ titulo, dataUrl }) => {
        const slide = pptx.addSlide();
        slide.addText(titulo, { x: 0.5, y: 0.3, fontSize: 18 });
        slide.addImage({ data: dataUrl, x: 0.5, y: 1, w: 8 });
      });
      pptx.writeFile({ fileName: `${nombreFinal}.pptx` });
    }

    document.getElementById("modalDescarga").style.display = "none";
  });
});
