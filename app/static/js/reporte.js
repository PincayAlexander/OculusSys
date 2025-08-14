// =========================
// VARIABLES GLOBALES
// =========================
const deteccionesEl = document.getElementById("detecciones");
const controladoEl = document.getElementById("controlado");

// =========================
// DATOS BASE
// =========================
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

// =========================
// CONFIGURACIÓN DE CHARTS
// =========================
const ctxLine = document.getElementById("lineChart").getContext("2d");
const ctxGauge1 = document.getElementById("gaugeControlado").getContext("2d");
const ctxGauge2 = document.getElementById("gaugeSinControlar").getContext("2d");
const ctxBar = document.getElementById("barChart").getContext("2d");

const lineChart = new Chart(ctxLine, {
  type: "line",
  data: {
    labels: [],
    datasets: [
      { label: "Detecciones", borderColor: "red", data: [], fill: false },
      { label: "Controlado", borderColor: "green", data: [], fill: false },
    ]
  },
  options: { responsive: true }
});

const gaugeControlado = new Chart(ctxGauge1, {
  type: 'doughnut',
  data: {
    labels: ['Controlado', 'Restante'],
    datasets: [{ data: [0, 100], backgroundColor: ['#4caf50', '#e0e0e0'], borderWidth: 0 }]
  },
  options: {
    cutout: '80%',
    plugins: { tooltip: { enabled: false }, legend: { display: false } }
  }
});

const gaugeSinControlar = new Chart(ctxGauge2, {
  type: 'doughnut',
  data: {
    labels: ['Sin Control', 'Controlado'],
    datasets: [{ data: [100, 0], backgroundColor: ['#f44336', '#e0e0e0'], borderWidth: 0 }]
  },
  options: {
    cutout: '80%',
    plugins: { tooltip: { enabled: false }, legend: { display: false } }
  }
});

const barChart = new Chart(ctxBar, {
  type: 'bar',
  data: {
    labels: ['La Roya', 'Mildiu', 'Ojo de gallo', 'Mancha de hierro'],
    datasets: [{ label: 'Detecciones', data: [], backgroundColor: '#2196f3' }]
  },
  options: { responsive: true, plugins: { legend: { display: false } } }
});

// =========================
// FUNCIÓN PARA ACTUALIZAR GRÁFICAS
// =========================
function updateCharts(range) {
  const data = dataSets[range];

  // Línea
  lineChart.data.labels = data.labels;
  lineChart.data.datasets[0].data = data.detecciones;
  lineChart.data.datasets[1].data = data.controlado;
  lineChart.update();

  // Totales y porcentajes
  const totalDetecciones = data.detecciones.reduce((a, b) => a + b, 0);
  const totalControlado = data.controlado.reduce((a, b) => a + b, 0);
  const porcentaje = Math.round((totalControlado / totalDetecciones) * 100);
  const restante = 100 - porcentaje;

  deteccionesEl.textContent = totalDetecciones;
  controladoEl.textContent = totalControlado;

  // Gauges
  gaugeControlado.data.datasets[0].data = [porcentaje, restante];
  gaugeSinControlar.data.datasets[0].data = [restante, porcentaje];
  gaugeControlado.update();
  gaugeSinControlar.update();

  // Barras
  barChart.data.datasets[0].data = data.tipos;
  barChart.update();
}

// Detectar cambio en fecha
document.getElementById("dateRange").addEventListener("change", (e) => {
  const valor = e.target.value.toLowerCase();
  let range = "enero-julio";
  if (valor.includes("mar")) range = "marzo-junio";
  if (valor.includes("may")) range = "mayo-julio";
  updateCharts(range);
});

// Inicial
updateCharts("enero-julio");

