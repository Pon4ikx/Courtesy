document.addEventListener('DOMContentLoaded', function() {
    // Переключение табов
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // Удаляем активный класс у всех кнопок и контента
            document.querySelectorAll('.tab-btn, .tab-content').forEach(el => {
                el.classList.remove('active');
            });
            
            // Добавляем активный класс текущей кнопке и контенту
            this.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // Подтверждение отмены записи
    const cancelBtns = document.querySelectorAll('.btn-cancel');
    cancelBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            if (confirm('Вы действительно хотите отменить запись?')) {
                // Здесь будет код для отмены записи
                this.closest('.talon-card').style.opacity = '0.5';
                this.disabled = true;
                alert('Запись отменена');
            }
        });
    });
});

// Обработка модального окна удаления аккаунта
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('deleteAccountModal');
    const btn = document.getElementById('deleteAccountBtn');
    const span = document.getElementsByClassName('close')[0];
    const cancelBtn = document.querySelector('.btn-cancel');

    btn.onclick = function() {
        modal.style.display = 'block';
    }

    span.onclick = function() {
        modal.style.display = 'none';
    }

    cancelBtn.onclick = function() {
        modal.style.display = 'none';
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
});