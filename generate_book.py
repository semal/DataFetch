# coding=utf-8
import os
import sys

reload(sys)
sys.setdefaultencoding('utf8')
import json

fo = open(sys.argv[1])
res = json.load(fo)
fo.close()
try:
    os.mkdir('%s' % res[0]['book_title'])
except OSError:
    pass

fa = open('%s.md' % res[0]['book_title'], 'w')
fa.write("""title: %s
date: 2012-05-07 13:01:05
category:
  - 小说
tag:
  - %s
---
""" % (res[0]['book_title'], res[0]['book_title']))
for k in sorted(res, key=lambda x: int(x['chapter_order'])):
    chapter_name = '第{:d}章 {chapter_name}'.format(
        int(k['chapter_order']),
        chapter_name=k['chapter_name'].split()[-1]
    )
    fo = open('%s/%s.md' % (k['book_title'], chapter_name), 'w')
    pre = """title: %s
categories:
  - 小说
  - %s
tag:
  - %s
date: 2012-05-07 12:01:05
show: hide
---
""" % (chapter_name, k['book_title'], k['book_title'])
    fo.write(pre)
    for p in k['chapter_content']:
        fo.write('%s\n\n' % p.strip())
    fo.close()
    fa.write('## [%s](../%s/%s)\n\n' % (chapter_name, k['book_title'], chapter_name))
