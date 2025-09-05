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
        document.querySelector('[data-stat="total-usuarios"]').textContent = data.stats.total_usuarios;
        document.querySelector('[data-stat="total-notificacoes"]').textContent = data.stats.total_notificacoes;

        // Atualizar lista de usuários
        const tabelaUsuarios = document.querySelector('#usuarios table tbody');
        
        // Fazer uma requisição separada para obter a lista completa de usuários
        const responseUsuarios = await fetch('/api/v1/admin/usuarios', {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        
        if (responseUsuarios.ok) {
            const usuarios = await responseUsuarios.json();
            tabelaUsuarios.innerHTML = usuarios.map(usuario => `
                <tr>
                    <td><i class="bi bi-person-circle text-primary me-2"></i>${usuario.nome}</td>
                    <td>${usuario.cpf}</td>
                    <td>${usuario.email}</td>
                    <td>${usuario.endereco || ''}</td>
                    <td>
                        <button class="btn btn-sm btn-primary btn-visualizar-usuario" data-id="${usuario.id}"><i class="bi bi-eye"></i></button>
                        <button class="btn btn-sm btn-warning btn-editar-usuario" data-id="${usuario.id}"><i class="bi bi-pencil"></i></button>
                        <button class="btn btn-sm btn-danger btn-excluir-usuario" data-id="${usuario.id}"><i class="bi bi-trash"></i></button>
                    </td>
                </tr>
            `).join('');
        }

        // Atualizar notificações
        const tabelaNotificacoes = document.querySelector('#notificacoes table tbody');
        tabelaNotificacoes.innerHTML = data.ultimas_notificacoes.map(notif => `
            <tr data-id="${notif.id}" class="${!notif.lida ? 'table-warning' : ''}">
                <td>${notif.mensagem}</td>
                <td>${new Date(notif.data_criacao).toLocaleDateString()}</td>
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

        // Atualizar configurações
        const configContainer = document.querySelector('#form-configuracoes');
        configContainer.innerHTML = data.configuracoes.map(config => `
            <div class="mb-4">
                <label class="form-label">${config.descricao || config.chave}</label>
                <input type="text" class="form-control" data-chave="${config.chave}" value="${config.valor}">
            </div>
        `).join('') + '<button type="submit" class="btn btn-primary">Salvar Configurações</button>';

    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao carregar dados do dashboard');
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
