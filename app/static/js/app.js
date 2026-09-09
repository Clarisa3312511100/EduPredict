let graduationChart = null;
let featureChart = null;
let batchDataCache = [];

document.addEventListener("DOMContentLoaded", () => {
  initNavigation();
  initSliderListeners();
  initFormInteractions();
  initBatchUpload();
  loadDashboardData();
  checkServerHealth();
});

// 1. Tab Navigation
function initNavigation() {
  const navButtons = document.querySelectorAll(".nav-item");
  const tabContents = document.querySelectorAll(".tab-content");
  const pageTitle = document.getElementById("pageTitle");
  const pageSubtitle = document.getElementById("pageSubtitle");

  const tabTitles = {
    "overview": {
      title: "Dashboard Ringkasan Akademik",
      subtitle: "Pemantauan risiko keterlambatan masa studi mahasiswa berbasis Machine Learning"
    },
    "single-predict": {
      title: "Simulasi Prediksi Individual",
      subtitle: "Eksplorasi pengaruh nilai dan faktor akademik terhadap probabilitas kelulusan (What-if Analysis)"
    },
    "batch-predict": {
      title: "Prediksi Massal (Batch Upload)",
      subtitle: "Unggah berkas CSV/Excel untuk memetakan risiko kelulusan seluruh mahasiswa per angkatan"
    },
    "model-metrics": {
      title: "Spesifikasi & Evaluasi Model",
      subtitle: "Dokumentasi metodologi, metrik evaluasi (Recall/Precision), dan pipeline pembelajaran"
    }
  };

  navButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetTab = btn.dataset.tab;

      navButtons.forEach(b => b.classList.remove("active"));
      tabContents.forEach(tab => tab.classList.remove("active"));

      btn.classList.add("active");
      const activeContent = document.getElementById(`tab-${targetTab}`);
      if (activeContent) activeContent.classList.add("active");

      if (tabTitles[targetTab]) {
        pageTitle.textContent = tabTitles[targetTab].title;
        pageSubtitle.textContent = tabTitles[targetTab].subtitle;
      }
    });
  });

  document.getElementById("btnRefreshData").addEventListener("click", () => {
    loadDashboardData();
  });
}

// 2. Health & Overview Loader
async function checkServerHealth() {
  try {
    const res = await fetch("/api/health");
    const data = await res.json();
    const dot = document.getElementById("serverStatusDot");
    const text = document.getElementById("serverStatusText");

    if (data.status === "online") {
      dot.className = "status-indicator online";
      text.textContent = data.model_ready ? "Model Aktif (Siap Inferensi)" : "Model Sedang Dilatih";
    }
  } catch (err) {
    const dot = document.getElementById("serverStatusDot");
    const text = document.getElementById("serverStatusText");
    dot.className = "status-indicator offline";
    text.textContent = "Server Offline";
  }
}

async function loadDashboardData() {
  try {
    const res = await fetch("/api/overview");
    const data = await res.json();

    if (!data.stats || !data.metrics) {
      console.warn("Artifacts belum siap. Jalankan skrip training.");
      return;
    }

    const { stats, metrics } = data;

    // Update KPI Cards
    document.getElementById("kpiTotalStudents").textContent = stats.total_mahasiswa.toLocaleString();
    document.getElementById("kpiOnTimeRate").textContent = `${stats.persentase_tepat_waktu}%`;
    document.getElementById("kpiOnTimeCount").textContent = `${stats.tepat_waktu_count} Mahasiswa`;
    document.getElementById("kpiDelayedRate").textContent = `${stats.persentase_terlambat}%`;
    document.getElementById("kpiDelayedCount").textContent = `${stats.terlambat_count} Mahasiswa Berisiko`;

    // Ambil metrik model terbaik
    const bestModelName = metrics.best_model;
    const bestMetrics = metrics.models_comparison[bestModelName];
    document.getElementById("kpiRecallScore").textContent = `${(bestMetrics.recall * 100).toFixed(1)}%`;
    document.getElementById("topAccuracyBadge").textContent = `${(bestMetrics.accuracy * 100).toFixed(1)}%`;
    document.getElementById("bestModelBadge").textContent = `Best Model: ${bestModelName} (F1: ${(bestMetrics.f1_score * 100).toFixed(1)}%)`;

    // Render Charts
    renderGraduationDonut(stats.tepat_waktu_count, stats.terlambat_count);
    renderFeatureImportanceChart(metrics.feature_importances);
    renderModelComparisonTable(metrics.models_comparison, bestModelName);
  } catch (err) {
    console.error("Gagal memuat overview:", err);
  }
}

