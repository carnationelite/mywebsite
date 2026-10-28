document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.querySelector('.ai-chatbot-toggle');
    const window = document.querySelector('.ai-chatbot-window');
    const close = document.querySelector('.ai-chatbot-close');
    const overlay = document.querySelector('.ai-chatbot-overlay');
    const input = document.querySelector('.ai-chatbot-input-area input');
    const sendBtn = document.querySelector('.ai-chatbot-send');
    const messagesContainer = document.querySelector('.ai-chatbot-messages');

    if (!toggle || !window) return;

    const knowledgeBase = [
        {
            keywords: ['about', 'who', 'company', 'experience', 'years', 'history', 'professional', 'center'],
            response: "CarNation Elite is a professional Auto Repair & Service Center in Dallas, TX. We have 10-15 years of hands-on experience and a team of certified technicians providing reliable, honest, and affordable care."
        },
        {
            keywords: ['expertise', 'certified', 'mechanic', 'technician', 'diagnostics', 'diagnostic', 'expert'],
            response: "Our mechanics have over 15 years of experience and handle complex electrical and mechanical repairs that other shops often miss, using advanced diagnostics technology."
        },
        {
            keywords: ['price', 'cost', 'estimate', 'transparent', 'hidden', 'fee', 'pricing', 'honest'],
            response: "We offer transparent pricing with no hidden fees. We provide digital estimates so you see exactly what your car needs before we start, ensuring upfront honest pricing."
        },
        {
            keywords: ['service', 'services', 'servies', 'repair', 'repairs', 'brake', 'engine', 'ac', 'fleet', 'towing', 'roadside', 'mobile'],
            response: "We offer expert auto repair, mobile and roadside services, fleet maintenance, and quality used cars. Our specific services include Brake Repair, Engine Diagnostics, AC Repair, and Fleet Services."
        },
        {
            keywords: ['location', 'address', 'where', 'dallas', 'richardson', 'plano', 'addison', 'place', 'city', 'area'],
            response: "We are located at 13610 Floyd Circle, Dallas, Texas 75243. We serve North Dallas, Richardson, Plano, and Addison."
        },
        {
            keywords: ['contact', 'contact number', 'phone', 'call', 'number', 'mobile', 'cell', 'email', 'mail'],
            response: "You can reach us at +1 (214) 597-4922 or email info@carnationelite.com."
        },
        {
            keywords: ['website', 'url', 'link', 'site', 'websit', 'online'],
            response: "Visit our official website at https://www.carnationelite.com for more details and to browse our inventory."
        },
        {
            keywords: ['car', 'buy', 'sale', 'inventory', 'used', 'trade', 'next car', 'vehicles', 'trucks', 'suvs', 'sedans'],
            response: "Looking for your next car? We have a featured inventory of reliable used cars with competitive pricing. We also offer options to sell or trade your vehicle."
        },
        {
            keywords: ['social', 'social media links', 'social media', 'socila', 'media', 'links', 'facebook', 'instagram', 'instasgram', 'linkedin', 'twitter', 'tiktok', 'x'],
            response: "Follow us on social media: \n• Facebook: https://www.facebook.com/carnationelite \n• Instagram: https://www.instagram.com/carnation_elite/ \n• LinkedIn: https://www.linkedin.com/company/carnation-elite/ \n• Twitter/X: https://twitter.com/carnationelite \n• TikTok: https://www.tiktok.com/in/about"
        },
        {
            keywords: ['status', 'repaired', 'happy', 'customers', 'satisfied', 'stats', 'statistics'],
            response: "We have repaired 100+ vehicles with 15+ years of experience and maintain 100% happy customers!"
        }
    ];

    const openChat = () => {
        window.classList.add('active');
        overlay.classList.add('active');
        input.focus();
    };

    const closeChat = () => {
        window.classList.remove('active');
        overlay.classList.remove('active');
    };

    toggle.addEventListener('click', () => {
        if (window.classList.contains('active')) {
            closeChat();
        } else {
            openChat();
        }
    });

    close.addEventListener('click', (e) => {
        e.stopPropagation();
        closeChat();
    });

    overlay.addEventListener('click', closeChat);

    const sendMessage = () => {
        const text = input.value.trim();
        if (text === '') return;

        appendMessage('user', text);
        input.value = '';

        const typingDiv = document.createElement('div');
        typingDiv.classList.add('ai-message', 'bot', 'typing');
        typingDiv.textContent = '...';
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        setTimeout(() => {
            if (messagesContainer.contains(typingDiv)) {
                messagesContainer.removeChild(typingDiv);
            }
            const response = getResponse(text);
            appendMessage('bot', response);
        }, 800);
    };

    const getResponse = (userInput) => {
        const input = userInput.toLowerCase().replace(/[^\w\s]/gi, '');
        const words = input.split(/\s+/);

        for (const entry of knowledgeBase) {
            const hasMatch = entry.keywords.some(keyword =>
                input.includes(keyword.toLowerCase()) ||
                words.some(word => word === keyword.toLowerCase())
            );

            if (hasMatch) {
                return "OK! " + entry.response;
            }
        }

        return "OK! I've received your inquiry about \"" + userInput + "\". A specialist from CarNation Elite will provide you with specific details shortly. You can also reach us directly at +1 (214) 597-4922 or visit www.carnationelite.com.";
    };

    const appendMessage = (sender, text) => {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('ai-message', sender);
        msgDiv.innerText = text;
        messagesContainer.appendChild(msgDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    };

    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
