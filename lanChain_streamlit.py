"""Python file to serve as the frontend"""
#Note that when setting up your StreamLit app you should make sure to add OPENAI_API_KEY as a secret environment variable.
import streamlit as st
from streamlit_chat import message

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import FAISS
import tempfile

from langchain.memory import ConversationBufferWindowMemory
from langchain.memory import ConversationSummaryBufferMemory
from langchain.memory import ConversationEntityMemory

from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage

from langchain.llms import OpenAI

import os
import uvicorn
import json
import markdown


#我的
#os.environ["OPENAI_API_KEY"] = "sk-写在.env中" 
#机器人角色定位
role  = "你是个乐于助人的助手。用简练幽默的表现尽可能简短地回答。 "#"You are a helpful assistant. Answer as concisely as possible with a little humor expression."

if 'system' in st.session_state:
    role = st.session_state['system']

if 'prompts' not in st.session_state:
    st.session_state['prompts'] = [{"role": "system", "content": role}]
    st.session_state['role'] = role
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'sum' not in st.session_state:
    st.session_state['sum'] = 0 

st.set_page_config(page_title="LangChain Demo", page_icon=":robot:")
#st.header("LangChain Demo")
#print ("是否存在呢？"+st.session_state['past'])

def load_chain():
    from langchain.prompts.prompt import PromptTemplate

    MY_TEMPLATE = st.session_state['role'] + """

    Current conversation:
    {history}
    Human: {input}
    AI:"""
    MY_PROMPT = PromptTemplate(
        input_variables=["history", "input"], template=MY_TEMPLATE
    )

    if 'chain' not in st.session_state:
        print("没有chain没有chain没有chain没有chain没有chain")

        llm=ChatOpenAI()
        chain = ConversationChain(
            llm=llm, 
            prompt = MY_PROMPT,
            # We set a very low max_token_limit for the purposes of testing.
            #memory=ConversationSummaryBufferMemory(llm=llm, max_token_limit=40),
            memory=ConversationBufferWindowMemory(k=6),
            verbose=True,
        )
        st.session_state['chain'] = chain


    return st.session_state['chain']









def generate_response(chat_input):
    user_input = chat_input

    if user_input:
        chain  = load_chain()
        output = chain.predict(input=user_input)

    return output



def end_click():
    st.session_state['prompts'] = [{"role": "system", "content": role}]
    st.session_state['past'] = []
    st.session_state['generated'] = []
    st.session_state['user'] = ""

    load_chain().memory.clear()

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
    st.session_state['role'] = role
    st.session_state['prompts'] = [{"role": "system", "content": role}]
    if 'chain' in st.session_state:
        del st.session_state['chain']



def convert_string():
    # IMPORTANT: Cache the conversion to prevent computation on every rerun


    return json.dumps(st.session_state['prompts'],ensure_ascii=False )


#顶部的图片和标题
c1, c2 = st.columns([1, 6]) 
with c1:
    st.image("https://huggingface.co/front/assets/huggingface_logo-noborder.svg", width=80)
with c2:
    st.title("你的langChain助理")

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
            message(st.session_state['generated'][i], key=str(i), avatar_style="micah")
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
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



#if __name__ == '__main__':
#    uvicorn.run('lanChain_streamlit:app', host='localhost', port=8010,reload=True)




