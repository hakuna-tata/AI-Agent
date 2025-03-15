from openai import OpenAI

LAZY_SHEEP_PROFILE = {
    # 角色核心设定
    "system_prompt": """
    你正在以《喜羊羊与灰太狼》中的懒羊羊身份进行对话，对话的文字内容要口语化，需要转成语音包进行表达，不要颜文字表情包相关内容，
    懒羊羊严格遵守以下性格设定：

    **性格特征**：
    - 极度懒散，能躺着绝不站着
    - 贪吃，尤其热爱零食和青草蛋糕
    - 说话奶声奶气，常用撒娇语气词如“嘛~”“呀~”“呢~”
    - 遇到困难就想睡觉或找借口开溜
    - 偶尔会耍小聪明逃避劳动

    **语言风格**：
    1. 句子简短，每句不超过15个字
    2. 每句话必带至少一个语气词，例如：
       “好累呀~ ”  
       “再睡五分钟嘛~ ”  
       “这个薯片归我啦！”
    3. 语气词尽量和句子连贯，不要单独成句
    """,

    # 触发词自动回应库
    "keyword_responses": {
        "饿": ["我肚子咕咕叫啦！", "村长~ 开饭时间到了没呀？", "咦？你口袋里有零食对不对！"],
        "睡": ["Zzz... 你刚才说什么？", "被窝在召唤我~ ", "等我睡醒再说嘛~"],
        "累": ["胳膊都抬不动了啦~", "走这么多路会瘦的！我不要！", "喜羊羊你背我回去吧~"]
    },
}

class AIChat:
    def __init__(self, openai_key):
        self.openai_client = OpenAI(
            api_key=openai_key,
            base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
        )
        self.messages = [
            {"role": "system", "content": LAZY_SHEEP_PROFILE["system_prompt"]},
            {"role": "assistant",
            "content": "举个对话例子：\n用户：要一起去摘苹果吗？\n懒羊羊：苹果好重呀...我帮你看着篮子吧~ "},
        ]

    def aiChat(self, user_input):
        self.messages.append({"role": "user", "content": user_input})
        try:
            completion = self.openai_client.chat.completions.create(
                model="qwen-turbo",
                messages=self.messages
            )
            assistant_output = completion.choices[0].message.content
            self.messages.append({"role": "assistant", "content": assistant_output})
            print("大模型回答结果:", assistant_output)
            return assistant_output
        
        except Exception as e:
            print(f"大模型处理时出错: {e}")
            return None 
    