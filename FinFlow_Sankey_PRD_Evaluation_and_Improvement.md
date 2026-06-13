# FinFlow Sankey PRD 평가 및 개선안

## 1. 평가 요약

### 1.1 강점

| 영역 | 평가 |
|------|------|
| **문제 정의** | 재무제표의 표 형태 한계, 계정명 차이, 부호 처리, 회계 검증 필요성을 명확히 제시함. |
| **기술 선택** | Polars-first + Plotly Sankey 조합은 대용량 재무 데이터 처리와 시각화 모두에 적합함. |
| **파이프라인** | Raw data → adapter → schema validation → mapping → validation → graph → render 흐름이 직관적임. |
| **검증 설계** | Period/Currency mismatch, reconciliation, missing account 등 구조화된 예외 설계가 견고함. |
| **확장성** | Template, mapper, validator, renderer를 교체 가능한 구조로 설계함. |

### 1.2 개선 필요 사항

| 영역 | 문제점 | 개선 방향 |
|------|--------|-----------|
| **색상 정책** | "매출, 이익, 비용 별로 색상이 달라야 함" 요구가 구체적으로 반영되지 않음. | 계정 역할(role)별 색상 팔레트를 정의하고, Sankey 노드/링크에 일관되게 적용. |
| **색상 커스터마이징** | 팔레트를 나중에 변경할 수 있는 구조가 없음. | YAML/JSON 팔레트 정의, 런타임 override, theme 시스템 추가. |
| **선 스타일** | "두께가 같은 선으로 구성" 요구가 모호하게 처리됨. | 링크 폭은 값에 비례하되, 링크/노드의 외곽선(stroke) 두께는 일정하게 통일. |
| **시각적 완성도** | hover, 폰트, 여백, 범례, 노드 정렬 등 구체적인 디자인 가이드가 부족함. | 재무 Sankey 전용 theme 시스템과 layout 가이드를 추가. |
| **재무상태표 UX** | reconciliation_view라는 개념이 있지만, 시각적으로 어떻게 다르게 보일지 구체적이지 않음. | 색상/배치/제목 형식으로 reconciliation 전용 스타일을 분리. |
| **minor grouping 시각화** | "Other"로 묶인 계정의 시각적 처리가 구체적이지 않음. | Other 노드의 색상, 위치, hover 정보를 별도 정책으로 관리. |

---

## 2. 핵심 개선안: 시각화 디자인 정책

### 2.1 색상 정책 (매출 / 비용 / 이익 / 현금 역할별)

Sankey의 노드와 링크는 **계정 역할(role)**에 따라 색상을 통일한다. 색상은 직관적인 재무 의미를 담고, 색맹/색약 사용자를 고려해 명도 차이도 확보한다.

#### 2.1.1 기본 색상 팔레트 (Default)

| 역할 (Role) | 의미 | 기본 색상 | Hex 코드 |
|-------------|------|-----------|----------|
| **revenue** | 매출 / 현금 유입 | 딥 블루 | `#2563EB` |
| **cost_of_revenue** | 매출원가 / 직접비 | 오렌지 | `#F59E0B` |
| **operating_expenses** | 판관비 / 간접비 | 레드 | `#DC2626` |
| **non_operating_items** | 영업외 수익/비용 | 슬레이트 | `#64748B` |
| **tax** | 법인세 / 세금 | 퍼플 | `#7C3AED` |
| **profit** / **net_income** | 이익 / 순이익 | 에메랄드 그린 | `#059669` |
| **cash_inflow** | 현금 유입 | 시안 블루 | `#0891B2` |
| **cash_outflow** | 현금 유출 | 코랄 레드 | `#E11D48` |
| **cash_balance** | 현금 잔액 | 골드 | `#D97706` |
| **asset** | 자산 | 네이비 | `#1E3A8A` |
| **liability** | 부채 | 버걸디 | `#9F1239` |
| **equity** | 자본 | 포레스트 그린 | `#15803D` |
| **other** | 기타/묶음 계정 | 그레이 | `#94A3B8` |
| **background** | 배경 | 화이트 | `#FFFFFF` |
| **plot_background** | plot 영역 배경 | 연한 회색 | `#F8FAFC` |
| **text** | 텍스트 | 슬레이트 | `#334155` |
| **border** | 테두리 | 슬레이트 | `#334155` |

