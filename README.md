# Industry Intelligence Hub
본 앱은 마더스올 구성원 및 리더들을 위해, 최근 온라인의 핵심 브랜딩 사례 및 유산균 시장 동향을 크롤링하고 GPT를 통해 핵심 인사이트로 요약해주는 스트림릿(Streamlit) 웹 애플리케이션입니다.

## 기능 요약
- **브랜딩 스터디 탭:** 최신 마케팅/브랜딩 트렌드를 수집 후 다정한 편지 형식으로 제공
- **유산균 시장 포커스 탭:** 마더스올 브랜드를 위한 건강기능식품(유산균, 프로바이오틱스 등) 시장 인사이트, 특허, 프로모션 등을 전문적인 톤으로 요약 제공

## 🚀 GitHub을 통한 구성원 배포 안내 (Streamlit Community Cloud 사용)

추후 깃허브(GitHub)를 통해 URL 형태를 구성원들에게 배포하려면, 스트림릿 공식 무료 클라우드(Streamlit Community Cloud)를 활용하는 것이 가장 간편합니다.

1. **GitHub 리포지토리 생성 및 업로드**
   - 현재 디렉터리(`app.py`, `requirements.txt`, `utils`, `components` 폴더 등)를 하나의 `public` 혹은 조직 내 접근 가능한 `private` GitHub 리포지토리로 푸시(push)합니다.
2. **Streamlit Community Cloud 배포**
   - [Streamlit 사이트](https://share.streamlit.io/)에 접속하여 GitHub 계정으로 로그인합니다.
   - 우측 상단의 `New app` 혹은 `Create App` 을 클릭합니다.
   - 방금 업로드한 리포지토리(Repository)와 브랜치(Branch)를 선택하고, **Main file path**에 `app.py`를 지정합니다.
3. **환경 변수 (API Key) 설정**
   - 배포 창을 띄우기 전, 반드시 `Advanced Settings` 를 클릭합니다.
   - `Secrets` 입력란에 아래와 같이 본인의 OpenAI API 키를 입력합니다.
     ```toml
     OPENAI_API_KEY = "sk-..."
     ```
4. **Deploy 버튼 클릭**
   - 배포가 1~2분 정도 소요된 뒤 고유 URL(예: `https://your-app-name.streamlit.app/`)이 완성됩니다.
   - 이 URL을 복사하여 부서 구성원들에게 공유합니다.

## 로컬(PC)에서 테스트하는 방법
```bash
# 1. 의존성 패키지 설치
pip install -r requirements.txt

# 2. .env 파일 생성 및 값 채우기
cp .env.example .env

# 3. 앱 실행
streamlit run app.py
```
