# -*- coding: utf-8 -*-
"""飞书课堂手册 XML 源稿校验器（feishuke-skill 通用检查）。

用法:
  python verify_manual.py <xml1> [<xml2> ...]     # 显式文件
  python verify_manual.py --dir <目录>            # 检查目录下 manual_lesson*.xml
  python verify_manual.py --dir <目录> --expect-img 2 --expect-h2 4
  python verify_manual.py <xml> --profile live    # 线上手改版式（h2 允许 3 或 4、总览表可缺）
  python verify_manual.py <xml> --img-mode any    # 截图数量不限（线上版含大量操作截图）

检查项:
  - 无 BOM / 无游离 & / title 存在（允许 xx年xx月xx日 与 2026-0x-xx 占位）
  - 标签白名单（v1.1 含 h4/grid/column/sheet/pre/code/blockquote/a）
  - h2 数量（默认期望 4：课前准备/课堂流程总览/课点N/课点N+1；profile=live 时允许 3–4）
  - h3 环节编号 ①②③… 连续无跳号
  - 总览表（表头含"时间"+"学习活动"）时间轴 0→90 连续无空档重叠（profile=live 时可缺）
  - img 数量（默认期望=课点数，即 2；--img-mode any 时不校验数量）
退出码 0=全过；1=有 FAIL。
"""
import io
import re
import sys
import glob

NUM = '①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱'

# v1.1 标签白名单（v1.0.1 + 线上手改版新增）
ALLOWED_TAGS = set('''title h1 h2 h3 h4 h5 h6 p b i u s em strong a span callout checkbox
hr br img table colgroup col thead tbody tr th td ol ul li source cite blockquote
code pre sheet grid column mark sub sup'''.split())
# 飞书 DocxXML 明确不支持、出现即需改写的块
BANNED_HINTS = {'details': '折叠块不支持', 'iframe': 'iframe 不支持'}


def check(path, expect_img=2, expect_h2=4, profile='v101', img_mode='exact'):
    fails, notes = [], []
    t = io.open(path, encoding='utf-8').read()
    if t.startswith('\ufeff'):
        fails.append('BOM')
    if re.search(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9A-Fa-f]+;)', t):
        fails.append('raw &')
    if not re.search(r'<title[^>]*>.+?</title>', t, re.S):
        fails.append('no title')
    # 标签白名单
    tags = set(re.findall(r'</?([a-zA-Z][a-zA-Z0-9]*)', t))
    unknown = sorted(tags - ALLOWED_TAGS)
    if unknown:
        fails.append('未知标签 %s（若为飞书新版式请加入白名单）' % ','.join(unknown))
    for b, why in BANNED_HINTS.items():
        if b in tags:
            fails.append('禁用标签 <%s>：%s' % (b, why))
    # h2
    h2s = re.findall(r'<h2[^>]*>(.*?)</h2>', t, re.S)
    if profile == 'live':
        if len(h2s) not in (3, 4):
            fails.append('h2=%d (live 允许 3–4)' % len(h2s))
    elif len(h2s) != expect_h2:
        fails.append('h2=%d (expect %d)' % (len(h2s), expect_h2))
    # h3 编号连续
    h3s = re.findall(r'<h3[^>]*>(.*?)</h3>', t, re.S)
    idx = 0
    for h in h3s:
        first = re.sub(r'<[^>]+>', '', h).strip()
        if first and first[0] in NUM:
            idx += 1
            if first[0] != NUM[idx - 1]:
                fails.append('h3 编号跳号 @%s' % first[:12])
    notes.append('h3=%d' % len(h3s))
    # 总览表时间轴
    tables = re.findall(r'<table>.*?</table>', t, re.S)
    ov = None
    for tb in tables:
        head = re.search(r'<thead.*?</thead>', tb, re.S)
        if head and '时间' in head.group(0) and ('学习活动' in head.group(0) or '我们一起' in head.group(0)):
            ov = tb
            break
    if ov is None:
        if profile == 'live':
            notes.append('总览表=无(live 允许)')
        else:
            fails.append('未找到总览表')
    else:
        body = re.search(r'<tbody>(.*?)</tbody>', ov, re.S)
        rows = re.findall(r'<tr>(.*?)</tr>', body.group(1), re.S) if body else []
        spans = []
        for r in rows:
            m = re.search(r'(\d+)\s*[–—-]\s*(\d+)\s*′', r)
            if m:
                spans.append((int(m.group(1)), int(m.group(2))))
        notes.append('总览行=%d' % len(spans))
        if not spans:
            fails.append('总览无时间行')
        else:
            if spans[0][0] != 0:
                fails.append('总览起点=%d≠0' % spans[0][0])
            if spans[-1][1] != 90:
                fails.append('总览终点=%d≠90' % spans[-1][1])
            for a, b in zip(spans, spans[1:]):
                if a[1] != b[0]:
                    fails.append('时间空档/重叠 %d–%d → %d–%d' % (a[0], a[1], b[0], b[1]))
                if a[1] <= a[0]:
                    fails.append('行区间非法 %d–%d' % (a[0], a[1]))
    # img
    imgs = re.findall(r'<img ', t)
    notes.append('img=%d' % len(imgs))
    if img_mode == 'exact' and len(imgs) != expect_img:
        fails.append('img=%d (expect %d)' % (len(imgs), expect_img))
    return fails, notes


def main():
    args = sys.argv[1:]
    profile, img_mode = 'v101', 'exact'
    if '--profile' in args:
        i = args.index('--profile')
        profile = args[i + 1]
        del args[i:i + 2]
    if '--img-mode' in args:
        i = args.index('--img-mode')
        img_mode = args[i + 1]
        del args[i:i + 2]
    kw = {}
    if '--expect-img' in args:
        i = args.index('--expect-img')
        kw['expect_img'] = int(args[i + 1])
        del args[i:i + 2]
    if '--expect-h2' in args:
        i = args.index('--expect-h2')
        kw['expect_h2'] = int(args[i + 1])
        del args[i:i + 2]
    files = []
    if args and args[0] == '--dir':
        files = sorted(glob.glob(args[1] + r'\manual_lesson*.xml')) if '\\' in args[1] else sorted(glob.glob(args[1] + '/*.xml'))
    else:
        files = args
    allfail = 0
    for f in files:
        try:
            fails, notes = check(f, profile=profile, img_mode=img_mode, **kw)
        except Exception as e:
            fails, notes = ['exception: %s' % e], []
        status = 'PASS' if not fails else 'FAIL'
        if fails:
            allfail += 1
        print('%s [%s] %s' % (status, f, ' | '.join(notes)))
        for x in fails:
            print('    - ' + x)
    sys.exit(1 if allfail else 0)


if __name__ == '__main__':
    main()
