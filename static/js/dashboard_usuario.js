// =================================================================
// 1. DEFINIÇÕES DE FUNÇÕES GLOBAIS
// Todas as funções são definidas aqui no escopo global para garantir
// que estejam disponíveis quando chamadas.
// =================================================================

function showSection(event, sectionId) {
  if (event) event.preventDefault();

  const allLinks = document.querySelectorAll('.sidebar-container .nav-link');

  allLinks.forEach(link => {
    link.classList.remove('active');
    link.style.borderLeft = '';
  });

  const targetLink = document.querySelector(`.nav-link[href="#${sectionId}"]`);
  if (targetLink) {
    targetLink.classList.add('active');
  }

  document.querySelectorAll('.section-panel').forEach(panel => panel.classList.remove('active'));

  let section = document.getElementById(sectionId);
  if (!section) {
      console.warn(`Seção "${sectionId}" não encontrada. Redirecionando para dashboard.`);
      sectionId = 'dashboard';
      section = document.getElementById(sectionId);
      history.replaceState({}, '', `#${sectionId}`);

      const newTargetLink = document.querySelector(`.nav-link[href="#${sectionId}"]`);
      if (newTargetLink) newTargetLink.classList.add('active');
  }

  if (section) section.classList.add('active');

  const sidebarEl = document.getElementById('sidebarMenu');
  if (sidebarEl && sidebarEl.classList.contains('show') && window.bootstrap) {
    const bsOffcanvas = bootstrap.Offcanvas.getInstance(sidebarEl);
    if (bsOffcanvas) bsOffcanvas.hide();
  }

  if (sectionId === 'alertas') {
    const sensorSelect = document.getElementById('sensorAlerta');
    if (sensorSelect && sensorSelect.options.length <= 1) {
      carregarSensoresParaAlertas();
    }
  }

  if (sectionId === 'sensores') {
    setTimeout(() => {
      const container = document.getElementById('sensores-container');
      const hasDetailView = container && container.querySelector('#visualizacao-sensores');
      if (hasDetailView) return;
      toggleSensorView('manage');
    }, 100);
  }

  history.pushState({}, '', `#${sectionId}`);
}

function handleHashChange() {
    const hash = window.location.hash.slice(1) || 'dashboard';
    showSection(null, hash);
}

function carregarSensoresGerenciamento() {
  const container = document.getElementById('sensores-container');
  if (!container) return;

  // Limpar a flag quando retornar ao modo de gerenciamento
  sessionStorage.removeItem('navigatedToDetailedView');

  container.innerHTML = `<div class="text-center py-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Carregando...</span></div><p class="mt-2 text-muted">Carregando sensores...</p></div>`;

  fetch('/api/v1/locais/', {
      credentials: 'include'
    })
    .then(response => {
      if (!response.ok) throw new Error('Erro ao carregar sensores');
      return response.json();
    })
    .then(sensores => {
      atualizarListaSensoresUsuario(sensores);
    })
    .catch(error => {
      console.error('Erro ao carregar sensores:', error);
      container.innerHTML = `<div class="text-center py-4"><i class="bi bi-exclamation-circle text-muted fs-1 mb-2"></i><p class="mb-0">Erro ao carregar sensores.</p></div>`;
    });
}

function atualizarListaSensoresUsuario(sensores) {
  const container = document.getElementById('sensores-container');
  if (!container) return;

  if (!sensores || sensores.length === 0) {
    container.innerHTML = `<div class="text-center py-4"><i class="bi bi-cpu fs-1 text-muted"></i><h5 class="mt-3 text-muted">Nenhum sensor registrado</h5><p class="text-muted">Registre seu primeiro sensor usando o formulário acima</p></div>`;
    return;
  }

  let html = `
  <div class="d-flex justify-content-between align-items-center mb-3">
    <h5 class="mb-0">Meus Sensores</h5>
    <button type="button" class="btn btn-sm btn-outline-primary" onclick="toggleSensorView('detailed')">
      <i class="bi bi-eye me-1"></i>Visualizar Dados
    </button>
  </div>
  <div class="row g-4">`;
  sensores.forEach(sensor => {
    html += `
    <div class="col-md-6 col-lg-4" id="sensor-card-${sensor.id}">
      <div class="card sensor-card h-100 border-0 shadow-sm">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-start mb-3">
            <div>
              <h5 class="card-title">${sensor.nome}</h5>
              <span class="badge bg-primary">${sensor.tipo}</span>
            </div>
          </div>
          ${sensor.descricao ? `<p class="card-text text-muted">${sensor.descricao}</p>` : ''}
          <div class="mt-3">
            <small class="text-muted"><i class="bi bi-calendar me-1"></i>Criado em: ${new Date(sensor.data_criacao).toLocaleDateString('pt-BR')}</small>
          </div>
        </div>
      </div>
    </div>`;
  });
  html += '</div>';
  container.innerHTML = html;
}

