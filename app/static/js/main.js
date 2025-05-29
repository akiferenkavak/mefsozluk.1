document.addEventListener('DOMContentLoaded', function() {
    // Favori butonu işlemleri
    document.querySelectorAll('.favorite-btn').forEach(button => {
        button.addEventListener('click', function() {
            const entryId = this.dataset.entryId;
            const isFavorited = this.dataset.favorited === 'true';
            
            fetch(`/api/favorite/${entryId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name=csrf-token]').getAttribute('content')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.dataset.favorited = data.is_favorited.toString();
                    this.innerHTML = `<i class="fas fa-heart"></i> ${data.favorite_count}`;
                    
                    if (data.is_favorited) {
                        this.classList.remove('btn-outline-danger');
                        this.classList.add('btn-danger');
                    } else {
                        this.classList.remove('btn-danger');
                        this.classList.add('btn-outline-danger');
                    }
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
    
    // Entry silme butonu
    document.querySelectorAll('.delete-entry-btn').forEach(button => {
        button.addEventListener('click', function() {
            if (confirm('Bu entry\'yi silmek istediğinizden emin misiniz?')) {
                const entryId = this.dataset.entryId;
                
                fetch(`/api/delete-entry/${entryId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('meta[name=csrf-token]').getAttribute('content')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.closest('.card').remove();
                        alert('Entry silindi.');
                    } else {
                        alert('Hata: ' + data.message);
                    }
                })
                .catch(error => console.error('Error:', error));
            }
        });
    });
});