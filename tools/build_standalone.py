"""Собирает index.html + img/ + fonts/ в один файл dist/lobach-marafon.html.

Запуск из корня репозитория:  python3 tools/build_standalone.py
"""
import base64, mimetypes, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
MIME = {".woff2": "font/woff2", ".svg": "image/svg+xml", ".webp": "image/webp"}


def data_uri(path: pathlib.Path) -> str:
    mime = MIME.get(path.suffix) or mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


html = (ROOT / "index.html").read_text(encoding="utf-8")

# 1) шрифты: подставляем fonts.css с вшитыми woff2
css = (ROOT / "fonts" / "fonts.css").read_text(encoding="utf-8")
css = re.sub(r"url\(([^)]+\.woff2)\)", lambda m: f"url({data_uri(ROOT / 'fonts' / m.group(1))})", css)
html = html.replace('<link rel="stylesheet" href="fonts/fonts.css">', f"<style>\n{css}</style>")

# 2) картинки: src="img/..." и href="img/..."
def inline_img(m):
    path = ROOT / m.group(2)
    return f'{m.group(1)}="{data_uri(path)}"' if path.exists() else m.group(0)


html = re.sub(r'(src|href)="(img/[^"]+)"', inline_img, html)

out = ROOT / "dist" / "lobach-marafon.html"
out.write_text(html, encoding="utf-8")
print(f"{out.relative_to(ROOT)}: {out.stat().st_size / 1024:.0f} KB")
