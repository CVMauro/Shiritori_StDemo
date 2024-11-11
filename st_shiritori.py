import streamlit as st
from fugashi import Tagger

class Player:
    def __init__(self, name, input):
        self.name = name
        self.input = input

@st.cache_resource
def load_model():
    return Tagger()

def first_turn(first_turn_result):
    if first_turn_result.pos[:2] != "名詞":
        st.markdown("名詞じゃない！P1の負けだ！")
        return False
    elif first_turn_result.feature.kana[-1] == "ン":
        st.markdown("語末は「ン」！P1の負けだ！")
        return False
    else:
        return True
    
def turns(current_result):
    previous_kana = st.session_state.prev_result.feature.kana[-1]
    if previous_kana == "ー":
        previous_kana = st.session_state.prev_result.feature.kana[-2]

    if current_result.pos[:2] != "名詞":
        st.markdown(f"名詞じゃない！{st.session_state.current_player.name}の負けだ！")
        return False
    elif current_result.feature.kana[0] != previous_kana and previous_kana not in st.session_state.small_characters:
        st.markdown(f"これは先の言葉が同じじゃない！{st.session_state.current_player.name}の負けだ！")
        return False
    elif previous_kana in st.session_state.small_characters and st.session_state.small_characters[previous_kana] != current_result.feature.kana[0]:
        st.markdown(f"これは先の言葉が同じじゃない！{st.session_state.current_player.name}の負けだ！")
        return False
    elif current_result.feature.kana[-1] == "ン":
        st.markdown(f"語末は「ン」！{st.session_state.current_player.name}の負けだ！")
        return False
    else:
        st.session_state.prev_result = current_result
        return True
    
tagger = load_model()

st.title("ようこそ、:green[しりとりへ]！")

if 'p1' not in st.session_state:
    st.session_state.p1 = Player("P1", "")
    st.session_state.p2 = Player("P2", "")

    st.session_state.players = [st.session_state.p1, st.session_state.p2]
    st.session_state.switch = 0
    st.session_state.current_player = st.session_state.players[0]
    st.session_state.counter = 0
    st.session_state.state = True

    tagger.parse("変数")
    dummy_result = tagger("変数")[0]
    st.session_state.prev_result = dummy_result

    st.session_state.small_characters = {"ャ" : "ヤ","ュ" : "ユ","ョ" : "ヨ","ァ" : "ア","ゥ" : "ウ","ォ" : "オ","ェ" : "エ","ィ" : "イ",}

st.session_state.counter += 1

if st.session_state.state:
    st.text_input("今の言葉", key="word")

    if len(st.session_state.word) and st.session_state.counter == 1:
        st.session_state.current_player.input = st.session_state.word

        tagger.parse(st.session_state.current_player.input)
        first_turn_result = tagger(st.session_state.current_player.input)[0]
        st.session_state.state = first_turn(first_turn_result)

        st.session_state.prev_result = first_turn_result
    elif len(st.session_state.word):
        st.session_state.current_player.input = st.session_state.word

        tagger.parse(st.session_state.current_player.input)
        current_result = tagger(st.session_state.current_player.input)[0]
        st.session_state.state = turns(current_result)

    if st.session_state.switch == -1:
        st.session_state.switch += 1
    else:
        st.session_state.switch -= 1
        st.session_state.current_player = st.session_state.players[st.session_state.switch]
