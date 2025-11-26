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
    const activePanel = document.getElementById(sectionId);
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

// Função para mostrar alertas
function mostrarAlerta(mensagem, tipo) {
    // Criar elemento de alerta
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${tipo} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${mensagem}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    // Adicionar ao container principal
    const main = document.querySelector('main');
    main.insertBefore(alertDiv, main.firstChild);

    // Remover após 5 segundos
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Função para copiar a chave de API
function copiarChaveApi() {
    const chaveInput = document.getElementById('chaveApiGerada');
    if (chaveInput) {
        navigator.clipboard.writeText(chaveInput.value).then(() => {
            mostrarAlerta('Chave API copiada para a área de transferência!', 'success');
        }).catch(err => {
            mostrarAlerta('Erro ao copiar chave API', 'danger');
            console.error('Erro ao copiar chave API:', err);
        });
    }
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
            localStorage.removeItem('adminAccessToken');
            window.location.href = '/login_admin.html';
        });
    }

    // E. Evento para formulário de registro de sensor
    const formRegistrarSensor = document.getElementById('formRegistrarSensor');
    if (formRegistrarSensor) {
        formRegistrarSensor.addEventListener('submit', async function(e) {
            e.preventDefault();
            const form = this;
            const formData = new FormData(form);
            const submitButton = form.querySelector('#btnRegistrarSensor');
            const originalButtonHtml = submitButton.innerHTML;

            submitButton.disabled = true;
            submitButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Registrando...`;

            const payload = {};
            for (const [key, value] of formData.entries()) {
                payload[key] = value;
            }

            try {
                const response = await fetch('/api/v1/locais/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('adminAccessToken')}`
                    },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    const data = await response.json();

                    // Exibir resultado do registro
                    const resultadoRegistro = document.getElementById('resultadoRegistro');
                    const chaveApiContainer = document.getElementById('chaveApiContainer');
                    const chaveApiGerada = document.getElementById('chaveApiGerada');

                    if (chaveApiGerada) {
                        chaveApiGerada.value = data.chave_api;
                    }

                    if (chaveApiContainer) {
                        chaveApiContainer.classList.remove('d-none');
                    }

                    if (resultadoRegistro) {
                        resultadoRegistro.classList.remove('d-none');
                    }

                    // Limpar formulário
                    form.reset();

                    // Atualizar a lista de sensores (recarregar a página ou atualizar a tabela)
                    location.reload();
                } else {
                    const errorData = await response.json();
                    mostrarAlerta(errorData.detail || 'Erro ao registrar sensor', 'danger');
                }
            } catch (error) {
                mostrarAlerta('Erro de conexão ao registrar sensor', 'danger');
            } finally {
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonHtml;
            }
        });
    }

    // --- 2. LÓGICA DE DADOS (API) - Roda depois da UI ---
    iniciarCarregamentoDados();
});


// Função separada para dados (Token Required)
function iniciarCarregamentoDados() {
    const accessToken = localStorage.getItem('adminAccessToken');

    if (!accessToken) {
        console.warn("Sem token de admin. Funcionalidades de API limitadas.");
        // Não redirecionamos imediatamente para não quebrar a UI se o Jinja já renderizou os dados
        return;
    }

    // Interceptor de Fetch Global
    const originalFetch = window.fetch;
    window.fetch = function(input, init = {}) {
        const url = typeof input === 'string' ? input : input.url;
        const headers = new Headers(init.headers || (typeof input !== 'string' && input.headers) || {});
        headers.set('Authorization', `Bearer ${accessToken}`);
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

        newBtn.addEventListener('click', async (e) => {
            const id = newBtn.dataset.id;
            if (!confirm('Tem certeza que deseja excluir este usuário?')) return;

            try {
                const res = await fetch(`/api/v1/admin/usuarios/${id}`, { method: 'DELETE' });
                if (res.ok) {
                    newBtn.closest('tr').remove();
                    const counter = document.querySelector('[data-stat="total-usuarios"]');
                    if(counter) counter.innerText = Math.max(0, parseInt(counter.innerText) - 1);
                } else {
                    alert('Erro ao excluir usuário. Verifique se você está logado.');
                }
            } catch (err) {
                console.error(err);
                alert('Erro de conexão.');
            }
        });
    });

}