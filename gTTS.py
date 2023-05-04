import streamlit as st


from gtts import gTTS


from playsound import playsound
from io import BytesIO


sound = BytesIO()

placeholder = st.container()


placeholder.title("说话")

tr = st.empty()
text = tr.text_area("**这里输入你想说的话**") #, value=st.session_state['input']['text']

def onTTS():
    output = text #st.session_state['input']['text']
    tts = gTTS(output, lang='zh-CN')
    tts.write_to_fp(sound)
    #playsound(sound)
    st.audio(sound)


#st.button("TTS",on_click=onTTS)


def on_speech():
  import speech
  speech.say(text)

#st.button("speech",on_click=on_speech)


def on_pyttsx3():   
   import pyttsx4
   engine = pyttsx4.init()
   engine.setProperty('rate',300)
   engine.setProperty('volume',0.7)
   voices = engine.getProperty('voices')
   for vc in voices:
      print("id={},name={}".format(vc.id,vc.name))

   engine.setProperty('voice',voices[0].id)
   output = text
   engine.say(output)
   #engine.save_to_file(text,sound)
   engine.runAndWait()
   engine.stop()
  # st.audio(sound)

st.button("ttsx",on_click=on_pyttsx3)


# python -m streamlit run .\gTTS.py