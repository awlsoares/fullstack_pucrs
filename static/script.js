// Controla abrir/fechar submenu individual
document.querySelectorAll('#sidebar .menu-link').forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    const parent = e.target.parentElement;
    parent.classList.toggle('active');
  });
});
//--------------------------------------------------------------------------

// Controla abrir/fechar todo o menu lateral
const toggleBtn = document.getElementById('toggle-menu-btn');
const sidebar = document.getElementById('sidebar');

toggleBtn.addEventListener('click', () => {
  sidebar.classList.toggle('collapsed');
  document.body.classList.toggle('menu-collapsed');
});
//--------------------------------------------------------------------------

// Faz a ordenação das colunas da tabela de contratos

let direcaoOrdem = [];
let ultimaColunaOrdenada = null;

function ordenarTabela(colunaIndex, thElemento) {
  const tabela = document.getElementById("tabelaContratos");
  const linhas = Array.from(tabela.tBodies[0].rows);
  const colunasNumericas = [3, 5, 7, 9, 11]; // ID, Assinatura, Protocolo, Conclusão, Total

  if (ultimaColunaOrdenada !== colunaIndex) {
    direcaoOrdem[colunaIndex] = true;
    ultimaColunaOrdenada = colunaIndex;
  } else {
    direcaoOrdem[colunaIndex] = !direcaoOrdem[colunaIndex];
  }
  const direcao = direcaoOrdem[colunaIndex] ? 1 : -1;

  function cellText(cell) {
    const span = cell.querySelector('span:last-child');
    return (span ? span.innerText : cell.innerText).trim();
  }

  function parseContrato(text) {
    if (!text) return { num: NaN, ano: NaN };
    text = text.replace(/\u00A0/g, ' ').trim(); // remove NBSP
    const m = text.match(/(\d+)\s*\/\s*(\d{1,4})/); // captura "numero/ano"
    if (!m) return { num: NaN, ano: NaN };
    return { num: parseInt(m[1], 10), ano: parseInt(m[2], 10) };
  }

  function parseDateDMY(text) {
    const parts = (text || "").split("/");
    if (parts.length !== 3) return NaN;
    const [d, m, y] = parts.map(Number);
    if (!d || !m || !y) return NaN;
    return new Date(y, m - 1, d).getTime();
  }

  linhas.sort((a, b) => {
    const aTexto = cellText(a.cells[colunaIndex]);
    const bTexto = cellText(b.cells[colunaIndex]);

    // Colunas de data (dd/mm/yyyy)
    if ([2, 6, 8, 10].includes(colunaIndex)) {
      const aTime = parseDateDMY(aTexto) || 0;
      const bTime = parseDateDMY(bTexto) || 0;
      return ((aTime - bTime) === 0 ? 0 : (aTime - bTime > 0 ? 1 : -1)) * direcao;
    }

    // Colunas no formato "numero/ano" (Proposta e Contrato)
    if ([12, 13].includes(colunaIndex)) {
      const A = parseContrato(aTexto);
      const B = parseContrato(bTexto);

      // Se não conseguiu parsear, volta para comparação de string
      if (isNaN(A.ano) || isNaN(B.ano) || isNaN(A.num) || isNaN(B.num)) {
        return aTexto.localeCompare(bTexto) * direcao;
      }

      if (A.ano !== B.ano) return (A.ano - B.ano) * direcao;
      return (A.num - B.num) * direcao;
    }

    // Colunas numéricas (R$)
    if (colunasNumericas.includes(colunaIndex)) {
      const aNum = parseFloat(aTexto.replace(/[^\d\-,.]/g, '').replace(',', '.')) || 0;
      const bNum = parseFloat(bTexto.replace(/[^\d\-,.]/g, '').replace(',', '.')) || 0;
      return ((aNum - bNum) === 0 ? 0 : (aNum - bNum > 0 ? 1 : -1)) * direcao;
    }

    // Fallback: comparação de strings (com locale)
    return aTexto.localeCompare(bTexto) * direcao;
  });

  linhas.forEach(linha => tabela.tBodies[0].appendChild(linha));

  document.querySelectorAll("th span").forEach(span => (span.textContent = ""));
  thElemento.querySelector("span").textContent = direcaoOrdem[colunaIndex] ? " ▲" : " ▼";
}

//--------------------------------------------------------------------------
// Faz a ordenação das colunas da tabela de contratos

let direcaoOrdem3 = [];
let ultimaColunaOrdenada3 = null; 
function ordenarTabelaNf(colunaIndex, thElemento) {
    const tabela = document.getElementById("tabelaNfs");
    const linhas = Array.from(tabela.tBodies[0].rows);

    const colunasNumericas = [1, 5, 6]; // Nº NF, Bruto, Liquido

    if (ultimaColunaOrdenada3 !== colunaIndex) {
        direcaoOrdem3[colunaIndex] = true;
        ultimaColunaOrdenada3 = colunaIndex;
    } else {
        direcaoOrdem3[colunaIndex] = !direcaoOrdem3[colunaIndex];
    }

    const direcao = direcaoOrdem3[colunaIndex] ? 1 : -1;

    linhas.sort((a, b) => {
        let aTexto, bTexto;

        // Verifica se há subelementos (ex.: <span>) na célula
        if (a.cells[colunaIndex].querySelector('span:last-child')) {
            aTexto = a.cells[colunaIndex].querySelector('span:last-child').innerText.trim();
            bTexto = b.cells[colunaIndex].querySelector('span:last-child').innerText.trim();
        } else {
            aTexto = a.cells[colunaIndex].innerText.trim();
            bTexto = b.cells[colunaIndex].innerText.trim();
        }

        if (colunaIndex === 2 || colunaIndex === 10 || colunaIndex === 11) {
          // Converte "dd/mm/yyyy" para Date
          const [ad, am, ay] = aTexto.split("/").map(Number);
          const [bd, bm, by] = bTexto.split("/").map(Number);
          const aData = new Date(ay, am - 1, ad);
          const bData = new Date(by, bm - 1, bd);
          return aData - bData > 0 ? direcao : aData - bData < 0 ? -direcao : 0;
        }

        // Lógica específica para a coluna "Número do Contrato" (tipo string no formato "número/ano")
        if (colunaIndex === 12) {
          // Divide o texto em número e ano, convertendo cada parte para número
          const [aNumero, aAno] = aTexto.split("/").map(Number);
          const [bNumero, bAno] = bTexto.split("/").map(Number);

          // Ordenação por ano primeiro
          if (aAno !== bAno) {
              return (aAno - bAno) * direcao; // Compara os anos
          }

          // Caso os anos sejam iguais, ordena pelo número
          return (aNumero - bNumero) * direcao; // Compara os números
        }
        
        // Lógica para ordenação de colunas numéricas
        if (colunasNumericas.includes(colunaIndex)) {
            aTexto = parseFloat(aTexto.replace("R$", "").replace(",", ".")) || 0;
            bTexto = parseFloat(bTexto.replace("R$", "").replace(",", ".")) || 0;
        }

        // Lógica para ordenação alfabética
        return aTexto < bTexto ? -1 * direcao : aTexto > bTexto ? 1 * direcao : 0;
    });

    linhas.forEach(linha => tabela.tBodies[0].appendChild(linha));

    document.querySelectorAll("th span").forEach(span => (span.textContent = ""));
    thElemento.querySelector("span").textContent = direcaoOrdem3[colunaIndex] ? " ▲" : " ▼";
}

