# 교육 진행 가이드

## 기본 흐름

1. 자신의 `edu/{교육생ID}` 브랜치를 Checkout한다.
2. `app-spec.yml`, `CLAUDE.md`, `docs/REQUIREMENTS.md`를 확인한다.
3. 요구사항을 기능 3개 이내로 작성한다.
4. Claude Code에 먼저 구현 계획과 변경 파일을 요청한다.
5. 한 번에 기능 하나만 구현한다.
6. 변경사항을 검토한다.
7. Commit과 Push를 승인한다.
8. Cloud Build 결과를 확인한다.
9. Cloud Run URL에서 화면과 기능을 확인한다.
10. 실패 로그나 화면 증상을 Claude Code에 전달한다.

## 기능 구현 요청 예시

```text
app-spec.yml과 CLAUDE.md를 먼저 읽어라.
docs/REQUIREMENTS.md의 첫 번째 기능만 구현하라.
먼저 변경 예정 파일과 구현 계획을 설명하고 내 확인을 기다려라.
```

## 빌드 실패 분석 요청 예시

```text
다음은 Cloud Build 실패 로그다.
실패 원인을 하나로 좁히고, 요구사항과 무관한 변경 없이 최소 수정안을 제시하라.
수정 후 어떤 빌드 단계에서 검증되는지도 설명하라.
```

## 금지사항

- 실제 고객정보 또는 개인정보 입력
- 다른 교육생 브랜치 수정
- main 브랜치 직접 수정
- Dockerfile, cloudbuild.yaml, IAM 임의 변경
- Secret 하드코딩
