#!/usr/bin/env python3
"""从 心理学家们.xlsx 提取数据并生成 lineage.html / lineage_v2_1.html"""

import json
import re
import shutil
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent
XLSX = BASE / "心理学家们.xlsx"
MAIN_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"

SCHOOL_KEYS = frozenset({"struct", "func", "behav", "gestalt", "psycho", "human", "cog"})

COL_META = [
    {"key": k, "zh": zh, "en": en, "full": full, "isSchool": is_school}
    for k, zh, en, full, is_school in [
        ("struct", "构造主义", "STRUCTURALISM", "构造主义心理学", True),
        ("func", "机能主义", "FUNCTIONALISM", "机能主义心理学", True),
        ("behav", "行为主义", "BEHAVIORISM", "行为主义心理学", True),
        ("gestalt", "格式塔", "GESTALT", "格式塔心理学", True),
        ("psycho", "精神分析", "PSYCHOANALYSIS", "精神分析心理学", True),
        ("human", "人本主义", "HUMANISTIC", "人本主义心理学", True),
        ("cog", "认知心理学", "COGNITIVE", "认知心理学", True),
        ("psychophysics", "心理物理学", "PSYCHOPHYSICS", "心理物理学", False),
        ("physio", "生理心理学", "PHYSIOLOGICAL", "生理心理学", False),
        ("experimental", "实验心理学", "EXPERIMENTAL", "实验心理学", False),
        ("edu", "科学教育学", "EDUCATION", "科学教育学", False),
        ("measure", "心理测量", "PSYCHOMETRICS", "心理测量", False),
        ("stats", "心理统计", "PSYCH STATS", "心理统计", False),
        ("dev", "毕生发展", "DEVELOPMENTAL", "毕生发展", False),
        ("learn", "学习心理", "LEARNING", "学习心理", False),
        ("social", "社会心理", "SOCIAL", "社会心理", False),
        ("mgmt", "管理心理", "ORGANIZATIONAL", "管理心理", False),
        ("positive", "积极心理学", "POSITIVE", "积极心理学", False),
        ("neuro", "神经心理学", "NEUROPSYCHOLOGY", "神经心理学", False),
        ("ethology", "动物行为学", "ETHOLOGY", "动物行为学", False),
    ]
]

COL_BY_KEY = {item["key"]: item for item in COL_META}

# (列 key, 研究方向标签)；七大学派成员 tag 为 None
PERSON_CLASSIFICATION = {
    "冯特": ("struct", None),
    "铁钦纳": ("struct", None),
    "詹姆斯": ("func", None),
    "杜威": ("func", None),
    "安吉尔": ("func", None),
    "霍尔": ("func", None),
    "伍德沃斯": ("func", None),
    "巴普洛夫": ("behav", None),
    "桑代克": ("behav", None),
    "华生": ("behav", None),
    "斯金纳": ("behav", None),
    "托尔曼": ("behav", None),
    "班杜拉": ("behav", None),
    "韦特海默": ("gestalt", None),
    "苛勒": ("gestalt", None),
    "考夫卡": ("gestalt", None),
    "阿希": ("gestalt", None),
    "佛洛伊德": ("psycho", None),
    "阿德勒": ("psycho", None),
    "荣格": ("psycho", None),
    "埃里克森": ("psycho", None),
    "安娜佛洛伊德": ("psycho", None),
    "马斯洛": ("human", None),
    "罗杰斯": ("human", None),
    "奈塞尔": ("cog", None),
    "皮亚杰": ("cog", None),
    "西蒙": ("cog", None),
    "布罗德本特": ("cog", None),
    "巴德利": ("cog", None),
    "加德纳": ("cog", None),
    "斯腾伯格": ("cog", None),
    "斯腾伯格48": ("cog", None),
    "卡尼曼": ("cog", None),
    "赫尔巴特": ("edu", "科学教育学"),
    "韦伯": ("psychophysics", "心理物理学"),
    "费希纳": ("psychophysics", "心理物理学"),
    "亥姆霍兹": ("physio", "生理心理学"),
    "艾宾浩斯": ("experimental", "实验心理学"),
    "缪勒": ("experimental", "实验心理学"),
    "高尔顿": ("measure", "心理测量"),
    "比内": ("measure", "心理测量"),
    "推孟": ("measure", "心理测量"),
    "斯皮尔曼": ("measure", "心理测量"),
    "韦克斯勒": ("measure", "心理测量"),
    "奥尔波特": ("measure", "心理测量"),
    "卡特尔": ("measure", "心理测量"),
    "艾森克": ("measure", "心理测量"),
    "皮尔逊": ("stats", "心理统计"),
    "戈塞特": ("stats", "心理统计"),
    "费舍": ("stats", "心理统计"),
    "小皮尔逊": ("stats", "心理统计"),
    "内曼": ("stats", "心理统计"),
    "海特": ("social", "社会心理"),
    "巴雷特": ("neuro", "神经心理学"),
    "洛夫特斯": ("cog", None),
    "戴维森": ("neuro", "神经心理学"),
    "达克沃斯": ("positive", "积极心理学"),
    "吉尔伯特": ("cog", None),
    "平克": ("cog", None),
    "彭凯平": ("positive", "积极心理学"),
    "普莱尔": ("dev", "毕生发展"),
    "维果茨基": ("dev", "毕生发展"),
    "科尔伯格": ("dev", "毕生发展"),
    "艾斯沃斯": ("dev", "毕生发展"),
    "乔姆斯基": ("dev", "毕生发展"),
    "加涅": ("learn", "学习心理"),
    "布鲁纳": ("learn", "学习心理"),
    "奥苏伯尔": ("learn", "学习心理"),
    "麦克里兰": ("learn", "学习心理"),
    "韦纳": ("learn", "学习心理"),
    "费斯汀格": ("social", "社会心理"),
    "米尔格拉姆": ("social", "社会心理"),
    "津巴多": ("social", "社会心理"),
    "勒温": ("social", "社会心理"),
    "泰勒": ("mgmt", "管理心理"),
    "韦伯76": ("mgmt", "管理心理"),
    "法约尔": ("mgmt", "管理心理"),
    "利维特": ("mgmt", "管理心理"),
    "麦克雷戈": ("mgmt", "管理心理"),
    "梅奥（梅约）": ("mgmt", "管理心理"),
    "赫茨伯格": ("mgmt", "管理心理"),
    "亚当斯": ("mgmt", "管理心理"),
    "闵斯特伯格": ("mgmt", "管理心理"),
    "麦基恩卡特尔": ("measure", "心理测量"),
    "波林": ("struct", None),
    "格赛尔": ("dev", "毕生发展"),
    "拉什利": ("neuro", "神经心理学"),
    "克伯屈": ("edu", "科学教育学"),
    "胡适": ("edu", "科学教育学"),
    "陶行知": ("edu", "科学教育学"),
    "塞利格曼": ("positive", "积极心理学"),
    "兰格": ("positive", "积极心理学"),
    "芭芭拉": ("positive", "积极心理学"),
    "鲁利亚": ("neuro", "神经心理学"),
    "斯佩里": ("neuro", "神经心理学"),
    "劳伦兹": ("ethology", "动物行为学"),
    "廷伯根": ("ethology", "动物行为学"),
    "赫布": ("physio", "生理心理学"),
    "布罗卡": ("physio", "生理心理学"),
    "裴斯泰洛齐": ("edu", "科学教育学"),
}

