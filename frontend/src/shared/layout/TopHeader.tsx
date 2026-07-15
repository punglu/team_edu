import styles from "./TopHeader.module.css";

export function TopHeader() {
  return (
    <header className={styles.header}>
      <label className={styles.search}>
        <span aria-hidden="true">⌕</span>
        <input aria-label="전체 검색" placeholder="프로젝트, 업무 검색..." />
      </label>
      <div className={styles.actions}>
        <button className={styles.iconButton} type="button" aria-label="알림">
          ♢
        </button>
        <div className={styles.user}>
          <div className={styles.avatar}>ED</div>
          <div>
            <strong>교육 사용자</strong>
            <span>edu@example.com</span>
          </div>
        </div>
      </div>
    </header>
  );
}
