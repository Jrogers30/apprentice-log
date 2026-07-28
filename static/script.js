function show(id){ document.getElementById(id).classList.remove('hidden'); }
function hide(id){ document.getElementById(id).classList.add('hidden'); }
function setMsg(id, text, type){
  const el = document.getElementById(id);
  el.textContent = text;
  el.className = 'msg ' + (type || '');
}



async function doRegister() {
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  const res = await fetch('/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email, password })
  });

  const data = await res.json();

  if (res.status === 201) {
    setMsg('auth-msg', 'Account created — now log in', 'success');
  } else {
    setMsg('auth-msg', data.message, 'error');
  }
}

async function doLogin() {
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  const res = await fetch('/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email, password })
  });

  const data = await res.json();

  if (res.ok) {
    hide('auth-screen');
    show('app-screen');
  } else {
    setMsg('auth-msg', data.message, 'error');
  }
}

async function doLogout() {
  await fetch('/logout', {
    method: 'POST'
  });

  hide('app-screen');
  show('auth-screen');

  document.getElementById('email').value = '';
  document.getElementById('password').value = '';
}

async function doUpload() {
  const fileInput = document.getElementById('file-input');
  const file = fileInput.files[0];

  if (!file) {
    setMsg('upload-msg', 'Pick a file first', 'error');
    return;
  }

  const form = new FormData();
  form.append('file', file);

  const res = await fetch('/upload', {
    method: 'POST',
    body: form
  });

  const data = await res.json();

  if (res.ok) {
    setMsg('upload-msg', `Uploaded — ${data.chunk_count} chunks`, 'success');
  } else {
    setMsg('upload-msg', data.message, 'error');
  }
}

async function doAsk() {
  const question = document.getElementById('question').value;
  const answerArea = document.getElementById('answer-area');

  answerArea.innerHTML = '';
  setMsg('ask-msg', 'Thinking...', '');

  const res = await fetch('/ask', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ question })
  });

  const data = await res.json();

  setMsg('ask-msg', '', '');

  if (data.status === 'no_match') {
    answerArea.innerHTML =
      '<div class="answer">No relevant information found in your documents.</div>';
  } else if (data.status === 'success') {
    renderAnswer(data);
  } else {
    setMsg('ask-msg', data.message, 'error');
  }
}


function renderAnswer(data){
  const answerArea = document.getElementById('answer-area');
  let html = `<div class="answer">${data.answer}</div>`;
  if(data.citations && data.citations.length){
    html += '<div class="citations"><strong>Sources:</strong>';
    data.citations.forEach(c => {
      html += `<div class="citation">${c.filename} — chunk ${c.chunk_index}</div>`;
    });
    html += '</div>';
  }
  answerArea.innerHTML = html;
}