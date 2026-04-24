#!/bin/bash
# Auto-sync plans to GitHub so ultraplan cloud sessions can access them
FILE_PATH="${CLAUDE_TOOL_INPUT_FILE_PATH:-${CLAUDE_TOOL_INPUT_file_path:-}}"
[[ "$FILE_PATH" != *".claude/plans/"* ]] && exit 0

cd "$HOME" || exit 0

# Re-resolve CLAUDE.md symlink if it exists (picks up iCloud changes)
if [ -L ".claude/CLAUDE.md" ]; then
    TARGET=$(readlink ".claude/CLAUDE.md")
    if [ -f "$TARGET" ]; then
        HASH=$(git hash-object -w "$TARGET")
        git update-index --cacheinfo 100644,"$HASH",".claude/CLAUDE.md" 2>/dev/null
    fi
fi

git add .claude/plans/*.md 2>/dev/null
git diff --cached --quiet && exit 0
git commit -m "sync: plan update $(date +%H:%M)" --quiet 2>/dev/null
git push --quiet 2>/dev/null &
exit 0
