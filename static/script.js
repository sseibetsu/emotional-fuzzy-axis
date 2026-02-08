let sessionId = localStorage.getItem('mindful_session_id');
if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem('mindful_session_id', sessionId);
}
let hasStarted = false;

const body = document.body;
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const messagesContainer = document.getElementById('chat-messages');

const dominantEmotionEl = document.getElementById('dominant-emotion');
const modeBadge = document.getElementById('mode-badge');
const barsContainer = document.getElementById('bars-container'); // Container for vertical bars

function startInterface() {
    if (hasStarted) return;
    hasStarted = true;
    body.classList.add('chat-started');
    setTimeout(() => { messageInput.placeholder = "Type your message..."; }, 500);
    loadHistory();
    connectWebSocket();
    renderBars([
        { label: "Gratitude", value: 0 },
        { label: "Joy", value: 0 },
        { label: "Interest", value: 0 },
        { label: "Love", value: 0 }
    ]);
}

messageInput.addEventListener('focus', startInterface);
chatForm.addEventListener('click', startInterface);

const follower = document.getElementById('mouse-follower');
let mouseX = 0, mouseY = 0, currentX = 0, currentY = 0;
document.addEventListener('mousemove', (e) => { mouseX = e.clientX; mouseY = e.clientY; follower.style.opacity = '1'; });
function animateFollower() {
    currentX += (mouseX - currentX) * 0.1;
    currentY += (mouseY - currentY) * 0.1;
    follower.style.transform = `translate(${currentX - 100}px, ${currentY - 100}px)`;
    requestAnimationFrame(animateFollower);
}
animateFollower();

function applyTheme(graphType) {
    const root = document.documentElement;
    if (graphType === 'Negative') {
        root.style.setProperty('--theme-primary', 'var(--coral-primary)');
        root.style.setProperty('--theme-secondary', 'var(--coral-secondary)');
        root.style.setProperty('--theme-accent', 'var(--coral-accent)');
        modeBadge.textContent = "Support & De-escalation";
    } else {
        root.style.setProperty('--theme-primary', 'var(--green-primary)');
        root.style.setProperty('--theme-secondary', 'var(--green-secondary)');
        root.style.setProperty('--theme-accent', 'var(--green-accent)');
        modeBadge.textContent = graphType === 'Positive' ? "Empathetic Mode" : "Neutral Mode";
    }
}

let socket;
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    socket = new WebSocket(`${protocol}//${window.location.host}/ws?session_id=${sessionId}`);
    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'ai_message') {
            removeTypingIndicator();
            appendMessage(data.content, false);
            updateAnalysis(data.meta);
        }
    };
    socket.onclose = () => setTimeout(connectWebSocket, 3000);
}

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    if (!hasStarted) startInterface();
    const text = messageInput.value.trim();
    if (!text) return;
    appendMessage(text, true);
    socket.send(text);
    messageInput.value = '';
    sendBtn.disabled = true;
    showTypingIndicator();
});

messageInput.addEventListener('input', (e) => { sendBtn.disabled = !e.target.value.trim(); });

function appendMessage(text, isUser) {
    const div = document.createElement('div');
    div.className = `message-row ${isUser ? 'user' : 'ai'}`;
    const avatar = `<div class="avatar ${isUser ? 'user' : 'ai'}">${isUser ? 'U' : 'AI'}</div>`;
    const bubble = `<div class="bubble ${isUser ? 'user' : 'ai'}">${text}</div>`;
    div.innerHTML = isUser ? (bubble + avatar) : (avatar + bubble);
    messagesContainer.appendChild(div);
    requestAnimationFrame(() => div.classList.add('visible'));
    scrollToBottom();
}

function showTypingIndicator() {
    const div = document.createElement('div');
    div.id = 'typing-indicator';
    div.className = 'message-row ai';
    div.innerHTML = `<div class="avatar ai">AI</div><div class="bubble ai" style="opacity:0.6;">...</div>`;
    messagesContainer.appendChild(div);
    scrollToBottom();
    requestAnimationFrame(() => div.classList.add('visible'));
}

function removeTypingIndicator() {
    const el = document.getElementById('typing-indicator');
    if (el) el.remove();
}

function scrollToBottom() {
    messagesContainer.scrollTo({ top: messagesContainer.scrollHeight, behavior: 'smooth' });
}

function renderBars(breakdown) {
    barsContainer.innerHTML = '';

    breakdown.forEach(item => {
        let percent = Math.min(100, Math.round(item.value * 100));

        const wrapper = document.createElement('div');
        wrapper.className = 'v-bar-wrapper';

        wrapper.innerHTML = `
            <div class="v-bar-val">${percent}%</div>
            <div class="v-bar-track">
                <div class="v-bar-fill" style="height: ${percent}%"></div>
            </div>
            <div class="v-bar-label">${item.label}</div>
        `;

        barsContainer.appendChild(wrapper);
    });
}

function updateAnalysis(meta) {
    if (!meta) return;
    applyTheme(meta.graph_type);
    dominantEmotionEl.textContent = meta.emotion.charAt(0).toUpperCase() + meta.emotion.slice(1);

    // Рендерим 4 вертикальных бара из массива breakdown
    if (meta.breakdown && meta.breakdown.length > 0) {
        renderBars(meta.breakdown);
    }
}

async function loadHistory() {
    try {
        const res = await fetch(`/history/${sessionId}`);
        const history = await res.json();
        history.forEach(msg => appendMessage(msg.content, msg.isUser));
    } catch (e) { }
}

document.getElementById('download-btn')?.addEventListener('click', () => {
    window.open(`/report?session_id=${sessionId}`, '_blank');
});