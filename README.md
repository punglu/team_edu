# ProjectFlow 교육용 웹 애플리케이션

영업사원 등 IT 지식이 많지 않은 교육생이 Claude Code와 대화하며 웹 애플리케이션을 수정하고, Git Push 후 Cloud Build와 Cloud Run을 통해 실제 서비스를 확인하는 교육용 공통 소스입니다.

## 기술 구성

- Frontend: React + Vite + TypeScript
- Backend: Python + FastAPI + Pydantic
- Database: Cloud Firestore
- Build: Cloud Build
- Runtime: Cloud Run
- Packaging: 프런트 빌드 결과와 FastAPI를 하나의 컨테이너로 배포

## 로컬 실행 정책

교육생 PC에서는 Node, Python, Docker, gcloud를 설치하거나 실행하지 않습니다.

```text
VSCode에서 소스 수정
→ 자신의 edu/{교육생ID} 브랜치에 Commit/Push
→ Cloud Build 자동 빌드
→ Cloud Run 자동 배포
→ 브라우저에서 결과 확인
```

## 디렉터리

```text
frontend/   React + TypeScript
backend/    FastAPI + Firestore
docs/       교육 자료
app-spec.yml 제품·화면·API SSOT
CLAUDE.md   Claude Code 작업 규칙
```

## 교육생이 주로 수정하는 위치

- `frontend/src/features/**`
- `backend/app/features/**`
- `docs/REQUIREMENTS.md`

## 임의 변경 금지

- `Dockerfile`
- `cloudbuild.yaml`
- `frontend/src/app/**`
- `frontend/src/shared/**`
- `backend/app/core/**`
- `CLAUDE.md`

## 주요 URL

- `/projects`: 프로젝트 관리 화면
- `/api/health`: 상태 확인
- `/api/projects`: 프로젝트 API
- `/docs`: FastAPI API 문서
