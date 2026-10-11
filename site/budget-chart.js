/* E10.3: rasterize a source-bearing SVG only after an explicit sharing action. */
(function () {
  'use strict';
  const controls = document.querySelector('[data-chart-url]');
  if (!controls) return;
  const shareButton = document.getElementById('budget-chart-share');
  const saveButton = document.getElementById('budget-chart-save');
  const feedback = document.getElementById('budget-chart-feedback');
  let prepared = null;

  async function imageFile() {
    if (prepared) return prepared;
    const url = new URL(controls.dataset.chartUrl, window.location.href);
    if (url.origin !== window.location.origin) throw new Error('Invalid chart origin');
    const response = await fetch(url.href, { credentials: 'omit' });
    if (!response.ok) throw new Error('Chart unavailable');
    const reader = response.body.getReader();
    let size = 0;
    const chunks = [];
    while (true) {
      const chunk = await reader.read();
      if (chunk.done) break;
      size += chunk.value.byteLength;
      if (size > 131072) { await reader.cancel(); throw new Error('Chart too large'); }
      chunks.push(chunk.value);
    }
    const svg = new Blob(chunks, { type: 'image/svg+xml' });
    const dataUrl = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () => reject(new Error('Image unavailable'));
      reader.readAsDataURL(svg);
    });
    const image = new Image();
    // The serving CSP already permits data images; no blob-image permission is needed.
    image.src = dataUrl;
    await image.decode();
    if (image.naturalWidth !== 1080 || image.naturalHeight > 8192) throw new Error('Invalid chart dimensions');
    const canvas = document.createElement('canvas');
    canvas.width = image.naturalWidth;
    canvas.height = image.naturalHeight;
    const context = canvas.getContext('2d');
    if (!context) throw new Error('Canvas unavailable');
    context.drawImage(image, 0, 0);
    const png = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
    if (!png) throw new Error('Image unavailable');
    prepared = new File([png], 'pge-2023.png', { type: 'image/png' });
    return prepared;
  }

  function download(file) {
    const url = URL.createObjectURL(file);
    const link = document.createElement('a');
    link.href = url;
    link.download = file.name;
    document.body.append(link);
    link.click();
    link.remove();
    // Downloads may consume the URL after the click handler returns.
    setTimeout(() => URL.revokeObjectURL(url), 60000);
  }

  async function act(nativeShare) {
    shareButton.disabled = true;
    saveButton.disabled = true;
    feedback.textContent = 'Preparando la imagen…';
    try {
      const file = await imageFile();
      if (nativeShare && navigator.share && navigator.canShare && navigator.canShare({ files: [file] })) {
        await navigator.share({ files: [file], title: 'PGE 2023: presupuesto aprobado',
          text: 'Reparto del presupuesto aprobado de 2023. Datos históricos; no son gasto ejecutado.' });
        feedback.textContent = 'Se ha compartido la imagen.';
      } else {
        download(file);
        feedback.textContent = 'Imagen descargada. Puedes compartirla desde tu dispositivo.';
      }
    } catch (error) {
      feedback.textContent = error.name === 'AbortError' ? '' :
        'No se pudo compartir la imagen. Prueba «Guardar imagen (PNG)» o descarga el gráfico SVG.';
    } finally {
      shareButton.disabled = false;
      saveButton.disabled = false;
    }
  }
  shareButton.hidden = false;
  saveButton.hidden = false;
  shareButton.addEventListener('click', () => act(true));
  saveButton.addEventListener('click', () => act(false));
}());
