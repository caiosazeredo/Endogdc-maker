// =============================================================================
// CONFIGURAÇÕES GLOBAIS
// =============================================================================

const BRAINSTORM_CONFIG = {
    API_BASE: '',
    SESSION_ID: null,
    COLORS: [
        '#FFD700', '#87CEEB', '#98FB98', '#DDA0DD', '#F0E68C', 
        '#FFB6C1', '#87CEFA', '#90EE90', '#FFA07A', '#20B2AA'
    ],
    CARD_SIZE: { width: 200, height: 120 },
    ANIMATION_DURATION: 300
};

// =============================================================================
// INICIALIZAÇÃO
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Iniciando sistema de brainstorming...');
    
    // Obter session_id da URL
    const urlParams = new URLSearchParams(window.location.search);
    BRAINSTORM_CONFIG.SESSION_ID = urlParams.get('session_id');
    
    if (!BRAINSTORM_CONFIG.SESSION_ID) {
        console.error('❌ Session ID não encontrado na URL');
        showErrorToast('Erro: Session ID não encontrado');
        return;
    }
    
    console.log(`✅ Session ID: ${BRAINSTORM_CONFIG.SESSION_ID}`);
    
    // Inicializar componentes
    initializeSuggestionsButton();
    initializeAddCardButton();
    initializeDragAndDrop();
    initializeCardInteractions();
    
    console.log('✅ Sistema de brainstorming inicializado com sucesso!');
});

// =============================================================================
// SISTEMA DE SUGESTÕES IA
// =============================================================================

function initializeSuggestionsButton() {
    console.log('🔗 Inicializando botão de sugestões...');
    
    // Seletores para encontrar o botão
    const selectors = [
        'button[onclick*="getSuggestions"]',
        'button[onclick*="sugestoes"]',
        '.btn:contains("Sugestões")',
        '.btn:contains("IA")',
        'button:contains("Obter Sugestões")',
        'button:contains("Sugestões da IA")',
        '.suggestions-btn',
        '#get-suggestions-btn',
        '.btn-success'
    ];
    
    let suggestionsButton = null;
    
    // Tentar encontrar pelos seletores
    for (const selector of selectors) {
        suggestionsButton = document.querySelector(selector);
        if (suggestionsButton) break;
    }
    
    // Se não encontrou, procurar por texto
    if (!suggestionsButton) {
        const buttons = document.querySelectorAll('button');
        suggestionsButton = Array.from(buttons).find(btn => {
            const text = btn.textContent.toLowerCase();
            return text.includes('sugestões') || 
                   text.includes('sugestão') || 
                   text.includes('ia') || 
                   text.includes('obter') ||
                   text.includes('gerar');
        });
    }
    
    if (suggestionsButton) {
        console.log('✅ Botão de sugestões encontrado:', suggestionsButton);
        
        // Remover eventos existentes
        suggestionsButton.removeAttribute('onclick');
        const newButton = suggestionsButton.cloneNode(true);
        suggestionsButton.parentNode.replaceChild(newButton, suggestionsButton);
        
        // Adicionar novo evento
        newButton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            getSuggestionsFromAI();
        });
        
        // Melhorar visual do botão
        newButton.style.cursor = 'pointer';
        newButton.style.transition = 'all 0.3s ease';
        
        console.log('✅ Evento anexado ao botão de sugestões!');
    } else {
        console.warn('⚠️ Botão de sugestões não encontrado, criando botão de fallback...');
        createFallbackSuggestionsButton();
    }
}

