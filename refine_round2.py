# -*- coding: utf-8 -*-
import json, re
from pathlib import Path

root = Path(__file__).resolve().parent
text = (root / 'data.js').read_text(encoding='utf-8')
lessons = json.loads(re.match(r'window\.LESSONS\s*=\s*(.*);\s*$', text, re.S).group(1))
by_id = {l['id']: l for l in lessons}

def ensure(lid):
    l = by_id[lid]
    l.setdefault('pptDeepDive', [])
    l.setdefault('supplementItems', [])
    l.setdefault('imageSupplements', [])
    l.setdefault('practiceItems', [])
    return l

def p(lid, source, typ, question, answer, reason, options=None, note=None):
    item = {'source': source, 'type': typ, 'question': question, 'answer': answer, 'placementReason': reason}
    if options: item['options'] = options
    if note: item['note'] = note
    ensure(lid)['practiceItems'].append(item)

def sup(lid, source, title, content):
    ensure(lid)['supplementItems'].append({'source': source, 'title': title, 'content': content})

def deep(lid, title, points):
    ensure(lid)['pptDeepDive'].append({'title': title, 'points': points})

def make_lesson(id, chapter, order, title, subtitle, evidence, intent, learning, exam, traps, answers, quiz):
    return {
        'id': id, 'status': 'ready', 'chapter': chapter, 'order': order, 'title': title, 'subtitle': subtitle,
        'sourceEvidence': evidence, 'intent': intent, 'learning': learning, 'exam': exam,
        'traps': traps, 'answers': answers, 'quiz': quiz,
        'review': {'sourceChecked': True, 'teachesFromScratch': True, 'examAligned': True, 'selfReviewed': True,
                   'reviewNote': '第二轮精修新增：根据 PPT 与样例题补充到正确考点。'}
    }

def sec(heading, body, bullets):
    return {'heading': heading, 'body': body, 'bullets': bullets}

def ex(type_, question, answer):
    return {'type': type_, 'question': question, 'answer': answer}

def ans(title, text):
    return {'title': title, 'text': text}

def quiz(question, options, correct, explain):
    return {'question': question, 'options': options, 'correct': correct, 'explain': explain}

# Convert existing evidence into a strict PPT supplement block so every lesson visibly carries course-material text.
for l in lessons:
    l.setdefault('pptDeepDive', [])
    if not l['pptDeepDive']:
        pts = [f"{e.get('ref','资料')}：{e.get('quote','')}" for e in l.get('sourceEvidence', [])]
        if pts:
            l['pptDeepDive'].append({'title': '本考点课件/资料摘录再核对', 'points': pts})