function copiarChaveSensor(chaveApi) {
  navigator.clipboard.writeText(chaveApi).then(() => {
    mostrarNotificacao('Chave API copiada para a área de transferência!', 'success');
  }).catch(err => {
    mostrarNotificacao('Erro ao copiar chave API', 'danger');
    console.error('Erro ao copiar chave API:', err);
  });
}


function toggleSensorView(viewType) {
  const container = document.getElementById('sensores-container');
  if (!container) return;
  if (viewType === 'manage') {
    carregarSensoresGerenciamento();
  } else if (viewType === 'detailed') {
    // Marcar que o usuário navegou ativamente para o modo detalhado
    sessionStorage.setItem('navigatedToDetailedView', 'true');
    container.innerHTML = `<div class="text-center py-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Carregando...</span></div><p class="mt-2 text-muted">Carregando dados dos sensores...</p></div>`;
    carregarDadosSensores();
  }
}

function montarQueryRelatorio(form) {
    const params = new URLSearchParams();
    const inicio = form.inicio.value;
    const fim = form.fim.value;
    const dispositivo = form.dispositivo.value;
    if (inicio) params.append('inicio', inicio);
    if (fim) params.append('fim', fim);
    if (dispositivo) params.append('dispositivo', dispositivo);
    return params.toString();
}

function carregarDadosSensores() {
  fetch('/api/v1/usuarios/dashboard-dados', {
      credentials: 'include'
    })
    .then(response => {
      if (!response.ok) throw new Error('Erro ao carregar dados dos sensores');
      return response.json();
    })
    .then(data => {
      console.log('Dados dos sensores:', data);
      localStorage.setItem('sensores', JSON.stringify(data.dispositivos));
      const totalDispositivos = document.getElementById('total-dispositivos');
      if (totalDispositivos) totalDispositivos.textContent = data.dispositivos.length;

      const selectDispositivos = document.getElementById('dispRel');
      if (selectDispositivos) {
        selectDispositivos.innerHTML = '<option value="">Todos</option>';
        data.dispositivos.forEach(disp => {
          const option = document.createElement('option');
          option.value = disp.id;
          option.textContent = disp.nome;
          selectDispositivos.appendChild(option);
        });
      }

      const container = document.getElementById('sensores-container');
      // Verificar se é um recarregamento da página usando sessionStorage
      // Marcar a navegação ao entrar em modo detalhado
      const isPageReload = !sessionStorage.getItem('navigatedToDetailedView');

      if (isPageReload) {
        // Ao recarregar a página, mostrar o modo de gerenciamento como padrão
        carregarSensoresGerenciamento();
      } else {
        // Foi uma navegação ativa para o modo detalhado, manter esse estado
        renderizarSensores(data);
      }
    })
    .catch(error => {
      console.error('Erro ao carregar dados dos sensores:', error.message);
      const container = document.getElementById('sensores-container');
      if (container) container.innerHTML = `<div class="text-center py-4"><i class="bi bi-exclamation-circle text-muted fs-1 mb-2 d-block"></i><p class="mb-0">Erro ao carregar dados dos sensores.</p></div>`;
    });
}

