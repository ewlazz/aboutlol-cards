"""경기 후 평점 카드 생성기 (@aboutlol.kr)

사용법:
    python3 make.py match.json            # out/<slug>/ 에 PNG + JPG 4장 생성
    python3 make.py match.json --out DIR  # 출력 폴더 지정

match.json 형식은 README.md 참고.
"""
import json, sys, html, pathlib, argparse
from PIL import Image, ImageFilter

HERE = pathlib.Path(__file__).resolve().parent
A = HERE / 'assets'
POS = ['top', 'jungle', 'mid', 'bot', 'support']
DIM = 'rgba(255,255,255,0.55)'
LAV = '#A9A3F0'


def uri(p):
    return pathlib.Path(p).resolve().as_uri()


def esc(s):
    return html.escape(str(s))


def base_css():
    f = A / 'fonts'
    return f"""
@font-face {{ font-family: 'Pretendard'; font-weight: 900; src: url('{uri(f/'Pretendard-Black.otf')}'); }}
@font-face {{ font-family: 'Pretendard'; font-weight: 700; src: url('{uri(f/'Pretendard-Bold.otf')}'); }}
@font-face {{ font-family: 'Pretendard'; font-weight: 500; src: url('{uri(f/'Pretendard-Medium.otf')}'); }}
@font-face {{ font-family: 'IDisp'; font-weight: 900; src: url('{uri(f/'InterDisplay-Black.otf')}'); }}
@font-face {{ font-family: 'IDisp'; font-weight: 700; src: url('{uri(f/'InterDisplay-Bold.otf')}'); }}
@font-face {{ font-family: 'IDisp'; font-weight: 500; src: url('{uri(f/'InterDisplay-Medium.otf')}'); }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: 1080px; height: 1350px; }}
body {{ background: #0B0B0E; color: #FFF; font-family: 'Pretendard', sans-serif; position: relative; overflow: hidden;
  -webkit-font-smoothing: antialiased; word-break: keep-all; }}
.en {{ font-family: 'IDisp', 'Pretendard', sans-serif; font-feature-settings: 'tnum' 1; }}
.tl, .tr {{ position: absolute; top: 64px; font-weight: 700; font-size: 34px; }}
.tl {{ left: 72px; }} .tr {{ right: 72px; font-family: 'IDisp'; }}
.cr {{ position: absolute; right: 72px; bottom: 40px; font-size: 24px; font-weight: 500; color: rgba(255,255,255,0.5); }}
"""


def page(body, css=''):
    return f'<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><style>{base_css()}{css}</style></head><body>{body}</body></html>'


def logo(team, h):
    p = A / 'logos_white' / f"{team.get('logo', '')}.png"
    if team.get('logo') and p.exists():
        return f'<img src="{uri(p)}" style="height:{h}px;display:block">'
    return f'<span style="font-weight:900;font-size:{int(h*0.6)}px;letter-spacing:-0.03em">{esc(team["name"])}</span>'


def crop_cover(src, dst, fx=0.5, fy=0.0):
    im = Image.open(src).convert('RGB')
    s = max(1080 / im.width, 1350 / im.height)
    w, h = round(im.width * s), round(im.height * s)
    im = im.resize((w, h), Image.LANCZOS)
    if s > 1.15:
        im = im.filter(ImageFilter.UnsharpMask(1.3, 50, 2))
    x0 = int(min(max(fx * w - 540, 0), w - 1080))
    y0 = int(min(max(fy * (h - 1350), 0), h - 1350))
    im.crop((x0, y0, x0 + 1080, y0 + 1350)).save(dst, quality=95)