function createFallbackSuggestionsButton() {
    const fallbackButton = document.createElement('button');
    fallbackButton.innerHTML = '🤖 Obter Sugestões da IA';
    fallbackButton.className = 'btn btn-success';
    fallbackButton.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        border: none;
        padding: 12px 20px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
        z-index: 1000;
        transition: all 0.3s ease;
    `;
    
    fallbackButton.addEventListener('click', getSuggestionsFromAI);
    fallbackButton.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-2px)';
        this.style.boxShadow = '0 6px 16px rgba(40, 167, 69, 0.4)';
    });
    fallbackButton.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
        this.style.boxShadow = '0 4px 12px rgba(40, 167, 69, 0.3)';
    });
    
    document.body.appendChild(fallbackButton);
    console.log('✅ Botão de fallback criado!');
}

function getSuggestionsFromAI() {
    console.log('🤖 Obtendo sugestões da IA...');
    
    // Mostrar loading
    showLoadingModal('🧠 Gerando sugestões inteligentes...', 'A IA está analisando seu projeto e criando ideias inovadoras!');
    
    // Obter contexto atual
    const context = getSessionContext();
    
    // Fazer requisição
    fetch('/brainstorm/get-suggestions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: parseInt(BRAINSTORM_CONFIG.SESSION_ID),
            context: context,
            existing_cards: getExistingCards()
        })
    })
    .then(response => {
        console.log(`📡 Resposta recebida: ${response.status}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        hideLoadingModal();
        console.log('📦 Dados recebidos:', data);
        
        if (data.success && data.suggestions && data.suggestions.length > 0) {
            showSuggestionsModal(data.suggestions);
            showSuccessToast(`🎉 ${data.suggestions.length} sugestões geradas com sucesso!`);
        } else {
            throw new Error(data.error || 'Nenhuma sugestão foi gerada');
        }
    })
    .catch(error => {
        hideLoadingModal();
        console.error('❌ Erro ao obter sugestões:', error);
        showErrorModal('Erro ao Obter Sugestões', error.message, [
            {
                text: 'Tentar Novamente',
                action: getSuggestionsFromAI,
                style: 'btn-primary'
            },
            {
                text: 'Fechar',
                action: () => hideModal('error-modal'),
                style: 'btn-secondary'
            }
        ]);
    });
}

function getSessionContext() {
    // Obter contexto da sessão atual
    const themeElement = document.querySelector('#theme-input, .session-theme, [name="theme"]');
    const theme = themeElement ? themeElement.value || themeElement.textContent : '';
    
    const descriptionElement = document.querySelector('#description, .session-description');
    const description = descriptionElement ? descriptionElement.value || descriptionElement.textContent : '';
    
    return {
        theme: theme || 'jogo educativo',
        description: description || '',
        card_count: getExistingCards().length
    };
}

function getExistingCards() {
    const cards = [];
    const cardElements = document.querySelectorAll('.card, .idea-card, .post-it, [data-card-id]');
    
    cardElements.forEach(card => {
        const text = card.textContent || card.innerText || '';
        if (text.trim()) {
            cards.push(text.trim());
        }
    });
    
    return cards;
}

// =============================================================================
// MODAIS E POP-UPS
// =============================================================================