# 网络补充：稀疏研究方向列的重要人物（无 Excel 头像）
SUPPLEMENT_PEOPLE = [
    {
        "id": "廷伯根",
        "cn": "廷伯根",
        "en": "尼科拉斯·廷伯根",
        "country": "荷兰/英国",
        "born": 1907,
        "died": 1988,
        "school": "动物行为学家 / 生态学家",
        "position": "现代习性学奠基人之一，1973年与劳伦兹、弗里isch共获诺贝尔生理学或医学奖",
        "bio": "与劳伦兹、弗里isch共同创立现代动物行为学（习性学），提出「四问」研究框架：机制、生存价值、个体发育与系统发育。",
        "theories": [
            {"t": "习性学四问", "d": "从因果机制、生存功能、个体发生与种系发生四个层面分析动物行为。"},
            {"t": "固定行为模式", "d": "与劳伦兹共同强调物种特异、受刺激释放的先天行为模式。"},
        ],
    },
    {
        "id": "赫布",
        "cn": "赫布",
        "en": "唐纳德·赫布",
        "country": "加拿大",
        "born": 1904,
        "died": 1985,
        "school": "生理心理学家 / 神经心理学家",
        "position": "《行为的组织》作者，提出赫布定律与细胞集合理论",
        "bio": "将神经生理机制与心理行为联系起来，为认知神经科学奠定概念基础。",
        "theories": [
            {"t": "赫布定律", "d": "当突触前神经元反复、持续兴奋突触后神经元时，该突触连接会增强（cells that fire together, wire together）。"},
            {"t": "细胞集合理论", "d": "知觉、思维等心理活动由同时激活的神经元集合（cell assembly）实现。"},
        ],
    },
    {
        "id": "布罗卡",
        "cn": "布罗卡",
        "en": "保罗·布罗卡",
        "country": "法国",
        "born": 1824,
        "died": 1880,
        "school": "外科医生 / 人类学家",
        "position": "发现语言运动中枢（布罗卡区），脑功能定位研究先驱",
        "bio": "通过失语症病人 Tan 的尸检，证明左额下回损伤导致运动性失语，开启脑与行为关系的实证研究。",
        "theories": [
            {"t": "布罗卡区", "d": "左半球额下回后部与言语产生密切相关，是脑功能定位说的经典证据。"},
        ],
    },
    {
        "id": "裴斯泰洛齐",
        "cn": "裴斯泰洛齐",
        "en": "约翰·亨利希·裴斯泰洛齐",
        "country": "瑞士",
        "born": 1746,
        "died": 1827,
        "school": "教育家 / 教育改革家",
        "position": "近代教育心理学先驱，《林哈德与葛笃德》作者",
        "bio": "强调教育应遵循儿童心理发展规律，主张「教育心理学化」，影响赫尔巴特及后世教育科学。",
        "theories": [
            {"t": "教育心理学化", "d": "教育过程应适应儿童自然发展，从感觉经验出发组织教学。"},
            {"t": "要素教育", "d": "通过数目、形状、名称等基本要素循序渐进地发展儿童能力。"},
        ],
    },
    {
        "id": "皮尔逊",
        "cn": "皮尔逊",
        "en": "卡尔·皮尔逊",
        "country": "英国",
        "born": 1857,
        "died": 1936,
        "school": "数学家 / 统计学家 / 生物计量学家",
        "position": "现代统计学的奠基人之一，创立《生物计量学》与伦敦大学学院生物计量学实验室",
        "bio": "将概率论与数据分析引入心理学与遗传研究，为高尔顿的优生学提供统计工具，深刻影响心理测量与实验数据分析。",
        "theories": [
            {"t": "皮尔逊积差相关系数 r", "d": "衡量两列连续变量线性相关程度，成为心理与教育研究中应用最广的相关指标之一。"},
            {"t": "卡方检验与拟合优度", "d": "用于分类数据与理论分布的比较，为心理实验中的频数分析奠定方法基础。"},
            {"t": "生物计量学（Biometrics）", "d": "与高尔顿合作，推动个体差异、遗传与能力测量的量化研究。"},
        ],
    },
    {
        "id": "戈塞特",
        "cn": "戈塞特",
        "en": "威廉·戈塞特",
        "country": "英国",
        "born": 1876,
        "died": 1937,
        "school": "化学家 / 统计学家",
        "position": "以笔名「Student」发表 t 检验， Guinness 啤酒厂首席酿酒师",
        "bio": "在小样本条件下发展 t 检验，解决心理与工业实验里样本量有限时的均值比较问题。",
        "theories": [
            {"t": "Student t 检验", "d": "比较两组小样本均值差异，是心理学实验报告中最常用的显著性检验之一。"},
            {"t": "小样本推断", "d": "证明在总体方差未知且样本较小时，仍可对均值差异作可靠推断。"},
        ],
    },
    {
        "id": "费舍",
        "cn": "费舍",
        "en": "罗纳德·费舍",
        "country": "英国",
        "born": 1890,
        "died": 1962,
        "school": "统计学家 / 遗传学家 / 实验设计家",
        "position": "方差分析（ANOVA）与随机化实验设计之父，《实验设计》作者",
        "bio": "系统化了心理学与农学实验中的统计推断，使多组比较、因子设计与显著性检验成为标准流程。",
        "theories": [
            {"t": "方差分析（ANOVA）", "d": "同时比较多组均值差异，适用于单因素、多因素及重复测量等心理实验设计。"},
            {"t": "随机化与区组设计", "d": "强调随机分配与控制混淆变量，提升实验内部效度。"},
            {"t": "最大似然估计", "d": "为参数估计与模型拟合提供一般框架，影响后续心理统计与结构方程模型。"},
        ],
    },
    {
        "id": "小皮尔逊",
        "cn": "小皮尔逊",
        "en": "埃贡·皮尔逊",
        "country": "英国",
        "born": 1895,
        "died": 1980,
        "school": "统计学家",
        "position": "卡尔·皮尔逊之子，与内曼共同建立假设检验理论",
        "bio": "继承并发展生物计量学传统，推动心理与教育研究中的统计推断规范化。",
        "theories": [
            {"t": "奈曼-皮尔逊检验理论", "d": "以第一类、第二类错误与检验力为核心，规范了心理学中的假设检验逻辑。"},
            {"t": "功效分析思想", "d": "强调在显著性之外考察检验力与效应量，影响现代心理统计报告规范。"},
        ],
    },
    {
        "id": "内曼",
        "cn": "内曼",
        "en": "耶利米·内曼",
        "country": "波兰/英国/美国",
        "born": 1894,
        "died": 1981,
        "school": "数学家 / 统计学家",
        "position": "现代数理统计与置信区间理论的重要奠基人",
        "bio": "与小皮尔逊合作建立假设检验理论，后在美国推动统计推断在社会科学中的应用。",
        "theories": [
            {"t": "奈曼-皮尔逊引理", "d": "给出在控制第一类错误率下最具检验力的检验构造原则。"},
            {"t": "置信区间推断", "d": "强调用区间估计补充显著性检验，为心理学效应量报告提供统计语言。"},
        ],
    },
    {
        "id": "安娜佛洛伊德",
        "cn": "安娜·佛洛伊德",
        "en": "安娜·弗洛伊德",
        "country": "奥地利/英国",
        "born": 1895,
        "died": 1982,
        "school": "精神分析学家 / 儿童心理学家",
        "position": "西格蒙德·弗洛伊德小女儿，儿童精神分析创始人",
        "bio": "在父亲精神分析体系内发展出独立的儿童分析传统，系统阐述自我防御机制，影响发展心理学与临床干预。",
        "theories": [
            {"t": "儿童精神分析", "d": "将精神分析应用于儿童，强调依恋关系、游戏治疗与发育阶段中的冲突，开创儿童分析学派。"},
            {"t": "自我心理学与防御机制", "d": "在《自我与防御机制》中系统分类压抑、投射、升华等防御方式，强调自我在焦虑调节中的核心功能。"},
            {"t": "战争孤儿与寄宿照护研究", "d": "二战期间对失去父母儿童的观察，揭示稳定依恋与照护环境对儿童心理结构的决定性作用。"},
        ],
    },
    {
        "id": "海特",
        "cn": "海特",
        "en": "乔纳森·海特",
        "country": "美国",
        "born": 1963,
        "school": "社会心理学家 / 道德心理学家",
        "position": "《正义之心》《象与骑象人》《焦虑的一代》作者，道德基础理论提出者",
        "bio": "2000 年后最具影响力的社会心理学者之一，将进化、文化与政治心理结合，近年关注青少年社交媒体与心理健康。",
        "theories": [
            {"t": "道德基础理论", "d": "认为人类道德判断由关怀、公平、忠诚、权威、圣洁等多重直觉基础构成，解释文化间与政治立场间的道德分歧。"},
            {"t": "象与骑象人模型", "d": "将自动化情绪直觉比作「象」，理性推理比作「骑象人」，强调改变行为需同时诉诸情感与理性。"},
        ],
    },
    {
        "id": "巴雷特",
        "cn": "巴雷特",
        "en": "莉莎·费尔德曼·巴雷特",
        "country": "美国",
        "born": 1963,
        "school": "神经科学家 / 心理学家",
        "position": "《情绪是如何产生的》作者，情绪建构理论代表人物",
        "bio": "21 世纪情绪科学最有影响力的研究者之一，用神经科学与预测加工框架挑战「基本情绪」传统观点。",
        "theories": [
            {"t": "情绪建构理论", "d": "情绪并非先天固定模块的触发，而是大脑对体内感觉与情境意义进行预测、归类后建构的体验。"},
            {"t": "情感科学整合框架", "d": "将神经可塑性、语言、文化与社会情境纳入同一研究框架，推动情感神经科学跨学科发展。"},
        ],
    },
    {
        "id": "洛夫特斯",
        "cn": "洛夫特斯",
        "en": "伊丽莎白·洛夫特斯",
        "country": "美国",
        "born": 1944,
        "school": "认知心理学家",
        "position": "虚假记忆与目击者证词研究权威，美国国家科学院院士",
        "bio": "其关于记忆可塑性的工作在 2000 年后深刻影响司法实践、媒体伦理与认知心理学教学。",
        "theories": [
            {"t": "记忆误导效应", "d": "事后信息可改变人们对事件细节的回忆，甚至植入从未发生的「伪记忆」。"},
            {"t": "目击者证词可靠性", "d": "证词并非录像式回放，而会在提问方式、压力与暗示中重构，需审慎用于法庭。"},
        ],
    },
    {
        "id": "戴维森",
        "cn": "戴维森",
        "en": "理查德·戴维森",
        "country": "美国",
        "born": 1951,
        "school": "神经科学家 / 情感神经科学创始人",
        "position": "威斯康星大学情感神经科学实验室创始人，《情绪大脑》作者",
        "bio": "2000 年后将冥想、正念与神经影像结合，推动情感神经科学与心理健康干预的实证研究。",
        "theories": [
            {"t": "情感风格（Affective Style）", "d": "个体在情绪反应性、恢复速度与调节策略上存在可测量的神经差异，且部分可通过训练改变。"},
            {"t": "正念神经机制", "d": "长期冥想练习与前额叶-杏仁核回路功能变化相关，为心理干预提供生物学依据。"},
        ],
    },
    {
        "id": "达克沃斯",
        "cn": "达克沃斯",
        "en": "安杰拉·达克沃斯",
        "country": "美国",
        "born": 1970,
        "school": "心理学家 / 教育研究者",
        "position": "「坚毅」（Grit）概念提出者，2013 年 TED 演讲现象级传播者",
        "bio": "2000 年后将人格特质与成就动机研究带入公众视野，在积极心理学与教育政策讨论中影响广泛。",
        "theories": [
            {"t": "坚毅（Grit）", "d": "对长期目标的激情与坚持，是预测学业与职业成就的重要非认知特质，可部分通过刻意练习培养。"},
            {"t": "自我控制与延迟满足", "d": "与沃尔特·米歇尔等研究传统衔接，强调情境与习惯在自控中的作用。"},
        ],
    },
    {
        "id": "吉尔伯特",
        "cn": "吉尔伯特",
        "en": "丹尼尔·吉尔伯特",
        "country": "美国",
        "born": 1957,
        "school": "社会心理学家 / 认知心理学家",
        "position": "《撞上幸福》作者，哈佛心理学教授",
        "bio": "2006 年起以通俗写作与实验研究结合，系统探讨人类如何预测未来情绪及系统性偏差。",
        "theories": [
            {"t": "情感预测偏差", "d": "人们高估未来事件对情绪的强度与持续时间（影响偏差），并低估心理免疫系统的恢复力。"},
            {"t": "合成幸福", "d": "当选择不可逆时，大脑会「合成」对现状的满意感，挑战「更多选择即更幸福」的直觉。"},
        ],
    },
    {
        "id": "平克",
        "cn": "平克",
        "en": "史蒂芬·平克",
        "country": "美国/加拿大",
        "born": 1954,
        "school": "认知心理学家 / 语言学家 / 科学作家",
        "position": "《语言本能》《白板》《人性中的善良天使》作者",
        "bio": "2000 年后以认知科学视角参与语言、暴力趋势与启蒙价值等公共议题，影响心理学与哲学交界讨论。",
        "theories": [
            {"t": "语言本能", "d": "人类语言能力是进化形成的认知本能，儿童具备普遍语法式的习得机制。"},
            {"t": "暴力下降的长时段证据", "d": "综合历史数据认为人类暴力在近代显著下降，强调理性、贸易与制度对行为的塑造。"},
        ],
    },
    {
        "id": "彭凯平",
        "cn": "彭凯平",
        "en": "彭凯平",
        "country": "中国",
        "born": 1964,
        "school": "社会心理学家 / 积极心理学家",
        "position": "清华大学心理学系创始系主任，《吾心可鉴》作者，中国积极心理学推广者",
        "bio": "2008 年回国后系统推动积极心理学在中国落地，在跨文化情绪、幸福科学与本土心理建设方面影响显著。",
        "theories": [
            {"t": "文化差异的情绪表达", "d": "东方与西方被试在情绪识别、表达规则与社交脚本上存在系统性差异，需文化嵌入的研究设计。"},
            {"t": "积极心理学科建设", "d": "将 PERMA、幸福感测量与本土文化价值结合，推动中国高校积极心理学课程与公众科普。"},
        ],
    },
    {
        "id": "麦基恩卡特尔",
        "cn": "麦基恩·卡特尔",
        "en": "詹姆斯·麦基恩·卡特尔",
        "country": "美国",
        "born": 1860,
        "died": 1944,
        "school": "心理学家 / 冯特门生",
        "position": "美国心理学会创始人之一，心理测验与个体差异研究先驱",
        "bio": "1883–1886 年在莱比锡任冯特助理并完成博士论文，后推动美国心理测验运动与《心理学评论》等期刊。",
        "theories": [
            {"t": "心理测验运动", "d": "系统测量个体差异与反应时，推动心理学从实验室走向应用测量。"},
            {"t": "冯特实验室传统", "d": "将莱比锡实验方法引入美国，与铁钦纳、霍尔等同为冯特第一代美国门生。"},
        ],
    },
    {
        "id": "波林",
        "cn": "波林",
        "en": "埃德温·波林",
        "country": "美国",
        "born": 1886,
        "died": 1968,
        "school": "心理学家 / 铁钦纳门生",
        "position": "《实验心理学史》作者，哈佛心理系主任",
        "bio": "在康奈尔大学随铁钦纳接受构造主义训练，后主持哈佛心理系并撰写心理学史经典。",
        "theories": [
            {"t": "实验心理学史", "d": "以构造主义视角梳理从冯特到当代的实验心理学发展。"},
        ],
    },
    {
        "id": "格赛尔",
        "cn": "格赛尔",
        "en": "阿诺德·格赛尔",
        "country": "美国",
        "born": 1880,
        "died": 1961,
        "school": "发展心理学家 / 霍尔门生",
        "position": "耶鲁儿童发展诊所创始人，双生子研究先驱",
        "bio": "在克拉克大学随霍尔学习，以双生子爬梯等研究奠定儿童发展心理学基础。",
        "theories": [
            {"t": "成熟势力说", "d": "强调遗传成熟在儿童动作与行为发展中的主导作用。"},
            {"t": "双生子爬梯实验", "d": "比较同卵与异卵双生子，说明成熟而非练习决定发展时间表。"},
        ],
    },
    {
        "id": "拉什利",
        "cn": "拉什利",
        "en": "卡尔·拉什利",
        "country": "美国",
        "born": 1890,
        "died": 1958,
        "school": "神经心理学家 / 华生门生",
        "position": "脑功能定位与整体活动原则研究先驱",
        "bio": "在约翰·霍普金斯大学随华生从事动物学习研究，后转向大脑皮层与学习记忆关系。",
        "theories": [
            {"t": "整体活动原则", "d": "大脑皮层以整体方式参与学习，切除范围比定位更重要。"},
            {"t": "脑功能定位研究", "d": "通过大鼠迷宫实验探索皮层区域与学习的对应关系。"},
        ],
    },
    {
        "id": "克伯屈",
        "cn": "克伯屈",
        "en": "威廉·克伯屈",
        "country": "美国",
        "born": 1871,
        "died": 1965,
        "school": "教育家 / 杜威门生",
        "position": "设计教学法（项目教学法）主要推广者",
        "bio": "哥伦比亚大学师范学院杜威学派核心成员，将进步主义教育理论系统化并广泛传播。",
        "theories": [
            {"t": "设计教学法", "d": "以有目的的项目活动组织学习，强调儿童主动建构知识。"},
        ],
    },
    {
        "id": "胡适",
        "cn": "胡适",
        "en": "胡适",
        "country": "中国",
        "born": 1891,
        "died": 1962,
        "school": "哲学家 / 教育家 / 杜威学生",
        "position": "实用主义与实验主义思想在中国的重要传播者",
        "bio": "1915–1917 年留学哥伦比亚大学，深受杜威实用主义影响，提倡「大胆假设，小心求证」。",
        "theories": [
            {"t": "实验主义方法论", "d": "将杜威实用主义转化为中国的启蒙与学术方法。"},
            {"t": "白话文运动", "d": "以文学革命推动现代中国思想与教育变革。"},
        ],
    },
    {
        "id": "陶行知",
        "cn": "陶行知",
        "en": "陶行知",
        "country": "中国",
        "born": 1891,
        "died": 1946,
        "school": "教育家 / 杜威门生",
        "position": "生活教育理论创立者，晓庄师范与育才学校创办人",
        "bio": "1915–1917 年在哥伦比亚大学师范学院师从杜威，回国后发展「生活即教育、社会即学校」。",
        "theories": [
            {"t": "生活教育", "d": "「生活即教育、社会即学校、教学做合一」，将杜威思想中国化。"},
            {"t": "小先生制", "d": "倡导儿童互助教与学，扩大教育覆盖面。"},
        ],
    },
]

