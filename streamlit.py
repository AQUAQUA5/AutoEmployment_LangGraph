import streamlit as st
import asyncio
from src.core import graph
from src.core.state import state_init

def main():
    st.set_page_config(page_title="AI 취업 비서 챗봇", page_icon="🤖", layout="wide")
    st.title("🤖 AI 취업 비서 챗봇")

    # --- 세션 상태 초기화 ---
    if 'agent' not in st.session_state:
        st.session_state.agent = graph.Graph()
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'agent_state' not in st.session_state:
        st.session_state.agent_state = state_init()

    # --- 사이드바 메뉴 구성 ---
    with st.sidebar:
        st.header("메뉴")
        
        # 1. 결과 보기 섹션
        with st.expander("결과 보기", expanded=True):
            st.subheader("추천 채용 공고")
            job_list = st.session_state.agent_state.get('job_list', [])
            if job_list:
                for idx, job in enumerate(job_list):
                    # job_list의 각 항목이 튜플 또는 리스트 형태라고 가정 (회사명, 직무, 링크 등)
                    company_name = job[0] if len(job) > 0 else "정보 없음"
                    job_title = job[1] if len(job) > 1 else "정보 없음"
                    st.markdown(f"- **{company_name}**: {job_title}")
            else:
                st.info("아직 추천된 채용 공고가 없습니다.")

            st.divider()

            st.subheader("생성된 자기소개서")
            jasosu_main = st.session_state.agent_state.get('jasosu_main', '')
            if jasosu_main:
                st.text_area("자기소개서 내용", value=jasosu_main, height=300, disabled=True)
            else:
                st.info("아직 생성된 자기소개서가 없습니다.")

        st.divider()
        
        # 2. 에이전트 워크플로우 시각화
        with st.expander("에이전트 워크플로우 보기"):
            try:
                png_data = st.session_state.agent.app.get_graph().draw_png()
                st.image(png_data, caption="에이전트 실행 흐름")
            except Exception as e:
                st.error(f"그래프를 불러오는 데 실패했습니다: {e}")

    # --- 메인 채팅 화면 구성 ---
    # 대화 기록 표시
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력 처리
    if prompt := st.chat_input("메시지를 입력하세요..."):
        # 사용자 메시지 표시
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # LangGraph 에이전트 실행
        with st.spinner("AI가 생각 중입니다..."):
            try:
                st.session_state.agent_state['tmp_input'] = prompt
                
                # 비동기 함수 실행
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                updated_state = loop.run_until_complete(st.session_state.agent.run(st.session_state.agent_state))
                loop.close()

                # 세션 상태 업데이트
                st.session_state.agent_state = updated_state
                
                # AI 응답에서 content만 추출하여 깔끔하게 표시
                response_object = updated_state.get('con_current', ["", "응답 없음"])[1]
                if hasattr(response_object, 'content'):
                    bot_response = response_object.content
                else:
                    bot_response = str(response_object)

            except Exception as e:
                st.error(f"에이전트 실행 중 오류가 발생했습니다: {e}")
                bot_response = "죄송합니다, 처리 중 문제가 발생했습니다."

        # 챗봇 응답 표시
        with st.chat_message("assistant"):
            st.markdown(bot_response)
        st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
        
        # 사이드바를 다시 그리도록 페이지 리로드 (선택사항, 더 나은 UX를 위함)
        st.rerun()

if __name__ == "__main__":
    main()
