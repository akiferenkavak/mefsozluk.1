// app/static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    // CSRF token'ını sayfa yüklendiğinde bir kez oku
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

    // Flash mesaj gösterme fonksiyonu (tüm sayfalarda kullanılabilir)
    function showFlashMessage(message, category) {
        const flashContainer = document.getElementById('flash-messages-container');
        if (flashContainer) {
            const alertDiv = document.createElement('div');
            // Bootstrap Toast stili için class'lar
            alertDiv.className = `toast align-items-center text-white bg-${category} border-0 mb-2`;
            alertDiv.role = 'alert';
            alertDiv.setAttribute('aria-live', 'assertive');
            alertDiv.setAttribute('aria-atomic', 'true');

            alertDiv.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            `;
            flashContainer.appendChild(alertDiv);
            
            // Bootstrap Toast'ı başlat ve göster
            const toast = new bootstrap.Toast(alertDiv, { delay: 5000 });
            toast.show();

            // Toast gizlendikten sonra DOM'dan kaldır
            alertDiv.addEventListener('hidden.bs.toast', function () {
                if (alertDiv.parentNode) { // Hâlâ DOM'da mı kontrol et
                    alertDiv.remove();
                }
            });
        } else {
            // Fallback eğer #flash-messages-container yoksa (eski alert yapısı)
            console.warn('#flash-messages-container bulunamadı, alert kullanılıyor.');
            alert(`${category.toUpperCase()}: ${message}`);
        }
    }

    // Profil sayfasındaki Takip Et/Takipten Çık butonu için özel mantık
    const followBtnOnProfile = document.getElementById('followBtn');
    if (followBtnOnProfile) {
        const buttonElement = followBtnOnProfile; // `this` referans sorununu çözmek için

        buttonElement.addEventListener('click', function() {
            // console.log('Profile Follow button clicked');
            
            const nickname = buttonElement.dataset.nickname;
            let action = buttonElement.dataset.action;      
            
            if (!csrfToken) {
                console.error('CSRF token bulunamadı (profile follow).');
                showFlashMessage('Güvenlik token\'ı bulunamadı. Sayfayı yenileyin.', 'danger');
                return;
            }
            
            const followUrl = `/user/follow/${nickname}`; // Bu URL yapısının doğru olduğunu varsayıyoruz
            const unfollowUrl = `/user/unfollow/${nickname}`; // Bu URL yapısının doğru olduğunu varsayıyoruz
            const url = action === 'follow' ? followUrl : unfollowUrl;
            
            buttonElement.disabled = true; 
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken 
                }
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(errData => {
                        throw { status: response.status, data: errData }; 
                    }).catch(() => {
                        throw new Error(`Network response was not ok: ${response.status} ${response.statusText}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    const followBtnText = document.getElementById('followBtnText'); 
                    const followerCountBadge = document.getElementById('followerCountBadge'); 
                    const icon = buttonElement.querySelector('i');

                    if (action === 'follow') {
                        buttonElement.dataset.action = 'unfollow'; 
                        if (followBtnText) followBtnText.textContent = 'Takipten Çık';
                        buttonElement.classList.remove('btn-success'); 
                        buttonElement.classList.add('btn-danger');    
                        if (icon) {
                            icon.classList.remove('fa-user-plus');
                            icon.classList.add('fa-user-minus');
                        }
                    } else { // action === 'unfollow'
                        buttonElement.dataset.action = 'follow';   
                        if (followBtnText) followBtnText.textContent = 'Takip Et';
                        buttonElement.classList.remove('btn-danger');  
                        buttonElement.classList.add('btn-success');  
                        if (icon) {
                            icon.classList.remove('fa-user-minus');
                            icon.classList.add('fa-user-plus');
                        }
                    }
                    
                    if (followerCountBadge && data.follower_count !== undefined) {
                        followerCountBadge.textContent = data.follower_count;
                    }
                    
                    showFlashMessage(data.message, 'success');
                } else {
                    showFlashMessage(data.message || 'İşlem başarısız oldu.', 'danger');
                }
            })
            .catch(error => {
                console.error('Profile Follow/Unfollow Fetch Error:', error);
                let errorMessage = 'Bir hata oluştu. Lütfen tekrar deneyin.';
                if (error && error.data && error.data.message) {
                    errorMessage = error.data.message; 
                } else if (error && error.message) {
                    errorMessage = error.message;
                }
                showFlashMessage(errorMessage, 'danger');
            })
            .finally(() => {
                buttonElement.disabled = false; 
            });
        });
    }

    // Diğer genel AJAX butonlarınız (örn: .favorite-btn, .follow-toggle-btn, .delete-entry-btn) için
    // event listener'lar da buraya eklenebilir. Her biri kendi `if (document.querySelector(...))`
    // kontrolü içinde olmalıdır ki sadece ilgili elementler sayfada varsa çalışsınlar.
    // Örneğin, daha önce followers.html/following.html için önerdiğim .follow-toggle-btn kodu:
    document.querySelectorAll('.follow-toggle-btn').forEach(button => {
        // #followBtn ID'li elemente zaten yukarıda listener eklediğimiz için tekrar eklemeyelim.
        // Bu, eğer .follow-toggle-btn class'ı aynı zamanda #followBtn ID'li elementte de varsa önemlidir.
        // Genellikle ID'ler benzersiz olduğu için bu kontrol gerekmeyebilir ya da farklı class/ID stratejisi izlenir.
        if (button.id === 'followBtn') return; 

        button.addEventListener('click', function() {
            const thisButton = this;
            const userNickname = thisButton.dataset.nickname;
            let currentAction = thisButton.dataset.action;

            if (!csrfToken) {
                showFlashMessage('Güvenlik token\'ı bulunamadı. Lütfen sayfayı yenileyin.', 'danger');
                return;
            }
            
            const followUrl = `/user/follow/${userNickname}`; // veya url_for ile oluşturulmuşsa o yapı
            const unfollowUrl = `/user/unfollow/${userNickname}`;
            const url = currentAction === 'follow' ? followUrl : unfollowUrl;
            
            thisButton.disabled = true;

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => { /* ... (response handling) ... */ if (!response.ok) { return response.json().then(err => { throw {data: err}; }); } return response.json(); })
            .then(data => {
                if (data.success) {
                    if (currentAction === 'follow') {
                        thisButton.dataset.action = 'unfollow';
                        thisButton.innerHTML = '<i class="fas fa-user-minus me-1"></i>Takipten Çık';
                        thisButton.classList.remove('btn-success');
                        thisButton.classList.add('btn-danger');
                    } else {
                        thisButton.dataset.action = 'follow';
                        thisButton.innerHTML = '<i class="fas fa-user-plus me-1"></i>Takip Et';
                        thisButton.classList.remove('btn-danger');
                        thisButton.classList.add('btn-success');
                    }
                    showFlashMessage(data.message, 'success');
                } else {
                    showFlashMessage(data.message || 'İşlem başarısız oldu.', 'danger');
                }
            })
            .catch(error => { /* ... (error handling) ... */ showFlashMessage(error.data?.message || error.message || 'Takip işlemi hatası.', 'danger'); })
            .finally(() => {
                thisButton.disabled = false;
            });
        });
    });

    // Favori butonları için olan kod da buraya eklenebilir (varsa .favorite-btn class'ı için)
    // Silme butonları için olan kod da buraya eklenebilir (varsa .delete-entry-btn class'ı için)

});