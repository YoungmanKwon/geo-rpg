"""한국어 index.html → 영어 en/index.html 자동 생성.
사용법 (저장소 최상위 폴더에서):  python tools/gen_en.py
번역 사전(tools/en_map.json)에 없는 한국어 문장은 'missing' 목록으로 출력된다.
그 문장들의 영어 번역을 en_map.json에 추가한 뒤 다시 실행하면 된다."""
import re, json, bisect, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, 'index.html'); dst = os.path.join(ROOT, 'en', 'index.html')
s = open(src, encoding='utf-8').read()
M = json.load(open(os.path.join(ROOT, 'tools', 'en_map.json'), encoding='utf-8'))
spans = [(m.start(), m.end()) for m in re.finditer(r'/\*.*?\*/|<!--.*?-->', s, re.S)]
spans += [(m.start(), m.end()) for m in re.finditer(r'(?<![:\'"\\])//[^\n]*', s)]
spans.sort(); starts = [a for a, b in spans]
def in_comment(i):
    k = bisect.bisect_right(starts, i) - 1
    return k >= 0 and spans[k][0] <= i < spans[k][1]
pat = re.compile(r"[^'\"`<>\n{}$]*[\uac00-\ud7a3\u3131-\u318e][^'\"`<>\n{}$]*")
out, last, miss = [], 0, []
for m in pat.finditer(s):
    if in_comment(m.start()): continue
    t = m.group(0)
    if t == '🌐 한국어': continue
    if t not in M:
        if '//' not in t: miss.append(t)
        continue
    out.append(s[last:m.start()]); out.append(M[t]); last = m.end()
out.append(s[last:]); e = ''.join(out)
e = e.replace('<html lang="ko">', '<html lang="en">', 1).replace('<a class="langsw" href="./en/">🌐 English</a>', '<a class="langsw" href="../">🌐 한국어</a>')
os.makedirs(os.path.dirname(dst), exist_ok=True); open(dst, 'w', encoding='utf-8').write(e)
print('en/index.html 생성 완료')
if miss:
    print('번역이 필요한 문장 (en_map.json에 추가):')
    for x in dict.fromkeys(miss): print('  ', json.dumps(x, ensure_ascii=False))
