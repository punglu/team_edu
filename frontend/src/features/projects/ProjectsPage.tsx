import { useEffect, useMemo, useState } from "react";
import { Button } from "../../shared/components/Button";
import { ProjectFormModal } from "./ProjectFormModal";
import { projectsApi } from "./api";
import type { Member, Project, ProjectInput, ProjectStatus } from "./types";
import styles from "./ProjectsPage.module.css";

const STATUS_LABELS: Record<ProjectStatus, string> = {
  IN_PROGRESS: "진행 중",
  IN_REVIEW: "검토 중",
  ON_HOLD: "보류",
  COMPLETED: "완료",
};

export function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [keyword, setKeyword] = useState("");
  const [status, setStatus] = useState<"ALL" | ProjectStatus>("ALL");
  const [modalOpen, setModalOpen] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [projectItems, memberItems] = await Promise.all([
        projectsApi.list(),
        projectsApi.members(),
      ]);
      setProjects(projectItems);
      setMembers(memberItems);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "정보를 불러오지 못했습니다.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  const filteredProjects = useMemo(() => {
    const normalizedKeyword = keyword.trim().toLowerCase();
    return projects.filter((project) => {
      const keywordMatch =
        !normalizedKeyword ||
        project.name.toLowerCase().includes(normalizedKeyword) ||
        project.ownerName.toLowerCase().includes(normalizedKeyword);
      const statusMatch = status === "ALL" || project.status === status;
      return keywordMatch && statusMatch;
    });
  }, [keyword, projects, status]);

  const summary = useMemo(() => ({
    total: projects.length,
    completed: projects.filter((project) => project.status === "COMPLETED").length,
    active: projects.filter((project) => project.status === "IN_PROGRESS").length,
    dueSoon: projects.filter((project) => project.status !== "COMPLETED" && project.progress < 50).length,
  }), [projects]);

  function openCreate() {
    setEditingProject(null);
    setModalOpen(true);
  }

  function openEdit(project: Project) {
    setEditingProject(project);
    setModalOpen(true);
  }

  async function saveProject(input: ProjectInput) {
    setSubmitting(true);
    try {
      if (editingProject) {
        const updated = await projectsApi.update(editingProject.id, input);
        setProjects((current) =>
          current.map((project) => (project.id === updated.id ? updated : project)),
        );
      } else {
        const created = await projectsApi.create(input);
        setProjects((current) => [created, ...current]);
      }
      setModalOpen(false);
    } catch (caught) {
      window.alert(caught instanceof Error ? caught.message : "저장하지 못했습니다.");
    } finally {
      setSubmitting(false);
    }
  }

  async function removeProject(project: Project) {
    if (!window.confirm(`"${project.name}" 프로젝트를 삭제할까요?`)) return;
    try {
      await projectsApi.remove(project.id);
      setProjects((current) => current.filter((item) => item.id !== project.id));
    } catch (caught) {
      window.alert(caught instanceof Error ? caught.message : "삭제하지 못했습니다.");
    }
  }

  return (
    <section>
      <div className={styles.pageHeader}>
        <div>
          <h1>프로젝트</h1>
          <p>프로젝트 현황을 한눈에 보고 관리하세요.</p>
        </div>
        <div className={styles.headerActions}>
          <Button type="button" onClick={() => void load()}>새로고침</Button>
          <Button type="button" variant="primary" onClick={openCreate}>+ 새 프로젝트</Button>
        </div>
      </div>

      <div className={styles.kpis}>
        <KpiCard label="전체 프로젝트" value={summary.total} helper={`진행 중 ${summary.active}개`} />
        <KpiCard label="완료된 프로젝트" value={summary.completed} helper="완료 상태 기준" />
        <KpiCard label="진행 중 프로젝트" value={summary.active} helper="현재 진행 상태" />
        <KpiCard label="확인 필요" value={summary.dueSoon} helper="진행률 50% 미만" />
      </div>

      <div className={styles.toolbar}>
        <label className={styles.search}>
          <span aria-hidden="true">⌕</span>
          <input
            value={keyword}
            onChange={(event) => setKeyword(event.target.value)}
            placeholder="프로젝트명 또는 담당자 검색..."
          />
        </label>
        <select
          value={status}
          onChange={(event) => setStatus(event.target.value as "ALL" | ProjectStatus)}
          aria-label="상태 필터"
        >
          <option value="ALL">전체 상태</option>
          {Object.entries(STATUS_LABELS).map(([value, label]) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
        <Button
          type="button"
          variant="ghost"
          onClick={() => {
            setKeyword("");
            setStatus("ALL");
          }}
        >
          초기화
        </Button>
      </div>

      <div className={styles.tableCard}>
        <div className={styles.tableTitle}>
          <div>
            <h2>프로젝트 목록</h2>
            <p>총 {filteredProjects.length}개</p>
          </div>
        </div>

        {loading && <div className={styles.state}>프로젝트 목록을 불러오는 중입니다.</div>}
        {!loading && error && (
          <div className={styles.state}>
            <strong>프로젝트 정보를 불러오지 못했습니다.</strong>
            <p>{error}</p>
            <Button type="button" onClick={() => void load()}>다시 시도</Button>
          </div>
        )}
        {!loading && !error && filteredProjects.length === 0 && (
          <div className={styles.state}>
            <strong>조건에 맞는 프로젝트가 없습니다.</strong>
            <p>검색 조건을 초기화하거나 새 프로젝트를 등록하세요.</p>
          </div>
        )}

        {!loading && !error && filteredProjects.length > 0 && (
          <div className={styles.tableWrap}>
            <table>
              <thead>
                <tr>
                  <th>프로젝트명</th>
                  <th>담당자</th>
                  <th>상태</th>
                  <th>진행률</th>
                  <th>시작일</th>
                  <th>마감일</th>
                  <th>관리</th>
                </tr>
              </thead>
              <tbody>
                {filteredProjects.map((project) => (
                  <tr key={project.id}>
                    <td>
                      <strong>{project.name}</strong>
                      <span className={styles.description}>{project.description || "설명 없음"}</span>
                    </td>
                    <td>{project.ownerName}</td>
                    <td>
                      <span className={`${styles.badge} ${styles[project.status]}`}>
                        {STATUS_LABELS[project.status]}
                      </span>
                    </td>
                    <td>
                      <div className={styles.progressRow}>
                        <progress
                          className={styles.progress}
                          value={project.progress}
                          max={100}
                          aria-label={`${project.name} 진행률`}
                        />
                        <span>{project.progress}%</span>
                      </div>
                    </td>
                    <td>{project.startDate}</td>
                    <td>{project.dueDate}</td>
                    <td>
                      <div className={styles.rowActions}>
                        <Button type="button" variant="ghost" onClick={() => openEdit(project)}>수정</Button>
                        <Button type="button" variant="ghost" onClick={() => void removeProject(project)}>삭제</Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <ProjectFormModal
        open={modalOpen}
        members={members}
        project={editingProject}
        submitting={submitting}
        onClose={() => setModalOpen(false)}
        onSubmit={saveProject}
      />
    </section>
  );
}

type KpiCardProps = {
  label: string;
  value: number;
  helper: string;
};

function KpiCard({ label, value, helper }: KpiCardProps) {
  return (
    <article className={styles.kpi}>
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{helper}</p>
    </article>
  );
}
