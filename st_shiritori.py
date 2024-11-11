import streamlit as st
from fugashi import Tagger
import time
import asyncio

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
        st.session_state.words_used.add(first_turn_result)
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
    elif current_result in st.session_state.words_used:
        st.markdown(f"もう使った！{st.session_state.current_player.name}の負けだ！")
        return False
    else:
        st.session_state.prev_result = current_result
        st.session_state.words_used.add(current_result)
        return True
    
def click_button():
    st.session_state.clicked = True

async def countdown(temporary):
    while st.session_state.timer > 0:
        temporary.metric("時間", st.session_state.timer)
        await asyncio.sleep(1)
        st.session_state.timer -= 1

    temporary.metric("時間", st.session_state.timer)
    st.markdown(f"時間が切れた！{st.session_state.current_player.name}の負けだ！")
    temporary.empty()

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
    st.session_state.clicked = False

    tagger.parse("変数")
    dummy_result = tagger("変数")[0]
    st.session_state.prev_result = dummy_result

    st.session_state.small_characters = {"ャ" : "ヤ","ュ" : "ユ","ョ" : "ヨ","ァ" : "ア","ゥ" : "ウ","ォ" : "オ","ェ" : "エ","ィ" : "イ",}
    st.session_state.words_used = set()

temporary = st.empty()

with temporary.container():
    st.markdown("名詞だけ使うべきだ")
    st.markdown("プレイヤーの言葉は先の言葉の語末と始まるべきだ")
    st.markdown("言葉は「ン」を語末すべきではない")
    st.markdown("前の言葉を使うべきではない")

    st.session_state.timer = st.slider("試合のタイマー", 5, 60)
    st.button("スタート", on_click=click_button)

if st.session_state.clicked:
    temporary.empty()

    st.session_state.counter += 1

    if st.session_state.state:
        temporary.metric("時間", st.session_state.timer)
        st.text_input("今の言葉", key="word")

        if len(st.session_state.word) and st.session_state.counter == 1:
            st.session_state.current_player.input = st.session_state.word
            st.session_state.word.clear()

            tagger.parse(st.session_state.current_player.input)
            first_turn_result = tagger(st.session_state.current_player.input)[0]
            st.session_state.state = first_turn(first_turn_result)

            st.session_state.prev_result = first_turn_result
        elif len(st.session_state.word):
            st.session_state.current_player.input = st.session_state.word

            tagger.parse(st.session_state.current_player.input)
            current_result = tagger(st.session_state.current_player.input)[0]
            st.session_state.state = turns(current_result)
        
        if st.session_state.state == False:
            temporary.empty()
        else:
            asyncio.run(countdown(temporary))

            st.session_state.state = False
            restart_bar = st.progress(0, "リスタートしています。。。")

            for x in range(100):
                time.sleep(0.01)
                restart_bar.progress(x + 1, "リスタートしています。。。")
            time.sleep(1)
            restart_bar.empty()
            st.rerun()

        if st.session_state.switch == -1:
            st.session_state.switch += 1
        else:
            st.session_state.switch -= 1
            st.session_state.current_player = st.session_state.players[st.session_state.switch]
    else:
        st.cache_data.clear()
        for key in st.session_state.keys():
             del st.session_state[key]
        st.button("もう一回")