#### 2.1.2 색상 적용 규칙

```text
1. 노드 색상: 해당 노드의 standard_role에 따라 팔레트에서 선택.
2. 링크 색상: source 노드의 색상을 기본으로 하되, 투명도 0.4~0.6 적용.
3. hover 시 링크 색상: 투명도를 0.8로 높여 강조.
4. "Other" 그룹 노드: 항상 팔레트의 other 색상으로 통일.
5. 색맹/색약 대비: 색상뿐 아니라 노드 label 접두사(+/-) 또는 아이콘으로 부호 표시.
```

#### 2.1.3 손익계산서 색상 적용 예시

```text
[Revenue] #2563EB
    ├── [Cost of Revenue] #F59E0B
    └── [Gross Profit] #2563EB
            ├── [Operating Expenses] #DC2626
            ├── [Non-operating Items] #64748B
            └── [Operating Income] #2563EB
                    ├── [Tax] #7C3AED
                    └── [Net Income] #059669
```

#### 2.1.4 현금흐름표 색상 적용 예시

```text
[Beginning Cash] #D97706
    ├── [Operating Cash Flow] #0891B2  (유입) / #E11D48 (유출)
    ├── [Investing Cash Flow] #E11D48
    ├── [Financing Cash Flow] #E11D48
    ├── [FX Effect] #64748B
    └── [Ending Cash] #D97706
```

#### 2.1.5 재무상태표 Reconciliation 색상 적용 예시

```text
[Total Assets] #1E3A8A
    ├── [Current Assets] #3B82F6
    └── [Non-current Assets] #1D4ED8

[Liabilities and Equity] #64748B
    ├── [Current Liabilities] #9F1239
    ├── [Non-current Liabilities] #BE123C
    └── [Equity] #15803D
```

> 재무상태표는 **좌측(Asset) / 우측(Liability + Equity)**으로 분할 배치하며, 제목에 `[Reconciliation View]`를 명시한다.

---

### 2.2 색상 팔레트 커스터마이징 시스템

색상 팔레트는 **런타임 교체 가능**해야 하며, 다음 3가지 경로를 모두 지원한다.

#### 2.2.1 YAML 파일 기반 팔레트

```yaml
# finflow_sankey/palettes/corporate_a.yaml
name: "Corporate A"
version: "1.0.0"
description: "기업 A 브랜드 컬러 기반 재무 Sankey 팔레트"
roles:
  revenue: "#0055FF"
  cost_of_revenue: "#FF8800"
  operating_expenses: "#CC0000"
  non_operating_items: "#6B7280"
  tax: "#7C3AED"
  profit: "#00AA55"
  net_income: "#00AA55"
  cash_inflow: "#0099CC"
  cash_outflow: "#DD1144"
  cash_balance: "#B8860B"
  asset: "#002277"
  liability: "#881122"
  equity: "#116622"
  other: "#9CA3AF"
semantic:
  background: "#FFFFFF"
  plot_background: "#F8FAFC"
  text: "#1F2937"
  border: "#1F2937"
  link_opacity: 0.45
  hover_opacity: 0.85
  node_border_width: 1.5
  link_border_width: 0.5
  node_thickness: 24
  font_family: "Inter, Pretendard, Arial"
  font_size: 12
  title_font_size: 18
```

#### 2.2.2 Python dict 기반 런타임 override

```python
from finflow_sankey import FinancialSankey

my_palette = {
    "revenue": "#FF5733",
    "operating_expenses": "#33FF57",
    "profit": "#3357FF",
    "other": "#A0A0A0",
}

fig = (
    FinancialSankey
    .income_statement(lf, period="FY2025", currency="USD")
    .validate()
    .render(
        title="FY2025 Income Statement Flow",
        palette=my_palette,  # 부분 override
    )
)
```

#### 2.2.3 Theme 시스템

```python
fig = (
    FinancialSankey
    .income_statement(lf)
    .validate()
    .render(
        title="FY2025 Income Statement Flow",
        theme="colorblind_safe",  # 내장 theme
    )
)
```