// -------------------------------------------------------------------------------------
// Filtra a tabela projetos pela texto digitado em "descrição"
function filtrarContratos() {
    const filtro = document.getElementById("filtroDescricao").value.toLowerCase();
    const linhas = document.querySelectorAll("#tabelaContratos tbody tr");

    linhas.forEach(linha => {
        const descricao = linha.querySelector(".escopo").textContent.toLowerCase();
        linha.style.display = descricao.includes(filtro) ? "" : "none";
    });
}
//--------------------------------------------------------------------------

// /* Confirma o recebimento ou não recebimento do valor da célula clicada na tabela, alterando o status de Assiantura/Protocolo/Aprovação
//    para 0/1 e atualiza a data associada a data_assinatura/data_protoclo/data_aprovacao */

function confirmarFaturamento(contratoId, tipo) {
    const coluna = event.currentTarget;
    const statusAtual = coluna.classList.contains('status-true'); // verifica se está true (verde)
    console.log("Status Atual:", statusAtual);

    const tipoFormatado = {
        assinatura: 'Assinatura',
        protocolo: 'Protocolo',
        conclusao: 'Conclusão'
    }[tipo] || tipo;

    const statusAtualTexto = statusAtual ? 'Faturado' : 'Não Faturado';
    const novoStatus = statusAtual ? 'Não Faturado' : 'Faturado';
    console.log("Status Atual Texto:", statusAtualTexto);
    console.log("Novo Status:", novoStatus);

    if (!statusAtual) {
        // Se o status for "Não Faturado", solicita ao usuário uma data
        abrirModalData((dataDoFaturamento) => {
            console.log("Data selecionada no modal:", dataDoFaturamento); // Para depuração
            abrirModalConfirmacao(contratoId, tipoFormatado, statusAtualTexto, novoStatus, dataDoFaturamento, (confirmacao) => {
                if (confirmacao) {
                    enviarAtualizacao(contratoId, tipo, dataDoFaturamento, statusAtualTexto);
                }
            });
        });
    } 
    
    else {
        // Usa a data atual se o status for "Faturado"
        const dataDoFaturamento = new Date().toISOString().split('T')[0]; // Formato YYYY-MM-DD
        abrirModalConfirmacao(contratoId, tipoFormatado, statusAtualTexto, novoStatus, dataDoFaturamento, (confirmacao) => {
            if (confirmacao) {
                enviarAtualizacao(contratoId, tipo, dataDoFaturamento, statusAtualTexto);
            }
        });
    }
}

function abrirModalData(callback) {
    const modal = document.createElement('div');
    modal.id = 'modalDataFaturamento';
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
    modal.style.display = 'flex';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';
    modal.style.zIndex = '1000';

    const container = document.createElement('div');
    container.style.backgroundColor = '#fff';
    container.style.padding = '20px';
    container.style.borderRadius = '8px';
    container.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
    container.style.textAlign = 'center';
    container.style.maxWidth = '400px';
    container.style.width = '100%';

    const label = document.createElement('label');
    label.textContent = 'Selecione a Data do Evento:';
    label.style.display = 'block';
    label.style.marginBottom = '10px';
    label.style.fontSize = '16px';
    label.style.fontWeight = 'bold';

    const inputDate = document.createElement('input');
    inputDate.type = 'date';
    inputDate.style.padding = '10px';
    inputDate.style.border = '1px solid #ccc';
    inputDate.style.borderRadius = '5px';
    inputDate.style.fontSize = '14px';
    inputDate.style.width = '100%';
    inputDate.focus();

    const btnCancelar = document.createElement('button');
    btnCancelar.textContent = 'Cancelar';
    btnCancelar.style.marginTop = '10px';
    btnCancelar.style.marginRight = '10px';
    btnCancelar.style.padding = '10px 15px';
    btnCancelar.style.backgroundColor = '#f44336';
    btnCancelar.style.color = '#fff';
    btnCancelar.style.border = 'none';
    btnCancelar.style.borderRadius = '5px';
    btnCancelar.style.cursor = 'pointer';
    btnCancelar.addEventListener('click', () => {
        document.body.removeChild(modal); // Fecha o modal
    });

    const btnConfirmar = document.createElement('button');
    btnConfirmar.textContent = 'Confirmar';
    btnConfirmar.style.marginTop = '10px';
    btnConfirmar.style.padding = '10px 15px';
    btnConfirmar.style.backgroundColor = '#4CAF50';
    btnConfirmar.style.color = '#fff';
    btnConfirmar.style.border = 'none';
    btnConfirmar.style.borderRadius = '5px';
    btnConfirmar.style.cursor = 'pointer';
    btnConfirmar.addEventListener('click', () => {
        const dataDoFaturamento = inputDate.value; // Captura a data selecionada
        if (!dataDoFaturamento) {
            alert('Por favor, selecione uma data válida.');
            return;
        }
        document.body.removeChild(modal); // Fecha o modal
        callback(dataDoFaturamento); // Passa a data para o callback
    });

    container.appendChild(label);
    container.appendChild(inputDate);
    container.appendChild(btnCancelar);
    container.appendChild(btnConfirmar); // Adiciona o botão Confirmar ao container

    modal.appendChild(container);
    document.body.appendChild(modal);
}

