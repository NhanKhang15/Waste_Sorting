const form = document.getElementById("finder-form");
const queryInput = document.getElementById("query");
const imageInput = document.getElementById("image");
const submitButton = document.getElementById("submit-button");
const statusText = document.getElementById("status-text");
const summaryCount = document.getElementById("summary-count");
const summaryMode = document.getElementById("summary-mode");
const feedback = document.getElementById("feedback");
const annotatedPreview = document.getElementById("annotated-preview");
const cropGrid = document.getElementById("crop-grid");
const cropTemplate = document.getElementById("crop-card-template");

function setFeedback(message, type = "info") {
  feedback.textContent = message;
  feedback.classList.toggle("error", type === "error");
}

function renderEmptyState(message) {
  cropGrid.innerHTML = `<div class="empty-state">${message}</div>`;
}

function resetResults() {
  annotatedPreview.removeAttribute("src");
  renderEmptyState("No cropped match yet.");
  statusText.textContent = "No result yet";
  summaryCount.textContent = "0 objects";
  summaryMode.textContent = "Waiting";
}

function renderMatches(matches) {
  cropGrid.innerHTML = "";

  if (!matches.length) {
    renderEmptyState("No detected object belongs to the requested waste group.");
    return;
  }

  for (const match of matches) {
    const node = cropTemplate.content.cloneNode(true);
    node.querySelector("img").src = `${match.crop_url}?t=${Date.now()}`;
    node.querySelector(".crop-title").textContent = `${match.class_name} -> ${match.waste_group}`;
    node.querySelector(".crop-confidence").textContent = `Confidence: ${match.confidence}`;
    cropGrid.appendChild(node);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!queryInput.value.trim()) {
    setFeedback("Please enter a supported query first.", "error");
    return;
  }

  if (!imageInput.files.length) {
    setFeedback("Please choose an image first.", "error");
    return;
  }

  const formData = new FormData();
  formData.append("query", queryInput.value.trim());
  formData.append("image", imageInput.files[0]);

  submitButton.disabled = true;
  submitButton.textContent = "Scanning...";
  setFeedback("YOLO26 is scanning the image and filtering detections through the Python waste classifier.");

  try {
    const response = await fetch("/api/find", {
      method: "POST",
      body: formData,
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "Image scanning failed.");
    }

    statusText.textContent = `Found ${payload.label} waste`;
    summaryCount.textContent = `${payload.count} objects`;
    summaryMode.textContent = "COCO 80 + keyword rules";
    annotatedPreview.src = `${payload.annotated_image}?t=${Date.now()}`;
    renderMatches(payload.matches);

    if (payload.count) {
      setFeedback(`Completed. ${payload.count} detected objects were mapped into ${payload.label} waste.`);
    } else {
      setFeedback(`Completed. No COCO object in this image matched ${payload.label} waste.`);
    }
  } catch (error) {
    resetResults();
    setFeedback(error.message, "error");
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Scan Image";
  }
});

resetResults();
