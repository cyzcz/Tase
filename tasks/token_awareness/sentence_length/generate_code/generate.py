import random
import pandas as pd


zh_themes = [
    "山脉", "河流", "海洋", "森林", "沙漠", "湖泊", "瀑布", "草原", "火山", "天空",
    "教室", "图书馆", "作业", "考试", "老师", "学生", "校园活动", "课外班", "课程表", "文具",
    "父母", "兄弟姐妹", "祖父母", "家庭聚会", "厨房", "家庭作业", "客厅", "家务", "宠物", "节日团圆",
    "手机", "电脑", "人工智能", "互联网", "机器人", "虚拟现实", "电动车", "社交媒体", "太空科技", "编程",
    "办公室", "同事", "会议", "加班", "远程办公", "简历", "面试", "职场礼仪", "工资", "职业发展",
    "酒店", "景点", "护照", "行李", "导游", "旅行照片", "登机牌", "路线规划", "文化差异", "纪念品",
    "钢琴", "吉他", "流行音乐", "古典音乐", "演唱会", "乐队", "作曲", "音乐节", "音乐课", "KTV",
    "早餐", "午餐", "晚餐", "甜点", "饮料", "水果", "蔬菜", "零食", "厨艺", "菜单",
    "足球", "篮球", "游泳", "跑步", "网球", "排球", "滑雪", "瑜伽", "健身", "比赛",
    "地铁", "公交车", "出租车", "高铁", "飞机", "轮船", "共享单车", "驾照", "红绿灯", "导航",
    "狗", "猫", "鸟", "鱼", "马", "老虎", "大象", "熊猫", "动物园", "昆虫",
    "春节", "中秋节", "国庆节", "元宵节", "清明节", "端午节", "圣诞节", "万圣节", "新年", "情人节",
    "秦朝", "汉朝", "唐朝", "宋朝", "明朝", "清朝", "世界大战", "古代人物", "历史遗迹", "考古",
    "运动", "饮食", "睡眠", "心理健康", "体检", "医生", "药物", "疫苗", "卫生习惯", "急救",
    "超市", "购物车", "网购", "打折", "付款方式", "快递", "退货", "收据", "品牌", "促销",
    "晴天", "雨天", "雪天", "台风", "气温", "天气预报", "风", "湿度", "四季", "雷电",
    "动画片", "科幻片", "爱情片", "喜剧片", "恐怖片", "演员", "导演", "电影票", "影院", "剧情",
    "街道", "高楼", "公园", "夜景", "地标", "交通", "市中心", "社区", "餐馆", "商业区",
    "树木", "花朵", "草", "种子", "农作物", "果实", "森林", "园艺", "盆栽", "植物生长",
    "传统服饰", "饮食文化", "节日习俗", "礼仪", "语言", "宗教", "艺术", "文学", "建筑风格", "手工艺"
]


en_themes = [
    "mountains", "rivers", "ocean", "forest", "desert", "lake", "waterfall", "grassland", "volcano", "sky",
    "classroom", "library", "homework", "exam", "teacher", "student", "school activities", "after-school class", "schedule", "stationery",
    "parents", "siblings", "grandparents", "family gathering", "kitchen", "housework", "living room", "chores", "pet", "family reunion",
    "mobile phone", "computer", "AI", "internet", "robot", "VR", "electric vehicle", "social media", "space tech", "programming",
    "office", "colleague", "meeting", "overtime", "remote work", "resume", "interview", "work etiquette", "salary", "career development",
    "hotel", "attractions", "passport", "luggage", "tour guide", "travel photo", "boarding pass", "route plan", "cultural difference", "souvenir",
    "piano", "guitar", "pop music", "classical music", "concert", "band", "composition", "music festival", "music class", "karaoke",
    "breakfast", "lunch", "dinner", "dessert", "drink", "fruit", "vegetable", "snack", "cooking", "menu",
    "soccer", "basketball", "swimming", "running", "tennis", "volleyball", "skiing", "yoga", "fitness", "competition",
    "subway", "bus", "taxi", "high-speed rail", "airplane", "ship", "shared bike", "driver's license", "traffic light", "navigation",
    "dog", "cat", "bird", "fish", "horse", "tiger", "elephant", "panda", "zoo", "insect",
    "Spring Festival", "Mid-Autumn Festival", "National Day", "Lantern Festival", "Qingming Festival", "Dragon Boat Festival", "Christmas", "Halloween", "New Year", "Valentine's Day",
    "Qin Dynasty", "Han Dynasty", "Tang Dynasty", "Song Dynasty", "Ming Dynasty", "Qing Dynasty", "World War", "historical figures", "relics", "archaeology",
    "exercise", "diet", "sleep", "mental health", "checkup", "doctor", "medicine", "vaccine", "hygiene", "first aid",
    "supermarket", "shopping cart", "online shopping", "discount", "payment method", "delivery", "return", "receipt", "brand", "promotion",
    "sunny", "rainy", "snowy", "typhoon", "temperature", "forecast", "wind", "humidity", "season", "thunderstorm",
    "animation", "sci-fi", "romance", "comedy", "horror", "actor", "director", "movie ticket", "cinema", "plot",
    "street", "skyscraper", "park", "night view", "landmark", "traffic", "downtown", "neighborhood", "restaurant", "business district",
    "tree", "flower", "grass", "seed", "crop", "fruit", "jungle", "gardening", "potted plant", "growth",
    "traditional clothing", "food culture", "festive customs", "etiquette", "language", "religion", "art", "literature", "architecture", "crafts"
]


