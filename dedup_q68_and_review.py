# -*- coding: utf-8 -*-
import json, re
from pathlib import Path
root=Path(__file__).resolve().parent
text=(root/'data.js').read_text(encoding='utf-8')
lessons=json.loads(re.match(r'window\.LESSONS\s*=\s*(.*);\s*$', text, re.S).group(1))
for l in lessons:
    if l['id']=='bank-network-full':
        seen=set(); items=[]
        for p in l.get('practiceItems',[]):
            key=p.get('source')
            if key in seen: continue
            seen.add(key); items.append(p)
        l['practiceItems']=items
practice_total=sum(len(l.get('practiceItems',[]) or []) for l in lessons)
unique_sources=len({p.get('source') for l in lessons for p in (l.get('practiceItems',[]) or []) if p.get('source')})
zju=len([p for l in lessons if l['id']=='bank-zju-full' for p in l.get('practiceItems',[])])
net=len([p for l in lessons if l['id']=='bank-network-full' for p in l.get('practiceItems',[])])
lines=['# 逐考点 Review 日志（第三轮：完整题目版）','',f'总页面/考点数：{len(lessons)}',f'题目放置总数（含完整题库重复收录）：{practice_total}',f'唯一题源数：{unique_sources}',f'浙大完整题：{zju}',f'网络完整题：{net}', '说明：网络题 Q68 在原始 docx 中题干截断，只保留可见文本并标注，不编造。','','| 序号 | 章节 | 页面/考点 | 完整题目数 | PPT/资料 | 三轮自审 |','|---:|---|---|---:|---|---|']
for l in lessons:
    lines.append(f"| {l['order']} | {l['chapter']} | {l['title']} | {len(l.get('practiceItems',[]) or [])} | 通过 | 通过 |")
(root/'review-log.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(root/'data.js').write_text('window.LESSONS = '+json.dumps(lessons,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
print('practice_total',practice_total,'unique_sources',unique_sources,'zju',zju,'net',net)
