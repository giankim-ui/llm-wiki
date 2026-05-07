/**
 * Claude Code PreToolUse hook — plan.md 자동 백업
 *
 * plan.md 덮어쓰기 시: 기존 파일을 아래 경로로 백업 후 쓰기 허용
 *   ~/!claudeProject/archive/{project_name}/plan-v{N}.md
 *
 * 그 외 기존 파일 덮어쓰기 시: 차단 (기존 동작 유지)
 */

const fs   = require('fs');
const path = require('path');
const os   = require('os');

let raw = '';
process.stdin.on('data', chunk => raw += chunk);
process.stdin.on('end', () => {
  let input;
  try {
    input = JSON.parse(raw);
  } catch (e) {
    process.stdout.write(JSON.stringify({ continue: true }));
    return;
  }

  const filePath = input.tool_input && input.tool_input.file_path;
  if (!filePath) {
    process.stdout.write(JSON.stringify({ continue: true }));
    return;
  }

  // 파일이 존재하지 않으면 그냥 허용
  if (!fs.existsSync(filePath)) {
    process.stdout.write(JSON.stringify({ continue: true }));
    return;
  }

  const basename = path.basename(filePath);

  // ── plan.md 전용: 백업 후 허용 ──────────────────────────────────────
  if (basename === 'plan.md') {
    const projectName = path.basename(path.dirname(filePath));
    const archiveDir  = path.join(os.homedir(), '!claudeProject', 'archive', projectName);

    try {
      fs.mkdirSync(archiveDir, { recursive: true });

      // 충돌 없는 다음 버전 번호 탐색
      let v = 1;
      while (fs.existsSync(path.join(archiveDir, `plan-v${v}.md`))) v++;

      const dest = path.join(archiveDir, `plan-v${v}.md`);
      fs.copyFileSync(filePath, dest);

      // 백업 성공 — 쓰기 허용 (stopReason은 continue:false 전용이므로 stderr 사용)
      process.stderr.write(`[plan.md 백업 완료] ${dest}\n`);
      process.stdout.write(JSON.stringify({ continue: true }));
    } catch (err) {
      process.stdout.write(JSON.stringify({
        continue: false,
        stopReason: `[plan.md 백업 실패] ${err.message}\n백업 후 덮어쓰기를 진행할 수 없습니다. 수동으로 백업하거나 archive 경로를 확인하세요.`
      }));
    }
    return;
  }

  // ── 그 외 기존 파일: 덮어쓰기 차단 (기존 동작) ──────────────────────
  process.stdout.write(JSON.stringify({
    continue: false,
    stopReason: `[덮어쓰기 차단] 파일이 이미 존재합니다: ${filePath}\n반드시 사용자에게 먼저 확인을 받은 후 다시 시도하십시오.`
  }));
});
