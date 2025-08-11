from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app, send_file
from app.utils import login_required, get_current_user, guardar_notificacions
from sqlalchemy.exc import SQLAlchemyError
from app.database import db
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import io
import os

# -------------------------
# RUTAS REPORTES
# -------------------------
reporte_bp = Blueprint('reporte', __name__, template_folder='app/templates')

@reporte_bp.route('/document', methods=['GET'])
def vista_reporte():
    if 'userID' in session:
        return render_template('reporte.html')
    return redirect(url_for('auth.mostrar_login'))



# -------------------------
# RUTAS DETECCIONES
# -------------------------
detecciones_bp = Blueprint('deteccion', __name__, template_folder='app/templates')

@detecciones_bp.route('/detection', methods=['GET'])
@login_required
def vista_detecciones():
    return render_template('deteccion.html')



"""
@report_bp.route('/generar_pdf', methods=['POST', 'GET'])
def generar_pdf_route():
    tipo = request.args.get('tipo', 'all')
    nivel = request.args.get('nivel', 'all')
    paralelo = request.args.get('paralelo', 'all')

    filtros = {}
    if nivel != 'all':
        filtros['nivel'] = nivel
    if paralelo != 'all':
        filtros['paralelo'] = paralelo
        
    try:
        pdf_response = generar_pdf(tipo, filtros)
        return send_file(
            pdf_response, 
            as_attachment=False, 
            download_name=f"{tipo}_reporte.pdf", 
            mimetype='application/pdf'
        )
        
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('inicio.menu'))
    
    except Exception as e:
        current_app.logger.error(f"Error generando PDF: {str(e)}")
        flash('Ocurrió un error interno al generar el reporte', 'danger')
        return redirect(url_for('inicio.menu'))


def generar_pdf(tipo, filtros):
    if tipo not in ['matricula', 'calificaciones']:
        raise ValueError('Tipo de reporte inválido. Debe ser "matricula" o "calificaciones"')
    
    # Crear buffer para el PDF
    buffer = io.BytesIO()
    size = A4 if tipo == 'matricula' else landscape(A4)
    doc = SimpleDocTemplate(buffer, pagesize=size, rightMargin=40, leftMargin=40, topMargin=80, bottomMargin=60)
    styles = getSampleStyleSheet()
    elementos = []

    estilo_info = styles['Normal']
    estilo_info.spaceBefore = 12
    estilo_info.spaceAfter = 12
    estilo_info.leftIndent = 20

    # Cuerpo del documento según tipo
    if tipo == 'matricula':
        datos = obtener_matriculas(filtros)
        if not datos:
            raise ValueError(f'No se encontraron matrículas para nivel: {filtros.get("nivel", "todos")}, paralelo: {filtros.get("paralelo", "todos")}')

        for i, estudiante in enumerate(datos):
            elementos.append(Spacer(1, 24))
            info = f""
                <b>Estudiante:</b> {estudiante['estudiante']}<br/>
                <b>Cédula:</b> {estudiante['cedula']}<br/>
                <b>Nivel:</b> {estudiante['nivel']}<br/>
                <b>Paralelo:</b> {estudiante['paralelo']}<br/>
                <b>Periodo:</b> {estudiante['periodo']} ({estudiante['duracion_periodo']})<br/>
                <b>Fecha Matrícula:</b> {estudiante['fecha_matricula']}<br/>
            ""
            elementos.append(Paragraph(info, styles['Normal']))
            elementos.append(Spacer(1, 24))
            elementos += generar_tabla_asignaciones_matricula(estudiante['asignaciones'], styles)
            
            elementos.append(Spacer(1, 34))
            nota_paragraph = Paragraph(f"<b>Nota Anual:</b> {estudiante['promedio_anual']:.2f}", styles['Normal'])
            nota_table = Table([[nota_paragraph]], colWidths=[400])
            nota_table.setStyle([('ALIGN', (0, 0), (-1, -1), 'RIGHT')])
            elementos.append(nota_table)

            if i < len(datos) - 1:
                elementos.append(PageBreak())


    elif tipo == 'calificaciones':
        datos = obtener_calificaciones(filtros)
        if not datos:
            raise ValueError(f'No se encontraron calificaciones para nivel: {filtros.get("nivel", "todos")}, paralelo: {filtros.get("paralelo", "todos")}')

        for i, estudiante in enumerate(datos):
            elementos.append(Spacer(1, 24))
            info = f""
                <b>Estudiante:</b> {estudiante['apellido']} {estudiante['nombre']} <br/>
                <b>Cédula:</b> {estudiante['cedula']}<br/>
                <b>Nivel:</b> {estudiante['nivel']}<br/>
                <b>Paralelo:</b> {estudiante['paralelo']}<br/>
            ""
            elementos.append(Paragraph(info, styles['Normal']))
            elementos.append(Spacer(1, 18))
            elementos += generar_tabla_calificaciones_por_estudiante(estudiante, styles)
            elementos.append(Spacer(1, 36))
            
            if i < len(datos) - 1:
                elementos.append(PageBreak())

    doc.build(elementos, onFirstPage=encabezado_y_footer, onLaterPages=encabezado_y_footer)
    buffer.seek(0)
    return buffer

def encabezado_y_footer(canvas, doc):
    agregar_encabezado(canvas, doc)
    agregar_footer(canvas, doc)

def agregar_encabezado(canvas, doc):
    canvas.saveState()
    
    try:
        logo_path = os.path.join(current_app.root_path, 'static', 'image', 'logo64px.png')
        canvas.drawImage(
            logo_path,
            x=doc.pagesize[0] - 60,
            y=doc.pagesize[1] - 80,
            width=40,
            height=40,
            preserveAspectRatio=True,
            mask='auto'
        )
    except Exception as e:
        print(f"Error al cargar logo: {e}")

    canvas.setFont('Helvetica-Bold', 14)
    titulo = current_app.config.get('TIPO_REPORTE', 'Reporte')
    canvas.drawCentredString(doc.pagesize[0] / 2, doc.pagesize[1] - 90, "DigiNote - Reporte")

    canvas.setStrokeColor(colors.lightgrey)
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, doc.pagesize[1] - 100, doc.pagesize[0] - doc.rightMargin, doc.pagesize[1] - 100)

    canvas.restoreState()
    
    
def agregar_footer(canvas, doc):
    canvas.saveState()

    # Fecha
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M')
    canvas.setFont('Helvetica', 8)
    canvas.drawString(doc.leftMargin, 30, f"Generado el: {fecha}")

    # Número de página
    canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, 30, f"Página {doc.page}")

    canvas.restoreState()
    

"""