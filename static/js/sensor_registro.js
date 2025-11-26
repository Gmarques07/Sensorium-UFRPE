// Função para registrar um novo sensor pelo usuário
async function registrarNovoSensor() {
    // Obter os dados do formulário
    const nome = document.getElementById('nomeSensor').value;
    const tipo = document.getElementById('tipoSensor').value;
    const descricao = document.getElementById('descricaoSensor').value;

    // Validar campos obrigatórios
    if (!nome || !tipo) {
        mostrarAlerta('Preencha todos os campos obrigatórios!', 'danger');
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
            mostrarAlerta('Sensor registrado com sucesso!', 'success');

            // Mostrar chave de API para o usuário copiar (se disponível)
            if (data.chave_api) {
                document.getElementById('chaveApiGerada').value = data.chave_api;
                document.getElementById('chaveApiContainer').classList.remove('d-none');
            } else {
                document.getElementById('chaveApiContainer').classList.add('d-none');
            }
            document.getElementById('resultadoRegistro').classList.remove('d-none');

            // Limpar o formulário
            document.getElementById('formRegistrarSensor').reset();

            // Atualizar a lista de sensores
            await carregarSensoresUsuario();

            // Adicionar temporizador para esconder a mensagem após 10 segundos
            setTimeout(() => {
                document.getElementById('resultadoRegistro').classList.add('d-none');
                document.getElementById('chaveApiContainer').classList.add('d-none');
                // Limpar o campo da chave API
                document.getElementById('chaveApiGerada').value = '';
            }, 10000); // 10000 milissegundos = 10 segundos

            // Adicionar listener para o botão de fechar do alerta
            const closeBtn = document.querySelector('#resultadoRegistro .btn-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', function() {
                    document.getElementById('resultadoRegistro').classList.add('d-none');
                    document.getElementById('chaveApiContainer').classList.add('d-none');
                    // Limpar o campo da chave API
                    document.getElementById('chaveApiGerada').value = '';
                });
            }
        } else {
            const error = await response.json();
            mostrarAlerta(`Erro ao registrar sensor: ${error.detail || 'Erro desconhecido'}`, 'danger');
        }
    } catch (error) {
        mostrarAlerta(`Erro de conexão: ${error.message}`, 'danger');
    } finally {
        // Restaurar o botão
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// Função para copiar a chave de API para a área de transferência
function copiarChaveApi() {
    const chaveApiInput = document.getElementById('chaveApiGerada');
    chaveApiInput.select();
    document.execCommand('copy');

    // Mostrar feedback
    const btn = document.getElementById('btnCopiarChaveApi');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="bi bi-check-lg"></i> Copiado!';

    setTimeout(() => {
        btn.innerHTML = originalText;
    }, 2000);
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

    // Adicionar ao container de alertas
    const container = document.getElementById('alertasContainer') || document.body;
    container.insertBefore(alertDiv, container.firstChild);

    // Remover após 5 segundos
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Função para carregar os sensores do usuário
async function carregarSensoresUsuario() {
    try {
        const response = await fetch('/api/v1/locais/', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
            }
        });

        if (response.ok) {
            const sensores = await response.json();
            atualizarListaSensores(sensores);
        }
    } catch (error) {
        console.error('Erro ao carregar sensores:', error);
    }
}

// Função para atualizar a lista de sensores na interface
function atualizarListaSensores(sensores) {
    const container = document.getElementById('sensores-container');
    if (!container) return;

    if (sensores.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4">
                <i class="bi bi-cpu fs-1 text-muted"></i>
                <h5 class="mt-3 text-muted">Nenhum sensor registrado</h5>
                <p class="text-muted">Registre seu primeiro sensor usando o formulário acima</p>
            </div>
        `;
        return;
    }

    let html = '<div class="row g-4">';
    sensores.forEach(sensor => {
        html += `
        <div class="col-md-6 col-lg-4">
            <div class="card sensor-card h-100 border-0 shadow-sm">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-3">
                        <div>
                            <h5 class="card-title">${sensor.nome}</h5>
                            <span class="badge bg-primary">${sensor.tipo}</span>
                        </div>
                        <div class="dropdown">
                            <button class="btn btn-sm btn-outline-secondary dropdown-toggle" type="button"
                                    data-bs-toggle="dropdown" aria-expanded="false">
                                <i class="bi bi-three-dots"></i>
                            </button>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="#" onclick="copiarChaveSensor('${sensor.chave_api}')">
                                    <i class="bi bi-key me-2"></i>Copiar Chave API
                                </a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item text-danger" href="#" onclick="excluirSensor(${sensor.id})">
                                    <i class="bi bi-trash me-2"></i>Excluir Sensor
                                </a></li>
                            </ul>
                        </div>
                    </div>

                    ${sensor.descricao ? `<p class="card-text text-muted">${sensor.descricao}</p>` : ''}

                    <div class="mt-3">
                        <small class="text-muted">
                            <i class="bi bi-calendar me-1"></i>
                            Criado em: ${new Date(sensor.data_criacao).toLocaleDateString('pt-BR')}
                        </small>
                        <div class="mt-2">
                            <small class="text-muted d-block">Chave API:</small>
                            <code class="small" style="word-break: break-all;">${sensor.chave_api || 'Não gerada'}</code>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        `;
    });
    html += '</div>';

    container.innerHTML = html;
}

// Função para copiar a chave de API de um sensor existente
function copiarChaveSensor(chaveApi) {
    navigator.clipboard.writeText(chaveApi).then(() => {
        mostrarAlerta('Chave API copiada para a área de transferência!', 'success');
    }).catch(err => {
        mostrarAlerta('Erro ao copiar chave API', 'danger');
        console.error('Erro ao copiar chave API:', err);
    });
}

// Função para excluir um sensor
async function excluirSensor(sensorId) {
    if (!confirm('Tem certeza que deseja excluir este sensor? Esta ação não pode ser desfeita.')) {
        return;
    }

    try {
        const response = await fetch(`/api/v1/locais/${sensorId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
            }
        });

        if (response.ok) {
            mostrarAlerta('Sensor excluído com sucesso!', 'success');
            await carregarSensoresUsuario(); // Atualizar a lista de sensores na mesma seção
        } else {
            const error = await response.json();
            mostrarAlerta(`Erro ao excluir sensor: ${error.detail || 'Erro desconhecido'}`, 'danger');
        }
    } catch (error) {
        mostrarAlerta(`Erro de conexão: ${error.message}`, 'danger');
    }
}

// Adicionar evento de submissão ao formulário
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('formRegistrarSensor');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            registrarNovoSensor();
        });
    }

    // Carregar sensores do usuário ao carregar a página (se estivermos na seção de sensores)
    const sensoresSection = document.getElementById('sensores');
    if (sensoresSection && sensoresSection.classList.contains('active')) {
        carregarSensoresUsuario();
    }
});