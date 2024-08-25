document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('cadastroForm');
    var senha = document.getElementById('senha');
    var confirmarSenha = document.getElementById('confirmar_senha');
    var errorMessage = document.getElementById('error-message');

    form.addEventListener('submit', function(event) {
        if (senha.value !== confirmarSenha.value) {
            errorMessage.textContent = 'As senhas não coincidem.';
            event.preventDefault(); // Impede o envio do formulário
        } else {
            errorMessage.textContent = ''; // Limpa a mensagem de erro
        }
    });
});