내장 theme 목록:

| Theme | 설명 |
|-------|------|
| `default` | 기본 재무 색상 팔레트 |
| `monochrome` | 회색조 중심, 인쇄용 |
| `colorblind_safe` | 색맹/색약 friendly (파랑/주황/청록 위주) |
| `minimal` | 흰 배경 + 테두리 강조 |
| `custom` | 사용자 YAML 팔레트 |

#### 2.2.4 팔레트 우선순위 (높은 순)

```text
1. render() 호출 시 전달된 palette dict
2. render() 호출 시 지정된 custom YAML 파일 경로
3. render() 호출 시 지정된 theme 이름
4. FinancialSankey 인스턴스 생성 시 설정된 default_palette
5. 라이브러리 기본 팔레트
```

---

### 2.3 선 스타일 정책: "두께가 같은 선"

원문의 "두께가 같은 선으로 구성" 요구는 Sankey의 **링크 폭(value 비례)**과 혼동될 수 있다. 따라서 다음과 같이 명확히 구분한다.

| 요소 | 동작 | 규칙 |
|------|------|------|
| **링크 폭 (link value)** | 데이터 값에 비례 | Sankey의 본질. 값이 클수록 링크가 두꺼워짐. |
| **링크 외곽선 (link line)** | 일정 두께 | 팔레트의 `link_border_width` (기본 0.5px)로 통일. 색상은 링크 색상보다 한 톤 어둡게. |
| **노드 테두리선 (node border)** | 일정 두께 | 팔레트의 `node_border_width` (기본 1.5px), 색상은 팔레트 `border` 값. |
| **노드 두께 (node thickness)** | 고정 | 팔레트의 `node_thickness` (기본 24px). |
| **노드 코너** | 둥글게 | radius 4px 적용. |

#### 2.3.1 Plotly 적용 예시

```python
import plotly.graph_objects as go

palette = load_palette("default")  # YAML 또는 내장

fig.add_trace(go.Sankey(
    arrangement="snap",
    node=dict(
        pad=20,
        thickness=palette["semantic"]["node_thickness"],
        line=dict(
            color=palette["semantic"]["border"],
            width=palette["semantic"]["node_border_width"],
        ),
        color=[palette["roles"][r] for r in node_roles],
        label=node_labels,
        hovertemplate=palette["templates"]["node_hover"],
    ),
    link=dict(
        source=source_indices,
        target=target_indices,
        value=values,
        color=[hex_to_rgba(palette["roles"][r], palette["semantic"]["link_opacity"]) for r in link_roles],
        line=dict(
            color=palette["semantic"]["border"],
            width=palette["semantic"]["link_border_width"],
        ),
        hovertemplate=palette["templates"]["link_hover"],
    ),
))
```

#### 2.3.2 선 두께 정책 요약

```text
✅ 링크의 납작한 면적(width)은 값에 비례 → Sankey 정보 전달의 핵심.
✅ 링크/노드의 선(line/border) 두께는 일정 → 깔끔하고 통일된 시각적 느낌.
✅ 노드 두께(thickness)는 고정값 사용 → 가독성 유지.
✅ 모든 선 스타일은 팔레트에서 중앙 관리 → 변경 시 한 곳만 수정.
```

---

### 2.4 시각적 깔끔함을 위한 Layout 정책

#### 2.4.1 기본 레이아웃 규칙

| 항목 | 규칙 | 이유 |
|------|------|------|
| **노드 정렬** | `arrangement="snap"` 또는 사용자 지정 x/y 좌표 사용 | 재무 흐름의 단계적 흐름을 명확히 함. |
| **수직 간격 (pad)** | 최소 20px | 노드 label이 겹치지 않도록 함. |
| **수평 단계 간격** | 4~5개 단계로 제한, 단계가 많으면 자동 축약 | Sankey가 너무 넓어지지 않도록 함. |
| **폰트** | 팔레트 `font_family` 사용. 기본 `"Inter, Pretendard, Arial"`, 본문 12px, 제목 18px. | 가독성과 전문성. |
| **여백** | left/right 40px, top/bottom 30px | 답답하지 않은 여백. |
| **배경** | 팔레트 `background`와 `plot_background` 사용 | 깔끔한 인쇄/보고서용. |
| **범례** | 색상 팔레트 기반 범례를 그래프 우측 또는 하단에 배치 | 색상 의미를 명확히 함. |
| **hover** | 금액, 비중, 기간, 통화, 검증 상태를 한 줄씩 표시 | 정보 과잉 방지. |

