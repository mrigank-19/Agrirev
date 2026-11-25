"""A permanent, no-setup page that simulates a WhatsApp conversation against
/webhook — lets anyone try the conversational flow in a plain browser tab
without a real WhatsApp/Twilio connection.
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

_PAGE = """
<html>
<head>
    <title>WhatsApp Chat Tester - AgriExport Advisor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; background: #0b0b0b; margin: 0; padding: 24px; }
        .wrap { max-width: 520px; margin: 0 auto; background: #111; color: #eee; padding: 20px; border-radius: 10px; }
        h2 { margin-top: 0; }
        #chat { background: #000; padding: 10px; border-radius: 8px; height: 420px; overflow-y: auto; margin-bottom: 10px; white-space: pre-wrap; font-size: 14px; }
        #chat b.you { color: #4da6ff; }
        #chat b.bot { color: #25D366; }
        .row { display: flex; gap: 8px; }
        input { flex: 1; padding: 8px; border-radius: 5px; border: none; }
        button { padding: 8px 16px; border-radius: 5px; border: none; background: #25D366; color: white; cursor: pointer; }
        .hint { margin-top: 10px; font-size: 12px; color: #888; }
    </style>
</head>
<body>
    <div class="wrap">
        <h2>AgriExport Advisor &mdash; WhatsApp Chat Tester</h2>
        <div id="chat"></div>
        <div class="row">
            <input id="msg" type="text" placeholder="Type your reply...">
            <button id="send">Send</button>
        </div>
        <div class="hint">Try: "hi", then a district like "Nashik, Maharashtra", then land size like "5", then last crop like "onion".</div>
    </div>
    <script>
        const chat = document.getElementById('chat');
        const phone = 'whatsapp:+91TESTER' + Math.floor(Math.random() * 100000);

        function addLine(who, text) {
            const div = document.createElement('div');
            div.style.margin = '8px 0';
            const cls = who === 'You' ? 'you' : 'bot';
            div.innerHTML = '<b class="' + cls + '">' + who + ':</b> ' + text.replace(/\\n/g, '<br>');
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }

        async function send() {
            const input = document.getElementById('msg');
            const body = input.value;
            if (!body) return;
            addLine('You', body);
            input.value = '';
            const form = new URLSearchParams();
            form.append('From', phone);
            form.append('Body', body);
            const res = await fetch('/webhook', { method: 'POST', body: form });
            const xml = await res.text();
            const match = xml.match(/<Message>([\\s\\S]*?)<\\/Message>/);
            addLine('Bot', match ? match[1] : '(no reply)');
        }

        document.getElementById('send').addEventListener('click', send);
        document.getElementById('msg').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') send();
        });
    </script>
</body>
</html>
"""


@router.get("/chat", response_class=HTMLResponse)
def chat_tester():
    return _PAGE
