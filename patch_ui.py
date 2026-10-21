from pathlib import Path

ROOT = Path('MINUKIMI_Public_V1')
app_p = ROOT / 'app.py'
html_p = ROOT / 'templates' / 'index.html'

# --- backend: status-aware trademark screening ---
s = app_p.read_text(encoding='utf-8')
start = s.index('def _fallback_risk(')
end = s.index('\ndef _phrase_variants', start)
new = r'''DEAD_STATUS_CODES = {
    *{str(x) for x in range(600, 610)},
    "614", "618", "622", "626", "690",
    "710", "711", "712", "713", "714", "716", "900",
}
REGISTERED_STATUS_CODES = {"624", "700", "701", "702", "703", "704", "705", "800"}
UNKNOWN_STATUS_CODES = {"", "620", "625"}


def _status_text(m: dict[str, Any]) -> str:
    for key in ("status_label", "status_text", "status_description", "status", "status_name", "status_category"):
        value = m.get(key)
        if value:
            return str(value).strip()
    return ""


def _status_signal(m: dict[str, Any]) -> tuple[str, str]:
    text = _status_text(m)
    low = text.lower()
    if any(w in low for w in ("abandon", "cancelled", "canceled", "expired", "dead")):
        return "dead", text or "Inactive"
    if any(w in low for w in ("registered", "renewed", "live", "pending", "published", "approved", "notice of allowance", "revived", "reinstated")):
        return "live", text or "Live"
    code = str(m.get("status_code") or "").strip()
    if code in DEAD_STATUS_CODES:
        if code.startswith("60") or code in {"614", "618"}:
            return "dead", "Abandoned"
        if code == "900":
            return "dead", "Expired"
        return "dead", "Cancelled"
    if code in REGISTERED_STATUS_CODES:
        return "live", "Registered"
    if code in UNKNOWN_STATUS_CODES:
        return "unknown", text or "Status unclear"
    if code.isdigit() and 630 <= int(code) <= 899:
        return "live", "Pending"
    return "unknown", text or (f"USPTO status {code}" if code else "Status unclear")


def _normalized_classes(m: dict[str, Any]) -> list[str]:
    raw = m.get("international_codes") or m.get("international_code") or m.get("classes") or []
    if isinstance(raw, (str, int)):
        raw = [raw]
    out: list[str] = []
    for x in raw:
        digits = re.sub(r"\D", "", str(x or ""))
        if digits:
            try:
                out.append(str(int(digits)))
            except ValueError:
                pass
    return list(dict.fromkeys(out))


def _class_relation(m: dict[str, Any], target_class: str) -> str:
    if not target_class:
        return "not_specified"
    return "same" if str(int(target_class)) in _normalized_classes(m) else "different"


def _screening_risk(sim: float, live_state: str, class_relation: str) -> str:
    if live_state == "dead":
        return "historical"
    if live_state == "live":
        if class_relation == "same":
            if sim >= 0.90:
                return "high"
            if sim >= 0.76:
                return "medium"
            return "low"
        if sim >= 0.90:
            return "medium"
        if sim >= 0.76:
            return "medium"
        return "low"
    if sim >= 0.90:
        return "medium"
    return "low"


def _fallback_risk(sim: float, status_code: str) -> str:
    state, _ = _status_signal({"status_code": status_code})
    return _screening_risk(sim, state, "not_specified")
'''
s = s[:start] + new + s[end:]

