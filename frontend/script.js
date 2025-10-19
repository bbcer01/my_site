document.addEventListener('DOMContentLoaded', () => {
    // --- Элементы формы ---
    const productNameInput = document.getElementById('productName');
    const tnvedCodeInput = document.getElementById('tnvedCode');
    const evaluateBtn = document.getElementById('evaluateBtn');
    const resultDiv = document.getElementById('result');
    const measureP = document.getElementById('measure');
    const reasonP = document.getElementById('reason');
    const metricsDiv = document.getElementById('metrics');
    const chartsDiv = document.getElementById('charts');
    const chartsContainer = document.getElementById('charts-container');
    const errorDiv = document.getElementById('error');
    const downloadReportBtn = document.getElementById('downloadReportBtn');

    // --- Элементы авторизации ---
    const authBtn = document.getElementById('authBtn');
    const authModal = document.getElementById('authModal');
    const authModalOverlay = document.getElementById('authModalOverlay');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const loginBtn = document.getElementById('loginBtn');
    const logoutBtn = document.getElementById('logoutBtn');

    // --- Состояние ---
    let authToken = localStorage.getItem('token');
    if (authToken) {
        authBtn.textContent = 'Профиль';
        logoutBtn.style.display = 'block';
    }

    // --- Хранилище данных результата ---
    let currentRequestData = null;

    // --- Функции ---
    function clearMessages() {
        errorDiv.textContent = '';
        resultDiv.style.display = 'none';
        metricsDiv.style.display = 'none';
        chartsDiv.style.display = 'none';
        chartsContainer.innerHTML = '';
        downloadReportBtn.style.display = 'none';
    }

    function showError(message) {
        errorDiv.textContent = message;
    }

    function showResult(measure, reason, metrics, charts) {
        measureP.textContent = measure;
        reasonP.textContent = reason;

        // --- ОТОБРАЖЕНИЕ МЕТРИК (на английском языке) ---
        if (metrics && Object.keys(metrics).length > 0) {
            metricsDiv.style.display = 'block';
            let metricsHtml = '<h4>Metrics:</h4><ul>';

            if (metrics['2024']) {
                const year2024 = metrics['2024'];
                for (const [key, value] of Object.entries(year2024)) {
                    metricsHtml += `<li>${key}: ${value}</li>`;
                }
            }

            for (const [key, value] of Object.entries(metrics)) {
                if (key === '2024') continue;
                if (typeof value === 'object' && value !== null) {
                    metricsHtml += `<li>${key}: <pre>${JSON.stringify(value, null, 2)}</pre></li>`;
                } else {
                    metricsHtml += `<li>${key}: ${value}</li>`;
                }
            }

            metricsHtml += '</ul>';
            metricsDiv.innerHTML = metricsHtml;
        } else {
            metricsDiv.style.display = 'none';
        }
        // ---

        // --- ОТОБРАЖЕНИЕ ГРАФИКОВ ---
        if (charts && charts.length > 0) {
            chartsDiv.style.display = 'block';
            chartsContainer.innerHTML = '';
            charts.forEach((chartDataUrl, index) => {
                const img = document.createElement('img');
                img.src = `${chartDataUrl}`;
                img.alt = `Chart ${index + 1}`;
                img.title = `Chart ${index + 1}`;
                chartsContainer.appendChild(img);
            });
        } else {
            chartsDiv.style.display = 'none';
        }
        // ---

        downloadReportBtn.style.display = 'inline-block';
        resultDiv.style.display = 'block';
    }

    // --- Обработчики событий ---
    authBtn.addEventListener('click', () => {
        // --- ПОКАЗАТЬ СООБЩЕНИЕ ОБ ОТКЛЮЧЁННОЙ АУТЕНТИФИКАЦИИ ---
        alert("В тестовой версии аутентификация отключена. Эта функция будет доступна в продакшене.");
        // authModal.style.display = 'block';
        // authModalOverlay.style.display = 'block';
    });

    authModalOverlay.addEventListener('click', () => {
        authModal.style.display = 'none';
        authModalOverlay.style.display = 'none';
    });

    loginBtn.addEventListener('click', async () => {
        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();

        if (!username || !password) {
            showError("Пожалуйста, введите логин и пароль.");
            return;
        }

        try {
            const response = await fetch('http://localhost:8000/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    username: username,
                    password: password
                })
            });

            if (!response.ok) {
                throw new Error(`Ошибка авторизации: ${response.status}`);
            }

            const data = await response.json();
            authToken = data.access_token;
            localStorage.setItem('token', authToken);

            authBtn.textContent = 'Профиль';
            logoutBtn.style.display = 'block';
            authModal.style.display = 'none';
            authModalOverlay.style.display = 'none';
            clearMessages();

        } catch (error) {
            showError(`Ошибка входа: ${error.message}`);
            console.error('Login Error:', error);
        }
    });

    logoutBtn.addEventListener('click', () => {
        authToken = null;
        localStorage.removeItem('token');
        authBtn.textContent = 'Войти';
        logoutBtn.style.display = 'none';
        usernameInput.value = '';
        passwordInput.value = '';
        clearMessages();
    });

    evaluateBtn.addEventListener('click', async () => {
        clearMessages();

        const productName = productNameInput.value.trim();
        const tnvedCode = tnvedCodeInput.value.trim();

        if (!productName || !tnvedCode) {
            showError("Пожалуйста, заполните все поля.");
            return;
        }

        try {
            const headers = {
                'Content-Type': 'application/json',
            };

            const response = await fetch('http://localhost:8000/evaluate', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({
                    product_name: productName,
                    tnved_code: tnvedCode
                })
            });

            if (!response.ok) {
                throw new Error(`Ошибка сервера: ${response.status}`);
            }

            const data = await response.json();
            showResult(data.measure, data.reason, data.metrics, data.charts);

            // Сохраняем данные для скачивания отчёта
            currentRequestData = { product_name: productName, tnved_code: tnvedCode };

        } catch (error) {
            showError(`Произошла ошибка: ${error.message}`);
            console.error('Error:', error);
        }
    });

    // --- ОБНОВЛЁННАЯ ФУНКЦИЯ СКАЧИВАНИЯ ОТЧЁТА ---
    downloadReportBtn.addEventListener('click', async () => {
        if (!currentRequestData) {
            alert("Нет данных для формирования отчёта. Пожалуйста, сначала выполните анализ.");
            return;
        }

        try {
            // Отправляем запрос на генерацию PDF
            const response = await fetch('http://localhost:8000/generate_report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(currentRequestData) // Отправляем только данные запроса
            });

            if (!response.ok) {
                throw new Error(`Ошибка генерации отчёта: ${response.status}`);
            }

            // Получаем blob (бинарные данные) из ответа
            const blob = await response.blob();
            // Создаём URL для blob
            const downloadUrl = window.URL.createObjectURL(blob);
            // Создаём временный элемент <a>
            const link = document.createElement('a');
            link.href = downloadUrl;
            // Устанавливаем имя файла
            link.download = `report_${currentRequestData.tnved_code}.pdf`;
            // Клик по ссылке для скачивания
            document.body.appendChild(link);
            link.click();
            // Удаляем элемент <a> и URL
            document.body.removeChild(link);
            window.URL.revokeObjectURL(downloadUrl);

        } catch (error) {
            alert(`Ошибка скачивания отчёта: ${error.message}`);
            console.error('Download Error:', error);
        }
    });
});