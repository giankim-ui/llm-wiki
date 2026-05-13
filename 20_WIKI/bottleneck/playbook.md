---
type: concept
scope: bottleneck
status: stable
tags:
  - bottleneck
  - playbook
  - checklist
---

# 신규 파이프라인 시작 전 체크리스트 (Playbook)

모든 bottleneck 문서의 `prevention` 항목에서 추출한 공통 대응 원칙.

## 필수 실행 순서

1. **Pre-flight 스크립트 실행** — 엑셀 시트 구조 먼저 dump ([[btlnk-hr-pipeline-260512]])
2. **컬럼 매핑 명시** — 헤더 row 읽고 한국어 레이블 1:1 대응 확인, `auto_detect` 금지
3. **PK scope 포함 설계** — `parent_id::dept_slug` 형태로 BU 충돌 방지
4. **LIMIT=1 → LIMIT=5 → 전체** 순 단계 검증
5. **검증 앵커 tolerance 설정** — `±15` 적용, 엄격 동등 비교 금지

## 카테고리별 체크리스트

| 카테고리 | 체크포인트 |
|---|---|
| [[tool-trap]] | DuckDB `auto_detect` 비활성화, 명시적 컬럼 매핑 |
| [[domain-knowledge]] | 비즈니스 레이블·룰 사전 확인 (코드 작성 전) |
| [[data-quality]] | 인코딩·결측·형식 preflight 스캔 |
| [[process]] | LIMIT 패턴 단계 검증 필수 |
| [[infra]] | 권한·의존성 사전 확인 |