# Add missing sample-question-driven lessons and insert them before final review.
new_lessons = []
new_lessons.append(make_lesson(
    'ch3-04-mcts', '第三章', '16.1', '蒙特卡洛树搜索 MCTS（样例题补充）', '样例题明确考 MCTS：采样搜索，不是穷举。',
    [{'ref':'第3章 蒙特卡洛搜索.pptx', 'quote':'MCTS 与 AlphaGo 相关，包含选择、扩展、模拟、反向传播。'}, {'ref':'浙大样例题 Q6','quote':'MCTS 不是穷举式枚举搜索。'}],
    ['样例题直接出现 MCTS，因此单独补成考点，放在搜索章节 Alpha-Beta 后。', '要记住四步和“基于采样而非穷举”。'],
    [sec('MCTS 是什么', ['蒙特卡洛树搜索通过多次采样模拟来估计节点价值，适合围棋这类搜索空间巨大、不能完全穷举的问题。'], ['基于采样。','用于博弈树。','有限时间内把搜索集中到更有希望的分支。']), sec('四个步骤', ['Selection 选择、Expansion 扩展、Simulation 模拟、Backpropagation 回传。模拟结果会更新路径上节点的访问次数和胜率。'], ['选择。','扩展。','模拟。','回传。'])],
    [ex('选择题','MCTS 描述不正确的是“穷举式枚举搜索”。','正确，它是基于采样的搜索。')],
    ['不要把 MCTS 当成 BFS/DFS 穷举。','四步中最后一步是回传，不是反向传播神经网络梯度。'],
    [ans('MCTS 模板','MCTS 是基于随机采样和模拟的博弈树搜索方法，典型步骤为选择、扩展、模拟和回传；它不是穷举搜索，而是在有限计算量下估计各行动价值。')],
    [quiz('MCTS 是否是穷举式搜索？',['不是，是采样搜索','是，必须枚举所有叶子','只是一种排序算法'],0,'MCTS 通过采样模拟估计价值，不穷举全部状态。')]
))
new_lessons.append(make_lesson(
    'ch3-05-game-nash', '第三章', '16.2', '博弈论与纳什均衡（样例题补充）', '放在对抗搜索之后，用来处理样例题中的纳什均衡。',
    [{'ref':'浙大样例题 Q14','quote':'纳什均衡不一定是最优局势；纳什均衡是一种稳定局势。'}, {'ref':'第3章 对抗搜索课件','quote':'对抗搜索研究竞争环境中一方最大化、另一方最小化的问题。'}],
    ['纳什均衡不是复习要点主线，但样例题出现，所以放在对抗搜索之后。','需要掌握：稳定不等于全局最优。'],
    [sec('纳什均衡', ['纳什均衡指在其他参与者策略不变时，任何一方单独改变策略都不能获得更好收益，因此它是一种稳定局势。'], ['稳定。','单方无动机改变。','不等于整体最优。']), sec('和对抗搜索的关系', ['对抗搜索假设对手理性选择对我不利的行动；博弈论也研究多方策略互动，但纳什均衡强调稳定策略组合。'], ['都研究多智能体。','对抗搜索常用于零和博弈。','纳什均衡可用于非零和博弈。'])],
    [ex('判断题','“纳什均衡一定是最优局势”是否正确？','错误。纳什均衡是稳定局势，不一定最优。')],
    ['不要把稳定局势等同于最优局势。','囚徒困境中的纳什均衡体现了个体稳定但整体未必最好。'],
    [ans('纳什均衡模板','纳什均衡是一个稳定策略组合：在其他参与者策略不变时，任何一方单独改变策略都不能获得更好收益；它不一定是整体最优局势。')],
    [quiz('纳什均衡一定最优吗？',['不一定','一定','只在 CNN 中成立'],0,'样例题明确把“一定最优”作为错误说法。')]
))
new_lessons.append(make_lesson(
    'ch5-13-bagging-boosting', '第五章', '30.1', 'Bagging、Boosting 与 AdaBoost（样例题补充）', '样例题多次考 Boosting/AdaBoost，补到机器学习章节。',
    [{'ref':'第4章_机器学习-统计学习_3_提升算法.pptx:11-20','quote':'Bagging 使用 bootstrap 采样并投票/平均；Boosting 调整错分样本权重，串行生成弱模型；随机森林是代表性 Bagging。'}, {'ref':'浙大样例题 Q9/Q18','quote':'Boosting 与 AdaBoost 权重调整是样例题重点。'}],
    ['虽然复习要点没有单列 Boosting，但老师样例题明确考到，必须放进机器学习章节。','和随机森林同属集成学习，但机制不同。'],
    [sec('Bagging', ['Bagging 通过 bootstrap 有放回采样得到多个训练子集，分别训练多个弱模型，分类时投票、回归时平均。随机森林是典型 Bagging。'], ['并行。','降低方差。','样本随机。']), sec('Boosting', ['Boosting 串行训练弱模型，后一个模型更关注前面分错的样本，最后把多个弱模型加权组合为强模型。'], ['串行。','关注错分样本。','弱模型加权组合。']), sec('AdaBoost', ['AdaBoost 中错分样本权重增加，正确样本权重降低；表现更好的弱分类器在最终投票中权重更大。'], ['错分样本权重增加。','弱分类器权重由错误率决定。','不是每轮都随便改每个弱分类器权重。'])],
    [ex('判断题','错分样本权重减少、正确样本权重增加。','错误，AdaBoost 正好相反。')],
    ['Bagging 并行，Boosting 串行。','AdaBoost 增加错分样本权重。','随机森林是 Bagging，不是 Boosting。'],
    [ans('集成学习模板','Bagging 通过 bootstrap 采样训练多个相对独立模型并投票/平均，代表是随机森林；Boosting 串行训练弱模型，使后续模型关注错分样本，最终加权组合，AdaBoost 是典型 Boosting。')],
    [quiz('AdaBoost 中错分样本权重如何变化？',['增加','减少','固定为 0'],0,'错分样本会被后续弱分类器重点关注。')]
))
new_lessons.append(make_lesson(
    'ch5-14-svm-supplement', '第五章', '30.2', 'SVM 支持向量机（样例题补充）', '网络样例题考 SVM 最优分界面，由支持向量决定。',
    [{'ref':'机器学习算法-3-支持向量机.pptx','quote':'SVM 通过最大化分类间隔寻找最优超平面，支持向量决定分界面。'}, {'ref':'网络样例题 Q49','quote':'SVM 的最优分界面由支持向量决定。'}],
    ['SVM 不在复习要点主列表中，但补充题出现，必须放到监督学习算法附近。','最需要记住“最大间隔”和“支持向量”。'],
    [sec('SVM 思想', ['SVM 寻找能分开类别且间隔最大的超平面。离分界面最近的关键样本叫支持向量，它们决定最优分界面。'], ['最大间隔。','支持向量。','分类超平面。']), sec('软间隔和核技巧', ['数据不可完全线性可分时，软间隔允许少量误分类；核技巧可把数据映射到高维空间处理非线性边界。'], ['软间隔。','惩罚参数 C。','核函数。'])],
    [ex('选择题','SVM 的最优分界面由什么决定？','支持向量。')],
    ['不是所有样本都决定分界面，关键是支持向量。','SVM 是监督学习分类算法。'],
    [ans('SVM 模板','SVM 是监督学习分类算法，通过寻找最大间隔超平面进行分类，离超平面最近并决定间隔的样本称为支持向量，最优分界面主要由支持向量决定。')],
    [quiz('SVM 最优分界面主要由什么决定？',['支持向量','所有样本平均值','PCA 主成分'],0,'支持向量是离边界最近的关键样本。')]
))

