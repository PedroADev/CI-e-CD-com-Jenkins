import re
import os
import base64
import markdown
from playwright.sync_api import sync_playwright

WORKSPACE = os.path.abspath(os.path.dirname(__file__))
MD_PATH = os.path.join(WORKSPACE, "RELATORIO_A2.md")
PDF_PATH = os.path.join(WORKSPACE, "RELATORIO_A2.pdf")
HTML_PATH = os.path.join(WORKSPACE, "relatorio_preview.html")

with open(MD_PATH, "r", encoding="utf-8") as f:
    md_content = f.read()

# Convert markdown to HTML
html_body = markdown.markdown(
    md_content,
    extensions=["extra", "sane_lists", "tables", "admonition"]
)

# Convert image paths to base64
def image_to_base64_url(match):
    img_tag = match.group(0)
    src_match = re.search(r'src="([^"]+)"', img_tag)
    if not src_match:
        return img_tag
    rel_path = src_match.group(1)
    abs_path = os.path.normpath(os.path.join(WORKSPACE, rel_path))
    if os.path.exists(abs_path):
        ext = os.path.splitext(abs_path)[1].lower().replace(".", "")
        mime = "image/png" if ext == "png" else "image/jpeg"
        with open(abs_path, "rb") as img_f:
            b64_data = base64.b64encode(img_f.read()).decode("utf-8")
        is_config = "01_job_configuracao" in rel_path
        extra_class = ' class="config-img"' if is_config else ""
        return f'<img src="data:{mime};base64,{b64_data}" alt="{src_match.group(1)}"{extra_class} />'
    return img_tag

# Group <p><img ...><br /><em>Figura ...</em></p> into <figure class="fig-card">
pattern = re.compile(
    r'<p>\s*(<img\s+[^>]+>)\s*(?:<br\s*/?>)?\s*<em>(Figura\s+\d+:[^<]+)</em>\s*</p>',
    re.DOTALL | re.IGNORECASE
)

def make_figure(match):
    img = match.group(1)
    caption = match.group(2)
    is_config = "01_job_configuracao" in img
    card_class = "fig-card fig-config" if is_config else "fig-card"
    return f'''
<figure class="{card_class}">
  {img}
  <figcaption>{caption}</figcaption>
</figure>
'''

html_body = pattern.sub(make_figure, html_body)

# Replace all remaining img tags with base64 embedded data
html_body = re.sub(r'<img\s+[^>]+>', image_to_base64_url, html_body)

# Wrap Q&A items to avoid awkward page breaks
html_body = re.sub(r'(<li>\s*<p><strong>[^<]+<\/strong>.*?<\/li>)', r'<li class="qa-item">\1</li>', html_body, flags=re.DOTALL)

styled_html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Relatório A2 - Arquitetura CI/CD com Jenkins</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 18mm 16mm 18mm 16mm;
  }}

  * {{
    box-sizing: border-box;
  }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #1e293b;
    line-height: 1.5;
    font-size: 10pt;
    margin: 0;
    padding: 0;
  }}

  h1 {{
    color: #0f172a;
    font-size: 20pt;
    font-weight: 700;
    border-bottom: 2.5px solid #0284c7;
    padding-bottom: 6px;
    margin-top: 0;
    margin-bottom: 10px;
    page-break-after: avoid;
    break-after: avoid;
  }}

  h2 {{
    color: #0369a1;
    font-size: 13.5pt;
    font-weight: 700;
    border-bottom: 1px solid #cbd5e1;
    padding-bottom: 4px;
    margin-top: 20px;
    margin-bottom: 10px;
    page-break-after: avoid;
    break-after: avoid;
  }}

  h3 {{
    color: #0284c7;
    font-size: 11.5pt;
    font-weight: 600;
    margin-top: 14px;
    margin-bottom: 6px;
    page-break-after: avoid;
    break-after: avoid;
  }}

  h4 {{
    color: #334155;
    font-size: 10.5pt;
    font-weight: 600;
    margin-top: 12px;
    margin-bottom: 4px;
    page-break-after: avoid;
    break-after: avoid;
  }}

  p {{
    margin: 5px 0 8px 0;
    text-align: justify;
  }}

  ul, ol {{
    margin: 4px 0 10px 18px;
    padding: 0;
  }}

  li {{
    margin-bottom: 4px;
  }}

  .qa-item {{
    page-break-inside: avoid;
    break-inside: avoid;
    margin-bottom: 8px;
  }}

  strong {{
    color: #0f172a;
  }}

  code {{
    font-family: "Cascadia Code", "Consolas", monospace;
    font-size: 9pt;
    background-color: #f1f5f9;
    padding: 2px 4px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
    color: #b91c1c;
  }}

  pre {{
    background-color: #0f172a;
    color: #f8fafc;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 8.5pt;
    line-height: 1.35;
    page-break-inside: avoid;
    break-inside: avoid;
  }}

  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0 14px 0;
    font-size: 9pt;
    page-break-inside: avoid;
    break-inside: avoid;
  }}

  th, td {{
    border: 1px solid #cbd5e1;
    padding: 6px 8px;
    text-align: left;
    vertical-align: top;
  }}

  th {{
    background-color: #f8fafc;
    color: #0f172a;
    font-weight: 600;
  }}

  tr:nth-child(even) td {{
    background-color: #fbfcfe;
  }}

  blockquote {{
    border-left: 3.5px solid #0284c7;
    background-color: #f0f9ff;
    margin: 8px 0 12px 0;
    padding: 6px 12px;
    border-radius: 0 4px 4px 0;
    color: #0369a1;
    font-size: 9.5pt;
    page-break-inside: avoid;
    break-inside: avoid;
  }}

  blockquote p {{
    margin: 2px 0;
  }}

  hr {{
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 14px 0;
  }}

  .fig-card {{
    margin: 10px auto 14px auto;
    text-align: center;
    page-break-inside: avoid;
    break-inside: avoid;
    display: block;
  }}

  .fig-card img {{
    max-width: 96%;
    max-height: 350px;
    height: auto;
    border: 1px solid #cbd5e1;
    border-radius: 5px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
    display: inline-block;
    object-fit: contain;
  }}

  /* Freestyle config image bounded to a single crisp view */
  .fig-config img {{
    max-height: 440px;
    max-width: 85%;
  }}

  .fig-card figcaption {{
    margin-top: 4px;
    font-size: 9pt;
    color: #64748b;
    font-style: italic;
    page-break-before: avoid;
    break-before: avoid;
    text-align: center;
  }}
</style>
</head>
<body>
{html_body}
</body>
</html>
'''

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(styled_html)

print("HTML preview saved:", HTML_PATH)

# Render to PDF using Playwright with system Chrome
with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page()
    page.goto(f"file:///{HTML_PATH.replace(os.sep, '/')}")
    page.wait_for_load_state("networkidle")
    
    page.pdf(
        path=PDF_PATH,
        format="A4",
        print_background=True,
        prefer_css_page_size=True,
        margin={"top": "16mm", "bottom": "16mm", "left": "14mm", "right": "14mm"},
        display_header_footer=True,
        header_template="<div></div>",
        footer_template="""
        <div style="font-size: 8pt; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; color: #64748b; width: 100%; text-align: right; padding-right: 14mm; box-sizing: border-box;">
          Relatório Exercício A2 &nbsp;|&nbsp; Página <span class="pageNumber"></span> de <span class="totalPages"></span>
        </div>
        """
    )
    browser.close()

print("PDF successfully generated at:", PDF_PATH)
size_mb = os.path.getsize(PDF_PATH) / (1024 * 1024)
print(f"File size: {size_mb:.2f} MB")
