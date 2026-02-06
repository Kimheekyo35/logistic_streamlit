import streamlit as st
import subprocess
import sys
from pathlib import Path

menu = st.sidebar.radio("Menu", ["홈","Fwee 송장번호 크롤링", "Numbuzin 송장번호 크롤링"])

if menu == "홈":                                                                
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