#### 2.4.2 Plotly Layout 예시

```python
fig.update_layout(
    title=dict(
        text="FY2025 Income Statement Flow",
        font=dict(
            size=palette["semantic"]["title_font_size"],
            color=palette["semantic"]["text"],
            family=palette["semantic"]["font_family"],
        ),
        x=0.5,
    ),
    font=dict(
        size=palette["semantic"]["font_size"],
        color=palette["semantic"]["text"],
        family=palette["semantic"]["font_family"],
    ),
    paper_bgcolor=palette["semantic"]["background"],
    plot_bgcolor=palette["semantic"]["plot_background"],
    margin=dict(l=40, r=40, t=60, b=40),
    showlegend=False,
    height=600,
    width=1100,
)
```

#### 2.4.3 범례( Legend ) 추가

Plotly Sankey는 기본적으로 범례를 지원하지 않으므로, 색상 의미를 annotation으로 추가한다.

```python
def add_color_legend(fig, palette, visible_roles):
    annotations = []
    for i, role in enumerate(visible_roles):
        color = palette["roles"].get(role, palette["roles"]["other"])
        label = role.replace("_", " ").title()
        annotations.append(dict(
            x=1.02,
            y=0.95 - i * 0.08,
            xref="paper",
            yref="paper",
            text=f"<span style='color:{color};'>■</span> {label}",
            showarrow=False,
            font=dict(size=12, family=palette["semantic"]["font_family"]),
            align="left",
        ))
    fig.update_layout(annotations=annotations)
```

---

### 2.5 Hover 템플릿 개선

#### 2.5.1 노드 Hover

```text
Revenue
Amount: $100,000,000
Share of Revenue: 100.0%
Period: FY2025
Currency: USD
Original accounts: Net Sales, Sales Revenue
Validation: Passed
```

#### 2.5.2 링크 Hover

```text
Revenue → Operating Expenses
Amount: $40,000,000
Share of Revenue: 40.0%
Flow type: Outflow
Original accounts: SG&A, R&D
```

#### 2.5.3 Plotly hovertemplate 예시

```python
hovertemplate_node = (
    "<b>%{label}</b><br>"
    "Amount: $%{value:,.0f}<br>"
    "Share of Revenue: %{customdata[0]}%<br>"
    "Period: %{customdata[1]}<br>"
    "Currency: %{customdata[2]}<br>"
    "Validation: %{customdata[3]}"
    "<extra></extra>"
)
```

---

## 3. 팔레트 커스터마이징 상세 설계

### 3.1 Palette 클래스 설계

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
import yaml


@dataclass(frozen=True)
class RolePalette:
    revenue: str = "#2563EB"
    cost_of_revenue: str = "#F59E0B"
    operating_expenses: str = "#DC2626"
    non_operating_items: str = "#64748B"
    tax: str = "#7C3AED"
    profit: str = "#059669"
    net_income: str = "#059669"
    cash_inflow: str = "#0891B2"
    cash_outflow: str = "#E11D48"
    cash_balance: str = "#D97706"
    asset: str = "#1E3A8A"
    liability: str = "#9F1239"
    equity: str = "#15803D"
    other: str = "#94A3B8"


@dataclass(frozen=True)
class SemanticStyle:
    background: str = "#FFFFFF"
    plot_background: str = "#F8FAFC"
    text: str = "#334155"
    border: str = "#334155"
    link_opacity: float = 0.45
    hover_opacity: float = 0.85
    node_border_width: float = 1.5
    link_border_width: float = 0.5
    node_thickness: int = 24
    font_family: str = "Inter, Pretendard, Arial"
    font_size: int = 12
    title_font_size: int = 18