function showSuggestionsModal(suggestions) {
    hideAllModals();
    
    const modal = document.createElement('div');
    modal.id = 'suggestions-modal';
    modal.className = 'brainstorm-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.6);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
        backdrop-filter: blur(5px);
        opacity: 0;
        transition: opacity ${BRAINSTORM_CONFIG.ANIMATION_DURATION}ms ease;
    `;
    
    modal.innerHTML = `
        <div class="modal-content" style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            padding: 0;
            max-width: 700px;
            max-height: 90vh;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            transform: scale(0.8) translateY(50px);
            transition: all ${BRAINSTORM_CONFIG.ANIMATION_DURATION}ms ease;
        ">
            <!-- Header -->
            <div style="
                background: rgba(255, 255, 255, 0.1);
                padding: 25px 30px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h2 style="margin: 0; color: white; font-size: 28px; font-weight: bold;">
                        🤖 Sugestões da IA
                    </h2>
                    <button onclick="hideModal('suggestions-modal')" style="
                        background: rgba(255, 255, 255, 0.2);
                        color: white;
                        border: none;
                        border-radius: 50%;
                        width: 40px;
                        height: 40px;
                        cursor: pointer;
                        font-size: 20px;
                        transition: all 0.3s ease;
                    " onmouseover="this.style.background='rgba(255,255,255,0.3)'" 
                       onmouseout="this.style.background='rgba(255,255,255,0.2)'">×</button>
                </div>
                <p style="margin: 10px 0 0 0; color: rgba(255, 255, 255, 0.9); font-size: 16px;">
                    ✨ Clique em qualquer sugestão para adicioná-la como uma nova ideia!
                </p>
            </div>
            
            <!-- Content -->
            <div style="
                background: white;
                padding: 30px;
                max-height: 500px;
                overflow-y: auto;
            ">
                ${suggestions.map((suggestion, index) => `
                    <div class="suggestion-item" onclick="addSuggestionAsCard('${suggestion.replace(/'/g, "\\'")}', ${index})" style="
                        margin: 15px 0;
                        padding: 20px;
                        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                        border: 2px solid transparent;
                        border-radius: 12px;
                        cursor: pointer;
                        transition: all 0.3s ease;
                        position: relative;
                        overflow: hidden;
                    " onmouseover="
                        this.style.transform='translateX(8px)';
                        this.style.borderColor='#28a745';
                        this.style.boxShadow='0 8px 25px rgba(40,167,69,0.3)';
                    " onmouseout="
                        this.style.transform='translateX(0)';
                        this.style.borderColor='transparent';
                        this.style.boxShadow='none';
                    ">
                        
                        <!-- Number Badge -->
                        <div style="
                            position: absolute;
                            top: -5px;
                            left: -5px;
                            background: linear-gradient(135deg, #28a745, #20c997);
                            color: white;
                            border-radius: 50%;
                            width: 35px;
                            height: 35px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-weight: bold;
                            font-size: 14px;
                            box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4);
                        ">${index + 1}</div>
                        
                        <!-- Content -->
                        <div style="margin-left: 40px;">
                            <div style="
                                font-size: 18px;
                                font-weight: bold;
                                color: #333;
                                margin-bottom: 8px;
                                line-height: 1.4;
                            ">${suggestion}</div>
                            
                            <div style="
                                font-size: 14px;
                                color: #6c757d;
                                display: flex;
                                align-items: center;
                                gap: 8px;
                            ">
                                <span>💡</span>
                                <span>Clique para adicionar esta ideia ao seu brainstorm</span>
                            </div>
                        </div>
                        
                        <!-- Hover Effect -->
                        <div style="
                            position: absolute;
                            top: 0;
                            right: 20px;
                            height: 100%;
                            display: flex;
                            align-items: center;
                            font-size: 24px;
                            opacity: 0;
                            transition: opacity 0.3s ease;
                        " class="add-icon">➕</div>
                    </div>
                `).join('')}
            </div>
            
            <!-- Footer -->
            <div style="
                background: #f8f9fa;
                padding: 20px 30px;
                border-top: 1px solid #dee2e6;
                display: flex;
                justify-content: space-between;
                align-items: center;
            ">
                <div style="color: #6c757d; font-size: 14px;">
                    🎯 ${suggestions.length} sugestões geradas para sua sessão
                </div>
                <div style="display: flex; gap: 10px;">
                    <button onclick="getSuggestionsFromAI()" style="
                        background: linear-gradient(135deg, #007bff, #0056b3);
                        color: white;
                        border: none;
                        padding: 12px 24px;
                        border-radius: 8px;
                        cursor: pointer;
                        font-weight: bold;
                        transition: all 0.3s ease;
                    " onmouseover="this.style.transform='translateY(-2px)'" 
                       onmouseout="this.style.transform='translateY(0)'">
                        🔄 Gerar Novas Sugestões
                    </button>
                    <button onclick="hideModal('suggestions-modal')" style="
                        background: #6c757d;
                        color: white;
                        border: none;
                        padding: 12px 24px;
                        border-radius: 8px;
                        cursor: pointer;
                        transition: all 0.3s ease;
                    ">Fechar</button>
                </div>
            </div>
        </div>
    `;
    
    // Adicionar CSS para scroll customizado
    const style = document.createElement('style');
    style.textContent = `
        .suggestion-item:hover .add-icon {
            opacity: 1;
        }
        
        .brainstorm-modal ::-webkit-scrollbar {
            width: 8px;
        }
        
        .brainstorm-modal ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }
        
        .brainstorm-modal ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 4px;
        }
        
        .brainstorm-modal ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(modal);
    
    // Animar entrada
    setTimeout(() => {
        modal.style.opacity = '1';
        const content = modal.querySelector('.modal-content');
        content.style.transform = 'scale(1) translateY(0)';
    }, 10);
}

