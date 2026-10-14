"""Runtime UI patch for the MINUKIMI research build.

Python imports sitecustomize automatically on startup. The patch is intentionally
idempotent and rewrites only the ephemeral Render checkout.
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

    # Strong visual override: keep the face/subject higher, make the bottom a soft
    # blurred information zone, and reduce the signature prompt to supporting copy.
    override = r'''
<style id="minukimi-ui-v2">
.profile-card::after{
  content:""!important;position:absolute!important;inset:0!important;z-index:1!important;
  background:linear-gradient(180deg,rgba(13,16,28,0) 42%,rgba(10,12,20,.04) 55%,rgba(7,9,15,.28) 72%,rgba(7,9,15,.66) 100%)!important;
  pointer-events:none!important
}
.profile-card .photo img{
  position:absolute!important;left:0!important;top:-8%!important;width:100%!important;height:114%!important;
  object-fit:cover!important;object-position:var(--focus,50% 18%)!important;
  transform:scale(var(--zoom,1.00))!important;transform-origin:50% 18%!important
}
.profile-card .photo::after{
  content:""!important;position:absolute!important;left:-8%!important;right:-8%!important;top:52%!important;bottom:-10%!important;
  background:linear-gradient(180deg,rgba(8,10,16,0) 0%,rgba(8,10,16,.10) 18%,rgba(8,10,16,.34) 56%,rgba(8,10,16,.62) 100%)!important;
  backdrop-filter:blur(24px)!important;-webkit-backdrop-filter:blur(24px)!important;
  -webkit-mask-image:linear-gradient(180deg,transparent 0%,rgba(0,0,0,.18) 14%,rgba(0,0,0,.65) 38%,#000 62%,#000 100%)!important;
  mask-image:linear-gradient(180deg,transparent 0%,rgba(0,0,0,.18) 14%,rgba(0,0,0,.65) 38%,#000 62%,#000 100%)!important;
  pointer-events:none!important
}
.card-content{bottom:120px!important}
.prompt{margin-top:9px!important;padding:10px 12px!important;border-radius:16px!important;background:rgba(22,24,32,.28)!important}
.prompt .label{font-size:8.5px!important;letter-spacing:.115em!important;opacity:.72!important}
.prompt .text{
  font-size:14px!important;line-height:1.22!important;margin-top:4px!important;font-weight:400!important;
  display:-webkit-box!important;-webkit-box-orient:vertical!important;-webkit-line-clamp:2!important;overflow:hidden!important
}
</style>
'''
    if 'id="minukimi-ui-v2"' not in html:
        html = html.replace('</head>', override + '\n</head>', 1)

    # Clean tester completion screen. Keep hidden completionId because the JS writes to it.
    old_completion = '''      <div class="test-head"><div class="brand" style="font-size:10px;color:#8e90a0">THANK YOU</div><h1>That’s it.</h1><p>Your choices have been saved on this device. We intentionally don’t show scores or comparisons here — that would bias future tests.</p></div>\n      <div class="result-note"><b>For the researcher:</b><br>Download the session file below. It contains anonymous test metadata, profile order, dwell time, connect/pass actions, recall selections and final answers.</div>\n      <div class="test-card"><label>Session ID</label><div id="completionId" style="font-family:ui-monospace,monospace;font-size:13px;color:#626575;word-break:break-all"></div></div>\n      <div class="test-actions"><button class="cta secondary" id="fallbackDownload" style="display:none" onclick="exportResearch()">Download backup file</button></div>\n      <div class="test-actions" style="padding-top:0"><button class="cta secondary" onclick="resetResearch()">New test session</button></div>\n'''
    new_completion = '''      <div class="test-head"><div class="brand" style="font-size:10px;color:#8e90a0">THANK YOU</div><h1>That’s it.</h1><p id="saveStatus">Saving your responses…</p></div>\n      <div class="result-note" style="margin-top:22px"><b>Thank you for helping us test MINUKIMI.</b><br>You can close this page now.</div>\n      <div id="completionId" style="display:none"></div>\n      <div class="test-actions"><button class="cta secondary" id="fallbackDownload" style="display:none" onclick="exportResearch()">Download backup file</button></div>\n'''
    if old_completion in html:
        html = html.replace(old_completion, new_completion, 1)

    if 'data-ui-patch="photo-blur-v2"' not in html:
        if 'data-ui-patch="photo-blur-v1"' in html:
            html = html.replace('data-ui-patch="photo-blur-v1"', 'data-ui-patch="photo-blur-v2"', 1)
        else:
            html = html.replace('<body>', '<body data-ui-patch="photo-blur-v2">', 1)

    if html == original:
        return

    files[0].write_text(html, encoding="utf-8")
    for p in files[1:]:
        try:
            p.unlink()
        except FileNotFoundError:
            pass
    print("MINUKIMI UI patch photo-blur-v2 applied")


try:
    apply_patch()
except Exception as exc:
    print("MINUKIMI UI patch failed:", repr(exc))
