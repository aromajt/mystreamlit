# 🌿 남도ON | 전남·광주 관광 데이터 대시보드

**공공데이터로 살펴보는 전남·광주의 관광 콘텐츠, 체류 특성, 소비 강도 및 방문자 추이**

[🌐 Streamlit 웹사이트](https://myapp-tcajypvztxaej7zzssuqut.streamlit.app/) · [💻 GitHub 저장소](https://github.com/aromajt/mystreamlit)

## 1. 프로젝트 소개

- **프로젝트 유형:** 공공데이터 활용 Streamlit 미니프로젝트
- **대상 지역:** 전라남도 및 광주광역시
- **목표:** 관광 콘텐츠 위치·유형·이미지를 탐색하고 관광 수요 및 방문자 추이를 대시보드로 비교 분석
- **활용 기술:** Python, Streamlit, Pandas, Plotly, Folium, GitHub, Streamlit Community Cloud
- **특징:** 수집한 공공데이터 CSV를 기반으로 표시하며, 실제 API 응답에 없는 수치를 임의 생성하지 않습니다.

## 2. 핵심 데이터 현황

| 데이터 | 저장 파일 | 확보 레코드 | 분석 기준 |
|---|---|---:|---|
| 관광 콘텐츠 | `data/tourism_places.csv` | 1,223행 | API 수집 당시 등록된 콘텐츠 |
| 관광 체류 강도 | `data/tourism_stay_demand.csv` | 1,460행 | 2025.09~2026.06 시군구·광역 비교 가능, 2026.08 광역 10행 별도 |
| 관광 소비 강도 | `data/tourism_spend_demand.csv` | 870행 | 2025.09~2026.06 |
| 지역별 방문자 추정치 | `data/tourism_visitors.csv` | 26,361행 | 2025.09.01~2026.06.30 (303일) |

**주의:** 위 건수는 데이터 레코드 수입니다. 관광 콘텐츠의 전체 개수나 관광객 수를 의미하지 않습니다.

## 3. 주요 화면 구성

| 메뉴 | 주요 기능 |
|---|---|
| 🏠 남도ON 소개 | 프로젝트 안내, 핵심 통계, 관광 유형·체류·소비·방문자 추이 미리보기 및 메뉴 바로가기 |
| 📊 관광 종합현황 | 전남·광주 관광 콘텐츠 유형별 비교, 통계 차트 |
| 🗺️ 관광지 검색·지도 | 지역·유형·키워드 검색, Folium 마커 클러스터, 툴팁·팝업, 관광 이미지 카드 |
| 🌙 체류 강도 분석 | 5종 관광 체류 관련 강도 지표의 월별·지역별 비교 |
| 💳 소비 강도 분석 | 3종 관광 소비 관련 강도 지표의 월별·지역별 비교 |
| 👥 방문자 분석 | 이동통신 기반 추정 방문자 수의 월별·유형별·지역별 비교 |
| 📚 데이터 출처 | API 출처, 집계 기간, 자료 이용 시 유의사항 |

## 4. 데이터 출처

1. [한국관광공사 국문 관광정보 서비스](https://www.data.go.kr/data/15101578/openapi.do): 관광 콘텐츠 목록 (`areaBasedList2`)
2. [한국관광공사 지역별 관광 수요 강도](https://www.data.go.kr/data/15151868/openapi.do): 체류·소비 관련 강도 지표 (`areaTarSjrnDsList`, `areaTarExpDsList`)
3. [한국관광공사 빅데이터 지역별 방문자 수](https://www.data.go.kr/data/15101972/openapi.do): 광역·시군구별 일별 추정 방문자 수 (`metcoRegnVisitrDDList`, `locgoRegnVisitrDDList`)

**원천 제공:** 공공데이터포털 / 한국관광공사. 이 저장소는 수집 자료를 활용한 학습용 분석 프로젝트이며, 원천기관의 공식 통계 대시보드는 아닙니다.

## 5. 설치 및 로컬 실행

Python과 Git이 설치된 환경에서 저장소를 내려받아 실행합니다.

```bash
git clone https://github.com/aromajt/mystreamlit.git
cd mystreamlit
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Windows에서 Python 3.12 설치 경로가 `C:\Python312\python.exe`라면 CMD에서 다음처럼 실행할 수 있습니다.

```cmd
C:\Python312\python.exe -m pip install -r requirements.txt
C:\Python312\python.exe -m streamlit run app.py
```

기본 로컬 주소는 `http://localhost:8501`입니다. Streamlit Community Cloud 배포는 저장소 `main` 브랜치의 `app.py`를 사용합니다.

### 프로젝트 주요 파일

```text
mystreamlit/
├── app.py
├── namdo_intro.py
├── namdo_overview.py
├── namdo_visitors.py
├── requirements.txt
├── README.md
└── data/
    ├── tourism_places.csv
    ├── tourism_stay_demand.csv
    ├── tourism_spend_demand.csv
    └── tourism_visitors.csv
```

*참고:* 원천 데이터 수집용 개인 API 인증키는 GitHub에 커밋하지 않습니다. 배포된 앱은 저장된 CSV를 읽는 방식으로 동작합니다. 지도 타일의 추가 언어 설정은 별도 외부 서비스 설정이 필요할 수 있습니다.

## 6. 분석 시 주의사항

- **관광 콘텐츠:** API 등록 콘텐츠 건수이며 전남·광주의 모든 관광시설을 빠짐없이 조사한 전체 수가 아닙니다.
- **체류·소비 강도:** 원천 API가 계산한 강도 지표값입니다. 실제 관광객 수·소비금액과 단위가 다르므로 직접 합산하지 않습니다.
- **방문자 분석:** 이동통신 기반 *일별 방문자 추정값*의 월별 합계입니다. 동일인이 여러 날 집계될 수 있어 월간 고유 방문자 수가 아닙니다.
- **지역별 합계:** 광역 값과 그 안의 시군구 값을 중복 합산하지 않습니다.
- **분석 기간:** 체류·소비 강도의 주요 비교기간은 2025.09~2026.06입니다. 체류 2026.07 자료 공백, 2026.08 광역 일부 자료를 본 비교에서 제외합니다.
- **위치:** 관광 콘텐츠 1,223건 중 좌표 이상·누락 5건은 지도 마커에서 제외합니다.

## 7. 데이터 검증 결과

- 관광 콘텐츠 ID 중복: **0건**
- 체류 강도 주요 분석기간 완전성: **1,450 / 1,450행**
- 소비 강도 주요 분석기간 완전성: **870 / 870행**
- 방문자 자료: **303일, 결측 0건, 음수 0건, 날짜×단위×지역×유형 중복 0건**
- 지도 좌표 확인 필요: **5건** (해당 위치 마커 제외)

검증 결과는 데이터가 수집·저장된 시점의 검사 결과입니다. 새 데이터를 업데이트할 경우 재검증해야 합니다.

## 8. 제출 링크

- **실행 코드(GitHub):** https://github.com/aromajt/mystreamlit
- **웹 대시보드(Streamlit):** https://myapp-tcajypvztxaej7zzssuqut.streamlit.app/
- **데이터 출처:** 위 4절의 공공데이터포털 API 페이지

---

남도ON은 관광 데이터를 학습·분석·시각화하기 위해 제작한 미니프로젝트입니다.
