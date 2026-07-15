import type { Member, Project, ProjectInput } from "./types";

const API_BASE = "/api";

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

export const projectsApi = {
  list(): Promise<Project[]> {
    return request<Project[]>("/projects");
  },
  create(input: ProjectInput): Promise<Project> {
    return request<Project>("/projects", {
      method: "POST",
      body: JSON.stringify(input),
    });
  },
  update(id: string, input: ProjectInput): Promise<Project> {
    return request<Project>(`/projects/${id}`, {
      method: "PUT",
      body: JSON.stringify(input),
    });
  },
  remove(id: string): Promise<void> {
    return request<void>(`/projects/${id}`, { method: "DELETE" });
  },
  members(): Promise<Member[]> {
    return request<Member[]>("/members");
  },
};