function renderizarSensores(data) {
  const container = document.getElementById('sensores-container');
  const isManagementView = container && container.querySelector('.sensor-card');
  const isDetailedView = container && container.querySelector('#visualizacao-sensores');

  if (isManagementView && !isDetailedView) {
      // Em modo gerenciamento, não renderiza a visão detalhada
  }

  if (!data.dispositivos || data.dispositivos.length === 0) {
    container.innerHTML = `<div class="text-center py-4"><i class="bi bi-exclamation-circle text-muted fs-1 mb-2 d-block"></i><p class="mb-0">Nenhum dispositivo encontrado.</p></div>`;
    return;
  }

  let html = `
  <div class="mb-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <label for="selectDispositivo" class="form-label fw-semibold">Selecione o Dispositivo:</label>
      <div class="d-flex gap-2">
        <button type="button" class="btn btn-sm btn-outline-secondary" onclick="toggleSensorView('manage')"><i class="bi bi-gear me-1"></i>Gerenciar Sensores</button>
      </div>
    </div>
    <select class="form-select w-auto d-inline-block" id="selectDispositivo" onchange="mostrarDispositivoSelecionado()">`;
  data.dispositivos.forEach((disp) => { html += `<option value="${disp.nome}">${disp.nome}</option>`; });
  html += `</select></div><div id="visualizacao-sensores" data-view="detailed">`;

  data.dispositivos.forEach((disp, index) => {
    const dispositivoId = disp.nome.replace(/\s/g, '_');
    const phData = data.ph_por_dispositivo[disp.nome];
    const nivelData = data.nivel_por_dispositivo[disp.nome];
    const umidadeData = data.umidade_por_dispositivo[disp.nome];

    html += `<div class="dispositivo-panel" id="panel-${dispositivoId}" style="display: ${index === 0 ? 'block' : 'none'};">
        <div class="row g-4">`;

    // pH Card
    if (phData) {
        html += `<div class="col-12 mb-4">
                <div class="card border-0 shadow-sm h-100">
                    <div class="card-header bg-primary text-white"><i class="bi bi-droplet-half me-2"></i>pH da Água</div>
                    <div class="card-body">`;
        if (phData && phData.atual) {
            const ph = phData.atual.ph;
            const badgeClass = ph < 6.5 ? 'bg-danger' : (ph > 8.5 ? 'bg-warning' : 'bg-success');
            const status = ph < 6.5 ? 'Ácido' : (ph > 8.5 ? 'Alcalino' : 'Neutro');
            html += `<div class="text-center mb-4">
                        <div class="display-4 text-primary mb-2">${ph}</div>
                        <span class="badge ${badgeClass} fs-6">${status}</span>
                        <p class="text-muted mt-3 mb-0"><i class="bi bi-clock me-1"></i>Última atualização: ${phData.atual.data}</p>
                    </div>
                    <div class="mt-4 position-relative" style="width: 100%; height: 100px;"><canvas id="phChart-${dispositivoId}"></canvas></div>`;
        } else {
            html += `<div class="text-center py-5"><i class="bi bi-exclamation-circle fs-1 text-muted mb-3"></i><p class="text-muted mb-0">Nenhum dado de pH disponível.</p></div>`;
        }
        html += `</div></div></div>`;
    }

    // pH History Card
    if (phData) {
        html += `<div class="col-12 mb-4"><div class="card border-0 shadow-sm"><div class="card-header bg-primary text-white"><i class="bi bi-graph-up me-2"></i>Histórico de pH</div><div class="card-body"><ul class="list-group list-group-flush">`;
        if (phData && phData.historico && phData.historico.length > 0) {
            phData.historico.forEach(item => { html += `<li class="list-group-item d-flex justify-content-between align-items-center"><span><i class="bi bi-calendar me-2"></i>${item.data}</span><span class="badge bg-primary">pH ${item.ph}</span></li>`; });
        } else {
            html += `<li class="list-group-item text-muted">Nenhum registro encontrado</li>`;
        }
        html += `</ul></div></div></div>`;
    }

    // Nível Card
    if (nivelData) {
        html += `<div class="col-12 mb-4">
                <div class="card border-0 shadow-sm h-100">
                    <div class="card-header bg-primary text-white"><i class="bi bi-water me-2"></i>Nível de Água</div>
                    <div class="card-body">`;
        if (nivelData && nivelData.atual) {
            const status = nivelData.atual.status;
            const boia = nivelData.atual.boia;
            const statusClass = status === 'ALTO' ? 'text-success' : 'text-warning';
            const badgeClass = status === 'ALTO' ? 'bg-success' : 'bg-warning';
            const boiaClass = boia === 1 ? 'bg-primary' : 'bg-secondary';
            const boiaText = boia === 1 ? 'Ativada' : 'Desativada';
            html += `<div class="text-center mb-4">
                        <div class="mb-4"><i class="bi bi-water fs-1 ${statusClass}"></i></div>
                        <div class="display-6 mb-2"><span class="badge ${badgeClass} fs-5">${status}</span></div>
                        <div class="mt-4"><p class="mb-2">Status da Boia:</p><span class="badge ${boiaClass} fs-6">${boiaText}</span></div>
                        <p class="text-muted mt-4 mb-0"><i class="bi bi-clock me-1"></i>Última atualização: ${nivelData.atual.data}</p>
                    </div>
                    <div class="mt-4 position-relative" style="width: 100%; height: 100px;"><canvas id="nivelChart-${dispositivoId}"></canvas></div>`;
        } else {
            html += `<div class="text-center py-5"><i class="bi bi-exclamation-circle fs-1 text-muted mb-3"></i><p class="text-muted mb-0">Nenhum dado de nível disponível.</p></div>`;
        }
        html += `</div></div></div>`;
    }

    // Nível History Card
    if (nivelData) {
        html += `<div class="col-12 mb-4"><div class="card border-0 shadow-sm"><div class="card-header bg-primary text-white"><i class="bi bi-clock-history me-2"></i>Histórico de Nível</div><div class="card-body"><ul class="list-group list_group_flush">`;
        if (nivelData && nivelData.historico && nivelData.historico.length > 0) {
            nivelData.historico.forEach(item => { const badgeClass = item.status === 'ALTO' ? 'bg-success' : 'bg-warning'; html += `<li class="list-group-item d-flex justify_content_between align-items-center"><span><i class="bi bi_calendar me-2"></i>${item.data}</span><span class="badge ${badgeClass}">${item.status}</span></li>`; });
        } else {
            html += `<li class="list-group-item text-muted">Nenhum registro encontrado</li>`;
        }
        html += `</ul></div></div></div>`;
    }

    // Umidade Card
    if (umidadeData) {
        html += `<div class="col-12 mb-4">
                <div class="card border-0 shadow-sm h-100">
                    <div class="card-header bg-primary text-white"><i class="bi bi-moisture me-2"></i>Umidade</div>
                    <div class="card-body">`;
        if (umidadeData && umidadeData.atual) {
            const umidade = umidadeData.atual.umidade_percentual;
            const status = umidadeData.atual.status;
            let badgeClass = 'bg-success';
            if (status === 'SECO') badgeClass = 'bg-warning';
            if (status === 'ENCHARCADO') badgeClass = 'bg-danger';
            html += `<div class="text-center mb-4">
                        <div class="display-4 text-primary mb-2">${umidade.toFixed(1)}<small class="fs-4">%</small></div>
                        <span class="badge ${badgeClass} fs-6">${status}</span>
                        <p class="text-muted mt-3 mb-0"><i class="bi bi-clock me-1"></i>Última atualização: ${umidadeData.atual.data}</p>
                    </div>
                    <div class="mt-4 position-relative" style="width: 100%; height: 100px;"><canvas id="umidadeChart-${dispositivoId}"></canvas></div>`;
        } else {
            html += `<div class="text-center py-5"><i class="bi bi-exclamation-circle fs-1 text-muted mb-3"></i><p class="text-muted mb-0">Nenhum dado de umidade disponível.</p></div>`;
        }
        html += `</div></div></div>`;
    }

    // Umidade History Card
    if (umidadeData) {
        html += `<div class="col-12 mb-4"><div class="card border-0 shadow-sm"><div class="card-header bg-primary text-white"><i class="bi bi-moisture me-2"></i>Histórico de Umidade</div><div class="card-body"><ul class="list-group list_group_flush">`;
        if (umidadeData && umidadeData.historico && umidadeData.historico.length > 0) {
            umidadeData.historico.forEach(item => { html += `<li class="list-group-item d-flex justify-content-between align-items-center"><span><i class="bi bi-calendar me-2"></i>${item.data}</span><span class="badge bg-info">${item.umidade_percentual.toFixed(1)}%</span></li>`; });
        } else {
            html += `<li class="list-group-item text-muted">Nenhum registro encontrado</li>`;
        }
        html += `</ul></div></div></div>`;
    }

    html += `</div></div>`; // Close .row and .dispositivo-panel
  });

  html += `</div>`;
  container.innerHTML = html;

  if (typeof Chart === 'undefined') {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
    script.onload = () => criarGraficos(data);
    document.head.appendChild(script);
  } else {
    criarGraficos(data);
  }
}