function abrirModalConfirmacao(contratoId, tipo, statusAtualTexto, novoStatus, dataDoFaturamento, callback) {
    console.log("Entrou em abriModalConfirmacao");
    const modal = document.createElement('div');
    modal.id = 'modalConfirmacao';
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
    modal.style.display = 'flex';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';
    modal.style.zIndex = '1000';

    const container = document.createElement('div');
    container.style.backgroundColor = '#fff';
    container.style.padding = '20px';
    container.style.borderRadius = '8px';
    container.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
    container.style.textAlign = 'center';
    container.style.maxWidth = '400px';
    container.style.width = '100%';

    const titulo = document.createElement('h3');
    titulo.textContent = "Confirmação de Alteração";
    titulo.style.marginBottom = '15px';

    const texto = document.createElement('p');

    if (statusAtualTexto==="Não Faturado") {
      // Converte a data do formato yyyy-mm-dd para dd/mm/yyyy
      const [ano, mes, dia] = dataDoFaturamento.split('-');
      const dataFormatada = `${dia}/${mes}/${ano}`;
      texto.textContent = `O status atual de "${tipo}" para o Contrato ID ${contratoId} está como "${statusAtualTexto}".\nDeseja alterar para "${novoStatus}" com a data do evento em "${dataFormatada}"?`;
    } 
    else {
      texto.textContent = `O status atual de "${tipo}" para o Contrato ID ${contratoId} está como "${statusAtualTexto}".\nDeseja alterar para "${novoStatus}" e excluir a Nota Fiscal associada?`;
    }   

    const btnConfirmar = document.createElement('button');
    btnConfirmar.textContent = 'Confirmar';
    btnConfirmar.style.marginTop = '10px';
    btnConfirmar.style.padding = '10px 15px';
    btnConfirmar.style.backgroundColor = '#4CAF50';
    btnConfirmar.style.color = '#fff';
    btnConfirmar.style.border = 'none';
    btnConfirmar.style.borderRadius = '5px';
    btnConfirmar.style.cursor = 'pointer';
    btnConfirmar.addEventListener('click', () => {
        document.body.removeChild(modal); // Fecha o modal
        callback(true);
    });

    const btnCancelar = document.createElement('button');
    btnCancelar.textContent = 'Cancelar';
    btnCancelar.style.marginTop = '10px';
    btnCancelar.style.marginLeft = '10px';
    btnCancelar.style.padding = '10px 15px';
    btnCancelar.style.backgroundColor = '#f44336';
    btnCancelar.style.color = '#fff';
    btnCancelar.style.border = 'none';
    btnCancelar.style.borderRadius = '5px';
    btnCancelar.style.cursor = 'pointer';
    btnCancelar.addEventListener('click', () => {
        document.body.removeChild(modal); // Fecha o modal
        callback(false);
    });

    container.appendChild(titulo);
    container.appendChild(texto);
    container.appendChild(btnConfirmar);
    container.appendChild(btnCancelar);
    modal.appendChild(container);
    document.body.appendChild(modal);
}

function enviarAtualizacao(contratoId, tipo, dataDoFaturamento, statusAtualTexto) {
    console.log("Entrou em enviarAtualizacao"); 
    console.log(`Tipo: "${tipo}" - Contrato ID ${contratoId} - Data ${dataDoFaturamento}`);

    fetch('/contratos/faturamento/atualizar_status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ contrato_id: contratoId, tipo: tipo, data_faturamento: dataDoFaturamento, statusAtualTexto: statusAtualTexto })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.redirect) {
                // Redireciona para a página especificada pelo backend
                window.location.href = data.redirect;
            } else {
                // Atualiza a página somente se não houver redirecionamento
                location.reload();
            }
        } else {
            alert('Erro ao atualizar: ' + (data.message || 'Desconhecido.'));
        }
    })
    .catch(error => {
        alert('Erro de comunicação: ' + error);
    });
}


//--------------------------------------------------------------------------

// Controles do modal de seleção de Status do Projeto
// Variáveis globais para controlar o modal
let projetoIdSelecionado = null; // ID do projeto sendo alterado
let modal = document.getElementById("statusModal");

function abrirModal(contratoId) {
  contratoIdSelecionado = contratoId; // Armazena o ID do projeto na variável global
  modal.style.display = "block"; // Exibe o modal
}

function fecharModal() {
  modal.style.display = "none"; // Esconde o modal
  contratoIdSelecionado = null; // Reseta o ID do projeto selecionado
}

function confirmarStatusContrato() {
  const form = document.getElementById("statusForm");
  const statusSelecionado = form.status.value; // Obtém o valor do status selecionado
  console.log(`O status selecionado foi ${statusSelecionado}`)

  if (!statusSelecionado) {
    alert("Por favor, selecione um status.");
    return;
  }

  // Aqui você pode fazer algo com o status selecionado, como enviar para o servidor
  alert(`Contrato ID: ${contratoIdSelecionado}, Novo Status: ${statusSelecionado}`);
  
  // Fetch para atualizar o status do projeto com o novo status selecionado.
  fetch('/contratos/atualizar_status_contrato', { 
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ contrato_id: contratoIdSelecionado, status_contrato: statusSelecionado })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      location.reload(); // atualiza a página para refletir a mudança
    } else {
      alert('Erro ao atualizar: ' + (data.message || 'Desconhecido.'));
    }
  })
  .catch(error => {
    alert('Erro de comunicação: ' + error);
  });

  // Fecha o modal após a confirmação
  fecharModal();
}

// Seleciona todas as células da coluna "Status"
document.querySelectorAll('td[data-label="Status"]').forEach(cell => {
  cell.style.cursor = 'pointer'; // Muda o cursor para a mão com dedo indicador
});
//--------------------------------------------------------------------------

// Função para abrir o formulário de edição de cliente
function abrirFormularioEdicaoCliente(clienteId) {
  // Redireciona para a página de edição do cliente com o ID informado
  window.location.href = `/clientes/${clienteId}/editar`;
}

//--------------------------------------------------------------------------

// Função para abrir o formulário de edição de projeto
function abrirFormularioEdicaoContrato(contratoId) {
  // Redireciona para a página de edição do projeto com o ID informado
  window.location.href = `/contratos/${contratoId}/editar`;
} 

// Função para abrir o formulário de criação de contrato vindo de uma proposta
function duplicarContrato(propostaID) {
  // Redireciona para a página de criação do contrato baseado na proposta do ID informado
  window.location.href = `/duplicar_contrato/${propostaID}`;
} 