@dataclass
class ColorPalette:
    name: str = "default"
    version: str = "1.0.0"
    description: str = ""
    roles: RolePalette = field(default_factory=RolePalette)
    semantic: SemanticStyle = field(default_factory=SemanticStyle)

    @classmethod
    def from_yaml(cls, path: str | Path) -> "ColorPalette":
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls(
            name=data["name"],
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            roles=RolePalette(**data.get("roles", {})),
            semantic=SemanticStyle(**data.get("semantic", {})),
        )

    def override(self, overrides: dict) -> "ColorPalette":
        """런타임 색상 override."""
        role_overrides = {k: v for k, v in overrides.items() if k in RolePalette.__dataclass_fields__}
        semantic_overrides = {k: v for k, v in overrides.items() if k in SemanticStyle.__dataclass_fields__}
        return ColorPalette(
            name=f"{self.name}_overridden",
            roles=RolePalette(**{**self.roles.__dict__, **role_overrides}),
            semantic=SemanticStyle(**{**self.semantic.__dict__, **semantic_overrides}),
        )

    def validate(self) -> None:
        """팔레트 유효성 검사."""
        for role, color in self.roles.__dict__.items():
            if not _is_valid_hex(color):
                raise ValueError(f"Invalid hex color for role '{role}': {color}")
        if not 0.0 <= self.semantic.link_opacity <= 1.0:
            raise ValueError("link_opacity must be between 0 and 1")
```

### 3.2 Theme 레지스트리

```python
from enum import Enum


class BuiltInTheme(Enum):
    DEFAULT = "default"
    MONOCHROME = "monochrome"
    COLORBLIND_SAFE = "colorblind_safe"
    MINIMAL = "minimal"


BUILT_IN_PALETTES: dict[str, ColorPalette] = {
    "default": ColorPalette(),
    "monochrome": ColorPalette(
        name="monochrome",
        roles=RolePalette(
            revenue="#374151",
            cost_of_revenue="#6B7280",
            operating_expenses="#4B5563",
            profit="#111827",
            other="#9CA3AF",
        ),
        semantic=SemanticStyle(
            background="#FFFFFF",
            plot_background="#FFFFFF",
            text="#111827",
            border="#000000",
        ),
    ),
    "colorblind_safe": ColorPalette(
        name="colorblind_safe",
        roles=RolePalette(
            revenue="#0173B2",
            cost_of_revenue="#DE8F05",
            operating_expenses="#029E73",
            profit="#D55E00",
            other="#949494",
        ),
    ),
    "minimal": ColorPalette(
        name="minimal",
        roles=RolePalette(
            revenue="#2563EB",
            operating_expenses="#DC2626",
            profit="#059669",
            other="#CBD5E1",
        ),
        semantic=SemanticStyle(
            node_border_width=2.0,
            link_border_width=0.8,
            background="#FFFFFF",
            plot_background="#FFFFFF",
        ),
    ),
}
```

### 3.3 Renderer에 Palette 통합

```python
class PlotlyRenderer:
    def __init__(self, palette: ColorPalette | None = None):
        self.palette = palette or BUILT_IN_PALETTES["default"]

    def render(self, graph: FinancialGraph) -> go.Figure:
        # palette 기반으로 node/link 색상, 선 두께, 레이아웃 모두 생성
        ...
```

### 3.4 런타임 API 예시

```python
import polars as pl
from finflow_sankey import FinancialSankey

lf = pl.scan_csv("income_statement.csv")

# 1. 내장 theme 사용
fig = (
    FinancialSankey
    .income_statement(lf, period="FY2025", currency="USD")
    .validate()
    .render(title="FY2025 Income Statement Flow", theme="colorblind_safe")
)

# 2. YAML 파일 기반 팔레트
fig = (
    FinancialSankey
    .income_statement(lf)
    .validate()
    .render(title="Custom Palette", palette="./palettes/corporate_a.yaml")
)

# 3. dict 기부분 override
fig = (
    FinancialSankey
    .income_statement(lf)
    .validate()
    .render(
        title="Partial Override",
        palette={"revenue": "#0055FF", "profit": "#00AA55"},
    )
)

