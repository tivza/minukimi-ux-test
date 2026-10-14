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

    override = r'''
<style id="minukimi-ui-v3">
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
.prompt .text{font-size:14px!important;line-height:1.22!important;margin-top:4px!important;font-weight:400!important;display:-webkit-box!important;-webkit-box-orient:vertical!important;-webkit-line-clamp:2!important;overflow:hidden!important}

/* Intro carousel */
.splash .status,.onboard .status{display:none!important}
.splash,.onboard{touch-action:pan-y!important}
.splash .brand{margin-top:8px!important}
.onboard .topbar{padding-top:10px!important}
#on1 .on-card{width:268px!important;padding:20px!important}
#on1 .on-card .big{font-size:28px!important;margin-bottom:12px!important}
#on1 .on-card .quote{font-size:14px!important;line-height:1.42!important;padding:15px!important}
#on1 .meaning-note{margin-top:10px;font-size:11px;line-height:1.45;color:#7d8090;text-align:center}
</style>
'''
    if 'id="minukimi-ui-v3"' not in html:
        html = html.replace('</head>', override + '\n</head>', 1)

    # First intro: product-facing, not research-facing, and move forward into onboarding.
    html = html.replace(
        '<p>A 20-profile UX test for one better question and one more intentional gesture.</p>',
        '<p>Meet people a little more intentionally — with one revealing question and one deliberate way to connect.</p>',
        1,
    )
    html = html.replace(
        '<button class="cta" style="width:100%" onclick="show(\'intake\')">Start the test</button>',
        '<button class="cta" style="width:100%" onclick="show(\'on1\')">Next</button>',
        1,
    )

    # Second intro: make the meaning of “In my head, I’m…” unmistakable.
    html = html.replace(
        '<div class="tiny">The part profiles usually miss</div><div class="big">In my head, I’m…</div><div class="quote">“Much braver than my actual life suggests. I should probably live near the sea and kiss people first.”</div>',
        '<div class="tiny">A glimpse beyond the facts</div><div class="big">In my head, I’m…</div><div class="quote">“already living near the sea, wearing linen and kissing first.”</div><div class="meaning-note">Finish the sentence with the version of you that feels most like you — even if real life has not caught up yet.</div>',
        1,
    )
    html = html.replace(
        '<h2>One question that can tell you more.</h2><p>Not a résumé. Not a personality test. Just one small place to show something real that a normal profile rarely catches.</p>',
        '<h2>Show a version of you facts can’t.</h2><p>Not your job title. Not a fantasy character. A small truth about the life, mood or version of yourself you feel drawn toward — something another person can actually connect with.</p>',
        1,
    )

    # Third intro leads into the research intake. Intake then starts discovery.
    html = html.replace(
        '<button class="cta" style="width:100%" onclick="startResearch();show(\'discover\');loadCard()">Try the 20-profile test</button>',
        '<button class="cta" style="width:100%" onclick="show(\'intake\')">Start</button>',
        1,
    )
    html = html.replace(
        '<div class="topbar"><button class="icon-btn" onclick="show(\'splash\')">←</button><div class="brand">MINUKIMI</div><span style="width:40px"></span></div>\n      <div class="intake-wrap">',
        '<div class="topbar"><button class="icon-btn" onclick="show(\'on2\')">←</button><div class="brand">MINUKIMI</div><span style="width:40px"></span></div>\n      <div class="intake-wrap">',
        1,
    )
    html = html.replace(
        "document.getElementById('intakeError').textContent='';saveResearchDraft();show('on1');",
        "document.getElementById('intakeError').textContent='';saveResearchDraft();startResearch();show('discover');loadCard();",
        1,
    )

    # Swipe intro screens horizontally: splash -> on1 -> on2 -> intake, and back.
    swipe_script = r'''
<script id="minukimi-intro-swipe">
(function(){
  const next={splash:'on1',on1:'on2',on2:'intake'};
  const prev={on1:'splash',on2:'on1',intake:'on2'};
  ['splash','on1','on2'].forEach(id=>{
    const el=document.getElementById(id); if(!el) return;
    let sx=0,sy=0,tracking=false;
    el.addEventListener('pointerdown',e=>{sx=e.clientX;sy=e.clientY;tracking=true});
    el.addEventListener('pointerup',e=>{
      if(!tracking)return;tracking=false;
      const dx=e.clientX-sx,dy=e.clientY-sy;
      if(Math.abs(dx)<55||Math.abs(dx)<Math.abs(dy)*1.2)return;
      if(dx<0&&next[id])show(next[id]);
      if(dx>0&&prev[id])show(prev[id]);
    });
    el.addEventListener('pointercancel',()=>tracking=false);
  });
})();
</script>
'''
    if 'id="minukimi-intro-swipe"' not in html:
        html = html.replace('</body>', swipe_script + '\n</body>', 1)

    # Clean tester completion screen. Keep hidden completionId because JS writes to it.
    old_completion = '''      <div class="test-head"><div class="brand" style="font-size:10px;color:#8e90a0">THANK YOU</div><h1>That’s it.</h1><p>Your choices have been saved on this device. We intentionally don’t show scores or comparisons here — that would bias future tests.</p></div>\n      <div class="result-note"><b>For the researcher:</b><br>Download the session file below. It contains anonymous test metadata, profile order, dwell time, connect/pass actions, recall selections and final answers.</div>\n      <div class="test-card"><label>Session ID</label><div id="completionId" style="font-family:ui-monospace,monospace;font-size:13px;color:#626575;word-break:break-all"></div></div>\n      <div class="test-actions"><button class="cta secondary" id="fallbackDownload" style="display:none" onclick="exportResearch()">Download backup file</button></div>\n      <div class="test-actions" style="padding-top:0"><button class="cta secondary" onclick="resetResearch()">New test session</button></div>\n'''
    new_completion = '''      <div class="test-head"><div class="brand" style="font-size:10px;color:#8e90a0">THANK YOU</div><h1>That’s it.</h1><p id="saveStatus">Saving your responses…</p></div>\n      <div class="result-note" style="margin-top:22px"><b>Thank you for helping us test MINUKIMI.</b><br>You can close this page now.</div>\n      <div id="completionId" style="display:none"></div>\n      <div class="test-actions"><button class="cta secondary" id="fallbackDownload" style="display:none" onclick="exportResearch()">Download backup file</button></div>\n'''
    if old_completion in html:
        html = html.replace(old_completion, new_completion, 1)

    if 'data-ui-patch="intro-v3"' not in html:
        if 'data-ui-patch="photo-blur-v2"' in html:
            html = html.replace('data-ui-patch="photo-blur-v2"', 'data-ui-patch="intro-v3"', 1)
        elif 'data-ui-patch="photo-blur-v1"' in html:
            html = html.replace('data-ui-patch="photo-blur-v1"', 'data-ui-patch="intro-v3"', 1)
        else:
            html = html.replace('<body>', '<body data-ui-patch="intro-v3">', 1)

    if html == original:
        return

    files[0].write_text(html, encoding="utf-8")
    for p in files[1:]:
        try:
            p.unlink()
        except FileNotFoundError:
            pass
    print("MINUKIMI UI patch intro-v3 applied")


try:
    apply_patch()
except Exception as exc:
    print("MINUKIMI UI patch failed:", repr(exc))
