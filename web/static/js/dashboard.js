document.addEventListener('DOMContentLoaded', function(){
  async function loadMode(){
    const res = await fetch('/api/accounting/mode');
    if(!res.ok) return;
    const j = await res.json();
    const sel = document.getElementById('modeSelect');
    sel.innerHTML = '';
    ['nom_propre','sasu'].forEach(m=>{
      const opt = document.createElement('option'); opt.value = m; opt.text = m; if(m===j.mode) opt.selected=true; sel.appendChild(opt);
    });
  }
  async function loadEntries(){
    const res = await fetch('/api/accounting/entries');
    const j = await res.json();
    const tbody = document.querySelector('#entriesTable tbody'); tbody.innerHTML='';
    (j.entries||[]).forEach(e=>{
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${e.date}</td><td>${e.category}/${e.subcategory}</td><td>${e.type}</td><td>${e.amount}</td><td>${e.currency}</td><td>${e.description||''}</td>`;
      tbody.appendChild(tr);
    });
  }
  document.getElementById('entryForm').addEventListener('submit', async function(ev){
    ev.preventDefault();
    const fd = new FormData(ev.target);
    const obj = Object.fromEntries(fd.entries());
    if(!obj.date) obj.date = new Date().toISOString();
    const res = await fetch('/api/accounting/entries', {method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(obj)});
    if(res.ok){ loadEntries(); ev.target.reset(); }
    else alert('error');
  });
  document.getElementById('switchMode').addEventListener('click', async function(){
    const mode = document.getElementById('modeSelect').value;
    const res = await fetch('/api/accounting/mode',{method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({mode})});
    if(res.ok) loadEntries();
    else alert('error switching mode');
  });
  document.getElementById('exportBtn').addEventListener('click', function(){ window.location='/api/accounting/export'; });
  loadMode(); loadEntries();
});