function criarGraficos(data) {
  data.dispositivos.forEach(disp => {
    const dispositivoId = disp.nome.replace(/\s/g, '_');
    const phData = data.ph_por_dispositivo[disp.nome];
    const nivelData = data.nivel_por_dispositivo[disp.nome];
    const umidadeData = data.umidade_por_dispositivo[disp.nome];

    const configComum = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { backgroundColor: 'rgba(0, 0, 0, 0.8)', titleFont: { family: "'Poppins', sans-serif" }, bodyFont: { family: "'Poppins', sans-serif" }, padding: 12, cornerRadius: 8, displayColors: false } }, scales: { y: { beginAtZero: false, grid: { color: 'rgba(0, 0, 0, 0.05)' }, ticks: { font: { family: "'Poppins', sans-serif" } } }, x: { grid: { display: false }, ticks: { font: { family: "'Poppins', sans-serif" } } } }, animation: { duration: 2000, easing: 'easeOutQuart' }, interaction: { intersect: false, mode: 'index' } };

    const phCtx = document.getElementById(`phChart-${dispositivoId}`);
    if (phCtx && phData && phData.historico) {
      const historicoPh = phData.historico.reverse();
      new Chart(phCtx, { type: 'line', data: { labels: historicoPh.map(item => item.data), datasets: [{ label: 'Histórico de pH', data: historicoPh.map(item => item.ph), borderColor: '#004183', backgroundColor: 'rgba(0,65,131,0.1)', borderWidth: 3, pointBackgroundColor: '#004183', pointBorderColor: '#fff', pointRadius: 6, pointHoverRadius: 8, fill: true, tension: 0.4 }] }, options: configComum });
    }

    const nivelCtx = document.getElementById(`nivelChart-${dispositivoId}`);
    if (nivelCtx && nivelData && nivelData.historico) {
      const historicoNivel = nivelData.historico.reverse();
      new Chart(nivelCtx, { type: 'line', data: { labels: historicoNivel.map(item => item.data), datasets: [{ label: 'Histórico de Nível', data: historicoNivel.map(item => item.status === 'ALTO' ? 2 : (item.status === 'BAIXO' ? 1 : 0)), borderColor: '#34c759', backgroundColor: 'rgba(52,199,89,0.1)', borderWidth: 3, pointBackgroundColor: '#34c759', pointBorderColor: '#fff', pointRadius: 6, pointHoverRadius: 8, fill: true, tension: 0.4 }] }, options: { ...configComum, scales: { ...configComum.scales, y: { beginAtZero: true, min: 0, max: 2, grid: { color: 'rgba(0, 0, 0, 0.05)' }, ticks: { callback: function(value) { if (value === 2) return 'ALTO'; if (value === 1) return 'BAIXO'; return ''; } } } } } });
    }

    const umidadeCtx = document.getElementById(`umidadeChart-${dispositivoId}`);
    if (umidadeCtx && umidadeData && umidadeData.historico) {
        const historicoUmidade = umidadeData.historico.reverse();
        new Chart(umidadeCtx, {
            type: 'line',
            data: {
                labels: historicoUmidade.map(item => item.data),
                datasets: [{
                    label: 'Histórico de Umidade',
                    data: historicoUmidade.map(item => item.umidade_percentual),
                    borderColor: '#8a6d3b', // Cor terrosa/marrom
                    backgroundColor: 'rgba(138, 109, 59, 0.1)',
                    borderWidth: 3,
                    pointBackgroundColor: '#8a6d3b',
                    pointBorderColor: '#fff',
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: { ...configComum, scales: { ...configComum.scales, y: { ...configComum.scales.y, beginAtZero: true, suggestedMax: 100 } } }
        });
    }
  });
}

function mostrarDispositivoSelecionado() {
  var select = document.getElementById('selectDispositivo');
  var valor = select.value.replace(/\s/g, '_');
  var paineis = document.querySelectorAll('.dispositivo-panel');
  paineis.forEach(function(p) { p.style.display = 'none'; });
  var painelAtivo = document.getElementById('panel-' + valor);
  if (painelAtivo) painelAtivo.style.display = 'block';
  localStorage.setItem('dispositivoSelecionado', select.value);
}

function carregarSensoresParaAlertas() {
  const select = document.getElementById('sensorAlerta');
  select.innerHTML = '<option value="">Selecione um sensor</option>';
  fetch('/api/v1/usuarios/dashboard-dados', {
      credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
      localStorage.setItem('sensores', JSON.stringify(data.dispositivos));
      data.dispositivos.forEach(disp => {
        const option = document.createElement('option');
        option.value = disp.id;
        option.textContent = disp.nome;
        select.appendChild(option);
      });
      const selectRelatorios = document.getElementById('dispRel');
      if (selectRelatorios) {
        selectRelatorios.innerHTML = '<option value="">Todos</option>';
        data.dispositivos.forEach(disp => {
          const option = document.createElement('option');
          option.value = disp.id;
          option.textContent = disp.nome;
          selectRelatorios.appendChild(option);
        });
      }
    })
    .catch(error => {
      console.error('Erro ao carregar sensores para alertas:', error);
      select.innerHTML = '<option value="">Erro ao carregar sensores</option>';
    });
}

function atualizarCamposSensor(tipoSensor) {
  const campoSelect = document.getElementById('campoAlerta');
  campoSelect.innerHTML = '<option value="">Campo</option>';
  const camposPorTipo = { 'PH': [{value: 'ph', text: 'pH'}], 'BOIA': [{value: 'valor', text: 'Valor (Boia)'}, {value: 'status', text: 'Status'}], 'UMIDADE': [{value: 'umidade_percentual', text: 'Umidade (%)'}, {value: 'raw', text: 'Valor Raw'}, {value: 'status', text: 'Status'}] };
  if (camposPorTipo[tipoSensor]) {
    camposPorTipo[tipoSensor].forEach(campo => {
      const option = document.createElement('option');
      option.value = campo.value;
      option.textContent = campo.text;
      campoSelect.appendChild(option);
    });
  }
}

function carregarAlertasConfigurados() {
  fetch('/api/v1/regras-alerta/', {
      credentials: 'include'
    })
    .then(response => {
      if (!response.ok) throw new Error('Erro ao carregar alertas');
      return response.json();
    })
    .then(alertas => {
      const container = document.getElementById('alertas-container');
      if (!alertas || alertas.length === 0) {
        container.innerHTML = `<div class="text-center py-4"><i class="bi bi-bell-slash text-muted fs-1 mb-3"></i><p class="text-muted mb-0">Nenhum alerta configurado.</p><p class="text-muted small">Configure seus primeiros alertas usando o formulário acima.</p></div>`;
        return;
      }
      let html = '<div class="table-responsive"><table class="table table-hover">';
      html += `<thead><tr><th>Sensor</th><th>Regra</th><th>Mensagem</th><th>Status</th><th>Ações</th></tr></thead><tbody>`;
      alertas.forEach(alerta => {
        const sensorNome = obterNomeSensor(alerta.local_id);
        html += `<tr><td>${sensorNome}</td><td>${alerta.campo_sensor} ${alerta.operador} ${alerta.valor_limite}</td><td>${alerta.mensagem_alerta || 'Alerta personalizado'}</td><td><span class="badge ${alerta.ativa ? 'bg-success' : 'bg-secondary'}">${alerta.ativa ? 'Ativo' : 'Inativo'}</span></td><td><button class="btn btn-outline-danger btn-sm" onclick="excluirAlerta(${alerta.id})" title="Excluir alerta"><i class="bi bi-trash"></i></button></td></tr>`;
      });
      html += '</tbody></table></div>';
      container.innerHTML = html;
    })
    .catch(error => {
      console.error('Erro ao carregar alertas configurados:', error);
      const container = document.getElementById('alertas-container');
      container.innerHTML = `<div class="text-center py-4"><i class="bi bi-exclamation-circle text-muted fs-1 mb-2 d-block"></i><p class="mb-0">Erro ao carregar alertas configurados.</p></div>`;
    });
}

function obterNomeSensor(localId) {
  try {
    const sensores = JSON.parse(localStorage.getItem('sensores')) || [];
    const sensor = sensores.find(s => s.id == localId);
    return sensor ? sensor.nome : `Sensor ${localId}`;
  } catch (e) {
    console.error('Erro ao obter nome do sensor:', e);
    return `Sensor ${localId}`;
  }
}

function excluirAlerta(alertaId) {
  confirmarAcao('Excluir Alerta', 'Tem certeza que deseja excluir este alerta?', () => {
      fetch(`/api/v1/regras-alerta/${alertaId}`, {
          method: 'DELETE',
          credentials: 'include'
        })
      .then(response => {
        if (response.ok) {
          carregarAlertasConfigurados();
          mostrarAlertaModal('Alerta excluído com sucesso!', 'Sucesso', 'success');
        } else {
          return response.json().then(data => { throw new Error(data.detail || 'Erro ao excluir alerta'); });
        }
      })
      .catch(error => {
        console.error('Erro:', error);
        mostrarAlertaModal(error.message || 'Erro ao excluir alerta.', 'Erro', 'danger');
      });
  });
}

function limparFormularioAlerta() {
  document.getElementById('formCriarAlerta').reset();
  document.getElementById('campoAlerta').innerHTML = '<option value="">Campo</option>';
}

function fecharVisualizacaoRelatorio() {
  const container = document.getElementById('relatorio-visualizacao');
  if (container) container.classList.add('d-none');
}

// =================================================================
// 2. INICIALIZAÇÃO
// Código que roda após o carregamento completo do DOM.
// =================================================================

document.addEventListener('DOMContentLoaded', function() {
  // Limpar a flag de navegação detalhada ao carregar a página
  // Isso garante que ao recarregar a página, volte ao modo de gerenciamento
  sessionStorage.removeItem('navigatedToDetailedView');

  // Inicializa a navegação baseada no hash da URL
  handleHashChange();

  // --- Autenticação e Carga de Dados ---
  fetch('/api/v1/usuarios/perfil', {
      credentials: 'include'  // Inclui cookies nas requisições
    })
    .then(response => {
      if (!response.ok) {
        window.location.href = '/login';
        throw new Error('Sessão inválida ou expirada.');
      }
      return response.json();
    })
    .then(user => {
      console.log('Usuário autenticado:', user);
      localStorage.setItem('user', JSON.stringify(user));
      const welcomeMessage = document.getElementById('welcome-message');
      if (welcomeMessage && user.nome) welcomeMessage.textContent = `Olá, ${user.nome}!`;
      carregarDadosSensores();
      carregarAlertasConfigurados();
    })
    .catch(error => {
      console.error('Erro na autenticação inicial:', error.message);
      if (!window.location.pathname.endsWith('/login')) {
        window.location.href = '/login';
      }
    });

  // --- Adiciona Event Listeners ---
  window.addEventListener('hashchange', handleHashChange);

  document.querySelectorAll('a.nav-link[href^="#"], a.stretched-link[href^="#"]').forEach(link => {
    link.addEventListener('click', function(event) {
      const href = this.getAttribute('href');
      if (href && href.startsWith('#')) {
        event.preventDefault();
        const sectionId = href.substring(1);
        showSection(event, sectionId);
      }
    });
  });

  document.getElementById('toggleSenha')?.addEventListener('click', function() {
    // ...
  });

  document.querySelector('#modalEditarPerfil form')?.addEventListener('submit', function(e) {
    // ...
  });

  document.getElementById('formCriarAlerta')?.addEventListener('submit', function(e) {
    // ...
  });

  document.getElementById('tipoSensorAlerta')?.addEventListener('change', function() {
    // ...
  });

  document.getElementById('btnVisualizarRelatorio')?.addEventListener('click', function() {
    const form = document.getElementById('formRelatorios');
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }

    const btn = this;
    const originalContent = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Carregando...';
    btn.disabled = true;

    const queryString = montarQueryRelatorio(form);

    fetch(`/api/v1/relatorios/visualizar?${queryString}`, {
      credentials: 'include'
    })
    .then(response => {
      if (!response.ok) throw new Error('Erro ao carregar relatório');
      return response.json();
    })
    .then(data => {
      const tbody = document.getElementById('tabela-relatorio-corpo');
      tbody.innerHTML = '';

      if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4">Nenhum registro encontrado para o período.</td></tr>';
      } else {
        data.forEach(item => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td class="ps-4">${item.data}</td>
            <td>${item.dispositivo}</td>
            <td><span class="badge bg-light text-dark border">${item.tipo}</span></td>
            <td class="fw-bold">${item.valor}</td>
            <td>${item.status !== '-' ? `<span class="badge ${item.status === 'ALTO' || item.status === 'NORMAL' ? 'bg-success' : 'bg-warning'}">${item.status}</span>` : '-'}</td>
          `;
          tbody.appendChild(tr);
        });
      }

      const container = document.getElementById('relatorio-visualizacao');
      container.classList.remove('d-none');

      // Scroll suave até o resultado
      container.scrollIntoView({ behavior: 'smooth', block: 'start' });
    })
    .catch(error => {
      console.error('Erro:', error);
      mostrarAlertaModal('Erro ao carregar dados do relatório.', 'Erro', 'danger');
    })
    .finally(() => {
      btn.innerHTML = originalContent;
      btn.disabled = false;
    });
  });

  document.getElementById('btnExportCSV')?.addEventListener('click', function() {
    const form = document.getElementById('formRelatorios');
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }
    const queryString = montarQueryRelatorio(form);
    window.open(`/api/v1/relatorios/exportar.csv?${queryString}`, '_blank');
  });

  document.getElementById('btnExportPDF')?.addEventListener('click', function() {
    const form = document.getElementById('formRelatorios');
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }
    const queryString = montarQueryRelatorio(form);
    window.open(`/api/v1/relatorios/exportar.pdf?${queryString}`, '_blank');
  });

  document.getElementById('btnEnviarEmail')?.addEventListener('click', function() {
    const form = document.getElementById('formRelatorios');
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }

    if(!confirm('Deseja enviar este relatório para o seu e-mail cadastrado?')) return;

    const btn = this;
    const originalContent = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Enviando...';
    btn.disabled = true;

    const queryString = montarQueryRelatorio(form);

    fetch(`/api/v1/relatorios/enviar-por-email?${queryString}`, {
      method: 'POST',
      credentials: 'include'
    })
    .then(response => {
      if (response.ok) {
        mostrarAlertaModal('Relatório enviado para o seu e-mail com sucesso!', 'Sucesso', 'success');
      } else {
        return response.json().then(err => { throw new Error(err.detail || 'Erro ao enviar e-mail'); });
      }
    })
    .catch(error => {
      console.error('Erro:', error);
      mostrarAlertaModal(error.message || 'Erro ao enviar relatório por e-mail.', 'Erro', 'danger');
    })
    .finally(() => {
      btn.innerHTML = originalContent;
      btn.disabled = false;
    });
  });

  const logoutButton = document.getElementById('logout-button');
  if (logoutButton) {
    logoutButton.addEventListener('click', function(e) {
      e.preventDefault();

      const modalEl = document.getElementById('modalConfirmLogout');
      if (modalEl) {
          const modal = new bootstrap.Modal(modalEl);
          modal.show();
      } else {
          console.error("Modal de logout não encontrado!");
          if(confirm("Deseja sair da sua conta?")) {
              fetch('/api/v1/auth/logout', {
                  method: 'POST',
                  credentials: 'include'
                })
                  .then(() => {
                      localStorage.removeItem('accessToken');
                      localStorage.removeItem('user');
                      window.location.href = '/login';
                  })
                  .catch(err => console.error('Erro no logout:', err));
          }
      }
    });
  }

  const confirmLogoutBtn = document.getElementById('btnConfirmLogout');
  if (confirmLogoutBtn) {
    confirmLogoutBtn.addEventListener('click', function() {
        fetch('/api/v1/auth/logout', {
            method: 'POST',
            credentials: 'include'
          })
            .then(() => {
                localStorage.removeItem('accessToken');
                localStorage.removeItem('user');
                window.location.href = '/login';
            })
            .catch(err => console.error('Erro no logout:', err));
    });
  }
});