def cover(m, out):
    a, b = m['teams']
    cv = m.get('cover') or {}
    css = """
.bg { position: absolute; inset: 0; width: 1080px; height: 1350px; }
.shade { position: absolute; left: 0; bottom: 0; width: 1080px; height: 700px; background: linear-gradient(rgba(0,0,0,0), rgba(0,0,0,0.9)); }
.lg { position: absolute; left: 72px; bottom: 300px; font-size: 40px; font-weight: 700; color: rgba(255,255,255,0.75); }
.sc { position: absolute; left: 72px; bottom: 80px; display: flex; align-items: center; gap: 52px; }
.sc .lw img { max-width: 250px; height: auto !important; max-height: 140px; }
.sc .n { font-family: 'IDisp'; font-weight: 900; font-size: 180px; letter-spacing: -0.04em; line-height: 1; }
.sc .c { font-family: 'IDisp'; font-weight: 700; font-size: 110px; color: rgba(255,255,255,0.4); }
.sc .lose { opacity: 0.45; }
"""
    bg = ''
    if cv.get('photo'):
        dst = out / 'cover.jpg'
        crop_cover(cv['photo'], dst, cv.get('focus_x', 0.5), cv.get('focus_y', 0.0))
        bg = f'<img class="bg" src="{uri(dst)}"><div class="shade"></div>'
    sa, sb = a['score'], b['score']
    la = '' if sa >= sb else ' lose'
    lb = '' if sb >= sa else ' lose'
    body = f"""{bg}
<div class="tl en">{esc(m['date'])}</div><div class="tr">01 / 04</div>
<div class="lg">{esc(m.get('league', ''))}</div>
<div class="sc">
  <div class="lw {la.strip()}">{logo(a, 140)}</div>
  <div class="n{la}">{sa}</div><div class="c">:</div><div class="n{lb}">{sb}</div>
  <div class="lw {lb.strip()}">{logo(b, 140)}</div>
</div>
{'<div class="cr">' + esc(cv['credit']) + '</div>' if cv.get('credit') else ''}"""
    return page(body, css)


def team_card(m, i, pageno):
    t = m['teams'][i]
    o = m['teams'][1 - i]
    win = t['score'] > o['score']
    css = f"""
.res {{ position: absolute; left: 72px; top: 124px; font-size: 32px; font-weight: 700; color: {DIM}; }}
.res b {{ color: {'#FFF' if win else DIM}; margin-left: 14px; }}
.list {{ position: absolute; left: 72px; right: 72px; top: 220px; }}
.r {{ display: flex; align-items: center; gap: 40px; padding: 30px 0; border-top: 1px solid rgba(255,255,255,0.14); }}
.r:first-child {{ border-top: none; }}
.r img {{ width: 72px; height: 72px; flex: none; }}
.who {{ flex: 1; min-width: 0; }}
.nm {{ font-size: 84px; font-weight: 900; letter-spacing: -0.035em; line-height: 1; display: flex; align-items: center; gap: 24px; }}
.nm .tag {{ font-family: 'IDisp'; font-size: 30px; font-weight: 700; color: {LAV}; letter-spacing: 0; }}
.note {{ font-size: 28px; font-weight: 500; color: {DIM}; margin-top: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.rt {{ font-family: 'IDisp'; font-weight: 900; font-size: 116px; letter-spacing: -0.04em; line-height: 1; margin-left: 30px; }}
.rt.low {{ color: {DIM}; }}
.foot {{ position: absolute; left: 72px; bottom: 72px; }}
"""
    rows = []
    for p in t['players']:
        r = float(p['rating'])
        tag = '<span class="tag">POG</span>' if p.get('pog') else ''
        note = f'<div class="note">{esc(p["note"])}</div>' if p.get('note') else ''
        rows.append(f'<div class="r"><img src="{uri(A/"icons"/(p["pos"]+"_w.png"))}">'
                    f'<div class="who"><div class="nm">{esc(p["name"])}{tag}</div>{note}</div>'
                    f'<div class="rt{" low" if r < m.get("low_below", 6.0) else ""}">{r:.1f}</div></div>')
    body = f"""<div class="tl">{esc(t['name'])} 평점</div><div class="tr">{pageno} / 04</div>
<div class="res">vs {esc(o['name'])} <span class="en">{t['score']} : {o['score']}</span><b>{'승' if win else '패'}</b></div>
<div class="list">{''.join(rows)}</div>
<div class="foot">{logo(t, 110)}</div>"""
    return page(body, css)


