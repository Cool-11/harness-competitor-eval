#!/usr/bin/env bash
# 环境恢复脚本（评测结束后跑这一条，把三款产品恢复到你原来的状态）
#
# 用法：  bash scripts/restore_env.sh
#
# 作用：把 _backup 下的技能目录原样移回个人目录，并还原 Codex 的 config.toml。
# 幂等：重复运行安全（已还原的会跳过）。

set -uo pipefail

# --- 路径 ---
# 从脚本自身位置推导仓库根，避免硬编码绝对路径（2026-10-16 仓库已迁至
# F:/for-project-new/harness-competitor-eval/；用推导方式后，再搬目录也不会失效）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/../runs/baseline" && pwd)"
BACKUP="$BASE_DIR/_backup"

WB_SRC="C:/Users/25634/.workbuddy/skills"
DSH_SRC="C:/Users/25634/.agents/skills"
CDX_SRC="C:/Users/25634/.codex/skills"
CDX_CFG="C:/Users/25634/.codex/config.toml"

echo "=== 环境恢复开始 ==="

restore_skills() {
  local name="$1" src="$2" bak="$3"
  if [ -d "$bak" ] && [ -n "$(ls -A "$bak" 2>/dev/null)" ]; then
    mkdir -p "$src"
    # 逐个移回，避免覆盖冲突
    for d in "$bak"/*/; do
      [ -e "$d" ] || continue
      mv -f "$d" "$src"/ 2>/dev/null && echo "  恢复: $(basename "$d")"
    done
    echo "[$name] 已恢复 -> $src （剩余未还原: $(ls -A "$bak" 2>/dev/null | wc -l)）"
  else
    echo "[$name] 备份为空，跳过（可能早已恢复）"
  fi
}

restore_skills "Workbuddy" "$WB_SRC"  "$BACKUP/workbuddy-skills"
restore_skills "DSH"       "$DSH_SRC" "$BACKUP/dsh-agents-skills"
restore_skills "Codex"     "$CDX_SRC" "$BACKUP/codex-skills"

# Codex config 还原
BAKCFG=$(ls -1t "$BACKUP/codex/"config.toml.*.bak 2>/dev/null | head -1)
if [ -n "$BAKCFG" ]; then
  cp -f "$BAKCFG" "$CDX_CFG" && echo "[Codex] config.toml 已还原 <- $BAKCFG"
  echo "        还原后 sha256: $(sha256sum "$CDX_CFG" | cut -d' ' -f1)"
else
  echo "[Codex] 未找到 config.toml 备份，跳过"
fi

echo "=== 恢复完成，请到各产品界面确认技能已回来 ==="
