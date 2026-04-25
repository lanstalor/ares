import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

export function ActionBar({ actions, disabled, onSelectAction, sceneTone }) {
  const [open, setOpen] = useState(false);
  const [anchor, setAnchor] = useState(null);
  const triggerRef = useRef(null);
  const popoverRef = useRef(null);

  const handleSelectAction = (prompt) => {
    onSelectAction(prompt);
    setOpen(false);
  };

  useLayoutEffect(() => {
    if (!open || !triggerRef.current) return undefined;

    function updateAnchor() {
      const rect = triggerRef.current.getBoundingClientRect();
      setAnchor({
        left: rect.left,
        bottom: window.innerHeight - rect.top + 10,
      });
    }

    updateAnchor();
    window.addEventListener("resize", updateAnchor);
    window.addEventListener("scroll", updateAnchor, true);
    return () => {
      window.removeEventListener("resize", updateAnchor);
      window.removeEventListener("scroll", updateAnchor, true);
    };
  }, [open]);

  useEffect(() => {
    if (!open) return undefined;

    function handlePointerDown(event) {
      if (triggerRef.current?.contains(event.target)) return;
      if (popoverRef.current?.contains(event.target)) return;
      setOpen(false);
    }

    function handleKeydown(event) {
      if (event.key === "Escape") {
        setOpen(false);
      }
    }

    document.addEventListener("mousedown", handlePointerDown);
    document.addEventListener("keydown", handleKeydown);
    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      document.removeEventListener("keydown", handleKeydown);
    };
  }, [open]);

  return (
    <div className={`quick-ops-control tone-${sceneTone} ${open ? "is-open" : ""}`}>
      <div className="quick-ops-terminal">
        <button
          ref={triggerRef}
          aria-expanded={open}
          aria-label="Show action ideas"
          className="quick-ops-trigger"
          disabled={disabled}
          onClick={() => setOpen((current) => !current)}
          type="button"
        >
          <span className="idea-bulb" aria-hidden="true" />
        </button>
      </div>

      {open && anchor
        ? createPortal(
            <div
              ref={popoverRef}
              className="action-grid action-grid-portal"
              role="menu"
              style={{ left: anchor.left, bottom: anchor.bottom }}
            >
              {actions.map((action) => (
                <button
                  className="action-button"
                  disabled={disabled}
                  key={action.id}
                  onClick={() => handleSelectAction(action.prompt)}
                  role="menuitem"
                  type="button"
                >
                  <span className="action-index">{action.key}</span>
                  <span className="action-icon">{action.icon}</span>
                  <span className="action-label">{action.label}</span>
                </button>
              ))}
            </div>,
            document.body,
          )
        : null}
    </div>
  );
}
