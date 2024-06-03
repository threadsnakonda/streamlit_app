import streamlit as st
import datetime
from PIL import Image
import io
import pickle
import os
from pympler import asizeof

import cv2
import numpy as np
import pyautogui
from io import BytesIO


class Meeting_Minutes:

    def __init__(self):

        self.today = datetime.datetime.today()
        self.password = 'G3002bsjc!'

        if 'password_correct' not in st.session_state:
            st.session_state.password_correct = False

        if 'byte_images' not in st.session_state:
            st.session_state.byte_images = []

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

            date, title, description = self.set_form(self.today, None, None)

            submit = st.button(label = ':orange[submit]')
                
            if submit:
                if title != '' and description != '':
                    self.add_contents(date, title, description)
                    st.session_state.byte_images = []
                    st.rerun()

            st.divider()

            selected_idxs = list(range(0, len(st.session_state.contents)))
            key_word = st.text_input('***:green[Search Key-word]***')
            if key_word:
                selected_idxs = self.find_idx(key_word)

            upload_contents = st.file_uploader('***:blue[upload contents]***', type = ['pkl'], accept_multiple_files = True)
                
            if upload_contents:
                for upload_content in upload_contents:
                    upload_content = pickle.load(upload_content)
                    for content in upload_content:
                        if not content in st.session_state.contents:
                            st.session_state.contents.append(content)


            save_digits_col, pickle_contents_col, _ = st.columns([1, 1, 4])

            with save_digits_col:
                save_digits = st.button('***:orange[Save as binary digits]***')
                if save_digits:
                    try:
                        save_name = f'data/contents_{self.today.strftime("%Y_%m_%d_%H_%M_%S")}.pkl'
                        with open (save_name, 'wb') as f:
                            pickle.dump(st.session_state.contents, f)
                        st.toast(f'{save_name} save complete!')
                    except: pass

            with pickle_contents_col:
                pickle_contents = pickle.dumps(st.session_state.contents)
                st.download_button(
                    label = '***:violet[Download as binary digits]***',
                    data = pickle_contents,
                    file_name = f'contents_{self.today.strftime("%Y_%m_%d_%H_%M_%S")}.pkl',
                    mime = 'application/octet-stream',
                )

            with st.container(height = 700):
                self.display_data(selected_idxs)


    def capture_screen(self):
        screenshot = pyautogui.screenshot()
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        return img

    def select_roi(self, img):
        cv2.namedWindow("Select Region", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Select Region", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setWindowProperty("Select Region", cv2.WND_PROP_TOPMOST, 1)
        r = cv2.selectROI("Select Region", img, False, False)
        cv2.destroyAllWindows()
        return r

    def set_form(self, init_date, init_title, init_description):

        screen_shot = st.button('***:green[Add Screen-shot]***')
        if screen_shot:
            img = self.capture_screen()
            x, y, w, h = self.select_roi(img)
            if w > 0 and h > 0:
                screenshot = pyautogui.screenshot(region=(x, y, w, h))

                img_buffer = BytesIO()
                screenshot.save(img_buffer, format='PNG')
                byte_data = img_buffer.getvalue()
                st.session_state.byte_images.append(byte_data)

        if st.session_state.byte_images:
            cols = st.columns(len(st.session_state.byte_images))
            for i, (col, byte_image) in enumerate(zip(cols, st.session_state.byte_images)):
                with col:
                    image = Image.open(io.BytesIO(byte_image))
                    max_size = (200, 200)
                    image.thumbnail(max_size)
                    st.image(image)
                    if st.button('Delete', key=f'delete_{i}'):
                        del st.session_state.byte_images[i]
                        st.rerun()

        date = st.date_input('***Date***', init_date)
        title = st.text_input('***Title***', init_title)
        description = st.text_area('***Description***', init_description)

        return date, title, description


    def add_contents(self, date, title, description):
        content = {'date' : date, 'title' : title, 'images' : st.session_state.byte_images, 'description' : description}
        st.session_state.contents.append(content)
        st.session_state.contents.sort(key=lambda x: x['date'], reverse=True)

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
                            # max_size = (200, 200)
                            # image.thumbnail(max_size)
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