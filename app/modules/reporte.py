from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from sqlalchemy.exc import SQLAlchemyError
from app.database import db

reporte_bp = Blueprint('reporte', __name__, template_folder='app/templates')

@reporte_bp.route('/document', methods=['GET'])
def vista_reporte():
    if 'userID' in session:
        return render_template('reporte.html')
    return redirect(url_for('auth.mostrar_login'))


Detecciones_bp = Blueprint('detecciones', __name__, template_folder='app/templates')

@Detecciones_bp.route('/document', methods=['GET'])
def vista_detecciones():
    if 'userID' in session:
        return render_template('deteccion.html')
    return redirect(url_for('auth.mostrar_login'))