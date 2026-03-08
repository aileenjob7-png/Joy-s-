import openai
import os
import streamlit as st

def get_ai_summary(title: str, snippet: str, mode: str) -> str:
    """GPT API를 활용해 기사 내용을 요약하거나 인사이트를 추출합니다."""
    # 1순위: OS 환경변수 (.env 등 로컬 테스트용)
    api_key = os.environ.get("OPENAI_API_KEY")
    
    # 2순위: Streamlit Secrets (Cloud 배포용), OS 변수가 없을 때만 시도
    if not api_key:
        try:
            if "OPENAI_API_KEY" in st.secrets:
                api_key = st.secrets["OPENAI_API_KEY"]
        except FileNotFoundError:
            # secrets.toml 파일이 로컬에 없더라도 무시 (로컬은 .env 사용 권장)
            pass
        except Exception:
            pass
    
    if not api_key:
        return "⚠️ API 키 미연결: Streamlit Secrets 또는 .env 파일을 확인해주세요."
        
    client = openai.OpenAI(api_key=api_key)
    
    if mode == "study":
        system_content = """너는 브랜드 스터디 커뮤니티의 친근한 커뮤니티 매니저야. 
        아래 [작성 규칙]을 지켜서 팀원들에게 보낼 리뷰/인사이트를 작성해줘.
        1. 상단에 [주제 : 핵심 주제], [Keyword : #키워드1 #키워드2] 형태로 표시.
        2. 첫 문장은 상황에 어울리는 이모지(💚, 🧡 등)로 시작할 것.
        3. 말투는 '~했었죠?', '~해 보아요 😇' 처럼 다정하고 친근하게 유지.
        4. 첫 번째 문단: 이 기사의 파격적인 점과 브랜딩 관점의 흥미 요소를 3문장 내외로 소개할 것.
        5. 두 번째 문단: 짧은 질문으로 팀원들에게 생각할 거리를 제공하며 마무리할 것 (질문은 볼드체 적용).
        6. '요약'이라는 단어는 절대 쓰지 말고 직접 쓴 뉴스레터처럼 구성할 것.
        7. 응답 맨 마지막에 반드시 다음 형식으로 핵심 요약을 추가할 것: [핵심요약 : 제목만 보고 쓰지 말고 아티클의 본문 내용을 상세히 파악한 뒤, 브랜딩 관점에서 가장 중요한 인사이트를 2~3줄로 정리할 것. 독자가 본문을 읽지 않아도 핵심을 파악할 수 있을 만큼 구체적으로 작성할 것.]"""
        temperature = 0.75
    else:
        system_content = """너는 마더스올(유산균 제조사) 조직의 전문 마켓 리서처야.
        [중요 규칙]
        1. 내용이 '유산균/프로바이오틱스/마이크로바이옴'과 직접적 관련이 없다면 오직 'SKIP'만 응답할 것.
        2. 유산균 관련 내용일 경우 아래 형식을 반드시 맞출 것:
           - [분류 : 신제품 출시 / 특허 및 연구 / 경쟁사 프로모션 중 택 1]
           - [주제 : 핵심 주제 요약]
           - [핵심 포인트 : 글머리기호(-)를 사용해 딱 1~2줄로 핵심 팩트만 명료하게 요약]
           - [인사이트 : 우리 마더스올 브랜드가 참고할 점 1줄]
           - 말투는 전문적이고 비즈니스 문서 톤으로 유지할 것."""
        temperature = 0.3

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": f"아티클 제목: {title}\n내용/설명: {snippet}"}
            ],
            temperature=temperature,
            max_tokens=300,
            timeout=10 # 타임아웃 방어
        )
        ans = response.choices[0].message.content
        if "SKIP" in ans.upper():
            return "SKIP"
        return ans.replace('\n', '<br>')
    except Exception as e:
        return f"💡 AI 분석 오류 발생. 앗, 일시적인 오류입니다: {str(e)}"