//--------------------------------------------------------------------------

// Função para abrir o formulário de criação de contrato vindo de uma proposta
function criarContrato(propostaID) {
  // Redireciona para a página de criação do contrato baseado na proposta do ID informado
  window.location.href = `/novo_contrato/proposta_aprovada/${propostaID}`;
} 

//--------------------------------------------------------------------------
// Função para filtrar faturamentos por ano e mes
function filtrarFaturamentosAnoMes(ano, mes) {
  window.location.href = `/faturamentos/${ano}/${mes}/diario`; 
}

//--------------------------------------------------------------------------
// Função para mostrar faturamentos por ano e mes na página
document.addEventListener("DOMContentLoaded", function () {
    // Seleciona o contêiner onde o conteúdo será carregado
    const listagemDiv = document.getElementById("listagem");

    // Carrega o conteúdo do arquivo faturamento_tipo.html
    fetch("faturamento/faturamento_tipo.html")
        .then(response => {
            if (!response.ok) {
                throw new Error("Erro ao carregar o conteúdo.");
            }
            return response.text(); // Converte a resposta para texto
        })
        .then(html => {
            // Adiciona o conteúdo carregado ao contêiner
            listagemDiv.innerHTML += html;
        })
        .catch(error => {
            console.error("Erro ao carregar o conteúdo:", error);
        });
});

//--------------------------------------------------------------------------
// Função para filtrar recebimentos por ano e mes
function filtrarRecebimentosAnoMes(ano, mes) {
  window.location.href = `/recebimentos/${ano}/${mes}/diario`; 
}



//--------------------------------------------------------------------------
// Função para mostrar recebimentos por ano e mes na página
document.addEventListener("DOMContentLoaded", function () {
    // Seleciona o contêiner onde o conteúdo será carregado
    const listagemDiv = document.getElementById("listagem");

    // Carrega o conteúdo do arquivo faturamento_tipo.html
    fetch("recebimento/recebimento_tipo.html")
        .then(response => {
            if (!response.ok) {
                throw new Error("Erro ao carregar o conteúdo.");
            }
            return response.text(); // Converte a resposta para texto
        })
        .then(html => {
            // Adiciona o conteúdo carregado ao contêiner
            listagemDiv.innerHTML += html;
        })
        .catch(error => {
            console.error("Erro ao carregar o conteúdo:", error);
        });
});

// ------------------------- PROPOSTA -----------------------------------------
// Controles do modal de seleção de Status da Proposta
// Variáveis globais para controlar o modal
let propostaIdSelecionado = null; // ID da proposta sendo alterado
let modalProposta = document.getElementById("statusModal");

function abrirModalProposta(propostaId) {
  propostaIdSelecionado = propostaId; // Armazena o ID do projeto na variável global
  modal.style.display = "block"; // Exibe o modal
}

function fecharModalProposta() {
  modal.style.display = "none"; // Esconde o modal
  propostaIdSelecionado = null; // Reseta o ID do projeto selecionado
}

function confirmarStatusProposta() {
  const form = document.getElementById("statusForm");
  const statusSelecionado = form.status.value; // Obtém o valor do status selecionado
  
  if (!statusSelecionado) {
    alert("Por favor, selecione um status.");
    return;
  }

  // Se o status for "Cancelado", pede confirmação antes
  if (statusSelecionado === "Cancelado") {
    const confirma = confirm(
      "⚠️ Atenção!\n\nO Cancelamento da Proposta no sistema não pode ser desfeito.\n" +
      "Deseja realmente CANCELAR a Proposta?"
    );
    
    if (!confirma) {
      // Usuário cancelou a operação, volta para a lista de propostas
      window.location.href = "/propostas"; 
      return;
    }
  }

  // Aqui você pode fazer algo com o status selecionado, como enviar para o servidor
  //alert(`Proposta Nº: ${numero_proposta}, Novo Status: ${statusSelecionado}`);
  
  // Fetch para atualizar o status da proposta com o novo status selecionado.
  fetch('/propostas/atualizar_status_proposta', { 
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ proposta_id: propostaIdSelecionado, status_proposta: statusSelecionado })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      location.reload(); // atualiza a página para refletir a mudança
    } else {
      alert('Erro ao atualizar: ' + (data.message || 'Desconhecido.'));
    }
  })
  .catch(error => {
    alert('Erro de comunicação: ' + error);
  });

  // Fecha o modal após a confirmação
  fecharModalProposta();
}

//--------------------------------------------------------------------------

// Função para abrir o formulário de edição de proposta
function abrirFormularioEdicaoProposta(propostaId) {
  // Redireciona para a página de edição do proposta com o ID informado
  window.location.href = `/propostas/${propostaId}/editar`;
} 

// ------------------------------------------------------------------------------
//--------------------------------------------------------------------------

// Faz a ordenação das colunas da tabela de Faturamentos
let direcaoOrdem1 = [];
let ultimaColunaOrdenada1 = null; 
function ordenarTabelaFaturamento(colunaIndex, thElemento) {
    const tabela = document.getElementById("tabelaFaturamentos");
    const linhas = Array.from(tabela.tBodies[0].rows);

    const colunasNumericas = [4]; // Valor em R$

    if (ultimaColunaOrdenada1 !== colunaIndex) {
        direcaoOrdem1[colunaIndex] = true;
        ultimaColunaOrdenada1 = colunaIndex;
    } else {
        direcaoOrdem1[colunaIndex] = !direcaoOrdem1[colunaIndex];
    }

    const direcao = direcaoOrdem1[colunaIndex] ? 1 : -1;

    linhas.sort((a, b) => {
        let aTexto, bTexto;

        // Verifica se há subelementos (ex.: <span>) na célula
        if (a.cells[colunaIndex].querySelector('span:last-child')) {
            aTexto = a.cells[colunaIndex].querySelector('span:last-child').innerText.trim();
            bTexto = b.cells[colunaIndex].querySelector('span:last-child').innerText.trim();
        } else {
            aTexto = a.cells[colunaIndex].innerText.trim();
            bTexto = b.cells[colunaIndex].innerText.trim();
        }

        if (colunaIndex === 3) {
          // Converte "dd/mm/yyyy" para Date
          const [ad, am, ay] = aTexto.split("/").map(Number);
          const [bd, bm, by] = bTexto.split("/").map(Number);
          const aData = new Date(ay, am - 1, ad);
          const bData = new Date(by, bm - 1, bd);
          return aData - bData > 0 ? direcao : aData - bData < 0 ? -direcao : 0;
        }

        // Lógica específica para a coluna "Número do Contrato" (tipo string no formato "número/ano")
        if (colunaIndex === 1) {
          // Divide o texto em número e ano, convertendo cada parte para número
          const [aNumero, aAno] = aTexto.split("/").map(Number);
          const [bNumero, bAno] = bTexto.split("/").map(Number);

          // Ordenação por ano primeiro
          if (aAno !== bAno) {
              return (aAno - bAno) * direcao; // Compara os anos
          }

          // Caso os anos sejam iguais, ordena pelo número
          return (aNumero - bNumero) * direcao; // Compara os números
        }
        
        // Lógica para ordenação de colunas numéricas
        if (colunasNumericas.includes(colunaIndex)) {
            aTexto = parseFloat(aTexto.replace("R$", "").replace(",", ".")) || 0;
            bTexto = parseFloat(bTexto.replace("R$", "").replace(",", ".")) || 0;
        }

        // Lógica para ordenação alfabética
        return aTexto < bTexto ? -1 * direcao : aTexto > bTexto ? 1 * direcao : 0;
    });

    linhas.forEach(linha => tabela.tBodies[0].appendChild(linha));

    document.querySelectorAll("th span").forEach(span => (span.textContent = ""));
    thElemento.querySelector("span").textContent = direcaoOrdem1[colunaIndex] ? " ▲" : " ▼";
}

