from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARTS = ROOT / "index_parts"


def apply_v10():
    files = sorted(PARTS.glob("index.part.*"))
    if not files:
        return
    html = b"".join(p.read_bytes() for p in files).decode("utf-8")
    if 'data-ui-v10="true"' in html:
        print("MINUKIMI v1.0 signature heart already applied")
        return

    old_left = 'M18 68 C58 69 86 66 108 52 C119 45 122 26 137 26 C149 26 157 36 159 47 C160 55 153 63 140 70'
    old_right = 'M274 68 C234 69 206 66 184 52 C173 45 170 26 155 26 C143 26 135 36 133 47 C132 55 139 63 152 70'

    # Each object is now literally one half of the same heart, with a long emotional tail.
    # At rest the two contact points are 18px apart. Moving each half 9px inward closes
    # both the top cleft and the lower point, so the existing lines themselves form the heart.
    heart_left = 'M8 58 C32 88 68 89 99 73 C114 65 129 64 137 77 C121 63 109 53 105 41 C101 28 108 19 119 18 C127 17 134 21 137 27'
    heart_right = 'M155 27 C158 21 165 17 173 18 C184 19 191 28 187 41 C183 53 171 63 155 77 C163 64 178 65 193 73 C224 89 260 88 284 58'
    html = html.replace(old_left, heart_left).replace(old_right, heart_right)

    html = html.replace('data-ui-v09="true"', 'data-ui-v09="true" data-ui-v10="true"', 1)
    html = html.replace('Bring the lines together', 'Bring the two halves together')
    html = html.replace('Flick either line away', 'Flick either half away')
    html = html.replace('pull the two heart-lines together', 'pull the two halves together')
    html = html.replace('flick either line away', 'flick either half away')
    html = html.replace('bring together to connect / flick away to pass', 'complete the heart to connect / flick a half away to pass')
    html = html.replace("version:'0.9'", "version:'1.0'").replace("research.version='0.9'", "research.version='1.0'")

    css = r'''
<style id="minukimi-signature-heart-v10">
/* The two live strokes ARE the heart. No extra traced heart is drawn on top. */
.heart-trace,.mk-teach-heart,.mk-heart-pulse{display:none!important}
.connection.connected .half-group{opacity:1!important}

/* Signature object */
.card-footer{left:20px!important;right:20px!important;bottom:10px!important;height:92px!important;border:0!important;border-radius:18px!important;background:linear-gradient(180deg,rgba(11,14,23,.025),rgba(11,14,23,.24))!important;box-shadow:0 13px 34px rgba(7,9,17,.075)!important;backdrop-filter:blur(11px)!important;-webkit-backdrop-filter:blur(11px)!important}
.connection{height:92px!important;width:min(352px,100%)!important;overflow:visible!important}.connection svg{height:88px!important;overflow:visible!important}
.connection .sig-line{stroke-width:2.55!important;filter:drop-shadow(0 5px 12px rgba(122,96,216,.14))!important;transition:stroke-width .16s ease,filter .16s ease,opacity .16s ease!important}
.connection .sig-glow{stroke-width:11!important;opacity:.045!important;filter:blur(4px)!important;transition:opacity .16s ease,filter .16s ease!important}
.connection.dragging .sig-glow{opacity:.11!important}.connection.attract .sig-glow{opacity:.31!important;filter:blur(5px)!important}.connection.attract .sig-line{stroke-width:2.85!important;filter:drop-shadow(0 0 7px rgba(196,147,255,.40)) drop-shadow(0 0 17px rgba(100,219,203,.20))!important}
.connection.connected .sig-line{stroke-width:2.9!important;filter:drop-shadow(0 0 8px rgba(255,132,170,.48)) drop-shadow(0 0 20px rgba(130,215,210,.32))!important}.connection.connected .sig-glow{opacity:.36!important;filter:blur(5.5px)!important}
.connection .hit-line{stroke-width:42!important}
.conn-label{bottom:-1px!important;font-size:8.5px!important;letter-spacing:.055em!important;color:rgba(238,240,248,.58)!important}
.connect-fallback{right:6px!important;top:1px!important;background:rgba(255,255,255,.09)!important;box-shadow:inset 0 0 0 1px rgba(255,255,255,.08)!important}

/* The magnetic moment should feel alive but not cartoony. */
.connection.magnet .sig-line{filter:drop-shadow(0 0 9px rgba(203,153,255,.52)) drop-shadow(0 0 22px rgba(104,223,205,.28))!important}
.connection.magnet .sig-glow{opacity:.42!important}
.mk-heart-event{position:absolute;left:50%;top:48px;width:12px;height:12px;margin:-6px 0 0 -6px;border-radius:50%;border:1px solid rgba(232,214,255,.94);box-shadow:0 0 17px rgba(193,152,255,.44);z-index:7;pointer-events:none;animation:mkHeartEvent .86s cubic-bezier(.16,1,.3,1) forwards}
@keyframes mkHeartEvent{0%{transform:scale(.25);opacity:0}18%{opacity:1}100%{transform:scale(4.6);opacity:0}}
.mk-heart-spark{position:absolute;left:50%;top:48px;width:3px;height:3px;margin:-1.5px;border-radius:50%;background:#fff;box-shadow:0 0 9px rgba(205,177,255,.95);z-index:8;pointer-events:none;animation:mkHeartSpark .72s cubic-bezier(.16,1,.3,1) forwards}
@keyframes mkHeartSpark{0%{transform:translate(0,0) scale(.2);opacity:0}17%{opacity:1}100%{transform:translate(var(--hx),var(--hy)) scale(.15);opacity:0}}

/* Onboarding uses the exact same geometry and physically closes the same two points. */
.mk-teach-card svg{height:96px!important;bottom:2px!important}
.mk-teach-line{stroke-width:2.6!important;filter:drop-shadow(0 6px 13px rgba(98,80,185,.13))!important}
.mk-teach-glow{stroke-width:10!important;opacity:.055!important;filter:blur(4px)!important}
.mk-teach-card.like .left{animation:mkV10TeachLeft 3.55s cubic-bezier(.16,1,.3,1) infinite!important}
.mk-teach-card.like .right{animation:mkV10TeachRight 3.55s cubic-bezier(.16,1,.3,1) infinite!important}
.mk-teach-card.like .leftg{animation:mkV10TeachLeft 3.55s cubic-bezier(.16,1,.3,1) infinite,mkV10TeachGlow 3.55s ease infinite!important}
.mk-teach-card.like .rightg{animation:mkV10TeachRight 3.55s cubic-bezier(.16,1,.3,1) infinite,mkV10TeachGlow 3.55s ease infinite!important}
.mk-teach-card.pass .right{animation:mkV10TeachPass 3.55s cubic-bezier(.2,.8,.2,1) infinite!important}.mk-teach-card.pass .left{animation:mkV10TeachStay 3.55s ease infinite!important}
@keyframes mkV10TeachLeft{0%,16%,100%{transform:translateX(0)}39%,66%{transform:translateX(9px)}80%{transform:translateX(0)}}
@keyframes mkV10TeachRight{0%,16%,100%{transform:translateX(0)}39%,66%{transform:translateX(-9px)}80%{transform:translateX(0)}}
@keyframes mkV10TeachGlow{0%,20%,82%,100%{opacity:.05;filter:blur(4px)}39%,66%{opacity:.34;filter:blur(5px)}}
@keyframes mkV10TeachPass{0%,20%,100%{transform:translateX(0);opacity:1}48%,66%{transform:translateX(92px);opacity:.04}78%{transform:translateX(0);opacity:0}88%{opacity:1}}
@keyframes mkV10TeachStay{0%,20%,100%{transform:translateX(0)}48%,66%{transform:translateX(-3px)}78%{transform:translateX(0)}}

/* Make the confirmation feel like a reward, not a system toast. */
.toast{top:54px!important;min-width:166px!important;padding:15px 24px 16px!important;border-radius:20px!important;font-size:16px!important;font-weight:780!important;box-shadow:0 22px 58px rgba(27,24,50,.32),0 0 0 1px rgba(255,255,255,.17),0 0 42px rgba(164,127,255,.17)!important}
.toast.show{animation:mkV10Toast 2.28s cubic-bezier(.16,1,.3,1) both!important}
@keyframes mkV10Toast{0%{opacity:0;transform:translate(-50%,-15px) scale(.90)}15%{opacity:1;transform:translate(-50%,1px) scale(1.035)}30%,78%{opacity:1;transform:translate(-50%,0) scale(1)}100%{opacity:0;transform:translate(-50%,-4px) scale(.98)}}
</style>
'''
    html = html.replace('</head>', css + '\n</head>', 1)

    js = r'''
<script id="minukimi-signature-heart-runtime-v10">
(function(){
  function resetHeart(conn,left,right){
    [left,right].forEach(h=>{if(!h)return;h.style.transition='transform .48s cubic-bezier(.16,1,.3,1),opacity .28s ease';h.style.transform='';h.style.opacity='';setTimeout(()=>{if(h)h.style.transition=''},500)});
    conn?.classList.remove('dragging','attract','magnet','connected');
  }

  window.wireGesture=function(){
    const conn=document.getElementById('connection'),left=document.getElementById('leftHalf'),right=document.getElementById('rightHalf');
    if(!conn||!left||!right)return;
    const halves=[left,right];
    halves.forEach((h,i)=>{
      h.onpointerdown=e=>{
        drag={h,side:i===0?'left':'right'};startX=e.clientX;startY=e.clientY;
        conn.classList.remove('connected');conn.classList.add('dragging');
        logEvent('gesture_start',{side:drag.side,dwell_ms:Date.now()-shownAt});h.setPointerCapture(e.pointerId)
      };
      h.onpointermove=e=>{
        if(!drag||drag.h!==h)return;
        const dx=e.clientX-startX,side=drag.side;
        const toward=side==='left'?Math.max(0,dx):Math.max(0,-dx);
        const away=side==='left'?Math.max(0,-dx):Math.max(0,dx);
        const p=Math.min(1,toward/34);
        const own=9*p,otherPull=9*p;
        h.style.transform=`translateX(${side==='left'?own:-own}px)`;
        const other=side==='left'?right:left;
        other.style.transition='transform .11s ease-out';
        other.style.transform=`translateX(${side==='left'?-otherPull:otherPull}px)`;
        conn.classList.toggle('attract',p>.38);conn.classList.toggle('magnet',p>.72);
        if(away>78){window.pass(true,side);drag=null}
      };
      h.onpointerup=e=>{
        if(!drag||drag.h!==h)return;
        const dx=e.clientX-startX,toward=drag.side==='left'?dx:-dx;
        conn.classList.remove('dragging','attract','magnet');
        if(toward>27)window.connect(false);
        else{logEvent('gesture_abandon',{side:drag.side,dwell_ms:Date.now()-shownAt});resetHeart(conn,left,right)}
        drag=null
      };
      h.onpointercancel=()=>{if(drag&&drag.h===h){resetHeart(conn,left,right);drag=null}}
    })
  };

  window.toast=function(t){
    const el=document.getElementById('toast');if(!el)return;
    el.querySelectorAll('.mk-toast-spark').forEach(x=>x.remove());el.classList.remove('show');el.textContent=t;
    [[-65,-31],[66,-28],[-79,3],[78,7],[-52,35],[53,37],[-19,-42],[20,-43]].forEach(([x,y],i)=>{const s=document.createElement('i');s.className='mk-toast-spark';s.style.setProperty('--sx',x+'px');s.style.setProperty('--sy',y+'px');s.style.animationDelay=(i*.035)+'s';el.appendChild(s)});
    void el.offsetWidth;el.classList.add('show');clearTimeout(window.__mkToastTimer);window.__mkToastTimer=setTimeout(()=>el.classList.remove('show'),2280)
  };

  function heartBurst(conn){
    const ring=document.createElement('i');ring.className='mk-heart-event';conn.appendChild(ring);setTimeout(()=>ring.remove(),950);
    [[-35,-24],[36,-25],[-47,2],[48,1],[-27,29],[28,30],[-9,-35],[10,-36]].forEach(([x,y],i)=>{const s=document.createElement('i');s.className='mk-heart-spark';s.style.setProperty('--hx',x+'px');s.style.setProperty('--hy',y+'px');s.style.animationDelay=(i*.025)+'s';conn.appendChild(s);setTimeout(()=>s.remove(),900)})
  }

  window.connect=function(fallback){
    logEvent('connect',{method:fallback?'button':'gesture',dwell_ms:Date.now()-shownAt});
    const conn=document.getElementById('connection'),l=document.getElementById('leftHalf'),r=document.getElementById('rightHalf'),card=document.getElementById('card');if(!conn||!l||!r)return;
    conn.classList.remove('dragging','attract','magnet');conn.classList.add('connected');
    l.style.transition=r.style.transition='transform .48s cubic-bezier(.16,1,.3,1),opacity .3s ease';
    l.style.transform='translateX(9px)';r.style.transform='translateX(-9px)';
    setTimeout(()=>heartBurst(conn),250);
    if(card){card.style.transition='transform .72s cubic-bezier(.16,1,.3,1),opacity .72s ease';card.style.transform='translateY(-2px) scale(.998)'}
    if(navigator.vibrate)navigator.vibrate([8,20,18]);
    setTimeout(()=>window.toast('I see it.'),300);
    setTimeout(()=>nextCard('connected'),1780)
  };

  window.pass=function(flick,side){
    logEvent('pass',{method:flick?'flick':'other',dwell_ms:Date.now()-shownAt});
    const card=document.getElementById('card'),conn=document.getElementById('connection');if(!card)return;
    const chosen=side==='right'?document.getElementById('rightHalf'):document.getElementById('leftHalf');
    const other=side==='right'?document.getElementById('leftHalf'):document.getElementById('rightHalf');
    if(chosen){chosen.style.transition='transform .40s cubic-bezier(.2,.76,.2,1),opacity .30s ease';chosen.style.transform=`translateX(${side==='right'?145:-145}px)`;chosen.style.opacity='0'}
    if(other){other.style.transition='transform .36s cubic-bezier(.16,1,.3,1),opacity .36s ease';other.style.transform=`translateX(${side==='right'?-3:3}px)`;other.style.opacity='.58'}
    conn?.classList.remove('dragging','attract','magnet');
    card.style.transition='opacity .44s ease,transform .44s ease';card.style.opacity='.12';card.style.transform='scale(.997)';
    setTimeout(()=>nextCard('pass'),470)
  };
})();
</script>
'''
    html = html.replace('</body>', js + '\n</body>', 1)

    files[0].write_text(html, encoding='utf-8')
    for p in files[1:]:
        try:
            p.unlink()
        except FileNotFoundError:
            pass
    print('MINUKIMI v1.0 signature heart applied')


if __name__ == '__main__':
    apply_v10()
