"""남도ON 첫 화면. 기존 app.py의 관광정보 데이터프레임을 전달받습니다."""
import html
import pandas as pd
import streamlit as st
from namdo_overview import show_overview

MENU = {
    "현황": "📊 관광 종합현황",
    "지도": "🗺️ 관광지 검색·지도",
    "체류": "🌙 체류 강도 분석",
    "소비": "💳 소비 강도 분석",
    "출처": "📚 데이터 출처",
}


def _move(target):
    st.session_state["namdo_navigation"] = target


def show_intro(places: pd.DataFrame, stay: pd.DataFrame, spend: pd.DataFrame):
    st.markdown("""<style>
    .intro-heading {font-size:23px;font-weight:800;color:#143b55;margin:25px 0 13px}
    .intro-sub {font-size:13px;color:#61798d;margin-top:-7px;margin-bottom:18px}
    .intro-banner {background:linear-gradient(125deg,#092f4e 0%,#086983 65%,#1e9c9c 100%);
        border-radius:18px;padding:25px 32px;color:white;margin-bottom:18px}
    .intro-banner h2 {color:white!important;margin:4px 0 10px;font-size:29px}
    .intro-banner p {color:#e2f7ff;margin:0;font-size:14px}
    .intro-tag {display:inline-block;padding:5px 11px;background:#ffffff22;border:1px solid #ffffff55;
        border-radius:30px;font-size:11px;font-weight:750;letter-spacing:1px}
    .intro-card {padding:22px 21px;border-radius:15px;background:#fff;border:1px solid #e2eaf0;
        min-height:144px;box-shadow:0 5px 16px #183b4b0b}
    .intro-card strong {font-size:19px;color:#123f56}
    .intro-card p {font-size:13px;color:#637b8b;margin:11px 0 0;line-height:1.6}
    .intro-pill {background:#e8f4f6;color:#05758c;border-radius:6px;padding:3px 8px;font-size:11px}
    </style>""", unsafe_allow_html=True)
    st.markdown("""<div class='intro-banner'>
    <span class='intro-tag'>NAMDO ON · TOURISM DATA PROJECT</span>
    <h2>데이터로 만나는 전남·광주 여행</h2>
    <p>어디에 관광 콘텐츠가 많을까? 체류와 소비 특성은 어떻게 다를까?<br>
    공공데이터로 남도의 관광 매력을 한눈에 살펴보세요.</p>
    </div>""", unsafe_allow_html=True)

    pcount = len(places)
    jcount = int((places['수집권역'].astype(str) == '전남').sum()) if '수집권역' in places else 0
    gcount = int((places['수집권역'].astype(str) == '광주').sum()) if '수집권역' in places else 0
    months = set()
    for frame in (stay, spend):
        if 'baseYm' in frame:
            months.update(str(x).split('.')[0] for x in frame['baseYm'].dropna().tolist() if str(x)[:6].isdigit() and len(str(x))>=6 and '202509' <= str(x)[:6] <= '202606')
    k1,k2,k3,k4=st.columns(4)
    k1.metric('전체 관광 콘텐츠',f'{pcount:,}건')
    k2.metric('전남 관광 콘텐츠',f'{jcount:,}건')
    k3.metric('광주 관광 콘텐츠',f'{gcount:,}건')
    k4.metric('수요 분석 기간',f'{len(months)}개월')
    st.caption('관광 콘텐츠는 한국관광공사 API 수집 건수입니다. 분석기간은 확보된 수요 데이터의 2025.09~2026.06 구간 기준입니다.')

    show_overview(places,stay,spend)
    st.markdown('<div class="intro-heading">한눈에 보는 주요 기능</div>',unsafe_allow_html=True)
    st.markdown('<div class="intro-sub">각 기능에서 실제 수집 데이터에 대한 차트·검색·상세정보를 확인할 수 있습니다.</div>',unsafe_allow_html=True)
    cards = [
        ('📊 관광 종합현황','관광지·음식점·숙박 등 유형별 분포와 전남·광주 비교','현황'),
        ('🗺️ 관광지 검색·지도','유형·지역 검색, 마커 클러스터, 마우스 오버와 관광 콘텐츠 카드','지도'),
        ('🌙 체류 강도 분석','월별·시군구별 숙박·방문 체류 강도 지표 비교','체류'),
        ('💳 소비 강도 분석','월별·지역별 관광 소비 강도 지표 비교','소비'),
    ]
    for start in (0,2):
        cols=st.columns(2,gap='medium')
        for col,(title,description,key) in zip(cols,cards[start:start+2]):
            with col:
                with st.container(border=True):
                    st.markdown(f'<div style="font-size:19px;font-weight:780;color:#134764;margin:2px 0 8px">{html.escape(title)}</div>',unsafe_allow_html=True)
                    st.write(description)
                    st.button('분석 화면 열기 →',key=f'intro_go_{key}',width='stretch',on_click=_move,args=(MENU[key],))
    st.markdown('<div class="intro-heading">관광 콘텐츠 미리보기</div>',unsafe_allow_html=True)
    if places.empty or not {'firstimage','title'}.issubset(places.columns):
        st.info('관광 콘텐츠 데이터를 불러오면 이미지 미리보기가 표시됩니다.')
    else:
        sample=places.loc[places['firstimage'].fillna('').astype(str).str.startswith('http')].head(3)
        if sample.empty:
            st.info('등록된 관광 사진이 없습니다.')
        else:
            cols=st.columns(3)
            for col,(_,item) in zip(cols,sample.iterrows()):
                with col:
                    with st.container(border=True):
                        try:
                            st.image(str(item['firstimage']),width='stretch')
                        except Exception:
                            st.caption('이미지 로딩 불가')
                        st.markdown('**'+html.escape(str(item['title']))+'**')
                        st.caption(f"{item.get('수집권역','')} · {item.get('콘텐츠유형명','')}")
    st.info('자료 출처: 한국관광공사 국문 관광정보 서비스 및 지역별 관광 수요 강도 API. 수요 강도는 실제 방문객 수나 결제 총액이 아닙니다.')
    st.button('데이터 출처 확인 →',key='intro_go_source',on_click=_move,args=(MENU['출처'],))
