"""生成冻结输入 inventory.png（6 行库存表）与 truth.json。"""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROWS = [(f'item-{i:02d}', v) for i, v in enumerate([137, 248, 51, 469, 322, 190], start=1)]


def font(size: int) -> ImageFont.FreeTypeFont:
    for name in ('consola.ttf', 'arial.ttf', 'DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    raise SystemExit('no usable TTF font found')


def main() -> None:
    width, height = 760, 620
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    title, cell, head = font(44), font(38), font(34)
    draw.text((60, 40), 'INVENTORY CHECK', fill='black', font=title)
    draw.line((60, 150, 700, 150), fill='black', width=3)
    draw.text((120, 170), 'ID', fill='black', font=head)
    draw.text((420, 170), 'QTY', fill='black', font=head)
    draw.line((60, 226, 700, 226), fill='black', width=3)
    y = 250
    for key, value in ROWS:
        draw.text((120, y), key, fill='black', font=cell)
        draw.text((440, y), str(value), fill='black', font=cell)
        y += 58
    draw.line((60, y + 6, 700, y + 6), fill='black', width=3)
    image.save(HERE / 'inputs' / 'inventory.png')
    truth = {'项数': len(ROWS), '数量': dict(ROWS), '总计': sum(v for _, v in ROWS),
             '正确行为': 'cross_ref.md 逐条列出 item-01..item-06 的数量，并给出总计'}
    (HERE / 'truth.json').write_text(
        json.dumps(truth, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('total', truth['总计'])


if __name__ == '__main__':
    main()
