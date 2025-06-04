document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const liveResults = document.getElementById('live-results');
    let searchTimeout;
    
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        
        if (this.value.length < 2) {
            liveResults.style.display = 'none';
            return;
        }
        
        searchTimeout = setTimeout(() => {
            fetch(`/search/?q=${encodeURIComponent(this.value)}&ajax=1`)
                .then(response => response.json())
                .then(data => {
                    let html = '';
                    
                    if (data.specialists && data.specialists.length) {
                        html += '<div class="search-group"><h4>Специалисты</h4>';
                        data.specialists.forEach(item => {
                            html += `<a href="/specialists/${item.id}">${item.full_name}</a>`;
                        });
                        html += '</div>';
                    }
                    
                    if (data.services && data.services.length) {
                        html += '<div class="search-group"><h4>Услуги</h4>';
                        data.services.forEach(item => {
                            html += `<a href="/services/${item.id}">${item.name}</a>`;
                        });
                        html += '</div>';
                    }
                    
                    liveResults.innerHTML = html;
                    liveResults.style.display = html ? 'block' : 'none';
                });
        }, 300);
    });
    
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.search-container')) {
            liveResults.style.display = 'none';
        }
    });
});