# Insert new lessons before final review if not already present.
existing = {l['id'] for l in lessons}
insert_at = next((i for i,l in enumerate(lessons) if l['id']=='final-review-map'), len(lessons))
for nl in new_lessons:
    if nl['id'] not in existing:
        lessons.insert(insert_at, nl)
        by_id[nl['id']] = nl
        existing.add(nl['id'])
        insert_at += 1

# Supplement materials from doc4/doc5.
sup('ch2-06-quantifiers', '4 命题和谓词的符号化---复习参考', '谓词符号化例题集中放这里', [
    '小李比小赵高：L(x,y) 表示 x 比 y 高，a=小李，b=小赵，则 L(a,b)。',
    '无锡位于南京和上海之间：P(x,y,z) 表示 x 位于 y 和 z 之间，a=无锡，b=南京，c=上海，则 P(a,b,c)。',
    '凡是有理数均可表成分数：若个体域为实数，应写 ∀x(R(x)->A(x))。',
    '每个自然数都是实数：∀x(N(x)->R(x))。',
    '对于任意 x，存在 y，使 x+y=5：∀x∃yH(x,y)。',
    '没有不呼吸的人：¬∃x(M(x)∧¬F(x))。',
    '素数不全是奇数：∃x(P(x)∧¬O(x))。',
    '所有大学生都爱学习：∀x(S(x)->L(x))。',
    '注意：原补充资料中个别“有些 A 是 B”写成蕴含形式，考试建议按标准逻辑写 ∃x(A(x)∧B(x))。'
])
sup('ch2-07-predicate-inference', '5 谓词推理---复习要点-new', '谓词推理四个证明例题放这里', [
    '技巧：先整理成量词在前的形式；有存在量词先做存在指定 EI；有全称量词再做全称指定 UI；最后按需要做存在推广 EG 或全称推广 UG。',
    '例1：∀x(P(x)->D(x)) 与 P(c) 可推出 D(c)：先 UI 得 P(c)->D(c)，再 MP。',
    '例2：∀x(F(x)->G(x)), ∃xF(x) => ∃xG(x)：EI 得 F(c)，UI 得 F(c)->G(c)，MP 得 G(c)，EG 得 ∃xG(x)。',
    '例3：∀x(F(x)->G(x)), ∃x(F(x)∧H(x)) => ∃x(G(x)∧H(x))：EI、合取消去、UI、MP、合取引入、EG。',
    '例4：F1:∀x(P(x)->(Q(x)∧R(x))), F2:∃x(P(x)∧S(x)), G:∃x(S(x)∧R(x))：由 F2 得 P(c),S(c)，由 F1 得 R(c)，合取得 S(c)∧R(c)，再 EG。'
])
# Alpha-beta image supplements.
imgs = sorted((root/'assets'/'alpha-beta').glob('*'))
for idx, img in enumerate(imgs, 1):
    ensure('ch3-03-alpha-beta-calculation')['imageSupplements'].append({
        'src': f"assets/alpha-beta/{img.name}",
        'title': f"Alpha-Beta 剪枝补充题图 {idx}",
        'alt': f"Alpha-Beta 剪枝补充题图 {idx}"
    })