def outro():
    B = A / 'brand'
    css = """
.main { position: absolute; left: 72px; right: 72px; top: 230px; }
.main .av { width: 300px; height: 300px; border-radius: 50%; overflow: hidden; border: 2px solid rgba(255,255,255,0.14); }
.main .av img { width: 100%; height: 100%; }
.main .h { display: flex; align-items: center; gap: 22px; margin-top: 48px; font-family: 'IDisp'; font-weight: 900; font-size: 112px; letter-spacing: -0.035em; line-height: 1; }
.main .d { font-size: 40px; font-weight: 700; color: rgba(255,255,255,0.6); margin-top: 22px; }
.subs { position: absolute; left: 72px; right: 72px; bottom: 90px; border-top: 1px solid rgba(255,255,255,0.14); }
.s { display: flex; align-items: center; gap: 26px; padding-top: 36px; }
.s .av { width: 96px; height: 96px; border-radius: 50%; overflow: hidden; flex: none; background: #fff; display: flex; align-items: center; justify-content: center; }
.s .av img { width: 100%; height: 100%; object-fit: cover; }
.s .av.site { background: #16161C; border: 2px solid rgba(255,255,255,0.14); }
.s .av.site img { width: 84%; height: auto; }
.s .nm { display: flex; align-items: center; gap: 12px; font-size: 40px; font-weight: 900; letter-spacing: -0.02em; }
.s .nm.en { font-family: 'IDisp'; }
.s .ds { font-size: 24px; font-weight: 500; color: rgba(255,255,255,0.55); margin-top: 4px; }
"""
    yt = ('<svg width="48" height="34" viewBox="0 0 28 20"><path d="M27.4 3.1A3.5 3.5 0 0 0 24.9.6C22.7 0 14 0 14 0S5.3 0 3.1.6A3.5 3.5 0 0 0 .6 3.1C0 5.3 0 10 0 10s0 4.7.6 6.9a3.5 3.5 0 0 0 2.5 2.5C5.3 20 14 20 14 20s8.7 0 10.9-.6a3.5 3.5 0 0 0 2.5-2.5C28 14.7 28 10 28 10s0-4.7-.6-6.9z" fill="#FF0000"/>'
          '<path d="M11.2 14.3 18.4 10l-7.2-4.3z" fill="#FFFFFF"/></svg>')
    ig = ('<svg width="92" height="92" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.2"><rect x="2.5" y="2.5" width="19" height="19" rx="5.5"/>'
          '<circle cx="12" cy="12" r="4.3"/><circle cx="17.6" cy="6.4" r="0.6" fill="#FFFFFF" stroke="none"/></svg>')
    body = f"""<div class="tr">04 / 04</div>
<div class="main"><div class="av"><img src="{uri(B/'aboutlol_profile2.png')}"></div>
<div class="h">{ig}aboutlol.kr</div><div class="d">팔로우하고 다음 소식 받기</div></div>
<div class="subs">
<div class="s"><div class="av site"><img src="{uri(B/'aboutlol_wordmark.png')}"></div><div><div class="nm en">aboutlol.com</div><div class="ds">롤 전적 분석 · 리뷰 · 강의</div></div></div>
<div class="s"><div class="av"><img src="{uri(B/'rolgaenam.png')}"></div><div><div class="nm">{yt}롤깨남</div><div class="ds">취미로 롤 분석하는 사람</div></div></div>
</div>"""
    return page(body, css)


def validate(m):
    assert len(m['teams']) == 2, 'teams 는 2팀'
    for t in m['teams']:
        assert len(t['players']) == 5, f"{t['name']}: 선수 5명 필요"
        for p in t['players']:
            assert p['pos'] in POS, f"pos 는 {POS} 중 하나: {p}"
            assert 0 <= float(p['rating']) <= 10, f"평점 0~10: {p}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec')
    ap.add_argument('--out')
    args = ap.parse_args()
    m = json.loads(pathlib.Path(args.spec).read_text(encoding='utf-8'))
    validate(m)
    out = pathlib.Path(args.out or HERE / 'out' / m['slug']).resolve()
    out.mkdir(parents=True, exist_ok=True)
    a, b = m['teams']
    cards = [('01_cover', cover(m, out)),
             (f"02_{a.get('logo') or 'team_a'}", team_card(m, 0, '02')),
             (f"03_{b.get('logo') or 'team_b'}", team_card(m, 1, '03')),
             ('04_end', outro())]
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--allow-file-access-from-files'])
        pg = br.new_page(viewport={'width': 1080, 'height': 1350}, device_scale_factor=1)
        for name, doc in cards:
            h = out / f'{name}.html'
            h.write_text(doc, encoding='utf-8')
            pg.goto(h.as_uri())
            pg.evaluate('document.fonts.ready')
            pg.wait_for_timeout(300)
            png = out / f'{name}.png'
            pg.screenshot(path=str(png))
            Image.open(png).convert('RGB').save(out / f'{name}.jpg', quality=92, subsampling=0)
            print(png)
        br.close()


if __name__ == '__main__':
    main()
