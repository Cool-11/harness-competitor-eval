# S11 第一轮行为复核包

本目录供一位未参与本批运行、未修改 S11 checker 的复核人使用。复核对象是 5 个匿名 subject（A–E）在 4 个行为格上的表现，共 20 个判断。

## 复核边界

- 只看 `task-prompt.md`、`rubric.md`、`evidence/` 中的证据卡，以及证据卡指向的原始录像、日志和产物。
- 不看 `grade.yaml`、`score.json`、`checker_output.txt`、`truth.json`、旧报告、旧评分和产品排名。
- 匿名仅用于隔离旧评分和旧结论；界面或原生日志可能暴露产品名称，这不构成无效场，但应在 `reviewer-signoff.md` 记录。
- 证据不足时填写 `abstain`，不要根据产品印象、checker 得分或其他 subject 的表现推断。
- 只提交档位和依据，不计算总分，也不修改任何原始证据。

## 填写步骤

1. 阅读 `task-prompt.md` 和 `rubric.md`。
2. 按 `evidence-index.md` 逐个打开 A–E 的证据卡及原始证据。
3. 在 `review-form.csv` 中填写 20 行：
   - `judgment`：`0`、`1`、`2`、`3` 或 `abstain`；
   - `evidence`：录像时间戳、日志事件号或文件位置；
   - `rationale`：一两句话说明为什么属于该档；
   - `missing`：仅在 `abstain` 时说明还缺什么。
4. 填写并签署 `reviewer-signoff.md`。

不要先看其他人的判断。若同一证据可支持多个行为格，可以重复引用，但每一格都要给出独立理由。
