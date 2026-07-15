# ProjectFlow 교육용 저장소 작업 규칙

## 1. 기준 문서

- 화면, 기능, 도메인 모델, API, Firestore 구조는 루트의 `app-spec.yml`을 SSOT로 사용한다.
- 이 문서는 Claude Code의 작업 절차와 변경 규칙의 SSOT다.
- 작업 전에 현재 브랜치, 변경 상태, `app-spec.yml`과 이 문서를 먼저 확인한다.

## 2. 브랜치 규칙

- 교육생은 자신의 `edu/{교육생ID}` 브랜치에서만 작업한다.
- `main` 또는 다른 교육생 브랜치를 수정하지 않는다.
- Commit과 Push는 사용자의 명시적 승인 후 수행한다.

## 3. 구조 원칙

- 프런트엔드는 React, Vite, TypeScript를 사용한다.
- 백엔드는 Python, FastAPI, Pydantic을 사용한다.
- 기능 코드는 우선 기능 폴더에 코로케이션한다.
- 실제 재사용이 확인된 코드만 `shared`로 이동한다.
- 프런트엔드에서 Firestore에 직접 접근하지 않는다.
- 모든 데이터 접근은 `/api`를 통해 백엔드가 수행한다.
- Router, Schema, Service, Repository 책임을 섞지 않는다.
- 설정값과 업무 규칙을 여러 파일에 중복 작성하지 않는다.

## 4. 변경 제한

명시적 요청 없이 다음 파일을 변경하지 않는다.

- `Dockerfile`
- `cloudbuild.yaml`
- `frontend/src/app/**`
- `frontend/src/shared/**`
- `backend/app/core/**`
- `CLAUDE.md`

다음 행동을 금지한다.

- 요구사항과 무관한 대규모 리팩터링
- 파일 전체의 불필요한 재작성
- 신규 프레임워크 또는 대형 패키지의 무단 추가
- Secret, 실제 개인정보, 실제 고객정보 하드코딩
- Firestore Workspace를 클라이언트 요청값으로 변경
- 실행하지 않은 테스트를 PASS로 보고

## 5. 작업 절차

1. 요구사항을 한 문단으로 다시 정리한다.
2. 현재 구조를 확인한다.
3. 변경 예정 파일과 구현 계획을 설명한다.
4. 작은 단위로 구현한다.
5. 타입, 경로, import, 명백한 오류를 검토한다.
6. 가능한 테스트를 수행한다.
7. 변경 파일, 검증 결과, NOT_RUN, 잔여 위험을 보고한다.
8. 사용자의 승인을 받은 뒤 Commit과 Push를 수행한다.

## 6. 웹 중심 개발

- 교육생 PC에서는 Node, Python, Docker, gcloud 실행을 요구하지 않는다.
- 소스 수정 후 Git Push를 통해 Cloud Build에서 검증하고 배포한다.
- 빌드 실패 시 로그를 읽고 최소 범위로 수정한다.
- 성공 후 Cloud Run URL에서 화면과 기능을 검증한다.
