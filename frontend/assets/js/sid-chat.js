const sidToggle  = document.getElementById('sidChatToggle');
const sidWindow  = document.getElementById('sidChatWindow');
const sidMsgs    = document.getElementById('sidMsgs');
const sidInput   = document.getElementById('sidInput');
const sidSendBtn = document.getElementById('sidSend');

if (sidToggle) {
  sidToggle.addEventListener('click', () => {
    sidWindow.classList.toggle('open');
    if (sidWindow.classList.contains('open') && sidInput) sidInput.focus();
  });
}

function appendMsg(text, type) {
  const div = document.createElement('div');
  div.className = `msg msg-${type} fade-in`;
  div.textContent = text;
  sidMsgs.appendChild(div);
  sidMsgs.scrollTop = sidMsgs.scrollHeight;
  return div;
}

function showTyping() {
  const div = document.createElement('div');
  div.className = 'msg msg-sid msg-typing';
  div.id = 'sidTyping';
  div.innerHTML = '<span></span><span></span><span></span>';
  sidMsgs.appendChild(div);
  sidMsgs.scrollTop = sidMsgs.scrollHeight;
}

function removeTyping() {
  const t = document.getElementById('sidTyping');
  if (t) t.remove();
}

async function sendToSid() {
  const msg = sidInput ? sidInput.value.trim() : '';
  if (!msg) return;
  sidInput.value = '';
  appendMsg(msg, 'user');
  showTyping();
  const data = await API.askSid(msg);
  removeTyping();
  const reply = data?.reply || "Uhh... my brain froze. Try again! — Sid";
  appendMsg(reply, 'sid');
}

if (sidSendBtn) sidSendBtn.addEventListener('click', sendToSid);
if (sidInput) {
  sidInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendToSid();
  });
}
