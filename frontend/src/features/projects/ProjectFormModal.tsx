import { useEffect, useState } from "react";
import { Button } from "../../shared/components/Button";
import { Modal } from "../../shared/components/Modal";
import type { Member, Project, ProjectInput, ProjectPriority } from "./types";
import styles from "./ProjectFormModal.module.css";

type ProjectFormModalProps = {
  open: boolean;
  members: Member[];
  project?: Project | null;
  submitting: boolean;
  onClose: () => void;
  onSubmit: (input: ProjectInput) => Promise<void>;
};

const EMPTY_FORM: ProjectInput = {
  name: "",
  ownerId: "",
  ownerName: "",
  description: "",
  startDate: "",
  dueDate: "",
  priority: "MEDIUM",
  invitedMemberIds: [],
};

export function ProjectFormModal({
  open,
  members,
  project,
  submitting,
  onClose,
  onSubmit,
}: ProjectFormModalProps) {
  const [form, setForm] = useState<ProjectInput>(EMPTY_FORM);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!open) return;
    if (project) {
      setForm({
        name: project.name,
        ownerId: project.ownerId,
        ownerName: project.ownerName,
        description: project.description ?? "",
        startDate: project.startDate,
        dueDate: project.dueDate,
        priority: project.priority,
        invitedMemberIds: project.invitedMemberIds,
      });
    } else {
      setForm(EMPTY_FORM);
    }
    setError("");
  }, [open, project]);

  async function submit() {
    if (!form.name.trim()) {
      setError("프로젝트명을 입력하세요.");
      return;
    }
    if (!form.ownerId) {
      setError("담당자를 선택하세요.");
      return;
    }
    if (!form.startDate || !form.dueDate) {
      setError("시작일과 마감일을 입력하세요.");
      return;
    }
    if (form.dueDate < form.startDate) {
      setError("마감일은 시작일보다 빠를 수 없습니다.");
      return;
    }
    await onSubmit(form);
  }

  return (
    <Modal
      title={project ? "프로젝트 수정" : "새 프로젝트 등록"}
      open={open}
      onClose={onClose}
      footer={
        <>
          <Button type="button" onClick={onClose}>취소</Button>
          <Button type="button" variant="primary" onClick={submit} disabled={submitting}>
            {submitting ? "저장 중..." : project ? "변경사항 저장" : "저장"}
          </Button>
        </>
      }
    >
      <div className={styles.grid}>
        <label className={styles.full}>
          <span>프로젝트명 *</span>
          <input
            value={form.name}
            onChange={(event) => setForm({ ...form, name: event.target.value })}
            maxLength={100}
          />
        </label>

        <label>
          <span>담당자 *</span>
          <select
            value={form.ownerId}
            onChange={(event) => {
              const member = members.find((item) => item.id === event.target.value);
              setForm({
                ...form,
                ownerId: event.target.value,
                ownerName: member?.name ?? "",
              });
            }}
          >
            <option value="">선택하세요</option>
            {members.map((member) => (
              <option key={member.id} value={member.id}>{member.name}</option>
            ))}
          </select>
        </label>

        <label>
          <span>우선순위</span>
          <select
            value={form.priority}
            onChange={(event) =>
              setForm({ ...form, priority: event.target.value as ProjectPriority })
            }
          >
            <option value="LOW">낮음</option>
            <option value="MEDIUM">보통</option>
            <option value="HIGH">높음</option>
          </select>
        </label>

        <label>
          <span>시작일 *</span>
          <input
            type="date"
            value={form.startDate}
            onChange={(event) => setForm({ ...form, startDate: event.target.value })}
          />
        </label>

        <label>
          <span>마감일 *</span>
          <input
            type="date"
            value={form.dueDate}
            onChange={(event) => setForm({ ...form, dueDate: event.target.value })}
          />
        </label>

        <label className={styles.full}>
          <span>설명</span>
          <textarea
            rows={5}
            value={form.description}
            onChange={(event) => setForm({ ...form, description: event.target.value })}
            maxLength={1000}
          />
        </label>

        {error && <p className={styles.error}>{error}</p>}
      </div>
    </Modal>
  );
}