//--------------------------------------------------------------------------

// Faz a ordenação das colunas da tabela de Faturamentos
let direcaoOrdemRec = [];
let ultimaColunaOrdenadaRec = null; 
function ordenarTabelaRecebimento(colunaIndex, thElemento) {
    const tabela = document.getElementById("tabelaRecebimentos");
    const linhas = Array.from(tabela.tBodies[0].rows);

    const colunasNumericas = [5, 6]; // Valor em R$

    if (ultimaColunaOrdenadaRec !== colunaIndex) {
        direcaoOrdemRec[colunaIndex] = true;
        ultimaColunaOrdenadaRec = colunaIndex;
    } else {
        direcaoOrdemRec[colunaIndex] = !direcaoOrdemRec[colunaIndex];
    }

    const direcao = direcaoOrdemRec[colunaIndex] ? 1 : -1;

    linhas.sort((a, b) => {
        let aTexto, bTexto;

        // Verifica se há subelementos (ex.: <span>) na célula
        if (a.cells[colunaIndex].querySelector('span:last-child')) {
            aTexto = a.cells[colunaIndex].querySelector('span:last-child').innerText.trim();
            bTexto = b.cells[colunaIndex].querySelector('span:last-child').innerText.trim();
        } else {
            aTexto = a.cells[colunaIndex].innerText.trim();
            bTexto = b.cells[colunaIndex].innerText.trim();
        }

        if (colunaIndex === 4) {
          // Converte "dd/mm/yyyy" para Date
          const [ad, am, ay] = aTexto.split("/").map(Number);
          const [bd, bm, by] = bTexto.split("/").map(Number);
          const aData = new Date(ay, am - 1, ad);
          const bData = new Date(by, bm - 1, bd);
          return aData - bData > 0 ? direcao : aData - bData < 0 ? -direcao : 0;
        }

        // // Lógica específica para a coluna "Número do Contrato" (tipo string no formato "número/ano")
        // if (colunaIndex === 1) {
        //   // Divide o texto em número e ano, convertendo cada parte para número
        //   const [aNumero, aAno] = aTexto.split("/").map(Number);
        //   const [bNumero, bAno] = bTexto.split("/").map(Number);

        //   // Ordenação por ano primeiro
        //   if (aAno !== bAno) {
        //       return (aAno - bAno) * direcao; // Compara os anos
        //   }

        //   // Caso os anos sejam iguais, ordena pelo número
        //   return (aNumero - bNumero) * direcao; // Compara os números
        // }
        
        // Lógica para ordenação de colunas numéricas
        if (colunasNumericas.includes(colunaIndex)) {
            aTexto = parseFloat(aTexto.replace("R$", "").replace(",", ".")) || 0;
            bTexto = parseFloat(bTexto.replace("R$", "").replace(",", ".")) || 0;
        }

        // Lógica para ordenação alfabética
        return aTexto < bTexto ? -1 * direcao : aTexto > bTexto ? 1 * direcao : 0;
    });

    linhas.forEach(linha => tabela.tBodies[0].appendChild(linha));

    document.querySelectorAll("th span").forEach(span => (span.textContent = ""));
    thElemento.querySelector("span").textContent = direcaoOrdemRec[colunaIndex] ? " ▲" : " ▼";
}

//--------------------------------------------------------------------------
// Faz a ordenação das colunas da tabela de Propostas
let direcaoOrdem2 = [];
let ultimaColunaOrdenada2 = null; 

function parseNumeroAno(text) {
    if (!text) return { num: NaN, ano: NaN };
    text = text.replace(/\u00A0/g, ' ').trim();

    if (text === "" || text === "---") return { num: NaN, ano: NaN };

    const partes = text.split("/");
    if (partes.length !== 2) return { num: NaN, ano: NaN };

    return {
        num: parseInt(partes[0], 10),
        ano: parseInt(partes[1], 10)
    };
}

