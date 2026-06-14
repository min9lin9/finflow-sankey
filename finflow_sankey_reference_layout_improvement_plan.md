# FinFlow Sankey 레퍼런스 레이아웃 개선 계획

## 1. 배경

`finflow-sankey`의 손익계산서 Sankey 출력은 레퍼런스 이미지처럼 매출, 비용, 이익 흐름을 직관적으로 보여줘야 한다. 현재 개선 작업에서는 상세 매출/비용 계정 노드, 파랑/초록/빨강 역할 색상, 무테두리 기본 스타일, 팔레트 기반 커스터마이징을 추가했다.

추가 검토 중 `Cost of Sales` 노드가 아래쪽에서 잘리는 문제가 발견되었다. 원인은 사용자 데이터가 아니라 라이브러리의 기본 fixed layout과 SVG 캔버스 높이 정책이다. 큰 비용 노드는 값에 비례해 세로 폭이 커지므로, 고정 y 좌표가 낮고 캔버스가 작으면 Plotly Sankey 영역 밖으로 클리핑된다.

따라서 이 문제는 호출부에서 임시로 y 좌표를 바꾸는 방식이 아니라, 라이브러리의 레퍼런스 레이아웃 정책으로 해결해야 한다.

## 2. 목표

| 목표 | 설명 |
|------|------|
| 레퍼런스 이미지 유사성 | 매출은 파랑, 이익은 초록, 비용은 빨강으로 구분하고, 상세 계정이 총계 노드로 흐르게 한다. |
| 클리핑 방지 | 큰 비용/이익 노드가 SVG 영역 밖으로 잘리지 않아야 한다. |
| 영역 겹침 방지 | 비용 flow와 이익 flow가 의도치 않게 겹쳐 회색 혼합 영역을 만들지 않아야 한다. |
| 팔레트 기반 DIY | 색상, 테두리, 선 두께는 별도 팔레트 YAML 또는 런타임 `palette` override로 조정 가능해야 한다. |
| 기존 테마 호환 | `theme="dark"` 등 명시 테마는 기존 동작을 유지해야 한다. |

## 3. 설계 원칙

### 3.1 레이아웃 문제는 레이아웃 정책으로 해결

큰 노드가 잘리는 문제를 해결하기 위해 노드를 임의로 위로 당기면 비용/이익 영역이 겹칠 수 있다. 올바른 방향은 다음과 같다.

1. 비용 branch와 이익 branch의 y 좌표는 서로 분리한다.
2. 큰 비용 노드가 필요한 세로 공간을 확보하도록 reference figure 높이를 늘린다.
3. Plotly fixed layout의 노드 좌표는 안정적으로 유지한다.
4. 출력 품질은 브라우저 렌더링 스크린샷으로 확인한다.

### 3.2 스타일은 팔레트에서 관리

레퍼런스 색상과 테두리 정책은 렌더러에 하드코딩하지 않는다.

| 설정 위치 | 역할 |
|-----------|------|
| `finflow_sankey/palettes/default.yaml` | 기본 reference 색상, 무테두리 기본값 |
| `semantic.node_border_width` | 노드 테두리 on/off 및 두께 |
| `semantic.link_border_width` | 링크 테두리 on/off 및 두께 |
| `semantic.border` | 테두리 색상 |
| `roles.revenue` | 매출 색상 |
| `roles.profit` | 이익 색상 |
| `roles.operating_expenses` | 비용 색상 |

## 4. 구현 계획

### Phase 1. 손익계산서 graph 구조 정리

| 작업 | 파일 | 완료 기준 |
|------|------|-----------|
| 상세 매출 계정 노드 생성 | `finflow_sankey/templates/income_statement_builder.py` | `Product Sales`, `Service Sales`가 `Total Revenue`로 흐른다. |
| 비용 상세 계정 노드 생성 | `finflow_sankey/templates/income_statement_sections.py` | `Payroll`, `Rent`, `Transport`가 `Operating Expenses`에서 분기된다. |
| 기존 API 유지 | `finflow_sankey/templates/income_statement.py` | `FinancialSankey.income_statement(...).render()` 호출 방식이 그대로 동작한다. |

### Phase 2. 레퍼런스 스타일 분리

| 작업 | 파일 | 완료 기준 |
|------|------|-----------|
| 레퍼런스 스타일 helper 추가 | `finflow_sankey/renderers/income_reference_style.py` | income reference graph만 전용 legend/layout을 적용한다. |
| Plotly renderer 연동 | `finflow_sankey/renderers/plotly_renderer.py` | reference graph는 fixed layout, 일반 graph는 기존 snap layout 유지. |
| 기본 무테두리 적용 | `finflow_sankey/palettes/default.yaml` | `node_border_width: 0`으로 검은 외곽선이 보이지 않는다. |

### Phase 3. 클리핑/겹침 해결

| 작업 | 파일 | 완료 기준 |
|------|------|-----------|
| 비용/이익 branch 분리 | `income_statement_builder.py` | `Gross Profit`은 위쪽, `Cost of Sales`는 아래쪽 branch에 유지된다. |
| SVG 영역 확대 | `income_reference_style.py` | reference figure height를 충분히 크게 설정한다. |
| 회귀 테스트 추가 | `tests/test_income_reference_style.py` | 비용 branch를 위로 당겨 해결하는 회귀가 다시 들어오지 않는다. |
| 브라우저 렌더 확인 | `finflow_reference_sample.png` | 하단 edge에 Sankey 색상 픽셀이 닿지 않는다. |

