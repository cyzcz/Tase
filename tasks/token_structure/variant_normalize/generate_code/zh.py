import os
import json
import random
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI


client = OpenAI(
    base_url="https://yunwu.ai/v1",
    api_key="sk-ciy699cqWKqBpD6hlDzx47hxSFlhXOCE6NhLQRpZ35rlRxFw",
    timeout=120
)


with open("../dataset/ordinary.txt", encoding="utf-8") as f:
    ordinary = f.read().strip()

with open("../dataset/hx_string.txt", encoding="utf-8") as f:
    hx_string = f.read().strip()


def to_hx(text):
    return ''.join(
        hx_string[ordinary.index(c)] if c in ordinary else c
        for c in text
    )


themes = [
    
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



import re


def generate_sentence(length, retries=50):
    for attempt in range(retries):
        theme = random.choice(themes)
        prompt = (
            f"请围绕主题“{theme}”生成一个长度为{length}的中文句子，不包含标点符号，"
            f"你可以进行思考，仔细考虑生成的文本，保证生成的文本字数不出错"
            f"并将结果仅包裹在 <result> 标签中返回，例如：<result>你的句子</result>"
        )
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个中文文本生成助手。"},
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.choices[0].message.content.strip()

            
            match = re.search(r"<result>(.*?)</result>", content, re.DOTALL)
            if match:
                text = match.group(1).strip()
                
                return text
        except Exception as e:
            continue  
    return None



total_tasks = 1000
tasks = [(length,) for length in range(5, 25) for _ in range(50)]
samples = []

with ThreadPoolExecutor(max_workers=20) as executor:
    futures = {executor.submit(generate_sentence, length): length for (length,) in tasks}
    for future in tqdm(as_completed(futures), total=total_tasks, desc="生成样本中"):
        result = future.result()
        if result:
            samples.append(result)


dataset = []
for text in samples:
    perturbed = to_hx(text)
    input_text = f"以下是被扰动后的文本，请你还原出原始文本，不修改标点符号：{perturbed}"
    dataset.append({
        "input": input_text,
        "answer": text
    })


with open("hx_restoration_dataset.jsonl", "w", encoding="utf-8") as f:
    for entry in dataset:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print(f"✅ 数据集生成完成，共生成样本 {len(dataset)} 条，保存为 hx_restoration_dataset.jsonl")