MANUAL_RELATIONS = [
    ("韦伯", "赫尔巴特", "inspire", "用实验证明赫尔巴特提出的阈限概念"),
    ("费希纳", "韦伯", "inspire", "韦伯定律启发费希纳建立心理物理学"),
    ("冯特", "亥姆霍兹", "mentor", "冯特曾是亥姆霍兹的助手"),
    ("艾宾浩斯", "费希纳", "inspire", "受费希纳《心理物理学纲要》影响"),
    ("艾宾浩斯", "冯特", "rupture", "第一个对记忆开展实验研究，反对冯特限制"),
    ("缪勒", "艾宾浩斯", "inspire", "继承并改进艾宾浩斯的记忆研究方法"),
    ("缪勒", "冯特", "rupture", "反对冯特「实验只能研究基本心理历程」"),
    ("铁钦纳", "冯特", "mentor", "师从冯特，将构造主义传入美国"),
    ("霍尔", "冯特", "mentor", "1878年获冯特授予的首位美国心理学哲学博士学位"),
    ("斯皮尔曼", "冯特", "mentor", "在莱比锡大学随冯特学习实验心理学"),
    ("艾宾浩斯", "冯特", "mentor", "曾赴莱比锡随冯特学习，后独立开展记忆研究"),
    ("麦基恩卡特尔", "冯特", "mentor", "在莱比锡任冯特助理并完成博士论文"),
    ("詹姆斯", "亥姆霍兹", "inspire", "赴德留学期间受亥姆霍兹生理心理学影响"),
    ("詹姆斯", "冯特", "inspire", "同受亥姆霍兹影响，机能主义与实验心理学并起"),
    ("霍尔", "詹姆斯", "mentor", "返美后于哈佛随詹姆斯继续心理学研究"),
    ("波林", "铁钦纳", "mentor", "在康奈尔大学随铁钦纳接受构造主义训练"),
    ("斯金纳", "波林", "inspire", "哈佛心理系学术环境中延续行为主义传统"),
    ("桑代克", "詹姆斯", "inspire", "哈佛求学期间受詹姆斯机能主义影响"),
    ("伍德沃斯", "詹姆斯", "inspire", "机能主义心理学传统下的代表学者"),
    ("马斯洛", "桑代克", "mentor", "在哥伦比亚大学师从桑代克完成博士训练"),
    ("杜威", "霍尔", "mentor", "在霍普金斯大学随霍尔攻读哲学博士"),
    ("推孟", "霍尔", "mentor", "在克拉克大学随霍尔学习"),
    ("格赛尔", "霍尔", "mentor", "在克拉克大学随霍尔学习发展心理学"),
    ("华生", "杜威", "inspire", "在芝加哥大学受杜威进步主义教育思想影响"),
    ("拉什利", "华生", "mentor", "在约翰·霍普金斯大学随华生从事动物行为研究"),
    ("克伯屈", "杜威", "mentor", "哥伦比亚大学师范学院随杜威学习设计教学法"),
    ("胡适", "杜威", "inspire", "留学哥伦比亚大学期间受杜威实用主义极大影响"),
    ("陶行知", "杜威", "mentor", "在哥伦比亚大学师范学院师从杜威，回国创办生活教育"),
    ("华生", "普莱尔", "rupture", "普莱尔反对白板说，与华生环境决定论相对"),
    ("托尔曼", "桑代克", "rupture", "整体目的行为观 vs 盲目试误学习观"),
    ("斯金纳", "桑代克", "inspire", "效果律启发操作性条件反射"),
    ("斯金纳", "巴普洛夫", "inspire", "经典/操作两类条件作用对照"),
    ("华生", "巴普洛夫", "inspire", "经典条件反射为 S-R 研究提供基础"),
    ("托尔曼", "华生", "rupture", "提出中介变量，反对机械 S-R"),
    ("班杜拉", "托尔曼", "inspire", "认知中介为社会学习理论铺路"),
    ("班杜拉", "华生", "rupture", "观察学习突破纯粹 S-R 框架"),
    ("安吉尔", "詹姆斯", "mentor", "继承詹姆斯机能主义"),
    ("阿德勒", "佛洛伊德", "rupture", "与弗洛伊德决裂，创立个体心理学"),
    ("荣格", "佛洛伊德", "rupture", "分道扬镳，发展分析心理学"),
    ("埃里克森", "佛洛伊德", "inspire", "在弗洛伊德基础上发展心理社会发展理论"),
    ("埃里克森", "安娜佛洛伊德", "mentor", "师从安娜·佛洛伊德，属新精神分析学派"),
    ("安娜佛洛伊德", "佛洛伊德", "mentor", "弗洛伊德之女，继承并发展精神分析与儿童分析"),
    ("苛勒", "韦特海默", "mentor", "格式塔心理学核心成员"),
    ("考夫卡", "韦特海默", "mentor", "与韦特海默共同创立格式塔心理学"),
    ("罗杰斯", "马斯洛", "inspire", "共同代表人本主义第三势力"),
    ("推孟", "比内", "inspire", "修订比内-西蒙量表为斯坦福-比内量表"),
    ("韦克斯勒", "比内", "inspire", "在比内测验基础上发展韦氏量表"),
    ("皮亚杰", "比内", "inspire", "儿童智力研究继承比内传统"),
    ("加涅", "桑代克", "inspire", "学习分类继承并超越行为主义"),
    ("布鲁纳", "皮亚杰", "inspire", "认知结构学习观受皮亚杰影响"),
    ("维果茨基", "皮亚杰", "rupture", "社会文化理论 vs 个体建构观"),
    ("科尔伯格", "皮亚杰", "inspire", "道德发展阶段论受皮亚杰启发"),
    ("费斯汀格", "阿希", "inspire", "认知失调与从众实验同属社会认知"),
    ("米尔格拉姆", "阿希", "inspire", "服从实验延伸从众研究"),
    ("津巴多", "米尔格拉姆", "inspire", "斯坦福监狱实验与服从研究一脉相承"),
    ("梅奥（梅约）", "泰勒", "rupture", "霍桑实验挑战泰勒科学管理"),
    ("赫茨伯格", "梅奥（梅约）", "inspire", "双因素理论受霍桑实验影响"),
    ("勒温", "费斯汀格", "inspire", "场论影响社会心理学"),
    ("闵斯特伯格", "冯特", "mentor", "师从冯特，开创工业心理学"),
    ("塞利格曼", "斯金纳", "rupture", "从行为主义转向积极心理学"),
    ("廷伯根", "劳伦兹", "inspire", "与劳伦兹共同创立现代习性学"),
    ("赫布", "亥姆霍兹", "inspire", "继承神经生理与心理行为联结的传统"),
    ("赫尔巴特", "裴斯泰洛齐", "inspire", "裴斯泰洛齐教育心理学化思想影响赫尔巴特"),
    ("皮尔逊", "高尔顿", "inspire", "继承高尔顿生物计量学，发展相关与分布理论"),
    ("斯皮尔曼", "皮尔逊", "inspire", "在皮尔逊积差相关基础上发展等级相关"),
    ("戈塞特", "皮尔逊", "mentor", "在皮尔逊指导下完成小样本 t 检验"),
    ("费舍", "皮尔逊", "inspire", "继承相关分析传统并发展 ANOVA 与实验设计"),
    ("费舍", "戈塞特", "inspire", "t 检验思想影响其推断统计体系"),
    ("小皮尔逊", "皮尔逊", "mentor", "师从父亲，共同主持生物计量学工作"),
    ("内曼", "小皮尔逊", "inspire", "合作建立奈曼-皮尔逊假设检验理论"),
    ("达克沃斯", "塞利格曼", "mentor", "在宾大师从塞利格曼，发展坚毅研究"),
    ("彭凯平", "塞利格曼", "inspire", "留美期间受积极心理学运动影响"),
    ("吉尔伯特", "卡尼曼", "inspire", "情感预测研究延续行为决策传统"),
    ("巴雷特", "卡尼曼", "inspire", "情绪建构吸收认知与决策科学视角"),
    ("海特", "费斯汀格", "inspire", "社会认知与认知失调传统下的道德心理研究"),
    ("洛夫特斯", "奈塞尔", "inspire", "在认知心理学框架下研究记忆重构"),
    ("戴维森", "斯佩里", "inspire", "从脑半球研究走向情感神经科学"),
    ("平克", "乔姆斯基", "inspire", "语言本能论继承普遍语法传统"),
]


