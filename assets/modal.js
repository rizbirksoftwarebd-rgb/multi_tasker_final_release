\
document.addEventListener("DOMContentLoaded", () => {
  if (window._copyModalInitialized) return;
  window._copyModalInitialized = true;
  const root = document.createElement('div');
  root.id = 'streamlit-copy-modal-root';
  document.body.appendChild(root);

  function makeModal(id, text, theme="auto") {
    const existing = document.getElementById('streamlit-copy-modal-root-inner');
    if (existing) existing.remove();
    const wrapper = document.createElement('div');
    wrapper.id = 'streamlit-copy-modal-root-inner';
    wrapper.className = 'copy-modal-overlay';
    const card = document.createElement('div');
    card.className = 'copy-modal';
    if (theme === 'dark') card.classList.add('dark');
    const header = document.createElement('div'); header.className = 'header';
    header.innerHTML = `<div><strong>User info</strong><div style="font-size:12px;color:rgba(0,0,0,0.45)">Copy credentials or inspect</div></div>`;
    const actions = document.createElement('div');
    actions.innerHTML = `<button class="theme-toggle" id="theme-toggle">Theme</button> <button class="close-btn" id="close-btn">✕</button>`;
    header.appendChild(actions);
    const codebox = document.createElement('pre');
    codebox.className = 'codebox';
    codebox.id = 'modal-codebox';
    codebox.textContent = text;
    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-btn';
    copyBtn.textContent = 'Copy';
    copyBtn.onclick = () => { navigator.clipboard.writeText(codebox.textContent).then(()=> showToast()); }
    wrapper.appendChild(card);
    card.appendChild(header);
    card.appendChild(codebox);
    card.appendChild(copyBtn);

    document.body.appendChild(wrapper);
    wrapper.style.display = 'flex';
    setTimeout(()=> card.style.transform = 'scale(1)', 20);

    const toggle = document.getElementById('theme-toggle');
    toggle.onclick = () => {
      if (card.classList.contains('dark')) { card.classList.remove('dark'); }
      else { card.classList.add('dark'); }
    }

    document.getElementById('close-btn').onclick = () => { wrapper.remove(); }
    wrapper.onclick = (e) => { if (e.target === wrapper) wrapper.remove(); }
  }

  function showToast(){
    let t = document.getElementById('streamlit-copy-toast');
    if(!t){
      t = document.createElement('div'); t.id = 'streamlit-copy-toast'; t.className = 'toast'; t.textContent = 'Copied to clipboard'; document.body.appendChild(t);
      setTimeout(()=> t.classList.add('show'), 10);
      setTimeout(()=> { t.classList.remove('show'); setTimeout(()=> t.remove(), 220); }, 1500);
    }
  }

  window.openCopyModal = function(text, theme='auto') { makeModal('modal', text, theme); }
});