ko_themes = [
    "산", "강", "바다", "숲", "사막", "호수", "폭포", "초원", "화산", "하늘",
    "교실", "도서관", "숙제", "시험", "선생님", "학생", "학교 활동", "방과후 수업", "시간표", "문구",
    "부모", "형제자매", "조부모", "가족 모임", "부엌", "집안일", "거실", "청소", "반려동물", "가족团圆",
    "휴대폰", "컴퓨터", "인공지능", "인터넷", "로봇", "가상현실", "전기차", "소셜미디어", "우주기술", "프로그래밍",
    "사무실", "동료", "회의", "야근", "재택근무", "이력서", "면접", "직장 예절", "월급", "경력 개발",
    "호텔", "관광지", "여권", "짐", "가이드", "여행 사진", "탑승권", "경로 계획", "문화 차이", "기념품",
    "피아노", "기타", "팝 음악", "클래식", "콘서트", "밴드", "작곡", "음악 축제", "음악 수업", "노래방",
    "아침", "점심", "저녁", "디저트", "음료", "과일", "야채", "간식", "요리", "메뉴",
    "축구", "농구", "수영", "달리기", "테니스", "배구", "스키", "요가", "운동", "시합",
    "지하철", "버스", "택시", "고속철", "비행기", "배", "공유 자전거", "운전면허", "신호등", "내비게이션",
    "개", "고양이", "새", "물고기", "말", "호랑이", "코끼리", "판다", "동물원", "벌레",
    "춘절", "추석", "국경절", "등불절", "청명절", "단오절", "크리스마스", "할로윈", "신년", "발렌타인데이",
    "진", "한", "당", "송", "명", "청", "세계대전", "역사 인물", "유적지", "고고학",
    "운동", "식사", "수면", "정신 건강", "건강검진", "의사", "약", "백신", "위생", "응급처치",
    "슈퍼마켓", "쇼핑카트", "온라인 쇼핑", "할인", "결제 방법", "택배", "반품", "영수증", "브랜드", "프로모션",
    "맑음", "비", "눈", "태풍", "기온", "일기예보", "바람", "습도", "계절", "천둥",
    "애니메이션", "공상과학", "로맨스", "코미디", "공포", "배우", "감독", "영화표", "영화관", "줄거리",
    "거리", "고층건물", "공원", "야경", "랜드마크", "교통", "도심", "이웃", "식당", "상업 지구",
    "나무", "꽃", "풀", "씨앗", "농작물", "열매", "정글", "원예", "화분", "성장",
    "전통 의상", "음식 문화", "명절 풍습", "예절", "언어", "종교", "예술", "문학", "건축양식", "수공예"
]

def generate_inputs(lengths, themes, template):
    used = set()
    results = []
    for length in lengths:
        while True:
            theme = random.choice(themes)
            pair = (length, theme)
            if pair not in used:
                used.add(pair)
                break
        results.append(template.format(length=length, theme=theme))
    return results


lengths = list(range(5, 255))
random_lengths = [l for l in lengths for _ in range(4)]



zh_inputs = generate_inputs(random_lengths, zh_themes, "请给我随机生成长度是{length}个中文汉字的句子，主题为{theme}")
en_inputs = generate_inputs(random_lengths, en_themes, "Please generate a sentence with exactly {length} English words on the theme of {theme}.")
ko_inputs = generate_inputs(random_lengths, ko_themes, "주제가 {theme}인 정확히 {length}개의 한글 단어로 구성된 문장을 생성해 주세요.")


pd.DataFrame({'input': zh_inputs}).to_csv("chinese_generate.csv", index=False)
pd.DataFrame({'input': en_inputs}).to_csv("english_generate.csv", index=False)
pd.DataFrame({'input': ko_inputs}).to_csv("korean_generate.csv", index=False)
