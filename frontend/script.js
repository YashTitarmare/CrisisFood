/**
 * CrisisFood AI - Frontend JavaScript
 */

// ============================================
// State
// ============================================
let conversationHistory = [];
let currentCrisis = 'general';
let isProcessing = false;

// Severe crisis types that show SOS alert
const severeCrisisTypes = ['flood', 'earthquake', 'outbreak', 'storm'];

// Section mapping for parsing AI responses
const sectionMap = {
  '✅': { className: 'safe', title: '✅ Safe to Eat Now' },
  '⚠️': { className: 'avoid', title: '⚠️ Avoid / Danger' },
  '💧': { className: 'water', title: '💧 Water Safety' },
  '📦': { className: 'prep', title: '📦 Prep & Storage' },
  '🆘': { className: 'emergency', title: '🆘 Emergency Tip' },
};

// ============================================
// Crisis Type Selection
// ============================================
function selectCrisis(element) {
  // Update active chip
  document.querySelectorAll('.chip').forEach(chip => {
    chip.classList.remove('active');
  });
  element.classList.add('active');
  
  // Update current crisis
  currentCrisis = element.dataset.crisis;
  
  // Show/hide SOS alert for severe crisis types
  const sosAlert = document.getElementById('sos');
  if (severeCrisisTypes.includes(currentCrisis)) {
    sosAlert.classList.add('show');
  } else {
    sosAlert.classList.remove('show');
  }
}

// ============================================
// Quick Question Buttons
// ============================================
function quickSend(question) {
  document.getElementById('message-input').value = question;
  sendMessage();
}

// ============================================
// Input Handling
// ============================================
function handleKeyDown(event) {
  // Send on Enter (without Shift)
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
}

function autoResize(textarea) {
  // Auto-resize textarea up to max height
  textarea.style.height = 'auto';
  textarea.style.height = Math.min(textarea.scrollHeight, 110) + 'px';
}

// ============================================
// Send Message
// ============================================
async function sendMessage() {
  if (isProcessing) return;
  
  const input = document.getElementById('message-input');
  const message = input.value.trim();
  
  if (!message) return;
  
  // Clear input and reset height
  input.value = '';
  input.style.height = 'auto';
  
  // Disable send button
  isProcessing = true;
  document.getElementById('send-btn').disabled = true;
  
  // Remove welcome card
  const welcomeCard = document.getElementById('welcome-card');
  if (welcomeCard) {
    welcomeCard.remove();
  }
  
  // Add user message
  addUserMessage(message);
  
  // Show typing indicator
  showTypingIndicator();
  
  // Stream response from backend
  await streamResponse(message);
  
  // Re-enable send button
  document.getElementById('send-btn').disabled = false;
  isProcessing = false;
  input.focus();
}

// ============================================
// Stream Response from Backend
// ============================================
async function streamResponse(message) {
  let fullResponse = '';
  
  try {
    const response = await fetch('/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        history: conversationHistory,
        crisis_type: currentCrisis
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    // Create bot message bubble
    const botBubble = addBotMessage();
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      // Decode and buffer
      buffer += decoder.decode(value, { stream: true });
      
      // Process complete lines
      const lines = buffer.split('\n');
      buffer = lines.pop(); // Keep incomplete line in buffer
      
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        
        try {
          const data = JSON.parse(line.slice(6));
          
          if (data.done) {
            // Stream complete
            botBubble.innerHTML = parseResponse(fullResponse);
            updateTimestamp();
          } else if (data.text) {
            // Add text to response
            fullResponse += data.text;
            botBubble.textContent = fullResponse;
            scrollToBottom();
          } else if (data.error) {
            // Handle error
            botBubble.innerHTML = `<span style="color: var(--danger)">❌ ${escapeHtml(data.error)}</span>`;
          }
        } catch (e) {
          // Ignore parse errors for incomplete JSON
        }
      }
    }
    
  } catch (error) {
    console.error('Error:', error);
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) typingIndicator.remove();
    
    const errorBubble = addBotMessage();
    errorBubble.innerHTML = `<span style="color: var(--danger)">❌ Connection error. Is the server running?</span>`;
  }
  
  // Update conversation history
  conversationHistory.push({ role: 'user', content: message });
  conversationHistory.push({ role: 'assistant', content: fullResponse });
  
  // Keep only last 20 messages
  if (conversationHistory.length > 20) {
    conversationHistory = conversationHistory.slice(-20);
  }
  
  // Remove typing indicator if still present
  const typingIndicator = document.getElementById('typing-indicator');
  if (typingIndicator) {
    typingIndicator.remove();
  }
  
  // Remove bot message ID for future reference
  const botLive = document.getElementById('bot-live');
  if (botLive) {
    botLive.removeAttribute('id');
  }
}

