from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from dm_bot.runtime.health import build_health_snapshot
from dm_bot.runtime.control_service import RuntimeControlService


PANEL_HTML = """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>Runtime Control Panel</title>
  <style>
    body { font-family: Segoe UI, sans-serif; margin: 24px; background: #101318; color: #e7edf3; }
    h1, h2 { margin: 0 0 12px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 20px; }
    .card { background: #18202a; border-radius: 10px; padding: 14px; border: 1px solid #243140; }
    .ok { color: #52d273; }
    .bad { color: #ff7979; }
    .warn { color: #ffcf5a; }
    button { margin: 4px 8px 4px 0; padding: 8px 12px; background: #2a6ef0; color: white; border: 0; border-radius: 8px; cursor: pointer; }
    button:hover { background: #3a7cf7; }
    pre { white-space: pre-wrap; background: #0e141b; padding: 12px; border-radius: 8px; min-height: 80px; }
  </style>
</head>
<body>
  <h1>Runtime Control Panel</h1>
  <p>自动轮询本地状态；执行动作后会刷新最新结果。</p>
  <div id="overview" class="grid"></div>
  <h2>操作</h2>
  <div id="actions"></div>
  <h2>最近结果</h2>
  <pre id="results">加载中…</pre>
  <h2>日志摘要</h2>
  <pre id="logs">加载中…</pre>
<script>
const actions = [
  ["start-bot", "启动 Bot"],
  ["restart-bot", "重启 Bot"],
  ["stop-bot", "停止 Bot"],
  ["start-api", "启动 API"],
  ["restart-api", "重启 API"],
  ["stop-api", "停止 API"],
  ["restart-system", "重启全系统"],
  ["sync-commands", "同步命令"],
  ["smoke-check", "运行 Smoke Check"],
];

function renderActions() {
  const box = document.getElementById("actions");
  box.innerHTML = "";
  for (const [name, label] of actions) {
    const btn = document.createElement("button");
    btn.textContent = label;
    btn.onclick = async () => {
      const resp = await fetch(`/control-panel/actions/${name}`, { method: "POST" });
      const data = await resp.json();
      document.getElementById("results").textContent = JSON.stringify(data, null, 2);
      await refresh();
    };
    box.appendChild(btn);
  }
}

function statusClass(value) {
  if (value === true || value === "healthy") return "ok";
  if (value === false || value === "down") return "bad";
  return "warn";
}

async function refresh() {
  const resp = await fetch("/control-panel/state");
  const data = await resp.json();
  const cards = [
    ["Bot", `${data.bot.running ? "运行中" : "未运行"} / ${data.bot.healthy ? "就绪" : "未就绪"}`, data.bot.healthy],
    ["API", `${data.api.running ? "运行中" : "未运行"} / ${data.api.healthy ? "可达" : "不可达"}`, data.api.healthy],
    ["Router", `${data.models.router_model} / ${data.models.router_available ? "可用" : "缺失"}`, data.models.router_available],
    ["Narrator", `${data.models.narrator_model} / ${data.models.narrator_available ? "可用" : "缺失"}`, data.models.narrator_available],
    ["Discord Sync", `${data.bot.sync_seen ? "已看到" : "未看到"}`, data.bot.sync_seen],
    ["Smoke Check", `${data.smoke_check.summary}`, data.smoke_check.passed],
  ];
  document.getElementById("overview").innerHTML = cards.map(([title, value, status]) => `
    <div class="card">
      <h3>${title}</h3>
      <div class="${statusClass(status)}">${value}</div>
    </div>`).join("");
  document.getElementById("logs").textContent = JSON.stringify(data.logs, null, 2);
}

renderActions();
refresh();
setInterval(refresh, 3000);
</script>
</body>
</html>
"""


def create_app(control_service: RuntimeControlService | None = None) -> FastAPI:
    app = FastAPI(title="dm-bot-runtime")
    control_service = control_service or RuntimeControlService(cwd=Path.cwd())

    @app.get("/health")
    async def health() -> dict[str, object]:
        return build_health_snapshot().model_dump()

    @app.get("/control-panel", response_class=HTMLResponse)
    async def control_panel() -> str:
        return PANEL_HTML

    @app.get("/control-panel/state")
    async def control_panel_state() -> dict[str, object]:
        return control_service.get_state().model_dump()

    @app.post("/control-panel/actions/{action}")
    async def control_panel_action(action: str) -> dict[str, object]:
        action_map = {
            "start-bot": "start_bot",
            "restart-bot": "restart_bot",
            "stop-bot": "stop_bot",
            "start-api": "start_api",
            "restart-api": "restart_api",
            "stop-api": "stop_api",
            "restart-system": "restart_system",
            "sync-commands": "sync_commands",
            "smoke-check": "run_smoke_check",
        }
        method_name = action_map.get(action)
        handler = getattr(control_service, method_name, None) if method_name else None
        if handler is None:
            raise HTTPException(status_code=404, detail="unknown action")
        return handler().model_dump()

    return app
