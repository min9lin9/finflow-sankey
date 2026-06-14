# FinFlow Sankey 안정화 및 문서 보강 기획

> 정반합(正-反-合) 기반 3회 반복 평가 + 기획

---

## Iteration 1: API 안정화 및 문서 기반 마련

### 1.1 正 (긍정적 측면)

| 항목 | 현재 상태 |
|------|-----------|
| API 체인 | `FinancialSankey.income_statement().validate().render().export_html()` 흐름이 직관적 |
| CI/CD | GitHub Actions (pytest, ruff, build) + PyPI trusted publishing 완료 |
| 버전 관리 | CHANGELOG, semantic tagging 정착 |
| 확장성 | layout="reference" opt-in, palette override 등 확장 포인트 확보 |

### 1.2 反 (부정적 측면)

| 항목 | 문제점 |
|------|--------|
| 버전 신호 | `v0.1.x`는 SemVer상 breaking changes 가능성을 암시. 외부 프로젝트가 의존하기 부담 |
| 문서 얇음 | README는 설치/빠른시작만. API reference, 심화 예제, 트러블슈팅 부재 |
| API 일관성 | `income_statement()`만 `layout` 파라미터. 다른 statement와의 인터페이스 균형 필요 |
| deprecation | `pyproject.toml`의 `license = {text = "MIT"}`가 2027년 2월 deprecated 예정 |

### 1.3 合 (종합 개선안)

| 작업 | 산출물 | 우선순위 |
|------|--------|----------|
| v1.0 로드맵 공개 | `ROADMAP.md` | 높음 |
| README 재구성 | `README.md` (Quickstart, API, Examples, FAQ) | 높음 |
| API reference 자동 생성 | `mkdocstrings` 연동 + `docs/api.md` | 높음 |
| `license` SPDX 마이그레이션 | `pyproject.toml` 수정 | 중간 |
| API 인터페이스 정리 | 모든 statement에 `layout` 파라미터 지원 여부 검토 문서 | 중간 |

---

## Iteration 2: 데이터 연동 및 예시 보강

### 2.1 正 (긍정적 측면)

| 항목 | 현재 상태 |
|------|-----------|
| Dartlab 연동 | 실제 삼성전자 데이터로 샘플 생성 가능 |
| Polars-first | 대용량 데이터 처리 성능 우수 |
| 입력 유연성 | DataFrame + section 매핑 방식으로 다양한 데이터 소스 적응 가능 |

### 2.2 反 (부정적 측면)

| 항목 | 문제점 |
|------|--------|
| Dartlab 한정 | Dartlab은 요약 데이터만. 상세 계정 시각화 어려움 |
| 예제 부족 | `examples/`에 Dartlab 1개뿐. 일반 사용자는 "내 데이터를 어떻게 넣지?" 막힘 |
| 데이터 변환 가이드 부재 | account → section 매핑 규칙, 통화 단위 처리, 기간 포맷 등 설명 없음 |
| 노트북 예제 없음 | Jupyter/Colab에서 바로 돌려볼 수 없음 |

### 2.3 合 (종합 개선안)

| 작업 | 산출물 | 우선순위 |
|------|--------|----------|
| DART OpenAPI 연동 예제 | `examples/dart_fss_integration.py` 또는 adapter | 높음 |
| Excel/CSV 입력 예제 | `examples/from_csv.py`, `examples/from_excel.py` | 높음 |
| Jupyter 노트북 2~3개 | `notebooks/01_income_statement.ipynb`, `notebooks/02_reference_layout.ipynb` | 높음 |
| 데이터 매핑 가이드 | `docs/mapping.md` | 중간 |
| FAQ / 트러블슈팅 | `docs/faq.md` | 중간 |

---

## Iteration 3: 커뮤니티 및 품질 보증

### 3.1 正 (긍정적 측면)

| 항목 | 현재 상태 |
|------|-----------|
| 테스트 | 36개 pytest 통과 |
| 린트 | ruff check 통과 |
| 배포 | PyPI 자동 업로드, GitHub Pages 문서 |
| License | MIT |

### 3.2 反 (부정적 측면)

| 항목 | 문제점 |
|------|--------|
| 1인 프로젝트 | 장기 유지보수, 버그 대응, 리뷰 체계 부재 |
| edge case 테스트 부족 | 누락 section, 0값, 음수 값, 극단적 비율, 통화 단위 mismatch 등 미검증 |
| 커뮤니티 인프라 없음 | Issue/PR 템플릿, CONTRIBUTING.md, Code of Conduct 부재 |
| 사용자 피드백 채널 없음 | GitHub Discussions 미활성화, 사용 설문/피드백 루프 없음 |
| 성능/회귀 테스트 없음 | 큰 데이터셋, 많은 계정 수에서의 렌더링 성능 측정 부재 |

### 3.3 合 (종합 개선안)

| 작업 | 산출물 | 우선순위 |
|------|--------|----------|
| Issue/PR 템플릿 | `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md` | 높음 |
| Contributor 가이드 | `CONTRIBUTING.md` | 높음 |
| Edge case 테스트 보강 | `tests/test_edge_cases.py` | 높음 |
| 성능/회귀 벤치마크 | `tests/benchmarks/test_render_performance.py` | 중간 |
| GitHub Discussions 활성화 | 설정 + 안내 문구 추가 | 중간 |
| 보안/의존성 관리 | `dependabot.yml`, `SECURITY.md` | 낮음 |

---

## 종합 실행 계획

### Phase 1: 문서 기반 (1~2주)

1. `ROADMAP.md` 작성: v0.2.x ~ v1.0 목표와 breaking changes 정책
2. README 재구성
3. mkdocstrings 연동하여 API reference 자동 생성
4. `license = "MIT"`로 마이그레이션

### Phase 2: 예시 및 연동 (2~3주)

1. DART OpenAPI(`dart-fss`) 연동 예제
2. CSV/Excel 입력 예제
3. Jupyter notebook 2개
4. `docs/mapping.md`, `docs/faq.md`

### Phase 3: 품질 및 커뮤니티 (2~3주)

1. Issue/PR 템플릿
2. `CONTRIBUTING.md`
3. Edge case 테스트 15개 이상 추가
4. GitHub Discussions 활성화

### 수용 기준

| ID | 기준 | 검증 방법 |
|----|------|-----------|
| S-01 | README만으로 처음 사용자가 10분 내에 첫 Sankey 생성 | 신규 사용자 테스트 |
| S-02 | API reference가 90% 이상 public API 커버 | mkdocstrings 빌드 확인 |
| S-03 | DART/CSV/Excel 3가지 입력 예제 동작 | 예제 스크립트 실행 |
| S-04 | edge case 테스트 15개 이상 통과 | `pytest tests/test_edge_cases.py -q` |
| S-05 | Issue/PR 템플릿 및 CONTRIBUTING.md 존재 | 파일 확인 |
| S-06 | 전체 테스트 50개 이상 통과 | `pytest -q` |
| S-07 | 린트 통과 | `ruff check .` |

---

## 다음 행동

위 3회 정반합 기획에 따라 **Phase 1부터 순차 실행**할 수 있습니다. 승인 시 다음 작업부터 시작합니다:

1. `ROADMAP.md` 초안 작성
2. README 재구성
3. mkdocstrings API reference 연동
