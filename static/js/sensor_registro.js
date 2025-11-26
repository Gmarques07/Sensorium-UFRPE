// Função para registrar um novo sensor pelo usuário
async function registrarNovoSensor() {
    // Obter os dados do formulário
    const nome = document.getElementById('nomeSensor').value;
    const tipo = document.getElementById('tipoSensor').value;
    const descricao = document.getElementById('descricaoSensor').value;

    // Validar campos obrigatórios
    if (!nome || !tipo) {
        mostrarNotificacao('Preencha todos os campos obrigatórios!', 'warning');
        return;
    }

    // Mostrar spinner de carregamento
    const btn = document.getElementById('btnRegistrarSensor');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Registrando...';
    btn.disabled = true;

    try {
        const response = await fetch('/api/v1/sensores/registrar-sensor', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
            },
            body: JSON.stringify({
                nome: nome,
                tipo: tipo,
                descricao: descricao
            })
        });

        if (response.ok) {
            const data = await response.json();
            
            // Preencher e mostrar o Modal de Sucesso
            const inputKey = document.getElementById('modalApiKeyInput');
            if (inputKey) {
                inputKey.value = data.chave_api;
                const modal = new bootstrap.Modal(document.getElementById('modalSucessoSensor'));
                modal.show();
            } else {
                // Fallback se o modal não existir (improvável)
                mostrarNotificacao('Sensor registrado! Chave: ' + data.chave_api, 'success');
            }

            // Limpar o formulário
            document.getElementById('formRegistrarSensor').reset();

            // Atualizar a lista de sensores (tenta chamar as funções globais se existirem)
            if (typeof carregarSensoresGerenciamento === 'function') {
                carregarSensoresGerenciamento();
            }
            if (typeof carregarDadosSensores === 'function') {
                carregarDadosSensores();
            }

        } else {
            const error = await response.json();
            mostrarNotificacao(`Erro ao registrar sensor: ${error.detail || 'Erro desconhecido'}`, 'danger');
        }
    } catch (error) {
        mostrarNotificacao(`Erro de conexão: ${error.message}`, 'danger');
    } finally {
        // Restaurar o botão
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// Funções auxiliares (duplicadas ou locais) removidas para evitar conflito.
// A lógica de listagem e exclusão deve ser centralizada no dashboard_usuario.js

// Adicionar evento de submissão ao formulário
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('formRegistrarSensor');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            registrarNovoSensor();
        });
    }
});