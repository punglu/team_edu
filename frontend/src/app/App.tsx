import { AppShell } from "./AppShell";
import { ProjectsPage } from "../features/projects/ProjectsPage";

export function App() {
  return (
    <AppShell>
      <ProjectsPage />
    </AppShell>
  );
}
