function abrirModalCambiarContrasena() {

    const modal = document.createElement('div');
    modal.id = 'modalCambiarContrasena';
    modal.className = 'modal__background';
    modal.style.display = 'flex';
    modal.setAttribute('aria-hidden', 'false');

    modal.innerHTML = `
        <div class="modal modal--small modal__contrasenia">
            <button class="modal__close" onclick="cerrarModalCambiarContrasena()">
                <div class="svg-src" data-src="cerrar"></div>
            </button>
            <h4 class="modal__title">Cambiar Contraseña</h4>
            <form id="formCambiarContrasena">
                <div class="modal__group">
                    <input type="password" name="password" id="password" class="modal__input" placeholder=" " required>
                    <label for="password" class="modal__label">Nueva contraseña</label>
                    <div class="svg-src password__toggle" data-src="visibility_off" role="button" tabindex="0"></div>
                </div>
                <div class="modal__group">
                    <input type="password" name="confirm_password" id="confirm_password" class="modal__input" placeholder=" " required>
                    <label for="confirm_password" class="modal__label">Confirmar contraseña</label>
                    <div class="svg-src password__toggle" data-src="visibility_off" role="button" tabindex="0"></div>
                </div>
                <div class="modal__group modal__group--validations">
                    <ul class="modal__list">
                        <li id="length-validation">🔒 Mínimo 8 caracteres</li>
                        <li id="chars-validation">🔠 Al menos 1 mayúscula, 1 minúscula y 1 número</li>
                        <li id="match-validation">✅ Las contraseñas coinciden</li>
                    </ul>
                </div>
                <div class="modal__buttons">
                    <button type="submit" class="btn btn__primary">Actualizar</button>
                </div>
            </form>
        </div>
    `;

    document.body.appendChild(modal);

    // --- Inicializar validaciones usando tus funciones globales ---
    const form = document.getElementById('formCambiarContrasena');
    const passwordInput = form.querySelector('#password');
    const confirmInput = form.querySelector('#confirm_password');
    const lengthValidation = form.querySelector('#length-validation');
    const charsValidation = form.querySelector('#chars-validation');
    const matchValidation = form.querySelector('#match-validation');

    function validarTodoModal() {
        const pwd = passwordInput.value;
        const confirmPwd = confirmInput.value;

        const esLongitudValida = validarLongitud(pwd);
        const esCaracterValido = validarCaracteres(pwd);
        const coincide = validarCoincidencia(pwd, confirmPwd);

        actualizarEstado(esLongitudValida, lengthValidation);
        actualizarEstado(esCaracterValido, charsValidation);
        actualizarEstado(coincide, matchValidation);

        return esLongitudValida && esCaracterValido && coincide;
    }

    passwordInput.addEventListener('input', validarTodoModal);
    confirmInput.addEventListener('input', validarTodoModal);

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!validarTodoModal()) return;

        const formData = new FormData();
        formData.append('password', passwordInput.value);

        try {
            const response = await fetch('/app/auth/perfil/actualizar_contrasenia', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();

            if (response.ok) {
                mostrarFlashMensaje(result.success || 'Contraseña actualizada correctamente', 'success');
                cerrarModalCambiarContrasena();
            } else {
                mostrarFlashMensaje(result.error || 'Error al actualizar la contraseña', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            mostrarFlashMensaje('Error de conexión con el servidor', 'error');
        }
    });

    // --- Inicializar toggles de contraseña dinámicamente ---
    modal.querySelectorAll('.password__toggle').forEach(toggle => setupPasswordToggle(toggle));

    // Insertar iconos SVG
    modal.querySelectorAll('.svg-src[data-src]').forEach(el => {
        insertarSVG(el.dataset.src, el);
    });
}

function cerrarModalCambiarContrasena() {
    const modal = document.getElementById('modalCambiarContrasena');
    if (modal) {
        modal.remove();
    }
}