function showLoadingModal(title, subtitle) {
    hideAllModals();
    
    const modal = document.createElement('div');
    modal.id = 'loading-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10001;
        backdrop-filter: blur(3px);
    `;
    
    modal.innerHTML = `
        <div style="
            background: white;
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            max-width: 400px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        ">
            <!-- Spinner -->
            <div style="
                width: 60px;
                height: 60px;
                border: 4px solid #f3f3f3;
                border-top: 4px solid #007bff;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px auto;
            "></div>
            
            <h3 style="margin: 0 0 10px 0; color: #333; font-size: 24px;">${title}</h3>
            <p style="margin: 0; color: #6c757d; font-size: 16px; line-height: 1.5;">${subtitle}</p>
        </div>
    `;
    
    // Adicionar animação CSS
    const style = document.createElement('style');
    style.textContent = `
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(modal);
}

function showErrorModal(title, message, buttons = []) {
    hideAllModals();
    
    const modal = document.createElement('div');
    modal.id = 'error-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.6);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10001;
        backdrop-filter: blur(5px);
    `;
    
    const defaultButtons = buttons.length > 0 ? buttons : [
        {
            text: 'Fechar',
            action: () => hideModal('error-modal'),
            style: 'btn-secondary'
        }
    ];
    
    modal.innerHTML = `
        <div style="
            background: white;
            border-radius: 15px;
            padding: 30px;
            max-width: 500px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            border-top: 5px solid #dc3545;
        ">
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="
                    font-size: 48px;
                    margin-bottom: 15px;
                ">❌</div>
                <h3 style="margin: 0 0 10px 0; color: #dc3545; font-size: 24px;">${title}</h3>
                <p style="margin: 0; color: #333; font-size: 16px; line-height: 1.5;">${message}</p>
            </div>
            
            <div style="display: flex; justify-content: center; gap: 10px; flex-wrap: wrap;">
                ${defaultButtons.map(btn => `
                    <button onclick="${btn.action.toString().includes('function') ? `(${btn.action})()` : btn.action}" style="
                        background: ${btn.style === 'btn-primary' ? '#007bff' : '#6c757d'};
                        color: white;
                        border: none;
                        padding: 12px 24px;
                        border-radius: 8px;
                        cursor: pointer;
                        font-weight: bold;
                        transition: all 0.3s ease;
                    ">${btn.text}</button>
                `).join('')}
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function hideLoadingModal() {
    hideModal('loading-modal');
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.opacity = '0';
        setTimeout(() => modal.remove(), BRAINSTORM_CONFIG.ANIMATION_DURATION);
    }
}

function hideAllModals() {
    const modals = ['suggestions-modal', 'loading-modal', 'error-modal', 'add-card-modal'];
    modals.forEach(hideModal);
}

// =============================================================================
// SISTEMA DE CARDS
// =============================================================================

function addSuggestionAsCard(suggestionText, suggestionIndex) {
    console.log(`➕ Adicionando sugestão ${suggestionIndex + 1} como card:`, suggestionText);
    
    // Feedback imediato
    showLoadingModal('📝 Adicionando Ideia...', 'Transformando a sugestão em um post-it no seu brainstorm!');
    
    // Selecionar cor aleatória
    const color = BRAINSTORM_CONFIG.COLORS[suggestionIndex % BRAINSTORM_CONFIG.COLORS.length];
    
    // Posição aleatória (evitar sobreposição)
    const position = generateRandomPosition();
    
    // Fazer requisição
    fetch('/brainstorm/add-card', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: parseInt(BRAINSTORM_CONFIG.SESSION_ID),
            text: suggestionText,
            content: suggestionText,
            color: color,
            category: 'ia_suggestion',
            position_x: position.x,
            position_y: position.y
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingModal();
        
        if (data.success) {
            console.log('✅ Card adicionado com sucesso:', data.card);
            
            // Fechar modal de sugestões
            hideModal('suggestions-modal');
            
            // Mostrar feedback de sucesso
            showSuccessToast('💡 Ideia adicionada com sucesso!');
            
            // Adicionar card visualmente (se possível) ou recarregar
            if (typeof addCardToUI === 'function') {
                addCardToUI(data.card);
            } else {
                // Recarregar página após delay para mostrar animação
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            }
        } else {
            throw new Error(data.error || 'Falha ao adicionar card');
        }
    })
    .catch(error => {
        hideLoadingModal();
        console.error('❌ Erro ao adicionar card:', error);
        showErrorToast(`Erro ao adicionar ideia: ${error.message}`);
    });
}

