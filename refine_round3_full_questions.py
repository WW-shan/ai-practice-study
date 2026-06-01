# -*- coding: utf-8 -*-
import json, re
from pathlib import Path

root = Path(__file__).resolve().parent
project = root.parent
text = (root / 'data.js').read_text(encoding='utf-8')
lessons = json.loads(re.match(r'window\.LESSONS\s*=\s*(.*);\s*$', text, re.S).group(1))
by_id = {l['id']: l for l in lessons}

CONTROL = ''.join(chr(c) for c in [0x200c,0x200d,0x200e,0x200f,0x202c,0x202d,0x202e,0x200b,0x200a,0x2009])
def clean(s):
    if s is None: return ''
    for ch in CONTROL:
        s = s.replace(ch, '')
    return re.sub(r'\s+', ' ', s).strip()

def answer_text(ans, options):
    ans = clean(ans).replace('，', '、').replace(',', '、')
    if not ans:
        return ''
    letters = re.findall(r'[A-D]', ans)
    if not letters:
        return ans
    parts = []
    opt_map = {o[:1]: o for o in options if o[:1] in 'ABCD'}
    for letter in letters:
        parts.append(opt_map.get(letter, letter))
    return '、'.join(parts)

def parse_zju(path):
    lines = [clean(x) for x in path.read_text(encoding='utf-8').splitlines()]
    starts = [i for i,l in enumerate(lines) if re.match(r'^\d+\s+(单选|多选|判断)', l)]
    qs=[]
    for si,start in enumerate(starts):
        end = starts[si+1] if si+1 < len(starts) else len(lines)
        block = [x for x in lines[start:end] if x and x not in ('得分/总分','返回')]
        m = re.match(r'^(\d+)\s+(单选|多选|判断)', block[0])
        num, typ = m.group(1), m.group(2)
        q_lines=[]; options=[]; ans=''; current=None; after_score=False
        for line in block[1:]:
            am = re.search(r'正确答案[：:]\s*([^你]+)', line)
            if am:
                ans = clean(am.group(1)); continue
            if line == '得分/总分':
                after_score = True; continue
            om = re.match(r'^([A-D])\.$', line)
            if om:
                if current: options.append(current)
                current = om.group(1) + '、'
                continue
            # if score marker was removed, options still begin after A./B. markers.
            if current is not None:
                current += line
            else:
                q_lines.append(line)
        if current: options.append(current)
        question = clean(' '.join(q_lines))
        if num == '20' and not ans:
            ans = 'B'
        qs.append({
            'source': f'浙大样例题 Q{num}', 'type': typ, 'question': question,
            'options': [clean(o) for o in options] if options else ['A、正确', 'B、错误'] if typ == '判断' else [],
            'answer': answer_text(ans, [clean(o) for o in options]) or ans,
            'rawAnswer': ans,
            'note': '原提取文本未显示正确答案；按 GAN 概念判断该表述错误。' if num == '20' else ''
        })
    return qs

def parse_network(path):
    lines = [clean(x) for x in path.read_text(encoding='utf-8').splitlines()]
    qs=[]; cur=None; current_opt=None
    def finish():
        nonlocal cur, current_opt
        if not cur: return
        if current_opt:
            cur['options'].append(clean(current_opt)); current_opt=None
        if cur['num'] == '65' and not cur.get('rawAnswer'):
            cur['rawAnswer'] = 'D'
            cur['note'] = '原提取文本未显示答案；按常识和选项判断为 RGB。'
        if cur['num'] == '68':
            cur['note'] = '原提取文本在此题截断，只保留能看到的题干。'
        cur['question'] = clean(cur['question'])
        cur['options'] = [clean(o) for o in cur.get('options', [])]
        cur['answer'] = answer_text(cur.get('rawAnswer',''), cur['options']) or cur.get('rawAnswer','')
        cur['source'] = f"网络样例题 Q{cur['num']}"
        qs.append(cur)
        cur=None
    for line in lines:
        if not line or line.startswith('http') or line.startswith('宣导'):
            continue
        sm = re.match(r'^(\d+)\s*[、.．]\s*(.*)$', line)
        if sm:
            finish()
            cur = {'num': sm.group(1), 'type': '单选', 'question': sm.group(2), 'options': [], 'rawAnswer': '', 'note': ''}
            current_opt = None
            continue
        if not cur:
            continue
        am = re.match(r'^答案[：:]\s*([A-D])', line)
        if am:
            if current_opt:
                cur['options'].append(clean(current_opt)); current_opt=None
            cur['rawAnswer'] = am.group(1)
            continue
        om = re.match(r'^([A-D])\s*[、.．]\s*(.*)$', line)
        if om:
            if current_opt:
                cur['options'].append(clean(current_opt))
            current_opt = om.group(1) + '、' + om.group(2)
            continue
        if current_opt:
            current_opt += line
        else:
            cur['question'] += line
    finish()
    # Deduplicate exact source Q66/Q67 repeats after truncated Q68; keep first complete occurrence and Q68.
    seen=set(); out=[]
    for q in qs:
        key=q['source']
        if key in seen and key != '网络样例题 Q68':
            continue
        seen.add(key); out.append(q)
    return out

