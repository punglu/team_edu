import type { ReactNode } from "react";
import styles from "./Modal.module.css";

type ModalProps = {
  title: string;
  open: boolean;
  children: ReactNode;
  footer: ReactNode;
  onClose: () => void;
};

export function Modal({ title, open, children, footer, onClose }: ModalProps) {
  if (!open) return null;

  return (
    <div className={styles.backdrop} role="presentation">
      <section className={styles.modal} role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <header className={styles.header}>
          <h2 id="modal-title">{title}</h2>
          <button type="button" className={styles.close} onClick={onClose} aria-label="닫기">
            ×
          </button>
        </header>
        <div className={styles.body}>{children}</div>
        <footer className={styles.footer}>{footer}</footer>
      </section>
    </div>
  );
}
