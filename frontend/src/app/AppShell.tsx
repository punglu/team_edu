import type { ReactNode } from "react";
import { Sidebar } from "../shared/layout/Sidebar";
import { TopHeader } from "../shared/layout/TopHeader";
import styles from "./AppShell.module.css";

type AppShellProps = {
  children: ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <div className={styles.shell}>
      <Sidebar />
      <div className={styles.main}>
        <TopHeader />
        <main className={styles.content}>{children}</main>
      </div>
    </div>
  );
}
