import os
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import HTMLResponse
from radio import Radio

app = FastAPI(title="Highrise Music Radio")
radio = Radio()
ADMIN_KEY = os.getenv("RADIO_ADMIN_KEY", "")

PAGE = r"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Highrise Music Radio</title>
<style>
body{font-family:system-ui;background:#10131b;color:#f4f5f7;display:grid;place-items:center;min-height:100vh;margin:0}
main{width:min(92vw,560px);background:#1b2130;border:1px solid #30394d;border-radius:22px;padding:26px;box-sizing:border-box}
small{color:#aab5c8}.dot{color:#62dfa3}button{background:#536dfe;color:white;border:0;padding:12px 18px;border-radius:12px;font-weight:700}
audio{width:100%;margin-top:20px}li{padding:7px 0;color:#dce3f0}h1{margin-bottom:4px}
</style></head><body><main><small><span class="dot">●</span> LIVE RADIO</small><h1>Highrise Music Radio</h1>
<p id="track">Loading current track…</p><audio id="player" controls></audio>
<h3>Up next</h3><ol id="queue"></ol><small>Open this page to listen. Playback is delivered as a web stream, not directly into Highrise voice.</small>
</main><script>
let currentId=null;
async function refresh(){
 try{
  const r=await fetch('/api/state');const d=await r.json();
  document.getElementById('track').textContent=d.paused?'Paused':(d.current?.title||'Waiting for a track');
  document.getElementById('queue').innerHTML=d.queue.slice(1,9).map(x=>'<li>'+escapeHtml(x.title)+'</li>').join('');
  if(d.current && d.current.id!==currentId){
    currentId=d.current.id;const p=document.getElementById('player');
    p.src='/api/current-audio';p.play().catch(()=>{});
  }
  if(!d.current){currentId=null;document.getElementById('player').removeAttribute('src');}
  if(d.paused) document.getElementById('player').pause();
 }catch(e){}
}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
refresh();setInterval(refresh,4000);
</script></body></html>"""

@app.get("/", response_class=HTMLResponse)
@app.get("/radio", response_class=HTMLResponse)
async def radio_page():
    return PAGE

@app.get("/health")
async def health():
    return {"ok": True}

@app.get("/api/state")
async def state():
    queue = await radio.queue_snapshot()
    return {"current": queue[0] if queue else None, "queue": queue,
            "paused": await radio.is_paused()}

@app.get("/api/current-audio")
async def current_audio():
    item = await radio.current()
    if not item:
        raise HTTPException(404, "No current track")
    # Redirect browser to the supplied direct audio URL. The source must permit playback.
    from fastapi.responses import RedirectResponse
    return RedirectResponse(item["url"], status_code=307)

def require_admin(key):
    if not ADMIN_KEY or key != ADMIN_KEY:
        raise HTTPException(403, "Invalid admin key")

@app.post("/api/admin/skip")
async def admin_skip(x_admin_key: str = Header(default="")):
    require_admin(x_admin_key); await radio.skip(); return {"ok": True}

@app.post("/api/admin/pause")
async def admin_pause(x_admin_key: str = Header(default="")):
    require_admin(x_admin_key); await radio.set_paused(True); return {"ok": True}

@app.post("/api/admin/resume")
async def admin_resume(x_admin_key: str = Header(default="")):
    require_admin(x_admin_key); await radio.set_paused(False); return {"ok": True}
