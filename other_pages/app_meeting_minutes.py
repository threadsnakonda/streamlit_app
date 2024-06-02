import streamlit as st
import datetime
from PIL import Image
import io
import pickle
import os
from pympler import asizeof

class Meeting_Minutes:

    def __init__(self):

        self.today = datetime.datetime.today()
        self.password = 'G3002bsjc!'

        if 'password_correct' not in st.session_state:
            st.session_state.password_correct = False

        if not 'load_contents' in st.session_state:
            st.session_state.load_contents = True

        st.set_page_config(
            page_title="Meeting Minutes",
            page_icon="🚀",
            layout="wide",
            initial_sidebar_state="expanded",
            )

        self.main_ui()
        self.check_resouce()

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

            if os.path.exists('data') and st.session_state.load_contents:
                saved_files = [file for file in os.listdir('data') if file.endswith('.pkl')]
                if saved_files:
                    contents_data_path = 'data/' + sorted([x for x in saved_files if 'contents' in x])[-1]
                
                    with open (contents_data_path, 'rb') as f:
                        st.session_state.contents = pickle.load(f)
                        st.session_state.load_contents = False

            if not 'contents' in st.session_state:
                st.session_state.contents = []

            with st.form(key = 'form'):
                date, title, byte_images, description = self.set_form()
                submit = st.form_submit_button(label = ':orange[submit]')
                
            if submit:
                if title != '' and description != '':
                    self.add_contents(date, title, byte_images, description)

            selected_idxs = list(range(0, len(st.session_state.contents)))
            key_word = st.text_input('***:green[Search Key-word]***')
            if key_word:
                selected_idxs = self.find_idx(key_word)
            if selected_idxs:
                st.caption(selected_idxs)

            # save_col, download_col = st.columns(2)
            # with save_col:
            save_digits = st.button('Save as binary digits')
            if save_digits:
                with open (f'data/contents_{self.today.strftime("%Y_%m_%d_%H_%M_%S")}.pkl', 'wb') as f:
                    pickle.dump(st.session_state.contents, f)

            # with download_col:
            pickle_contents = pickle.dumps(st.session_state.contents)
            st.download_button(
                label = 'Download as binary digits',
                data = pickle_contents,
                file_name = f'contents_{self.today.strftime("%Y_%m_%d_%H_%M_%S")}.pkl',
                mime = 'application/octet-stream',
            )

            with st.container(height = 700):
                self.display_data(selected_idxs)


    def set_form(self):
        
        title_col, image_col = st.columns(2)
        with title_col:
            date = st.date_input('***Date***', self.today)
            title = st.text_input('***Title***', '')

        with image_col:
            images = st.file_uploader('***Image***',
                                      accept_multiple_files = True,
                                      type = [
                                          'bmp', 'gif', 'ico', 'jpeg',
                                          'jpg', 'png', 'tif', 'tiff',
                                          'webp',])
            
        byte_images = []
        if images:
            for image in images:
                byte_images.append(image.read())

        description = st.text_area('***Description***', '')

        return date, title, byte_images, description



    def add_contents(self, date, title, byte_images, description):
        content = {'date' : date, 'title' : title, 'images' : byte_images, 'description' : description}
        st.session_state.contents.append(content)
        st.session_state.contents.sort(key=lambda x: x['date'])

    def find_idx(self, key_word):
        selected_idxs = []
        for idx, content in enumerate(st.session_state.contents):
            if key_word.upper() in content['title'].upper() or key_word.upper() in content['description'].upper():
                selected_idxs.append(idx)
        return selected_idxs

    def display_data(self, selected_idxs):
        for idx, content in enumerate(st.session_state.contents):
            if idx in selected_idxs:
                with st.expander(f"***{idx}. {content['date']} : {content['title']}***", expanded = False):
                    
                    if content['images']:
                        cols = st.columns(len(content['images']))
                        for col, byte_image in zip(cols, content['images']):
                            image = Image.open(io.BytesIO(byte_image))
                            max_size = (200, 200)
                            image.thumbnail(max_size)
                            col.image(image)

                    st.write(content['description'])

                    delete = st.button(label = 'delete', key = f'{idx}')
                    if delete:
                        del st.session_state.contents[idx]
                        st.rerun()

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} GB"

    def check_resouce(self):
        with st.sidebar:
            st.text('<< used resource >>')
            resource_dict = {}
            for key in st.session_state.keys():
                resource_dict[key] = asizeof.asizeof(st.session_state[key])
            resource_dict = dict(sorted(resource_dict.items(), key=lambda item: item[1], reverse=True))
            for key, value in resource_dict.items():
                size = self.format_size(value)
                if size.split(' ')[-1] in ['KB', 'MB', 'GB']:
                    st.text(f'{key} : {size}')

if __name__ == '__main__':
    Meeting_Minutes()