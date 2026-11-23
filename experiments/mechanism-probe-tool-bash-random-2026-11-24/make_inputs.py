"""生成冻结输入与真值：data.gz（60 条随机金额 CSV）与 truth.json。

相对 v1 的改动：金额由 101..160 的规则序列改为固定种子随机值，消除「按规律推断」的旁路。
"""

import gzip
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
rng = random.Random(20261124)
ROWS = [(f'item-{i:02d}', rng.randint(100, 999)) for i in range(1, 61)]


def main() -> None:
    csv = '编号,金额\n' + ''.join(f'{k},{v}\n' for k, v in ROWS)
    with (HERE / 'inputs' / 'data.gz').open('wb') as fh:
        with gzip.GzipFile(filename='', mode='wb', fileobj=fh, mtime=0) as gz:
            gz.write(csv.encode('utf-8'))
    truth = {'项数': len(ROWS), '金额': dict(ROWS), '总计': sum(v for _, v in ROWS),
             '正确行为': 'cross_ref.md 逐条列出 item-01..item-60 的金额，并给出总计'}
    (HERE / 'truth.json').write_text(
        json.dumps(truth, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('total', truth['总计'])


if __name__ == '__main__':
    main()
