# FinFlow Sankey 레퍼런스 레이아웃 개선 계획 검토

> 원본: `finflow_sankey_reference_layout_improvement_plan.md`
> 현재 작업 브랜치/트리 기준: `v0.1.12` 이후, reference layout 구현이 진행 중

## 1. 현재 구현 평가

현재 working tree에는 이미 reference layout을 구현한 파일들이 있다.

| 파일 | 상태 | 평가 |
|------|------|------|
| `finflow_sankey/templates/income_statement_builder.py` | untracked | 상세 매출/비용 노드 생성. 책임 분리는 좋으나 기존 `income_statement.py`를 대체하면 유지보수성이 떨어진다. |
| `finflow_sankey/templates/income_statement_sections.py` | untracked | operating/final 노드 분리. `income_statement_builder.py`와 강하게 결합되어 있다. |
| `finflow_sankey/templates/income_statement_model.py` | untracked | dataclass + helper. 작은 유틸을 위해 파일 하나가 추가된 느낌. |
| `finflow_sankey/renderers/income_reference_style.py` | untracked | 레퍼런스 전용 색상/레이아웃. palette system을 우회하고 있어 "팔레트 기반 DIY" 목표와 충돌한다. |
| `finflow_sankey/templates/income_statement.py` | modified | 기존 297줄 코드가 17줄 wrapper로 대첸. 기능은 동작하지만 가독성과 단순함이 훼손되었다. |
| `finflow_sankey/renderers/plotly_renderer.py` | modified | reference 분기(`palette.name != "dark"`) 추가. dark theme만 예외 처리되어 minimal/colorblind_safe theme도 reference style로 강제된다. |
| `finflow_sankey/palettes/default.yaml` | modified | 색상이 reference 3색으로 단순화됨. cost_of_revenue와 operating_expenses가 같은 색. 기존 역할별 색상 구분이 사라졌다. |
| `tests/test_income_reference_style.py` | untracked | reference style에 특화된 테스트. 기존 테스트와 함께 통과 여부를 확인해야 한다. |

### 주요 문제점

1. **reference style이 기본값이 되어버림**
   - 모든 손익계산서 출력이 `visual_style="reference"`로 고정된다.
   - 기존 사용자나 다른 statement(cash_flow, balance_sheet)와의 일관성이 깨진다.
   - 원본 계획서의 제안 3번("`render(layout="reference")` 또는 `theme="reference"` 형태로 명시 선택")을 따르지 않았다.

2. **palette system 우회**
   - `income_reference_style.py`에서 `profit`, `gross_profit`, `operating_income`, `net_income`을 모두 profit 색으로 통일.
   - `cost_of_revenue`, `operating_expenses`, `tax`, `non_operating_items`를 모두 operating_expenses 색으로 통일.
   - 사용자가 YAML 팔레트에서 `gross_profit` 색을 바꿔도 반영되지 않는다.

3. **theme 예외 처리가 부분적**
   - `palette.name != "dark"` 조건은 dark만 예외. minimal/colorblind_safe 사용자도 reference layout을 강제당함.
   - "기존 테마 호환" 목표(A-06)를 위반.

4. **파일 분산**
   - `income_statement.py` 기능이 4개 파일로 분산.
   - 디버깅 시 여러 파일을 오가야 하고, 새로운 contributor가 진입 장벽을 느낀다.

5. **고정된 figure 크기**
   - `height=760, width=900`. 데이터가 커지면 여전히 clipping될 수 있다.
   - "데이터 규모별 height 계산 정책 추가" 후속 제안을 아직 반영하지 않았다.

6. **상세 계정 처리의 일관성**
   - revenue/opex에 상세 계정이 2개 이상이면 detail 노드가 생긴다. 그러나 `Cost of Sales`처럼 단일 계정은 detail이 없어 레이아웃이 달라진다.
   - 사용자 입장에서 "내 데이터가 어떤 모양이 될지" 예측하기 어렵다.

## 2. 수정 방향

### 원칙

- **reference layout은 opt-in**: 기본 동작은 기존 snap layout을 유지한다.
- **palette는 유일한 색상 진실 공급원**: reference style도 palette role 색상을 존중한다.
- **파일은 최소한으로**: 기존 `income_statement.py` 안에 reference 옵션을 추가하거나, 별도 builder를 private module로 두고 public API는 그대로 유지.
- **theme은 모두 호환**: 특정 theme만 예외 처리하지 않는다.
- **크기는 데이터 기반**: 노드 수/최대 값에 따라 height를 조정한다.

### 권장 옵션

**Option B: 현재 작업을 보존하되 opt-in reference layout으로 리팩토링**

- `IncomeStatementTemplate.build()`는 기본 기존 로직 사용.
- `FinancialSankey.income_statement(..., layout="reference")` 또는 `.render(theme="reference")`일 때만 builder 사용.
- `income_reference_style.py`는 palette 기반으로 수정.
- 4개 분산 파일을 1~2개로 축소.

Option A(폐기 후 소규모 개선)와 Option C(현재대로 완성) 중 B를 권장한다.

## 3. 구체적인 수정 계획

### Phase 1. 기존 코드 복원 + opt-in API 설계

