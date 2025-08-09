document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('signinForm');
    const passwordInput = document.getElementById('password');
    const confirmInput = document.getElementById('confirm_password');

    const lengthValidation = document.getElementById('length-validation');
    const charsValidation = document.getElementById('chars-validation');
    const matchValidation = document.getElementById('match-validation');

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
        elemento.classList.remove('validation-success', 'validation-error');
        elemento.classList.add(valid ? 'validation-success' : 'validation-error');
    }

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


 document.getElementById('profileForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Limpiar errores anteriores
    document.querySelectorAll('.error-message').forEach(el => {
      el.textContent = '';
      el.style.display = 'none';
    });
    document.querySelectorAll('.forms__group').forEach(el => {
      el.classList.remove('has-error');
    });

    const form = e.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    // Validación frontend básica
    if (data.password && data.password !== data.confirm_password) {
      showError('confirm_password', 'Las contraseñas no coinciden');
      return;
    }

    try {
      const response = await fetch(form.action, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(data)
      });
      
      const result = await response.json();
      
      if (response.ok) {
        // Mostrar mensaje de éxito
        showNotification('Perfil actualizado correctamente', 'success');
        
        // Actualizar la información mostrada
        if (result.usuario) {
          document.querySelector('.profile__name').textContent = 
            `${result.usuario.first_name} ${result.usuario.last_name}`;
          document.querySelector('.profile__email').textContent = result.usuario.email;
        }
      } else {
        // Mostrar errores del backend
        if (result.error) {
          showNotification(result.error, 'error');
        } else if (result.errors) {
          // Mostrar errores de validación por campo
          Object.entries(result.errors).forEach(([field, message]) => {
            showError(field, message);
          });
        }
      }
    } catch (error) {
      mostrarFlashMensaje('Error de conexión con el servidor', 'danger');
    }
  });

  function showError(field, message) {
    const errorElement = document.getElementById(`${field}-error`);
    if (errorElement) {
      errorElement.textContent = message;
      errorElement.style.display = 'block';
      const inputGroup = errorElement.closest('.forms__group');
      if (inputGroup) inputGroup.classList.add('has-error');
    } else {
      mostrarFlashMensaje(message, 'danger');
    }
  }

});


document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('profileForm');
  const passwordInput = document.getElementById('password');
  const confirmInput = document.getElementById('confirm_password');

  const lengthValidation = document.getElementById('length-validation');
  const charsValidation = document.getElementById('chars-validation');
  const matchValidation = document.getElementById('match-validation');

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
    elemento.classList.remove('validation-success', 'validation-error');
    elemento.classList.add(valid ? 'validation-success' : 'validation-error');
  }

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

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    document.querySelectorAll('.error-message').forEach(el => {
      el.textContent = '';
      el.style.display = 'none';
    });
    document.querySelectorAll('.forms__group').forEach(el => {
      el.classList.remove('has-error');
    });

    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    // Eliminar campos de contraseña si están vacíos
    if (!data.password) {
      delete data.password;
      delete data.confirm_password;
    }

    // Validación manual
    if (data.password && data.password !== data.confirm_password) {
      showError('confirm_password', 'Las contraseñas no coinciden');
      return;
    }

    try {
      const response = await fetch(form.action, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(data)
      });

      const result = await response.json();

      if (response.ok) {
        mostrarFlashMensaje('Perfil actualizado correctamente', 'success');

        if (result.usuario) {
          document.querySelector('.profile__name').textContent = 
            `${result.usuario.first_name} ${result.usuario.last_name}`;
          document.querySelector('.profile__email').textContent = result.usuario.email;
        }
      } else {
        if (result.error) {
          mostrarFlashMensaje(result.error, 'danger');
        } else if (result.errors) {
          Object.entries(result.errors).forEach(([field, message]) => {
            showError(field, message);
          });
        }
      }
    } catch (error) {
      console.error('Error:', error);
      mostrarFlashMensaje('Error de conexión con el servidor', 'danger');
    }
  });

  function showError(field, message) {
    const errorElement = document.getElementById(`${field}-error`);
    if (errorElement) {
      errorElement.textContent = message;
      errorElement.style.display = 'block';
      const inputGroup = errorElement.closest('.forms__group');
      if (inputGroup) inputGroup.classList.add('has-error');
    } else {
      mostrarFlashMensaje(message, 'danger');
    }
  }
});
