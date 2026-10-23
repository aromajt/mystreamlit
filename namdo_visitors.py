"""남도ON - 한국관광공사 일별 방문자 추정치 분석. 외부 API 키 불필요."""
import pandas as pd
import plotly.express as px
import streamlit as st

_COLORS = {"전남": "#087c91", "광주": "#e99b4b"}


def _prepare(df):
    x = df.copy()
    x["baseYmd"] = x["baseYmd"].astype(str).str.replace(r"\.0$", "", regex=True)
    x["날짜"] = pd.to_datetime(x["baseYmd"], format="%Y%m%d", errors="coerce")
    x["월"] = x["날짜"].dt.strftime("%Y-%m")
    x["추정방문"] = pd.to_numeric(x["touNum"], errors="coerce")
    x["방문자구분"] = x["touDivNm"].astype(str).str.replace(r"\([abc]\)$", "", regex=True)
    x["시군구"] = x["signguNm"].fillna("").astype(str)
    x["지역명"] = x["지역"].astype(str) + " · " + x["시군구"]
    return x.dropna(subset=["날짜", "추정방문"])


def show_visitor_analysis(visitors):
    st.markdown("### 👥 지역별 방문자 분석")
    st.caption("자료: 한국관광공사 관광빅데이터 API v4.1 | 일별 이동통신 기반 방문자 추정치")
    if visitors.empty:
        st.info("data/tourism_visitors.csv 파일을 추가하면 방문자 분석 차트가 표시됩니다.")
        return
    missing = set(["구분", "지역", "baseYmd", "touNum", "touDivNm", "signguNm"]) - set(visitors.columns)
    if missing:
        st.error("방문자 데이터에 필요한 컬럼이 없습니다: " + ", ".join(sorted(missing)))
        return
    x = _prepare(visitors)
    if x.empty:
        st.warning("분석할 수 있는 방문자 수치가 없습니다.")
        return
    c1,c2,c3 = st.columns(3)
    level = c1.selectbox("집계 단위", ["광역", "시군구"], key="v_level")
    region = c2.selectbox("지역", ["전체", "전남", "광주"], key="v_region")
    types = sorted(x["방문자구분"].unique())
    selected = c3.multiselect("방문자 유형", types, default=types, key="v_types")
    filt = x[(x["구분"] == level) & x["방문자구분"].isin(selected)].copy()
    if region != "전체": filt = filt[filt["지역"] == region]
    if level == "시군구":
        places = sorted(filt["지역명"].unique())
        chosen = st.multiselect("시군구 선택 (미선택 시 전체)", places, key="v_places")
        if chosen: filt = filt[filt["지역명"].isin(chosen)]
    if filt.empty:
        st.info("선택 조건에 해당하는 자료가 없습니다.")
        return
    summary = filt.groupby(["월", "지역"], as_index=False)["추정방문"].sum()
    a,b,c = st.columns(3)
    a.metric("자료 시작", filt["날짜"].min().strftime("%Y.%m.%d"))
    b.metric("자료 종료", filt["날짜"].max().strftime("%Y.%m.%d"))
    c.metric("분석 일수", f"{filt['날짜'].nunique():,}일")
    st.info("아래 월간 수치는 **일별 추정 방문자 수를 더한 값**으로, 월간 고유 방문자 수가 아닙니다. 광역과 시군구 자료는 서로 합산하지 않습니다.")
    st.markdown("#### 월별 방문 추이")
    fig = px.line(summary, x="월", y="추정방문", color="지역", markers=True, color_discrete_map=_COLORS,
                  labels={"추정방문": "일별 추정 방문자 수 합계", "월": "기준월"})
    fig.update_layout(height=370, margin=dict(l=10,r=10,t=20,b=10), legend_title_text="")
    st.plotly_chart(fig, width="stretch")
    a,b = st.columns(2)
    with a:
        st.markdown("#### 방문자 유형별 구성")
        t = filt.groupby("방문자구분", as_index=False)["추정방문"].sum()
        fig2 = px.pie(t, names="방문자구분", values="추정방문", hole=.48)
        fig2.update_layout(height=350, margin=dict(l=5,r=5,t=10,b=10))
        st.plotly_chart(fig2,width="stretch")
    with b:
        st.markdown("#### 최근 월 지역별 비교")
        m = filt["월"].max()
        y = filt[filt["월"] == m].groupby("지역명" if level == "시군구" else "지역", as_index=False)["추정방문"].sum()
        col = "지역명" if level == "시군구" else "지역"
        y = y.sort_values("추정방문", ascending=False).head(12)
        fig3 = px.bar(y, x="추정방문", y=col, orientation="h", labels={"추정방문":"일별 추정 방문자 수 합계"})
        fig3.update_layout(height=350, margin=dict(l=5,r=5,t=10,b=10), yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig3,width="stretch")
    st.markdown("#### 월별 집계 데이터")
    st.dataframe(summary, width="stretch", hide_index=True)
    st.download_button("월별 집계 CSV 다운로드", summary.to_csv(index=False).encode("utf-8-sig"),
                       file_name="namdo_visitors_monthly.csv", mime="text/csv")


def show_visitor_intro(visitors):
    if visitors.empty or not {"구분", "지역", "baseYmd", "touNum", "touDivNm", "signguNm"}.issubset(visitors.columns):
        return
    df = _prepare(visitors)
    df = df[df["구분"] == "광역"]
    if df.empty: return
    st.markdown("### 👥 월별 추정 방문 규모")
    m = df.groupby(["월", "지역"], as_index=False)["추정방문"].sum()
    fig = px.line(m, x="월", y="추정방문", color="지역", markers=True, color_discrete_map=_COLORS,
                  labels={"추정방문":"일별 추정 방문자 수 합계", "월":"기준월"})
    fig.update_layout(height=310,margin=dict(l=10,r=10,t=20,b=10),legend_title_text="")
    st.plotly_chart(fig,width="stretch")
    st.caption("이동통신 기반 일별 추정 방문자 수를 월별 합산한 참고 지표이며 월간 고유 방문자 수가 아닙니다.")