# PPT strict extra notes for some lessons.
deep('ch3-04-mcts', '课件关键词：MCTS 四步', ['选择 Selection：沿树选择最值得探索的节点。', '扩展 Expansion：添加新子节点。', '模拟 Simulation：从新节点模拟到终局。', '回传 Backpropagation：把胜负结果更新到路径节点。'])
deep('ch5-13-bagging-boosting', '课件关键词：Bagging 与 Boosting 对比', ['Bagging 弱模型不存在强依赖关系，可并行生成。', 'Boosting 弱模型有强依赖关系，串行生成。', '随机森林是最有代表性的 Bagging 算法。'])
deep('ch8-03-ai-applications', '课件关键词：CV 与 NLP 应用', ['计算机视觉：图像分类回答 what，目标检测回答 what & where，分割回答像素级 what & where。', 'NLP：文本分类把文档分到预定义类别，文本聚类按内容相似度自动分组。'])

# Zhejiang sample questions Q1-Q20.
p('ch1-01-ai-concept-origin','浙大样例题 Q1','单选','标志着人工智能走上人类历史舞台的事件是？','B：1955 年 Dartmouth AI 夏季研讨会提议报告。','考 AI 起源，放在 AI 概念与起源考点。')
p('ch5-02-supervised','浙大样例题 Q2','单选','前者和后者之间存在真子集关系的是？','B：监督学习、机器学习。','考监督学习属于机器学习的子集。')
p('ch2-03-proposition-logic','浙大样例题 Q3','单选','若 a->b 为真，哪个命题一定为真？','C：该命题的逆否命题。','考蕴含与逆否命题等价。')
p('ch3-01-greedy-astar','浙大样例题 Q4','单选','贪婪最佳优先搜索和 A* 都需要的辅助信息是？','C：任意城市与目标城市之间的直线距离。','考启发函数 h(n)。')
p('ch3-02-adversarial-alpha-beta','浙大样例题 Q5','单选','Alpha-Beta 剪枝搜索描述不正确的是？','A：节点位置先后次序不会影响搜索效率。','节点顺序会影响剪枝效率，放在 Alpha-Beta 概念。')
p('ch3-04-mcts','浙大样例题 Q6','单选','MCTS 描述不正确的是？','B：是一种穷举式枚举的搜索方法。','MCTS 是采样搜索，不是穷举。')
p('ch5-05-loss-functions','浙大样例题 Q7','单选','期望风险和经验风险描述正确的是？','D：期望风险是真实分布期望损失，经验风险是训练样本平均损失。','考损失、风险和统计学习。')
p('ch5-08-linear-regression','浙大样例题 Q8','单选','线性回归描述不正确的是？','D：线性回归模型训练是非监督学习方法。','线性回归是监督学习。')
p('ch5-13-bagging-boosting','浙大样例题 Q9','单选','Boosting 描述不正确的是？','D：每一轮迭代均会更改每个弱分类器的权重。','考 Boosting/AdaBoost 权重机制。')
p('ch5-10-pca','浙大样例题 Q10','单选','PCA 和特征人脸描述不正确的是？','D：原始 n*n 人脸图像，特征人脸维度是其一半。','考 PCA/特征脸降维，不是简单一半。')
p('ch6-03-dnn-cnn-params','浙大样例题 Q11','单选','CNN 相比前馈网络还需要自动优化的参数是？','C：卷积矩阵（卷积核）。','考 CNN 可学习参数。')
p('ch6-04-conv-layer','浙大样例题 Q12','单选','卷积操作描述不正确的是？','A：卷积矩阵参数手工事先指定且图像间不共享。','卷积核参数由训练学习且权值共享。')
p('ch7-03-value-functions','浙大样例题 Q13','单选','强化学习中如何得到最优策略？','A：每步选择使未来反馈期望最大的动作。','考长期期望回报，不是即时奖励。')
p('ch3-05-game-nash','浙大样例题 Q14','单选','博弈论和纳什均衡描述不正确的是？','B：纳什均衡是一种最优局势。','纳什均衡是稳定局势，不一定最优。')
p('ch1-05-alphago','浙大样例题 Q15','单选','哪个系统利用课程至少三个方面内容？','B：Alpha Go。','AlphaGo 综合搜索、深度学习、强化学习等。')
p('final-review-map','浙大样例题 Q16','多选','机器学习算法中哪些需要事先指定参数或信息？','A、B、D。','跨考点综合题，放在总复习，同时相关点已分散补到 CNN、AdaBoost、K-means。')
p('final-review-map','浙大样例题 Q17','多选','从研究范畴来说，哪些说法正确？','A、B、C、D。','跨章节层级关系综合题，放在总复习。')
p('ch5-13-bagging-boosting','浙大样例题 Q18','判断','AdaBoost 中当前弱分类器分错样本则减少该样本权重，否则增大权重。','B：错误。','错分样本权重应增加。')
p('ch1-05-alphago','浙大样例题 Q19','判断','2016 年 AlphaGo 只是通过无监督学习机制训练。','B：错误。','AlphaGo 使用监督学习、强化学习、深度学习和搜索。')
p('ch5-07-discriminative-generative','浙大样例题 Q20','判断','GAN 中生成网络区别真伪，判别网络产生虚拟数据。','B：错误。','原文未显示答案；按概念判断：生成器产生数据，判别器辨别真伪。')

