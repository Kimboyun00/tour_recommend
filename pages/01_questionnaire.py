import streamlit as st
import time
import sys
import os

# 현재 디렉토리를 Python 경로에 추가 (임포트 오류 해결)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from utils import (questions, calculate_factor_scores, determine_cluster, 
                      validate_answers, show_footer, reset_survey_state, 
                      check_access_permissions, apply_global_styles)
except ImportError as e:
    st.error(f"❌ 필수 모듈을 불러올 수 없습니다: {e}")
    st.info("💡 **해결 방법**: `utils.py` 파일이 올바른 위치에 있는지 확인해주세요.")
    st.code("""
    프로젝트 구조:
    ├── app.py
    ├── utils.py  ← 이 파일이 필요합니다
    └── pages/
        ├── 01_questionnaire.py
        ├── 02_analyzing.py
        └── ...
    """)
    st.stop()

# 페이지 설정
st.set_page_config(
    page_title="웰니스 관광 성향 설문",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 접근 권한 확인
try:
    check_access_permissions('questionnaire')
except Exception as e:
    st.error(f"❌ 접근 권한 확인 중 오류: {e}")
    if st.button("🏠 홈으로 돌아가기"):
        st.switch_page("app.py")
    st.stop()

# 로그인 확인
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ 로그인 후 이용해주세요.")
    if st.button("🏠 로그인 페이지로 돌아가기", key="login_redirect"):
        st.switch_page("app.py")
    st.stop()

# 설문 재설정 플래그 확인
if st.session_state.get('reset_survey_flag', False):
    reset_survey_state()
    st.session_state.reset_survey_flag = False

# 전역 스타일 적용
apply_global_styles()

# 설문 전용 추가 스타일
st.markdown("""
<style>
    /* 사이드바 스타일링 */
    .css-1d391kg {
        background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 100%);
    }
    
    /* 질문 카드 스타일 */
    .question-card {
        background: var(--card-bg);
        backdrop-filter: blur(15px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: var(--border-radius);
        padding: 30px;
        margin: 25px 0;
        transition: all 0.3s ease;
        box-shadow: var(--shadow);
        position: relative;
        overflow: hidden;
    }
    
    .question-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(45deg, var(--primary), var(--secondary));
        border-radius: var(--border-radius) var(--border-radius) 0 0;
    }
    
    .question-card:hover {
        transform: translateY(-2px);
        border-color: var(--primary);
        box-shadow: var(--shadow-hover);
    }
    
    .question-card.error {
        border-color: #FF5722;
        background: linear-gradient(135deg, rgba(255, 87, 34, 0.1), var(--card-bg));
        animation: shake 0.6s ease-in-out;
    }
    
    .question-card.error::before {
        background: linear-gradient(45deg, #FF5722, #FF7043);
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-3px); }
        75% { transform: translateX(3px); }
    }
    
    /* 질문 제목 */
    .question-title {
        color: var(--primary-dark);
        font-size: 1.3em;
        font-weight: 700;
        margin-bottom: 20px;
        line-height: 1.5;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    .question-title.error {
        color: #FF5722;
    }
    
    /* 요인 태그 */
    .factor-tag {
        display: inline-block;
        background: linear-gradient(45deg, var(--primary), var(--primary-light));
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 700;
        margin-bottom: 18px;
        box-shadow: 0 3px 10px rgba(76, 175, 80, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* 라디오 버튼 스타일 개선 */
    div[data-testid="stRadio"] {
        margin: 20px 0;
    }
    
    div[data-testid="stRadio"] > div {
        gap: 15px !important;
    }
    
    div[data-testid="stRadio"] label {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 2px solid rgba(76, 175, 80, 0.3) !important;
        border-radius: 15px !important;
        padding: 18px 22px !important;
        margin: 0 !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(10px) !important;
        cursor: pointer !important;
        min-height: 65px !important;
        display: flex !important;
        align-items: center !important;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.08) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    div[data-testid="stRadio"] label::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(76, 175, 80, 0.1), transparent);
        transition: all 0.6s ease;
    }
    
    div[data-testid="stRadio"] label:hover::before {
        left: 100%;
    }
    
    div[data-testid="stRadio"] label:hover {
        transform: translateY(-3px) !important;
        border-color: var(--primary) !important;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.25) !important;
        background: rgba(255, 255, 255, 1) !important;
    }
    
    div[data-testid="stRadio"] input:checked + div {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.15), rgba(129, 199, 132, 0.1)) !important;
        border-color: var(--primary) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3) !important;
    }
    
    div[data-testid="stRadio"] label span {
        font-size: 1.05em !important;
        color: var(--primary-dark) !important;
        font-weight: 600 !important;
        line-height: 1.6 !important;
        z-index: 1 !important;
        position: relative !important;
    }
    
    /* 메인 제목 */
    .main-title {
        color: var(--primary-dark) !important;
        text-align: center;
        font-size: 2.8em !important;
        font-weight: 800 !important;
        margin-bottom: 30px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        background: var(--card-bg);
        padding: 30px;
        border-radius: var(--border-radius);
        border: 3px solid var(--primary);
        box-shadow: var(--shadow);
        position: relative;
        overflow: hidden;
    }
    
    .main-title::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(45deg, var(--primary), var(--secondary));
        border-radius: var(--border-radius) var(--border-radius) 0 0;
    }
    
    /* 인트로 카드 */
    .intro-card {
        background: var(--card-bg);
        backdrop-filter: blur(15px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: var(--border-radius);
        padding: 30px;
        margin: 25px 0;
        text-align: center;
        box-shadow: var(--shadow);
        position: relative;
        overflow: hidden;
    }
    
    .intro-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(45deg, var(--primary), var(--secondary));
        border-radius: var(--border-radius) var(--border-radius) 0 0;
    }
    
    /* 진행률 바 */
    div[data-testid="stProgress"] > div > div {
        background: linear-gradient(45deg, var(--primary), var(--primary-light)) !important;
        border-radius: 12px !important;
        height: 16px !important;
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3) !important;
    }
    
    div[data-testid="stProgress"] > div {
        background: rgba(76, 175, 80, 0.2) !important;
        border-radius: 12px !important;
        height: 16px !important;
        box-shadow: inset 0 2px 8px rgba(76, 175, 80, 0.1) !important;
    }
    
    /* 진행률 텍스트 */
    .progress-text {
        font-size: 1.4em;
        font-weight: 800;
        color: var(--primary-dark);
        text-align: center;
        margin: 20px 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    /* 프로그레스 컨테이너 */
    .progress-container {
        background: var(--card-bg);
        backdrop-filter: blur(15px);
        border: 2px solid rgba(76, 175, 80, 0.3);
        border-radius: var(--border-radius);
        padding: 30px;
        margin: 25px 0;
        box-shadow: var(--shadow);
        position: relative;
        overflow: hidden;
    }
    
    .progress-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(45deg, var(--primary), var(--secondary));
        border-radius: var(--border-radius) var(--border-radius) 0 0;
    }
    
    /* 완료 버튼 특별 스타일 */
    .complete-button {
        background: linear-gradient(45deg, #2E7D32, var(--primary)) !important;
        font-size: 1.2em !important;
        padding: 18px 30px !important;
        border-radius: 25px !important;
        box-shadow: 0 6px 20px rgba(46, 125, 50, 0.4) !important;
        text-transform: none !important;
        letter-spacing: 1px !important;
    }
    
    .complete-button:hover {
        background: linear-gradient(45deg, #1B5E20, #2E7D32) !important;
        transform: translateY(-5px) !important;
        box-shadow: 0 10px 30px rgba(46, 125, 50, 0.5) !important;
    }
    
    /* 사이드바 사용자 정보 */
    .sidebar-user-info {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border: 2px solid rgba(76, 175, 80, 0.3);
        text-align: center;
    }
    
    .sidebar-progress {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border: 2px solid rgba(76, 175, 80, 0.3);
    }
</style>
""", unsafe_allow_html=True)

def get_factor_description(factor_key):
    """요인별 설명 반환"""
    descriptions = {
        "요인1": "계획적 정보 추구형",
        "요인2": "쇼핑 중심형", 
        "요인3": "한국 여행 경험축",
        "요인4": "실용적 현지 탐색형",
        "요인5": "편의 인프라 중시형",
        "요인6": "전통문화 안전 추구형",
        "요인7": "패션 쇼핑형",
        "요인8": "프리미엄 사회적 여행형",
        "요인9": "성별 기반 쇼핑 선호형",
        "요인10": "디지털 미디어 개인형",
        "요인11": "절차 중시 자연 관광형",
        "요인12": "교통 편의 미식형"
    }
    return descriptions.get(factor_key, "미정의 요인")

def questionnaire_page():
    # 사이드바에 사용자 정보 및 진행 상황
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-user-info">
            <h3 style="color: #2E7D32; margin-bottom: 15px;">👤 사용자 정보</h3>
            <p style="color: #4CAF50; font-weight: 700; font-size: 1.1em; margin: 0;">
                🌿 {st.session_state.username}님
            </p>
            <p style="color: #666; font-size: 0.9em; margin: 5px 0 0 0;">
                12개 요인 분석 시스템
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 시스템 정보
        st.markdown("""
        <div class="sidebar-progress">
            <h4 style="color: #2E7D32; margin-bottom: 15px;">📊 분석 시스템</h4>
            <div style="margin: 10px 0;">
                <span style="color: #4CAF50; font-weight: 600;">🔬 과학적 근거:</span><br>
                <span style="color: #666; font-size: 0.85em;">2,591명 데이터 기반</span>
            </div>
            <div style="margin: 10px 0;">
                <span style="color: #4CAF50; font-weight: 600;">🎯 분석 정확도:</span><br>
                <span style="color: #666; font-size: 0.85em;">95% 이상</span>
            </div>
            <div style="margin: 10px 0;">
                <span style="color: #4CAF50; font-weight: 600;">⏱️ 소요 시간:</span><br>
                <span style="color: #666; font-size: 0.85em;">약 5분</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 로그아웃 버튼
        st.markdown("---")
        if st.button("🚪 로그아웃", use_container_width=True, key="sidebar_logout"):
            # 세션 상태 클리어
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("app.py")

    # 세션 상태 초기화
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    if 'survey_completed' not in st.session_state:
        st.session_state.survey_completed = False
    if 'validation_errors' not in st.session_state:
        st.session_state.validation_errors = set()

    def update_answers():
        """답변 업데이트 함수"""
        for q_key in questions.keys():
            radio_key = f"radio_{q_key}"
            if radio_key in st.session_state:
                st.session_state.answers[q_key] = st.session_state[radio_key]

    # 메인 제목
    st.markdown('<h1 class="main-title">🌿 한국 관광 성향 진단 시스템 2.0</h1>', unsafe_allow_html=True)
    
    # 소개 메시지
    st.markdown("""
    <div class="intro-card">
        <h3 style="color: #2E7D32; margin-bottom: 20px; font-size: 1.6em;">🎯 12개 요인 기반 정밀 분석</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; text-align: left; margin: 20px 0;">
            <div>
                <h4 style="color: #4CAF50; margin-bottom: 10px; display: flex; align-items: center;">
                    <span style="font-size: 1.3em; margin-right: 8px;">🔬</span>과학적 분석
                </h4>
                <p style="color: #2E7D32; font-size: 0.95em; line-height: 1.6; margin: 0;">
                    실제 2,591명의 외국인 관광객 데이터를 요인분석하여 개발된 검증된 시스템
                </p>
            </div>
            <div>
                <h4 style="color: #4CAF50; margin-bottom: 10px; display: flex; align-items: center;">
                    <span style="font-size: 1.3em; margin-right: 8px;">🎭</span>정밀 분류
                </h4>
                <p style="color: #2E7D32; font-size: 0.95em; line-height: 1.6; margin: 0;">
                    12개 핵심 요인으로 8가지 독특한 여행 성향 유형을 정확히 분류
                </p>
            </div>
        </div>
        <div style="background: rgba(76, 175, 80, 0.1); padding: 15px; border-radius: 12px; margin-top: 20px;">
            <p style="color: #2E7D32; font-weight: 700; margin: 0; font-size: 1.05em;">
                💡 각 질문은 특정 요인을 측정하여 당신만의 여행 패턴을 과학적으로 분석합니다
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 진행률 표시를 위한 플레이스홀더
    progress_placeholder = st.empty()
    
    st.markdown("---")

    # 설문 문항 표시
    for i, (q_key, question) in enumerate(questions.items(), 1):
        is_error = q_key in st.session_state.validation_errors
        current_answer = st.session_state.answers.get(q_key)
        
        # 질문 카드 생성
        card_class = "question-card error" if is_error else "question-card"
        title_class = "question-title error" if is_error else "question-title"
        
        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
        
        # 요인 태그
        factor_desc = get_factor_description(question['factor'])
        st.markdown(f'<div class="factor-tag">{question["factor"]}: {factor_desc}</div>', unsafe_allow_html=True)
        
        # 질문 제목
        title_text = question['title']
        if is_error:
            title_text += " ⚠️ **필수 응답**"
        
        st.markdown(f'<div class="{title_class}">{title_text}</div>', unsafe_allow_html=True)
        
        # 라디오 버튼 옵션
        index_to_pass = current_answer if current_answer is not None else None
        
        # 각 질문마다 고유한 라벨 생성 (접근성 향상)
        radio_label = f"질문 {i}번 응답 선택"
        
        st.radio(
            radio_label,
            options=list(range(len(question['options']))),
            format_func=lambda x, opts=question['options']: f"{x+1}. {opts[x]}",
            key=f"radio_{q_key}",
            on_change=update_answers,
            index=index_to_pass,
            label_visibility="hidden"  # 라벨은 숨기지만 스크린 리더를 위해 제공
        )
        
        st.markdown('</div>', unsafe_allow_html=True)

    # 진행률 계산 및 표시
    answered_count = len([q for q in questions.keys() if st.session_state.answers.get(q) is not None])
    progress_value = answered_count / len(questions)
    
    with progress_placeholder:
        st.markdown('<div class="progress-container">', unsafe_allow_html=True)
        
        # 진행률 바
        st.progress(progress_value)
        
        # 진행률 텍스트
        if progress_value == 1:
            st.markdown(f"""
            <div class="progress-text">
                🎉 모든 문항 완료! ({answered_count}/{len(questions)})
                <br><small style="color: #4CAF50;">이제 분석을 시작할 수 있습니다!</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            remaining = len(questions) - answered_count
            st.markdown(f"""
            <div class="progress-text">
                📝 진행률: {answered_count}/{len(questions)} ({progress_value:.0%})
                <br><small style="color: #666;">남은 문항: {remaining}개</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # 완료 버튼
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        button_text = "🎯 12개 요인 분석 시작하기" if progress_value == 1 else f"📝 설문 완료하기 ({answered_count}/{len(questions)})"
        
        if st.button(button_text, type="primary", use_container_width=True, key="complete_survey"):
            if validate_answers():
                try:
                    # 분석 시작 메시지
                    with st.spinner("🧠 12개 요인 분석을 시작합니다..."):
                        time.sleep(0.5)  # 사용자 경험을 위한 짧은 지연
                        
                        # 요인 점수 계산
                        factor_scores = calculate_factor_scores(st.session_state.answers)
                        st.session_state.factor_scores = factor_scores
                        
                        # 클러스터 결정
                        cluster_result = determine_cluster(st.session_state.answers)
                        st.session_state.cluster_result = cluster_result
                        st.session_state.survey_completed = True
                        
                        # 성공 메시지
                        st.success("✅ 설문이 완료되었습니다! 분석을 시작합니다...")
                        st.balloons()
                        
                        # 잠시 후 분석 페이지로 이동
                        time.sleep(1.5)
                        st.switch_page("pages/02_analyzing.py")
                        
                except Exception as e:
                    st.error(f"❌ 분석 중 오류가 발생했습니다.")
                    
                    # 사용자 친화적 오류 메시지
                    if "module" in str(e).lower() or "import" in str(e).lower():
                        st.warning("💡 **시스템 초기화 중입니다.** 잠시 후 다시 시도해주세요.")
                    else:
                        st.info("🔄 시스템을 재시작하거나 페이지를 새로고침해주세요.")
                    
                    # 디버깅 정보 (개발 환경에서만)
                    with st.expander("🔍 기술 정보 (개발자용)", expanded=False):
                        st.code(f"""
오류 타입: {type(e).__name__}
오류 메시지: {str(e)}
답변 수: {len(st.session_state.answers)}
완료된 문항: {list(st.session_state.answers.keys())}
                        """)
                        
                        # 재시도 버튼
                        if st.button("🔄 다시 시도", key="retry_analysis"):
                            st.rerun()
                    
            else:
                error_count = len(st.session_state.validation_errors)
                st.error(f"⚠️ {error_count}개의 문항에 답변이 필요합니다!")
                
                # 오류가 있는 문항들 표시
                missing_questions = []
                for q_key in st.session_state.validation_errors:
                    if q_key in questions:
                        q_num = q_key.replace('q', '')
                        missing_questions.append(f"Q{q_num}")
                
                if missing_questions:
                    st.warning(f"📝 **미완료 문항**: {', '.join(missing_questions)}")
                    st.info("💡 위로 스크롤하여 미완료 문항을 찾아 답변해주세요.")
                
                # 페이지 새로고침하여 오류 표시
                time.sleep(0.5)
                st.rerun()

    # 추가 도움말
    st.markdown("---")
    
    help_col1, help_col2 = st.columns(2)
    
    with help_col1:
        st.markdown("""
        <div style="background: rgba(76, 175, 80, 0.1); padding: 20px; border-radius: 15px; border-left: 4px solid #4CAF50;">
            <h4 style="color: #2E7D32; margin-bottom: 10px;">💡 설문 작성 팁</h4>
            <ul style="color: #2E7D32; font-size: 0.9em; line-height: 1.6;">
                <li>직관적으로 가장 맞다고 생각하는 답변을 선택하세요</li>
                <li>모든 문항은 여행 성향 분석에 중요한 역할을 합니다</li>
                <li>정답은 없으니 솔직하게 답변해주세요</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with help_col2:
        st.markdown("""
        <div style="background: rgba(33, 150, 243, 0.1); padding: 20px; border-radius: 15px; border-left: 4px solid #2196F3;">
            <h4 style="color: #1976D2; margin-bottom: 10px;">📊 분석 결과</h4>
            <ul style="color: #1976D2; font-size: 0.9em; line-height: 1.6;">
                <li>개인별 12개 요인 점수 제공</li>
                <li>8개 클러스터 중 최적 유형 매칭</li>
                <li>맞춤형 한국 관광지 추천</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # 푸터
    show_footer()

# 실행부 - 강화된 에러 처리
if __name__ == '__main__':
    try:
        questionnaire_page()
    except Exception as e:
        st.error("❌ 페이지 로딩 중 오류가 발생했습니다.")
        
        # 일반적인 오류 해결 방법 제시
        if "module" in str(e).lower() or "import" in str(e).lower():
            st.warning("""
            🔧 **모듈 임포트 오류 해결 방법:**
            1. `utils.py` 파일이 프로젝트 루트 디렉토리에 있는지 확인
            2. 필요한 라이브러리가 설치되어 있는지 확인
            3. 페이지를 새로고침하거나 앱을 재시작
            """)
        else:
            st.info("🔄 페이지를 새로고침하거나 다시 시도해주세요.")
        
        # 에러 상세 정보 (개발자용)
        with st.expander("🔍 오류 상세 정보", expanded=False):
            st.exception(e)
        
        # 복구 옵션
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 페이지 새로고침", key="refresh_page"):
                st.rerun()
        
        with col2:
            if st.button("🏠 홈으로 돌아가기", key="home_redirect"):
                try:
                    st.switch_page("pages/03_home.py")
                except:
                    st.switch_page("app.py")
                
        with col3:
            if st.button("🚪 로그아웃", key="error_logout"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.switch_page("app.py")
else:
    questionnaire_page()