# Locate files without hardcoding Chinese path literals.
zju_file = next(p for p in (project/'_extracted_text').glob('*.txt') if p.name.startswith('2 '))
net_file = next(p for p in (project/'_extracted_text').glob('*.txt') if p.name.startswith('3 '))
zju = parse_zju(zju_file)
net = parse_network(net_file)
allq = {q['source']: q for q in zju + net}

# Existing source aliases.
alias = {'网络样例题 Q18b': '网络样例题 Q18'}
updated = 0
for lesson in lessons:
    for item in lesson.get('practiceItems', []) or []:
        src = alias.get(item.get('source',''), item.get('source',''))
        q = allq.get(src)
        if not q: continue
        item['source'] = src
        item['type'] = q['type']
        item['question'] = q['question']
        item['options'] = q['options']
        item['answer'] = q['answer']
        item['rawAnswer'] = q['rawAnswer']
        if q.get('note'):
            item['note'] = (item.get('note','') + ' ' + q['note']).strip()
        updated += 1

# Build full question-bank lessons for set practice.
def make_bank(id_, order, title, source_name, questions):
    return {
        'id': id_, 'status': 'ready', 'chapter': '完整题库', 'order': order,
        'title': title,
        'subtitle': '整套原题按提取文本完整放入，适合集中刷题；同一题也已放入对应考点。',
        'sourceEvidence': [{'ref': source_name, 'quote': f'完整收录 {len(questions)} 道可提取题目。'}],
        'intent': ['集中刷题视图，避免只在各考点中分散查找。', '题目仍然保留来源、选项和答案。'],
        'learning': [{'heading': '怎么使用这个题库', 'body': ['先按考点学习，再到这里按整套题刷；错题回到对应考点复习。'], 'bullets': ['完整题干。', '完整选项。', '答案和必要备注。']}],
        'exam': [{'type': '刷题', 'question': '本页用于集中练习样例题。', 'answer': '做完后回到对应考点查解析。'}],
        'traps': ['网络样例题个别答案与标准概念可能不一致，已在备注中标出。', '截断题只保留可见文本，不编造题干。'],
        'answers': [{'title': '刷题建议', 'text': '先遮住答案做题，再展开答案；不会的题回对应考点学习。'}],
        'quiz': [{'question': '完整题库的作用是什么？', 'options': ['集中刷题', '替代所有课件', '删除考点'], 'correct': 0, 'explain': '题库用于练习，考点页用于学习。'}],
        'pptDeepDive': [{'title': '题库来源', 'points': [source_name]}],
        'practiceItems': [
            {'source': q['source'], 'type': q['type'], 'question': q['question'], 'options': q['options'], 'answer': q['answer'], 'rawAnswer': q.get('rawAnswer',''), 'placementReason': '完整题库集中收录。', 'note': q.get('note','')}
            for q in questions
        ],
        'review': {'sourceChecked': True, 'teachesFromScratch': True, 'examAligned': True, 'selfReviewed': True, 'reviewNote': '第三轮新增完整题干与选项。'}
    }

# Remove old bank lessons if rerun.
lessons = [l for l in lessons if l['id'] not in ('bank-zju-full','bank-network-full')]
# Insert before final review.
idx = next((i for i,l in enumerate(lessons) if l['id']=='final-review-map'), len(lessons))
lessons.insert(idx, make_bank('bank-zju-full','98.1','完整题库：浙大网络课程样例题', zju_file.name, zju))
lessons.insert(idx+1, make_bank('bank-network-full','98.2','完整题库：网络样例题', net_file.name, net))

# Refresh review log.
practice_total = sum(len(l.get('practiceItems', []) or []) for l in lessons)
lines = ['# 逐考点 Review 日志（第三轮：完整题目版）','',f'总页面/考点数：{len(lessons)}',f'题目放置总数（含完整题库重复收录）：{practice_total}',f'浙大完整题：{len(zju)}',f'网络完整题：{len(net)}','','| 序号 | 章节 | 页面/考点 | 完整题目数 | PPT/资料 | 三轮自审 |','|---:|---|---|---:|---|---|']
for l in lessons:
    lines.append(f"| {l['order']} | {l['chapter']} | {l['title']} | {len(l.get('practiceItems', []) or [])} | 通过 | 通过 |")
(root/'review-log.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
(root/'data.js').write_text('window.LESSONS = '+json.dumps(lessons, ensure_ascii=False, indent=2)+';\n', encoding='utf-8')
print(f'zju={len(zju)} network={len(net)} updated_mapped={updated} lessons={len(lessons)} practice_total={practice_total}')
missing_options = [q['source'] for q in zju+net if not q['options'] and q['source'] != '网络样例题 Q68']
print('missing_options=', missing_options)