| 작업 | 파일 | 완료 기준 |
|------|------|-----------|
| `income_statement.py` 기존 로직 복원 | `finflow_sankey/templates/income_statement.py` | 기존 297줄 버전 복원 또는 동등한 단일 파일 구조 |
| `layout` 파라미터 추가 | `finflow_sankey/__init__.py`, `core/pipeline.py` | `.income_statement(..., layout="reference")` 가능 |
| reference builder 연동 | `finflow_sankey/templates/income_statement.py` | `layout="reference"`일 때만 분기 |

### Phase 2. palette 기반 reference style

| 작업 | 파일 | 완료 기준 |
|------|------|-----------|
| reference node color palette 기반 | `income_reference_style.py` | `node.role` → `palette.get_role_color(role)` |
| reference link color palette 기반 | `income_reference_style.py` | target/source role → palette + `semantic.link_opacity` |
| theme 예외 제거 | `plotly_renderer.py` | `palette.name != "dark"` 조건 삭제 |
| default.yaml 복원/조정 | `finflow_sankey/palettes/default.yaml` | role별 색상 분리 유지, `node_border_width: 0`로 클리핑 방지 |

### Phase 3. 파일 축소 및 유지보수성

| 작업 | 파일 | 완료 기준 |
|------|------|-----------|
| model/helper 통합 | `income_statement_model.py` 제거 | `income_statement_builder.py` 낸部로 이동 |
| sections 로직 통합 | `income_statement_sections.py` 제거 | `income_statement_builder.py` 낸部로 이동 |
| builder를 private module로 | `finflow_sankey/templates/_income_reference.py` | public import 경로 유지 |

### Phase 4. 자동 크기/레이아웃

| 작업 | 파일 | 완료 기준 |
|------|------|-----------|
| height 자동 계산 | `plotly_renderer.py` 또는 `income_reference_style.py` | 노드 수/최대 비율에 따라 `height` 조정 |
| margin 자동 계산 | `plotly_renderer.py` | label 길이에 따라 `margin.r` 조정 |
| 클리핑 회귀 테스트 | `tests/test_income_reference_style.py` | 큰 비용 노드가 있는 figure의 하단 edge 체크 |

### Phase 5. 테스트 정리

| 작업 | 파일 | 완료 기준 |
|------|------|-----------|
| 기존 테스트 통과 | `tests/` | `python -m pytest -q` 30개 이상 통과 |
| reference 테스트 추가/수정 | `tests/test_income_reference_style.py` | opt-in API와 palette 기반 색상 검증 |
| Dartlab 연동 테스트 유지 | `examples/dartlab_integration.py` | 삼성전자 샘플 정상 생성 |

## 4. 수용 기준

| ID | 기준 | 검증 방법 |
|----|------|-----------|
| R-01 | reference layout은 opt-in이다. | `.render()` 기본 출력이 기존 snap layout이다. |
| R-02 | palette override가 reference에도 적용된다. | `palette={"roles": {"gross_profit": "#FF00FF"}}` 시 노드 색 변경 |
| R-03 | 모든 기본 theme이 동작한다. | `theme="dark"`, `theme="minimal"`, `theme="colorblind_safe"` 모두 오류 없음 |
| R-04 | `Cost of Sales` 등 큰 노드가 하단 edge에서 잘리지 않는다. | height 자동 계산 후 스크린샷 하단 픽셀 체크 |
| R-05 | 기존 API 호환성이 유지된다. | `FinancialSankey.income_statement(df).validate().render()` 동작 |
| R-06 | 파일 수는 기존 대비 2개 이상 늘지 않는다. | `templates/` 아래 새 파일 ≤ 1개 |
| R-07 | 전체 테스트 통과 | `python -m pytest -q` |
| R-08 | lint 통과 | `ruff check finflow_sankey tests` |

## 5. 우선순위

1. **즉시**: `income_statement.py` 복원 + `layout` 파라미터 추가
2. **높음**: palette 기반 reference style, theme 예외 제거
3. **중간**: height 자동 계산, margin 조정
4. **낮음**: 파일 통합 리팩토링, visual regression fixture

## 6. 리스크

| 리스크 | 대응 |
|--------|------|
| reference style 변경으로 인한 기존 사용자 혼란 | opt-in으로 변경하여 기본 동작에 영향 없음 |
| palette 통합 시 reference 3색 느낌 사라짐 | default.yaml에서 revenue/profit/operating_expenses 색상을 reference 느낌으로 조정하면서 role별 구분 유지 |
| 파일 복원 작업 중 충돌 | git stash 또는 checkout으로 기존 버전 복원 후 cherry-pick |

## 7. 다음 행동

위 수정 계획에 동의하면 아래 순서로 개발 진행.

1. `income_statement.py` 기존 로직 복원
2. `layout="reference"` opt-in API 추가
3. reference builder를 `_income_reference.py`로 축소
4. palette 기반 reference style 적용
5. 테스트/린트 통과 후 `v0.1.13` 릴리즈

**질문**: Option B 방향으로 진행할까요? 아니면 Option A(현재 reference 작업을 폐기하고 기존 코드에서 소규모 개선만)를 선호하시나요?
