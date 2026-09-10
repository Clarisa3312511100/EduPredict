let graduationChart = null;
let featureChart = null;
let batchDataCache = [];

document.addEventListener("DOMContentLoaded", () => {
  initAuth();
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
      title: "Prediksi Massal Data Mahasiswa",
      subtitle: "Unggah berkas CSV/Excel untuk memprediksi risiko kelulusan seluruh mahasiswa per angkatan"
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

    const setSafeText = (id, text) => {
      const el = document.getElementById(id);
      if (el) el.textContent = text;
    };

    // Update KPI Cards
    setSafeText("kpiTotalStudents", stats.total_mahasiswa.toLocaleString());
    setSafeText("kpiOnTimeRate", `${stats.persentase_tepat_waktu}%`);
    setSafeText("kpiOnTimeCount", `${stats.tepat_waktu_count} Mahasiswa`);
    setSafeText("kpiDelayedRate", `${stats.persentase_terlambat}%`);
    setSafeText("kpiDelayedCount", `${stats.terlambat_count} Mahasiswa Berisiko`);

    // Update KPI Card ke-4
    if (stats.rata_rata_ipk) {
      setSafeText("kpiAverageIpk", `${stats.rata_rata_ipk.toFixed(2)} / 4.00`);
    }

    // Status Model
    const bestModelName = metrics.best_model || "Logistic Regression";
    const bestMetrics = (metrics.models_comparison && metrics.models_comparison[bestModelName]) || {};
    if (bestMetrics.accuracy) {
      setSafeText("topAccuracyBadge", `${(bestMetrics.accuracy * 100).toFixed(1)}%`);
    } else {
      setSafeText("topAccuracyBadge", "Aktif");
    }

    // Render Charts
    renderGraduationDonut(stats.tepat_waktu_count, stats.terlambat_count);
    if (metrics.feature_importances) {
      renderFeatureImportanceChart(metrics.feature_importances);
    }
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
        backgroundColor: ["#2d6a4f", "#991b1b"],
        hoverBackgroundColor: ["#1b4332", "#7f1d1d"],
        borderWidth: 1,
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
        backgroundColor: "#1e293b",
        borderRadius: 2
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
    { id: "inpIpk", labelId: "valIpk", isDec: true },
    { id: "inpUmur", labelId: "valUmur", isDec: false }
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
    document.getElementById("inpNIM").value = "20180055";
    document.getElementById("inpNama").value = "Bambang Hidayat";
    document.getElementById("inpGender").value = "Laki-laki";
    setSliderVal("inpUmur", "valUmur", 27, false);

    // Set nilai profil berisiko (tren menurun)
    setSliderVal("inpIps1", "valIps1", 3.10, true);
    setSliderVal("inpIps2", "valIps2", 2.65, true);
    setSliderVal("inpIps3", "valIps3", 2.20, true);
    setSliderVal("inpIps4", "valIps4", 1.95, true);
    setSliderVal("inpIpk", "valIpk", 2.48, true);

    document.getElementById("inpBekerja").checked = true;
    document.getElementById("inpNikah").checked = true;

    // Trigger auto predict
    form.dispatchEvent(new Event("submit"));
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      NIM: document.getElementById("inpNIM").value,
      Nama: document.getElementById("inpNama").value,
      Jenis_Kelamin: document.getElementById("inpGender").value,
      Umur: parseInt(document.getElementById("inpUmur").value) || 23,
      Status_Bekerja: document.getElementById("inpBekerja").checked ? 1 : 0,
      Status_Nikah: document.getElementById("inpNikah").checked ? 1 : 0,
      IPS_Sem1: parseFloat(document.getElementById("inpIps1").value),
      IPS_Sem2: parseFloat(document.getElementById("inpIps2").value),
      IPS_Sem3: parseFloat(document.getElementById("inpIps3").value),
      IPS_Sem4: parseFloat(document.getElementById("inpIps4").value),
      IPK_Kumulatif: parseFloat(document.getElementById("inpIpk").value)
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
  if (sl && lb) {
    sl.value = val;
    lb.textContent = isDec ? parseFloat(val).toFixed(2) : val;
  }
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
  const setElText = (id, txt) => {
    const el = document.getElementById(id);
    if (el) el.textContent = txt;
  };

  setElText("resIpk", summary.ipk_kumulatif.toFixed(2));
  setElText("resTren", (summary.tren_ips > 0 ? "+" : "") + summary.tren_ips.toFixed(2));
  setElText("resUmur", `${summary.umur} Thn`);
  setElText("resIps4", summary.ips_sem4 ? summary.ips_sem4.toFixed(2) : "--");

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

  // Search & Filter Batch Table
  const searchInput = document.getElementById("searchBatchStudent");
  const btnExportCsv = document.getElementById("btnExportBatchCsv");

  function applyBatchFilters() {
    const riskVal = filterRisk.value;
    const query = (searchInput ? searchInput.value.trim().toLowerCase() : "");

    let filtered = batchDataCache;

    if (riskVal !== "ALL") {
      filtered = filtered.filter(item => item.tingkat_risiko === riskVal);
    }

    if (query) {
      filtered = filtered.filter(item => 
        (item.nama && item.nama.toLowerCase().includes(query)) ||
        (item.nim && item.nim.toLowerCase().includes(query))
      );
    }

    renderBatchTable(filtered);
  }

  filterRisk.addEventListener("change", applyBatchFilters);
  if (searchInput) {
    searchInput.addEventListener("input", applyBatchFilters);
  }

  // Export Batch Results to CSV
  if (btnExportCsv) {
    btnExportCsv.addEventListener("click", () => {
      exportBatchCsv(batchDataCache);
    });
  }

  // Print Diagnosis Lembar Rekomendasi PA
  const btnPrint = document.getElementById("btnPrintDiagnosis");
  if (btnPrint) {
    btnPrint.addEventListener("click", () => {
      window.print();
    });
  }
}

function renderBatchTable(data) {
  const tbody = document.getElementById("batchTableBody");
  tbody.innerHTML = "";

  if (!data || data.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4">Tidak ada data mahasiswa yang sesuai dengan kriteria pencarian/filter.</td></tr>';
    return;
  }

  data.forEach(item => {
    const tr = document.createElement("tr");
    const trenFormatted = item.tren_ips > 0 ? `+${item.tren_ips.toFixed(2)}` : item.tren_ips.toFixed(2);
    const trenClass = item.tren_ips < -0.3 ? "text-danger font-bold" : (item.tren_ips > 0.2 ? "text-success font-bold" : "");

    tr.innerHTML = `
      <td><code>${item.nim}</code></td>
      <td><strong>${item.nama}</strong></td>
      <td><strong>${item.ipk.toFixed(2)}</strong></td>
      <td><span class="${trenClass}">${trenFormatted}</span></td>
      <td>${item.umur} Thn</td>
      <td><strong>${item.prob_terlambat}%</strong></td>
      <td><span class="badge ${item.status_color}">${item.tingkat_risiko}</span></td>
      <td><span class="badge ${item.status_color}">${item.status}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

function exportBatchCsv(data) {
  if (!data || data.length === 0) {
    alert("Tidak ada data hasil prediksi untuk diunduh. Silakan proses batch terlebih dahulu.");
    return;
  }

  const headers = ["NIM", "Nama Mahasiswa", "IPK Kumulatif", "Tren Nilai IPS", "Usia", "Probabilitas Terlambat (%)", "Tingkat Risiko", "Prediksi Kelulusan"];
  
  const csvRows = [];
  csvRows.push(headers.join(","));

  data.forEach(row => {
    const values = [
      `"${row.nim}"`,
      `"${row.nama.replace(/"/g, '""')}"`,
      row.ipk.toFixed(2),
      row.tren_ips.toFixed(2),
      row.umur,
      row.prob_terlambat,
      `"${row.tingkat_risiko}"`,
      `"${row.status}"`
    ];
    csvRows.push(values.join(","));
  });

  const csvContent = "data:text/csv;charset=utf-8,\uFEFF" + encodeURIComponent(csvRows.join("\n"));
  const downloadAnchor = document.createElement("a");
  downloadAnchor.setAttribute("href", csvContent);
  downloadAnchor.setAttribute("download", `Hasil_Prediksi_Kelulusan_EduPredict_${new Date().toISOString().slice(0,10)}.csv`);
  document.body.appendChild(downloadAnchor);
  downloadAnchor.click();
  document.body.removeChild(downloadAnchor);
}

