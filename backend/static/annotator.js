const imageList = document.getElementById("image-list");
const annotationList = document.getElementById("annotation-list");
const classSelect = document.getElementById("class-select");
const saveButton = document.getElementById("save-button");
const clearButton = document.getElementById("clear-button");
const feedback = document.getElementById("annotator-feedback");
const canvas = document.getElementById("annotator-canvas");
const canvasPanel = document.querySelector(".canvas-panel");
const imageTemplate = document.getElementById("image-item-template");
const annotationTemplate = document.getElementById("annotation-item-template");
const ctx = canvas.getContext("2d");

const state = {
  classes: [],
  images: [],
  currentImage: null,
  annotations: [],
  imageWidth: 0,
  imageHeight: 0,
  scale: 1,
  imageElement: null,
  dragStart: null,
  draftBox: null,
};

function setFeedback(message, type = "info") {
  feedback.textContent = message;
  feedback.classList.toggle("error", type === "error");
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function renderImageList() {
  imageList.innerHTML = "";
  if (!state.images.length) {
    imageList.innerHTML = '<div class="empty-state">Chưa có ảnh nào trong thư mục training_image.</div>';
    return;
  }

  for (const image of state.images) {
    const node = imageTemplate.content.cloneNode(true);
    const button = node.querySelector(".image-item");
    const isActive = state.currentImage && state.currentImage.path === image.path;
    button.classList.toggle("active", Boolean(isActive));
    node.querySelector(".image-name").textContent = image.path;
    node.querySelector(".image-meta").textContent =
      `${image.width}x${image.height} | ${image.box_count} box | ${image.label_exists ? "đã lưu label" : "chưa lưu label"}`;
    button.addEventListener("click", () => loadImage(image.path));
    imageList.appendChild(node);
  }
}

function renderAnnotationList() {
  annotationList.innerHTML = "";
  if (!state.currentImage) {
    annotationList.innerHTML = '<div class="empty-state">Chọn một ảnh để xem danh sách box.</div>';
    return;
  }

  if (!state.annotations.length) {
    annotationList.innerHTML = '<div class="empty-state">Ảnh này chưa có box nào.</div>';
    return;
  }

  state.annotations.forEach((annotation, index) => {
    const node = annotationTemplate.content.cloneNode(true);
    node.querySelector(".annotation-name").textContent = annotation.class_name;
    node.querySelector(".annotation-coords").textContent =
      `(${Math.round(annotation.x1)}, ${Math.round(annotation.y1)}) → (${Math.round(annotation.x2)}, ${Math.round(annotation.y2)})`;
    node.querySelector(".annotation-delete").addEventListener("click", () => {
      state.annotations.splice(index, 1);
      renderAnnotationList();
      redrawCanvas();
    });
    annotationList.appendChild(node);
  });
}

function getCanvasPoint(event) {
  const rect = canvas.getBoundingClientRect();
  return {
    x: clamp(event.clientX - rect.left, 0, rect.width),
    y: clamp(event.clientY - rect.top, 0, rect.height),
  };
}

function toImageCoords(point) {
  return {
    x: point.x / state.scale,
    y: point.y / state.scale,
  };
}

function drawBox(box, color = "#0d7a5f", lineWidth = 2) {
  const x = box.x1 * state.scale;
  const y = box.y1 * state.scale;
  const width = (box.x2 - box.x1) * state.scale;
  const height = (box.y2 - box.y1) * state.scale;

  ctx.strokeStyle = color;
  ctx.lineWidth = lineWidth;
  ctx.strokeRect(x, y, width, height);

  ctx.fillStyle = color;
  ctx.font = "600 14px 'Be Vietnam Pro'";
  const label = box.class_name || "";
  if (label) {
    const textWidth = ctx.measureText(label).width + 12;
    ctx.fillRect(x, Math.max(0, y - 24), textWidth, 22);
    ctx.fillStyle = "#ffffff";
    ctx.fillText(label, x + 6, Math.max(15, y - 8));
  }
}

function redrawCanvas() {
  if (!state.imageElement) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    return;
  }

  const availableWidth = Math.max(320, canvasPanel.clientWidth - 28);
  state.scale = Math.min(1, availableWidth / state.imageWidth);
  canvas.width = Math.max(1, Math.round(state.imageWidth * state.scale));
  canvas.height = Math.max(1, Math.round(state.imageHeight * state.scale));

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(state.imageElement, 0, 0, canvas.width, canvas.height);

  for (const annotation of state.annotations) {
    drawBox(annotation, "#0d7a5f", 2);
  }

  if (state.draftBox) {
    drawBox(state.draftBox, "#c46d18", 2);
  }
}

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "Có lỗi xảy ra.");
  }
  return payload;
}