function ordenarTabelaProposta(colunaIndex, thElemento) {
    const tabela = document.getElementById("tabelaPropostas");
    const linhas = Array.from(tabela.tBodies[0].rows);

    const colunasNumericas = [4, 5, 6, 7]; // Valor em R$

    if (ultimaColunaOrdenada2 !== colunaIndex) {
        direcaoOrdem2[colunaIndex] = true;
        ultimaColunaOrdenada2 = colunaIndex;
    } else {
        direcaoOrdem2[colunaIndex] = !direcaoOrdem2[colunaIndex];
    }

    const direcao = direcaoOrdem2[colunaIndex] ? 1 : -1;

    linhas.sort((a, b) => {
        let aTexto, bTexto;

        // Se a célula tiver <span>, pega o último
        if (a.cells[colunaIndex].querySelector('span:last-child')) {
            aTexto = a.cells[colunaIndex].querySelector('span:last-child').innerText.trim();
            bTexto = b.cells[colunaIndex].querySelector('span:last-child').innerText.trim();
        } else {
            aTexto = a.cells[colunaIndex].innerText.trim();
            bTexto = b.cells[colunaIndex].innerText.trim();
        }

        // Ordenação de DATA (coluna "Envio")
        if (colunaIndex === 1) {
            const [ad, am, ay] = aTexto.split("/").map(Number);
            const [bd, bm, by] = bTexto.split("/").map(Number);
            const aData = new Date(ay, am - 1, ad);
            const bData = new Date(by, bm - 1, bd);
            return aData > bData ? direcao : aData < bData ? -direcao : 0;
        }

        // Ordenação de PROPOSTA (formato número/ano)
        if (colunaIndex === 9) {
            const A = parseNumeroAno(aTexto);
            const B = parseNumeroAno(bTexto);

            if (isNaN(A.ano) || isNaN(A.num)) return 1 * direcao;
            if (isNaN(B.ano) || isNaN(B.num)) return -1 * direcao;

            if (A.ano !== B.ano) return (A.ano - B.ano) * direcao;
            return (A.num - B.num) * direcao;
        }

        // Ordenação de CONTRATO (formato número/ano ou "---")
        if (colunaIndex === 10) {
            const A = parseNumeroAno(aTexto);
            const B = parseNumeroAno(bTexto);

            // "---" sempre vai para o fim
            if (isNaN(A.ano) || isNaN(A.num)) return 1 * direcao;
            if (isNaN(B.ano) || isNaN(B.num)) return -1 * direcao;

            if (A.ano !== B.ano) return (A.ano - B.ano) * direcao;
            return (A.num - B.num) * direcao;
        }

        // Ordenação de VALORES numéricos
        if (colunasNumericas.includes(colunaIndex)) {
            aTexto = parseFloat(aTexto.replace("R$", "").replace(",", ".")) || 0;
            bTexto = parseFloat(bTexto.replace("R$", "").replace(",", ".")) || 0;
            return (aTexto - bTexto) * direcao;
        }

        // Ordenação padrão (alfabética)
        return aTexto < bTexto ? -1 * direcao : aTexto > bTexto ? 1 * direcao : 0;
    });

    // Reanexa as linhas já ordenadas
    linhas.forEach(linha => tabela.tBodies[0].appendChild(linha));

    // Atualiza o indicador visual (seta ▲▼)
    document.querySelectorAll("th span").forEach(span => (span.textContent = ""));
    thElemento.querySelector("span").textContent = direcaoOrdem2[colunaIndex] ? " ▲" : " ▼";
}

// --------------------------------------------------------------------------
//
// Função para abrir o formulário de edição de banco / contas.
function abrirFormularioEdicaoBanco(bancoId) {
  // Redireciona para a página de edição do banco com o ID informado
  window.location.href = `/bancos/${bancoId}/editar`;
}

// --------------------------------------------------------------------------
// Monitora a escolha da opção de boleto na forma de pagamento do cadastro de NF
function toggleBoletoField() {
        // Obtém o valor selecionado no select
        const formaDePagamento = document.getElementById('forma_de_pagamento').value;

        // Obtém a div que contém o campo de boleto
        const boletoField = document.getElementById('boleto-field');

        // Exibe ou oculta o campo de boleto com base na seleção
        if (formaDePagamento === 'Boleto') {
            boletoField.style.display = 'block';
        } else {
            boletoField.style.display = 'none';
        }
    }

    // Chama a função ao carregar a página para ajustar o campo de boleto se necessário
    document.addEventListener('DOMContentLoaded', function () {
        toggleBoletoField();
    });


// --------------------------------------------------------------------------
// Verifica a quantidade de caracteres dos campos observações
function updateCharCount() {
        const input = document.getElementById('observacao');
        const charCount = document.getElementById('char-count');
        charCount.textContent = `${input.value.length}/300 caracteres`;
    }

//--------------------------------------------------------------------------

// Função para abrir o formulário de criação de nota fiscal
function criarNf(contratoId, tipo, data_faturamento) {
  // Redireciona para a página de criação de Nota Fiscal baseada no ID do Contrato e no Tipo informado (Assinatura/Protocolo/Conclusão)
  window.location.href = `/nova_nf/${tipo}/${contratoId}/${data_faturamento}`;
} 

// /* Confirma o recebimento ou não recebimento de uma Nota Fiscal

function confirmarRecebimentoNf(nfId) {
    const coluna = event.currentTarget;
    abrirModalDataNf((dataDoRecebimento) => {
        abrirModalConfirmacaoNf(nfId, dataDoRecebimento, (confirmacao) => {
            if (confirmacao) {
                enviarAtualizacaoNf(nfId, dataDoRecebimento);
            }
        });
    });
  }
    
function abrirModalDataNf(callback) {
    // Cria dinamicamente o modal para selecionar a data
    const modal = document.createElement('div');
    modal.id = 'modalDataRecebimentoNf';
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
    modal.style.display = 'flex';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';
    modal.style.zIndex = '1000';

    const container = document.createElement('div');
    container.style.backgroundColor = '#fff';
    container.style.padding = '20px';
    container.style.borderRadius = '8px';
    container.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
    container.style.textAlign = 'center';
    container.style.maxWidth = '400px';
    container.style.width = '100%';

    const label = document.createElement('label');
    label.textContent = 'Selecione a Data do Evento:';
    label.style.display = 'block';
    label.style.marginBottom = '10px';
    label.style.fontSize = '16px';
    label.style.fontWeight = 'bold';

    const inputDate = document.createElement('input');
    inputDate.type = 'date';
    inputDate.style.padding = '10px';
    inputDate.style.border = '1px solid #ccc';
    inputDate.style.borderRadius = '5px';
    inputDate.style.fontSize = '14px';
    inputDate.style.width = '100%';

    inputDate.focus();

    const btnCancelar = document.createElement('button');
    btnCancelar.textContent = 'Cancelar';
    btnCancelar.style.marginTop = '10px';
    btnCancelar.style.marginRight = '10px';
    btnCancelar.style.padding = '10px 15px';
    btnCancelar.style.backgroundColor = '#f44336';
    btnCancelar.style.color = '#fff';
    btnCancelar.style.border = 'none';
    btnCancelar.style.borderRadius = '5px';
    btnCancelar.style.cursor = 'pointer';
    btnCancelar.addEventListener('click', () => {
        document.body.removeChild(modal); // Fecha o modal
    });

    inputDate.addEventListener('change', (e) => {
        const dataDoRecebimento = e.target.value;
        document.body.removeChild(modal); // Fecha o modal
        callback(dataDoRecebimento);
    });

    container.appendChild(label);
    container.appendChild(inputDate);
    container.appendChild(btnCancelar);
    modal.appendChild(container);
    document.body.appendChild(modal);
}

