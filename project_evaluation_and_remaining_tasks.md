# FinFlow Sankey 프로젝트 평가 및 잔여작업 브리핑

## 1. 현재 구현 현황

| 영역 | 구현 내용 | 상태 |
|------|-----------|------|
| **핵심 파이프라인** | `FinancialSankey` → `SankeyPipeline` → `validate()` → `render()` 체인 | ✅ |
| **입력 처리** | Polars `DataFrame` / `LazyFrame` 지원, schema validation | ✅ |
| **손익계산서** | Revenue → Cost/Expense/Tax → Net Income Sankey | ✅ |
| **현금흐름표** | Beginning Cash → Flows → Ending Cash bridge | ✅ |
| **색상 팔레트** | 역할별 색상, 4개 내장 theme, YAML/dict 런타임 override | ✅ |
| **선 스타일** | 링크 외곽선 0.5px, 노드 테두리 1.5px 통일 | ✅ |
| **회계 검증** | 기간/통화 일치, 합계 검증, 필수 계정 확인, 중복/null 검사 | ✅ |
| **Plotly 렌더링** | `go.Figure` 반환, hover, 범례 annotation | ✅ |
| **테스트** | pytest 7개 통과, ruff 통과 | ✅ |
| **문서** | README, PRD 개선안 파일 | ✅ |
| **재무상태표** | Reconciliation Sankey | ❌ 미구현 |
| **계정 매핑** | YAML mapping, 사용자 정의 mapping override | ❌ 미구현 |
| **pandas adapter** | optional pandas 입력 지원 | ❌ 미구현 |
| **HTML export helper** | `fig.write_html()` 래퍼 | ❌ 미구현 |
| **CLI** | CSV → HTML 변환 명령어 | ❌ 미구현 |

---

## 2. 다차원 평가 (정반합)

### 2.1 기획/요구사항 충족도 (가중치 20%)

| 평가 항목 | 점수 | 근거 |
|-----------|------|------|
| PRD 핵심 목표 반영 | 8.5/10 | 회계 검증 + Sankey 자동 생성 + Polars-first 구현 완료 |
| MVP 범위 충족 | 7.5/10 | 손익계산서/현금흐름표 완료, 재무상태표는 미구현 |
| 요구사항 반영 (색상/선) | 9.0/10 | 역할별 색상, 일정 선 두께, 깔끔한 레이아웃 구현 |
| 비목표 준수 | 8.5/10 | pandas 중심 처리 배제, Polars-first 유지 |

**정반합**
- ✅ 강점: PRD의 핵심 차별점(검증 가능한 Sankey)이 코드에 반영됨
- ⚠️ 약점: v0.1에 포함될 일부 항목(HTML export helper)이 아직 없음

**부분 점수: 8.4/10 × 0.20 = 1.68**

---

### 2.2 기술 설계/구현 품질 (가중치 25%)

| 평가 항목 | 점수 | 근거 |
|-----------|------|------|
| 아키텍처 분리 | 8.5/10 | schema/validator/normalizer/graph/renderer/template 명확히 분리 |
| Polars-first 설계 | 8.0/10 | LazyFrame 사용, collect 지연 의도 반영 |
| 확장성 | 8.0/10 | template/renderer 교체 가능 구조, palette 시스템 확장 용이 |
| 코드 품질 | 7.5/10 | ruff 통과, 다소 간결하지만 일부 하드코딩 존재 |
| 예외 처리 | 8.0/10 | 구조화된 예외 클래스 정의, 메시지 포함 |

**정반합**
- ✅ 강점: 모듈 분리가 잘 되어 있고, palette/validator 확장이 용이함
- ⚠️ 약점: pipeline 난이에 template별 처리가 일부 하드코딩되어 있음 (income/cash 분기)

**부분 점수: 8.0/10 × 0.25 = 2.00**

---

### 2.3 시각화/UX 디자인 (가중치 20%)

| 평가 항목 | 점수 | 근거 |
|-----------|------|------|
| 색상 정책 | 9.0/10 | 역할별 팔레트, theme 시스템, 런타임 변경 모두 구현 |
| 선 스타일 | 8.5/10 | 면적-선 두께 분리 명확, palette에서 중앙 관리 |
| 레이아웃 | 7.5/10 | 깔끔한 기본 레이아웃, 여백/폰트/범례 적용 |
| hover 정보 | 7.0/10 | 금액/비중/기간/통화 포함, 원천 계정 목록은 아직 미흡 |
| 가독성 | 7.5/10 | 노드/링크 색상 구분 가능, 다만 복잡한 계정 구조에서는 Other 처리 필요 |

**정반합**
- ✅ 강점: 색상 팔레트 커스터마이징이 매우 유연함
- ⚠️ 약점: Plotly Sankey 자체 한계로 노드 배치가 항상 최적은 아님, level 기반 x좌표 미적용

**부분 점수: 7.9/10 × 0.20 = 1.58**

---

### 2.4 테스트/검증 (가중치 15%)

| 평가 항목 | 점수 | 근거 |
|-----------|------|------|
| 테스트 커버리지 | 6.5/10 | 기본 케이스 7개, 핵심 흐름 커버 |
| 검증 로직 | 8.5/10 | 합계 검증, 기간/통화/중복/null 검사 구현 |
| 오류 메시지 | 7.5/10 | 구조화된 예외, 금액/규칙 포함 |
| 엣지 케이스 | 5.5/10 | multi-currency/period, missing account, large data 등 추가 필요 |
| 회귀 방지 | 6.0/10 | golden output test, fixture 기반 테스트 부족 |

**정반합**
- ✅ 강점: 핵심 검증(손익, 현금흐름 합계)이 동작함
- ⚠️ 약점: 테스트가 happy path 위주, 다양한 실패 케이스 fixture가 부족

