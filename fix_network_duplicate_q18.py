# -*- coding: utf-8 -*-
import json, re
from pathlib import Path
root=Path(__file__).resolve().parent
text=(root/'data.js').read_text(encoding='utf-8')
lessons=json.loads(re.match(r'window\.LESSONS\s*=\s*(.*);\s*$', text, re.S).group(1))
q18a = {
    'source': '网络样例题 Q18a', 'type': '单选', 'question': '深度学习可以具有几个隐藏层()。',
    'options': ['A、1个','B、2个','C、3个','D、4个'], 'answer': 'B、2个', 'rawAnswer': 'B',
    'placementReason': '完整题库集中收录。', 'note': '原题编号显示为 18；为避免与后面“多分类”题重复，记为 Q18a。'
}
q18b = {
    'source': '网络样例题 Q18b', 'type': '单选', 'question': '两种以上(不含两种)的分类问题被称为()。',
    'options': ['A、二分类','B、多分类','C、分类器','D、归一化'], 'answer': 'B、多分类', 'rawAnswer': 'B',
    'placementReason': '完整题库集中收录。', 'note': '原题编号也显示为 18；为避免与前面“深度学习隐藏层”题重复，记为 Q18b。'
}
for l in lessons:
    # mapped lessons
    if l['id']=='ch6-03-dnn-cnn-params':
        for p in l.get('practiceItems',[]):
            if p.get('source')=='网络样例题 Q18' and '深度学习可以具有' in p.get('question',''):
                p.update(q18a); p['placementReason']='放在深度网络层数/DNN 考点。'; p['note']=q18a['note']
    if l['id']=='ch8-03-ai-applications':
        for p in l.get('practiceItems',[]):
            # This was originally Q18b but got overwritten by duplicate Q18.
            if p.get('source')=='网络样例题 Q18' and '深度学习可以具有' in p.get('question',''):
                p.update(q18b); p['placementReason']='多分类属于 AI 应用中的分类任务。'; p['note']=q18b['note']
    if l['id']=='bank-network-full':
        items=[]; inserted=False
        for p in l.get('practiceItems',[]):
            if p.get('source')=='网络样例题 Q18' and '深度学习可以具有' in p.get('question',''):
                item=dict(q18a); items.append(item)
                items.append(dict(q18b)); inserted=True
            else:
                items.append(p)
        if not inserted:
            items.append(dict(q18a)); items.append(dict(q18b))
        l['practiceItems']=items

practice_total=sum(len(l.get('practiceItems',[]) or []) for l in lessons)
unique_sources=len({p.get('source') for l in lessons for p in (l.get('practiceItems',[]) or []) if p.get('source')})
zju=len([p for l in lessons if l['id']=='bank-zju-full' for p in l.get('practiceItems',[])])
net=len([p for l in lessons if l['id']=='bank-network-full' for p in l.get('practiceItems',[])])
lines=['# 逐考点 Review 日志（第三轮：完整题目版）','',f'总页面/考点数：{len(lessons)}',f'题目放置总数（含完整题库重复收录）：{practice_total}',f'唯一题源数：{unique_sources}',f'浙大完整题：{zju}',f'网络完整题：{net}', '说明：网络样例题原文有两个编号 18，已拆为 Q18a 和 Q18b；网络题 Q68 在原始 docx 中题干截断，只保留可见文本并标注，不编造。','','| 序号 | 章节 | 页面/考点 | 完整题目数 | PPT/资料 | 三轮自审 |','|---:|---|---|---:|---|---|']
for l in lessons:
    lines.append(f"| {l['order']} | {l['chapter']} | {l['title']} | {len(l.get('practiceItems',[]) or [])} | 通过 | 通过 |")
(root/'review-log.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(root/'data.js').write_text('window.LESSONS = '+json.dumps(lessons,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
print('practice_total',practice_total,'unique_sources',unique_sources,'zju',zju,'net',net)
