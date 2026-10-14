from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
PARTS = ROOT / "index_parts"


def apply_v09():
    files = sorted(PARTS.glob("index.part.*"))
    if not files:
        return
    html = b"".join(p.read_bytes() for p in files).decode("utf-8")
    if 'data-ui-v09="true"' in html:
        print("MINUKIMI v0.9 overlay already applied")
        return

    css = r'''
<style id="minukimi-ui-v09">
.status{display:none!important}
.screen>.topbar,.intake-screen>.topbar,.profile-setup>.topbar{padding-top:10px!important}

/* Gesture onboarding: show both actions, not just prose */
#on2 .art{height:350px!important;display:flex!important;align-items:center!important;justify-content:center!important}
.mk-gesture-teach{width:min(340px,100%);display:grid;gap:12px}
.mk-teach-card{position:relative;height:132px;border-radius:24px;background:rgba(255,255,255,.74);border:1px solid rgba(40,42,58,.07);box-shadow:0 16px 42px rgba(59,49,100,.08);overflow:hidden;padding:13px 14px 10px}
.mk-teach-copy{display:flex;align-items:center;justify-content:space-between;gap:12px;position:relative;z-index:2}
.mk-teach-copy b{font-size:12px;letter-spacing:.01em}.mk-teach-copy span{font-size:10.5px;color:#888b99;text-align:right}
.mk-teach-card svg{position:absolute;left:10px;right:10px;bottom:5px;width:calc(100% - 20px);height:94px;overflow:visible}
.mk-teach-line{fill:none;stroke-width:2.8;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 6px 14px rgba(100,82,190,.13));transform-box:fill-box;transform-origin:center}
.mk-teach-glow{fill:none;stroke-width:10;stroke-linecap:round;opacity:.08;filter:blur(4px);transform-box:fill-box;transform-origin:center}
.mk-teach-heart{fill:none;stroke:url(#mkTeachHeart);stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round;opacity:0;filter:drop-shadow(0 7px 16px rgba(154,119,239,.24))}
.mk-teach-card.like .left,.mk-teach-card.like .leftg{animation:mkTeachLeft 3.2s cubic-bezier(.16,1,.3,1) infinite}
.mk-teach-card.like .right,.mk-teach-card.like .rightg{animation:mkTeachRight 3.2s cubic-bezier(.16,1,.3,1) infinite}
.mk-teach-card.like .mk-teach-heart{animation:mkTeachHeart 3.2s ease infinite}
.mk-teach-card.pass .right,.mk-teach-card.pass .rightg{animation:mkTeachPass 3.2s cubic-bezier(.2,.8,.2,1) infinite}
@keyframes mkTeachLeft{0%,18%,100%{transform:translateX(0)}42%,64%{transform:translateX(7px)}}
@keyframes mkTeachRight{0%,18%,100%{transform:translateX(0)}42%,64%{transform:translateX(-7px)}}
@keyframes mkTeachHeart{0%,28%,100%{opacity:0;stroke-dasharray:110;stroke-dashoffset:110}43%,62%{opacity:1;stroke-dashoffset:0}76%{opacity:0;stroke-dashoffset:0}}
@keyframes mkTeachPass{0%,20%,100%{transform:translateX(0);opacity:1}46%,66%{transform:translateX(78px);opacity:.08}78%{transform:translateX(0);opacity:0}88%{opacity:1}}

/* Discovery gesture: aligned with prompt, no decorative micro-lines */
.card-footer{left:20px!important;right:20px!important;bottom:10px!important;height:88px!important;border:0!important;border-radius:18px!important;background:linear-gradient(180deg,rgba(15,18,28,.05),rgba(15,18,28,.38))!important;box-shadow:0 12px 30px rgba(8,10,18,.08)!important;backdrop-filter:blur(13px)!important;-webkit-backdrop-filter:blur(13px)!important}
.connection{width:min(350px,100%)!important;height:88px!important}.connection svg{height:83px!important}
.handle-mark,.center-flare,.center-flare-sharp{display:none!important}
.connection .sig-line{stroke-width:2.65!important;filter:drop-shadow(0 5px 12px rgba(124,99,219,.16))!important;transition:filter .18s ease,stroke-width .18s ease}
.connection .sig-glow{stroke-width:10!important;opacity:.07!important;filter:blur(4px)!important;transition:opacity .18s ease,filter .18s ease}
.connection.dragging .sig-glow{opacity:.14!important}.connection.attract .sig-glow{opacity:.34!important;filter:blur(5px)!important}.connection.attract .sig-line{stroke-width:2.95!important;filter:drop-shadow(0 0 7px rgba(190,145,255,.36)) drop-shadow(0 0 15px rgba(103,221,202,.18))!important}
.connection .hit-line{stroke-width:38!important}.conn-label{bottom:1px!important;font-size:9px!important;letter-spacing:.045em!important;color:rgba(239,241,248,.66)!important}
.connect-fallback{right:6px!important;top:3px!important;border:0!important;background:rgba(255,255,255,.11)!important;color:#f7f5ff!important;padding:5px 9px!important;box-shadow:inset 0 0 0 1px rgba(255,255,255,.09)!important}
.connection.connected .sig-line{filter:drop-shadow(0 0 8px rgba(255,142,171,.42)) drop-shadow(0 0 20px rgba(135,212,210,.28))!important}
.mk-heart-pulse{position:absolute;left:50%;top:42px;width:16px;height:16px;margin:-8px 0 0 -8px;border-radius:50%;border:1px solid rgba(222,203,255,.85);pointer-events:none;z-index:5;animation:mkHeartPulse .78s cubic-bezier(.16,1,.3,1) forwards}
@keyframes mkHeartPulse{0%{transform:scale(.35);opacity:0}25%{opacity:1}100%{transform:scale(3.1);opacity:0}}

/* Stronger but still refined connect confirmation */
.toast{top:58px!important;min-width:148px!important;padding:14px 20px 15px!important;border-radius:18px!important;background:linear-gradient(135deg,rgba(32,34,49,.96),rgba(48,45,70,.95))!important;font-size:15px!important;font-weight:760!important;letter-spacing:.01em!important;box-shadow:0 20px 54px rgba(28,25,51,.30),0 0 0 1px rgba(255,255,255,.16),0 0 34px rgba(169,133,255,.12)!important;overflow:visible!important}
.toast::before{content:"";position:absolute;inset:-18px;border-radius:28px;background:radial-gradient(circle,rgba(207,184,255,.20),rgba(255,150,178,.07) 38%,transparent 70%);opacity:0;pointer-events:none}.toast.show::before{animation:mkToastHalo 2.15s ease both}
@keyframes mkToastHalo{0%{opacity:0;transform:scale(.7)}18%{opacity:1}70%{opacity:.42}100%{opacity:0;transform:scale(1.18)}}
.mk-toast-spark{position:absolute;left:50%;top:50%;width:4px;height:4px;border-radius:50%;background:#fff;box-shadow:0 0 8px rgba(202,177,255,.9);pointer-events:none;animation:mkToastSpark .72s cubic-bezier(.16,1,.3,1) forwards}
@keyframes mkToastSpark{0%{transform:translate(-50%,-50%) scale(.2);opacity:0}20%{opacity:1}100%{transform:translate(calc(-50% + var(--sx)),calc(-50% + var(--sy))) scale(.15);opacity:0}}

/* City normalization */
.city-field{position:relative!important;overflow:visible!important}.city-suggestions{position:absolute;left:0;right:0;top:calc(100% + 7px);z-index:80;background:rgba(255,255,255,.98);border:1px solid #e7e7ef;border-radius:16px;box-shadow:0 18px 44px rgba(45,39,80,.14);padding:5px;display:none;max-height:205px;overflow:auto}.city-suggestions.show{display:block}.city-option{width:100%;border:0;background:transparent;text-align:left;border-radius:12px;padding:9px 10px;display:block;color:#343746}.city-option:hover,.city-option:focus{background:#f5f3ff;outline:0}.city-option b{display:block;font-size:12px}.city-option small{display:block;font-size:10px;color:#8c8f9d;margin-top:2px}.city-note{font-size:9px;color:#9a9daa;margin-top:5px}
</style>
'''
    html = html.replace('</head>', css + '\n</head>', 1)

    # Remove fake OS chrome everywhere, not just onboarding.
    html = html.replace('<body data-ui-patch="full-v4">', '<body data-ui-patch="full-v4" data-ui-v09="true">', 1)

    # Normalize the two line halves into visible pieces of a heart.
    left_old = 'M22 56 C58 58 82 56 103 45 C116 38 127 39 139 47'
    right_old = 'M270 56 C234 58 210 56 189 45 C176 38 165 39 153 47'
    left_new = 'M18 68 C58 69 86 66 108 52 C119 45 122 26 137 26 C149 26 157 36 159 47 C160 55 153 63 140 70'
    right_new = 'M274 68 C234 69 206 66 184 52 C173 45 170 26 155 26 C143 26 135 36 133 47 C132 55 139 63 152 70'
    html = html.replace(left_old, left_new).replace(right_old, right_new)
    html = html.replace('bring the lines together / pull away to pass', 'bring together to connect / flick away to pass')

    # Make the gesture lesson self-explanatory, with both positive and negative actions animated.
    teach = r'''<div class="art"><div class="mk-gesture-teach">
      <div class="mk-teach-card like"><div class="mk-teach-copy"><b>Like them?</b><span>Bring the lines together</span></div><svg viewBox="0 0 292 88"><defs><linearGradient id="mkTeachL" x1="0" x2="1"><stop stop-color="#ff7898"/><stop offset="1" stop-color="#bd8eff"/></linearGradient><linearGradient id="mkTeachR" x1="1" x2="0"><stop stop-color="#74dac8"/><stop offset="1" stop-color="#8d82ff"/></linearGradient><linearGradient id="mkTeachHeart" x1="0" x2="1"><stop stop-color="#ff7898"/><stop offset=".5" stop-color="#bc8eff"/><stop offset="1" stop-color="#74dac8"/></linearGradient></defs><path class="mk-teach-glow leftg" d="M18 68 C58 69 86 66 108 52 C119 45 122 26 137 26 C149 26 157 36 159 47 C160 55 153 63 140 70" stroke="url(#mkTeachL)"/><path class="mk-teach-glow rightg" d="M274 68 C234 69 206 66 184 52 C173 45 170 26 155 26 C143 26 135 36 133 47 C132 55 139 63 152 70" stroke="url(#mkTeachR)"/><path class="mk-teach-line left" d="M18 68 C58 69 86 66 108 52 C119 45 122 26 137 26 C149 26 157 36 159 47 C160 55 153 63 140 70" stroke="url(#mkTeachL)"/><path class="mk-teach-line right" d="M274 68 C234 69 206 66 184 52 C173 45 170 26 155 26 C143 26 135 36 133 47 C132 55 139 63 152 70" stroke="url(#mkTeachR)"/><path class="mk-teach-heart" d="M146 70 C121 55 113 42 117 31 C122 19 136 21 146 36 C156 21 170 19 175 31 C179 42 171 55 146 70"/></svg></div>
      <div class="mk-teach-card pass"><div class="mk-teach-copy"><b>Not for you?</b><span>Flick either line away</span></div><svg viewBox="0 0 292 88"><defs><linearGradient id="mkPassL" x1="0" x2="1"><stop stop-color="#ff7898"/><stop offset="1" stop-color="#bd8eff"/></linearGradient><linearGradient id="mkPassR" x1="1" x2="0"><stop stop-color="#74dac8"/><stop offset="1" stop-color="#8d82ff"/></linearGradient></defs><path class="mk-teach-line left" d="M18 68 C58 69 86 66 108 52 C119 45 122 26 137 26 C149 26 157 36 159 47 C160 55 153 63 140 70" stroke="url(#mkPassL)"/><path class="mk-teach-line right" d="M274 68 C234 69 206 66 184 52 C173 45 170 26 155 26 C143 26 135 36 133 47 C132 55 139 63 152 70" stroke="url(#mkPassR)"/></svg></div>
    </div></div><div><h2>One gesture, two clear choices.</h2><p>If you want to connect, pull the two heart-lines together. If you are not interested, flick either line away. You can let go at any time if you change your mind.</p>'''
    html = re.sub(r'<div class="art"><div class="gesture-demo">.*?</div></div>\s*<div><h2>.*?</h2><p>.*?</p>', teach, html, count=1, flags=re.S)

    # Add a real city chooser to profile creation.
    city_old = '<div class="profile-field"><label>City</label><input id="mkCity" maxlength="40" autocomplete="address-level2" placeholder="Lisbon"></div>'
    city_new = '<div class="profile-field city-field"><label>City</label><input id="mkCity" maxlength="60" autocomplete="off" placeholder="Start typing a city"><div class="city-suggestions" id="mkCitySuggestions"></div><div class="city-note">Choose a suggestion so locations stay consistent.</div></div>'
    html = html.replace(city_old, city_new, 1)

    # Version marker in saved sessions.
    html = html.replace("version:'0.8'", "version:'0.9'").replace("research.version='0.8'", "research.version='0.9'")

    js = r'''
<script id="minukimi-v09-runtime">
(function(){
  /* City autocomplete / normalization via Open-Meteo's keyless geocoding API. */
  const input=document.getElementById('mkCity'),list=document.getElementById('mkCitySuggestions');
  if(input&&list){
    let timer=null,ctl=null;
    const hide=()=>list.classList.remove('show');
    const displayName=r=>{const main=r.name||'';const region=r.admin1&&r.admin1!==main?r.admin1:'';const country=r.country||'';return [main,region,country].filter(Boolean).join(', ')};
    const render=(rows,q)=>{list.innerHTML='';if(!rows.length){const b=document.createElement('button');b.type='button';b.className='city-option';b.innerHTML='<b>No city found</b><small>Try another spelling</small>';list.appendChild(b);list.classList.add('show');return}rows.slice(0,6).forEach(r=>{const b=document.createElement('button');b.type='button';b.className='city-option';const label=displayName(r);b.innerHTML='<b>'+String(r.name||'').replace(/[<>]/g,'')+'</b><small>'+[r.admin1,r.country].filter(Boolean).join(', ').replace(/[<>]/g,'')+'</small>';b.onclick=()=>{input.value=label;input.dataset.cityValidated=label;input.dataset.cityLookupUnavailable='';hide();input.dispatchEvent(new Event('change',{bubbles:true}))};list.appendChild(b)});list.classList.add('show')};
    async function lookup(){const q=input.value.trim();delete input.dataset.cityValidated;if(q.length<2){hide();return}if(ctl)ctl.abort();ctl=new AbortController();try{const u='https://geocoding-api.open-meteo.com/v1/search?name='+encodeURIComponent(q)+'&count=7&language=en&format=json';const r=await fetch(u,{signal:ctl.signal});if(!r.ok)throw new Error('lookup');const j=await r.json();input.dataset.cityLookupUnavailable='';render(j.results||[],q)}catch(e){if(e.name==='AbortError')return;input.dataset.cityLookupUnavailable='1';list.innerHTML='<div class="city-option"><b>City lookup is temporarily unavailable</b><small>You can continue with the city you typed.</small></div>';list.classList.add('show')}}
    input.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(lookup,260)});input.addEventListener('focus',()=>{if(input.value.trim().length>=2&&!input.dataset.cityValidated)lookup()});document.addEventListener('pointerdown',e=>{if(!e.target.closest('.city-field'))hide()});
    if(window.mkProfile&&mkProfile.city){input.dataset.cityValidated=mkProfile.city}
    const original=window.mkGoPrompt;
    if(typeof original==='function')window.mkGoPrompt=function(){const city=input.value.trim();const err=document.getElementById('mkBasicsError');if(!city){err.textContent='Add your city.';return}if(!input.dataset.cityValidated&&input.dataset.cityLookupUnavailable!=='1'){err.textContent='Choose your city from the suggestions so we can match locations correctly.';input.focus();return}if(input.dataset.cityValidated)input.value=input.dataset.cityValidated;return original()}
  }

  /* Override the gesture with a subtler heart assembly and a quieter pass. */
  window.wireGesture=function(){
    const conn=document.getElementById('connection'),left=document.getElementById('leftHalf'),right=document.getElementById('rightHalf');if(!conn||!left||!right)return;
    const halves=[left,right];
    const reset=()=>{halves.forEach(h=>{h.style.transition='transform .48s cubic-bezier(.16,1,.3,1),opacity .28s ease';h.style.transform='';h.style.opacity='';setTimeout(()=>h.style.transition='',500)});conn.classList.remove('dragging','attract')};
    halves.forEach((h,i)=>{h.onpointerdown=e=>{drag={h,side:i===0?'left':'right'};startX=e.clientX;startY=e.clientY;conn.classList.add('dragging');logEvent('gesture_start',{side:drag.side,dwell_ms:Date.now()-shownAt});h.setPointerCapture(e.pointerId)};h.onpointermove=e=>{if(!drag||drag.h!==h)return;const dx=e.clientX-startX,side=drag.side,toward=side==='left'?Math.max(0,dx):Math.max(0,-dx),away=side==='left'?Math.max(0,-dx):Math.max(0,dx),p=Math.min(1,toward/52);h.style.transform=`translate(${side==='left'?8*p:-8*p}px,0)`;const other=side==='left'?right:left;other.style.transition='transform .12s ease-out';other.style.transform=`translate(${side==='left'?-2*p:2*p}px,0)`;if(p>.58)conn.classList.add('attract');else conn.classList.remove('attract');if(away>86){window.pass(true,side);drag=null}};h.onpointerup=e=>{if(!drag||drag.h!==h)return;const dx=e.clientX-startX,toward=drag.side==='left'?dx:-dx;conn.classList.remove('dragging','attract');if(toward>42)window.connect(false);else{logEvent('gesture_abandon',{side:drag.side,dwell_ms:Date.now()-shownAt});reset()}drag=null};h.onpointercancel=()=>{if(drag&&drag.h===h){reset();drag=null}}})
  };

  window.toast=function(t){const el=document.getElementById('toast');if(!el)return;el.classList.remove('show');el.textContent=t;[[ -55,-28],[58,-24],[-67,12],[67,14],[-32,34],[34,36]].forEach(([x,y],i)=>{const s=document.createElement('i');s.className='mk-toast-spark';s.style.setProperty('--sx',x+'px');s.style.setProperty('--sy',y+'px');s.style.animationDelay=(i*.035)+'s';el.appendChild(s)});void el.offsetWidth;el.classList.add('show');clearTimeout(window.__mkToastTimer);window.__mkToastTimer=setTimeout(()=>el.classList.remove('show'),2200)};

  window.connect=function(fallback){logEvent('connect',{method:fallback?'button':'gesture',dwell_ms:Date.now()-shownAt});const conn=document.getElementById('connection'),l=document.getElementById('leftHalf'),r=document.getElementById('rightHalf'),card=document.getElementById('card');if(!conn||!l||!r)return;conn.classList.remove('dragging','attract');conn.classList.add('connected');l.style.transition=r.style.transition='transform .58s cubic-bezier(.16,1,.3,1),opacity .32s ease';l.style.transform='translate(6px,0)';r.style.transform='translate(-6px,0)';const pulse=document.createElement('i');pulse.className='mk-heart-pulse';conn.appendChild(pulse);setTimeout(()=>pulse.remove(),900);if(card){card.style.transition='transform .7s cubic-bezier(.16,1,.3,1),opacity .7s ease';card.style.transform='translateY(-2px) scale(.998)'}if(navigator.vibrate)navigator.vibrate([9,22,16]);window.toast('I see it.');setTimeout(()=>nextCard('connected'),1550)};

  window.pass=function(flick,side){logEvent('pass',{method:flick?'flick':'other',dwell_ms:Date.now()-shownAt});const card=document.getElementById('card'),conn=document.getElementById('connection');if(!card)return;const h=side==='right'?document.getElementById('rightHalf'):document.getElementById('leftHalf');if(h){h.style.transition='transform .38s cubic-bezier(.2,.75,.2,1),opacity .3s ease';h.style.transform=`translate(${side==='right'?112:-112}px,0)`;h.style.opacity='0'}if(conn)conn.classList.remove('dragging','attract');card.style.transition='transform .46s ease,opacity .42s ease';card.style.opacity='.13';setTimeout(()=>nextCard('pass'),440)};
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
    print('MINUKIMI v0.9 overlay applied')


try:
    apply_v09()
except Exception as exc:
    print('MINUKIMI v0.9 overlay failed:', repr(exc))
