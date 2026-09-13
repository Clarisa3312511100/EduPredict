import os
import sys
import subprocess
from pathlib import Path
import markdown

# Pastikan console output mendukung UTF-8 di Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def get_browser_path():
    chrome_path = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    edge_path = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
    
    if chrome_path.exists():
        return str(chrome_path)
    if edge_path.exists():
        return str(edge_path)
    raise FileNotFoundError("Browser Chrome atau Edge tidak ditemukan.")

def build_html(markdown_content: str, title: str = "EduPredict Documentation") -> str:
    body_html = markdown.markdown(
        markdown_content,
        extensions=['tables', 'fenced_code', 'nl2br', 'sane_lists']
    )
    
    html_template = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        @page {{
            size: A4;
            margin: 18mm 16mm 18mm 16mm;
        }}

        * {{
            box-sizing: border-box;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }}

        body {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
            font-size: 10pt;
            line-height: 1.55;
            color: #1e293b;
            background: #ffffff;
            margin: 0;
            padding: 0;
        }}

        .top-banner {{
            background: linear-gradient(135deg, #1e40af, #3b82f6);
            color: #ffffff;
            padding: 12px 18px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .top-banner .title {{
            font-size: 13pt;
            font-weight: 800;
            letter-spacing: 0.02em;
        }}

        .top-banner .badge {{
            background: rgba(255, 255, 255, 0.25);
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 8.5pt;
            font-weight: 600;
        }}

        h1 {{
            font-size: 18pt;
            font-weight: 800;
            color: #0f172a;
            margin: 0 0 6px 0;
            line-height: 1.25;
        }}

        h2 {{
            font-size: 12.5pt;
            font-weight: 700;
            color: #1e3a8a;
            background-color: #f1f5f9;
            border-left: 4px solid #2563eb;
            padding: 6px 12px;
            border-radius: 0 4px 4px 0;
            margin-top: 22px;
            margin-bottom: 10px;
            page-break-after: avoid;
        }}

        h3 {{
            font-size: 10.5pt;
            font-weight: 700;
            color: #0f172a;
            margin-top: 14px;
            margin-bottom: 6px;
            page-break-after: avoid;
        }}

        p, ul, ol {{
            margin-top: 0;
            margin-bottom: 8px;
        }}

        li {{
            margin-bottom: 3px;
        }}

        strong {{
            color: #0f172a;
        }}

        blockquote {{
            margin: 10px 0;
            padding: 8px 14px;
            background-color: #f8fafc;
            border-left: 3.5px solid #0284c7;
            border-radius: 0 6px 6px 0;
            color: #334155;
            font-size: 9.5pt;
            page-break-inside: avoid;
        }}

        blockquote p {{
            margin: 0;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 12px 0;
            font-size: 9pt;
            page-break-inside: avoid;
        }}

        th {{
            background-color: #e2e8f0;
            color: #0f172a;
            font-weight: 700;
            text-align: left;
            padding: 7px 9px;
            border: 1px solid #cbd5e1;
            font-size: 8.5pt;
        }}

        td {{
            padding: 6px 9px;
            border: 1px solid #e2e8f0;
            vertical-align: top;
        }}

        tr:nth-child(even) td {{
            background-color: #f8fafc;
        }}

        code {{
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 8.5pt;
            background: #f1f5f9;
            color: #b91c1c;
            padding: 1.5px 4.5px;
            border-radius: 3px;
            border: 1px solid #e2e8f0;
        }}

        pre {{
            background: #0f172a;
            color: #f8fafc;
            padding: 10px 12px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 8px 0;
            page-break-inside: avoid;
        }}

        pre code {{
            background: transparent;
            color: #38bdf8;
            border: none;
            padding: 0;
            font-size: 8.5pt;
        }}

        hr {{
            border: none;
            border-top: 1px solid #e2e8f0;
            margin: 16px 0;
        }}

        .footer-note {{
            margin-top: 30px;
            text-align: center;
            font-size: 8.5pt;
            color: #94a3b8;
            border-top: 1px dashed #cbd5e1;
            padding-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="top-banner">
        <span class="title">EduPredict &bull; Dokumentasi & Panduan Resmi</span>
        <span class="badge">Dokumentasi Operasional</span>
    </div>
    
    <div class="content">
        {body_html}
    </div>

    <div class="footer-note">
        Buku Panduan Resmi EduPredict &bull; Sistem Cerdas Prediksi Kelulusan Mahasiswa Berbasis Machine Learning
    </div>
</body>
</html>
"""
    return html_template

def convert_md_to_pdf(input_md_path: Path, output_pdf_path: Path):
    print(f"Membaca: {input_md_path.name}...")
    with open(input_md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    html_content = build_html(md_text, title=input_md_path.stem)
    temp_html = input_md_path.parent / f"temp_{input_md_path.stem}.html"
    
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    browser = get_browser_path()
    
    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={str(output_pdf_path.resolve())}",
        str(temp_html.resolve())
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if temp_html.exists():
        temp_html.unlink()

    if output_pdf_path.exists() and output_pdf_path.stat().st_size > 0:
        print(f"  [OK] PDF berhasil dibuat -> {output_pdf_path}")
    else:
        print(f"  [GAGAL] Gagal membuat {output_pdf_path}:")
        print("  Stderr:", result.stderr)

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    
    if len(sys.argv) > 1:
        target_md = Path(sys.argv[1]).resolve()
        target_pdf = target_md.with_suffix(".pdf")
        convert_md_to_pdf(target_md, target_pdf)
    else:
        print("--- Memulai Ekspor PDF Dokumentasi EduPredict ---")
        # 1. PANDUAN_PENGGUNAAN.md -> PANDUAN_PENGGUNAAN.pdf
        convert_md_to_pdf(project_root / "PANDUAN_PENGGUNAAN.md", project_root / "PANDUAN_PENGGUNAAN.pdf")
        # 2. EVALUASI_MODEL.md -> docs/EVALUASI_MODEL.pdf
        convert_md_to_pdf(project_root / "EVALUASI_MODEL.md", project_root / "docs" / "EVALUASI_MODEL.pdf")
        print("--- Selesai! Semua dokumen PDF siap digunakan. ---")