async function loadInventory() {
  const payload = await fetchJson("/api/annotator/files");
  state.classes = payload.classes;
  state.images = payload.images;

  classSelect.innerHTML = "";
  for (const className of state.classes) {
    const option = document.createElement("option");
    option.value = className;
    option.textContent = className;
    classSelect.appendChild(option);
  }

  renderImageList();
  renderAnnotationList();
}

async function loadImage(relativePath) {
  setFeedback("Đang tải ảnh và label...");
  const annotationPayload = await fetchJson(`/api/annotator/annotations?image=${encodeURIComponent(relativePath)}`);

  state.currentImage = { path: relativePath };
  state.annotations = annotationPayload.annotations;
  state.imageWidth = annotationPayload.width;
  state.imageHeight = annotationPayload.height;
  state.draftBox = null;
  state.dragStart = null;

  const imageElement = new Image();
  imageElement.onload = () => {
    state.imageElement = imageElement;
    renderImageList();
    renderAnnotationList();
    redrawCanvas();
    setFeedback(`Đã tải ${relativePath}. Kéo chuột trên ảnh để tạo box, sau đó nhấn "Lưu label".`);
  };
  imageElement.src = `/api/annotator/image?path=${encodeURIComponent(relativePath)}&t=${Date.now()}`;
}

canvas.addEventListener("mousedown", (event) => {
  if (!state.currentImage || !state.imageElement) {
    return;
  }

  const point = toImageCoords(getCanvasPoint(event));
  state.dragStart = point;
  state.draftBox = null;
});

canvas.addEventListener("mousemove", (event) => {
  if (!state.dragStart || !state.currentImage) {
    return;
  }

  const point = toImageCoords(getCanvasPoint(event));
  state.draftBox = {
    class_name: classSelect.value,
    x1: Math.min(state.dragStart.x, point.x),
    y1: Math.min(state.dragStart.y, point.y),
    x2: Math.max(state.dragStart.x, point.x),
    y2: Math.max(state.dragStart.y, point.y),
  };
  redrawCanvas();
});

canvas.addEventListener("mouseup", () => {
  if (!state.dragStart || !state.draftBox) {
    state.dragStart = null;
    state.draftBox = null;
    return;
  }

  const minSize = 6;
  if (
    state.draftBox.x2 - state.draftBox.x1 >= minSize &&
    state.draftBox.y2 - state.draftBox.y1 >= minSize
  ) {
    state.annotations.push({ ...state.draftBox });
    renderAnnotationList();
  }

  state.dragStart = null;
  state.draftBox = null;
  redrawCanvas();
});

saveButton.addEventListener("click", async () => {
  if (!state.currentImage) {
    setFeedback("Bạn cần chọn một ảnh trước.", "error");
    return;
  }

  saveButton.disabled = true;
  setFeedback("Đang lưu label YOLO...");
  try {
    const payload = await fetchJson("/api/annotator/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        image: state.currentImage.path,
        annotations: state.annotations,
      }),
    });

    state.annotations = payload.annotations;
    renderAnnotationList();
    await loadInventory();
    setFeedback(`Đã lưu ${payload.box_count} box cho ảnh ${payload.image}.`);
  } catch (error) {
    setFeedback(error.message, "error");
  } finally {
    saveButton.disabled = false;
  }
});

clearButton.addEventListener("click", () => {
  state.annotations = [];
  state.draftBox = null;
  renderAnnotationList();
  redrawCanvas();
  setFeedback("Đã xóa box trên giao diện. Nhấn 'Lưu label' nếu muốn ghi thay đổi xuống file.");
});

window.addEventListener("resize", () => {
  if (state.imageElement) {
    redrawCanvas();
  }
});

loadInventory().catch((error) => {
  setFeedback(error.message, "error");
});
