document.addEventListener('DOMContentLoaded', function () {
    // CSRF token'ını almak için yardımcı fonksiyon
    const getCsrfToken = () => {
        const csrfInput = document.querySelector('input[name="csrf_token"]');
        if (csrfInput) return csrfInput.value;
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        if (csrfMeta) return csrfMeta.content;
        console.warn('CSRF token bulunamadı. POST istekleri başarısız olabilir.');
        return null;
    };

    // "Toast" bildirimlerini göstermek için yardımcı fonksiyon
    const showToast = (message, type = 'success') => {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            console.warn('Toast container (#toast-container) bulunamadı. Mesaj alert ile gösteriliyor.');
            alert(message); // Yedek olarak alert kullan
            return;
        }

        const toastId = 'toast-' + Date.now();
        const toastHTML = `
            <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="5000">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        const toastElement = document.getElementById(toastId);
        
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            const toast = new bootstrap.Toast(toastElement);
            toast.show();
            toastElement.addEventListener('hidden.bs.toast', () => toastElement.remove());
        } else {
            console.warn('Bootstrap Toast objesi bulunamadı. Toast basitçe gösteriliyor.');
            toastElement.classList.add('show'); // Basitçe göster, kendi kendine kaybolmaz
            setTimeout(() => toastElement.remove(), 5000); // 5 saniye sonra kaldır
        }
    };

    // Sunucuya Fetch API ile istek göndermek için genel yardımcı fonksiyon
    const makeFetchRequest = (url, options = { method: 'POST' }, successCallback, buttonElement) => {
        let originalButtonHtml = '';
        if (buttonElement) {
            originalButtonHtml = buttonElement.innerHTML;
            buttonElement.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> İşleniyor...';
            buttonElement.disabled = true;
        }

        const csrfToken = getCsrfToken();
        const headers = {
            'Accept': 'application/json',
            ...options.headers // Gelen diğer header'ları ekle
        };
        if (csrfToken && (options.method === 'POST' || options.method === 'PUT' || options.method === 'DELETE')) {
            headers['X-CSRFToken'] = csrfToken;
        }
         // Eğer body JSON ise Content-Type'ı ayarla
        if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
            headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(options.body);
        }


        fetch(url, { ...options, headers: headers })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errData => Promise.reject(errData || { message: `HTTP error! Status: ${response.status}` }));
            }
            // Yanıtın içeriği olmayabilir (örn: 204 No Content)
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.indexOf("application/json") !== -1) {
                return response.json();
            } else {
                return { success: true, message: response.statusText || "İşlem başarılı." }; // JSON olmayan başarılı yanıtlar için
            }
        })
        .then(data => {
            if (data.success) {
                showToast(data.message || "İşlem başarıyla tamamlandı.", 'success');
                if (successCallback) successCallback(data);
            } else {
                showToast(data.message || 'Bir hata oluştu.', 'danger');
            }
        })
        .catch(error => {
            console.error('Fetch Hatası:', error);
            const errorMessage = error.message || (typeof error === 'string' ? error : 'İstek gönderilirken bir ağ hatası oluştu.');
            showToast(errorMessage, 'danger');
        })
        .finally(() => {
            if (buttonElement) {
                buttonElement.innerHTML = originalButtonHtml;
                buttonElement.disabled = false;
            }
        });
    };

    // --- Admin Kullanıcı Yönetimi İşlemleri ---
    // Bu kısım sadece admin/users.html sayfasında çalışacak elementler için.
    // Daha güvenli olması için, bu kodun sadece admin/users sayfasında çalışmasını sağlayacak bir kontrol eklenebilir
    // (örneğin body class'ı veya spesifik bir elementin varlığı kontrol edilerek).
    // Şimdilik, buton class'larının varlığına göre çalışacak.

    // Aktif/Pasif Durumu Değiştirme Butonları
    document.querySelectorAll('.toggle-active-btn').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const userId = this.dataset.userId;
            const url = this.dataset.url;
            makeFetchRequest(url, { method: 'POST' }, (data) => {
                const statusBadge = document.getElementById(`status-active-${userId}`);
                const buttonText = document.getElementById(`toggle-active-text-${userId}`);
                if (statusBadge && buttonText) {
                    if (data.is_active) {
                        statusBadge.className = 'badge bg-success';
                        statusBadge.textContent = 'Evet';
                        buttonText.textContent = 'Pasif Yap';
                    } else {
                        statusBadge.className = 'badge bg-danger';
                        statusBadge.textContent = 'Hayır';
                        buttonText.textContent = 'Aktif Yap';
                    }
                }
            }, this);
        });
    });

    // Admin Durumu Değiştirme Butonları
    document.querySelectorAll('.toggle-admin-btn').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const userId = this.dataset.userId;
            const url = this.dataset.url;
            makeFetchRequest(url, { method: 'POST' }, (data) => {
                const statusBadge = document.getElementById(`status-admin-${userId}`);
                const buttonText = document.getElementById(`toggle-admin-text-${userId}`);
                if(statusBadge && buttonText) {
                    if (data.is_admin) {
                        statusBadge.className = 'badge bg-info';
                        statusBadge.textContent = 'Evet';
                        buttonText.textContent = 'Adminliği Kaldır';
                    } else {
                        statusBadge.className = 'badge bg-secondary';
                        statusBadge.textContent = 'Hayır';
                        buttonText.textContent = 'Admin Yap';
                    }
                }
            }, this);
        });
    });

    // Kullanıcı Silme İşlemleri
    const deleteUserModalElement = document.getElementById('deleteUserModal');
    if (deleteUserModalElement && typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        const deleteUserModal = new bootstrap.Modal(deleteUserModalElement);
        let userIdToDelete = null;
        let userDeleteUrl = null;

        document.querySelectorAll('.delete-user-btn').forEach(button => {
            button.addEventListener('click', function (e) {
                e.preventDefault();
                userIdToDelete = this.dataset.userId;
                userDeleteUrl = this.dataset.url;
                const userNickname = this.dataset.userNickname;
                const modalNicknameSpan = deleteUserModalElement.querySelector('#userNicknameToDelete');
                if(modalNicknameSpan) modalNicknameSpan.textContent = userNickname;
                deleteUserModal.show();
            });
        });

        const confirmDeleteBtn = document.getElementById('confirmDeleteUserBtn');
        if (confirmDeleteBtn) {
            confirmDeleteBtn.addEventListener('click', function () {
                if (userIdToDelete && userDeleteUrl) {
                    makeFetchRequest(userDeleteUrl, { method: 'POST' }, (data) => {
                        const userRow = document.getElementById(`user-row-${userIdToDelete}`);
                        if (userRow) userRow.remove();
                        // Opsiyonel: Toplam kullanıcı sayısını güncelle (eğer tabloda gösteriliyorsa)
                        const totalUsersElement = document.querySelector('.card-header h6'); // Daha spesifik bir seçici gerekebilir
                        if (totalUsersElement && data.new_total_users !== undefined) {
                            totalUsersElement.textContent = `Kullanıcı Listesi (Toplam: ${data.new_total_users})`;
                        } else if (totalUsersElement && users.total) { // Fallback if new_total_users not sent
                             // Bu kısım doğrudan JS ile güncellenemez, Flask'tan gelen users.total'a erişim yok.
                             // Sayfa yenilenmeden toplam sayıyı güncellemek için backend'den yeni toplamı almak gerekir.
                        }
                    }, this);
                    deleteUserModal.hide();
                    userIdToDelete = null;
                    userDeleteUrl = null;
                }
            });
        }
    } else if (deleteUserModalElement) {
        console.warn('Bootstrap Modal objesi bulunamadı. Silme modalı düzgün çalışmayabilir.');
    }

    // --- Profil Sayfası Takip Butonu İşlemleri (Eğer bu main.js global ise) ---
    const followBtnOnProfile = document.getElementById('followBtn');
    if (followBtnOnProfile) {
        followBtnOnProfile.addEventListener('click', function() {
            const nickname = this.dataset.nickname;
            let action = this.dataset.action;
            const url = action === 'follow' ? `/user/follow/${nickname}` : `/user/unfollow/${nickname}`; // URL'leri backend route'larınıza göre ayarlayın

            makeFetchRequest(url, { method: 'POST' }, (data) => {
                const followBtnText = document.getElementById('followBtnText'); // Buton içindeki text span'ı
                const followerCountBadge = document.getElementById('followerCountBadge'); // Takipçi sayısını gösteren span/badge
                const icon = this.querySelector('i');

                if (action === 'follow') {
                    this.dataset.action = 'unfollow';
                    if (followBtnText) followBtnText.textContent = 'Takipten Çık';
                    this.classList.remove('btn-success');
                    this.classList.add('btn-danger');
                    if (icon) {
                        icon.classList.remove('fa-user-plus');
                        icon.classList.add('fa-user-minus');
                    }
                } else { // action === 'unfollow'
                    this.dataset.action = 'follow';
                    if (followBtnText) followBtnText.textContent = 'Takip Et';
                    this.classList.remove('btn-danger');
                    this.classList.add('btn-success');
                    if (icon) {
                        icon.classList.remove('fa-user-minus');
                        icon.classList.add('fa-user-plus');
                    }
                }
                if (followerCountBadge && data.follower_count !== undefined) {
                    followerCountBadge.textContent = data.follower_count;
                }
            }, this);
        });
    }

    // --- Genel Takip Butonları (Örn: Kullanıcı listelerinde) ---
    document.querySelectorAll('.follow-toggle-btn').forEach(button => {
        if (button.id === 'followBtn') return; // Profil sayfasındaki butonu tekrar ele alma

        button.addEventListener('click', function() {
            const userNickname = this.dataset.nickname;
            let currentAction = this.dataset.action;
            const url = currentAction === 'follow' ? `/user/follow/${userNickname}` : `/user/unfollow/${userNickname}`;

            makeFetchRequest(url, { method: 'POST' }, (data) => {
                if (currentAction === 'follow') {
                    this.dataset.action = 'unfollow';
                    this.innerHTML = '<i class="fas fa-user-minus me-1"></i>Takipten Çık';
                    this.classList.remove('btn-success', 'btn-outline-success');
                    this.classList.add('btn-danger');
                } else {
                    this.dataset.action = 'follow';
                    this.innerHTML = '<i class="fas fa-user-plus me-1"></i>Takip Et';
                    this.classList.remove('btn-danger', 'btn-outline-danger');
                    this.classList.add('btn-success');
                }
                // Takipçi sayısını güncellemek için ek mantık gerekebilir (eğer bu butonlar bir listedeyse)
            }, this);
        });
    });

}); // DOMContentLoaded sonu