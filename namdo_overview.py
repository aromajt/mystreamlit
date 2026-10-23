"""인트로 보조 분석. 기존 자료에서만 수치를 계산합니다."""
import pandas as pd
import plotly.express as px
import streamlit as st


def show_overview(places, stay, spend):
    st.markdown('### 📊 남도 관광 데이터 한눈에 보기')
    if places.empty:
        st.info('관광정보 파일이 없습니다.')
        return
    a, b = st.columns([1.3, 1])
    with a:
        x = places.groupby(['콘텐츠유형명','수집권역']).size().reset_index(name='건수')
        fig = px.bar(x,x='콘텐츠유형명',y='건수',color='수집권역',barmode='group',
                     color_discrete_map={'전남':'#087c91','광주':'#e99b4b'},
                     labels={'콘텐츠유형명':'콘텐츠 유형','수집권역':'지역'})
        fig.update_layout(title='관광 콘텐츠 유형별 분포',height=350,margin=dict(l=10,r=10,t=55,b=10))
        st.plotly_chart(fig,width='stretch')
    with b:
        reg=places['수집권역'].value_counts().rename_axis('지역').reset_index(name='건수')
        fig=px.pie(reg,names='지역',values='건수',hole=.62,color='지역',
                   color_discrete_map={'전남':'#087c91','광주':'#e99b4b'})
        fig.update_layout(title='전남·광주 콘텐츠 비중',height=350,margin=dict(l=10,r=10,t=55,b=10))
        st.plotly_chart(fig,width='stretch')
    st.markdown('### 🌙💳 최신 비교 가능 월의 관광 수요 지표')
    c1,c2=st.columns(2)
    for frame, code, value, title, col in [
        (stay,'2101','tarSjrnDsIxVal','타권역 방문자 비중 지표',c1),
        (spend,'2201','tarExpDsIxVal','외지인 소비액 강도 지표',c2),
    ]:
        with col:
            if frame.empty:
                st.info(f'{title}: 데이터 없음')
                continue
            code_col='tarSjrnDsIxCd' if frame is stay else 'tarExpDsIxCd'
            d=frame.copy()
            d=d[(d['baseYm'].astype(str).between('202509','202606')) &
                (d['signguCd'].astype(str).str.replace(r'\\.0$','',regex=True)=='0') &
                (d[code_col].astype(str)==code)]
            if d.empty:
                st.info(f'{title}: 광역 합계 데이터 없음')
                continue
            d['val']=pd.to_numeric(d[value],errors='coerce')
            d=d.dropna(subset=['val'])
            fig=px.line(d,x='baseYm',y='val',color='수집권역',markers=True,
                        color_discrete_map={'전남':'#087c91','광주':'#e99b4b'},
                        labels={'baseYm':'기준월','val':'강도 지표값','수집권역':'지역'})
            fig.update_layout(title=title,height=320,margin=dict(l=10,r=10,t=55,b=10))
            st.plotly_chart(fig,width='stretch')
    st.caption('관광 콘텐츠는 API 등록 건수, 수요 지표는 가공된 강도 값입니다. 서로 합산하거나 실방문자 수로 해석하지 않습니다.')
