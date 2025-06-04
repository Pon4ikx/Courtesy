document.addEventListener('DOMContentLoaded', function() {

    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            

            document.querySelectorAll('.tab-btn, .tab-content').forEach(el => {
                el.classList.remove('active');
            });
            

            this.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
});


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

document.querySelectorAll('.btn-cancel').forEach(btn => {
    btn.addEventListener('click', async function(e) {
        e.preventDefault();
        const talonId = this.getAttribute('data-talon-id');
        const card = this.closest('.talon-card');
        
        if (confirm('Вы действительно хотите отменить запись?')) {
            try {
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                
                const response = await fetch(`/cancel_talon/${talonId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/json',
                    },
                    credentials: 'same-origin'
                });
                
                const data = await response.json();
                
                if (response.ok && data.status === 'success') {

                    showToast(data.message, 'success');
                    

                    card.style.transition = 'all 0.3s ease';
                    card.style.opacity = '0';
                    setTimeout(() => card.remove(), 300);
                    
                } else {
                    showToast(data.message || 'Ошибка при отмене записи', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showToast('Произошла ошибка при отправке запроса', 'error');
            }
        }
    });
});

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-icon">
            ${type === 'success' ? '✓' : '⚠'}
        </div>
        <div class="toast-message">${message}</div>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}