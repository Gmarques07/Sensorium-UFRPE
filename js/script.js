document.addEventListener('DOMContentLoaded', function() {
    var cpfField = document.getElementById('cpf');
    if (cpfField) {
        cpfField.addEventListener('input', function() {
            let value = cpfField.value.replace(/\D/g, '');
            if (value.length > 11) {
                value = value.slice(0, 11);
            }
            cpfField.value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
        });
    }

    var form = document.getElementById('cadastroForm');
    var senha = document.getElementById('senha');
    var confirmarSenha = document.getElementById('confirmacao_senha');
    var errorMessage = document.getElementById('error-message');

    if (form && senha && confirmarSenha && errorMessage) {
        form.addEventListener('submit', function(event) {
            if (senha.value !== confirmarSenha.value) {
                errorMessage.textContent = 'As senhas não coincidem.';
                event.preventDefault();
            } else {
                errorMessage.textContent = '';
            }
        });
    }
});
