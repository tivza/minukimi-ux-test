"""Runtime UI hotfix for the MINUKIMI research build.

Python imports sitecustomize automatically on startup. We use that hook so the
Render build/runtime can patch the assembled tester shell without rewriting the
large chunk files in GitHub. The patch is intentionally idempotent.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARTS = ROOT / "index_parts"


def apply_patch():
    files = sorted(PARTS.glob("index.part.*"))
    if not files:
        return

    html = b"".join(p.read_bytes() for p in files).decode("utf-8")
    original = html

    old_css = '''.profile-card::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(16,20,38,0) 36%,rgba(14,16,26,.08) 56%,rgba(12,14,20,.68) 100%);pointer-events:none}\n.profile-card .photo{position:absolute;inset:0;overflow:hidden;background:#d9dbe6}.profile-card .photo img{width:100%;height:100%;display:block;object-fit:cover;object-position:var(--focus,50% 24%);transform:scale(var(--zoom,1.02));transform-origin:var(--origin,50% 26%);transition:transform .35s ease}.profile-card .photo::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(255,255,255,.02) 0%,rgba(255,255,255,0) 32%,rgba(10,12,18,.04) 52%,rgba(8,10,16,.44) 78%,rgba(8,10,16,.70) 100%);pointer-events:none}\n'''

    new_css = '''.profile-card::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(16,20,38,0) 45%,rgba(14,16,26,.06) 60%,rgba(10,12,18,.54) 100%);pointer-events:none;z-index:1}\n.profile-card .photo{position:absolute;inset:0;overflow:hidden;background:#d9dbe6}.profile-card .photo img{position:absolute;left:0;top:-3%;width:100%;height:106%;display:block;object-fit:cover;object-position:var(--focus,50% 24%);transform:scale(var(--zoom,1.02));transform-origin:var(--origin,50% 24%);transition:transform .35s ease}.profile-card .photo::after{content:"";position:absolute;left:-5%;right:-5%;top:46%;bottom:-8%;background:linear-gradient(180deg,rgba(10,12,18,.02),rgba(8,10,16,.18) 38%,rgba(8,10,16,.52) 100%);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);-webkit-mask-image:linear-gradient(180deg,transparent 0%,rgba(0,0,0,.28) 18%,#000 46%,#000 100%);mask-image:linear-gradient(180deg,transparent 0%,rgba(0,0,0,.28) 18%,#000 46%,#000 100%);pointer-events:none}\n'''

    if old_css in html:
        html = html.replace(old_css, new_css, 1)

    old_completion = '''      <div class="test-head"><div class="brand" style="font-size:10px;color:#8e90a0">THANK YOU</div><h1>That’s it.</h1><p>Your choices have been saved on this device. We intentionally don’t show scores or comparisons here — that would bias future tests.</p></div>\n      <div class="result-note"><b>For the researcher:</b><br>Download the session file below. It contains anonymous test metadata, profile order, dwell time, connect/pass actions, recall selections and final answers.</div>\n      <div class="test-card"><label>Session ID</label><div id="completionId" style="font-family:ui-monospace,monospace;font-size:13px;color:#626575;word-break:break-all"></div></div>\n      <div class="test-actions"><button class="cta secondary" id="fallbackDownload" style="display:none" onclick="exportResearch()">Download backup file</button></div>\n      <div class="test-actions" style="padding-top:0"><button class="cta secondary" onclick="resetResearch()">New test session</button></div>\n'''

    new_completion = '''      <div class="test-head"><div class="brand" style="font-size:10px;color:#8e90a0">THANK YOU</div><h1>That’s it.</h1><p id="saveStatus">Saving your responses…</p></div>\n      <div class="result-note" style="margin-top:22px"><b>Thank you for helping us test MINUKIMI.</b><br>You can close this page now.</div>\n      <div id="completionId" style="display:none"></div>\n      <div class="test-actions"><button class="cta secondary" id="fallbackDownload" style="display:none" onclick="exportResearch()">Download backup file</button></div>\n'''

    if old_completion in html:
        html = html.replace(old_completion, new_completion, 1)

    # Add a tiny marker so our public smoke test can prove the patched shell is live.
    if 'data-ui-patch="photo-blur-v1"' not in html:
        html = html.replace('<body>', '<body data-ui-patch="photo-blur-v1">', 1)

    if html == original:
        return

    # Collapse to one runtime part. This only changes the ephemeral Render checkout;
    # the source chunk files in GitHub remain untouched.
    files[0].write_text(html, encoding="utf-8")
    for p in files[1:]:
        try:
            p.unlink()
        except FileNotFoundError:
            pass
    print("MINUKIMI UI patch photo-blur-v1 applied")


try:
    apply_patch()
except Exception as exc:
    print("MINUKIMI UI patch failed:", repr(exc))
