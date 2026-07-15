-- ============================================================
-- PostgreSQL 교육생별 스키마 생성 스크립트
-- ============================================================
-- Cloud SQL 인스턴스: lgcns-lgeus-bliiling-dashboard:asia-northeast3:team-edu-dev
-- Database: team_edu
-- 스키마 소유자: team_edu_master
-- ============================================================

-- 1. 현재 접속 정보 확인
SELECT current_database() AS database_name,
       current_user AS current_user;

-- 2. 교육생별 스키마 생성 (총 13개)
CREATE SCHEMA IF NOT EXISTS junnyunk AUTHORIZATION team_edu_master;
CREATE SCHEMA IF NOT EXISTS kcjang7 AUTHORIZATION team_edu_master;
CREATE SCHEMA IF NOT EXISTS namss AUTHORIZATION team_edu_master;
CREATE SCHEMA IF NOT EXISTS seulki AUTHORIZATION team_edu_master;
CREATE SCHEMA IF NOT EXISTS go23 AUTHORIZATION team_edu_master;
CREATE SCHEMA IF NOT EXISTS hyungjin_moon AUTHORIZATION team_edu_master;
CREATE SCHEMA IF NOT EXISTS spy28 AUTHORIZATION team_edu_master;
CREATE SCHEMA IF NOT EXISTS hgpark05 AUTHORIZATION team_edu_master;
CREATE SCHEMA IF NOT EXISTS jsbyeon AUTHORIZATION team_edu_master;
CREATE SCHEMA IF NOT EXISTS jbyun AUTHORIZATION team_edu_master;
CREATE SCHEMA IF NOT EXISTS spjeong AUTHORIZATION team_edu_master;
CREATE SCHEMA IF NOT EXISTS bkchoi21 AUTHORIZATION team_edu_master;
CREATE SCHEMA IF NOT EXISTS mcolors AUTHORIZATION team_edu_master;

-- 3. 생성된 스키마 목록 확인
SELECT schema_name,
       schema_owner
FROM information_schema.schemata
WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'public')
ORDER BY schema_name;

-- 4. 스키마별 권한 설정
-- 각 교육생은 자신의 스키마에서만 테이블 생성 가능
GRANT USAGE ON SCHEMA junnyunk TO gcp_billing;
GRANT CREATE ON SCHEMA junnyunk TO gcp_billing;

GRANT USAGE ON SCHEMA kcjang7 TO gcp_billing;
GRANT CREATE ON SCHEMA kcjang7 TO gcp_billing;

GRANT USAGE ON SCHEMA namss TO gcp_billing;
GRANT CREATE ON SCHEMA namss TO gcp_billing;

GRANT USAGE ON SCHEMA seulki TO gcp_billing;
GRANT CREATE ON SCHEMA seulki TO gcp_billing;

GRANT USAGE ON SCHEMA go23 TO gcp_billing;
GRANT CREATE ON SCHEMA go23 TO gcp_billing;

GRANT USAGE ON SCHEMA hyungjin_moon TO gcp_billing;
GRANT CREATE ON SCHEMA hyungjin_moon TO gcp_billing;

GRANT USAGE ON SCHEMA spy28 TO gcp_billing;
GRANT CREATE ON SCHEMA spy28 TO gcp_billing;

GRANT USAGE ON SCHEMA hgpark05 TO gcp_billing;
GRANT CREATE ON SCHEMA hgpark05 TO gcp_billing;

GRANT USAGE ON SCHEMA jsbyeon TO gcp_billing;
GRANT CREATE ON SCHEMA jsbyeon TO gcp_billing;

GRANT USAGE ON SCHEMA jbyun TO gcp_billing;
GRANT CREATE ON SCHEMA jbyun TO gcp_billing;

GRANT USAGE ON SCHEMA spjeong TO gcp_billing;
GRANT CREATE ON SCHEMA spjeong TO gcp_billing;

GRANT USAGE ON SCHEMA bkchoi21 TO gcp_billing;
GRANT CREATE ON SCHEMA bkchoi21 TO gcp_billing;

GRANT USAGE ON SCHEMA mcolors TO gcp_billing;
GRANT CREATE ON SCHEMA mcolors TO gcp_billing;

-- 5. 권한 설정 확인
SELECT grantee, privilege_type
FROM information_schema.role_table_grants
WHERE table_schema IN ('junnyunk', 'kcjang7', 'namss', 'seulki', 'go23', 'hyungjin_moon',
                       'spy28', 'hgpark05', 'jsbyeon', 'jbyun', 'spjeong', 'bkchoi21', 'mcolors')
ORDER BY grantee, privilege_type;
