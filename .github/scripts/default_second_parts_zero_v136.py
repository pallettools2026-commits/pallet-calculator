from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

replacements = {
    '["Поперечный настил 2",0,22,98,"PW"]': '["Поперечный настил 2",0,22,98,"PW"]',
    '["Лыжа 2",2,22,98,1200]': '["Лыжа 2",0,22,98,1200]',
    '["Шашка 2",3,75,100,98]': '["Шашка 2",0,75,100,98]',
}

for old, new in replacements.items():
    if old == new:
        if old not in text:
            raise SystemExit(f'default marker not found: {old}')
        continue
    if old not in text:
        # Allow idempotent reruns.
        if new in text:
            continue
        raise SystemExit(f'default marker not found: {old}')
    text = text.replace(old, new, 1)

path.write_text(text, encoding='utf-8')
