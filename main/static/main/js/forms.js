// Обработка быстрой формы связи
document.addEventListener('DOMContentLoaded', function() {
    const quickContactForm = document.querySelector('.quick-contact-form');
    
    if (quickContactForm) {
        quickContactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitButton = this.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            
            // Показываем состояние загрузки
            submitButton.textContent = 'Отправляем...';
            submitButton.disabled = true;
            
            // Отправляем AJAX запрос
            fetch('/quick-contact/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Показываем сообщение об успехе
                    showMessage(data.message, 'success');
                    quickContactForm.reset();
                } else {
                    // Показываем сообщение об ошибке
                    showMessage(data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                showMessage('Произошла ошибка при отправке. Пожалуйста, попробуйте позже.', 'error');
            })
            .finally(() => {
                // Восстанавливаем кнопку
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            });
        });
    }
    
    // Обработка формы калькулятора
    const calculatorForm = document.querySelector('.calculator-form');
    
    if (calculatorForm) {
        calculatorForm.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;
            
            // Проверяем обязательные поля
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('error');
                    isValid = false;
                } else {
                    field.classList.remove('error');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showMessage('Пожалуйста, заполните все обязательные поля.', 'error');
            }
        });
    }
    
    // Обработка формы обратной связи
    const contactForm = document.querySelector('.contact-form');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;
            
            // Проверяем обязательные поля
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('error');
                    isValid = false;
                } else {
                    field.classList.remove('error');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showMessage('Пожалуйста, заполните все обязательные поля.', 'error');
            }
        });
    }
});

// Функция для показа сообщений
function showMessage(message, type = 'info') {
    // Удаляем существующие сообщения
    const existingMessages = document.querySelectorAll('.message-popup');
    existingMessages.forEach(msg => msg.remove());
    
    // Создаем новое сообщение
    const messageElement = document.createElement('div');
    messageElement.className = `message-popup message-popup-${type}`;
    messageElement.innerHTML = `
        <div class="message-popup-content">
            <span class="message-popup-text">${message}</span>
            <button class="message-popup-close">&times;</button>
        </div>
    `;
    
    // Добавляем в body
    document.body.appendChild(messageElement);
    
    // Показываем сообщение
    setTimeout(() => {
        messageElement.classList.add('show');
    }, 100);
    
    // Автоматически скрываем через 5 секунд
    setTimeout(() => {
        hideMessage(messageElement);
    }, 5000);
    
    // Обработчик закрытия
    const closeButton = messageElement.querySelector('.message-popup-close');
    closeButton.addEventListener('click', () => {
        hideMessage(messageElement);
    });
}

// Функция для скрытия сообщения
function hideMessage(messageElement) {
    messageElement.classList.remove('show');
    setTimeout(() => {
        if (messageElement.parentNode) {
            messageElement.parentNode.removeChild(messageElement);
        }
    }, 300);
}

// Валидация телефона
function validatePhone(input) {
    const phoneRegex = /^[\+]?[0-9\s\-\(\)]{10,}$/;
    return phoneRegex.test(input.value);
}

// Валидация email
function validateEmail(input) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(input.value);
}

// Добавляем валидацию в реальном времени
document.addEventListener('DOMContentLoaded', function() {
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    const emailInputs = document.querySelectorAll('input[type="email"]');
    
    phoneInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value && !validatePhone(this)) {
                this.classList.add('error');
                showFieldError(this, 'Введите корректный номер телефона');
            } else {
                this.classList.remove('error');
                hideFieldError(this);
            }
        });
    });
    
    emailInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value && !validateEmail(this)) {
                this.classList.add('error');
                showFieldError(this, 'Введите корректный email адрес');
            } else {
                this.classList.remove('error');
                hideFieldError(this);
            }
        });
    });
});

// Показать ошибку поля
function showFieldError(field, message) {
    hideFieldError(field);
    
    const errorElement = document.createElement('div');
    errorElement.className = 'field-error';
    errorElement.textContent = message;
    
    field.parentNode.appendChild(errorElement);
}

// Скрыть ошибку поля
function hideFieldError(field) {
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}