start = s.index('def _normalize_markbase_match(')
end = s.index('\n\ndef markbase_screen', start)
new = r'''def _normalize_markbase_match(m: dict[str, Any], phrase: str, target_class: str = "") -> dict[str, Any]:
    mark = str(m.get("word_mark") or m.get("mark") or "").strip()
    sim = m.get("similarity")
    try:
        simf = float(sim)
        if simf > 1:
            simf /= 100.0
    except Exception:
        simf = SequenceMatcher(None, _norm_mark(phrase), _norm_mark(mark)).ratio() if mark else 0.0
    live_state, status_label = _status_signal(m)
    relation = _class_relation(m, target_class)
    risk = _screening_risk(simf, live_state, relation)
    classes = _normalized_classes(m)
    goods = (m.get("goods_services") or m.get("goods_and_services") or m.get("goods_service_description") or m.get("description") or m.get("goods") or m.get("services") or "")
    if isinstance(goods, list):
        goods = "; ".join(str(x) for x in goods if x)
    return {
        "word_mark": mark,
        "serial_number": m.get("serial_number"),
        "registration_number": m.get("registration_number"),
        "owner_name": m.get("owner_name"),
        "status_code": m.get("status_code"),
        "status_label": status_label,
        "live_state": live_state,
        "international_codes": [str(x).zfill(3) for x in classes],
        "class_relation": relation,
        "goods_services": str(goods or "").strip(),
        "filing_date": m.get("filing_date"),
        "registration_date": m.get("registration_date"),
        "similarity": round(simf, 4),
        "risk": risk,
    }
'''
s = s[:start] + new + s[end:]
old = '    matches = [_normalize_markbase_match(m, phrase) for m in raw if str(m.get("word_mark") or m.get("mark") or "").strip()]'
new = '''    enrich_params: dict[str, Any] = {"q": phrase, "limit": "25", "highlight": "full"}\n    edata, emeta = markbase_get("/search", enrich_params, timeout=10)\n    enrich_by_serial: dict[str, dict[str, Any]] = {}\n    if edata:\n        for h in (edata.get("hits") or []):\n            serial = str(h.get("serial_number") or "")\n            if serial:\n                enrich_by_serial[serial] = h\n    enriched_raw = []\n    for m in raw:\n        serial = str(m.get("serial_number") or "")\n        extra = enrich_by_serial.get(serial, {})\n        enriched_raw.append({**extra, **m})\n\n    matches = [_normalize_markbase_match(m, phrase, klass) for m in enriched_raw if str(m.get("word_mark") or m.get("mark") or "").strip()]'''
assert old in s, 'old normalize call missing'
s = s.replace(old, new, 1)
old = '''    matches = sorted(filtered, key=lambda m: ({"high": 3, "medium": 2, "low": 1}.get(m["risk"], 0), m["similarity"]), reverse=True)[:12]\n    order = {"high": 3, "medium": 2, "low": 1, "none": 0}\n    highest = max((m["risk"] for m in matches), key=lambda r: order.get(r, 0), default="none")'''
new = '''    matches = sorted(filtered, key=lambda m: ({"high": 4, "medium": 3, "low": 2, "historical": 1}.get(m["risk"], 0), m["similarity"]), reverse=True)[:12]\n    order = {"high": 4, "medium": 3, "low": 2, "historical": 1, "none": 0}\n    highest = max((m["risk"] for m in matches), key=lambda r: order.get(r, 0), default="none")'''
assert old in s, 'old sort block missing'
s = s.replace(old, new, 1)
app_p.write_text(s, encoding='utf-8')

# --- frontend: clearer labels + live/dead/class-aware result cards ---
p = html_p
s = p.read_text(encoding='utf-8')
s = s.replace('>IP Screen<', '>Trademark Check<')
s = s.replace('<a href="#ip">Trademark Check</a>', '<a href="#check" id="navTrademark">Trademark Check</a>')
s = s.replace('Screening…', 'Checking…')
s = s.replace('Use “Check IP” for preliminary U.S. word-mark screening.', 'Use “Trademark Check” for preliminary U.S. word-mark screening.')
needle = "function openIp(phrase=''){setActive('#checkTabs','check','check','ip');if(phrase)$('#ipPhrase').value=phrase;$('#check').scrollIntoView({behavior:'smooth',block:'start'});setTimeout(()=>$('#ipPhrase').focus(),450)}"
if 'id="navTrademark"' in s and 'navTrademark.addEventListener' not in s:
    s = s.replace(needle, needle + "\nconst navTrademark=$('#navTrademark');if(navTrademark)navTrademark.addEventListener('click',e=>{e.preventDefault();openIp()});", 1)