# Online sample questions visible in doc3.
p('ch4-01-python-libraries','网络样例题 Q1','单选','哪个库不属于大数据分析和处理的三剑客？','A：seaborn。','考 Python 库用途。')
p('ch8-03-ai-applications','网络样例题 Q2','单选','不属于自然语言处理核心环节的是？','D：语音语义识别。','放在 NLP 应用考点。')
p('ch5-01-ml-stat-learning','网络样例题 Q3','单选','有特征、有部分标签的机器学习属于？','B：半监督学习。','补充机器学习类型。')
p('ch8-03-ai-applications','网络样例题 Q4','单选','哪种神经网络更适合自然语言处理？','B：RNN。','放在 NLP/RNN 内容下。')
p('ch4-02-preprocessing-onehot','网络样例题 Q5','单选','关于归一化不正确的是？','资料答案：B。','归一化/标准化考点。','网络题答案与常规定义不完全一致；本课按课件重点记：归一化和标准化要区分。')
p('ch1-01-ai-concept-origin','网络样例题 Q6','单选','不属于人工智能研究基本内容的是？','C：自动化。','AI 基本内容概念题。')
p('ch6-04-conv-layer','网络样例题 Q7','单选','卷积神经网络的主要特点是具有？','C：卷积操作。','CNN 卷积层核心。')
p('ch6-03-dnn-cnn-params','网络样例题 Q18','单选','深度学习可以具有几个隐藏层？','资料答案：B。','放在深度网络层数考点。','网络题表述较旧；本课课件强调深度模型有更多层，通常多个隐藏层。')
p('ch5-03-unsupervised','网络样例题 Q9','单选','寻找数据相似性并划分组的方法称为？','D：聚类。','聚类定义。')
p('ch5-01-ml-stat-learning','网络样例题 Q10','单选','AI、机器学习、深度学习三者关系正确的是？','C。','考 AI/ML/DL 层级关系。')
p('ch5-03-unsupervised','网络样例题 Q11','单选','关联规则中置信度的含义是？','资料答案：C；概念校正更接近 D。','关联规则属于无监督补充。','该网络题疑似把支持度/置信度混淆；考试若考标准定义，置信度是 P(后项|前项)。')
p('ch5-04-similarity','网络样例题 Q12','单选','哪个方法不是用于计算相似度？','C：均方根误差 RMSE。','相似度公式考点。')
p('ch5-02-supervised','网络样例题 Q13','单选','不能对给定样本进行分类的是？','C：梯度下降算法。','梯度下降是优化方法，不是分类器。')
p('ch5-05-loss-functions','网络样例题 Q14','单选','梯度下降法的目标是？','B：寻找损失函数的最小值。','损失和优化考点。')
p('ch1-02-turing','网络样例题 Q15','单选','图灵测试的含义是？','A：隔开人和机器提问，无法确认哪个是机器则通过。','图灵测试考点。')
p('ch5-09-kmeans','网络样例题 Q16','单选','关于聚类说法正确的是？','D：聚类质心就是各簇群特征的平均值。','K-means 中心更新。')
p('ch8-03-ai-applications','网络样例题 Q17','单选','买《机器学习》后平台可能推荐哪本书？','A：《人工智能》。','推荐系统应用，基于相似性/关联。')
p('ch8-03-ai-applications','网络样例题 Q18b','单选','两种以上的分类问题称为？','B：多分类。','分类应用。')
p('ch6-03-dnn-cnn-params','网络样例题 Q19','单选','CNN 中用来完成分类的是？','C：全连接层。','CNN 结构补充。')
p('ch5-02-supervised','网络样例题 Q20','单选','分类器测试的作用是？','D：检验分类器的效果。','监督分类流程。')
p('ch6-03-dnn-cnn-params','网络样例题 Q21','单选','深度神经网络与基本神经网络区别是？','C：隐含层个数不同。','DNN 层数考点。')
p('ch6-04-conv-layer','网络样例题 Q22','单选','关于卷积层说法错误的是？','B：卷积核参数值是人为指定的。','卷积核参数是学习得到。')
p('ch5-09-kmeans','网络样例题 Q41','单选','K 均值聚类算法属于？','B：无监督学习。','K-means 考点。')
p('ch1-01-ai-concept-origin','网络样例题 Q42','单选','不属于人工智能研究基本内容的是？','C：自动化。','AI 研究内容概念题。')
p('ch5-03-unsupervised','网络样例题 Q43','单选','有特征、无标签的机器学习是？','C：无监督学习。','无监督定义。')
p('ch6-03-dnn-cnn-params','网络样例题 Q44','单选','何种情况下神经网络被称为深度学习模型？','A：加入更多层，使网络层数增加。','深度网络层数。')
p('ch5-01-ml-stat-learning','网络样例题 Q45','单选','机器学习中的从数据中学习通常不包含？','资料答案：B：强化学习。','机器学习范畴补充。','本课程复习要点明确把强化学习作为机器学习/AI 重要内容单列；考试本课时优先按课件。')
p('ch4-01-python-libraries','网络样例题 Q46','单选','matplotlib 的作用是？','C：制作图表。','可视化库。')
p('ch6-02-bp-calculation','网络样例题 Q47','单选','BP 算法的直接作用是？','B：加快/训练权值参数和偏置参数。','BP 用于训练参数。')
p('ch6-05-pooling','网络样例题 Q48','单选','池化层的作用不包括？','D：实现特征分类。','池化不负责分类。')
p('ch5-14-svm-supplement','网络样例题 Q49','单选','SVM 的最优分界面由什么决定？','A：支持向量。','SVM 补充考点。')
p('ch1-01-ai-concept-origin','网络样例题 Q50','单选','哪些不是 AI 概念的正确表述？','D：人工智能将其定义为人类智能体的研究。','AI 定义辨析。')
p('ch5-02-supervised','网络样例题 Q51','单选','分类器构造和实施步骤描述错误的是？','C：在训练样本上执行分类模型生成预测结果。','预测评估应在测试集上做。')
p('ch8-03-ai-applications','网络样例题 Q52','单选','不属于家中 AI 产品的是？','C：声控灯。','AI 应用辨析。')
p('ch5-02-supervised','网络样例题 Q53','单选','把样本所属类型和样本对应起来称为？','C：标注。','监督学习标签。')
p('ch6-03-dnn-cnn-params','网络样例题 Q54','单选','图像识别成功率提升的主要因素有？','A：计算力提升。','深度学习发展条件补充。')
p('ch8-02-ai-attacks-defenses','网络样例题 Q60','单选','AI 研发和应用政策应把什么置于核心？','B：人。','AI 安全/伦理补充。')
p('ch5-03-unsupervised','网络样例题 Q61','单选','无监督学习可完成什么任务？','C：聚类。','无监督学习任务。')
p('ch8-03-ai-applications','网络样例题 Q62','单选','以下哪个不是图像基本运算？','B：块运算。','计算机视觉应用补充。')
p('ch5-01-ml-stat-learning','网络样例题 Q63','单选','机器学习主要特点是？','A：通过算法从大数据中学习如何完成任务。','机器学习概念。')
p('ch5-08-linear-regression','网络样例题 Q64','计算/单选','线性回归方程 y=0.849x-85.712，x=172 时预测体重？','B：约 60.316kg。','线性回归计算。')
p('ch8-03-ai-applications','网络样例题 Q65','单选','计算机显示器使用的颜色模型是？','D：RGB。','CV 基础补充；原文未显示答案，按常识判断。')
p('ch1-01-ai-concept-origin','网络样例题 Q66','单选','人工智能是研究、开发用于模拟、延伸和扩展人的什么？','A：智能。','AI 定义原句。')
p('ch8-03-ai-applications','网络样例题 Q67','单选','OpenCV 主要应用领域是？','A：计算机视觉和机器学习。','CV 工具补充。')
p('final-review-map','网络样例题 Q68','截断题','原文只剩“初始化采...”且题干不完整。','无法可靠作答。','题目截断，放在总复习说明未纳入考核答案。','原始提取文本不完整，避免编造。')

# Update final review count later; write files.
(root / 'data.js').write_text('window.LESSONS = ' + json.dumps(lessons, ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
print(f'refined lessons={len(lessons)} practice={sum(len(l.get("practiceItems", [])) for l in lessons)} supplements={sum(len(l.get("supplementItems", [])) for l in lessons)} images={sum(len(l.get("imageSupplements", [])) for l in lessons)}')
