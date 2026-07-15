export type ProjectStatus = "IN_PROGRESS" | "IN_REVIEW" | "ON_HOLD" | "COMPLETED";
export type ProjectPriority = "LOW" | "MEDIUM" | "HIGH";

export type Project = {
  id: string;
  name: string;
  ownerId: string;
  ownerName: string;
  description?: string;
  status: ProjectStatus;
  progress: number;
  startDate: string;
  dueDate: string;
  priority: ProjectPriority;
  invitedMemberIds: string[];
  createdAt: string;
  updatedAt: string;
};

export type ProjectInput = {
  name: string;
  ownerId: string;
  ownerName: string;
  description?: string;
  startDate: string;
  dueDate: string;
  priority: ProjectPriority;
  invitedMemberIds: string[];
};

export type Member = {
  id: string;
  name: string;
  department?: string;
  role?: string;
};
