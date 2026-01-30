const state = {
    topics: [],
    currentTopic: null,
    isMaskMode: true,
    isStealthMode: false
};

const app = document.getElementById('app');

// Fetch Data
async function init() {
    try {
        const response = await fetch('topics.json');
        if (!response.ok) throw new Error('Failed to load topics');
        state.topics = await response.json();

        // Handle initial route
        handleRoute();

        // Listen for hash changes
        window.addEventListener('hashchange', handleRoute);
    } catch (error) {
        app.innerHTML = `<div class="error">エラーが発生しました: ${error.message}<br>ローカルで実行している場合は、Webサーバー経由で開いてください (例: python -m http.server)</div>`;
        console.error(error);
    }
}

// Router
function handleRoute() {
    const hash = window.location.hash;
    if (hash.startsWith('#topic/')) {
        const id = hash.split('/')[1];
        const topic = state.topics.find(t => t.id === id);
        if (topic) {
            renderDetail(topic);
        } else {
            renderList(); // Fallback
        }
    } else {
        renderList();
    }
}

// Render List View
function renderList() {
    state.currentTopic = null;
    const listHtml = `
        <div class="list-view">
            <ul class="topic-list">
                ${state.topics.map(topic => `
                    <li class="topic-item" onclick="location.hash='#topic/${topic.id}'">
                        <span class="topic-category">${topic.category || '未分類'}</span>
                        <div class="topic-title">${topic.title}</div>
                    </li>
                `).join('')}
            </ul>
        </div>
    `;
    app.innerHTML = listHtml;
    updateHeader("理論暗記ツール");
}

// Render Detail View
function renderDetail(topic) {
    state.currentTopic = topic;

    // Apply body class for stealth mode persistence
    if (state.isStealthMode) {
        document.body.classList.add('stealth-mode');
    } else {
        document.body.classList.remove('stealth-mode');
    }

    const contentHtml = `
        <div class="detail-view ${state.isMaskMode ? 'mask-active' : ''}">
            <div class="controls">
                <label class="toggle-switch">
                    <input type="checkbox" id="mask-toggle" ${state.isMaskMode ? 'checked' : ''}>
                    <span style="margin-left: 8px;">赤シート (暗記モード)</span>
                </label>
                <label class="toggle-switch" style="margin-left: 15px;">
                    <input type="checkbox" id="stealth-toggle" ${state.isStealthMode ? 'checked' : ''}>
                    <span style="margin-left: 8px;">ステルスモード</span>
                </label>
            </div>
            
            <a class="back-button" href="#">&larr; 一覧に戻る</a>
            
            <h2 class="sub-title">${topic.title}</h2>
            <div class="content-body" id="content-area">
                ${topic.content}
            </div>
            
            <br>
            <a class="back-button" href="#">&larr; 一覧に戻る</a>
        </div>
    `;

    app.innerHTML = contentHtml;
    updateHeader(topic.title);

    // Attach Event Listeners for this view
    document.getElementById('mask-toggle').addEventListener('change', (e) => {
        state.isMaskMode = e.target.checked;
        const container = document.querySelector('.detail-view');
        if (state.isMaskMode) {
            container.classList.add('mask-active');
            // Reset all individually revealed items
            document.querySelectorAll('.span-memory.revealed').forEach(el => {
                el.classList.remove('revealed');
            });
        } else {
            container.classList.remove('mask-active');
        }
    });

    document.getElementById('stealth-toggle').addEventListener('change', (e) => {
        state.isStealthMode = e.target.checked;
        if (state.isStealthMode) {
            document.body.classList.add('stealth-mode');
        } else {
            document.body.classList.remove('stealth-mode');
        }
    });

    // Add click-to-reveal functionality for masks
    const masks = document.querySelectorAll('.span-memory');
    masks.forEach(mask => {
        mask.addEventListener('click', function () {
            if (state.isMaskMode) {
                this.classList.toggle('revealed');
            }
        });
    });
}

function updateHeader(text) {
    // document.getElementById('app-title').textContent = text;
    // Keeping main header static usually looks better, but we can change page title
    document.title = text + " - 理論暗記ツール";
}

// Start
init();
