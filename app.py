"""
お問い合わせ機能追加、メール送信をmailhogで確認 @app02.py
<ブログ記事名>
「【Streamlit v1.46.1】お問い合わせ機能の追加とMailHogで受信確認」
-------------------------
(1)このapp.pyは上のapp02.pyの拡張版です。SQLite3なしでも
 st.session_state[]で保持、一応できた。signup後のご登録ありがとうメールの送信も追加!
 ここからさらに、SQLite3と連携させる（テーブルのリレーションなし、usersのみ）
 <ブログ記事名>


"""

import streamlit as st #  v1.46.1 ⇨ v1.47.1(25/08/04)
# ↓画像を扱いたい方は以下もimportすると便利です。
from PIL import Image
import sqlite3
import smtplib # smtplibモジュールはPythonの標準ライブラリ、pipでインストールする必要なし。
from email.mime.text import MIMEText #  MIME形式のデータを送信するため
from email.mime.multipart import MIMEMultipart # MIME形式のmultipartメッセージを作成する
# ↓pip install email-validator
from email_validator import validate_email, EmailNotValidError
import os
import pandas as pd
import copy
import logging


BaseDir = "uploadfile"
Basefilename = "バイタルデータ.csv"

# 状態管理
if "page" not in st.session_state:
    st.session_state["page"] = "login"

if "mypage" not in st.session_state:
    st.session_state["mypage"] = "Home" 


# ---SQLite3処理関数---
# ユーザー情報
def create_user(username, email, password):
    conn = sqlite3.connect("st-menber.db")
    try: 
        cur = conn.cursor()
        cur.execute("insert into users (username, email, password) values (?,?,?)",(username, email, password))
        conn.commit()
        conn.close()
        print("サンプルユーザーの作成に成功しました")
        return True
    except Exception as e:
        logging.exception("エラーが発生しました: %s", e)
        return False
    

# 特定のユーザー取得
def get_user(username, password):
    conn = sqlite3.connect("st-menber.db")
    try:
        cur = conn.cursor()
        cur.execute("select username, password from users where username = ?",(username,))
        row = cur.fetchone()
        # print(row[1])
        # print(len(row))
        conn.close()
        return row
    except Exception as e:
        st.error(f"ユーザー情報取得エラー: {e}")
        return None
        

# --ユーザー認証関数---
# メールアドレスの検証
def is_valid_email(email):
    try:
        # validate the email address given, raises an exception if it's not valid
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError as e:
        # email is not valid, exception message is human-readable
        # print(str(e))
        return False

# thank you mail
def signup_mail(username, email):
     # メール構築
    msg = MIMEMultipart()  # クラスインスタンス
    msg["From"] = "info@example.com"
    msg["To"] = email
    msg["Subject"] = "ご登録ありがとうざいます。"
    body = f"{username}様 \n この度はご登録ありがとうざいました。\n 宜しくお願い致します。"
    msg.attach(MIMEText(body, "plain"))  # MIMEオブジェクトを生成

    # MailHogのSMTPサーバーに送信
    smtp = smtplib.SMTP("localhost", 1026)
    smtp.send_message(msg)
    smtp.quit()  # smtpセッションを切る

    
# 画面遷移先
def Registor():
    #ここから処理記載 ※sidebarの中で呼び出せばsidebarに表示される
    with st.form(key='signup-form',clear_on_submit=True):
        username = st.text_input("お名前", placeholder="氏名をご記入")
        email = st.text_input("メールアドレス", placeholder="メールアドレスをご記入")
        password1 = st.text_input("パスワード" , type="password", placeholder="パスワードをご記入")
        password2 = st.text_input("パスワード(確認用)" , type="password", placeholder="もう一度パスワードをご記入")
        submit_button = st.form_submit_button(label='登録')
        if submit_button:
            if username == "":
                st.markdown("<span style='color:red;'>お名前をご記入ください</span>", unsafe_allow_html=True) 
            elif email == "":
                st.markdown("<span style='color:red;'>メールアドレスをご記入ください</span>", unsafe_allow_html=True) 
            elif not is_valid_email(email):
                st.markdown("<span style='color:red;'>" f"{email} は無効なメールアドレスです。"
                "</span>", unsafe_allow_html=True) 
            elif password1 != password2:
                st.markdown("<span style='color:red;'>パスワードが一致しません</span>", unsafe_allow_html=True) 
            else:
                # 登録処理
                result = create_user(username, email, password1)

                if result:
                    st.session_state["page"] = "login"
                    st.markdown("<span style='color:blue;'>ご登録ありがとうございました。</span>", unsafe_allow_html=True) 
                    signup_mail(username, email)
                    st.rerun()
                else:
                    st.markdown("<span style='color:red;'>申し訳ありませんが、再度ご登録をお願いします。</span>", unsafe_allow_html=True) 

    st.divider()
    if st.button("ログイン画面に戻る"):
        st.session_state["page"] = "login"
        st.rerun()

def Home():
    st.header('ホーム画面')
    # 何も無いと寂しいので、取り敢えず画像を左右に並べています。
    img1="./images/公園の河.jpg"      # ←プロジェクト内で保存
    img2="./images/palazzina寺院.jpg" # ←プロジェクト内で保存
    # ここで画面を左右に２分割しています。
    col1,col2 = st.columns(2)
    # 左側に画像を表示
    with col1:
        image1= Image.open(img1)
        st.image(image1)
    # 右側に別の画像を表示
    with col2:
        image2 = Image.open(img2)
        st.image(image2)

