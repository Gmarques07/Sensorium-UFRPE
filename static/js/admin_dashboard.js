// --- 1. LÓGICA DE NAVEGAÇÃO (UI) - Roda independente de login ---

// Função Global para ser chamada pelo HTML
function showSection(event, sectionId) {
    if (event) event.preventDefault();

    console.log("Navegando para:", sectionId); // Debug para saber se clicou

    // 1. Remove classe 'active' de TODOS os links da sidebar
    const allLinks = document.querySelectorAll('.sidebar-container .nav-link');
    allLinks.forEach(link => {
        link.classList.remove('active');
        link.style.borderLeft = ''; // Limpa sujeira visual
    });

    // 2. Adiciona 'active' no botão clicado (ou correspondente ao ID)
    if (event && event.currentTarget) {
        event.currentTarget.classList.add('active');
    } else {
        const targetLink = document.querySelector(`.nav-link[href="#${sectionId}"]`);
        if (targetLink) targetLink.classList.add('active');
    }

    // 3. Esconde TODAS as seções de conteúdo
    const allPanels = document.querySelectorAll('.section-panel');
    allPanels.forEach(panel => {
        panel.classList.remove('active'); 
        // Força display none via style para garantir, caso o CSS falhe
        panel.style.display = 'none'; 
    });

    // 4. Mostra APENAS a seção desejada
    let activePanel = document.getElementById(sectionId);
    
    // Fallback: Se a seção não existir (hash inválido), voltar para o painel inicial
    if (!activePanel) {
        console.warn(`Seção "${sectionId}" não encontrada. Redirecionando para painel.`);
        sectionId = 'painel';
        activePanel = document.getElementById(sectionId);
        history.replaceState({}, '', `#${sectionId}`);
        
        // Corrige a sidebar para refletir a mudança
        allLinks.forEach(link => link.classList.remove('active'));
        const targetLink = document.querySelector(`.nav-link[href="#${sectionId}"]`);
        if (targetLink) targetLink.classList.add('active');
    }

    if (activePanel) {
        activePanel.classList.add('active');
        activePanel.style.display = 'block'; // Garante visibilidade
    } else {
        console.warn("Seção não encontrada:", sectionId);
    }

    // 5. Fecha menu mobile
    const sidebarEl = document.getElementById('sidebarMenu');
    if (sidebarEl && sidebarEl.classList.contains('show') && window.bootstrap) {
        const bsOffcanvas = bootstrap.Offcanvas.getInstance(sidebarEl);
        if (bsOffcanvas) bsOffcanvas.hide();
    }

    // Atualiza URL
    history.pushState({}, '', `#${sectionId}`);
}

// Inicialização da Interface
document.addEventListener('DOMContentLoaded', function() {
    console.log("Admin Dashboard: UI Iniciada");

    // A. Data no Header
    try {
        const dateElement = document.getElementById('current-date');
        if (dateElement) {
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            const today = new Date().toLocaleDateString('pt-BR', options);
            dateElement.textContent = today.charAt(0).toUpperCase() + today.slice(1);
        }
    } catch (e) { console.error(e); }

    // B. Inicializa a Aba Correta
    const hash = window.location.hash.slice(1) || 'painel';
    showSection(null, hash);

    // C. Adiciona clicks manuais nos links (Garantia extra)
    const navLinks = document.querySelectorAll('.sidebar-container .nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href').substring(1);
            showSection(e, href);
        });
    });

    // D. Logout
    const logoutButton = document.getElementById('logout-button');
    if (logoutButton) {
        logoutButton.addEventListener('click', (e) => {
            e.preventDefault();
            const modalEl = document.getElementById('modalConfirmLogout');
            if (modalEl) {
                const modal = new bootstrap.Modal(modalEl);
                modal.show();
            } else {
                console.error("Modal de logout não encontrado!");
                // Fallback para garantir que o usuário consiga sair
                if(confirm("Deseja sair do sistema?")) {
                    fetch('/api/v1/admin/logout', { method: 'POST' })
                        .then(() => {
                            localStorage.removeItem('adminAccessToken');
                            window.location.href = '/admin';
                        })
                        .catch(err => console.error('Erro no logout:', err));
                }
            }
        });
    }

    const confirmLogoutBtn = document.getElementById('btnConfirmLogout');
    if (confirmLogoutBtn) {
        confirmLogoutBtn.addEventListener('click', () => {
            fetch('/api/v1/admin/logout', { method: 'POST' })
                .then(() => {
                    localStorage.removeItem('adminAccessToken');
                    window.location.href = '/admin';
                })
                .catch(err => console.error('Erro no logout:', err));
        });
    }

    // --- 2. LÓGICA DE DADOS (API) - Roda depois da UI ---
    iniciarCarregamentoDados();
});


// Função separada para dados (Token Required)
function iniciarCarregamentoDados() {
    const accessToken = localStorage.getItem('adminAccessToken');
    
    if (!accessToken) {
        console.warn("Sem token de admin. Tentando usar autenticação via Cookie.");
    }

    // Interceptor de Fetch Global
    const originalFetch = window.fetch;
    window.fetch = function(input, init = {}) {
        const url = typeof input === 'string' ? input : input.url;
        const headers = new Headers(init.headers || (typeof input !== 'string' && input.headers) || {});
        
        if (accessToken) {
            headers.set('Authorization', `Bearer ${accessToken}`);
        }
        
        let newInit = { ...init, headers };
        let newRequest = typeof input === 'string' ? new Request(input, newInit) : new Request(input, newInit);
        return originalFetch(newRequest);
    };

    // Configura botões de ação (Excluir, Editar)
    setupActionButtons();
}

function setupActionButtons() {
    document.querySelectorAll('.btn-excluir-usuario').forEach(btn => {
        // Clone para remover listeners antigos e evitar duplicidade
        const newBtn = btn.cloneNode(true);
        btn.parentNode.replaceChild(newBtn, btn);
        
        newBtn.addEventListener('click', (e) => {
            const id = newBtn.dataset.id;
            
            confirmarAcao('Excluir Usuário', 'Tem certeza que deseja excluir este usuário? Esta ação não pode ser desfeita.', async () => {
                try {
                    const res = await fetch(`/api/v1/admin/usuarios/${id}`, { method: 'DELETE' });
                    if (res.ok) {
                        newBtn.closest('tr').remove();
                        const counter = document.querySelector('[data-stat="total-usuarios"]');
                        if(counter) counter.innerText = Math.max(0, parseInt(counter.innerText) - 1);
                        mostrarAlertaModal('Usuário excluído com sucesso.', 'Sucesso', 'success');
                    } else {
                        mostrarAlertaModal('Erro ao excluir usuário.', 'Erro', 'danger');
                    }
                } catch (err) {
                    console.error(err);
                    mostrarAlertaModal('Erro de conexão.', 'Erro de Conexão', 'danger');
                }
            });
        });
    });
}