# 4. SankeyPipeline 생성 시 기본 팔레트 설정
sankey = (
    FinancialSankey
    .income_statement(lf)
    .with_palette("./palettes/corporate_a.yaml")
    .validate()
)
fig = sankey.render()
```

### 3.5 팔레트 검증 규칙

| 검증 항목 | 설명 | 실패 시 |
|-----------|------|---------|
| 필수 role 존재 | `revenue`, `operating_expenses`, `profit`, `other` 최소 4개 필요 | `MissingRoleColorError` |
| Hex 유효성 | `#RRGGBB` 또는 `#RGB` 형식 | `InvalidColorError` |
| 투명도 범위 | `link_opacity`, `hover_opacity`는 0~1 | `InvalidOpacityError` |
| 대비 경고 | 배경-텍스트, 배경-노드 간 WCAG 대비 부족 시 warning | `LowContrastWarning` |
| 중복 색상 | 서로 다른 role이 동일 색상이면 warning | `DuplicateColorWarning` |

---

## 4. 개선된 PRD 섹션: 16. UX / 시각화 정책

원문 PRD의 16장을 다음과 같이 대체/보완한다.

---

### 16. UX / 시각화 정책

#### 16.1 기본 방향

재무제표 Sankey는 예쁘게 보이는 것보다 **오해 없이 읽히는 것**이 더 중요하다. 따라서 모든 시각적 요소는 **회계 의미를 정확히 전달**하는 데 집중한다.

색상은 계정 역할(role)에 따라 통일되며, 색상 팔레트는 **런타임에 교체 가능**해야 한다.

기본 정책:

```text
수익·현금유입: 파란/청록 계열
비용·손실·현금유출: 빨강/주황 계열
이익·잔여 항목: 녹색 계열
자산: 남색 계열
부채: 적색/버걸디 계열
자본: 녹색 계열
현금 잔액: 금색 계열
묶음/기타: 회색
```

#### 16.2 색상 팔레트 정의

색상 팔레트는 다음 3가지 방식으로 관리한다.

1. **내장 theme**: `default`, `monochrome`, `colorblind_safe`, `minimal`
2. **YAML 파일**: 사용자가 직접 작성한 `.yaml` 파일
3. **런타임 dict**: `.render(palette={...})`로 일부 색상 override

기본 색상:

| 역할 | 색상 | Hex |
|------|------|-----|
| Revenue | 딥 블루 | `#2563EB` |
| Cost of Revenue | 오렌지 | `#F59E0B` |
| Operating Expenses | 레드 | `#DC2626` |
| Tax | 퍼플 | `#7C3AED` |
| Net Income / Profit | 에메랄드 그린 | `#059669` |
| Cash Inflow | 시안 블루 | `#0891B2` |
| Cash Outflow | 코랄 레드 | `#E11D48` |
| Cash Balance | 골드 | `#D97706` |
| Asset | 네이비 | `#1E3A8A` |
| Liability | 버걸디 | `#9F1239` |
| Equity | 포레스트 그린 | `#15803D` |
| Other | 그레이 | `#94A3B8` |

색상 적용 규칙:

```text
- 노드 색상: standard_role에 따라 팔레트에서 선택.
- 링크 색상: source 노드 색상에 투명도 0.45 적용.
- hover 시 링크 투명도 0.85로 상향.
- 색맹/색약 사용자를 위해 label 옆에 (+)/(-)/(=) 접두사 선택 표시.
- 모든 색상은 palette에서 중앙 관리하며, 런타임 교체 가능.
```

#### 16.3 선 스타일 정책

Sankey 링크의 **면적(width)**은 데이터 값에 비례해야 하지만, **외곽선(line)**과 **노드 테두리**의 두께는 일정하게 유지한다.

| 요소 | 규칙 |
|------|------|
| 링크 면적 | value에 비례 |
| 링크 외곽선 두께 | 0.5px, 색상 `border` |
| 노드 두께 | 24px 고정 |
| 노드 테두리 두께 | 1.5px, 색상 `border` |
| 노드 모서리 | radius 4px |

선 스타일 역시 palette의 `semantic` 영역에서 관리한다.

#### 16.4 레이아웃 정책