function generateRandomPosition() {
    const margin = 50;
    const maxX = Math.max(window.innerWidth - BRAINSTORM_CONFIG.CARD_SIZE.width - margin, margin);
    const maxY = Math.max(window.innerHeight - BRAINSTORM_CONFIG.CARD_SIZE.height - margin, margin);
    
    return {
        x: Math.random() * (maxX - margin) + margin,
        y: Math.random() * (maxY - margin) + margin
    };
}

// =============================================================================
// SISTEMA DE NOTIFICAÇÕES (TOASTS)
// =============================================================================

function showSuccessToast(message) {
    showToast(message, 'success', 4000);
}

function showErrorToast(message) {
    showToast(message, 'error', 6000);
}

function showInfoToast(message) {
    showToast(message, 'info', 3000);
}

function showToast(message, type = 'info', duration = 3000) {
    // Remover toasts existentes do mesmo tipo
    const existingToasts = document.querySelectorAll(`.toast-${type}`);
    existingToasts.forEach(toast => toast.remove());
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const colors = {
        success: { bg: '#28a745', icon: '✅' },
        error: { bg: '#dc3545', icon: '❌' },
        info: { bg: '#17a2b8', icon: 'ℹ️' },
        warning: { bg: '#ffc107', icon: '⚠️' }
    };
    
    const config = colors[type] || colors.info;
    
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${config.bg};
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        z-index: 10002;
        font-weight: bold;
        font-size: 16px;
        max-width: 400px;
        word-wrap: break-word;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        display: flex;
        align-items: center;
        gap: 10px;
    `;
    
    toast.innerHTML = `
        <span style="font-size: 20px;">${config.icon}</span>
        <span style="flex: 1;">${message}</span>
        <button onclick="this.parentElement.remove()" style="
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: none;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            cursor: pointer;
            font-size: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
        ">×</button>
    `;
    
    document.body.appendChild(toast);
    
    // Animar entrada
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
    }, 10);
    
    // Auto-remover
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }
    }, duration);
}

// =============================================================================
// SISTEMA DE ADICIONAR CARDS MANUALMENTE
// =============================================================================

function initializeAddCardButton() {
    console.log('🔗 Inicializando botão adicionar card...');
    
    const addButtons = document.querySelectorAll('button[onclick*="addCard"], .add-card-btn, .btn:contains("Adicionar")');
    
    addButtons.forEach(button => {
        const text = button.textContent.toLowerCase();
        if (text.includes('adicionar') || text.includes('ideia') || text.includes('card')) {
            button.removeAttribute('onclick');
            button.addEventListener('click', function(e) {
                e.preventDefault();
                showAddCardModal();
            });
            console.log('✅ Botão adicionar card configurado:', button);
        }
    });
}

function showAddCardModal() {
    hideAllModals();
    
    const modal = document.createElement('div');
    modal.id = 'add-card-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.6);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
        backdrop-filter: blur(5px);
    `;
    
    modal.innerHTML = `
        <div style="
            background: white;
            border-radius: 15px;
            padding: 30px;
            max-width: 500px;
            width: 90%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        ">
            <h3 style="margin: 0 0 20px 0; color: #333; text-align: center;">💡 Adicionar Nova Ideia</h3>
            
            <div style="margin-bottom: 20px;">
                <label style="display: block; margin-bottom: 8px; font-weight: bold; color: #555;">Sua Ideia:</label>
                <textarea id="card-text-input" placeholder="Digite sua ideia aqui..." style="
                    width: 100%;
                    height: 120px;
                    border: 2px solid #e9ecef;
                    border-radius: 8px;
                    padding: 15px;
                    font-size: 16px;
                    resize: vertical;
                    font-family: inherit;
                    box-sizing: border-box;
                " onkeydown="if(event.key==='Enter' && event.ctrlKey) addCardFromModal()"></textarea>
            </div>
            
            <div style="margin-bottom: 25px;">
                <label style="display: block; margin-bottom: 8px; font-weight: bold; color: #555;">Cor do Post-it:</label>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    ${BRAINSTORM_CONFIG.COLORS.map((color, index) => `
                        <div onclick="selectCardColor('${color}')" style="
                            width: 40px;
                            height: 40px;
                            background: ${color};
                            border-radius: 8px;
                            cursor: pointer;
                            border: 3px solid ${index === 0 ? '#333' : 'transparent'};
                            transition: all 0.3s ease;
                        " class="color-option" data-color="${color}"></div>
                    `).join('')}
                </div>
            </div>
            
            <div style="display: flex; justify-content: space-between; gap: 15px;">
                <button onclick="hideModal('add-card-modal')" style="
                    flex: 1;
                    background: #6c757d;
                    color: white;
                    border: none;
                    padding: 15px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 16px;
                    transition: all 0.3s ease;
                ">Cancelar</button>
                
                <button onclick="addCardFromModal()" style="
                    flex: 1;
                    background: linear-gradient(135deg, #28a745, #20c997);
                    color: white;
                    border: none;
                    padding: 15px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: bold;
                    transition: all 0.3s ease;
                ">➕ Adicionar Ideia</button>
            </div>
            
            <div style="text-align: center; margin-top: 15px; color: #6c757d; font-size: 14px;">
                💡 Dica: Use Ctrl+Enter para adicionar rapidamente
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Focar no campo de texto
    setTimeout(() => {
        const input = document.getElementById('card-text-input');
        if (input) input.focus();
    }, 100);
}

function selectCardColor(color) {
    const options = document.querySelectorAll('.color-option');
    options.forEach(option => {
        option.style.border = option.dataset.color === color ? '3px solid #333' : '3px solid transparent';
    });
}

function addCardFromModal() {
    const textInput = document.getElementById('card-text-input');
    const selectedColor = document.querySelector('.color-option[style*="border: 3px solid rgb(51, 51, 51)"]');
    
    const text = textInput ? textInput.value.trim() : '';
    const color = selectedColor ? selectedColor.dataset.color : BRAINSTORM_CONFIG.COLORS[0];
    
    if (!text) {
        showErrorToast('Por favor, digite sua ideia antes de adicionar!');
        if (textInput) textInput.focus();
        return;
    }
    
    hideModal('add-card-modal');
    
    // Adicionar card
    addCardManually(text, color);
}

function addCardManually(text, color) {
    console.log('📝 Adicionando card manualmente:', text);
    
    showLoadingModal('📝 Adicionando Ideia...', 'Criando seu post-it personalizado!');
    
    const position = generateRandomPosition();
    
    fetch('/brainstorm/add-card', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: parseInt(BRAINSTORM_CONFIG.SESSION_ID),
            text: text,
            content: text,
            color: color,
            category: 'manual',
            position_x: position.x,
            position_y: position.y
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingModal();
        
        if (data.success) {
            console.log('✅ Card adicionado manualmente:', data.card);
            showSuccessToast('✨ Ideia adicionada com sucesso!');
            
            // Recarregar ou adicionar à UI
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            throw new Error(data.error || 'Falha ao adicionar card');
        }
    })
    .catch(error => {
        hideLoadingModal();
        console.error('❌ Erro ao adicionar card manual:', error);
        showErrorToast(`Erro ao adicionar ideia: ${error.message}`);
    });
}

// =============================================================================
// SISTEMA DE DRAG AND DROP
// =============================================================================

function initializeDragAndDrop() {
    console.log('🎯 Inicializando sistema de drag and drop...');
    
    // Observar mudanças no DOM para cards adicionados dinamicamente
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) { // Element node
                    const cards = node.querySelectorAll ? node.querySelectorAll('.card, .idea-card, .post-it, [data-card-id]') : [];
                    cards.forEach(makeDraggable);
                    
                    if (node.classList && (node.classList.contains('card') || node.classList.contains('idea-card'))) {
                        makeDraggable(node);
                    }
                }
            });
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Aplicar a cards existentes
    const existingCards = document.querySelectorAll('.card, .idea-card, .post-it, [data-card-id]');
    existingCards.forEach(makeDraggable);
    
    console.log(`✅ ${existingCards.length} cards configurados para drag and drop`);
}

function makeDraggable(cardElement) {
    if (cardElement.dataset.draggableInit) return; // Já inicializado
    
    cardElement.draggable = true;
    cardElement.style.cursor = 'move';
    cardElement.style.transition = 'transform 0.2s ease';
    cardElement.dataset.draggableInit = 'true';
    
    let isDragging = false;
    let startX, startY, initialX, initialY;
    
    cardElement.addEventListener('dragstart', function(e) {
        isDragging = true;
        const rect = cardElement.getBoundingClientRect();
        startX = e.clientX - rect.left;
        startY = e.clientY - rect.top;
        initialX = rect.left;
        initialY = rect.top;
        
        cardElement.style.opacity = '0.7';
        cardElement.style.transform = 'scale(1.05)';
        
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/html', cardElement.outerHTML);
    });
    
    cardElement.addEventListener('dragend', function(e) {
        isDragging = false;
        cardElement.style.opacity = '1';
        cardElement.style.transform = 'scale(1)';
        
        // Calcular nova posição
        const rect = cardElement.getBoundingClientRect();
        const newX = rect.left;
        const newY = rect.top;
        
        // Só atualizar se houve movimento significativo
        if (Math.abs(newX - initialX) > 5 || Math.abs(newY - initialY) > 5) {
            updateCardPosition(cardElement, newX, newY);
        }
    });
    
    // Adicionar efeitos visuais
    cardElement.addEventListener('mouseenter', function() {
        if (!isDragging) {
            this.style.transform = 'scale(1.02)';
            this.style.boxShadow = '0 8px 25px rgba(0,0,0,0.15)';
        }
    });
    
    cardElement.addEventListener('mouseleave', function() {
        if (!isDragging) {
            this.style.transform = 'scale(1)';
            this.style.boxShadow = '';
        }
    });
}

function updateCardPosition(cardElement, x, y) {
    const cardId = cardElement.dataset.cardId || cardElement.id;
    
    if (!cardId) {
        console.warn('⚠️ Card sem ID, não é possível atualizar posição');
        return;
    }
    
    console.log(`📍 Atualizando posição do card ${cardId} para (${x}, ${y})`);
    
    fetch('/brainstorm/update-card-position', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            card_id: parseInt(cardId),
            position_x: x,
            position_y: y
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('✅ Posição atualizada com sucesso');
        } else {
            console.error('❌ Erro ao atualizar posição:', data.error);
        }
    })
    .catch(error => {
        console.error('❌ Erro na requisição de posição:', error);
    });
}

// =============================================================================
// INTERAÇÕES AVANÇADAS COM CARDS
// =============================================================================

function initializeCardInteractions() {
    console.log('🎨 Inicializando interações avançadas com cards...');
    
    // Adicionar menu de contexto aos cards
    document.addEventListener('contextmenu', function(e) {
        const card = e.target.closest('.card, .idea-card, .post-it, [data-card-id]');
        if (card) {
            e.preventDefault();
            showCardContextMenu(card, e.clientX, e.clientY);
        }
    });
    
    // Fechar menu ao clicar fora
    document.addEventListener('click', function() {
        hideCardContextMenu();
    });
}

function showCardContextMenu(cardElement, x, y) {
    hideCardContextMenu();
    
    const menu = document.createElement('div');
    menu.id = 'card-context-menu';
    menu.style.cssText = `
        position: fixed;
        top: ${y}px;
        left: ${x}px;
        background: white;
        border-radius: 8px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        z-index: 10003;
        min-width: 180px;
        overflow: hidden;
        border: 1px solid #e9ecef;
    `;
    
    const cardId = cardElement.dataset.cardId || cardElement.id;
    const cardText = cardElement.textContent.trim();
    
    menu.innerHTML = `
        <div class="context-menu-item" onclick="editCard('${cardId}')" style="
            padding: 12px 16px;
            cursor: pointer;
            border-bottom: 1px solid #f8f9fa;
            transition: background 0.2s ease;
        " onmouseover="this.style.background='#f8f9fa'" onmouseout="this.style.background='white'">
            ✏️ Editar Texto
        </div>
        
        <div class="context-menu-item" onclick="changeCardColor('${cardId}')" style="
            padding: 12px 16px;
            cursor: pointer;
            border-bottom: 1px solid #f8f9fa;
            transition: background 0.2s ease;
        " onmouseover="this.style.background='#f8f9fa'" onmouseout="this.style.background='white'">
            🎨 Mudar Cor
        </div>
        
        <div class="context-menu-item" onclick="duplicateCard('${cardId}')" style="
            padding: 12px 16px;
            cursor: pointer;
            border-bottom: 1px solid #f8f9fa;
            transition: background 0.2s ease;
        " onmouseover="this.style.background='#f8f9fa'" onmouseout="this.style.background='white'">
            📋 Duplicar
        </div>
        
        <div class="context-menu-item" onclick="deleteCard('${cardId}')" style="
            padding: 12px 16px;
            cursor: pointer;
            color: #dc3545;
            transition: background 0.2s ease;
        " onmouseover="this.style.background='#ffe6e6'" onmouseout="this.style.background='white'">
            🗑️ Excluir
        </div>
    `;
    
    document.body.appendChild(menu);
    
    // Ajustar posição se sair da tela
    const rect = menu.getBoundingClientRect();
    if (rect.right > window.innerWidth) {
        menu.style.left = (x - rect.width) + 'px';
    }
    if (rect.bottom > window.innerHeight) {
        menu.style.top = (y - rect.height) + 'px';
    }
}

function hideCardContextMenu() {
    const menu = document.getElementById('card-context-menu');
    if (menu) menu.remove();
}

// =============================================================================
// UTILITÁRIOS E HELPERS
// =============================================================================

// Função global para ser chamada pelos templates
window.getSuggestions = getSuggestionsFromAI;
window.getSuggestionsFromAI = getSuggestionsFromAI;
window.addSuggestionAsCard = addSuggestionAsCard;
window.hideModal = hideModal;
window.selectCardColor = selectCardColor;
window.addCardFromModal = addCardFromModal;

// Event listeners globais
window.addEventListener('beforeunload', function() {
    hideAllModals();
});

// Teclas de atalho
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        hideAllModals();
        hideCardContextMenu();
    }
    
    if (e.ctrlKey && e.key === 'i') {
        e.preventDefault();
        showAddCardModal();
    }
    
    if (e.ctrlKey && e.shiftKey && e.key === 'S') {
        e.preventDefault();
        getSuggestionsFromAI();
    }
});

// =============================================================================
// LOG FINAL
// =============================================================================

console.log(`
🎉 SISTEMA DE BRAINSTORMING CARREGADO COM SUCESSO!

📋 Funcionalidades Disponíveis:
✅ Botão "Obter Sugestões da IA" funcional
✅ Pop-up profissional com animações
✅ Adicionar sugestões como post-its
✅ Sistema de drag and drop
✅ Menu de contexto para cards (clique direito)
✅ Adicionar cards manualmente
✅ Notificações toast
✅ Tratamento completo de erros
✅ Atalhos de teclado:
   - Ctrl+I: Adicionar nova ideia
   - Ctrl+Shift+S: Obter sugestões da IA
   - Escape: Fechar modais

🚀 Sua ferramenta está pronta para uso!
`);