def info():
    st.header('お知らせ')
    st.write("〇〇公園のひまわりが見頃です。")
    st.write("〇〇町の祇園祭が無事終了しました。")
    # 何らかの処理を書く

# お問い合わせ関数
def inquiry():
    st.header('お問い合わせ')
    with st.form(key='form-inquiry',clear_on_submit=True):
        from_name = st.text_input('お名前', placeholder="氏名をご記入")
        from_address = st.text_input('メールアドレス', placeholder="メールアドレス記入")
        body = st.text_area("お問い合わせ内容", placeholder="自由にご記入ください")
        subject = "お問い合わせの件"
        submit_button = st.form_submit_button(label='送信')
    
        if submit_button:
            if from_name == "":
                st.markdown("<span style='color:red;'>お名前をご記入ください</span>", unsafe_allow_html=True) 
            elif from_address == "":
                st.markdown("<span style='color:red;'>メールアドレスをご記入ください</span>", unsafe_allow_html=True) 
            elif not is_valid_email(from_address):
                st.markdown("<span style='color:red;'>" f"{from_address} は無効なメールアドレスです。"
                "</span>", unsafe_allow_html=True) 
            elif body == "":
                st.markdown("<span style='color:red;'>お問い合わせ内容をご記入ください</span>", unsafe_allow_html=True) 

            
            else:
                # メール構築
                msg = MIMEMultipart()  # クラスインスタンス
                msg["From"] = from_address
                msg["To"] = "info.sample.com"
                # msg["To"] = "tatsu.gunchan@gmail.com"  # Googleの場合
                msg["Subject"] = subject
                msg.attach(MIMEText(body, "plain"))  # MIMEオブジェクトを生成

                # MailHogのSMTPサーバーに送信
                smtp = smtplib.SMTP("localhost", 1026)
                smtp.send_message(msg)
                smtp.quit()  # smtpセッションを切る

                # Googleの場合
                # app_pasword= 'gcau lawd uisw viwl'
                # smtp = smtplib.SMTP("smtp.gmail.com", 587)
                # smtp.starttls()
                # smtp.login("dbfummaster@gmail.com", app_pasword)
                # smtp.send_message(msg)
                # smtp.quit() 

                # 後処理
                st.markdown("<span style='color:blue;'>送信ありがとうございました。</span>", unsafe_allow_html=True) 

#　


# サイドバーの実装
with st.sidebar:
    if st.session_state["page"]== "login":
        st.header('ログイン')
        username = st.text_input("ユーザー名")
        password = st.text_input("パスワード", type="password")

        if st.button("ログイン"):
            # 認証処理
            result=get_user(username, password)
            if result is not None and password == result[1] :
                st.session_state["page"] = "dashboard"
                st.session_state["mypage"] = 'Home'
                st.session_state["login_user"] = result[0]
                st.rerun()
            else:
                st.markdown("<span style='color:red;'>" + f"{username}さん、ログイン失敗" + "</span>", unsafe_allow_html=True) 
            # for user in dict_data:
            #     if user.get("username") == username and user.get("password") == password:
            #         st.session_state["page"] = "dashboard"
            #         st.session_state["mypage"] = 'Home'
            #         st.session_state["login_user"] = username
                    # ↓Streamlitのv1.26.0以降でst.experimental_rerun()はst.rerun()に置き換えられました。
                    # st.rerun()  
                    # break
            # st.markdown("<span style='color:red;'>" + f"{username}さん、ログイン失敗" + "</span>", unsafe_allow_html=True) 
        st.divider()
        if st.button('新規登録はこちらから'):
            st.session_state["page"] = "signup"
            st.rerun()

    elif st.session_state["page"]== "dashboard":
        # st.write("ログインに成功しました。<br>ようこそ!!")  # NG
        # st.markdown("ログインに成功しました。  \nようこそ!!")  # OK ※半角スペース２個+\nで改行になる
        # st.markdown("ログインに成功しました。<br>ようこそ!!")  # NG
        st.write("ログインに成功しました。")
        st.write(f"{st.session_state['login_user']}さん、ようこそ")

        dash_page = st.selectbox('選択してください',['Home','お知らせ', 'お問い合わせ'])
        st.session_state["mypage"] = dash_page

        st.divider()
        # ログアウトボタン
        if st.button('ログアウト'):
            st.session_state["page"] = 'login'
            st.session_state["login_user"] = None
            st.rerun()  # 再読込
    elif st.session_state["page"] == "signup":
        st.header('登録フォーム')
        st.write("アカウントをお持ちでない方はこちらから登録してください。")
        Registor()

# メイン画面の設計
if st.session_state["page"] == "dashboard":
    # st.header('ダッシュボード')
    # 画面遷移
    if st.session_state["mypage"] == "Home":
        Home()
    elif st.session_state["mypage"] == "お知らせ":
        info()
    elif st.session_state["mypage"] == "お問い合わせ":
        inquiry()

    # # ログアウトボタン
    # if st.button('logout'):
    #     st.session_state["page"] = 'login'
    #     st.rerun()  # 再読込

    