```text
노드 정렬: snap 또는 사용자 지정 좌표
수직 간격(pad): 20px 이상
폰트: palette.font_family, 본문 12px, 제목 18px
배경: palette.background (#FFFFFF), plot 영역 palette.plot_background (#F8FAFC)
여백: left/right 40px, top 60px, bottom 40px
크기: 기본 1100x600px
범례: 색상 의미를 annotation으로 우측에 표시
```

#### 16.5 부호 표시

Sankey link의 폭은 양수 값으로 표현하되, 원래 값의 부호는 metadata에 보존한다.

```text
raw_value = -120
display_value = 120
flow_direction = outflow
sign = negative
node_label_prefix = "(-)"  # 선택적
```

#### 16.6 Hover 표시

**노드 hover:**

```text
Revenue
Amount: $100.0M
Share of Revenue: 100.0%
Period: FY2025
Currency: USD
Original accounts: Net Sales, Sales Revenue
Validation: Passed
```

**링크 hover:**

```text
Revenue → Operating Expenses
Amount: $40.0M
Share of Revenue: 40.0%
Flow type: Outflow
Original accounts: SG&A, R&D
```

#### 16.7 재무상태표 Reconciliation View

재무상태표는 기간 흐름이 아니라 특정 시점의 잔액이므로, 다음과 같이 시각적으로 구분한다.

```text
제목: "[Reconciliation View] Assets vs Liabilities and Equity (2025-12-31)"
배치: 좌측 Assets, 우측 Liabilities and Equity
색상: Asset은 남색 계열, Liability는 버걸디, Equity는 녹색
링크: Asset → Liability, Asset → Equity (양쪽 합계가 같은 길이로 표현)
```

#### 16.8 minor grouping 시각화

작은 계정을 "Other"로 묶을 때는 다음 시각적 규칙을 따른다.

```text
색상: 팔레트 other 색상 (#94A3B8) 고정
위치: 동일 parent 바로 아래 또는 마지막에 배치
hover: "Includes: account1, account2, account3" 표시
label: "Other (n accounts)" 또는 "Other"
```

#### 16.9 팔레트 커스터마이징 인터페이스

```python
# YAML 파일
.render(palette="./my_palette.yaml")

# 내장 theme
.render(theme="colorblind_safe")

# dict override
.render(palette={"revenue": "#FF5733", "profit": "#3357FF"})

# pipeline 수준 기본 설정
FinancialSankey.income_statement(lf).with_palette("./my_palette.yaml")
```

팔레트 검증:

```text
- 필수 role 색상 존재 여부
- Hex 색상 형식 유효성
- 투명도 0~1 범위
- 배경-텍스트 대비 경고
- 중복 색상 경고
```

---

## 5. 개선된 PRD 섹션: 8. MVP 범위 (팔레트/Theme 추가)

### 8.1 v0.1 포함 (추가)

| 기능 | 설명 | 우선순위 |
|------|------|----------|
| 기본 색상 팔레트 | role별 기본 색상 정의 | P0 |
| 내장 theme 2종 | `default`, `minimal` | P1 |

### 8.2 v0.2 포함 (추가)

| 기능 | 설명 |
|------|------|
| YAML 팔레트 지원 | 사용자 정의 `.yaml` 색상 팔레트 로드 |
| 런타임 palette override | `.render(palette={...})` 지원 |
| 추가 내장 theme | `monochrome`, `colorblind_safe` |
| 팔레트 검증 | Hex, 대비, 중복 검사 |
| 팔레트 문서화 | 기본 팔레트 및 custom 예시 제공 |

### 8.3 v0.3 이후 (추가)

| 기능 | 설명 |
|------|------|
| 팔레트 버전 관리 | `version` 필드로 팔레트 호환성 관리 |
| 팔레트 마켓플레이스 | 재무 보고서용 프리셋 팔레트 공유 구조 |
| 다크모드 theme | `dark` 내장 theme |
| 기업 브랜드 컬러 자동 추출 | 로고/브랜드 가이드에서 색상 자동 생성 (optional) |

---

## 6. 개선된 PRD 섹션: 21. 주요 리스크와 대응 (추가)

