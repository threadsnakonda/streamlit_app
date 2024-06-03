import streamlit as st
from st_pages import Page, show_pages
from openai import OpenAI

class App_chat_gpt:

    def __init__(self):

        self.password = 'G3002bsjc!'
        if 'password_correct' not in st.session_state:
            st.session_state.password_correct = False
        if not 'api_key' in st.session_state:
            st.session_state.api_key = False

        self.init_chat = {
            'role': 'system',
            'content': '한국말로 간결하게 대답해줘. 코드를 생성하는 영역에는 영어로 써줘',
            }

        st.set_page_config(
            page_title="Chat GPT",
            page_icon="🚀",
            layout="wide",
            initial_sidebar_state="expanded",
            )

        show_pages(
            [
                Page('app_chat_gpt.py', '1. Chat_GPT'),
                # Page('other_pages/app_meeting_minutes.py', '2. Meeting Minutes'),
            ]
        )

        self.main_ui()

    def main_ui(self):

        if not st.session_state.password_correct:
            with st.form(key = 'form'):
                password = st.text_input(label = 'Pass Word', type = 'password')
                submit = st.form_submit_button(label = 'Submit')

            if submit:
                if not password == self.password:
                    st.title(':no_entry_sign: :busts_in_silhouette: Access is not possible')
                    return
                else:
                    st.session_state.password_correct = True
                    st.rerun()
            else:
                return

        if st.session_state.password_correct:

            if not st.session_state.api_key:
                st.session_state.api_key = st.text_input(label = 'OpenAI API KEY', type = 'password')

            st.subheader('무엇이든 물어보살')

            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []

            self.print_chat()
            if question :=st.chat_input('메세지를 입력해 주세요'):
                st.chat_message('user').write(question)
                with st.chat_message('assistant'):
                    answer_placeholder = st.empty()
                self.chat_generator(question, answer_placeholder)

            if st.session_state.chat_history:
                del_chat_chain = st.button(label = '대화 삭제')
                if del_chat_chain:
                    self.delete_chat_chain()


    def print_chat(self):
        if 'chat_history' in st.session_state:
            for chat in st.session_state.chat_history[1:]:
                st.chat_message(chat['role']).write(chat['content'])


    def chat_generator(self, question, answer_placeholder):

        client = OpenAI(api_key = st.session_state.api_key)
        
        if not st.session_state.chat_history:
            st.session_state.chat_history.append(self.init_chat)

        self.add_chat_history('user', question)

        try:
            response = client.chat.completions.create(
                model = 'gpt-4o',
                messages = st.session_state.chat_history,
                stream = True,
            )
        except:
            st.session_state.chat_history = []
            st.warning('Invalid API key', icon="⚠️")
            return

        answer = ''
        for chunk in response:
            chunk_content = chunk.choices[0].delta.content
            if isinstance(chunk_content, str):
                answer += chunk_content
                answer_placeholder.write(answer)

        self.add_chat_history('assistant', answer)

    def add_chat_history(self, role, content):
        st.session_state.chat_history.append(
            {'role' : role, 'content' : content,}
            )

    def delete_chat_chain(self):
        st.session_state.chat_history = []
        st.rerun()

if __name__ == '__main__':
    App_chat_gpt()