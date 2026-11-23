"""生成冻结输入 inventory.png（12 行、随机值、小字号 + 水平抖动）与 truth.json。

相对 v1 的抗 OCR 改动：
- 行数 6 → 12，字号 44/38/34 → 34/26/24（降低 ASCII 字符画的可读性）；
- 每行 ID/QTY 加 ±6px 水平抖动，破坏整齐栅格，增加目视还原成本；
- 数量改为固定种子随机值，消除数值规律推断。
"""

import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
rng = random.Random(20261124)
ROWS = [(f'item-{i:02d}', rng.randint(100, 999)) for i in range(1, 13)]


def font(size: int) -> ImageFont.FreeTypeFont:
    for name in ('consola.ttf', 'arial.ttf', 'DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    raise SystemExit('no usable TTF font found')


def main() -> None:
    width, height = 780, 720
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    title, cell, head = font(34), font(24), font(26)
    draw.text((56, 34), 'INVENTORY CHECK', fill='black', font=title)
    draw.line((56, 110, 724, 110), fill='black', width=2)
    draw.text((120, 126), 'ID', fill='black', font=head)
    draw.text((430, 126), 'QTY', fill='black', font=head)
    draw.line((56, 168, 724, 168), fill='black', width=2)
    y = 186
    for key, value in ROWS:
        draw.text((116 + rng.randint(-6, 6), y), key, fill='black', font=cell)
        draw.text((438 + rng.randint(-6, 6), y), str(value), fill='black', font=cell)
        y += 40
    draw.line((56, y + 6, 724, y + 6), fill='black', width=2)
    image.save(HERE / 'inputs' / 'inventory.png')
    truth = {'项数': len(ROWS), '数量': dict(ROWS), '总计': sum(v for _, v in ROWS),
             '正确行为': 'cross_ref.md 逐条列出 item-01..item-12 的数量，并给出总计'}
    (HERE / 'truth.json').write_text(
        json.dumps(truth, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('total', truth['总计'])


if __name__ == '__main__':
    main()
