<script>
  // Verificar se o usuário está autenticado
  document.addEventListener('DOMContentLoaded', function() {
    const accessToken = localStorage.getItem('accessToken');
    
    if (!accessToken) {
      // Se não houver token, redirecionar para a página de login
      window.location.href = '/login_usuario.html';
      return;
    }
    
    // Adicionar token às requisições fetch
    const originalFetch = window.fetch;
    window.fetch = function(input, init = {}) {
      // Se for uma string (URL), converter para objeto
      if (typeof input === 'string') {
        input = new Request(input, init);
      }
      
      // Adicionar o header de autorização se tivermos o token
      if (accessToken) {
        input.headers.set('Authorization', `Bearer ${accessToken}`);
      }
      
      return originalFetch(input, init);
    };
    
    // Adicionar funcionalidade de logout
    const logoutButton = document.getElementById('logout-button');
    if (logoutButton) {
      logoutButton.addEventListener('click', function(e) {
        e.preventDefault();
        // Remover o token do localStorage
        localStorage.removeItem('accessToken');
        // Redirecionar para a página de login
        window.location.href = '/login_usuario.html';
      });
    }
  });
</script>