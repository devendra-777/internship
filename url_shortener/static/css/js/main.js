function copyToClipboard(inputId) {
  const input = document.getElementById(inputId);
  if (!input) return;
  input.select();
  input.setSelectionRange(0, 99999); // for mobile
  navigator.clipboard.writeText(input.value)
    .then(() => {
      showToast("Copied to clipboard");
    })
    .catch(() => {
      alert("Copy failed. Please copy manually.");
    });
}

function copyText(text) {
  navigator.clipboard.writeText(text)
    .then(() => showToast("Copied to clipboard"))
    .catch(() => alert("Copy failed. Please copy manually."));
}

function showToast(message) {
  // Lightweight feedback—use Bootstrap alert or native toast if desired
  const el = document.createElement("div");
  el.className = "position-fixed top-0 end-0 p-3";
  el.style.zIndex = "1080";
  el.innerHTML = `
    <div class="toast align-items-center text-bg-dark border-0 show" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">${message}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>`;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 2000);
}