## 5. 수용 기준

| ID | 기준 | 검증 방법 |
|----|------|-----------|
| A-01 | `Cost of Sales` 아래쪽이 잘리지 않는다. | 브라우저 스크린샷 및 하단 edge 픽셀 체크 |
| A-02 | 비용 flow와 이익 flow가 의도치 않게 겹치지 않는다. | 스크린샷 육안 확인 |
| A-03 | 기본 출력에는 검은 테두리가 없다. | `sankey.node.line.width == 0` |
| A-04 | 사용자가 테두리를 다시 켤 수 있다. | `palette={"border": "#111827", "node_border_width": 2.5}` 테스트 |
| A-05 | 기본 레퍼런스 색상은 팔레트 파일에서 조정 가능하다. | `default.yaml` roles 값 변경 또는 palette override |
| A-06 | 기존 dark theme 동작은 유지된다. | 기존 `test_dark_theme` 통과 |
| A-07 | 전체 테스트가 통과한다. | `python -m pytest -q` |
| A-08 | 변경 파일 lint가 통과한다. | `ruff check ...` |

## 6. 테스트 계획

### 6.1 단위/구조 테스트

`tests/test_income_reference_style.py`에서 다음을 검증한다.

| 검증 항목 | 기대값 |
|-----------|--------|
| 상세 매출 노드 | `Product Sales`, `Service Sales` 존재 |
| 총매출 노드 | `Total Revenue` 존재 |
| 상세 비용 노드 | `Payroll`, `Rent`, `Transport` 존재 |
| x 배치 | 매출 상세 `0.0`, 총매출 `0.25`, 순이익 `1.0` |
| y 배치 | `Gross Profit`은 위쪽 branch, `Cost of Sales`는 아래쪽 branch |
| 색상 | 매출 `#2F80ED`, 이익 `#12A878`, 비용 `#C91F3A` |
| 기본 테두리 | `node.line.width == 0` |
| DIY 테두리 | palette override 값이 node line에 반영 |
| 캔버스 높이 | reference layout height가 clipping 방지 크기 |

### 6.2 통합 테스트

```bash
python -m pytest -q
ruff check finflow_sankey/renderers/plotly_renderer.py \
  finflow_sankey/renderers/income_reference_style.py \
  finflow_sankey/templates/income_statement_builder.py \
  tests/test_income_reference_style.py
```

### 6.3 수동 QA

1. `FinancialSankey.income_statement(...).export_html(...)`로 샘플 HTML을 생성한다.
2. Chromium으로 HTML을 렌더링하고 스크린샷을 저장한다.
3. 다음을 확인한다.
   - 비용/이익 영역이 구분된다.
   - `Cost of Sales` 노드와 flow가 아래쪽에서 잘리지 않는다.
   - 검은 외곽선이 보이지 않는다.
   - legend, title, 주요 node label이 보인다.

## 7. 산출물

| 산출물 | 설명 |
|--------|------|
| `finflow_sankey/templates/income_statement_builder.py` | 손익계산서 reference graph의 주요 node/link 배치 |
| `finflow_sankey/templates/income_statement_sections.py` | 영업비용, 영업이익, 순이익 구간 분리 |
| `finflow_sankey/renderers/income_reference_style.py` | reference layout, legend, role color helper |
| `finflow_sankey/renderers/plotly_renderer.py` | reference style 분기 및 palette-driven border 적용 |
| `finflow_sankey/palettes/default.yaml` | 기본 reference 색상과 무테두리 설정 |
| `tests/test_income_reference_style.py` | 레이아웃/색상/DIY 테두리 회귀 테스트 |
| `finflow_reference_sample.html` | 브라우저 확인용 샘플 HTML |
| `finflow_reference_sample.png` | 시각 QA용 스크린샷 |

## 8. 리스크와 후속 작업

| 리스크 | 설명 | 대응 |
|--------|------|------|
| Plotly Sankey fixed layout 한계 | 값 분포가 극단적이면 다른 노드에서도 clipping 가능 | 데이터 규모별 height 계산 정책 추가 |
| 긴 계정명 label | 오른쪽 상세 비용 label이 잘리거나 겹칠 수 있음 | label wrapping 또는 margin 자동 확장 |
| 많은 상세 계정 | 세부 노드가 많으면 vertical spacing 부족 | `group_minor()`와 reference layout 연동 |
| 테마별 의도 충돌 | dark/minimal/colorblind theme에서 reference layout 적용 범위가 달라질 수 있음 | theme별 reference policy 명시 |

## 9. 다음 개선 제안

1. 데이터 기반 자동 height 계산
   - 총 node 수, 최대 node 값 비중, 상세 계정 수를 고려해 reference figure height를 자동 산정한다.

2. 자동 margin 계산
   - 오른쪽 상세 label 길이에 따라 `margin.r`을 늘린다.

3. reference layout 옵션화
   - `render(layout="reference")` 또는 `theme="reference"` 형태로 명시 선택 가능하게 한다.

4. visual regression artifact 관리
   - 샘플 HTML/PNG를 테스트 fixture 또는 docs asset으로 관리한다.

## 10. 현재 상태

현재 구현 방향은 이 문서의 Phase 1-3에 맞춰 진행 중이며, 핵심 검증은 다음 상태를 목표로 한다.

```text
python -m pytest -q
32 passed

ruff check ...
All checks passed
```