// 3. Render Visualizations
function renderGraduationDonut(onTimeCount, delayedCount) {
  const ctx = document.getElementById("graduationChart").getContext("2d");
  if (graduationChart) graduationChart.destroy();

  graduationChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Tepat Waktu", "Terlambat / Berisiko"],
      datasets: [{
        data: [onTimeCount, delayedCount],
        backgroundColor: ["#10b981", "#ef4444"],
        hoverBackgroundColor: ["#059669", "#dc2626"],
        borderWidth: 2,
        borderColor: "#ffffff"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom" },
        tooltip: {
          callbacks: {
            label: function (context) {
              const total = onTimeCount + delayedCount;
              const val = context.raw;
              const pct = ((val / total) * 100).toFixed(1);
              return ` ${context.label}: ${val} (${pct}%)`;
            }
          }
        }
      }
    }
  });
}

function renderFeatureImportanceChart(importances) {
  const ctx = document.getElementById("featureChart").getContext("2d");
  if (featureChart) featureChart.destroy();

  const topFeatures = importances.slice(0, 6);
  const labels = topFeatures.map(item => {
    return item.feature
      .replace("num__", "")
      .replace("cat__", "")
      .replace("_", " ");
  });
  const values = topFeatures.map(item => item.importance);

  featureChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Bobot Pengaruh (Importance)",
        data: values,
        backgroundColor: "#4f46e5",
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          beginAtZero: true,
          grid: { color: "#f1f5f9" }
        },
        y: {
          grid: { display: false }
        }
      }
    }
  });
}