| 리스크 | 설명 | 대응 |
|--------|------|------|
| 색상 혼란 | 매출/비용/이익 색상이 통일되지 않으면 오해 발생 | role별 색상 팔레트를 코드와 문서에 동일하게 정의 |
| 선 두께 불일치 | 링크 외곽선 두께가 제각각이면 지저분해 보임 | 링크 line.width=0.5px, 노드 border=1.5px로 강제 |
| 색맹/색약 | 색상만으로 역할 구분이 어려울 수 있음 | label 접두사 (+/-) 및 범례 annotation 추가, `colorblind_safe` theme |
| 팔레트 변경 어려움 | 하드코딩된 색상은 유지보수/커스터마이징이 어려움 | palette를 YAML/JSON/클로바 중앙 관리, theme 시스템 도입 |
| 커스텀 팔레트 오류 | 사용자가 잘못된 색상을 지정할 수 있음 | 팔레트 검증: hex, 필수 role, 대비, 중복 |
| 재무상태표 오해 | Sankey로 흐름처럼 보일 수 있음 | 제목에 [Reconciliation View] 명시, 좌우 분할 배치 |
| 그래프 복잡도 | 계정이 많으면 시각적 혼란 | minor grouping + Other 회색 처리 + top_n 제한 |

---

## 7. 구현 체크리스트

PRD 개선안을 실제 코드에 반영할 때 다음 항목을 확인한다.

- [ ] `renderers/plotly_renderer.py`에 `ColorPalette` 객체 전달
- [ ] `palettes/default.yaml`, `palettes/monochrome.yaml`, `palettes/colorblind_safe.yaml` 추가
- [ ] `ColorPalette.from_yaml()` 구현
- [ ] `ColorPalette.override()` 구현
- [ ] `ColorPalette.validate()` 구현 (hex, role, opacity, contrast, duplicate)
- [ ] `BUILT_IN_PALETTES` 레지스트리 구현
- [ ] `.render(theme=...)` API 지원
- [ ] `.render(palette="path/to/file.yaml")` API 지원
- [ ] `.render(palette={...})` API 지원
- [ ] `.with_palette()` pipeline 메서드 지원
- [ ] 링크 색상을 source role 색상 + palette.link_opacity로 생성
- [ ] 노드 테두리 두께 palette.node_border_width, 링크 외곽선 palette.link_border_width로 통일
- [ ] 노드 thickness palette.node_thickness 고정
- [ ] hover template에 금액/비중/기간/통화/검증 상태 포함
- [ ] 범례 annotation 자동 생성 (visible roles 기반)
- [ ] 색맹/색약-safe theme 옵션 추가
- [ ] 재무상태표 reconciliation view 좌우 분할 배치
- [ ] Other 그룹은 other 색상 + "Includes: ..." hover 정보
- [ ] 사용자 정의 색상 팔레트 YAML 예시 문서화

---

## 8. 종합 평가 점수

| 항목 | 원문 점수 | 개선안 반영 후 점수 | 개선 내용 |
|------|----------|---------------------|-----------|
| 색상 정책 | 4/10 | 9/10 | 역할별 팔레트, 투명도, hover 강조 정의 |
| 색상 커스터마이징 | 2/10 | 9/10 | YAML, dict override, theme 시스템, palette 클래스 추가 |
| 선 스타일 정책 | 3/10 | 9/10 | 면적 vs 선 두께 분리, palette 중앙 관리 |
| 시각적 깔끔함 | 5/10 | 9/10 | 폰트, 여백, 정렬, 범례, 레이아웃 구체화 |
| 회계 의미 전달 | 8/10 | 9.5/10 | 색상으로 역할 구분, reconciliation view 명시 |
| 구현 가능성 | 8/10 | 9.5/10 | Plotly 코드 예시, 클래스 설계, 체크리스트 제공 |
| 문서 완성도 | 8/10 | 9.5/10 | 색상표, 예시, 체크리스트, 리스크, API 추가 |

---

*본 문서는 원문 PRD의 시각화/UX 정책을 중심으로 평가하고, 요구사항(매출/이익/비용 색상 구분, 깔끔한 디자인, 일정한 선 두께, 팔레트 변경 가능성)을 구체적으로 반영한 개선안이다.*