def parse_years(text):
    if not text:
        return None, None
    match = re.search(r"(\d{3,4})\s*[-–—]\s*(\d{3,4}|)", text)
    if match:
        born = int(match.group(1))
        died = int(match.group(2)) if match.group(2) else None
        return born, died
    match = re.search(r"(\d{4})", text)
    return (int(match.group(1)), None) if match else (None, None)


def parse_theories(values):
    theories = []
    for col in ("F", "G", "I", "J", "K"):
        text = values.get(col, "").strip()
        if not text or text.startswith("=DISPIMG"):
            continue
        for part in re.split(r"\n(?=\d+[\.．、])", text):
            part = re.sub(r"^\d+[\.．、]\s*", "", part.strip())
            if not part:
                continue
            lines = part.split("\n", 1)
            theories.append({"t": lines[0].strip(), "d": lines[1].strip() if len(lines) > 1 else ""})
    return theories


def extract():
    avatars_dir = BASE / "avatars"
    data_dir = BASE / "data"
    avatars_dir.mkdir(exist_ok=True)
    data_dir.mkdir(exist_ok=True)

    with zipfile.ZipFile(XLSX) as zf:
        shared = []
        for si in ET.fromstring(zf.read("xl/sharedStrings.xml")).findall(f".//{MAIN_NS}si"):
            parts = [t.text or "" for t in si.findall(f".//{MAIN_NS}t")]
            shared.append("".join(parts))

        rels = {rel.attrib["Id"]: rel.attrib["Target"] for rel in ET.fromstring(zf.read("xl/_rels/cellimages.xml.rels"))}
        id_to_media = {}
        for pic in ET.fromstring(zf.read("xl/cellimages.xml")).iter():
            if not pic.tag.endswith("pic"):
                continue
            name = embed = None
            for child in pic.iter():
                if child.tag.endswith("cNvPr"):
                    name = child.attrib.get("name")
                if child.tag.endswith("blip"):
                    embed = child.attrib.get(f"{REL_NS}embed")
            if name and embed:
                target = rels.get(embed, "")
                id_to_media[name] = "xl/" + target.replace("../", "")

        rows = {}
        for cell in ET.fromstring(zf.read("xl/worksheets/sheet1.xml")).findall(f".//{MAIN_NS}c"):
            ref = cell.attrib.get("r")
            col, row = re.match(r"([A-Z]+)(\d+)", ref).groups()
            row = int(row)
            t = cell.attrib.get("t")
            value_node = cell.find(f"{MAIN_NS}v")
            value = ""
            if value_node is not None and value_node.text is not None:
                value = shared[int(value_node.text)] if t == "s" else value_node.text
            rows.setdefault(row, {})[col] = value

        avatar_files = {}
        for row, values in rows.items():
            match = re.search(r'DISPIMG\("([^"]+)"', values.get("A", ""))
            if not match:
                continue
            media = id_to_media.get(match.group(1))
            if not media or media not in zf.namelist():
                continue
            filename = f"row_{row}{Path(media).suffix or '.jpeg'}"
            (avatars_dir / filename).write_bytes(zf.read(media))
            avatar_files[row] = f"avatars/{filename}"

    people = []
    perspective = None
    seen_ids = {}
    for row in sorted(rows):
        values = rows[row]
        a = values.get("A", "").strip()
        b = values.get("B", "").strip()
        if a and not b and not a.startswith("=DISPIMG"):
            perspective = a
            continue
        if not b:
            continue

        lines = b.split("\n")
        cn = lines[0].strip()
        en = re.sub(r"^[（(]|[）)]$", "", lines[1].strip("（）() ")) if len(lines) > 1 else ""
        country_lines = values.get("C", "").split("\n") if values.get("C") else []
        born, died = parse_years(country_lines[1].strip() if len(country_lines) > 1 else "")

        pid = re.sub(r"\s+", "", cn)
        if pid in seen_ids:
            pid = f"{pid}{row}"
        seen_ids[pid] = True

        ftext = values.get("F", "")
        experiment = None
        if ftext and not ftext.startswith("=DISPIMG"):
            experiment = {"title": ftext.split("\n")[0][:100], "body": ftext}

        people.append(
            {
                "id": pid,
                "row": row,
                "cn": cn,
                "en": en,
                "col": "other",
                "perspective": perspective,
                "country": country_lines[0].strip() if country_lines else "",
                "born": born,
                "died": died,
                "school": values.get("D", "").replace("\n", " / "),
                "position": values.get("E", "").replace("\n", " ")[:200],
                "bio": values.get("E", ""),
                "theories": parse_theories(values)[:10],
                "experiment": experiment,
                "avatar": avatar_files.get(row),
            }
        )

    apply_classification(people)
    merge_supplements(people)

    name_to_id = {}
    for person in people:
        cn = person["cn"]
        if cn not in name_to_id or not re.search(r"\d$", person["id"]):
            name_to_id[cn] = person["id"]
    relations = []
    seen = set()
    for fr, to, rel_type, label in MANUAL_RELATIONS:
        fid, tid = name_to_id.get(fr), name_to_id.get(to)
        if not fid or not tid or fid == tid:
            continue
        key = (fid, tid, rel_type)
        if key in seen:
            continue
        seen.add(key)
        relations.append({"from": fid, "to": tid, "type": rel_type, "label": label, "source": "table"})

    (data_dir / "people.json").write_text(json.dumps(people, ensure_ascii=False, indent=2), encoding="utf-8")
    (data_dir / "relations.json").write_text(json.dumps(relations, ensure_ascii=False, indent=2), encoding="utf-8")
    (data_dir / "columns.json").write_text(json.dumps(COL_META, ensure_ascii=False, indent=2), encoding="utf-8")
    return people, relations


