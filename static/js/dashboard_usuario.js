// Funções de utilidade geral
function showSection(event, sectionId) {
  if (event) event.preventDefault();

  // --- CORREÇÃO FINAL: SELETOR ROBUSTO ---
  // Busca todos os links dentro do container da sidebar (independente de ser nav-pills ou não)
  const allLinks = document.querySelectorAll('.sidebar-container .nav-link');
  
  allLinks.forEach(link => {
    link.classList.remove('active');
    // Limpa qualquer estilo inline que possa estar travando a cor
    link.style.borderLeft = ''; 
    link.style.borderLeftColor = '';
  });

  // Ativa o botão clicado
  if (event && event.currentTarget) {
    event.currentTarget.classList.add('active');
  } else {
    // Se a função foi chamada via código (ex: ao carregar a página)
    const targetLink = document.querySelector(`.nav-link[href="#${sectionId}"]`);
    if (targetLink) targetLink.classList.add('active');
  }

  // Troca os painéis visíveis
  document.querySelectorAll('.section-panel').forEach(panel => panel.classList.remove('active'));
  const section = document.getElementById(sectionId);
  if (section) section.classList.add('active');

  // Fecha o menu no mobile
  const sidebarEl = document.getElementById('sidebarMenu');
  if (sidebarEl && sidebarEl.classList.contains('show') && window.bootstrap) {
    const bsOffcanvas = bootstrap.Offcanvas.getInstance(sidebarEl);
    if (bsOffcanvas) bsOffcanvas.hide();
  }

  // Lógica de Alertas (carregar sensores se necessário)
  if (sectionId === 'alertas') {
    const sensorSelect = document.getElementById('sensorAlerta');
    if (sensorSelect && sensorSelect.options.length <= 1) {
      carregarSensoresParaAlertas();
    }
  }

  // Atualiza a URL
  history.pushState({}, '', `#${sectionId}`);
}

