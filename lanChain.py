# 导入依赖包
import os
from langchain.embeddings.openai import OpenAIEmbeddings  #文本Embedding
from langchain.vectorstores import Chroma   #向量存储
from langchain.text_splitter import TokenTextSplitter #文本切分
from langchain.llms import OpenAI
#from langchain.chat_models import ChatOpenAI
from langchain.chains import ChatVectorDBChain #聊天向量数据库链
#from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders import DirectoryLoader #文件加载器
import jieba as jb  #汉字切词 文字向量预处理

import nltk  
from nltk.book import *

files=['yl.txt','xm.txt','ch.txt','xj.txt']

for file in files:
    #读取data文件夹中的中文文档
    my_file=f"./data/{file}"
    with open(my_file,"r",encoding='utf-8') as f:  
        data = f.read()
    
    #对中文文档进行分词处理
    cut_data = " ".join([w for w in list(jb.cut(data))])
    #分词处理后的文档保存到data文件夹中的cut子文件夹中
    cut_file=f"./data/cut/cut_{file}"
    with open(cut_file, 'w',encoding='utf-8') as f:   
        f.write(cut_data)
        f.close()

#加载文档
loader = DirectoryLoader('./data/cut',glob='**/*.txt')
docs = loader.load()

#文档切块
text_splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=0)
doc_texts = text_splitter.split_documents(docs)

#调用openai Embeddings
#这里填写你的key，或者在环境中写
#set OPENAI_API_KEY = "your key"
os.environ["OPENAI_API_KEY"] = "xxxxxx"
embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])

#向量化 这个动作要每次做吗？还是第一次做完，文件不变就不用做第二次，直接加载？
vectordb = Chroma.from_documents(doc_texts, embeddings, persist_directory="./data/cut")
vectordb.persist()

#创建聊天机器人对象chain
chain = ChatVectorDBChain.from_llm(OpenAI(temperature=0, model_name="gpt-3.5-turbo"), vectordb, return_source_documents=True)


def get_answer(question):
  chat_history = []
  result = chain({"question": question, "chat_history": chat_history});
  return result["answer"]


if __name__ == '__main__':
    question = "2023年3月都有什么新闻。用中文回答"
    print(get_answer(question))

