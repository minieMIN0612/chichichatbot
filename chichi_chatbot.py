import streamlit as st
import openai

# 페이지 설정
st.set_page_config(page_title="치치와 감정 알아보기", page_icon="🐱")
st.title("🐱 치치가 들어줄게냥!")
st.write("무슨 일이 있었냥? 어떤 마음인지 함께 알아보자냥!")

# ✅ secrets에서 API 키 가져오기
openai.api_key = st.secrets["OPENAI_API_KEY"]

# 세션 상태 초기화
if "stage" not in st.session_state:
    st.session_state.stage = "ask_who"
if "who" not in st.session_state:
    st.session_state.who = ""
if "when" not in st.session_state:
    st.session_state.when = ""
if "what" not in st.session_state:
    st.session_state.what = ""
if "emotion_choices" not in st.session_state:
    st.session_state.emotion_choices = []
if "final_emotion" not in st.session_state:
    st.session_state.final_emotion = ""
if "response" not in st.session_state:
    st.session_state.response = ""

# GPT 응답 생성 함수
def get_emotion_candidates(who, when, what):
    prompt = f"누구: {who}\n언제: {when}\n어떤 일: {what}\n위 상황에서 예상되는 감정 단어 3개와 각 단어의 정의를 다음 형식으로 알려줘: 감정단어: 정의"
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "넌 감정을 분석해주는 따뜻한 고양이야. 사용자에게 '~냥' 말투로 반응하고, 상황을 듣고 예상 감정 단어를 정의와 함께 제공해줘. 감정 단어만 제시하고, 그 외 멘트는 하지 마."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def get_alternative_emotions(who, when, what):
    prompt = f"누구: {who}\n언제: {when}\n어떤 일: {what}\n이전에 제공한 감정이 아니라고 했을 때, 대체 가능한 감정 단어 3개와 그 정의를 감정단어: 정의 형태로 알려줘."
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "넌 감정을 분석해주는 따뜻한 고양이야. 사용자에게 '~냥' 말투로 반응하고, 상황을 듣고 예상 감정 단어를 정의와 함께 제공해줘. 감정 단어만 제시하고, 그 외 멘트는 하지 마."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def get_final_response(emotion, who, when, what):
    prompt = f"누구: {who}\n언제: {when}\n무슨 일: {what}\n감정: {emotion}\n이런 상황에서 고양이 치치가 아이의 감정을 진심으로 이해하고 따뜻하게 위로해주는 말을 '~냥' 말투로 해줘. 문장은 간단하고 진심 어린 느낌이면 좋아. 지나치게 흥분하거나 유아어처럼 들리면 안 돼."
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "너는 고양이 치치야. 치치는 초등학생처럼 귀엽고 다정하게 이야기해. '~냥' 말투를 써서 따뜻하게 감정을 받아주고, 진심으로 공감하거나 위로해줘. 말투는 너무 흥분하거나 과하게 장난스럽지 않고, 차분하고 진심 어린 말투로 말해. '하둑'이나 이상한 단어는 쓰지 마. 문장은 간결하고 자연스럽게 해줘."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# 단계별 인터페이스
if st.session_state.stage == "ask_who":
    st.session_state.who = st.text_input("🐱 누구와 있었던 일이냥?")
    if st.button("다음") and st.session_state.who.strip():
        st.session_state.stage = "ask_when"
        st.rerun()

elif st.session_state.stage == "ask_when":
    st.session_state.when = st.text_input("🐱 그건 언제 있었던 일이냥?")
    if st.button("다음") and st.session_state.when.strip():
        st.session_state.stage = "ask_what"
        st.rerun()

elif st.session_state.stage == "ask_what":
    st.session_state.what = st.text_area("🐱 어떤 일이 있었는지 자세히 말해주라옹")
    if st.button("다음") and st.session_state.what.strip():
        with st.spinner("치치가 감정을 추측 중이야... 🐾"):
            result = get_emotion_candidates(st.session_state.who, st.session_state.when, st.session_state.what)
            st.session_state.emotion_choices = [line.strip() for line in result.split("\n") if ":" in line]
        st.session_state.stage = "choose_emotion"
        st.rerun()

elif st.session_state.stage == "choose_emotion":
    st.write("🐱 치치의 생각은 이렇다옹:")
    chosen = st.radio("이 중 어떤 감정이 제일 비슷하냥?", options=st.session_state.emotion_choices + ["이 감정들이 아니야"])
    if st.button("선택"):
        if chosen == "이 감정들이 아니야":
            with st.spinner("다른 감정을 찾아보는 중이다옹..."):
                new_choices = get_alternative_emotions(st.session_state.who, st.session_state.when, st.session_state.what)
                st.session_state.emotion_choices = [line.strip() for line in new_choices.split("\n") if ":" in line]
                st.rerun()
        else:
            st.session_state.final_emotion = chosen.split(":")[0].strip()
            st.session_state.stage = "show_response"
            st.rerun()

elif st.session_state.stage == "show_response":
    st.write("🐱 치치의 대답:")
    st.success(get_final_response(st.session_state.final_emotion, st.session_state.who, st.session_state.when, st.session_state.what))
    if st.button("↩️ 다시 시작하기"):
        for key in ["stage", "who", "when", "what", "emotion_choices", "final_emotion", "response"]:
            st.session_state.pop(key, None)
        st.rerun()