function handleHashChange() {
    const hash = window.location.hash.slice(1) || 'dashboard';
    // Chama showSection passando null como evento
    showSection(null, hash);
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


// Bloco principal de execução quando o DOM está pronto
document.addEventListener('DOMContentLoaded', function() {
  const hash = window.location.hash.slice(1) || 'dashboard';
  
  // --- 1. LIMPEZA INICIAL DA SIDEBAR ---
  // Garante que nenhum botão comece verde errado ao carregar
  const allLinks = document.querySelectorAll('.sidebar-container .nav-link');
  allLinks.forEach(link => {
      link.classList.remove('active');
      link.style.borderLeft = '';
  });
  
  // Ativa apenas o botão correto
  const activeLink = document.querySelector(`.nav-link[href="#${hash}"]`);
  if (activeLink) activeLink.classList.add('active');

  // --- 2. MOSTRA O CONTEÚDO CORRETO ---
  document.querySelectorAll('.section-panel').forEach(p => p.classList.remove('active'));
  const activePanel = document.getElementById(hash);
  if (activePanel) {
      activePanel.classList.add('active');
  } else {
      const dash = document.getElementById('dashboard');
      if(dash) dash.classList.add('active');
  }

  // --- 3. AUTENTICAÇÃO ---
  const accessToken = localStorage.getItem('accessToken');
  
  if (!accessToken) {
    window.location.href = '/login_usuario.html';
    return;
  }

  // Wrapper de Fetch para adicionar token de autenticação a todas as requisições
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

  // 4. CARGA DE DADOS DO PERFIL E SISTEMA
  fetch('/api/v1/usuarios/perfil')
    .then(response => {
      if (!response.ok) {
        localStorage.removeItem('accessToken');
        window.location.href = '/login_usuario.html';
        throw new Error('Token inválido ou expirado');
      }
      return response.json();
    })
    .then(user => {
      console.log('Usuário autenticado:', user);
      localStorage.setItem('user', JSON.stringify(user)); 
      const welcomeMessage = document.getElementById('welcome-message');
      if (welcomeMessage && user.nome) {
        welcomeMessage.textContent = `Bem-vindo(a), ${user.nome}!`;
      }
      carregarDadosSensores();
      carregarAlertasConfigurados();
    })
    .catch(error => {
      console.error('Erro na autenticação inicial:', error);
    });

  // 5. EVENT LISTENERS
  window.addEventListener('hashchange', handleHashChange);

  document.getElementById('toggleSenha').addEventListener('click', function() {
    const senhaInput = document.getElementById('senha');
    const icon = this.querySelector('i');
    if (senhaInput.type === 'password') {
      senhaInput.type = 'text';
      icon.classList.remove('bi-eye');
      icon.classList.add('bi-eye-slash');
    } else {
      senhaInput.type = 'password';
      icon.classList.remove('bi-eye-slash');
      icon.classList.add('bi-eye');
    }
  });

  document.querySelector('#modalEditarPerfil form').addEventListener('submit', function(e) {
    e.preventDefault();
    const form = this;
    const formData = new FormData(form);
    const submitButton = form.querySelector('button[type="submit"]');
    const originalButtonHtml = submitButton.innerHTML;

    const payload = {};
    for (const [key, value] of formData.entries()) {
        if (value) payload[key] = value;
    }

    if (Object.keys(payload).length === 0) return;

    submitButton.disabled = true;
    submitButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Salvando...`;

    fetch('/api/v1/usuarios/editar-perfil', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(async response => {
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalEditarPerfil'));
            modal.hide();
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-success alert-dismissible fade show';
            alertDiv.role = 'alert';
            alertDiv.innerHTML = `Perfil atualizado com sucesso!<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>`;
            document.querySelector('main').insertBefore(alertDiv, document.querySelector('main').firstChild);
            
            if (payload.nome) {
              document.querySelector('#welcome-message').textContent = `Bem-vindo(a), ${payload.nome}!`;
            }

            setTimeout(() => alertDiv.remove(), 3000);
        } else {
            const errorData = await response.json();
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-danger alert-dismissible fade show';
            alertDiv.role = 'alert';
            alertDiv.innerHTML = `${errorData.detail || 'Erro ao atualizar o perfil.'}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>`;
            document.querySelector('#modalEditarPerfil .modal-body').prepend(alertDiv);
        }
    })
    .catch(() => {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `Erro de conexão. Tente novamente.<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>`;
        document.querySelector('#modalEditarPerfil .modal-body').prepend(alertDiv);
    })
    .finally(() => {
        submitButton.disabled = false;
        submitButton.innerHTML = originalButtonHtml;
    });
  });

  // Evento para formulário de alertas
  document.getElementById('formCriarAlerta').addEventListener('submit', function(e) {
    e.preventDefault();
    const form = this;
    const formData = new FormData(form);
    const submitButton = form.querySelector('button[type="submit"]');
    const originalButtonHtml = submitButton.innerHTML;

    submitButton.disabled = true;
    submitButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Salvando...`;

    const payload = {};
    for (const [key, value] of formData.entries()) {
      if (key !== 'local_id') {
        payload[key] = value;
      } else {
        payload[key] = parseInt(value);
      }
    }

    payload.usuario_email = JSON.parse(localStorage.getItem('user')).email;

    fetch('/api/v1/regras-alerta', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    .then(async response => {
      if (response.ok) {
        form.reset();
        carregarAlertasConfigurados();
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-success alert-dismissible fade show';
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `Alerta criado com sucesso!<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>`;
        document.querySelector('main').insertBefore(alertDiv, document.querySelector('main').firstChild);
        setTimeout(() => alertDiv.remove(), 3000);
      } else {
        const errorData = await response.json();
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `${errorData.detail || 'Erro ao criar alerta.'}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>`;
        document.querySelector('#formCriarAlerta').prepend(alertDiv);
        setTimeout(() => alertDiv.remove(), 5000);
      }
    })
    .catch(() => {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `Erro de conexão. Tente novamente.<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>`;
        document.querySelector('#formCriarAlerta').prepend(alertDiv);
        setTimeout(() => alertDiv.remove(), 5000);
    })
    .finally(() => {
        submitButton.disabled = false;
        submitButton.innerHTML = originalButtonHtml;
    });
  });

  // Evento para mudança de tipo de sensor
  document.getElementById('tipoSensorAlerta').addEventListener('change', function() {
    atualizarCamposSensor(this.value);
  });

  // Eventos Botões Exportação
  document.getElementById('btnExportCSV').addEventListener('click', function() {
    const form = document.getElementById('formRelatorios');
    if (!form.inicio.value || !form.fim.value) {
      alert('Preencha a data inicial e final.');
      return;
    }
    
    const btn = this;
    const originalHtml = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Exportando...`;

    const qs = montarQueryRelatorio(form);
    const url = `/api/v1/relatorios/exportar.csv?${qs}`;
    
    fetch(url)
      .then(response => {
        if (!response.ok) throw new Error('Erro ao exportar relatório.');
        return response.blob();
      })
      .then(blob => {
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = `relatorio_${form.inicio.value}_${form.fim.value}.csv`;
        link.click();
      })
      .catch(error => {
        console.error('Erro:', error);
        alert(error.message || 'Erro ao exportar relatório.');
      })
      .finally(() => {
        btn.disabled = false;
        btn.innerHTML = originalHtml;
      });
  });

  document.getElementById('btnExportPDF').addEventListener('click', function() {
    const form = document.getElementById('formRelatorios');
    if (!form.inicio.value || !form.fim.value) {
      alert('Preencha a data inicial e final.');
      return;
    }

    const btn = this;
    const originalHtml = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Exportando...`;

    const qs = montarQueryRelatorio(form);
    const url = `/api/v1/relatorios/exportar.pdf?${qs}`;
    
    fetch(url)
      .then(response => {
        if (!response.ok) throw new Error('Erro ao exportar relatório.');
        return response.blob();
      })
      .then(blob => {
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = `relatorio_${form.inicio.value}_${form.fim.value}.pdf`;
        link.click();
      })
      .catch(error => {
        console.error('Erro:', error);
        alert(error.message || 'Erro ao exportar relatório.');
      })
      .finally(() => {
        btn.disabled = false;
        btn.innerHTML = originalHtml;
      });
  });

  document.getElementById('btnEnviarEmail').addEventListener('click', function() {
    const form = document.getElementById('formRelatorios');
    if (!form.inicio.value || !form.fim.value) {
      alert('Preencha a data inicial e final.');
      return;
    }
    
    const btn = this;
    const originalHtml = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Enviando...';
    
    const qs = montarQueryRelatorio(form);
    const url = `/api/v1/relatorios/enviar-por-email?${qs}`;
    
    fetch(url, { method: 'POST' })
      .then(response => {
        if (!response.ok) return response.json().then(data => { throw new Error(data.detail || 'Erro ao enviar e-mail.'); });
        return response.json();
      })
      .then(data => {
        alert(data.message || 'Relatório enviado com sucesso!');
      })
      .catch(error => {
        console.error('Erro:', error);
        alert(error.message || 'Erro ao enviar e-mail.');
      })
      .finally(() => {
        btn.disabled = false;
        btn.innerHTML = originalHtml;
      });
  });

  const logoutButton = document.getElementById('logout-button');
  if (logoutButton) {
    logoutButton.addEventListener('click', function(e) {
      e.preventDefault();
      localStorage.removeItem('accessToken');
      window.location.href = '/login_usuario.html';
    });
  }
});


// Funções de carregamento de dados
function carregarDadosSensores() {
  fetch('/api/v1/usuarios/dashboard-dados')
    .then(response => {
      if (!response.ok) {
        throw new Error('Erro ao carregar dados dos sensores');
      }
      return response.json();
    })
    .then(data => {
      console.log('Dados dos sensores:', data);
      localStorage.setItem('sensores', JSON.stringify(data.dispositivos));
      
      const totalDispositivos = document.getElementById('total-dispositivos');
      if (totalDispositivos) {
        totalDispositivos.textContent = data.dispositivos.length;
      }
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
      renderizarSensores(data);
    })
    .catch(error => {
      console.error('Erro ao carregar dados dos sensores:', error);
      const container = document.getElementById('sensores-container');
      if (container) {
        container.innerHTML = `<div class="text-center py-4"><i class="bi bi-exclamation-circle text-muted fs-1 mb-2 d-block"></i><p class="mb-0">Erro ao carregar dados dos sensores.</p></div>`;
      }
    });
}

function renderizarSensores(data) {
  const container = document.getElementById('sensores-container');
  if (!data.dispositivos || data.dispositivos.length === 0) {
    container.innerHTML = `<div class="text-center py-4"><i class="bi bi-exclamation-circle text-muted fs-1 mb-2 d-block"></i><p class="mb-0">Nenhum dispositivo encontrado.</p></div>`;
    return;
  }

  let html = `<div class="mb-4"><label for="selectDispositivo" class="form-label fw-semibold">Selecione o Dispositivo:</label><select class="form-select w-auto d-inline-block ms-2" id="selectDispositivo" onchange="mostrarDispositivoSelecionado()">`;
  data.dispositivos.forEach((disp) => {
    html += `<option value="${disp.nome}">${disp.nome}</option>`;
  });
  html += `</select></div>`;

  data.dispositivos.forEach((disp, index) => {
    const dispositivoId = disp.nome.replace(/\s/g, '_');
    const phData = data.ph_por_dispositivo[disp.nome];
    const nivelData = data.nivel_por_dispositivo[disp.nome];
    
    html += `
      <div class="dispositivo-panel" id="panel-${dispositivoId}" style="display: ${index === 0 ? 'block' : 'none'};">
        <div class="row g-4">
          <div class="col-md-6 mb-4">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-primary text-white">
                <i class="bi bi-droplet-half me-2"></i>pH da Água
              </div>
              <div class="card-body">
    `;
    
    if (phData && phData.atual) {
      const ph = phData.atual.ph;
      const badgeClass = ph < 6.5 ? 'bg-danger' : (ph > 8.5 ? 'bg-warning' : 'bg-success');
      const status = ph < 6.5 ? 'Ácido' : (ph > 8.5 ? 'Alcalino' : 'Neutro');
      
      html += `
        <div class="text-center mb-4">
          <div class="display-4 text-primary mb-2">${ph}</div>
          <span class="badge ${badgeClass} fs-6">${status}</span>
          <p class="text-muted mt-3 mb-0">
            <i class="bi bi-clock me-1"></i>
            Última atualização: ${phData.atual.data}
          </p>
        </div>
        <div class="mt-4 position-relative" style="width: 100%; height: 200px;">
          <canvas id="phChart-${dispositivoId}"></canvas>
        </div>
      `;
    } else {
      html += `
        <div class="text-center py-5">
          <i class="bi bi-exclamation-circle fs-1 text-muted mb-3"></i>
          <p class="text-muted mb-0">Nenhum dado de pH disponível.</p>
        </div>
      `;
    }
    
    html += `
              </div>
            </div>
          </div>

          <div class="col-md-6 mb-4">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-primary text-white">
                <i class="bi bi-water me-2"></i>Nível de Água
              </div>
              <div class="card-body">
    `;
    
    if (nivelData && nivelData.atual) {
      const status = nivelData.atual.status;
      const boia = nivelData.atual.boia;
      const statusClass = status === 'ALTO' ? 'text-success' : 'text-warning';
      const badgeClass = status === 'ALTO' ? 'bg-success' : 'bg-warning';
      const boiaClass = boia === 1 ? 'bg-primary' : 'bg-secondary';
      const boiaText = boia === 1 ? 'Ativada' : 'Desativada';
      
      html += `
        <div class="text-center mb-4">
          <div class="mb-4">
            <i class="bi bi-water fs-1 ${statusClass}"></i>
          </div>
          <div class="display-6 mb-2">
            <span class="badge ${badgeClass} fs-5">${status}</span>
          </div>
          <div class="mt-4">
            <p class="mb-2">Status da Boia:</p>
            <span class="badge ${boiaClass} fs-6">${boiaText}</span>
          </div>
          <p class="text-muted mt-4 mb-0">
            <i class="bi bi-clock me-1"></i>
            Última atualização: ${nivelData.atual.data}
          </p>
        </div>
        <div class="mt-4 position-relative" style="width: 100%; height: 200px;">
          <canvas id="nivelChart-${dispositivoId}"></canvas>
        </div>
      `;
    } else {
      html += `
        <div class="text-center py-5">
          <i class="bi bi-exclamation-circle fs-1 text-muted mb-3"></i>
          <p class="text-muted mb-0">Nenhum dado de nível disponível.</p>
        </div>
      `;
    }
    
    html += `
              </div>
            </div>
          </div>
        </div>

        <div class="row g-4 mt-2">
          <div class="col-md-6">
            <div class="card border-0 shadow-sm">
              <div class="card-header bg-primary text-white">
                <i class="bi bi-graph-up me-2"></i>Histórico de pH
              </div>
              <div class="card-body">
                <ul class="list-group list-group-flush">
    `;
    
    if (phData && phData.historico && phData.historico.length > 0) {
      phData.historico.forEach(item => {
        html += `
          <li class="list-group-item d-flex justify-content-between align-items-center">
            <span><i class="bi bi-calendar me-2"></i>${item.data}</span>
            <span class="badge bg-primary">pH ${item.ph}</span>
          </li>
        `;
      });
    } else {
      html += `<li class="list-group-item text-muted">Nenhum registro encontrado</li>`;
    }
    
    html += `
                </ul>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="card border-0 shadow-sm">
              <div class="card-header bg-primary text-white">
                <i class="bi bi-clock-history me-2"></i>Histórico de Nível
              </div>
              <div class="card-body">
                <ul class="list-group list-group-flush">
    `;
    
    if (nivelData && nivelData.historico && nivelData.historico.length > 0) {
      nivelData.historico.forEach(item => {
        const badgeClass = item.status === 'ALTO' ? 'bg-success' : 'bg-warning';
        html += `
          <li class="list-group-item d-flex justify-content-between align-items-center">
            <span><i class="bi bi-calendar me-2"></i>${item.data}</span>
            <span class="badge ${badgeClass}">${item.status}</span>
          </li>
        `;
      });
    } else {
      html += `<li class="list-group-item text-muted">Nenhum registro encontrado</li>`;
    }
    
    html += `
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  });
  
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
    
    // Configuração comum para responsividade
    const configComum = {
        responsive: true,
        maintainAspectRatio: false, // CRÍTICO PARA MOBILE
        plugins: { 
            legend: { display: false },
            tooltip: { 
                backgroundColor: 'rgba(0, 0, 0, 0.8)', 
                titleFont: { family: "'Poppins', sans-serif" }, 
                bodyFont: { family: "'Poppins', sans-serif" }, 
                padding: 12, 
                cornerRadius: 8, 
                displayColors: false 
            } 
        },
        scales: { 
            y: { beginAtZero: false, grid: { color: 'rgba(0, 0, 0, 0.05)' }, ticks: { font: { family: "'Poppins', sans-serif" } } }, 
            x: { grid: { display: false }, ticks: { font: { family: "'Poppins', sans-serif" } } } 
        },
        animation: { duration: 2000, easing: 'easeOutQuart' },
        interaction: { intersect: false, mode: 'index' }
    };

    const phCtx = document.getElementById(`phChart-${dispositivoId}`);
    if (phCtx && phData && phData.historico) {
      const historicoPh = phData.historico.reverse();
      new Chart(phCtx, {
        type: 'line',
        data: {
          labels: historicoPh.map(item => item.data),
          datasets: [{
            label: 'Histórico de pH',
            data: historicoPh.map(item => item.ph),
            borderColor: '#004183',
            backgroundColor: 'rgba(0,65,131,0.1)',
            borderWidth: 3,
            pointBackgroundColor: '#004183',
            pointBorderColor: '#fff',
            pointRadius: 6,
            pointHoverRadius: 8,
            fill: true,
            tension: 0.4
          }]
        },
        options: configComum
      });
    }
    
    const nivelCtx = document.getElementById(`nivelChart-${dispositivoId}`);
    if (nivelCtx && nivelData && nivelData.historico) {
      const historicoNivel = nivelData.historico.reverse();
      new Chart(nivelCtx, {
        type: 'line',
        data: {
          labels: historicoNivel.map(item => item.data),
          datasets: [{
            label: 'Histórico de Nível',
            data: historicoNivel.map(item => item.status === 'ALTO' ? 2 : (item.status === 'BAIXO' ? 1 : 0)),
            borderColor: '#34c759',
            backgroundColor: 'rgba(52,199,89,0.1)',
            borderWidth: 3,
            pointBackgroundColor: '#34c759',
            pointBorderColor: '#fff',
            pointRadius: 6,
            pointHoverRadius: 8,
            fill: true,
            tension: 0.4
          }]
        },
        options: {
            ...configComum,
            scales: {
                ...configComum.scales,
                y: { 
                    beginAtZero: true, min: 0, max: 2, 
                    grid: { color: 'rgba(0, 0, 0, 0.05)' }, 
                    ticks: { callback: function(value) { if (value === 2) return 'ALTO'; if (value === 1) return 'BAIXO'; return ''; } } 
                }
            }
        }
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

// Funções para carregar e gerenciar alertas

function carregarSensoresParaAlertas() {
  const select = document.getElementById('sensorAlerta');
  select.innerHTML = '<option value="">Selecione um sensor</option>';
  
  fetch('/api/v1/usuarios/dashboard-dados')
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
  
  const camposPorTipo = {
    'PH': [
      {value: 'ph', text: 'pH'},
    ],
    'BOIA': [
      {value: 'valor', text: 'Valor (Boia)'},
      {value: 'status', text: 'Status'},
    ],
    'UMIDADE': [
      {value: 'umidade_percentual', text: 'Umidade (%)'},
      {value: 'raw', text: 'Valor Raw'},
      {value: 'status', text: 'Status'},
    ]
  };
  
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
  fetch('/api/v1/regras-alerta')
    .then(response => {
      if (!response.ok) {
        throw new Error('Erro ao carregar alertas');
      }
      return response.json();
    })
    .then(alertas => {
      const container = document.getElementById('alertas-container');
      if (!alertas || alertas.length === 0) {
        container.innerHTML = `
          <div class="text-center py-4">
            <i class="bi bi-bell-slash text-muted fs-1 mb-3"></i>
            <p class="text-muted mb-0">Nenhum alerta configurado.</p>
            <p class="text-muted small">Configure seus primeiros alertas usando o formulário acima.</p>
          </div>
        `;
        return;
      }

      let html = '<div class="table-responsive"><table class="table table-hover">';
      html += `
        <thead>
          <tr>
            <th>Sensor</th>
            <th>Regra</th>
            <th>Mensagem</th>
            <th>Status</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
      `;

      alertas.forEach(alerta => {
        const sensorNome = obterNomeSensor(alerta.local_id);
        html += `
          <tr>
            <td>${sensorNome}</td>
            <td>${alerta.campo_sensor} ${alerta.operador} ${alerta.valor_limite}</td>
            <td>${alerta.mensagem_alerta || 'Alerta personalizado'}</td>
            <td><span class="badge ${alerta.ativa ? 'bg-success' : 'bg-secondary'}">${alerta.ativa ? 'Ativo' : 'Inativo'}</span></td>
            <td>
              <button class="btn btn-outline-danger btn-sm" onclick="excluirAlerta(${alerta.id})" title="Excluir alerta">
                <i class="bi bi-trash"></i>
              </button>
            </td>
          </tr>
        `;
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
  if (!confirm('Tem certeza que deseja excluir este alerta?')) {
    return;
  }

  fetch(`/api/v1/regras-alerta/${alertaId}`, {
    method: 'DELETE'
  })
  .then(response => {
    if (response.ok) {
      carregarAlertasConfigurados();
      const alertDiv = document.createElement('div');
      alertDiv.className = 'alert alert-success alert-dismissible fade show';
      alertDiv.role = 'alert';
      alertDiv.innerHTML = `Alerta excluído com sucesso!<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>`;
      document.querySelector('main').insertBefore(alertDiv, document.querySelector('main').firstChild);
      setTimeout(() => alertDiv.remove(), 3000);
    } else {
      return response.json().then(data => {
        throw new Error(data.detail || 'Erro ao excluir alerta');
      });
    }
  })
  .catch(error => {
    console.error('Erro:', error);
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `${error.message || 'Erro ao excluir alerta.'}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>`;
    document.querySelector('main').insertBefore(alertDiv, document.querySelector('main').firstChild);
    setTimeout(() => alertDiv.remove(), 5000);
  });
}

function limparFormularioAlerta() {
  document.getElementById('formCriarAlerta').reset();
  document.getElementById('campoAlerta').innerHTML = '<option value="">Campo</option>';
}