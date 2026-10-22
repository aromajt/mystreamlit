"""남도ON | 전남·광주 관광 데이터 대시보드. 실행: streamlit run app.py"""
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="남도ON | 전남·광주 관광 데이터", page_icon="🌿", layout="wide", initial_sidebar_state="expanded")
BASE = Path(__file__).resolve().parent
DATA = BASE / "data"

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"],.stApp {font-family:'Noto Sans KR',sans-serif;}
.stApp {background:#f5f8fc;color:#15263d}
[data-testid="stSidebar"] {background:#0e2e47;}
[data-testid="stSidebar"] * {color:#f2f7ff !important}
.block-container{padding-top:1.6rem;max-width:1450px}
.hero{padding:27px 32px;border-radius:19px;background:linear-gradient(120deg,#083b56,#0a6e84);color:white;margin-bottom:20px;box-shadow:0 12px 26px #114c6720}
.hero .eyebrow{font-size:12px;letter-spacing:3px;color:#b3edf0;font-weight:800}
.hero h1{font-size:35px;line-height:1.3;color:white;margin:8px 0}
.hero p{color:#e0f4f6;margin:0}
.section-title{font-size:22px;font-weight:800;color:#16334a;margin:14px 0 3px}
.section-desc{font-size:13px;color:#66798d;margin-bottom:14px}
[data-testid="stMetric"]{background:#fff;border:1px solid #e0eaf1;border-radius:14px;padding:16px 20px;box-shadow:0 5px 18px #223c5008}
[data-testid="stMetricLabel"]{font-weight:600;color:#66798d}
[data-testid="stMetricValue"]{font-weight:800;color:#0f4763}
[data-testid="stPlotlyChart"], [data-testid="stDataFrame"] {background:white;border-radius:14px}
div.stButton > button{border-radius:10px}
.small-note{background:#e9f2f7;border-left:4px solid #0c7c94;padding:11px 15px;border-radius:7px;color:#34526a;font-size:13px;margin:8px 0 15px}
</style>""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_csv(name):
    path = DATA / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, dtype={"signguCd":"string", "contentid":"string"}, encoding="utf-8-sig")

places = load_csv("tourism_places.csv")
stay = load_csv("tourism_stay_demand.csv")
spend = load_csv("tourism_spend_demand.csv")
visitors = load_csv("tourism_visitors.csv")

st.sidebar.markdown("## 🌿 남도ON")
st.sidebar.caption("전남·광주 공공 관광데이터")
page = st.sidebar.radio("분석 메뉴", ["📊 관광 종합현황", "🗺️ 관광지 검색·지도", "🌙 체류 강도 분석", "💳 소비 강도 분석", "👥 방문자 분석", "📚 데이터 출처"], label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.info("수집 기준: 공공데이터포털 관광 API\n\n수요 분석: 2025.09 ~ 2026.06")

st.markdown('<div class="hero"><div class="eyebrow">NAMDO ON · TOURISM INTELLIGENCE</div><h1>전남·광주 관광 데이터 대시보드</h1><p>공공데이터로 살펴보는 관광 콘텐츠, 지역별 체류 특성, 관광 소비 강도</p></div>', unsafe_allow_html=True)

if places.empty and stay.empty and spend.empty:
    st.error("관광 데이터 CSV를 찾지 못했습니다. GitHub 저장소의 app.py와 같은 위치에 data/ 폴더 및 CSV 3개를 업로드해 주세요.")
    st.code("data/tourism_places.csv\ndata/tourism_stay_demand.csv\ndata/tourism_spend_demand.csv")
    st.stop()

if not places.empty:
    places["지역"] = places["수집권역"].fillna("미분류")
    places["유형"] = places["콘텐츠유형명"].fillna("기타")
    places["경도"] = pd.to_numeric(places.get("mapx"), errors="coerce")
    places["위도"] = pd.to_numeric(places.get("mapy"), errors="coerce")
    places["사진"] = places.get("firstimage", pd.Series(index=places.index, dtype="object")).fillna("")
    # 한국의 유효 경도/위도 범위로 범위를 한정하고 0 좌표를 제거합니다.
    places["지도표시"] = places["경도"].between(124, 132) & places["위도"].between(33, 39)

for table, code, value in ((stay, "tarSjrnDsIxCd", "tarSjrnDsIxVal"),(spend, "tarExpDsIxCd", "tarExpDsIxVal")):
    if not table.empty:
        table["월"] = table["baseYm"].astype(str)
        table["지역"] = table["수집권역"].astype(str)
        table["시군구코드"] = table["signguCd"].astype(str).str.replace(r"\.0$", "", regex=True)
        table["값"] = pd.to_numeric(table[value], errors="coerce")
        table["지표코드"] = table[code].astype(str)

# 2026.07~08의 광역 단독 조회 데이터는 지역별 비교 추이에서 제외
PERIOD_START, PERIOD_END = "202509", "202606"
PALETTE = ["#087c91", "#e99b4b", "#425cbb", "#60a686", "#b277aa"]

def plot_style(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10,r=10,t=25,b=12), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Noto Sans KR"), legend_title_text="", hovermode="x unified")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#edf1f5", zeroline=False)
    return fig

def demand_ui(df, kind):
    if df.empty:
        st.warning(f"{kind} 파일이 없습니다. data 폴더를 확인하세요.")
        return
    ref = df[df["월"].between(PERIOD_START, PERIOD_END)].copy()
    if ref.empty:
        st.warning("선택 분석기간의 자료가 없습니다.")
        return
    code_col = "tarSjrnDsIxNm" if kind == "체류 강도" else "tarExpDsIxNm"
    st.markdown(f'<div class="section-title">{kind} 분석</div><div class="section-desc">2025년 9월 ~ 2026년 6월 · 전남/광주 광역 합계 및 시군구별 강도 지표</div>', unsafe_allow_html=True)
    opts = ref[["지표코드",code_col]].drop_duplicates().sort_values("지표코드")
    choices = {str(row["지표코드"]):row[code_col] for _,row in opts.iterrows()}
    c1,c2,c3 = st.columns([2,1,1])
    selected = c1.selectbox("분석 지표", list(choices), format_func=lambda x: f"{x} · {choices[x]}")
    region = c2.selectbox("지역", ["전체", "전남", "광주"])
    view = c3.selectbox("지역 단위", ["광역 합계", "시군구"])
    filt = ref[ref["지표코드"] == selected]
    if region != "전체": filt = filt[filt["지역"]==region]
    if view == "광역 합계":
        filt = filt[filt["시군구코드"]=="0"].copy()
        filt["비교지역"] = filt["지역"]
    else:
        filt = filt[filt["시군구코드"]!="0"].copy()
        filt["비교지역"] = filt["지역"] + " · " + filt["signguNm"].astype(str)
    st.markdown('<div class="small-note">수치는 한국관광공사에서 산출한 관광 수요 <b>강도 지표값</b>입니다. 실제 관광객 수나 소비액 원자료로 합산하지 않습니다. 광역 합계와 시군구를 동시에 합산하지 않습니다.</div>', unsafe_allow_html=True)
    if filt.empty:
        st.warning("해당 조건의 데이터가 없습니다.")
        return
    latest = filt["월"].max()
    latest_data = filt[filt["월"] == latest]
    a,b,c = st.columns(3)
    a.metric("최근 분석 월", latest[:4]+"."+latest[4:])
    b.metric("해당 월 비교 지역", f"{len(latest_data):,}개")
    c.metric("분석 레코드", f"{len(filt):,}건")
    if view == "시군구" and region == "전체":
        st.caption("시군구 수가 많아 상위 지역 10개만 추이 차트에 표시합니다. 상세 값은 하단 표에서 확인하세요.")
        top = latest_data.nlargest(10,"값")["비교지역"].tolist()
        chart_df = filt[filt["비교지역"].isin(top)]
    else:
        chart_df=filt
    fig=px.line(chart_df.sort_values("월"),x="월",y="값",color="비교지역",markers=True,color_discrete_sequence=PALETTE, labels={"월":"기준 월","값":"강도 지표값","비교지역":"지역"})
    st.plotly_chart(plot_style(fig,390),width="stretch")
    st.markdown("#### 최근 월 지역별 비교")
    rank=latest_data.sort_values("값",ascending=False)
    fig2=px.bar(rank.head(20),x="값",y="비교지역",orientation="h",color="지역",color_discrete_map={"전남":"#087c91","광주":"#e99b4b"},labels={"값":"강도 지표값","비교지역":"지역"})
    fig2.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(plot_style(fig2,max(320,22*min(20,len(rank))+90)),width="stretch")
    st.dataframe(filt[["월","지역","signguNm",code_col,"값"]].sort_values(["월","지역"],ascending=[False,True]),width="stretch",hide_index=True)

if page == "📊 관광 종합현황":
    st.markdown('<div class="section-title">관광 종합현황</div><div class="section-desc">관광정보 API에 등록된 콘텐츠 현황입니다. 실제 관광자원 총량을 의미하지는 않습니다.</div>',unsafe_allow_html=True)
    if places.empty: st.warning("관광정보 CSV가 없습니다.")
    else:
        k1,k2,k3,k4=st.columns(4)
        k1.metric("관광 콘텐츠",f"{len(places):,}건")
        k2.metric("전남 콘텐츠",f"{(places['지역']=='전남').sum():,}건")
        k3.metric("광주 콘텐츠",f"{(places['지역']=='광주').sum():,}건")
        k4.metric("이미지 보유",f"{places['사진'].astype(str).str.strip().ne('').mean()*100:.1f}%")
        a,b=st.columns([1.3,1])
        with a:
            ct=places.groupby(["유형","지역"]).size().reset_index(name="건수")
            fig=px.bar(ct,x="유형",y="건수",color="지역",barmode="group",color_discrete_map={"전남":"#087c91","광주":"#e99b4b"},labels={"유형":"콘텐츠 유형"})
            st.plotly_chart(plot_style(fig),width="stretch")
        with b:
            ct2=places.groupby("유형").size().reset_index(name="건수")
            fig=px.pie(ct2,names="유형",values="건수",hole=.56,color_discrete_sequence=PALETTE)
            st.plotly_chart(plot_style(fig),width="stretch")
        st.markdown("#### 지역별 관광 콘텐츠")
        st.dataframe(pd.crosstab(places["유형"],places["지역"],margins=True,margins_name="합계"),width="stretch")
        st.caption("출처: 한국관광공사 국문 관광정보 서비스 · 수집 데이터 기준")

elif page == "🗺️ 관광지 검색·지도":
    st.markdown('<div class="section-title">관광지 검색·지도</div><div class="section-desc">관광지·음식점·숙박시설 등을 검색하고 지도에서 위치를 확인하세요.</div>',unsafe_allow_html=True)
    if places.empty: st.warning("관광정보 CSV가 없습니다.")
    else:
        c1,c2,c3=st.columns([1,1,2])
        region=c1.selectbox("지역",["전체"]+sorted(places["지역"].dropna().unique().tolist()))
        types=c2.selectbox("콘텐츠 유형",["전체"]+sorted(places["유형"].dropna().unique().tolist()))
        word=c3.text_input("키워드 검색",placeholder="예: 여수, 순천, 카페, 해수욕장")
        df=places.copy()
        if region!="전체":df=df[df["지역"]==region]
        if types!="전체":df=df[df["유형"]==types]
        if word:df=df[df["title"].fillna("").str.contains(word,case=False,regex=False) | df["addr1"].fillna("").str.contains(word,case=False,regex=False)]
        st.caption(f"검색 결과 {len(df):,}건 · 위치 표시 가능 {int(df['지도표시'].sum()):,}건")
        loc=df[df["지도표시"]]
        if not loc.empty:
            st.map(loc.rename(columns={"위도":"lat","경도":"lon"})[["lat","lon"]].head(900),zoom=7 if region=="전체" else 9)
        else:st.info("표시 가능한 위치 좌표가 없습니다.")
        st.download_button("검색 결과 CSV 내려받기", data=df.to_csv(index=False).encode("utf-8-sig"), file_name="namdo_places_filtered.csv", mime="text/csv")
        st.markdown("#### 관광 콘텐츠")
        max_count=min(len(df),36)
        for start in range(0,max_count,3):
            cols=st.columns(3)
            for i,(_,item) in enumerate(df.iloc[start:start+3].iterrows()):
                with cols[i]:
                    with st.container(border=True):
                        if str(item["사진"]).startswith("http"):
                            st.image(item["사진"],width="stretch")
                        else:st.markdown("📷 *등록된 이미지 없음*")
                        st.markdown("**"+str(item["title"])+"**")
                        st.caption(f"{item['지역']} · {item['유형']}")
                        st.caption(str(item.get("addr1","") or "주소 없음"))
                        with st.expander("상세정보 및 위치"):
                            st.write("콘텐츠 ID:", item.get("contentid", "-"))
                            st.write("주소:", item.get("addr1", "-"))
                            if pd.notna(item.get("addr2")) and str(item.get("addr2")).strip():
                                st.write("상세주소:", item.get("addr2"))
                            if bool(item["지도표시"]):
                                lat, lon = float(item["위도"]), float(item["경도"])
                                st.link_button("구글 지도에서 위치 확인", f"https://www.google.com/maps/search/?api=1&query={lat},{lon}", width="stretch")
                            else:
                                st.caption("유효하지 않은 좌표로 지도 링크를 제공하지 않습니다.")
                            st.caption("운영시간과 요금은 현재 수집 CSV에 포함되어 있지 않습니다.")
        if len(df)>max_count:st.caption(f"화면 성능을 위해 검색 결과 중 상위 {max_count}개 카드만 표시합니다. 검색어로 범위를 좁혀 주세요.")

elif page == "🌙 체류 강도 분석": demand_ui(stay,"체류 강도")
elif page == "💳 소비 강도 분석": demand_ui(spend,"소비 강도")
elif page == "👥 방문자 분석":
    st.markdown('<div class="section-title">지역별 방문자 분석</div>', unsafe_allow_html=True)
    if visitors.empty:
        st.info("방문자 수 CSV는 아직 수집 전입니다. 다른 분석 메뉴는 정상 이용할 수 있습니다.")
        st.write("예정 데이터 파일: `data/tourism_visitors.csv`")
        st.markdown("[한국관광공사 지역별 방문자 수 API](https://www.data.go.kr/data/15101972/openapi.do)")
    else:
        st.success(f"방문자 자료 {len(visitors):,}행을 불러왔습니다.")
        st.dataframe(visitors.head(1000), width="stretch", hide_index=True)
        st.caption("원자료의 집계 단위와 필드명을 검토한 다음 월별 차트를 연결할 예정입니다.")
else:
    st.markdown('<div class="section-title">데이터 출처 및 이용 안내</div>',unsafe_allow_html=True)
    st.markdown("""- **관광 콘텐츠**: [한국관광공사 국문 관광정보 서비스](https://www.data.go.kr/data/15101578/openapi.do) · `areaBasedList2`
- **체류·소비 강도**: [한국관광공사 지역별 관광 수요 강도](https://www.data.go.kr/data/15151868/openapi.do) · `areaTarSjrnDsList`, `areaTarExpDsList`
- **분석 기간**: 수요 시군구 자료 2025년 9월~2026년 6월. 2026년 7월 자료 미수집/미제공, 8월은 일부 광역 단위만 있어 시계열에서 제외
- **지표 주의사항**: 공공데이터 API의 가공된 강도 지표이며 방문자 수·매출 합계가 아닙니다. 지표별 산식·단위는 원 API 매뉴얼을 참조하세요.
- **관광 콘텐츠**: 특정 API 조회 기준의 데이터이며 지역 내 모든 관광시설을 포괄하지 않을 수 있습니다.
- **방문자 분석**: [한국관광공사 지역별 방문자 수](https://www.data.go.kr/data/15101972/openapi.do) · CSV 수집 이후 연계
""")
    st.markdown("#### 실제 앱에서 불러온 파일")
    for name,df in (("tourism_places.csv",places),("tourism_stay_demand.csv",stay),("tourism_spend_demand.csv",spend)):
        st.write(f"`data/{name}` · **{len(df):,}행**" if not df.empty else f"`data/{name}` · 파일 없음")

st.divider()
st.caption("NAMDO ON · 전남·광주 관광 공공데이터 활용 미니프로젝트 · API 원천자료를 그대로 존중하며 분석")