def apply_classification(people):
    for person in people:
        col, tag = PERSON_CLASSIFICATION.get(person["id"], ("experimental", "实验心理学"))
        person["col"] = col
        meta = COL_BY_KEY.get(col, {})
        if meta.get("isSchool"):
            person["isSchool"] = True
        elif tag:
            person["tag"] = tag
        elif meta:
            person["tag"] = meta["zh"]
        if person["id"] == "比内" and person.get("born") == 1957:
            person["born"] = 1857


def merge_supplements(people):
    existing = {p["id"] for p in people}
    for item in SUPPLEMENT_PEOPLE:
        if item["id"] in existing:
            continue
        person = dict(item)
        person["col"] = "other"
        people.append(person)
    apply_classification(people)


def render_html(people, relations):
    compact = []
    for person in people:
        item = {k: person[k] for k in ("id", "cn", "en", "col", "country", "born", "died", "school", "position", "bio", "avatar") if person.get(k) is not None}
        if person.get("isSchool"):
            item["isSchool"] = True
        if person.get("tag"):
            item["tag"] = person["tag"]
        if person.get("theories"):
            item["theories"] = person["theories"]
        if person.get("experiment"):
            item["experiment"] = person["experiment"]
        compact.append(item)

    era_markers = [
        {"year": 1780, "label": "哲学思辨与教育学奠基期"},
        {"year": 1860, "label": "心理物理学方法论独立期"},
        {"year": 1879, "label": "莱比锡建校 · 实验心理学诞生"},
        {"year": 1900, "label": "机能主义崛起 · 客观主义萌芽"},
        {"year": 1913, "label": "行为主义革命 · 心理学第一势力"},
        {"year": 1950, "label": "认知革命与人本主义第三势力"},
        {"year": 1980, "label": "认知神经科学与社会心理学繁荣期"},
        {"year": 2000, "label": "积极心理学运动兴起"},
    ]

    template_path = BASE / "lineage_v2_1.html"
    if not template_path.exists():
        raise SystemExit("缺少 lineage_v2_1.html 模板，请先保留一份 HTML 模板。")

    html = template_path.read_text(encoding="utf-8")

    def inject_const(name, payload):
        nonlocal html
        serialized = json.dumps(payload, ensure_ascii=False)
        pattern = rf"const {name} = \[.*?\];"
        html = re.sub(
            pattern,
            lambda _match, n=name, s=serialized: f"const {n} = {s};",
            html,
            count=1,
            flags=re.S,
        )

    inject_const("COLS", COL_META)
    inject_const("PEOPLE", compact)
    inject_const("RELATIONS", relations)
    inject_const("ERA_MARKERS", era_markers)
    return html


def main():
    people, relations = extract()
    html = render_html(people, relations)
    (BASE / "lineage.html").write_text(html, encoding="utf-8")
    shutil.copy(BASE / "lineage.html", BASE / "lineage_v2_1.html")
    print(f"完成：{len(people)} 位学者，{len(relations)} 条关系，头像 {len(list((BASE/'avatars').glob('*')))} 张")


if __name__ == "__main__":
    main()