// =========================
// LÓGICA DEL MODAL DE EXPORTACIÓN
// =========================
(function () {
  const MODAL_ID = document.getElementById("modalDescarga")
    ? "modalDescarga"
    : (document.getElementById("modalExportarArchivo") ? "modalExportarArchivo" : null);

  if (!MODAL_ID) {
    console.warn("No se encontró el modal de exportación.");
  }

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  let formatoSeleccionado = null;

  function limpiarSeleccionFormato() {
    formatoSeleccionado = null;
    $$("#"+MODAL_ID+" .formato").forEach(b => b.classList.remove("activo"));
  }

  // Botón abrir modal
  const btnAbrirExportar = (() => {
    const iconoExportar = $('.options__header .svg-src[data-src="exportar"]');
    return iconoExportar ? iconoExportar.closest("button") : null;
  })();

  if (btnAbrirExportar && MODAL_ID) {
    btnAbrirExportar.addEventListener("click", () => {
      sincronizarRangoFechasAlModal();
      limpiarSeleccionFormato();
      abrirModal(MODAL_ID);
    });
  }

  // Sincronizar fechas
  function sincronizarRangoFechasAlModal() {
    const filtroFecha = document.getElementById("filtroFecha");
    if (!filtroFecha || !MODAL_ID) return;
    const resumen = $("#"+MODAL_ID+" input[name='rangoFechas'], #"+MODAL_ID+" input#rangoResumen");
    if (resumen) resumen.value = filtroFecha.value || "";
  }

  // Selección de formato
  if (MODAL_ID) {
    $$("#"+MODAL_ID+" .formato").forEach(btn => {
      btn.addEventListener("click", () => {
        $$("#"+MODAL_ID+" .formato").forEach(b => b.classList.remove("activo"));
        btn.classList.add("activo");
        formatoSeleccionado = btn.dataset.formato;
      });
    });
  }

  // Exportar
  if (MODAL_ID) {
    const btnExportar = $("#"+MODAL_ID+" .btn.btn__primary.exportar") || $("#btnExportarArchivo");
    if (btnExportar) {
      btnExportar.addEventListener("click", () => {
        const form = $("#formExportarArchivo") || $("#"+MODAL_ID+" form");
        const nombreArchivo = (form.querySelector("[name='nombreArchivo']")?.value || "").trim();
        if (!nombreArchivo) {
          alert("Ingresa un nombre de archivo.");
          return;
        }
        if (!formatoSeleccionado) {
          alert("Selecciona un formato.");
          return;
        }
        const rango = (form.querySelector("[name='rangoFechas']")?.value || "").trim();

        const charts = [
          { id: "lineChart", titulo: "Detecciones vs Controlado" },
          { id: "gaugeControlado", titulo: "% Plagas Controlado" },
          { id: "gaugeSinControlar", titulo: "% Plagas Sin Controlar" },
          { id: "barChart", titulo: "Tipos de Plagas Detectadas" },
        ].map(c => {
          const canvas = document.getElementById(c.id);
          return {
            titulo: c.titulo,
            dataUrl: canvas.toDataURL("image/png", 1.0)
          };
        });

        if (formatoSeleccionado === "pdf") exportarPDF(nombreArchivo, charts, rango);
        if (formatoSeleccionado === "ppt") exportarPPT(nombreArchivo, charts, rango);
        if (formatoSeleccionado === "xls") exportarXLS(nombreArchivo, rango);

        cerrarModal(MODAL_ID);
      });
    }
  }

  function exportarPDF(nombre, capturas, rango) {
    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF("p", "pt", "a4");
    pdf.setFontSize(16);
    pdf.text(`Informe: ${nombre}`, 40, 40);
    if (rango) {
      pdf.setFontSize(11);
      pdf.text(`Rango: ${rango}`, 40, 60);
    }
    capturas.forEach(({ titulo, dataUrl }, index) => {
      if (index > 0) pdf.addPage();
      pdf.setFontSize(12);
      pdf.text(titulo, 40, 80);
      pdf.addImage(dataUrl, "PNG", 40, 100, 500, 300);
    });
    pdf.save(`${nombre}.pdf`);
  }

  function exportarPPT(nombre, capturas, rango) {
    const pptx = new PptxGenJS();
    let slide = pptx.addSlide();
    slide.addText(`Informe: ${nombre}`, { x: 0.5, y: 0.5, fontSize: 24 });
    if (rango) slide.addText(`Rango: ${rango}`, { x: 0.5, y: 1.1, fontSize: 14 });
    capturas.forEach(({ titulo, dataUrl }) => {
      const s = pptx.addSlide();
      s.addText(titulo, { x: 0.5, y: 0.3, fontSize: 18 });
      s.addImage({ data: dataUrl, x: 0.5, y: 1.0, w: 8.5 });
    });
    pptx.writeFile({ fileName: `${nombre}.pptx` });
  }

  function exportarXLS(nombre, rango) {
    const ws = XLSX.utils.aoa_to_sheet([
      ["Informe", nombre],
      ["Rango", rango || ""],
      [],
      ["Métrica", "Valor"],
      ["Ejemplo", 123]
    ]);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Reporte");
    XLSX.writeFile(wb, `${nombre}.xlsx`);
  }
})();
