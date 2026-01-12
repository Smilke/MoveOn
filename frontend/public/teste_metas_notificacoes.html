<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <title>Teste - Metas e Notificações</title>
</head>
<body>
  <h1>Teste - Metas e Notificações do Paciente</h1>

  <label>
    Paciente ID (CPF):
    <input id="pacienteId" type="text" value="12345678901" />
  </label>
  <button onclick="carregarMetas()">Carregar metas</button>
  <button onclick="carregarNotificacoes()">Carregar notificações</button>

  <h2>Metas ativas / em andamento</h2>
  <div id="listaMetas"></div>

  <h2>Notificações</h2>
  <div id="listaNotificacoes"></div>

  <script>
    const API_BASE = "http://127.0.0.1:8000/api";

    async function carregarMetas() {
      const pacienteId = document.getElementById("pacienteId").value.trim();
      if (!pacienteId) {
        alert("Informe o ID do paciente (CPF).");
        return;
      }

      const resp = await fetch(`${API_BASE}/pacientes/${pacienteId}/metas`);
      const metas = await resp.json();

      const container = document.getElementById("listaMetas");
      container.innerHTML = "";

      if (metas.length === 0) {
        container.innerText = "Nenhuma meta ativa/em andamento.";
        return;
      }

      metas.forEach((meta) => {
        const div = document.createElement("div");
        div.style.border = "1px solid #ccc";
        div.style.margin = "8px 0";
        div.style.padding = "8px";

        div.innerHTML = `
          <strong>ID:</strong> ${meta.id} <br/>
          <strong>Descrição:</strong> ${meta.descricao} <br/>
          <strong>Período:</strong> ${meta.data_inicio} até ${meta.data_fim} <br/>
          <strong>Status:</strong> ${meta.status} <br/>
          <button data-id="${meta.id}" data-status="em_andamento">Marcar em andamento</button>
          <button data-id="${meta.id}" data-status="concluida">Concluir</button>
          <button data-id="${meta.id}" data-status="nao_atingida">Não atingida</button>
        `;

        div.querySelectorAll("button").forEach((btn) => {
          btn.addEventListener("click", () => {
            const id = btn.getAttribute("data-id");
            const novoStatus = btn.getAttribute("data-status");
            atualizarStatusMeta(id, novoStatus);
          });
        });

        container.appendChild(div);
      });
    }

    async function atualizarStatusMeta(id, novoStatus) {
      await fetch(`${API_BASE}/metas/${id}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ novo_status: novoStatus }),
      });

      // depois de atualizar, recarrega as metas
      carregarMetas();
    }

    async function carregarNotificacoes() {
      const pacienteId = document.getElementById("pacienteId").value.trim();
      if (!pacienteId) {
        alert("Informe o ID do paciente (CPF).");
        return;
      }

      const resp = await fetch(`${API_BASE}/pacientes/${pacienteId}/notificacoes`);
      const notificacoes = await resp.json();

      const container = document.getElementById("listaNotificacoes");
      container.innerHTML = "";

      if (notificacoes.length === 0) {
        container.innerText = "Nenhuma notificação.";
        return;
      }

      notificacoes.forEach((noti) => {
        const div = document.createElement("div");
        div.style.border = "1px solid #ccc";
        div.style.margin = "4px 0";
        div.style.padding = "4px";

        div.innerHTML = `
          <strong>${noti.tipo}</strong> - ${noti.data_hora} <br/>
          ${noti.mensagem}
        `;

        container.appendChild(div);
      });
    }
  </script>
</body>
</html>
