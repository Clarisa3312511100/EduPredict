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

def build_html(markdown_content: str, title: str = "Dokumentasi Tugas Besar") -> str:
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
            margin: 20mm 18mm 20mm 18mm;
            @bottom-center {{
                content: "EduPredict - Tugas Besar";
                font-size: 8pt;
                color: #6b7280;
            }}
        }}

        * {{
            box-sizing: border-box;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }}

        body {{
            font-family: Arial, "Helvetica Neue", Helvetica, "Segoe UI", sans-serif;
            font-size: 9.5pt;
            line-height: 1.5;
            color: #1f2937;
            background: #ffffff;
            margin: 0;
            padding: 0;
        }}

        .header-meta {{
            font-size: 8.5pt;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 1px solid #e5e7eb;
            padding-bottom: 4px;
            margin-bottom: 16px;
        }}

        h1 {{
            font-size: 16pt;
            font-weight: 700;
            color: #111827;
            margin: 0 0 4px 0;
            line-height: 1.3;
        }}

        h2 {{
            font-size: 11.5pt;
            font-weight: 700;
            color: #111827;
            border-bottom: 1px solid #d1d5db;
            padding-bottom: 4px;
            margin-top: 20px;
            margin-bottom: 10px;
            page-break-after: avoid;
        }}

        h3 {{
            font-size: 10pt;
            font-weight: 700;
            color: #1f2937;
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
            color: #111827;
        }}

        blockquote {{
            margin: 8px 0;
            padding: 6px 12px;
            background-color: #f9fafb;
            border-left: 3px solid #9ca3af;
            color: #374151;
            font-size: 9pt;
            page-break-inside: avoid;
        }}

        blockquote p {{
            margin: 0;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0 14px 0;
            font-size: 8.5pt;
            page-break-inside: avoid;
        }}

        th {{
            background-color: #f3f4f6;
            color: #111827;
            font-weight: 700;
            text-align: left;
            padding: 6px 8px;
            border: 1px solid #d1d5db;
        }}

        td {{
            padding: 5px 8px;
            border: 1px solid #e5e7eb;
            vertical-align: top;
        }}

        tr:nth-child(even) td {{
            background-color: #fafafa;
        }}

        code {{
            font-family: Consolas, "Courier New", monospace;
            font-size: 8.5pt;
            background: #f3f4f6;
            color: #111827;
            padding: 1px 4px;
            border-radius: 2px;
            border: 1px solid #e5e7eb;
        }}

        pre {{
            background: #f9fafb;
            color: #1f2937;
            border: 1px solid #e5e7eb;
            padding: 8px 10px;
            border-radius: 4px;
            overflow-x: auto;
            margin: 8px 0;
            page-break-inside: avoid;
        }}

        pre code {{
            background: transparent;
            color: #111827;
            border: none;
            padding: 0;
            font-size: 8.5pt;
        }}

        hr {{
            border: none;
            border-top: 1px solid #e5e7eb;
            margin: 16px 0;
        }}

        .footer-note {{
            margin-top: 24px;
            text-align: center;
            font-size: 8pt;
            color: #9ca3af;
            border-top: 1px solid #e5e7eb;
            padding-top: 8px;
        }}
    </style>
</head>
<body>
    <div class="header-meta">
        Dokumen Teknis &bull; Tugas Besar Sistem Cerdas Prediksi Kelulusan Mahasiswa
    </div>
    
    <div class="content">
        {body_html}
    </div>

    <div class="footer-note">
        EduPredict &bull; Laporan dan Panduan Penggunaan Sistem Tugas Besar
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
        print("--- Memulai Ekspor PDF (Format Standar Dokumen Laporan) ---")
        # 1. PANDUAN_PENGGUNAAN.md -> PANDUAN_PENGGUNAAN.pdf
        convert_md_to_pdf(project_root / "PANDUAN_PENGGUNAAN.md", project_root / "PANDUAN_PENGGUNAAN.pdf")
        # 2. EVALUASI_MODEL.md -> docs/EVALUASI_MODEL.pdf
        convert_md_to_pdf(project_root / "EVALUASI_MODEL.md", project_root / "docs" / "EVALUASI_MODEL.pdf")
        print("--- Selesai! Dokumen PDF berhasil diperbarui. ---")
