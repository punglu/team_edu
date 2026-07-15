import styles from "./Sidebar.module.css";

const items = [
  ["대시보드", "⌂"],
  ["프로젝트", "▣"],
  ["업무", "✓"],
  ["캘린더", "□"],
  ["보고서", "▤"],
  ["팀원", "♙"],
];

export function Sidebar() {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.brand}>
        <div className={styles.logo}>P</div>
        <div>
          <strong>ProjectFlow</strong>
          <span>Education</span>
        </div>
      </div>

      <nav className={styles.nav} aria-label="주 메뉴">
        {items.map(([label, icon]) => (
          <button
            key={label}
            className={`${styles.item} ${label === "프로젝트" ? styles.active : ""}`}
            type="button"
          >
            <span aria-hidden="true">{icon}</span>
            <span>{label}</span>
          </button>
        ))}
      </nav>

      <button className={styles.settings} type="button">
        <span aria-hidden="true">⚙</span>
        <span>설정</span>
      </button>
    </aside>
  );
}
