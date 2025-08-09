from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from sqlalchemy.exc import SQLAlchemyError
from app.database import db

live_bp = Blueprint('camara', __name__, template_folder='app/templates')

# --- Rutas de autenticación ---
@live_bp.route('/Live', methods=['GET'])
def vista_camara():
    if 'userID' in session:
        return render_template('Live.html')
    return redirect(url_for('auth.mostrar_login'))