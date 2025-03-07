from autogen import UserProxyAgent, AssistantAgent, register_function, GroupChatManager, GroupChat
from .tools import tavily_search
import os

os.environ["TAVILY_API_KEY"] = "api"

user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: "최종 보고서 작성이 완료되었습니다." in x.get("content", ""),
    function_map={"tavily_search": tavily_search},
    code_execution_config={
        "use_docker": False,
    }

)

# 리서처 정의 (호출자 역할)
researcher = AssistantAgent(
    name="researcher",
    llm_config={
        "config_list": [{
            "model": "qwen2.5:3b",
            "api_type": "ollama",
            "base_url": "http://localhost:11434"
        }]
    },
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
    caller=researcher,
    executor=user_proxy,
    name="tavily_search",
    description="웹에서 정보를 검색하고 요약된 결과를 반환합니다."
)

# 밸리데이터, 에디터 정의
validator = AssistantAgent(
    name="validator",
    llm_config={
        "config_list": [{
            "model": "EcomGen:0.0.1v",
            "api_type": "ollama",
            "base_url": "http://localhost:11434"
        }]
    },
    system_message=(
        "이전에 researcher가 정리한 내용을 기반으로 논리적으로 적절한지 판단하여 내용을 정리합니다."
        "이전 내용에 있는 정보가 잘못되었을 경우 수정합니다."
        "제목, 본문, 결론, 출처 링크까지 마크다운 형식으로 정리합니다."
        "정리한 이후에 최종 보고서 작성이 완료되었습니다. 라고 작성하여 마무리해주세요."
    )
)

# editor = AssistantAgent(
#     name="editor",
#     llm_config={
#         "config_list": [{
#             "model": "EcomGen:0.0.1v",
#             "api_type": "ollama",
#             "base_url": "http://localhost:11434"
#         }]
#     },
#     system_message=(
#         "이전에 validator가 검토한 내용을 기반으로 보고서를 정리합니다."
#         "이전 내용에 없는 내용은 추가하지 않습니다."
#         "제목, 본문, 결론, 출처 링크까지 마크 다운 형식으로 정리합니다."
#         "보고서 정리가 끝났으면 최종 보고서 작성이 완료되었습니다. 라고 작성을 마무리 꼭 해주세요."
#     )
# )

# GroupChatManager 설정 (내부 스피커 선택을 위한 LLM 지정 필수)
manager = GroupChatManager(
    groupchat=GroupChat(
        agents=[user_proxy, researcher, validator],
        messages=[],
    ),
    llm_config={
        "config_list": [{
            "model": "qwen2.5:3b",
            "api_type": "ollama",
            "base_url": "http://localhost:11434"
        }]
    },
    is_termination_msg=lambda msg: "최종 보고서 작성이 완료되었습니다." in msg.get("content", ""),
)

chat = user_proxy.initiate_chat(
    manager,
    message="겨울철 건강관리에 대해서 정리해줘"
)

print(chat)
