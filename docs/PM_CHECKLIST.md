# PM 구축·운영 체크리스트

## 저장소

- [ ] main 기준 공통 소스 검토
- [ ] 교육생별 `edu/{ID}` 브랜치 생성
- [ ] main 브랜치 보호
- [ ] 교육생별 GitHub 접근 권한 확인

## GCP

- [ ] 교육용 GCP 프로젝트
- [ ] Billing 연결 및 예산 알림
- [ ] Cloud Build API
- [ ] Cloud Run API
- [ ] Artifact Registry API
- [ ] Firestore API
- [ ] Artifact Registry 저장소
- [ ] Cloud Build 배포 서비스 계정
- [ ] Cloud Run 런타임 서비스 계정
- [ ] Firestore 접근 권한
- [ ] Cloud Build Trigger (`^edu/[a-z0-9][a-z0-9_-]*$`)

## 파일럿

- [ ] 테스트 브랜치 Push
- [ ] TypeScript 검사
- [ ] 프런트 빌드
- [ ] 백엔드 테스트
- [ ] 이미지 빌드 및 Push
- [ ] Cloud Run 배포
- [ ] `/api/health`
- [ ] 프로젝트 CRUD
- [ ] Firestore Workspace 분리
- [ ] 실패 시 기존 정상 Revision 유지
