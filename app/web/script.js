// App State
let currentUser = null;
let currentQuiz = {
    questions: [],
    currentIndex: 0,
    score: 0,
    correctCount: 0,
    timer: 15,
    timerInterval: null,
    category: '',
    difficulty: ''
};

// DOM Elements
const sections = {
    auth: document.getElementById('auth-section'),
    dashboard: document.getElementById('dashboard-section'),
    quiz: document.getElementById('quiz-section'),
    result: document.getElementById('result-section')
};

// Navigation
function showSection(sectionId) {
    Object.values(sections).forEach(s => s.classList.add('hidden'));
    sections[sectionId].classList.remove('hidden');
}

// Auth Logic
document.getElementById('to-register').onclick = () => {
    document.getElementById('login-form').classList.add('hidden');
    document.getElementById('register-form').classList.remove('hidden');
};

document.getElementById('to-login').onclick = () => {
    document.getElementById('register-form').classList.add('hidden');
    document.getElementById('login-form').classList.remove('hidden');
};

document.getElementById('login-btn').onclick = async () => {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    if (username && password) {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        });
        const data = await response.json();
        
        if (data.success) {
            currentUser = data.user;
            document.getElementById('display-name').innerText = currentUser.username;
            showSection('dashboard');
            loadHistory();
        } else {
            alert(data.message || 'Login failed');
        }
    }
};

document.getElementById('register-btn').onclick = async () => {
    const username = document.getElementById('reg-username').value;
    const password = document.getElementById('reg-password').value;
    
    if (username && password) {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        });
        const data = await response.json();
        
        if (data.success) {
            alert('Registration successful! Please login.');
            document.getElementById('to-login').click();
        } else {
            alert(data.message || 'Registration failed');
        }
    }
};

document.getElementById('logout-btn').onclick = () => {
    currentUser = null;
    showSection('auth');
};

async function loadHistory() {
    if (!currentUser) return;
    const response = await fetch(`/api/history?user_id=${currentUser.id}`);
    const data = await response.json();
    const historyList = document.getElementById('history-list');
    
    if (data.history && data.history.length > 0) {
        historyList.innerHTML = data.history.map(h => 
            `<p>${h.category} (${h.difficulty}): ${h.score} pts (${h.date.split(' ')[0]})</p>`
        ).join('');
    } else {
        historyList.innerHTML = '<p class="empty-msg">No recent activity</p>';
    }
}

// Quiz Logic
document.getElementById('start-quiz-btn').onclick = async () => {
    const category = document.getElementById('category-select').value;
    const difficulty = document.getElementById('difficulty-select').value;
    
    const response = await fetch(`/api/questions?category=${encodeURIComponent(category)}&difficulty=${encodeURIComponent(difficulty)}`);
    const data = await response.json();
    
    if (data.questions && data.questions.length > 0) {
        currentQuiz.questions = data.questions.sort(() => Math.random() - 0.5);
        currentQuiz.currentIndex = 0;
        currentQuiz.score = 0;
        currentQuiz.correctCount = 0;
        currentQuiz.category = category;
        currentQuiz.difficulty = difficulty;
        showSection('quiz');
        loadQuestion();
    } else {
        alert('No questions found for this category and difficulty.');
    }
};

function loadQuestion() {
    const q = currentQuiz.questions[currentQuiz.currentIndex];
    document.getElementById('question-count').innerText = `Question ${currentQuiz.currentIndex + 1} of ${currentQuiz.questions.length}`;
    document.getElementById('question-text').innerText = q.text;
    
    const optionsContainer = document.getElementById('options-container');
    optionsContainer.innerHTML = '';
    
    q.options.forEach((opt, index) => {
        const btn = document.createElement('button');
        btn.className = 'option-btn';
        btn.innerText = opt;
        btn.onclick = () => selectOption(index, btn);
        optionsContainer.appendChild(btn);
    });

    document.getElementById('next-btn').disabled = true;
    startTimer();
    updateProgress();
}

function selectOption(index, btn) {
    document.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    currentQuiz.selectedOption = index;
    document.getElementById('next-btn').disabled = false;
}

function startTimer() {
    clearInterval(currentQuiz.timerInterval);
    currentQuiz.timer = 15;
    document.getElementById('timer-display').innerText = currentQuiz.timer;
    
    currentQuiz.timerInterval = setInterval(() => {
        currentQuiz.timer--;
        document.getElementById('timer-display').innerText = currentQuiz.timer;
        if (currentQuiz.timer <= 0) {
            clearInterval(currentQuiz.timerInterval);
            handleNext(); // Auto-skip
        }
    }, 1000);
}

function updateProgress() {
    const percent = ((currentQuiz.currentIndex + 1) / currentQuiz.questions.length) * 100;
    document.getElementById('progress-fill').style.width = percent + '%';
}

document.getElementById('next-btn').onclick = handleNext;

function handleNext() {
    clearInterval(currentQuiz.timerInterval);
    
    const q = currentQuiz.questions[currentQuiz.currentIndex];
    if (currentQuiz.selectedOption === q.correct) {
        currentQuiz.correctCount++;
        currentQuiz.score += 10;
    }

    currentQuiz.currentIndex++;
    currentQuiz.selectedOption = null;

    if (currentQuiz.currentIndex < currentQuiz.questions.length) {
        loadQuestion();
    } else {
        showResults();
    }
}

async function showResults() {
    showSection('result');
    document.getElementById('final-score').innerText = currentQuiz.score;
    document.getElementById('stat-correct').innerText = currentQuiz.correctCount;
    document.getElementById('stat-wrong').innerText = currentQuiz.questions.length - currentQuiz.correctCount;
    
    const percent = (currentQuiz.correctCount / currentQuiz.questions.length) * 100;
    document.getElementById('stat-percent').innerText = percent + '%';
    
    let grade = 'F';
    if (percent >= 90) grade = 'A+';
    else if (percent >= 80) grade = 'A';
    else if (percent >= 70) grade = 'B';
    else if (percent >= 60) grade = 'C';
    else if (percent >= 50) grade = 'D';
    
    document.getElementById('grade-badge').innerText = `Grade: ${grade}`;
    
    if (currentUser) {
        await fetch('/api/results', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: currentUser.id,
                score: currentQuiz.score,
                total_questions: currentQuiz.questions.length,
                category: currentQuiz.category,
                difficulty: currentQuiz.difficulty
            })
        });
        loadHistory();
    }
}

document.getElementById('finish-btn').onclick = () => showSection('dashboard');

