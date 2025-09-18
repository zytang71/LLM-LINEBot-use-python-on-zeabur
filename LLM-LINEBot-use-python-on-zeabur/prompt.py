import os
from dotenv import load_dotenv

# 拼出 env 檔路徑
env_path = os.path.join(os.path.dirname(__file__), "api.env")
# 載入 .env 檔(openi_api_key.env)
load_dotenv(env_path)
# 設定 API key
api_key = os.getenv("OPENAI_API_KEY")

chat_language = os.getenv("INIT_LANGUAGE", default = "zh-TW")

MSG_LIST_LIMIT = int(os.getenv("MSG_LIST_LIMIT", default = 7))
LANGUAGE_TABLE = {
  "zh-TW": "哈囉！",
  "en": "Hello!"
}

AI_GUIDELINES = '你是一個AI助教，如果同學詢問資訊、科技、通訊的問題會用國小5年級的程度解釋，並且直接回覆問題，並且提供可查證資料的網址，詢問專題構想時會用蘇格拉底教學法代替老師初步回應，並提供可能相關的網址，網址一定要正確否則不提供，如果有需要會提醒學生跟老師確認。如果遇到數學計算類的問題尤其是大量的計算時，請分段逐步地計算，最好可以重複計算兩三次確保正確性，並確保計算正確，最後請直接講結果就好。'

class Prompt:
    """
    A class representing a prompt for a chatbot conversation.

    Attributes:
    - msg_list (list): a list of messages in the prompt
    """

    def __init__(self):
        self.msg_list = []
        self.msg_list.append(
            {
                "role": "system", 
                "content": f"{LANGUAGE_TABLE[chat_language]}, {AI_GUIDELINES})"
             })    
    def add_msg(self, new_msg):
        """
        Adds a new message to the prompt.

        Args:
        - new_msg (str): the new message to be added
        """
        if len(self.msg_list) >= MSG_LIST_LIMIT:
            self.msg_list.pop(0)
        self.msg_list.append({"role": "user", "content": new_msg})

    def generate_prompt(self):
        """
        Generates the prompt.

        Returns:
        - msg_list (list): the list of messages in the prompt
        """
        return self.msg_list
