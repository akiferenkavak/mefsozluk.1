document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]') ? document.querySelector('meta[name="csrf-token"]').getAttribute('content') : null;

    // Favori Butonları İşlemleri
    document.querySelectorAll('.favorite-btn').forEach(button => {
        button.addEventListener('click', function(event) { // 'event' parametresini ekleyin
            event.preventDefault(); // <<< --- BU SATIRI EKLEYİN! Formun varsayılan gönderimini engeller.

            const entryId = this.dataset.entryId;
            const apiEndpoint = `/api/favorite/${entryId}`; 

            // if (!csrfToken) {
            //     console.error('CSRF token meta tag not found!');
            //     alert('Bir güvenlik hatası oluştu. Lütfen sayfayı yenileyin.');
            //     return;
            // }

            fetch(apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json', // AJAX isteğimiz JSON content type kullanacak
                    // 'X-CSRFToken': csrfToken
                },
                // body: JSON.stringify({}) // API'niz body beklemiyorsa buna gerek yok
            })
            // ... (geri kalan fetch ve .then blokları aynı kalacak) ...
            .then(response => {
                if (!response.ok) {
                    return response.json().then(errData => {
                        throw new Error(errData.message || `HTTP error! status: ${response.status}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    const iconElement = this.querySelector('i');
                    const countElement = this.querySelector('span');

                    if (data.is_favorited) {
                        this.classList.remove('btn-outline-danger');
                        this.classList.add('btn-danger');
                        iconElement.classList.remove('far'); 
                        iconElement.classList.add('fas');   
                    } else {
                        // Eğer bu buton favorites.html'deki "Favoriden Çıkar" ise ve işlem başarılıysa,
                        // butonu değiştirmek yerine kartı DOM'dan kaldırmak daha mantıklı olabilir.
                        // Şimdilik title.html'deki gibi davranıyor:
                        this.classList.remove('btn-danger');
                        this.classList.add('btn-outline-danger');
                        iconElement.classList.remove('fas'); 
                        iconElement.classList.add('far');   
                    }

                    if (countElement) {
                        countElement.textContent = data.favorite_count;
                    } else {
                        this.innerHTML = `<i class="${iconElement.className}"></i> ${data.favorite_count}`;
                    }

                    // Eğer bu favorites.html sayfasındaysa ve favoriden çıkarıldıysa kartı kaldır:
                    if (!data.is_favorited && window.location.pathname.includes('/user/favorites')) {
                        const cardToRemove = this.closest('.card');
                        if (cardToRemove) {
                            cardToRemove.remove();
                        }
                    }

                } else {
                    console.warn('Favori işlemi sunucu tarafından başarısız olarak raporlandı.', data.message);
                    alert(data.message || 'Favori işlemi başarısız oldu.');
                }
            })
            .catch(error => {
                console.error('Favori işlemi hatası:', error);
                alert(error.message || 'Favori işlemi sırasında bir hata oluştu. Lütfen daha sonra tekrar deneyin.');
            });
        });
    });
    
    // Entry Silme Butonu İşlemleri (Burada da event.preventDefault() eklenebilir eğer buton form içindeyse)
    document.querySelectorAll('.delete-entry-btn').forEach(button => {
        button.addEventListener('click', function(event) { 
            // Eğer bu buton da bir form içindeyse ve type="submit" ise:
            // event.preventDefault(); // Gerekirse ekleyin

            if (confirm('Bu entry\'yi silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.')) {
                // ... (geri kalan silme kodu aynı) ...
                const entryId = this.dataset.entryId;
                const apiEndpoint = `/api/delete-entry/${entryId}`;

                if (!csrfToken) {
                    console.error('CSRF token meta tag not found!');
                    alert('Bir güvenlik hatası oluştu. Lütfen sayfayı yenileyin.');
                    return;
                }

                fetch(apiEndpoint, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(errData => {
                            throw new Error(errData.message || `HTTP error! status: ${response.status}`);
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        const cardToRemove = this.closest('.card');
                        if (cardToRemove) {
                            cardToRemove.remove();
                        }
                    } else {
                        alert('Entry silinemedi: ' + (data.message || 'Bilinmeyen bir hata oluştu.'));
                    }
                })
                .catch(error => {
                    console.error('Entry silme hatası:', error);
                    alert(error.message || 'Entry silme işlemi sırasında bir hata oluştu.');
                });
            }
        });
    });
});