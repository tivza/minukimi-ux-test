from pathlib import Path

p = Path('MINUKIMI_Public_V1/templates/index.html')
s = p.read_text(encoding='utf-8')
s = s.replace('>IP Screen<', '>Trademark Check<')
s = s.replace('<a href="#ip">Trademark Check</a>', '<a href="#check" id="navTrademark">Trademark Check</a>')
s = s.replace('Screening…', 'Checking…')
needle = "function openIp(phrase=''){setActive('#checkTabs','check','check','ip');if(phrase)$('#ipPhrase').value=phrase;$('#check').scrollIntoView({behavior:'smooth',block:'start'});setTimeout(()=>$('#ipPhrase').focus(),450)}"
if "id=\"navTrademark\"" in s and "navTrademark.addEventListener" not in s:
    s = s.replace(needle, needle + "\nconst navTrademark=$('#navTrademark');if(navTrademark)navTrademark.addEventListener('click',e=>{e.preventDefault();openIp()});", 1)
p.write_text(s, encoding='utf-8')

# Fail the build if stale public copy survived.
text = p.read_text(encoding='utf-8')
assert '>IP Screen<' not in text
assert 'id="navTrademark"' in text
assert 'navTrademark.addEventListener' in text
print('Trademark Check UI patch applied')
