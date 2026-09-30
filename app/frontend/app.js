const chooseBtn = document.getElementById("choose-btn");
const resultEl = document.getElementById("result");
const emptyStateEl = document.getElementById("empty-state");
const resultFileEl = document.getElementById("result-file");
const resultStatusEl = document.getElementById("result-status");
const resultReasonEl = document.getElementById("result-reason");

const steps = {
  structural: document.getElementById("step-structural"),
  empty: document.getElementById("step-empty"),
  pipeline: document.getElementById("step-pipeline"),
};

function setStepState(step, state, label) {
  step.dataset.state = state;
  step.querySelector(".pipeline__status").textContent = label || "";
}

function resetPipeline() {
  setStepState(steps.structural, "idle", "");
  setStepState(steps.empty, "idle", "");
  setStepState(steps.pipeline, "idle", "não executada ainda");
}

// limpar resultado anterior
function clearResult() {
  resultEl.hidden = true;
  emptyStateEl.hidden = false;
  resetPipeline();
}

function applyPipelineState(data) {
  // data.fase é a fase que FALHOU ("estrutural" | "vazio"), ou null
  // Aqui mostramos cada passo da checagem.
  if (data.fase === "estrutural") {
    setStepState(steps.structural, "fail", "falhou");
    setStepState(steps.empty, "skipped", "não executado");
    setStepState(steps.pipeline, "skipped", "não executado");
    return;
  }

  setStepState(steps.structural, "pass", "ok");

  if (data.fase === "vazio") {
    setStepState(steps.empty, "fail", "falhou");
    setStepState(steps.pipeline, "skipped", "não executado");
    return;
  }

  setStepState(steps.empty, "pass", "ok");

  if (data.pipeline_rodou) {
    setStepState(steps.pipeline, "pass", "enviado para a pipeline");
  } else {
    setStepState(steps.pipeline, "skipped", "não executado");
  }
}

function renderResult(data) {
  resultFileEl.textContent = data.nome_do_arquivo;

  resultStatusEl.textContent = data.valido
    ? "válido"
    : `inválido \u2014 ${data.fase}`;
  resultStatusEl.className =
    "result__value " + (data.valido ? "result__value--pass" : "result__value--fail");

  resultReasonEl.textContent = data.razao;

  applyPipelineState(data);

  emptyStateEl.hidden = true;
  resultEl.hidden = false;
}

async function handleChoose() {
  clearResult();

  chooseBtn.disabled = true;
  chooseBtn.textContent = "Checando\u2026";

  try {
    const data = await window.pywebview.api.escolher_e_validar_arquivo();
    if (data) {
      renderResult(data);
    }
  } catch (err) {
    resultFileEl.textContent = "\u2014";
    resultStatusEl.textContent = "error";
    resultStatusEl.className = "result__value result__value--fail";
    resultReasonEl.textContent =
      "Erro ao chamar validador: " + err;
    emptyStateEl.hidden = true;
    resultEl.hidden = false;
  } finally {
    chooseBtn.disabled = false;
    chooseBtn.textContent = "Escolha um arquivo\u2026";
  }
}

chooseBtn.addEventListener("click", handleChoose);

resetPipeline();