// ============================================
// UI Helper Functions
// ============================================
function addUserMessage(text) {
  const chat = document.getElementById('chat');
  const time = getCurrentTime();
  
  const html = `
    <div class="msg user">
      <div class="bubble-wrap">
        <div class="bubble user">${escapeHtml(text)}</div>
        <span class="timestamp">${time}</span>
      </div>
      <div class="avatar user">👤</div>
    </div>
  `;
  
  chat.insertAdjacentHTML('beforeend', html);
  scrollToBottom();
}

function addBotMessage() {
  const chat = document.getElementById('chat');
  const time = getCurrentTime();
  
  const html = `
    <div class="msg" id="bot-live">
      <div class="avatar bot">🍱</div>
      <div class="bubble-wrap">
        <div class="bubble bot" id="bot-bubble"></div>
        <span class="timestamp" id="bot-timestamp">${time}</span>
      </div>
    </div>
  `;
  
  chat.insertAdjacentHTML('beforeend', html);
  scrollToBottom();
  
  return document.getElementById('bot-bubble');
}

function showTypingIndicator() {
  const chat = document.getElementById('chat');
  
  const html = `
    <div class="msg" id="typing-indicator">
      <div class="avatar bot">🍱</div>
      <div class="bubble-wrap">
        <div class="bubble bot">
          <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>
  `;
  
  chat.insertAdjacentHTML('beforeend', html);
  scrollToBottom();
}

function updateTimestamp() {
  const timestamp = document.getElementById('bot-timestamp');
  if (timestamp) {
    timestamp.textContent = getCurrentTime();
  }
}

function scrollToBottom() {
  const chat = document.getElementById('chat');
  chat.scrollTop = chat.scrollHeight;
}

function getCurrentTime() {
  return new Date().toLocaleTimeString('en-IN', {
    hour: '2-digit',
    minute: '2-digit'
  });
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// ============================================
// Parse AI Response into Sections
// ============================================
function parseResponse(rawText) {
  let html = '';
  let currentSection = null;
  let buffer = [];
  
  const flushBuffer = () => {
    const content = buffer.join('<br>').trim();
    if (!content) {
      buffer = [];
      return;
    }
    
    if (currentSection) {
      const section = sectionMap[currentSection];
      html += `<div class="response-section ${section.className}">
        <div class="section-title">${section.title}</div>
        ${content}
      </div>`;
    } else {
      html += `<p style="margin: 4px 0; font-size: 14px">${content}</p>`;
    }
    
    buffer = [];
  };
  
  // Process each line
  const lines = rawText.split('\n');
  for (const line of lines) {
    const trimmed = line.trim();
    let matched = false;
    
    // Check for section markers
    for (const key of Object.keys(sectionMap)) {
      // Check for line starting with emoji OR "1. ✅" format
      if (trimmed.startsWith(key) || trimmed.match(new RegExp(`^\\d+\\.\\s*${key}`))) {
        flushBuffer();
        currentSection = key;
        
        // Extract content after the marker
        let content = trimmed
          .replace(/^\d+\.\s*/, '')  // Remove "1. " prefix
          .replace(key, '')            // Remove emoji
          .replace(/^[\s:\u2013\-]+/, ''); // Remove leading punctuation
        
        if (content) {
          buffer.push(escapeHtml(content));
        }
        
        matched = true;
        break;
      }
    }
    
    if (!matched) {
      buffer.push(escapeHtml(trimmed));
    }
  }
  
  flushBuffer();
  
  // Fallback if no sections found
  return html || `<p>${escapeHtml(rawText)}</p>`;
}

// ============================================
// Initialize
// ============================================
// Focus input on load
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('message-input').focus();
});