// 6. Autentikasi Sederhana (Dosen / Admin)
function initAuth() {
  const loginOverlay = document.getElementById("loginOverlay");
  const loginForm = document.getElementById("loginForm");
  const loginAlert = document.getElementById("loginAlert");
  const loginUsername = document.getElementById("loginUsername");
  const loginPassword = document.getElementById("loginPassword");
  const navUserName = document.getElementById("navUserName");
  const navUserRole = document.getElementById("navUserRole");
  const btnLogout = document.getElementById("btnLogout");
  const btnDemoDosen = document.getElementById("btnDemoDosen");
  const btnDemoAdmin = document.getElementById("btnDemoAdmin");

  // Periksa apakah user sudah login di localStorage
  const savedUserJson = localStorage.getItem("edupredict_auth_user");
  if (savedUserJson) {
    try {
      const user = JSON.parse(savedUserJson);
      if (user.name && user.name.toLowerCase().includes("clarisa")) {
        user.name = "Dosen Pembimbing Akademik";
        user.role = "Dosen PA";
        localStorage.setItem("edupredict_auth_user", JSON.stringify(user));
      }
      applyUserSession(user);
    } catch (e) {
      showLoginModal();
    }
  } else {
    showLoginModal();
  }

  function showLoginModal() {
    loginOverlay.style.display = "flex";
  }

  function hideLoginModal() {
    loginOverlay.style.display = "none";
  }

  function applyUserSession(user) {
    if (navUserName) navUserName.textContent = user.name;
    if (navUserRole) navUserRole.textContent = user.role;
    hideLoginModal();
  }

  // Handle submit form login
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      loginAlert.style.display = "none";

      const username = loginUsername.value.trim();
      const password = loginPassword.value.trim();

      try {
        const res = await fetch("/api/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password })
        });

        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || "Gagal melakukan autentikasi");
        }

        const data = await res.json();
        localStorage.setItem("edupredict_auth_user", JSON.stringify(data.user));
        applyUserSession(data.user);
      } catch (err) {
        loginAlert.textContent = err.message;
        loginAlert.style.display = "block";
      }
    });
  }

  // Quick Demo Buttons
  if (btnDemoDosen) {
    btnDemoDosen.addEventListener("click", () => {
      loginUsername.value = "dosen";
      loginPassword.value = "password123";
      loginForm.dispatchEvent(new Event("submit"));
    });
  }

  if (btnDemoAdmin) {
    btnDemoAdmin.addEventListener("click", () => {
      loginUsername.value = "admin";
      loginPassword.value = "admin123";
      loginForm.dispatchEvent(new Event("submit"));
    });
  }

  // Logout Handler
  if (btnLogout) {
    btnLogout.addEventListener("click", () => {
      if (confirm("Apakah Anda yakin ingin keluar dari sistem EduPredict?")) {
        localStorage.removeItem("edupredict_auth_user");
        showLoginModal();
      }
    });
  }
}
