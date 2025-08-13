// Funciones compartidas
function validarLongitud(pwd) {
    return pwd.length >= 8;
}

function validarCaracteres(pwd) {
    const tieneMayus = /[A-Z]/.test(pwd);
    const tieneMinus = /[a-z]/.test(pwd);
    const tieneNumero = /\d/.test(pwd);
    return tieneMayus && tieneMinus && tieneNumero;
}

function validarCoincidencia(pwd, confirmPwd) {
    return pwd === confirmPwd && pwd.length > 0;
}

function actualizarEstado(valid, elemento) {
    if (!elemento) return;
    elemento.classList.remove('validation-success', 'validation-error');
    elemento.classList.add(valid ? 'validation-success' : 'validation-error');
}

function showError(field, message) {
    const errorElement = document.getElementById(`${field}-error`);
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        const inputGroup = errorElement.closest('.forms__group');
        if (inputGroup) inputGroup.classList.add('has-error');
    } else {
        mostrarFlashMensaje(message, 'error');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Función para enlazar validación a un formulario
    function inicializarValidacionPassword(formId) {
        const form = document.getElementById(formId);
        if (!form) return;

        const passwordInput = form.querySelector('#password');
        const confirmInput = form.querySelector('#confirm_password');
        const lengthValidation = form.querySelector('#length-validation');
        const charsValidation = form.querySelector('#chars-validation');
        const matchValidation = form.querySelector('#match-validation');

        function validarTodo() {
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

        passwordInput.addEventListener('input', validarTodo);
        confirmInput.addEventListener('input', validarTodo);

        return { form, validarTodo };
    }

    // Inicializar validación para formularios
    const signinValidation = inicializarValidacionPassword('signinForm');

    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(profileForm);

            try {
                const response = await fetch(profileForm.action, {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    window.location.reload();
                    mostrarFlashMensaje('Usuario Actualizado correctamente', 'info')
                }
            } catch (error) {
                mostrarFlashMensaje('Error de conexión con el servidor', 'error');
            }
        });
    }

    const passwordValidation = inicializarValidacionPassword('formCambiarContrasena')
});
