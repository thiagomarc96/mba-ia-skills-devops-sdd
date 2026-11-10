'use strict';
let dados = null;
const el = id => document.getElementById(id);
function texto(tag, valor) { const n = document.createElement(tag); n.textContent = String(valor); return n; }
function render() {
  const alvo = el('conteudo'); alvo.replaceChildren(); if (!dados) return;
  const busca = el('busca').value.toLocaleLowerCase('pt-BR');
  const blocos = [
    ['Pods','pods',['nome','fase','pronto','reinicios','motivo']],
    ['Deployments','deployments',['nome','prontos','desejados']],
    ['Services','services',['nome','tipo','endpoints']],
    ['Eventos recentes (até 50)','events',['nome','tipo','motivo','mensagem','quando']]
  ];
  for (const [titulo, chave, colunas] of blocos) {
    const section = document.createElement('section'); section.append(texto('h2',titulo));
    if (dados.erros[chave]) { const p = texto('p',dados.erros[chave]); p.className = 'erro'; section.append(p); }
    else {
      const linhas = dados[chave].filter(row => row.nome.toLocaleLowerCase('pt-BR').includes(busca));
      if (!linhas.length) section.append(texto('p','Nenhum objeto para este filtro.'));
      else { const table = document.createElement('table'); const head = document.createElement('tr');
        colunas.forEach(c => head.append(texto('th',c))); const thead = document.createElement('thead'); thead.append(head); table.append(thead);
        const tbody = document.createElement('tbody');
        linhas.forEach(row => { const tr = document.createElement('tr'); colunas.forEach(c => tr.append(texto('td', typeof row[c] === 'boolean' ? (row[c] ? 'Sim' : 'Não') : row[c]))); tbody.append(tr); });
        table.append(tbody); const scroll = document.createElement('div'); scroll.className='tabela'; scroll.append(table); section.append(scroll); }
    }
    alvo.append(section);
  }
}
async function atualizar(event) {
  if(event) event.preventDefault();
  if(el('atualizar').disabled) return;
  el('atualizar').disabled = true; el('namespace').disabled = true;
  el('status').textContent = 'Consultando recursos…'; dados = null; render();
  try {
    const response = await fetch('/api/estado?namespace=' + encodeURIComponent(el('namespace').value));
    if(!response.ok) throw new Error('Não foi possível obter o estado. Confira o namespace e tente novamente.');
    dados = await response.json();
    el('contexto').textContent = (dados.simulado ? 'EXEMPLO — ' : '') + 'Contexto fixado ao iniciar: ' + (dados.contexto || 'indisponível');
    el('namespaces').replaceChildren(...dados.namespaces.map(n => {const option=document.createElement('option'); option.value=n; return option;}));
    const avisos = Object.entries(dados.erros).map(([k,v]) => k + ': ' + v);
    el('status').textContent = 'Consulta: ' + dados.coletado_em + (avisos.length ? '. ' + avisos.join(' ') : '. Atualize para consultar novamente.'); render();
  } catch(err) { el('status').textContent = err.message; }
  finally { el('atualizar').disabled = false; el('namespace').disabled = false; }
}
el('filtros').addEventListener('submit',atualizar);
el('busca').addEventListener('input',render);
atualizar();
