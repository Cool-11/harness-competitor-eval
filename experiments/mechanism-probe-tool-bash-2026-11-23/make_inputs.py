"""生成冻结输入与真值：data.gz（60 条 CSV）与 truth.json。"""

import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = [(f'item-{i:02d}', 100 + i) for i in range(1, 61)]


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
