from flask import Blueprint, render_template, redirect, url_for, session, jsonify

inicio_bp = Blueprint('inicio', __name__, template_folder='app/templates')

# --- Rutas de autenticación ---
@inicio_bp.route('/inicio', methods=['GET'])
def menu_inicio(): 
    if 'userID' in session:
        return render_template('inicio.html', userID=session['userID'])
    return redirect(url_for('auth.mostrar_login'))