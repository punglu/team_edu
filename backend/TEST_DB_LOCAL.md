# 로컬 Cloud SQL 연결 테스트 가이드

## 현재 설정
- **데이터베이스**: PostgreSQL
- **접속 방식**: Cloud SQL Proxy (Unix socket)
- **연결 문자열**: 
  ```
  postgresql://gcp_billing:Cns22329!!@/team_edu?host=/cloudsql/lgcns-lgeus-bliiling-dashboard:asia-northeast3:team_edu
  ```

## 로컬 테스트 방법

### 1단계: Cloud SQL Proxy 설치 및 실행

```bash
# 1) Proxy 다운로드 (이미 설치되어 있으면 스킵)
# macOS
wget https://dl.google.com/cloudsql/cloud_sql_proxy.mac.amd64 -O cloud_sql_proxy
chmod +x cloud_sql_proxy

# 2) Proxy 실행 (별도 터미널에서)
./cloud_sql_proxy -instances=lgcns-lgeus-bliiling-dashboard:asia-northeast3:team_edu_dev=tcp:5432 -verbose
```

이 명령어는:
- TCP 포트 5432에서 Cloud SQL 인스턴스로 연결을 터널링합니다
- gcloud auth 설정이 필요합니다

### 2단계: 연결 문자열 수정 (로컬 테스트용)

`.env` 파일에서:
```env
# 원본 (Cloud SQL Proxy Unix socket)
DATABASE_URL=postgresql://gcp_billing:Cns22329!!@/team_edu?host=/cloudsql/lgcns-lgeus-bliiling-dashboard:asia-northeast3:team_edu

# 로컬 테스트용 (TCP localhost)
DATABASE_URL=postgresql://gcp_billing:Cns22329!!@localhost:5432/team_edu
```

### 3단계: 파이썬 환경 설정 및 테스트

```bash
cd backend

# 가상환경 생성 (선택)
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 연결 테스트
python3 test_db_connection.py
```

## 예상 결과

✅ **성공**
```
============================================================
Cloud SQL Connection Test
============================================================

Configuration:
  DATABASE_URL: postgresql://gcp_billing:***@localhost:5432/team_edu
  ...

Test Result:
  status: ok
  message: Cloud SQL connection successful

✅ Connection successful!
```

❌ **실패**
```
Test Result:
  status: error
  message: could not connect to server: No such file or directory
```

## 문제 해결

| 증상 | 원인 | 해결책 |
|------|------|--------|
| `could not connect to server` | Proxy 미실행 | Proxy를 먼저 실행하세요 |
| `authentication failed` | 잘못된 사용자명/비밀번호 | `.env` 파일의 자격증명 확인 |
| `database does not exist` | 잘못된 DB 이름 | DB 이름 확인: `team_edu` |
| `gcloud auth error` | 인증 미설정 | `gcloud auth login` 실행 |

## Cloud Build 배포 후

`.env` 파일은 **Git에 커밋하지 마세요** (.gitignore에 추가)

Cloud Run 배포 시 환경 변수는:
```yaml
--set-secrets="DATABASE_URL=team_edu_db_url:latest"
```

이 설정으로 자동 주입됩니다.