css_old = '.risk-high{color:var(--bad)}.risk-medium{color:var(--warn)}.risk-low,.risk-none{color:var(--ok)}.ip-match{border-top:1px solid var(--line);padding:11px 0}'
css_new = '.risk-high{color:var(--bad)}.risk-medium{color:var(--warn)}.risk-low,.risk-none{color:var(--ok)}.risk-historical{color:#7d8190}.ip-match{border-top:1px solid var(--line);padding:13px 0}.mark-state{display:inline-flex;padding:3px 6px;border-radius:999px;font-size:8px;font-weight:900;letter-spacing:.06em;margin-right:5px}.mark-state.live{background:#e8f5ef;color:var(--ok)}.mark-state.dead{background:#f0f0f4;color:#777b89}.mark-state.unknown{background:#fff4d9;color:var(--warn)}.goods{font-size:10px;color:#747887;line-height:1.45;margin-top:6px}.class-same{color:var(--bad);font-weight:800}.class-different{color:#727684}.historical-badge{background:#f0f0f4;color:#777b89}'
assert css_old in s, 'IP css marker missing'
s = s.replace(css_old, css_new, 1)
start = s.index('function renderIp(data)')
end = s.index('\nfunction ipLegal', start)
render = r'''function riskBadge(m){
  const r=m.risk||'low';
  const cls=r==='high'?'fail':r==='medium'?'review':r==='historical'?'historical-badge':'pass';
  const label=r==='historical'?'HISTORICAL':r.toUpperCase();
  return `<span class="status ${cls}">${esc(label)}</span>`
}
function markState(m){const s=m.live_state||'unknown';return `<span class="mark-state ${esc(s)}">${esc(s.toUpperCase())}</span>`}
function classNote(m){if(m.class_relation==='same')return '<span class="class-same">same class</span>';if(m.class_relation==='different')return '<span class="class-different">different class</span>';return 'class relevance not assessed'}
function renderIp(data){
  const out=$('#resultIp');out.classList.add('show');const links=data.official_links||{};
  if(!data.ok){out.innerHTML=`<div class="issue review"><b>Automated trademark source unavailable</b><div>${esc(data.error||'The automated check could not be completed right now.')}</div></div>${ipLegal(data,links)}`;out.scrollIntoView({behavior:'smooth',block:'nearest'});return}
  const risk=data.highest_risk||'none',matches=data.matches||[],live=matches.filter(m=>m.live_state==='live').length,dead=matches.filter(m=>m.live_state==='dead').length;
  const guidance=risk==='high'?'Live close match in the same class — inspect before using this phrase.':risk==='medium'?'Review live matches and goods/services before using this phrase.':risk==='historical'?'Only inactive federal records surfaced in this pass. They are historical context, not current federal blockers.':'No strong current conflict surfaced in this preliminary pass.';
  out.innerHTML=`<div class="ip-layout"><div class="ipbox"><div class="micro">PRELIMINARY TRADEMARK SIGNAL</div><div class="risk-big risk-${esc(risk)}">${esc(risk.toUpperCase())}</div><div class="muted">${matches.length} candidate match(es) surfaced · ${live} live · ${dead} inactive.</div><div class="notice" style="margin-top:12px">${esc(guidance)}${data.class?` Target class: ${esc(String(data.class).padStart(3,'0'))}.`:' Add a Nice class for a more useful conflict signal.'}</div></div><div class="ipbox ip-results">${matches.length?matches.slice(0,10).map(m=>`<div class="ip-match"><div class="cardtop"><div><b>${esc(m.word_mark)}</b><div style="margin-top:5px">${markState(m)}<span class="micro">${esc(m.status_label||'Status unclear')}</span></div></div>${riskBadge(m)}</div><div class="micro" style="margin-top:6px">Similarity ${Math.round((m.similarity||0)*100)}%${m.owner_name?` · ${esc(m.owner_name)}`:''}${m.international_codes?.length?` · class ${esc(m.international_codes.join(', '))}`:''} · ${classNote(m)}</div>${m.goods_services?`<div class="goods"><b>Goods/services:</b> ${esc(m.goods_services).slice(0,320)}</div>`:''}${m.serial_number?`<div class="links" style="margin-top:7px"><a href="https://tsdr.uspto.gov/#caseNumber=${encodeURIComponent(m.serial_number)}&caseSearchType=US_APPLICATION&caseType=DEFAULT&searchType=statusSearch" target="_blank" rel="noopener">USPTO record ↗</a></div>`:''}</div>`).join(''):'<div class="empty">No relevant candidate was surfaced by this automated pass. This is still not clearance.</div>'}</div></div>${ipLegal(data,links)}`;
  out.scrollIntoView({behavior:'smooth',block:'nearest'})
}'''
s = s[:start] + render + s[end:]
p.write_text(s, encoding='utf-8')

# Build-time sanity checks.
text = p.read_text(encoding='utf-8')
assert '>IP Screen<' not in text
assert 'id="navTrademark"' in text
assert 'HISTORICAL' in text
assert 'mark-state' in text
backend = app_p.read_text(encoding='utf-8')
assert 'DEAD_STATUS_CODES' in backend
assert 'class_relation' in backend
assert 'historical' in backend
print('Trademark Check status-aware patch applied')
