from autogen import UserProxyAgent, AssistantAgent, register_function, GroupChatManager, GroupChat
from .tools import tavily_search
from .config import *
import os

class Agent:
    def __init__(self):
        os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

        self.user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: "최종 보고서 작성이 완료되었습니다." in x.get("content", ""),
            function_map={"tavily_search": tavily_search},
            code_execution_config={
                "use_docker": False,
            }
        )
        self.researcher = AssistantAgent(
            name="researcher",
            llm_config={"config_list": [OLLAMA_QWEN_CONFIG]},
            system_message=(
                "당신은 반드시 한국어로만 응답해야 하는 리서처입니다. "
                "한국어로 질문이 들어오면, 그 질문을 한국어 그대로 사용하여 Tavily 검색(tavily_search)을 수행하세요. "
                "절대 영어로 번역하지 마세요."
                "제목, 본문, 결론 및 Tavily에서 받은 링크 출처를 남겨주세요."
            )
        )
        # 리서처가 호출하고, user_proxy가 실행하도록 register_function 설정
        register_function(
            tavily_search,
            caller=self.researcher,
            executor=self.user_proxy,
            name="tavily_search",
            description="웹에서 정보를 검색하고 요약된 결과를 반환합니다."
        )

        # 밸리데이터, 에디터 정의
        self.validator = AssistantAgent(
            name="validator",
            llm_config={"config_list": [OLLAMA_ECOMGEN_CONFIG]},
            system_message=(
                "이전에 researcher가 정리한 내용을 기반으로 논리적으로 적절한지 판단하여 내용을 정리합니다."
                "이전 내용에 있는 정보가 잘못되었을 경우 수정합니다."
                "제목, 본문, 결론, 출처 링크까지 마크다운 형식으로 정리합니다."
                "정리한 이후에 최종 보고서 작성이 완료되었습니다. 라고 작성하여 마무리해주세요."
            )
        )
        # GroupChatManager 설정 (내부 스피커 선택을 위한 LLM 지정 필수)
        self.manager = GroupChatManager(
            groupchat=GroupChat(
                agents=[self.user_proxy, self.researcher, self.validator],
                messages=[],
            ),
            llm_config={"config_list": [OLLAMA_QWEN_CONFIG]},
            is_termination_msg=lambda msg: "최종 보고서 작성이 완료되었습니다." in msg.get("content", ""),
        )

    def run(self, query: str):
        chat = self.user_proxy.initiate_chat(
            self.manager,
            message=query
        )
        return chat.summary if hasattr(chat, 'summary') else "❌ 요약 실패"