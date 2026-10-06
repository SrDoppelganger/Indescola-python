const slotRows = Array.from(document.querySelectorAll(".input-row[data-slot]"));

const outputBtn = document.getElementById("output-btn");
const outputPathEl = document.getElementById("output-path");

const submitBtn = document.getElementById("submit-btn");
const submitHint = document.getElementById("submit-hint");
const submitResultEl = document.getElementById("submit-result");

function rowElements(row) {
  return {
    slot: row.dataset.slot,
    button: row.querySelector(".input-row__btn"),
    pipelineSteps: {
      structural: row.querySelector('.pipeline__step[data-step="structural"]'),
      empty: row.querySelector('.pipeline__step[data-step="empty"]'),
      pipeline: row.querySelector('.pipeline__step[data-step="pipeline"]'),
    },
    resultSection: row.querySelector(".result"),
    resultFileEl: row.querySelector(".result-file"),
    resultStatusEl: row.querySelector(".result-status"),
    resultReasonEl: row.querySelector(".result-reason"),
  };
}

function setStep(stepEl, state, label) {
  stepEl.dataset.state = state;
  stepEl.querySelector(".pipeline__status").textContent = label || "";
}

function resetRowPipeline(row) {
  const { pipelineSteps, resultSection } = rowElements(row);
  setStep(pipelineSteps.structural, "idle", "");
  setStep(pipelineSteps.empty, "idle", "");
  setStep(pipelineSteps.pipeline, "idle", "");
  resultSection.hidden = true;
}

// data.fase is the stage that FAILED ("estrutural" | "vazio"), or null if
// the file passed everything - matches the Portuguese field names api.py
// actually returns now.
function applyPipelineState(row, data) {
  const { pipelineSteps } = rowElements(row);

  if (data.fase === "estrutural") {
    setStep(pipelineSteps.structural, "fail", "falhou");
    setStep(pipelineSteps.empty, "skipped", "n\u00e3o executado");
    setStep(pipelineSteps.pipeline, "skipped", "n\u00e3o enviado");
    return;
  }

  setStep(pipelineSteps.structural, "pass", "ok");

  if (data.fase === "vazio") {
    setStep(pipelineSteps.empty, "fail", "falhou");
    setStep(pipelineSteps.pipeline, "skipped", "n\u00e3o enviado");
    return;
  }

  setStep(pipelineSteps.empty, "pass", "ok");
  setStep(pipelineSteps.pipeline, "idle", "aguardando envio");
}

function renderSlotResult(row, data) {
  if (!data) {
    // usuário cancelou a escolha - deixa a linha como estava
    return;
  }

  const { resultSection, resultFileEl, resultStatusEl, resultReasonEl } = rowElements(row);

  resultFileEl.textContent = data.nome_arquivo;
  resultStatusEl.textContent = data.valido ? "v\u00e1lido" : `inv\u00e1lido \u2014 ${data.fase}`;
  resultStatusEl.className =
    "result__value result-status " + (data.valido ? "result__value--pass" : "result__value--fail");
  resultReasonEl.textContent = data.razao;

  applyPipelineState(row, data);
  resultSection.hidden = false;
}

async function handleSlotChoose(row) {
  const { slot, button } = rowElements(row);

  resetRowPipeline(row);

  button.disabled = true;
  const originalLabel = button.textContent;
  button.textContent = "Verificando\u2026";

  try {
    const data = await window.pywebview.api.escolher_arquivo(slot);
    renderSlotResult(row, data);
  } catch (err) {
    const { resultSection, resultFileEl, resultStatusEl, resultReasonEl } = rowElements(row);
    resultFileEl.textContent = "\u2014";
    resultStatusEl.textContent = "erro";
    resultStatusEl.className = "result__value result-status result__value--fail";
    resultReasonEl.textContent = "Erro ao falar com o validador: " + err;
    resultSection.hidden = false;
  } finally {
    button.disabled = false;
    button.textContent = originalLabel;
    refreshSubmitState();
  }
}

async function handleOutputChoose() {
  outputBtn.disabled = true;
  try {
    const path = await window.pywebview.api.escolher_pasta_saida();
    if (path) {
      outputPathEl.textContent = path;
    }
  } catch (err) {
    outputPathEl.textContent = "Erro ao escolher a pasta: " + err;
  } finally {
    outputBtn.disabled = false;
    refreshSubmitState();
  }
}

async function refreshSubmitState() {
  const status = await window.pywebview.api.get_arquivos_status();
  submitBtn.disabled = !status.pronto;
  submitHint.hidden = status.pronto;
}

function markAllRowsSubmitted() {
  slotRows.forEach((row) => {
    const { pipelineSteps } = rowElements(row);
    setStep(pipelineSteps.pipeline, "pass", "enviado");
  });
}

async function handleSubmit() {
  submitBtn.disabled = true;
  submitResultEl.hidden = true;

  try {
    const result = await window.pywebview.api.submeter_arquivos();
    submitResultEl.hidden = false;
    if (result.enviado) {
      submitResultEl.dataset.state = "pass";
      submitResultEl.textContent = `Enviado. A sa\u00edda vai para: ${result.pasta_saida}`;
      markAllRowsSubmitted();
    } else {
      submitResultEl.dataset.state = "fail";
      submitResultEl.textContent = `N\u00e3o enviado: ${result.motivo}`;
    }
  } catch (err) {
    submitResultEl.hidden = false;
    submitResultEl.dataset.state = "fail";
    submitResultEl.textContent = "Erro ao falar com o validador: " + err;
  } finally {
    await refreshSubmitState();
  }
}

slotRows.forEach((row) => {
  const { button } = rowElements(row);
  button.addEventListener("click", () => handleSlotChoose(row));
  resetRowPipeline(row);
});

outputBtn.addEventListener("click", handleOutputChoose);
submitBtn.addEventListener("click", handleSubmit);

window.addEventListener("pywebviewready", () => {
  refreshSubmitState();
});