**부분 점수: 6.8/10 × 0.15 = 1.02**

---

### 2.5 문서화/완성도 (가중치 10%)

| 평가 항목 | 점수 | 근거 |
|-----------|------|------|
| README | 7.5/10 | 설치, quickstart, theme/palette 예시 포함 |
| PRD 개선안 | 9.0/10 | 색상/선/레이아웃 정책 구체화, 팔레트 시스템 설계 |
| 코드 문서화 | 6.5/10 | docstring 일부, 더 상세한 API 문서 필요 |
| 예제 | 7.5/10 | 손익/현금흐름 예제, notebook은 없음 |

**정반합**
- ✅ 강점: PRD 개선안이 구현 방향과 설계 의도를 잘 정리함
- ⚠️ 약점: API reference, notebook 예제, 개발 가이드 부족

**부분 점수: 7.6/10 × 0.10 = 0.76**

---

### 2.6 확장성/유지보수성 (가중치 10%)

| 평가 항목 | 점수 | 근거 |
|-----------|------|------|
| 모듈 결합도 | 8.0/10 | template/validator/renderer가 느슨하게 결합 |
| 팔레트 확장 | 9.0/10 | YAML 추가만으로 새 theme 생성 가능 |
| 템플릿 추가 용이성 | 7.5/10 | base class 상속 구조, but statement_type 분기 추가 필요 |
| 의존성 관리 | 8.0/10 | pyproject.toml, optional extras 정의 |
| 버전 관리 | 6.0/10 | palette version 필드만 존재, 아직 활용 안 함 |

**정반합**
- ✅ 강점: palette/theme 시스템이 확장성이 뛰어남
- ⚠️ 약점: template 추가 시 __init__.py와 validator 수정 필요, 플러그인 구조는 아님

**부분 점수: 7.7/10 × 0.10 = 0.77**

---

## 3. 종합 점수

| 평가 영역 | 가중치 | 부분 점수 | 환산 점수 |
|-----------|--------|-----------|-----------|
| 기획/요구사항 충족도 | 20% | 8.4/10 | 1.68 |
| 기술 설계/구현 품질 | 25% | 8.0/10 | 2.00 |
| 시각화/UX 디자인 | 20% | 7.9/10 | 1.58 |
| 테스트/검증 | 15% | 6.8/10 | 1.02 |
| 문서화/완성도 | 10% | 7.6/10 | 0.76 |
| 확장성/유지보수성 | 10% | 7.7/10 | 0.77 |
| **종합** | **100%** | - | **7.81/10** |

### 등급: B+ (양호, 추가 다듬으면 A급)

- **7.81/10**은 MVP 기준으로 양호한 수준
- 핵심 기능(손익, 현금흐름, 색상 팔레트, 검증)이 모두 동작
- 테스트 커버리지와 문서화를 보강하면 8.5점 이상 도달 가능

---

## 4. 잔여작업 브리핑

### 4.1 v0.1 마무리 (높은 우선순위)

| ID | 작업 | 설명 | 예상 소요 |
|----|------|------|-----------|
| R-01 | HTML export helper | `fig.write_html()` 래퍼 + 경로/파일명 자동 생성 | 1h |
| R-02 | minor grouping 고도화 | `group_minor(min_pct/min_value/top_n)` 버그 수정 및 metadata 보존 | 2h |
| R-03 | hover metadata 강화 | 원천 계정 목록, 묶인 계정 리스트, 검증 상태 상세 표시 | 2h |
| R-04 | 엣지 케이스 테스트 | multi-currency/period, missing account, null value, reconciliation error fixture | 3h |
| R-05 | 노드 x좌표 배치 | template의 level 정보를 Plotly node x좌표에 반영 | 2h |

### 4.2 v0.2 확장 (중간 우선순위)

| ID | 작업 | 설명 | 예상 소요 |
|----|------|------|-----------|
| R-06 | 재무상태표 reconciliation | Assets = Liabilities + Equity 좌우 분할 Sankey | 4h |
| R-07 | YAML account mapping | `default_income_statement.yaml` 등 계정명 → role 매핑 | 3h |
| R-08 | pandas optional adapter | `pip install finflow-sankey[pandas]` + `from_pandas()` | 2h |
| R-09 | dark mode theme | `dark` 내장 palette 추가 | 1h |
| R-10 | palette version 활용 | 버전 호환성 체크, migration 경고 | 1h |

### 4.3 v0.3 이후 (낮은 우선순위)

| ID | 작업 | 설명 | 예상 소요 |
|----|------|------|-----------|
| R-11 | 다기간 비교 Sankey | YoY/QoQ 비교, 변화량 흐름 시각화 | 6h |
| R-12 | XBRL adapter | XBRL concept 기반 계정 매핑 구조 | 8h |
| R-13 | CLI | `finflow-sankey csv input.csv --statement income --output out.html` | 3h |
| R-14 | Dashboard helpers | Streamlit/Dash 예제 컴포넌트 | 4h |
| R-15 | notebook 예제 | `.ipynb` quickstart, validation error 예제 | 2h |

---

## 5. 핵심 개선 방향

1. **테스트 강화**: PRD에 명시된 fixture 데이터 기반 golden output test 추가
2. **문서 보강**: API reference, 개발 가이드, notebook 예제 작성
3. **재무상태표 구현**: v0.2의 핵심 기능, reconciliation view 명확히 구현
4. **계정 매핑**: YAML 기반 mapping으로 기업별 계정명 차이 흡수
5. **노드 배치**: template level 정보를 시각적 x좌표로 변환

---

*본 평가는 MVP 기준으로 작성되었으며, v0.2 기능 구현 후 재평가 시 8.5점 이상 상향 가능.*