function abrirModalConfirmacaoNf(nfId, dataDoRecebimento, callback) {
    const modal = document.createElement('div');
    modal.id = 'modalConfirmacaoNf';
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
    modal.style.display = 'flex';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';
    modal.style.zIndex = '1000';

    const container = document.createElement('div');
    container.style.backgroundColor = '#fff';
    container.style.padding = '20px';
    container.style.borderRadius = '8px';
    container.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
    container.style.textAlign = 'center';
    container.style.maxWidth = '400px';
    container.style.width = '100%';

    const titulo = document.createElement('h3');
    titulo.textContent = "Confirmação de Alteração";
    titulo.style.marginBottom = '15px';

    const texto = document.createElement('p');

    // Converte a data do formato yyyy-mm-dd para dd/mm/yyyy
    const [ano, mes, dia] = dataDoRecebimento.split('-');
    const dataFormatada = `${dia}/${mes}/${ano}`;
    texto.textContent = `Confirma o recebimento da Nota fiscal em "${dataFormatada}"?`; 

    const btnConfirmar = document.createElement('button');
    btnConfirmar.textContent = 'Confirmar';
    btnConfirmar.style.marginTop = '10px';
    btnConfirmar.style.padding = '10px 15px';
    btnConfirmar.style.backgroundColor = '#4CAF50';
    btnConfirmar.style.color = '#fff';
    btnConfirmar.style.border = 'none';
    btnConfirmar.style.borderRadius = '5px';
    btnConfirmar.style.cursor = 'pointer';
    btnConfirmar.addEventListener('click', () => {
        document.body.removeChild(modal); // Fecha o modal
        callback(true);
    });

    const btnCancelar = document.createElement('button');
    btnCancelar.textContent = 'Cancelar';
    btnCancelar.style.marginTop = '10px';
    btnCancelar.style.marginLeft = '10px';
    btnCancelar.style.padding = '10px 15px';
    btnCancelar.style.backgroundColor = '#f44336';
    btnCancelar.style.color = '#fff';
    btnCancelar.style.border = 'none';
    btnCancelar.style.borderRadius = '5px';
    btnCancelar.style.cursor = 'pointer';
    btnCancelar.addEventListener('click', () => {
        document.body.removeChild(modal); // Fecha o modal
        callback(false);
    });

    container.appendChild(titulo);
    container.appendChild(texto);
    container.appendChild(btnConfirmar);
    container.appendChild(btnCancelar);
    modal.appendChild(container);
    document.body.appendChild(modal);
}

function enviarAtualizacaoNf(nfId, dataDoRecebimento) {
    console.log(`Entrou em Enviar Atualização!!!!!!!!!!!!!!!!!`)
    fetch('/nfs/atualizar_data_pagamento', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ nf_id: nfId, data_usuario: dataDoRecebimento })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload(); // Atualiza a página
            } else {
                alert('Erro ao atualizar: ' + (data.message || 'Desconhecido.'));
            }
        })
        .catch(error => {
            alert('Erro de comunicação: ' + error);
        });
}

function cancelarRecebimentoNf(nfId) {
    // Exibe uma confirmação antes de cancelar o recebimento
    if (confirm("Tem certeza de que deseja cancelar o recebimento desta Nota Fiscal?")) {
        // Faz a requisição POST para a rota cancelar_recebimento
        fetch(`/nfs/${nfId}/cancelar_recebimento`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
        })
        .then(response => {
            if (response.ok) {
                // Atualiza a página para refletir as mudanças
                location.reload();
            } else {
                response.json().then(data => {
                    alert(data.message || "Erro ao cancelar recebimento.");
                });
            }
        })
        .catch(error => {
            alert("Erro de comunicação com o servidor: " + error);
        });
    }
}

//--------------------------------------------------------------------------

// Função para abrir o formulário de edição de Nota Fiscal
function abrirFormularioEdicaoNf(nfId) {
    // Redireciona para a página de edição de NF com o ID informado
    window.location.href = `/nfs/${nfId}/editar`;

} 

// --------------------------------------------------------------------------
//
// Função para abrir o formulário de edição de Tipo de Despesa.
function abrirFormularioEdicaoTipoDespesa(tipoId) {
  // Redireciona para a página de edição do Tipo de Despesa com o ID informado
  window.location.href = `/despesas/${tipoId}/editar_tipo`;
}

// --------------------------------------------------------------------------

// /* Alterar o status de uma Movimentação 

function alterarStatusMovimentacao(movId, operacao) {
    const coluna = event.currentTarget;

    abrirModalSelecaoStatus(operacao, (novoStatus) => {
        if (!novoStatus) return; // cancelado
        abrirModalDataMovimentacao((dataDaMovimentacao) => {
            abrirModalConfirmacaoMovimentacao(movId, dataDaMovimentacao, (confirmacao) => {
                if (confirmacao) {
                    enviarAtualizacaoMovimentacao(movId, dataDaMovimentacao, novoStatus);
                }
            });
        });
    });
}

