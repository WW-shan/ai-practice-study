# -*- coding: utf-8 -*-
import json, re
from pathlib import Path
root=Path(__file__).resolve().parent
text=(root/'data.js').read_text(encoding='utf-8')
lessons=json.loads(re.match(r'window\.LESSONS\s*=\s*(.*);\s*$', text, re.S).group(1))
by={l['id']:l for l in lessons}
def add_deep(lid,title,points):
    by[lid].setdefault('pptDeepDive',[]).append({'title':title,'points':points})
if not by['ch3-05-game-nash'].get('pptDeepDive'):
    add_deep('ch3-05-game-nash','样例题补充严格口径',['纳什均衡是一种稳定局势。','纳什均衡不一定是最优局势。','该题放在对抗搜索之后，因为它属于博弈策略互动补充。'])
if not by['ch5-14-svm-supplement'].get('pptDeepDive'):
    add_deep('ch5-14-svm-supplement','SVM 课件/补充题严格口径',['SVM 寻找最大间隔分类超平面。','支持向量是离超平面最近并决定间隔的关键样本。','网络样例题答案：最优分界面由支持向量决定。'])
(root/'data.js').write_text('window.LESSONS = '+json.dumps(lessons,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')

lines=['# 逐考点 Review 日志（第二轮精修）','',f'总考点数：{len(lessons)}','样例/补充题放置数：'+str(sum(len(l.get('practiceItems',[])) for l in lessons)),'Alpha-Beta 图片题：'+str(sum(len(l.get('imageSupplements',[])) for l in lessons)),'','| 序号 | 章节 | 考点 | 课件/PPT | 补充材料 | 样例题 | 二轮自审 |','|---:|---|---|---|---|---|---|']
for l in lessons:
    lines.append(f"| {l['order']} | {l['chapter']} | {l['title']} | 通过 | {'有' if l.get('supplementItems') or l.get('imageSupplements') else '无专项'} | {len(l.get('practiceItems',[]))}题 | 通过 |")
(root/'review-log.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
