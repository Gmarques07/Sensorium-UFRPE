document.addEventListener('DOMContentLoaded', () => {
    const themeToggleButton = document.getElementById('theme-toggle');
    const navbar = document.getElementById('main-navbar');
    const sunIcon = themeToggleButton.querySelector('.bi-sun-fill');
    const moonIcon = themeToggleButton.querySelector('.bi-moon-fill');

    const applyTheme = (theme) => {
        if (theme === 'dark') {
            document.body.classList.add('dark-mode');
            sunIcon.classList.add('d-none');
            moonIcon.classList.remove('d-none');
        } else {
            document.body.classList.remove('dark-mode');
            sunIcon.classList.remove('d-none');
            moonIcon.classList.add('d-none');
        }
    };

    const toggleTheme = () => {
        const currentTheme = document.body.classList.contains('dark-mode') ? 'light' : 'dark';
        localStorage.setItem('theme', currentTheme);
        applyTheme(currentTheme);
    };

    themeToggleButton.addEventListener('click', (e) => {
        e.preventDefault();
        toggleTheme();
    });

    // Aplica o tema inicial ao carregar a página
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme) {
        applyTheme(savedTheme);
    } else if (systemPrefersDark) {
        applyTheme('dark');
    } else {
        applyTheme('light');
    }
});
