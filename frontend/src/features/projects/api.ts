import type { Member, Project, ProjectInput } from "./types";

const API_BASE = "/api";

type ProjectResponse = {
  id: string;
  name: string;
  owner_id: string;
  owner_name: string;
  description?: string;
  status: Project["status"];
  progress: number;
  start_date: string;
  due_date: string;
  priority: Project["priority"];
  invited_member_ids: string[];
  created_at: string;
  updated_at: string;
};

type MemberResponse = {
  id: string;
  name: string;
  department?: string;
  role?: string;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    ...init,
  });

  if (!response.ok) {
    const error = (await response.json().catch(() => null)) as { message?: string } | null;
    throw new Error(error?.message ?? "요청을 처리하지 못했습니다.");
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

function toProject(response: ProjectResponse): Project {
  return {
    id: response.id,
    name: response.name,
    ownerId: response.owner_id,
    ownerName: response.owner_name,
    description: response.description,
    status: response.status,
    progress: response.progress,
    startDate: response.start_date,
    dueDate: response.due_date,
    priority: response.priority,
    invitedMemberIds: response.invited_member_ids,
    createdAt: response.created_at,
    updatedAt: response.updated_at,
  };
}

function toProjectPayload(input: ProjectInput) {
  return {
    name: input.name,
    owner_id: input.ownerId,
    owner_name: input.ownerName,
    description: input.description,
    start_date: input.startDate,
    due_date: input.dueDate,
    priority: input.priority,
    invited_member_ids: input.invitedMemberIds,
  };
}

export const projectsApi = {
  async list(): Promise<Project[]> {
    const response = await request<ProjectResponse[]>("/projects");
    return response.map(toProject);
  },
  async create(input: ProjectInput): Promise<Project> {
    const response = await request<ProjectResponse>("/projects", {
      method: "POST",
      body: JSON.stringify(toProjectPayload(input)),
    });
    return toProject(response);
  },
  async update(id: string, input: ProjectInput): Promise<Project> {
    const response = await request<ProjectResponse>(`/projects/${id}`, {
      method: "PUT",
      body: JSON.stringify(toProjectPayload(input)),
    });
    return toProject(response);
  },
  remove(id: string): Promise<void> {
    return request<void>(`/projects/${id}`, { method: "DELETE" });
  },
  async members(): Promise<Member[]> {
    const response = await request<MemberResponse[]>("/members");
    return response.map((member) => ({
      id: member.id,
      name: member.name,
      department: member.department,
      role: member.role,
    }));
  },
};