function abrirModalSelecaoStatus(operacao, callback) {
    const modal = document.createElement('div');
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
    modal.style.display = 'flex';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';
    modal.style.zIndex = '1000';

    const container = document.createElement('div');
    container.style.backgroundColor = '#fff';
    container.style.padding = '20px';
    container.style.borderRadius = '8px';
    container.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
    container.style.textAlign = 'center';
    container.style.maxWidth = '400px';
    container.style.width = '100%';

    const titulo = document.createElement('h3');
    titulo.textContent = 'Selecione o novo status';
    titulo.style.marginBottom = '10px';

    const select = document.createElement('select');
    select.style.padding = '10px';
    select.style.width = '100%';
    select.style.borderRadius = '5px';
    select.style.border = '1px solid #ccc';
    select.style.marginBottom = '15px';

    // Define as opções de acordo com o tipo de operação
    const opcoes = operacao === 'Entrada'
        ? ['Aberto', 'Recebido', 'Cancelado']
        : ['Aberto', 'Pago', 'Cancelado'];

    opcoes.forEach(op => {
        const option = document.createElement('option');
        option.value = op;
        option.textContent = op;
        select.appendChild(option);
    });

    const btnConfirmar = document.createElement('button');
    btnConfirmar.textContent = 'Confirmar';
    btnConfirmar.style.padding = '10px 15px';
    btnConfirmar.style.backgroundColor = '#4CAF50';
    btnConfirmar.style.color = '#fff';
    btnConfirmar.style.border = 'none';
    btnConfirmar.style.borderRadius = '5px';
    btnConfirmar.style.cursor = 'pointer';
    btnConfirmar.addEventListener('click', () => {
        const valorSelecionado = select.value;
        document.body.removeChild(modal);
        callback(valorSelecionado);
    });

    const btnCancelar = document.createElement('button');
    btnCancelar.textContent = 'Cancelar';
    btnCancelar.style.marginLeft = '10px';
    btnCancelar.style.padding = '10px 15px';
    btnCancelar.style.backgroundColor = '#f44336';
    btnCancelar.style.color = '#fff';
    btnCancelar.style.border = 'none';
    btnCancelar.style.borderRadius = '5px';
    btnCancelar.style.cursor = 'pointer';
    btnCancelar.addEventListener('click', () => {
        document.body.removeChild(modal);
        callback(null);
    });

    container.appendChild(titulo);
    container.appendChild(select);
    container.appendChild(btnConfirmar);
    container.appendChild(btnCancelar);
    modal.appendChild(container);
    document.body.appendChild(modal);
}

    
function abrirModalDataMovimentacao(callback) {
    // Cria dinamicamente o modal para selecionar a data
    const modal = document.createElement('div');
    modal.id = 'modalDataRecebimentoNf';
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
    modal.style.display = 'flex';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';
    modal.style.zIndex = '1000';

    const container = document.createElement('div');
    container.style.backgroundColor = '#fff';
    container.style.padding = '20px';
    container.style.borderRadius = '8px';
    container.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
    container.style.textAlign = 'center';
    container.style.maxWidth = '400px';
    container.style.width = '100%';

    const label = document.createElement('label');
    label.textContent = 'Selecione a Data do Evento:';
    label.style.display = 'block';
    label.style.marginBottom = '10px';
    label.style.fontSize = '16px';
    label.style.fontWeight = 'bold';

    const inputDate = document.createElement('input');
    inputDate.type = 'date';
    inputDate.style.padding = '10px';
    inputDate.style.border = '1px solid #ccc';
    inputDate.style.borderRadius = '5px';
    inputDate.style.fontSize = '14px';
    inputDate.style.width = '100%';

    inputDate.focus();

    const btnCancelar = document.createElement('button');
    btnCancelar.textContent = 'Cancelar';
    btnCancelar.style.marginTop = '10px';
    btnCancelar.style.marginRight = '10px';
    btnCancelar.style.padding = '10px 15px';
    btnCancelar.style.backgroundColor = '#f44336';
    btnCancelar.style.color = '#fff';
    btnCancelar.style.border = 'none';
    btnCancelar.style.borderRadius = '5px';
    btnCancelar.style.cursor = 'pointer';
    btnCancelar.addEventListener('click', () => {
        document.body.removeChild(modal); // Fecha o modal
    });

    inputDate.addEventListener('change', (e) => {
        const dataDaMovimentacao = e.target.value;
        document.body.removeChild(modal); // Fecha o modal
        callback(dataDaMovimentacao);
    });

    container.appendChild(label);
    container.appendChild(inputDate);
    container.appendChild(btnCancelar);
    modal.appendChild(container);
    document.body.appendChild(modal);
}

function abrirModalConfirmacaoMovimentacao(movID, dataDaMovimentacao, callback) {
    const modal = document.createElement('div');
    modal.id = 'modalConfirmacaoNf';
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
    modal.style.display = 'flex';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';
    modal.style.zIndex = '1000';

    const container = document.createElement('div');
    container.style.backgroundColor = '#fff';
    container.style.padding = '20px';
    container.style.borderRadius = '8px';
    container.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
    container.style.textAlign = 'center';
    container.style.maxWidth = '400px';
    container.style.width = '100%';

    const titulo = document.createElement('h3');
    titulo.textContent = "Confirmação de Alteração";
    titulo.style.marginBottom = '15px';

    const texto = document.createElement('p');

    // Converte a data do formato yyyy-mm-dd para dd/mm/yyyy
    const [ano, mes, dia] = dataDaMovimentacao.split('-');
    const dataFormatada = `${dia}/${mes}/${ano}`;
    texto.textContent = `Confirma a alteração do Status em "${dataFormatada}"?`; 

    const btnConfirmar = document.createElement('button');
    btnConfirmar.textContent = 'Confirmar';
    btnConfirmar.style.marginTop = '10px';
    btnConfirmar.style.padding = '10px 15px';
    btnConfirmar.style.backgroundColor = '#4CAF50';
    btnConfirmar.style.color = '#fff';
    btnConfirmar.style.border = 'none';
    btnConfirmar.style.borderRadius = '5px';
    btnConfirmar.style.cursor = 'pointer';
    btnConfirmar.addEventListener('click', () => {
        document.body.removeChild(modal); // Fecha o modal
        callback(true);
    });

    const btnCancelar = document.createElement('button');
    btnCancelar.textContent = 'Cancelar';
    btnCancelar.style.marginTop = '10px';
    btnCancelar.style.marginLeft = '10px';
    btnCancelar.style.padding = '10px 15px';
    btnCancelar.style.backgroundColor = '#f44336';
    btnCancelar.style.color = '#fff';
    btnCancelar.style.border = 'none';
    btnCancelar.style.borderRadius = '5px';
    btnCancelar.style.cursor = 'pointer';
    btnCancelar.addEventListener('click', () => {
        document.body.removeChild(modal); // Fecha o modal
        callback(false);
    });

    container.appendChild(titulo);
    container.appendChild(texto);
    container.appendChild(btnConfirmar);
    container.appendChild(btnCancelar);
    modal.appendChild(container);
    document.body.appendChild(modal);
}

function enviarAtualizacaoMovimentacao(movID, dataDaMovimentacao, novoStatus) {
    fetch('/movimentacao/atualizar_status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            mov_id: movID,
            data_usuario: dataDaMovimentacao,
            novo_status: novoStatus
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Erro ao atualizar: ' + (data.message || 'Desconhecido.'));
        }
    })
    .catch(error => {
        alert('Erro de comunicação: ' + error);
    });
}
