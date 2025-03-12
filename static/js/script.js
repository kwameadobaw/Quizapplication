// Quiz App JavaScript

// Function to handle form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const inputs = form.querySelectorAll('input[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.classList.add('error');
        } else {
            input.classList.remove('error');
        }
    });
    
    return isValid;
}

// Function to handle quiz submission
function setupQuizForm() {
    const quizForm = document.getElementById('quiz-form');
    if (!quizForm) return;
    
    quizForm.addEventListener('submit', function(e) {
        const questions = document.querySelectorAll('.question-card');
        let allAnswered = true;
        
        questions.forEach(question => {
            const options = question.querySelectorAll('input[type="radio"]');
            const questionId = options[0].name;
            const answered = Array.from(options).some(option => option.checked);
            
            if (!answered) {
                allAnswered = false;
                question.classList.add('unanswered');
            } else {
                question.classList.remove('unanswered');
            }
        });
        
        if (!allAnswered) {
            e.preventDefault();
            alert('Please answer all questions before submitting.');
        }
    });
}

// Function to handle flash messages
function setupFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(message => {
        // Auto-hide flash messages after 5 seconds
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.style.display = 'none';
            }, 500);
        }, 5000);
    });
}

// Function to handle mobile navigation
function setupMobileNav() {
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (!menuToggle || !navLinks) return;
    
    menuToggle.addEventListener('click', () => {
        navLinks.classList.toggle('active');
        
        // Toggle menu icon
        const spans = menuToggle.querySelectorAll('span');
        spans.forEach(span => {
            span.classList.toggle('active');
        });
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.menu-toggle') && !e.target.closest('.nav-links')) {
            if (navLinks.classList.contains('active')) {
                navLinks.classList.remove('active');
                
                const spans = menuToggle.querySelectorAll('span');
                spans.forEach(span => {
                    span.classList.remove('active');
                });
            }
        }
    });
}

// Function to handle theme toggle
function setupThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;
    
    // Check if user has a preferred theme stored
    const currentTheme = localStorage.getItem('theme');
    if (currentTheme) {
        document.body.classList.toggle('dark-theme', currentTheme === 'dark');
        themeToggle.checked = currentTheme === 'dark';
    } else {
        // Check if user prefers dark mode in their OS settings
        const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
        if (prefersDarkScheme.matches) {
            document.body.classList.add('dark-theme');
            themeToggle.checked = true;
            localStorage.setItem('theme', 'dark');
        }
    }
    
    themeToggle.addEventListener('change', function() {
        document.body.classList.toggle('dark-theme');
        const theme = document.body.classList.contains('dark-theme') ? 'dark' : 'light';
        localStorage.setItem('theme', theme);
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupQuizForm();
    setupFlashMessages();
    setupMobileNav();
    setupThemeToggle();
    
    // Add event listeners for form validation
    const loginForm = document.querySelector('form[action*="login"]');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            if (!validateForm('login-form')) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    }
    
    const signupForm = document.querySelector('form[action*="signup"]');
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            if (!validateForm('signup-form')) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    }
    
    // Make tables responsive
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        const wrapper = document.createElement('div');
        wrapper.classList.add('table-responsive');
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    });
    
    // Add active class to current nav link
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (currentLocation === linkPath || 
            (linkPath !== '/' && currentLocation.startsWith(linkPath))) {
            link.classList.add('active');
        }
    });
});

// Add these styles for mobile menu toggle animation
document.head.insertAdjacentHTML('beforeend', `
<style>
.menu-toggle span.active:nth-child(1) {
    transform: rotate(-45deg) translate(-5px, 6px);
}
.menu-toggle span.active:nth-child(2) {
    opacity: 0;
}
.menu-toggle span.active:nth-child(3) {
    transform: rotate(45deg) translate(-5px, -6px);
}
.table-responsive {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}
.nav-right {
    display: flex;
    align-items: center;
}
</style>
`);