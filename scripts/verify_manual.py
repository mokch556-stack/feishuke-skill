# -*- coding: utf-8 -*-
"""飞书课堂手册 XML 源稿校验器（feishuke-skill 通用检查）。

用法:
  python verify_manual.py <xml1> [<xml2> ...]     # 显式文件
  python verify_manual.py --dir <目录>            # 检查目录下 manual_lesson*.xml
  python verify_manual.py --dir <目录> --expect-img 2 --expect-h2 4

检查项:
  - 无 BOM / 无游离 & / title 存在（允许 xx年xx月xx日 占位）
  - h2 数量（默认期望 4：课前准备/课堂流程总览/课点N/课点N+1）
  - h3 环节编号 ①②③… 连续无跳号
  - 总览表（表头含"时间"+"学习活动"）时间轴 0→90 连续无空档重叠
  - img 数量（默认期望=课点数，即 2）
退出码 0=全过；1=有 FAIL。
"""
import io
import re
import sys
import glob

NUM = '①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱'

def check(path, expect_img=2, expect_h2=4):
    fails, notes = [], []
    t = io.open(path, encoding='utf-8').read()
    if t.startswith('\ufeff'):
        fails.append('BOM')
    if re.search(r'&(?!amp;|lt;|gt;|quot;|apos;)', t):
        fails.append('raw &')
    if not re.search(r'<title[^>]*>.+?</title>', t, re.S):
        fails.append('no title')
    h2s = re.findall(r'<h2[^>]*>(.*?)</h2>', t, re.S)
    if len(h2s) != expect_h2:
        fails.append('h2=%d (expect %d)' % (len(h2s), expect_h2))
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
    imgs = re.findall(r'<img ', t)
    if len(imgs) != expect_img:
        fails.append('img=%d (expect %d)' % (len(imgs), expect_img))
    return fails, notes

def main():
    args = sys.argv[1:]
    files = []
    if args and args[0] == '--dir':
        files = sorted(glob.glob(args[1] + r'\manual_lesson*.xml')) if '\\' in args[1] else sorted(glob.glob(args[1] + '/*.xml'))
    else:
        files = args
    allfail = 0
    for f in files:
        try:
            fails, notes = check(f)
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
