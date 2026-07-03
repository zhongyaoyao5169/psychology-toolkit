#!/usr/bin/env python3
"""扩充实验详情字段并写入 data/experiments.json"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT = BASE / "data" / "experiments.json"

# 在原有字段基础上追加 detail 内容
DETAILS = {
    "wundt-reaction-time": {
        "background": "教材第一章「实验心理学的由来」以费希纳、冯特、艾宾浩斯三位学者串联实验心理学诞生史。19 世纪亥姆霍兹已在生理实验室测量神经传导与反应时间；冯特在莱比锡将这一传统发展为系统的心理学实验范式，主张心理过程可分解与测量。",
        "participants": "经过严格训练的大学生被试，需能配合内省报告并在反应键上稳定作答。",
        "variables": {"iv": "任务类型（简单 / 选择 / 辨别反应时）", "dv": "刺激呈现至按键反应的时间（ms）", "control": "刺激强度、呈现间隔、练习遍数、实验环境（隔音与光线）"},
        "steps": [
            {"title": "实验装置与情境", "text": "被试坐在隔音、光线可控的小室中，仅通过窗口与主试通讯。刺激器可呈现光或声信号，被试需在感知刺激后尽快按下反应键，实验室 chronoscope 记录时间间隔。", "image": "assets/wundt-reaction-time-setup.svg"},
            {"title": "任务类型与流程", "text": "简单反应时：单一刺激对应单一反应；选择反应时：多种刺激对应不同按键；辨别反应时：先辨别刺激类别再反应。每种条件重复多次取平均，并比较不同任务间的差异。", "image": "assets/wundt-reaction-time-flow.svg"},
            {"title": "内省与记录", "text": "被试在反应后简要报告主观体验（如是否意识到刺激性质），主试将反应时数据与内省报告对照，分析心理过程各阶段所占时间。"},
        ],
        "resultsDetail": "反应时随任务复杂度系统增加；冯特由此论证心理内容可被实验分解，但内省报告的可信度亦受到后世持续讨论。",
    },
    "ebbinghaus-forgetting": {
        "background": "教材第一章第三节以艾宾浩斯为例说明：高级心理过程同样可被实验化。艾宾浩斯反对「记忆不可测量」的观点，用节省法与无意义音节材料，首次对遗忘进行定量研究。",
        "participants": "以自身为主被试，长期、反复进行自我实验（节省法）。",
        "variables": {"iv": "学习后时间间隔", "dv": "再学习所需遍数（节省率）", "control": "无意义音节材料、学习遍数、朗读节奏"},
        "steps": [
            {"title": "材料与学习", "text": "自编无意义音节（如 DAX、BOK），避免已有意义联想干扰。按顺序朗读直至能在一次回忆中正确背出整张表，记录达到标准所需遍数。", "image": "assets/ebbinghaus-forgetting-setup.svg"},
            {"title": "间隔保持与再学习", "text": "在学习完成后分别等待 20 分钟、1 小时、9 小时、1 天、2 天……直至 31 天，再进行再学习至同一标准，记录第二次所需遍数。", "image": "assets/ebbinghaus-forgetting-flow.svg"},
            {"title": "计算节省率", "text": "节省率 =（首次学习遍数 − 再学习遍数）/ 首次学习遍数 × 100%，以节省率作为保持量的指标，绘制随时间变化的遗忘曲线。"},
        ],
        "resultsDetail": "遗忘在学习后最初迅速发生，随后速度趋缓，呈典型的对数型下降曲线，即「先快后慢」规律。",
    },
    "pavlov-conditioning": {
        "background": "巴甫洛夫原研究消化生理，注意到狗在仅听到喂食者脚步声时也会分泌唾液，由此转向条件反射机制的系统研究。",
        "participants": "健康实验犬，部分实验配合唾液腺导管手术以便精确计量。",
        "variables": {"iv": "条件刺激（CS）与无条件刺激（US）的配对", "dv": "唾液分泌量", "control": "刺激强度、配对次数、间隔、非配对对照"},
        "steps": [
            {"title": "建立基准", "text": "测量食物（US）单独呈现时的唾液分泌（UR），以及铃声等中性刺激（CS）单独呈现时的反应（应接近零）。", "image": "assets/pavlov-conditioning-setup.svg"},
            {"title": "配对训练", "text": "在 CS 呈现后或同时呈现 US，重复数十次。记录 CS 单独呈现时是否出现唾液分泌（CR）。", "image": "assets/pavlov-conditioning-flow.svg"},
            {"title": "泛化、分化与消退", "text": "测试与 CS 相似的刺激是否引发反应（泛化）；训练被试区分 CS+ 与 CS−；停止 US 配对后观察 CR 如何减弱（消退）。"},
        ],
        "resultsDetail": "中性刺激经配对可获得条件反应；条件反射遵循获得、消退、自发恢复、泛化与分化等规律，成为学习心理学基础模型。",
    },
    "thorndike-puzzle-box": {
        "background": "桑代克受达尔文进化论影响，试图用动物实验研究学习的机制，反对「推理」或「顿悟」主导动物行为的观点。",
        "participants": "饥饿的猫（及其他动物如小鸡、狗等后续研究）。",
        "variables": {"iv": "练习次数 / 迷笼难度", "dv": "逃出所需时间、错误动作次数", "control": "饥饿程度、食物奖赏、装置结构"},
        "steps": [
            {"title": "迷笼装置", "text": "将猫置于箱内，箱外可见食物。箱门由内部杠杆或拉环控制，猫需通过特定动作才能开门取食。", "image": "assets/thorndike-puzzle-box-setup.svg"},
            {"title": "试误过程", "text": "猫在箱内乱抓、乱咬、乱撞，偶然触发机关后门打开。多次重复后，无效动作减少，正确反应潜伏期缩短。", "image": "assets/thorndike-puzzle-box-flow.svg"},
            {"title": "效果律总结", "text": "桑代克归纳：满意后果加强刺激—反应联结，不满意后果削弱联结，提出效果律、练习律与准备律。"},
        ],
        "resultsDetail": "学习是渐进的 S-R 联结建立，而非推理洞察；这一范式为行为主义学习理论奠定经验基础。",
    },
    "wertheimer-phi": {
        "background": "1910 年韦特海默在火车旅途中注意到灯光似在移动，回到实验室用 tachistoscope 精确控制刺激间隔，验证「似动」现象。",
        "participants": "正常视觉的被试（含韦特海默本人及同事）。",
        "variables": {"iv": "两刺激时间间隔（ISI）与空间距离", "dv": "被试报告（静止两点 / 似动 / 融合）", "control": "亮度、视角、背景暗度"},
        "steps": [
            {"title": "刺激呈现", "text": "在暗室中依次点亮两个空间分离的光点 A 与 B，精确调节出现的时间间隔 Δt。", "image": "assets/wertheimer-phi-setup.svg"},
            {"title": "被试判断", "text": "当 Δt 适中时，被试报告看到单一光点在 A、B 间移动（Φ 现象），而非两个独立闪烁。", "image": "assets/wertheimer-phi-flow.svg"},
            {"title": "完形解释", "text": "知觉组织优先于感觉元素相加；整体结构（运动轨迹）在意识中直接呈现，无法还原为孤立点知觉之和。"},
        ],
        "resultsDetail": "似动现象证明知觉具有整体性，成为格式塔心理学反对构造主义元素分析的核心证据。",
    },
    "kohler-insight": {
        "background": "苛勒在加那利群岛特内里费岛猩猩研究站，系统观察黑猩猩在自然情境中的问题解决，与桑代克试误学习形成对照。",
        "participants": "笼养黑猩猩（如苏丹等著名个体）。",
        "variables": {"iv": "工具有无、情境布局", "dv": "问题解决潜伏期、尝试模式", "control": "食物动机、熟悉度、工具可用性"},
        "steps": [
            {"title": "叠箱取香蕉", "text": "香蕉悬于天花板，地面有散放木箱。猩猩先随意尝试，随后突然将箱叠起站上去取食，错误动作骤减。", "image": "assets/kohler-insight-setup.svg"},
            {"title": "棍棒取食", "text": "提供两根可接合或单根够不到的棍棒，猩猩在停顿后组合或使用工具，一次性完成取食。", "image": "assets/kohler-insight-flow.svg"},
            {"title": "顿悟特征", "text": "成功前常有停顿、环视；一旦理解整体关系，行为立即正确，体现「啊哈」式领悟而非盲目试误。"},
        ],
        "resultsDetail": "高级问题解决包含对情境整体的洞察，格式塔「顿悟学习」挑战纯联结主义解释。",
    },
    "watson-little-albert": {
        "background": "华生主张情绪与思维一样可还原为 S-R 联结，试图用婴儿实验证明恐惧可被条件反射习得。",
        "participants": "11 个月大的「小阿尔伯特」（真实身份后有学术争议）。",
        "variables": {"iv": "白鼠（CS）与巨响（US）配对", "dv": "对白鼠及类似毛茸物的恐惧反应", "control": "配对前对白鼠无恐惧基线"},
        "steps": [
            {"title": "基线评估", "text": "呈现白鼠、兔子、狗、无毛发物等，记录阿尔伯特是否表现恐惧（配对前对白鼠无恐惧）。", "image": "assets/watson-little-albert-setup.svg"},
            {"title": "恐惧条件化", "text": "每当阿尔伯特伸手触摸白鼠，实验者在身后敲击金属棒发出巨响（US），重复若干次配对。", "image": "assets/watson-little-albert-flow.svg"},
            {"title": "泛化测试", "text": "仅呈现白鼠时阿尔伯特哭泣、退缩；对兔子、圣诞老人面具等毛茸刺激也出现恐惧，显示刺激泛化。"},
        ],
        "resultsDetail": "情绪反应可通过经典条件作用建立并泛化；实验因伦理问题（未消除恐惧）备受批评，但影响深远。",
    },
    "skinner-operant": {
        "background": "斯金纳区分经典条件反射（应答性）与操作性条件反射（自发行为受后果塑造），设计可控环境研究强化程序。",
        "participants": "饥饿的白鼠或鸽子。",
        "variables": {"iv": "强化程序（比率 / 间隔、固定 / 变动）", "dv": "杠杆按压频率、反应模式", "control": "剥夺程度、强化物数量、箱内刺激"},
        "steps": [
            {"title": "斯金纳箱", "text": "动物在隔音箱内自由活动，按压杠杆可能触发食物投放（强化物），计算机记录每次反应的时间与频率。", "image": "assets/skinner-operant-setup.svg"},
            {"title": "塑造与强化", "text": "起初任意接近杠杆的行为被强化，逐步要求更接近完整按压（行为塑造）；随后切换不同强化程序观察反应率曲线。", "image": "assets/skinner-operant-flow.svg"},
            {"title": "消退与惩罚", "text": "停止强化后反应频率下降（消退）；引入电击等惩罚或移除厌恶刺激，分析其对反应的影响。"},
        ],
        "resultsDetail": "行为后果决定反应概率；不同强化程序产生 characteristic 反应模式，为应用行为分析提供技术基础。",
    },
    "stroop-effect": {
        "background": "教材第六章将 Stroop 效应列为「本章实验一」，用以说明注意选择与自动化加工冲突。1935 年 Stroop 发现命名字体颜色时，词义会自动干扰颜色命名。",
        "participants": "大学生被试。",
        "variables": {"iv": "词义—颜色一致 vs 冲突", "dv": "命名颜色反应时、错误率", "control": "字体、呈现时间、练习顺序"},
        "steps": [
            {"title": "三种条件", "text": "① 读字（词义任务）；② 命名色块颜色；③ 命名字体颜色而忽略词义（Stroop 任务）。", "image": "assets/stroop-effect-setup.svg"},
            {"title": "冲突试次", "text": "呈现「红」字但用绿色油墨印刷等不一致试次，被试需抑制自动阅读，仅报告颜色。", "image": "assets/stroop-effect-flow.svg"},
            {"title": "测量与比较", "text": "记录每种条件下 100 个试次的平均反应时；Stroop 条件显著慢于色块条件，错误率亦升高。"},
        ],
        "resultsDetail": "自动化阅读加工难以关闭，与颜色命名竞争认知资源，成为测量执行控制与注意的标杆任务。",
    },
    "piaget-conservation": {
        "background": "皮亚杰通过「临床法」与儿童对话，发现逻辑概念（如守恒）随年龄逐步建构，而非先天或单纯学习。",
        "participants": "3–11 岁儿童，按阶段分组。",
        "variables": {"iv": "液体 / 数量 / 重量排列方式", "dv": "守恒判断（是否认为量改变）", "control": "等量初始状态、主试提问方式"},
        "steps": [
            {"title": "液体守恒", "text": "向儿童展示两杯等量液体，将其中一杯倒入高瘦量杯，询问「哪边多或一样多」。", "image": "assets/piaget-conservation-setup.svg"},
            {"title": "数量与重量守恒", "text": "将相同数量纽扣排成不同行距，或相同重量黏土捏成不同形状，重复提问。", "image": "assets/piaget-conservation-flow.svg"},
            {"title": "阶段差异", "text": "前运算阶段儿童常回答「高的那边多」；具体运算阶段（约 7–11 岁）逐步理解数量不随外观排列改变。"},
        ],
        "resultsDetail": "认知发展经历可逆性、去中心化等逻辑能力获得，守恒是具体运算阶段的重要指标。",
    },
    "asch-conformity": {
        "background": "阿希受二战从众与宣传现象触动，在清晰知觉情境中检验个体是否会因群体压力而违背 obvious 事实。",
        "participants": "123 名美国大学生，每小组 1 真被试 + 若干假被试（同谋）。",
        "variables": {"iv": "同谋是否一致给出错误答案", "dv": "真被试从众选错的比例", "control": "线段长度差异、座位顺序"},
        "steps": [
            {"title": "线条判断任务", "text": "呈现标准线段与三条比较线，被试依次公开报告哪条与标准等长（答案 obvious）。", "image": "assets/asch-conformity-setup.svg"},
            {"title": "同谋操纵", "text": "前几试 everyone 正确；关键试中所有同谋一致选错，观察真被试是否跟随错误多数。", "image": "assets/asch-conformity-flow.svg"},
            {"title": "事后访谈", "text": "询问被试意识到冲突时的感受：是「真的看见不同」还是「不想显得格格不入」。"},
        ],
        "resultsDetail": "约 37% 的试次出现从众错误，75% 被试至少从众一次；规范压力可压倒清晰知觉证据。",
    },
    "milgram-obedience": {
        "background": "米尔格拉姆在艾希曼审判背景下，探究普通人在权威指令下是否会伤害他人，挑战「只有恶人才会作恶」的直觉。",
        "participants": "纽黑文地区 40 岁男性市民（后扩展多样样本）。",
        "variables": {"iv": "实验者权威压力、受害者距离", "dv": "施加的最高电击档位", "control": "电击装置实为模拟、学习者实为同谋"},
        "steps": [
            {"title": "角色分配", "text": "抽签决定「教师」与「学习者」（抽签被操纵，真被试恒为教师）。学习者被绑在椅子上，电极连接（假）。", "image": "assets/milgram-obedience-setup.svg"},
            {"title": "记忆—惩罚任务", "text": "教师朗读词对，学习者答错则按指令施加逐级电击（15V–450V），实验者在旁要求「请继续，实验要求您继续」。", "image": "assets/milgram-obedience-flow.svg"},
            {"title": "压力与终止", "text": "学习者在 150V 后不再回应，教师表现出焦虑但仍多数在权威敦促下继续；若拒绝三次才停止。"},
        ],
        "resultsDetail": "约 65% 被试执行到 450V 最高档；情境、权威与角色分工强烈塑造服从，引发巨大伦理讨论。",
    },
    "bandura-bobo": {
        "background": "班杜拉质疑行为主义仅强调直接强化，提出观察学习：个体通过观看榜样行为及其后果而习得新反应。",
        "participants": "36 名学龄前儿童，随机分组。",
        "variables": {"iv": "观看攻击榜样 / 非攻击榜样 / 无榜样", "dv": "随后对波波玩偶的攻击行为频率", "control": "挫折诱发、实验室玩具设置"},
        "steps": [
            {"title": "榜样阶段", "text": "儿童观看成人对 inflatable 波波玩偶踢打、用锤敲击或安静玩耍的影片或现场示范。", "image": "assets/bandura-bobo-setup.svg"},
            {"title": "挫折诱发", "text": "随后儿童被带入有玩具的房间，不久实验者以「这些玩具要给别的小朋友」为由收走，留下波波玩偶。", "image": "assets/bandura-bobo-flow.svg"},
            {"title": "观察反应", "text": "单向玻璃后记录儿童是否模仿攻击动作、言语及使用锤子等，比较三组差异。"},
        ],
        "resultsDetail": "观看攻击榜样的儿童显著更多攻击行为；证明观察学习无需直接强化即可发生。",
    },
    "festinger-dissonance": {
        "background": "费斯汀格提出认知失调：相互矛盾的认知产生不适，个体通过改变态度或行为恢复一致。",
        "participants": "斯坦福大学修读心理学导论的学生。",
        "variables": {"iv": "撒谎报酬（1 美元 vs 20 美元）", "dv": "对枯燥任务的真实喜爱程度评分", "control": "任务实际无聊程度、同谋配合"},
        "steps": [
            {"title": "枯燥任务", "text": "被试长时间转动栓钉、整理线轴等无聊活动，建立对任务的负面态度。", "image": "assets/festinger-dissonance-setup.svg"},
            {"title": "撒谎要求", "text": "主试请被试向下一位「被试」（同谋）谎称任务很有趣，报酬仅 1 或 20 美元。", "image": "assets/festinger-dissonance-flow.svg"},
            {"title": "态度测量", "text": "撒谎后填写问卷，评价任务有趣程度、是否愿意再做、对实验的科学价值等。"},
        ],
        "resultsDetail": "1 美元组比 20 美元组更倾向报告任务有趣——低外部理由促使改变态度以减少「我为小钱撒谎」的失调。",
    },
    "zimbardo-prison": {
        "background": "津巴多探讨情境与角色标签如何快速改变正常大学生行为，原计划进行两周模拟监狱研究。",
        "participants": "经心理筛选的 24 名斯坦福男性大学生，随机分派看守或囚犯。",
        "variables": {"iv": "角色（看守 / 囚犯）", "dv": "行为指标、情绪、权力行使", "control": "随机分配、统一规则（后随情境崩解）"},
        "steps": [
            {"title": "角色启动", "text": "「囚犯」在自家被「逮捕」、搜身、换囚服、分配编号；「看守」配警棍、墨镜与制服。", "image": "assets/zimbardo-prison-setup.svg"},
            {"title": "模拟监狱生活", "text": "在斯坦福心理学系地下室 24 小时生活，看守负责点名、劳动与惩戒；囚犯需服从规则。", "image": "assets/zimbardo-prison-flow.svg"},
            {"title": "提前终止", "text": "仅 6 天即因看守虐待、囚犯极端应激与研究者卷入而中止；显示情境力量之强与伦理风险。"},
        ],
        "resultsDetail": "角色与权力结构迅速内化，正常学生出现去个体化与虐待；实验成为情境论与伦理反思的标志性案例。",
    },
    "loftus-misinformation": {
        "background": "洛夫特斯研究事件后信息如何与原始记忆互动，质疑记忆是固定录像带的观念。",
        "participants": "大学生被试观看交通事故等短片。",
        "variables": {"iv": "提问措辞（碰撞 vs 撞碎）或植入的虚假细节", "dv": "速度估计、虚假细节回忆率", "control": "同一视频、随机分配问题"},
        "steps": [
            {"title": "观看事件", "text": "被试观看汽车相撞短片，之后离开一段时间或立即接受提问。", "image": "assets/loftus-misinformation-setup.svg"},
            {"title": "误导性提问", "text": "「两辆车接触时的速度大约多少？」vs「撞碎时的速度？」；或在问卷中加入未出现的「停止标志」。", "image": "assets/loftus-misinformation-flow.svg"},
            {"title": "记忆测试", "text": "一周后询问细节，比较不同提问组对速度估计与虚假物体回忆的差异。"},
        ],
        "resultsDetail": "动词强度影响速度估计；约 30% 被试「回忆」出未出现的停止标志，显示记忆可被事后信息重构。",
    },
    "hawthorne": {
        "background": "1924 年起西方电气霍桑工厂研究照明与效率关系，梅奥等人随后加入，发现社会因素同样关键。",
        "participants": "继电器装配女工小组及后续多组工人。",
        "variables": {"iv": "照明强度、休息制度、工资方案等", "dv": "产量、出勤、态度", "control": "对照组、记录方式"},
        "steps": [
            {"title": "照明实验", "text": "改变工作场所照明亮度，观察产量变化；令人意外的是降低照明时产量有时仍上升。", "image": "assets/hawthorne-setup.svg"},
            {"title": "继电器组访谈", "text": "对 6 人小组进行长期观察，调整休息、点心、工时，产量持续上升 regardless of 具体改动方向。", "image": "assets/hawthorne-flow.svg"},
            {"title": "群体规范发现", "text": "非正式群体形成产量「规范」，工人因被关注与参与感提高而改变投入，即霍桑效应。"},
        ],
        "resultsDetail": "社会心理、归属感与关注本身影响绩效；推动工业心理学从纯物理条件转向人际关系研究。",
    },
    "sperry-split-brain": {
        "background": "为治疗严重癫痫，部分患者切断胼胝体。斯佩里设计巧妙任务，分别向左右半球呈现不同信息。",
        "participants": "胼胝体切开术后患者（如 W.J. 等）。",
        "variables": {"iv": "刺激呈现视野（左 / 右）", "dv": "口头报告 vs 左手选取", "control": "固视点、呈现时间"},
        "steps": [
            {"title": "半视野呈现", "text": "被试注视屏幕中央十字，快速呈现图片或文字于左侧或右侧视野（分别投射至右或左半球）。", "image": "assets/sperry-split-brain-setup.svg"},
            {"title": "双反应系统", "text": "左半球优势语言：右视野刺激可口头命名；右半球优势空间：左视野刺激只能用左手选取对应物体，无法说出名称。", "image": "assets/sperry-split-brain-flow.svg"},
            {"title": "半球功能推断", "text": "两半球可各自处理信息而互不知晓，证明功能 specialization 与意识分离的可能性。"},
        ],
        "resultsDetail": "左半球偏语言与分析，右半球偏空间与整体加工；为认知神经科学半球研究奠定里程碑。",
    },
}


SOURCE_BOOK = "郭秀艳《实验心理学》（人民教育出版社）"

BOOK_SOURCE = {
    "feichner-psychophysics": ("第一章 绪论；第五章 心理物理学", "一、费希纳；第一节 传统心理物理学"),
    "weber-law": ("第五章 心理物理学", "第二节 心理物理函数 · 韦伯定律"),
    "wundt-reaction-time": ("第一章 绪论；第四章 反应时", "二、冯特；第一节 反应时在心理学中的研究历史"),
    "donders-subtraction": ("第四章 反应时", "第三节 反应时新法 · 减数法"),
    "ebbinghaus-forgetting": ("第一章 绪论；第八章 记忆与学习", "三、艾宾浩斯；第一节 记忆的早期研究"),
    "pavlov-conditioning": ("第八章 记忆与学习", "第二节 学习的早期研究"),
    "thorndike-puzzle-box": ("第八章 记忆与学习", "第二节 学习的早期研究"),
    "wertheimer-phi": ("第七章 知觉", "第二节 视知觉和听知觉"),
    "kohler-insight": ("第八章 记忆与学习；第九章 思维", "问题解决与顿悟"),
    "watson-little-albert": ("第八章 记忆与学习", "情绪与行为的习得（拓展）"),
    "skinner-operant": ("第八章 记忆与学习", "操作性条件反射（拓展）"),
    "stroop-effect": ("第六章 注意", "本章实验一 斯特鲁普效应"),
    "piaget-conservation": ("第八章 记忆与学习", "儿童认知发展（拓展）"),
    "asch-conformity": ("社会认知拓展", "从众研究经典"),
    "milgram-obedience": ("社会认知拓展", "服从权威研究"),
    "bandura-bobo": ("社会认知拓展", "观察学习"),
    "festinger-dissonance": ("社会认知拓展", "认知失调"),
    "zimbardo-prison": ("社会认知拓展", "情境与角色"),
    "loftus-misinformation": ("第八章 记忆与学习", "错误记忆与真实记忆"),
    "hawthorne": ("应用研究拓展", "工业心理学霍桑研究"),
    "sperry-split-brain": ("附录 脑功能成像相关", "割裂脑研究"),
}

NEW_EXPERIMENTS = [
    {
        "id": "feichner-psychophysics",
        "title": "费希纳心理物理学",
        "year": 1860,
        "researcher": "古斯塔夫·费希纳",
        "category": "experimental",
        "categoryLabel": "实验心理学奠基",
        "summary": "提出心理物理学，用极限法、恒定刺激法、平均差误法建立刺激强度与感觉量的数量关系。",
        "method": "采用三种传统心理物理法测量绝对阈限与差别阈限，推导 S=k·log R。",
        "finding": "感觉量随刺激强度对数增长（费希纳定律），为心理现象量化奠定基础。",
        "significance": "教材以费希纳作为实验心理学由来第一人，标志心理学开始走向定量实验科学。",
    },
    {
        "id": "weber-law",
        "title": "韦伯定律",
        "year": 1834,
        "researcher": "恩斯特·韦伯",
        "category": "experimental",
        "categoryLabel": "实验心理学奠基",
        "summary": "差别阈限与标准刺激强度之比为常数，即 ΔI/I=K。",
        "method": "用两点阈限、重量辨别等任务，系统测量可被觉察的最小强度增量。",
        "finding": "韦伯分数在中等强度范围内近似恒定，费希纳在此基础上建立对数定律。",
        "significance": "教材第五章将其作为心理物理函数的核心定律，连接感觉测量与数学模型。",
    },
    {
        "id": "donders-subtraction",
        "title": "唐德斯减数法",
        "year": 1868,
        "researcher": "弗朗西斯·唐德斯",
        "category": "experimental",
        "categoryLabel": "实验心理学奠基",
        "summary": "用简单反应时与选择反应时之差估计「选择/辨别」心理过程耗时。",
        "method": "比较 A 反应（简单）、B 反应（选择）、C 反应（辨别）的反应时差异。",
        "finding": "复杂反应时 − 简单反应时 ≈ 特定认知加工阶段所需时间，开创减法反应时逻辑。",
        "significance": "教材第四章「反应时新法」以减数法为核心，是后续加因素法等范式的基础。",
    },
]

EXTRA_DETAILS = {
    "feichner-psychophysics": {
        "background": "教材第一章第一节「一、费希纳」：1860 年《心理物理学纲要》出版，费希纳提出「一门精确的科学分支——心理物理学」，把感觉与物理刺激强度用数学公式联系起来。",
        "participants": "正常成年被试，在控制暗适应与呈现条件的实验室中完成阈限测量。",
        "variables": {"iv": "物理刺激强度", "dv": "绝对阈限 / 差别阈限 / 主观感觉量", "control": "暗适应、呈现时长、仪器校准"},
        "steps": [
            {"title": "三种传统心理物理法", "text": "教材指出费希纳提出三种测量心理现象的方法：最小可觉差法（极限法）、正误法（恒定刺激法）与均误法（平均差误法）。它们虽从最简单的感觉过程入手，却首次用数量关系表达心理现象，使心理学可像物理学一样通过精确仪器加以测定。"},
            {"title": "心理物理学的意义", "text": "费希纳的工作建立了实验心理物理学。教材引波林评价：费希纳是实验心理物理学的始祖，把心理学带上科学道路；在实验心理学史上，除冯特外，费希纳同样可称「实验心理学之父」。其阈限思想也直接启发了后来的信号检测论。"},
            {"title": "费希纳定律", "text": "在韦伯定律 ΔI/I=K 基础上，费希纳假定差别阈限对应相等的感觉增量，得到 S=k·log R，即刺激强度 R 的对数与感觉量 S 成正比。"},
        ],
        "resultsDetail": "感觉与刺激之间可建立数量关系；三种心理物理法成为感觉实验的基本工具。",
    },
    "wundt-reaction-time": {
        "background": "教材第一章：1879 年 W.M. Wundt 在莱比锡大学建立第一个心理学实验室，以实验法研究心理现象，标志着科学心理学的诞生。",
        "participants": "莱比锡心理学实验室受训学生与受试者；教材还提到蔡元培 1907—1913 年曾在此听课。",
        "variables": {"iv": "实验任务与刺激类型", "dv": "反应时与内省报告", "control": "实验室标准化条件、仪器、练习"},
        "steps": [
            {"title": "建立实验心理学", "text": "教材指出：冯特倡导以心理现象为心理学研究对象，1879 年在莱比锡大学建立第一个心理学实验室，以实验法对心理现象作定量研究，创立实验心理学新学科。"},
            {"title": "实验室与人才培养", "text": "冯特在莱比锡实验室培养大量学生。教材统计：116 人曾在此研究心理学，其中 34 人成为著名学者，如 G.S.霍尔、J.M.卡特尔、E.B.铁钦纳等，他们将实验心理学传播到世界各地。"},
            {"title": "反应时与内省", "text": "冯特实验室以反应时测量与经过训练的内省报告为核心方法，分析简单心理过程，为第四章「反应时」专章讨论奠定历史基础。"},
        ],
        "resultsDetail": "实验法成为心理学核心范式；莱比锡实验室成为国际实验心理学研究中心。",
    },
    "ebbinghaus-forgetting": {
        "background": "教材第一章「三、艾宾浩斯」：在冯特认为实验心理学只能研究基本心理元素时，艾宾浩斯率先用实验研究学习、记忆与遗忘等高级心理过程。",
        "participants": "艾宾浩斯以自身为主试与被试，长期重复实验。",
        "variables": {"iv": "学习后时间间隔", "dv": "节省量（再学习节省的遍数或时间）", "control": "无意义音节、学习标准、朗读节奏"},
        "steps": [
            {"title": "无意义音节材料", "text": "教材介绍：艾宾浩斯创造性地采用无意义音节（两辅音夹一元音，如 Gij、Dax、Nov）作为实验材料，共约 2300 个，以避免词义联想对记忆的干扰，使实验情境更可控。"},
            {"title": "节省法", "text": "与背诵法不同，节省法要求被试先学到标准，间隔一段时间后再次学习同一材料，以两次学习所需遍数或时间之差（节省量）作为保持量的指标，使高级心理过程也能精确测量。"},
            {"title": "遗忘曲线数据", "text": "教材给出典型结果：学习后 20 分钟约保持 58%，1 小时约 44%，1 天约 30%；随后遗忘趋缓，约 1 个月后仍保持约 20%。由此建立第一条高级心理过程的功能关系——遗忘曲线。"},
        ],
        "resultsDetail": "遗忘先快后慢；记忆与遗忘可被定量研究，拓展了实验心理学的研究范围。",
    },
    "weber-law": {
        "background": "教材第五章第二节「一、韦伯定律」强调：韦伯通过实验发现，对于中等强度刺激，差别阈限 ΔI 与标准刺激 I 之比近似恒定。",
        "participants": "成年被试，视觉、听觉、触觉等多通道验证。",
        "variables": {"iv": "标准刺激强度 I", "dv": "差别阈限 ΔI", "control": "呈现方式、适应状态、反应标准"},
        "steps": [
            {"title": "两点阈限与重量辨别", "text": "教材以两点阈限（圆规）与重量辨别实验为例：被试判断两重量是否相同，主试逐步缩小两重量之差。"},
            {"title": "计算韦伯分数", "text": "对多个标准重量分别测定 ΔI，绘制 ΔI/I 曲线；在中等强度区段 K 值趋于稳定，即韦伯定律成立。"},
        ],
        "resultsDetail": "ΔI/I=K 揭示感觉系统对强度变化采用相对而非绝对标准，为费希纳对数定律提供经验基础。",
    },
    "donders-subtraction": {
        "background": "教材第四章第三节介绍唐德斯减数法：若某一心理过程可随任务要求出现或消失，则该过程耗时 ≈ 含该过程任务反应时 − 不含该过程任务反应时。",
        "participants": "经过练习的人类被试，保证反应时稳定。",
        "variables": {"iv": "反应任务类型（A/B/C）", "dv": "反应时（ms）", "control": "刺激强度、呈现位置、手指、练习量"},
        "steps": [
            {"title": "三类反应任务", "text": "A 反应：单一刺激单一反应；B 反应：多刺激择一反应（含选择）；C 反应：辨别刺激后反应（含辨别+选择）。分别测量平均反应时。"},
            {"title": "减数法计算", "text": "选择时间 ≈ RT_B − RT_A；辨别时间 ≈ RT_C − RT_B。通过反应时相减，推断不可直接观察的内部加工阶段耗时。"},
        ],
        "resultsDetail": "首次用实验逻辑分离心理过程阶段；减数法成为认知心理学测量加工时间的经典思路（尽管其后受到纯阶段假说等批评）。",
    },
}


def strip_step_images(steps):
    for step in steps or []:
        step.pop("image", None)
        step.pop("fallback", None)
        step.pop("bookPage", None)
        step.pop("pdfPage", None)


def attach_figures(item):
    try:
        from book_figures import figures_for_experiment
        figs = figures_for_experiment(item["id"])
        if figs:
            item["figures"] = figs
        else:
            item.pop("figures", None)
    except Exception:
        pass
    item.pop("bookPages", None)
    item.pop("pdfPages", None)


def main():
    data = json.loads(OUT.read_text(encoding="utf-8"))
    existing = {item["id"] for item in data}
    for item in NEW_EXPERIMENTS:
        if item["id"] not in existing:
            data.append(item)
            existing.add(item["id"])

    for item in data:
        merged = {**DETAILS.get(item["id"], {}), **EXTRA_DETAILS.get(item["id"], {})}
        item.update(merged)
        if "steps" not in item:
            item["steps"] = [
                {"title": "实验设计", "text": item.get("method", "")},
                {"title": "主要发现", "text": item.get("finding", "")},
            ]
        strip_step_images(item["steps"])
        attach_figures(item)
        if "resultsDetail" not in item:
            item["resultsDetail"] = item.get("finding", "")
        ch, sec = BOOK_SOURCE.get(item["id"], ("拓展章节", "经典研究"))
        item["sourceBook"] = SOURCE_BOOK
        item["sourceChapter"] = ch
        item["sourceSection"] = sec

    data.sort(key=lambda x: (x.get("year") or 0, x.get("title", "")))
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已扩充 {len(data)} 条实验详情（出处：{SOURCE_BOOK}）")


if __name__ == "__main__":
    main()
