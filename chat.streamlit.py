import openai
import openai.error
import json
import markdown
import streamlit as st
from streamlit_chat import message

#openai.api_key = 'sk-写在.env中'
#机器人角色定位
role  = "You are a helpful assistant. Answer as concisely as possible with a little humor expression."



if 'system' in st.session_state:
    role = st.session_state['system']

if 'prompts' not in st.session_state:
    st.session_state['prompts'] = [{"role": "system", "content": role}]
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'sum' not in st.session_state:
    st.session_state["sum"] = 0 
    

def generate_response(prompt):
    
    try:
        st.session_state['prompts'].append({"role": "user", "content":prompt})
        completion=openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = st.session_state['prompts']
        )
        
        message=completion.choices[0].message.content

        st.session_state["sum"]= st.session_state["sum"] + completion["usage"]["total_tokens"]
        st.session_state["total"] = f'总用量【{st.session_state["sum"]}】本次对话Tokens用量【{completion["usage"]["total_tokens"]} / 4096】 (提问+上文 {completion["usage"]["prompt_tokens"]}，回答 {completion["usage"]["completion_tokens"]} )'
    except openai.error.AuthenticationError:
        st.error("认证失败，请检查API-key是否正确。")
       
    except openai.error.Timeout:
        st.error("请求超时，请检查网络连接。")
        
    except openai.error.APIConnectionError:
        st.error("连接失败，请检查网络连接。")
        
    except openai.error.RateLimitError:
        st.error("请求过于频繁，请5s后再试。")
        
    except:
        st.error("发生了未知错误")



    return message

def end_click():
    st.session_state['prompts'] = [{"role": "system", "content": role}]
    st.session_state['past'] = []
    st.session_state['generated'] = []
    st.session_state['user'] = ""

def chat_click():
    if st.session_state['user']!= '':
        chat_input = st.session_state['user']
        output=generate_response(chat_input)
        #store the output
        st.session_state['past'].append(chat_input)
        st.session_state['generated'].append(output)
        st.session_state['prompts'].append({"role": "assistant", "content": output})
        st.session_state['user'] = ""

def  sys_click():
    role = st.session_state['system']
    st.session_state['prompts'] = [{"role": "system", "content": role}]



def convert_string():
    # IMPORTANT: Cache the conversion to prevent computation on every rerun


    return json.dumps(st.session_state['prompts'],ensure_ascii=False )



st.set_page_config(page_title='对话机器人')
#顶部的图片和标题
c1, c2 = st.columns([1, 6]) 
with c1:
    st.image("https://huggingface.co/front/assets/huggingface_logo-noborder.svg", width=80)
with c2:
    st.title("你的机器人助手")

#聊天输入框
user_input=st.text_input("这里输入", key="user")

#输入框下面的两个按钮，用行列控制layout
col1, col2 = st.columns([6, 1])
with col2:
    chat_button=st.button("Send", on_click=chat_click)

with col1:
     end_button=st.button("重新开始", on_click=end_click)


#分成两个标签页布局，一个放对话内容，一个观测数据。
tab1, tab2 ,tab3 = st.tabs(["对话", "统计","设定"])    

if 'generated' in st.session_state:       
    with tab1:
        #range(start, stop[, step]) 从最后走到-1，步长-1，倒着取值
        for i in range(len(st.session_state['generated'])-1, -1, -1):
            message(markdown.markdown(  st.session_state['generated'][i]), key=str(i), avatar_style="big-smile")
            message(markdown.markdown(  st.session_state['past'][i]), is_user=True, key=str(i) + '_user')
    with tab2:
        #查看使用了多少token
        if 'total' in st.session_state:
            st.info(st.session_state["total"])

        #st.download_button(label="对话下载",data="")
        st.download_button(
            label="Download history as txt",
            data=convert_string(),
            file_name='history.txt',
            mime='text/txt',
        )

    with tab3:
        #修改system角色设定
        sys_input=st.text_area("修改设定",role,key="system")
        cc1, cc2 = st.columns([ 6,1]) 
        with cc2:
            sys_button=st.button("确定",on_click=sys_click)
    

        