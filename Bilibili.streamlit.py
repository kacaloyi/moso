#官方SDK，只能链接自己的房间。而且要在房间开启的情况下。
#很不好用。
#可以需要结合网上的一些项目做改造

#弹幕游戏框架（有年头了，不知道还能不能联通）
#https://github.com/VoidmatrixHeathcliff/DanmuGame

import proto
from ws import BiliClient
        
import streamlit as st
import streamlit_chat as message



host = "live-open.biliapi.com"
#key_id = ""
#key_secret = ""
#room_id = ""

#如果已经有一个streamlit实例在跑，这个会失败。
#st.set_page_config(page_title='B站直播互动')

if 'key_id' not in st.session_state:
    st.session_state['key_id'] = "fJuy7knWmYxdEtzu81eXQZqv"
if 'key_secret' not in st.session_state:
    st.session_state['key_secret'] = "cwrVSAcgYD4YPqkcUVeUfNzsJIbpbN"
if 'room_id' not in st.session_state:
    st.session_state['room_id'] = "1029"




def run_click():
    room = st.session_state['room_id']
    k_secret =st.session_state['key_secret']
    k_id = st.session_state['key_id']

    try:
        cli = BiliClient(
            roomId = room,
            key = k_id,
            secret = k_secret,
            host = host)
        cli.run()
    except Exception as e:
        print("err", e)






room_id_input =st.text_input("房间号", key="room_id")
key_id_input  =st.text_input("access_key_id", key="key_id")
key_secret_input=st.text_input("access_key_secret", key="key_secret")

r1c1,r1c2=st.columns([6,1])
with r1c2:
    run_button=st.button("开始", on_click=run_click)


#! python -m streamlit run Bilibili.streamlit.py

#！您提交的入驻申请已通过，秘钥如下：
#access_key_id:fJuy7knWmYxdEtzu81eXQZqv
#access_key_secret:cwrVSAcgYD4YPqkcUVeUfNzsJIbpbN
#房间号：1029 2559737 27349261

