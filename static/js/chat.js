async function sendChat(message) {
    const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    });
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let result = '';
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        result += chunk;
        console.log(chunk); // Print each chunk as it arrives
    }
    
    return result;
}

// UI Handling Code
document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.getElementById('chat-container');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const clearBtn = document.getElementById('clear-btn');

    // Add message to chat UI
    function addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'bubble';
        bubbleDiv.textContent = content;
        
        messageDiv.appendChild(bubbleDiv);
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Modified wrapper to parse JSON response
    async function handleUserMessage(message) {
        // Add user message to UI
        addMessage(message, 'user');
        
        // Disable UI during processing
        sendBtn.disabled = true;
        userInput.disabled = true;
        
        // Create bot message placeholder
        const botMessageDiv = document.createElement('div');
        botMessageDiv.className = 'message bot-message';
        const botBubble = document.createElement('div');
        botBubble.className = 'bubble';
        botBubble.textContent = '...'; // Loading indicator
        botMessageDiv.appendChild(botBubble);
        chatContainer.appendChild(botMessageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        try {
            // Use your EXACT original function
            const rawResponse = await sendChat(message);
            
            // PARSE THE JSON RESPONSE AND EXTRACT THE CONTENT
            let responseContent = rawResponse;
            try {
                const parsed = JSON.parse(rawResponse);
                if (parsed.response) {
                    responseContent = parsed.response;
                }
            } catch (e) {
                console.log('Response is not JSON, using raw response');
            }
            
            // Update bot message with final response
            botBubble.textContent = responseContent;
        } catch (error) {
            console.error('Chat error:', error);
            botBubble.textContent = 'Error: ' + error.message;
        }
        
        // Re-enable UI
        sendBtn.disabled = false;
        userInput.disabled = false;
        userInput.focus();
    }

    // Event handlers
    sendBtn.addEventListener('click', () => {
        const message = userInput.value.trim();
        if (!message) return;
        
        userInput.value = '';
        handleUserMessage(message);
    });

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendBtn.click();
    });

    clearBtn.addEventListener('click', () => {
        chatContainer.innerHTML = '';
    });
});