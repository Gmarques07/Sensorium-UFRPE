// Função para carregar os dados do dashboard
async function carregarDadosDashboard() {
    try {
        const accessToken = localStorage.getItem('adminAccessToken');
        if (!accessToken) {
            window.location.href = '/login_admin.html';
            return;
        }

        const response = await fetch('/api/v1/admin/dashboard', {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                // Token inválido ou expirado
                localStorage.removeItem('adminAccessToken');
                window.location.href = '/login_admin.html';
                return;
            }
            throw new Error('Erro ao carregar dados do dashboard');
        }

        const data = await response.json();
        
        // Atualizar estatísticas
        const totalUsuariosEl = document.querySelector('[data-stat="total-usuarios"]');
        const totalNotificacoesEl = document.querySelector('[data-stat="total-notificacoes"]');
        
        if (totalUsuariosEl) {
            totalUsuariosEl.textContent = data.stats.total_usuarios || 0;
        }
        
        if (totalNotificacoesEl) {
            totalNotificacoesEl.textContent = data.stats.total_notificacoes || 0;
        }

        // Atualizar lista de usuários apenas se não estiver usando template e se houver dados
        const tabelaUsuarios = document.querySelector('#usuarios table tbody');
        if (tabelaUsuarios && data.usuarios_recentes && data.usuarios_recentes.length > 0) {
            tabelaUsuarios.innerHTML = data.usuarios_recentes.map(usuario => `
                <tr>
                    <td><i class="bi bi-person-circle text-primary me-2"></i>${usuario.nome || ''}</td>
                    <td>${usuario.email || ''}</td>
                    <td>${usuario.endereco || ''}</td>
                    <td>
                        <button class="btn btn-sm btn-primary btn-visualizar-usuario" data-id="${usuario.id}"><i class="bi bi-eye"></i></button>
                        <a href="/gerenciar_sensores/${usuario.id}" class="btn btn-sm btn-warning"><i class="bi bi-pencil"></i></a>
                        <button class="btn btn-sm btn-danger btn-excluir-usuario" data-id="${usuario.id}"><i class="bi bi-trash"></i></button>
                    </td>
                </tr>
            `).join('');
        }

        // Atualizar notificações apenas se não estiver usando template
        const tabelaNotificacoes = document.querySelector('#notificacoes-lista');
        if (tabelaNotificacoes && data.ultimas_notificacoes) {
            tabelaNotificacoes.innerHTML = data.ultimas_notificacoes.map(notif => `
                <tr data-id="${notif.id}" class="${!notif.lida ? 'table-warning' : ''}">
                    <td>${notif.tipo || ''}</td>
                    <td>${notif.titulo || ''}</td>
                    <td>${notif.mensagem || ''}</td>
                    <td>${notif.data_criacao ? new Date(notif.data_criacao).toLocaleDateString() : ''}</td>
                    <td>
                        <span class="badge ${notif.lida ? 'bg-success' : 'bg-warning'}">
                            ${notif.lida ? 'Lida' : 'Não lida'}
                        </span>
                    </td>
                    <td>
                        ${!notif.lida ? `
                            <button class="btn btn-sm btn-success btn-marcar-lida"><i class="bi bi-check-lg"></i></button>
                        ` : ''}
                    </td>
                </tr>
            `).join('');
        }

        // Atualizar configurações apenas se não estiver usando template
        const configContainer = document.querySelector('#form-configuracoes');
        if (configContainer && data.configuracoes) {
            configContainer.innerHTML = data.configuracoes.map(config => `
                <div class="mb-4">
                    <label class="form-label">${config.descricao || config.chave}</label>
                    <input type="text" class="form-control" data-chave="${config.chave}" value="${config.valor || ''}">
                </div>
            `).join('') + '<button type="submit" class="btn btn-primary">Salvar Configurações</button>';
        }

    } catch (error) {
        console.error('Erro:', error);
        // Only show alert if we're not using server-side rendering
        if (!document.querySelector('#usuarios table tbody tr')) {
            alert('Erro ao carregar dados do dashboard: ' + error.message);
        }
    }
}

// Carregar dados quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    carregarDadosDashboard();
    
    // Recarregar dados a cada 30 segundos
    setInterval(carregarDadosDashboard, 30000);
});

// Adicionar funcionalidade de logout
document.getElementById('logout-button').addEventListener('click', (e) => {
    e.preventDefault();
    localStorage.removeItem('adminAccessToken');
    window.location.href = '/login_admin.html';
});