function renderModelComparisonTable(modelsComparison, bestModel) {
  const tbody = document.getElementById("modelsTableBody");
  tbody.innerHTML = "";

  Object.entries(modelsComparison).forEach(([name, m]) => {
    const isBest = name === bestModel;
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td><strong>${name}</strong></td>
      <td>${(m.accuracy * 100).toFixed(2)}%</td>
      <td>${(m.precision * 100).toFixed(2)}%</td>
      <td><strong class="text-primary">${(m.recall * 100).toFixed(2)}%</strong></td>
      <td>${(m.f1_score * 100).toFixed(2)}%</td>
      <td>${(m.roc_auc * 100).toFixed(2)}%</td>
      <td>
        ${isBest ? '<span class="badge success"><i class="fa-solid fa-crown"></i> Terpilih (Best)</span>' : '<span class="badge">Baseline</span>'}
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// 4. Slider Listeners
function initSliderListeners() {
  const sliders = [
    { id: "inpIps1", labelId: "valIps1", isDec: true },
    { id: "inpIps2", labelId: "valIps2", isDec: true },
    { id: "inpIps3", labelId: "valIps3", isDec: true },
    { id: "inpIps4", labelId: "valIps4", isDec: true },
    { id: "inpSksLulus", labelId: "valSksLulus", isDec: false },
    { id: "inpSksGagal", labelId: "valSksGagal", isDec: false },
    { id: "inpKehadiran", labelId: "valKehadiran", isDec: false }
  ];

  sliders.forEach(s => {
    const input = document.getElementById(s.id);
    const label = document.getElementById(s.labelId);
    if (input && label) {
      input.addEventListener("input", (e) => {
        label.textContent = s.isDec ? parseFloat(e.target.value).toFixed(2) : e.target.value;
      });
    }
  });
}

// 5. Single Predict Form & Simulation
function initFormInteractions() {
  const form = document.getElementById("singlePredictForm");
  const btnPreset = document.getElementById("btnFillPreset");

  btnPreset.addEventListener("click", () => {
    document.getElementById("inpNIM").value = "2021008765";
    document.getElementById("inpNama").value = "Rafi Nugraha";
    document.getElementById("inpJalur").value = "Mandiri";
    document.getElementById("inpGender").value = "Laki-laki";

    // Set nilai berisiko
    setSliderVal("inpIps1", "valIps1", 3.10, true);
    setSliderVal("inpIps2", "valIps2", 2.65, true);
    setSliderVal("inpIps3", "valIps3", 2.20, true);
    setSliderVal("inpIps4", "valIps4", 1.95, true);
    setSliderVal("inpSksLulus", "valSksLulus", 68, false);
    setSliderVal("inpSksGagal", "valSksGagal", 14, false);
    setSliderVal("inpKehadiran", "valKehadiran", 68, false);

    document.getElementById("inpBekerja").checked = true;
    document.getElementById("inpCuti").checked = true;

    // Trigger auto predict
    form.dispatchEvent(new Event("submit"));
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      NIM: document.getElementById("inpNIM").value,
      Nama: document.getElementById("inpNama").value,
      Jalur_Masuk: document.getElementById("inpJalur").value,
      Jenis_Kelamin: document.getElementById("inpGender").value,
      IPS_Sem1: parseFloat(document.getElementById("inpIps1").value),
      IPS_Sem2: parseFloat(document.getElementById("inpIps2").value),
      IPS_Sem3: parseFloat(document.getElementById("inpIps3").value),
      IPS_Sem4: parseFloat(document.getElementById("inpIps4").value),
      SKS_Lulus: parseInt(document.getElementById("inpSksLulus").value),
      SKS_Gagal: parseInt(document.getElementById("inpSksGagal").value),
      Persentase_Kehadiran: parseFloat(document.getElementById("inpKehadiran").value),
      Status_Bekerja: document.getElementById("inpBekerja").checked ? 1 : 0,
      Pernah_Cuti: document.getElementById("inpCuti").checked ? 1 : 0
    };

    const btn = document.getElementById("btnRunPrediction");
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Memproses Analisis...';

    try {
      const res = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Gagal melakukan prediksi");
      }

      const result = await res.json();
      renderPredictionResult(result);
    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Analisis & Prediksi Kelulusan';
    }
  });
}

function setSliderVal(sliderId, labelId, val, isDec) {
  const sl = document.getElementById(sliderId);
  const lb = document.getElementById(labelId);
  sl.value = val;
  lb.textContent = isDec ? parseFloat(val).toFixed(2) : val;
}

function renderPredictionResult(res) {
  const badge = document.getElementById("riskBadge");
  badge.className = `badge ${res.status_color}`;
  badge.textContent = `${res.status} (Risiko ${res.tingkat_risiko})`;

  // Meter probabilitas
  const riskPct = res.probabilitas_terlambat;
  document.getElementById("riskPercentage").textContent = `${riskPct}%`;
  const bar = document.getElementById("riskProgressBar");
  bar.style.width = `${riskPct}%`;

  if (riskPct >= 60) {
    bar.style.backgroundColor = "var(--danger)";
  } else if (riskPct >= 35) {
    bar.style.backgroundColor = "var(--warning)";
  } else {
    bar.style.backgroundColor = "var(--success)";
  }

  // Mini summary
  const summary = res.ringkasan_akademik;
  document.getElementById("resIpk").textContent = summary.ipk_kumulatif.toFixed(2);
  document.getElementById("resTren").textContent = (summary.tren_ips > 0 ? "+" : "") + summary.tren_ips.toFixed(2);
  document.getElementById("resSksGagal").textContent = `${summary.sks_gagal} SKS`;
  document.getElementById("resKehadiran").textContent = `${summary.kehadiran}%`;

  // Risk Factors
  const riskList = document.getElementById("riskFactorsList");
  riskList.innerHTML = "";
  if (res.faktor_risiko && res.faktor_risiko.length > 0) {
    res.faktor_risiko.forEach(item => {
      const li = document.createElement("li");
      li.className = "risk";
      li.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> ${item}`;
      riskList.appendChild(li);
    });
  } else {
    riskList.innerHTML = '<li class="empty-text">Tidak ditemukan faktor risiko signifikan</li>';
  }

  // Positive Factors
  const posList = document.getElementById("positiveFactorsList");
  posList.innerHTML = "";
  if (res.faktor_positif && res.faktor_positif.length > 0) {
    res.faktor_positif.forEach(item => {
      const li = document.createElement("li");
      li.className = "positive";
      li.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${item}`;
      posList.appendChild(li);
    });
  } else {
    posList.innerHTML = '<li class="empty-text">Tidak ada catatan performa menonjol</li>';
  }

  // Action Recommendation
  document.getElementById("recommendationText").textContent = res.rekomendasi_tindakan;
}

// 6. Batch Upload Logic
function initBatchUpload() {
  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("batchFileInput");
  const btnBrowse = document.getElementById("btnBrowseFile");
  const fileNameTag = document.getElementById("selectedFileName");
  const btnProcess = document.getElementById("btnProcessBatch");
  const filterRisk = document.getElementById("filterBatchRisk");

  let selectedFile = null;

  btnBrowse.addEventListener("click", () => fileInput.click());

  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.style.borderColor = "var(--primary)";
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.style.borderColor = "#cbd5e1";
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.style.borderColor = "#cbd5e1";
    if (e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  function handleFileSelected(file) {
    selectedFile = file;
    fileNameTag.innerHTML = `<i class="fa-solid fa-file"></i> ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    btnProcess.disabled = false;
  }

  btnProcess.addEventListener("click", async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append("file", selectedFile);

    btnProcess.disabled = true;
    btnProcess.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Memproses File...';

    try {
      const res = await fetch("/api/predict-batch", {
        method: "POST",
        body: formData
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Gagal memproses batch data");
      }

      const data = await res.json();
      batchDataCache = data.results;

      // Update Summary Cards
      document.getElementById("batchSummaryCard").style.display = "block";
      document.getElementById("batchResultsTableContainer").style.display = "block";

      document.getElementById("batchTotal").textContent = data.total_mahasiswa;
      document.getElementById("batchOnTime").textContent = data.tepat_waktu_count;
      document.getElementById("batchMedium").textContent = data.risiko_sedang_count;
      document.getElementById("batchHigh").textContent = data.risiko_tinggi_count;

      renderBatchTable(batchDataCache);
    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      btnProcess.disabled = false;
      btnProcess.innerHTML = '<i class="fa-solid fa-play"></i> Proses Prediksi Seluruh Mahasiswa';
    }
  });

  filterRisk.addEventListener("change", (e) => {
    const val = e.target.value;
    if (val === "ALL") {
      renderBatchTable(batchDataCache);
    } else {
      const filtered = batchDataCache.filter(item => item.tingkat_risiko === val);
      renderBatchTable(filtered);
    }
  });
}

function renderBatchTable(data) {
  const tbody = document.getElementById("batchTableBody");
  tbody.innerHTML = "";

  if (data.length === 0) {
    tbody.innerHTML = '<tr><td colspan="9" class="text-center">Tidak ada data mahasiswa sesuai filter.</td></tr>';
    return;
  }

  data.forEach(item => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><code>${item.nim}</code></td>
      <td><strong>${item.nama}</strong></td>
      <td>${item.ipk.toFixed(2)}</td>
      <td>${item.sks_lulus} SKS</td>
      <td><span class="${item.sks_gagal > 6 ? 'text-danger font-bold' : ''}">${item.sks_gagal} SKS</span></td>
      <td>${item.kehadiran}%</td>
      <td><strong>${item.prob_terlambat}%</strong></td>
      <td><span class="badge ${item.status_color}">${item.tingkat_risiko}</span></td>
      <td><span class="badge ${item.status_color}">${item.status}</span></td>
    `;
    tbody.appendChild(tr);
  });
}
