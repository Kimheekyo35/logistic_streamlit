import streamlit as st
import subprocess
import sys
from pathlib import Path

menu = st.sidebar.radio("Menu", ["홈","Fwee 송장번호 크롤링", "Numbuzin 송장번호 크롤링"])

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# 로그인 함수 정의
def login(id, pw):
    if id == "admin" and pw == "admin123":
        st.session_state["logged_in"] = True
        st.success("로그인 성공!")
        st.rerun() # 페이지 새로고침
    else:
        st.error("아이디 또는 비밀번호가 올바르지 않습니다.")

def logout():
    st.session_state["logged_in"] = False
    st.success("로그아웃 되었습니다.")
    st.rerun() # 페이지 새로고침

# 로그인 화면
if not st.session_state["logged_in"]:
    st.title("로그인")
    id = st.text_input("아이디")
    pw = st.text_input("비밀번호", type="password")
    if st.button("로그인"):
        login(id, pw)
    st.stop()  # 로그인 전에는 아래 코드 실행 안 함

elif menu == "홈":                                                           
    st.title("물류팀 shopee 송장번호 크롤링 자동화 프로그램")                                                              
    st.write("Welcome to the homepage!")                 

elif menu == "Fwee 송장번호 크롤링":                                                          
    st.title("Fwee 송장번호 크롤링")                                                          
    st.subheader("사용 방법")
    st.text("1. '로그인 세션' 버튼 클릭 -> 인증코드 입력 -> 반드시 '확인' 버튼 클릭")
    st.text("2. 30초 정도 대기")
    st.text("2. 원하는 나라 선택 후 크롤링 시작")
    st.write("----------------------------------------------------------------")
    script_path = Path(__file__).parent / "fwee_auth_login_once.py"

    if st.button("로그인 세션 시작"):
        st.session_state.proc = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=script_path.parent,
        )
        st.success("세션 시작됨. 인증코드 입력 후 확인하세요.")

    with st.form("auth_form"):
        code = st.text_input("인증코드")                                                              
        submitted = st.form_submit_button("확인")                                                     
                                                                                                        
    if submitted:                                                                                     
        proc = st.session_state.proc                                                                  
        if not proc or proc.poll() is not None:                                                       
            st.error("실행 중인 세션이 없습니다.")                                                    
        elif not code.strip():                                                                        
            st.warning("인증코드를 입력하세요.")                                                      
        else:                                                                                         
            proc.stdin.write(code.strip() + "\n")                                                     
            proc.stdin.flush()                                                                        
            st.success("인증 완료") 
            
    with st.form("country_form"):
        options = ["Singapore", "Malaysia", "Thailand", "Philippines", "Vietnam", "Taiwan Xiapi"]
        selected_countries = st.multiselect("나라를 선택하세요:", options)
        country_submitted = st.form_submit_button("크롤링 시작")

        if country_submitted and selected_countries:
            script = Path(__file__).parent / "fwee_crawling.py"
            subprocess.run([sys.executable, str(script), *selected_countries], cwd=script.parent)
            st.success("크롤링이 완료되었습니다.")


elif menu == "Numbuzin 송장번호 크롤링":                                                            
    st.title("Numbuzin 송장번호 크롤링")  
    st.subheader("사용 방법")
    st.text("1. '로그인 세션' 버튼 클릭 -> 인증코드 입력 -> 반드시 '확인' 버튼 클릭")
    st.text("2. 30초 정도 대기")
    st.text("2. 원하는 나라 선택 후 크롤링 시작")
    st.write("----------------------------------------------------------------")
    script_path = Path(__file__).parent / "numbuzin_auth_login_once.py"             
                                                                                    
    if st.button("로그인 세션 시작"):                                               
        st.session_state.proc = subprocess.Popen(                                   
            [sys.executable, str(script_path)],                                     
            stdin=subprocess.PIPE,                                                  
            stdout=subprocess.PIPE,                                                 
            stderr=subprocess.PIPE,                                                 
            text=True,                                                              
            cwd=script_path.parent,                                                 
        )                                                                           
        st.success("세션 시작됨. 인증코드 입력 후 확인하세요.")                     
                                                                                    
    with st.form("auth_form"):
        code = st.text_input("인증코드")                                                              
        submitted = st.form_submit_button("확인")                                                     
                                                                                                        
        if submitted:                                                                                     
            proc = st.session_state.proc                                                                  
            if not proc or proc.poll() is not None:                                                       
                st.error("실행 중인 세션이 없습니다.")                                                    
            elif not code.strip():                                                                        
                st.warning("인증코드를 입력하세요.")                                                      
            else:                                                                                         
                proc.stdin.write(code.strip() + "\n")                                                     
                proc.stdin.flush()                                                                        
                st.success("인증 완료")
    
    with st.form("country_form"):
        options = ["Singapore", "Malaysia", "Philippines", "Vietnam", "Taiwan Xiapi"]
        selected_countries = st.multiselect("나라를 선택하세요:", options)
        country_submitted = st.form_submit_button("크롤링 시작")

        if country_submitted and selected_countries:
            script = Path(__file__).parent / "numbuzin_crawling.py"
            subprocess.run([sys.executable, str(script), *selected_countries], cwd=script.parent)
            st.success("크롤링이 완료되었습니다.")
