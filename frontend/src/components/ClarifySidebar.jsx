import { useEffect, useRef, useState } from "react";

function renderInline(text, baseKey) {
  const segments = [];
  const regex = /(\*\*[^*]+\*\*|\*[^*]+\*)/g;
  let lastIndex = 0;
  let match;
  let i = 0;
  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      segments.push(text.substring(lastIndex, match.index));
    }
    const token = match[0];
    if (token.startsWith("**")) {
      segments.push(<strong key={`${baseKey}-${i++}`}>{token.slice(2, -2)}</strong>);
    } else {
      segments.push(<em key={`${baseKey}-${i++}`}>{token.slice(1, -1)}</em>);
    }
    lastIndex = regex.lastIndex;
  }
  if (lastIndex < text.length) segments.push(text.substring(lastIndex));
  return segments.length > 0 ? segments : [text];
}

function formatClarifyText(text) {
  if (!text) return null;
  const elements = [];
  let key = 0;

  for (const block of text.split(/\n\n+/)) {
    const lines = block.split("\n").filter((l) => l.trim());
    if (!lines.length) continue;

    const first = lines[0].trim();

    if (first.startsWith("## ") || first.startsWith("# ")) {
      const content = first.startsWith("## ") ? first.slice(3) : first.slice(2);
      elements.push(<h3 key={key++} className="clarify-heading">{renderInline(content, key)}</h3>);
    } else if (first.startsWith("- ") || first.startsWith("* ")) {
      const items = lines
        .filter((l) => /^[-*] /.test(l.trim()))
        .map((l, i) => <li key={i}>{renderInline(l.trim().slice(2), key + i)}</li>);
      elements.push(<ul key={key++}>{items}</ul>);
      key += items.length;
    } else if (/^\d+\. /.test(first)) {
      const items = lines
        .filter((l) => /^\d+\. /.test(l.trim()))
        .map((l, i) => <li key={i}>{renderInline(l.trim().replace(/^\d+\. /, ""), key + i)}</li>);
      elements.push(<ol key={key++}>{items}</ol>);
      key += items.length;
    } else {
      elements.push(<p key={key++}>{renderInline(lines.join(" "), key)}</p>);
    }
  }

  return elements.length > 0 ? elements : text;
}

export function ClarifySidebar({ isOpen, onClose, campaignId, onClarify }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const scrollRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    function handleKeyDown(e) {
      if (isOpen && e.key === "Escape") {
        onClose();
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isThinking]);

  if (!isOpen) return null;

  async function handleSubmit(e) {
    e.preventDefault();
    if (!inputValue.trim() || isThinking) return;

    const userQuery = inputValue.trim();
    setInputValue("");
    setMessages((prev) => [...prev, { role: "user", text: userQuery }]);
    setIsThinking(true);

    try {
      const result = await onClarify(campaignId, { query: userQuery });
      setMessages((prev) => [...prev, { role: "gm", text: result.explanation }]);
    } catch (error) {
      setMessages((prev) => [...prev, { role: "system", text: `Error: ${error.message}` }]);
    } finally {
      setIsThinking(false);
    }
  }

  return (
    <aside className="clarify-sidebar">
      <header className="clarify-sidebar-header">
        <div className="header-title">
          <span className="eyebrow">Utility</span>
          <h2>GM Clarify</h2>
        </div>
        <button className="close-button" onClick={onClose} title="Close sidebar">×</button>
      </header>

      <div className="clarify-sidebar-content" ref={scrollRef}>
        <div className="welcome-message">
          <p>Operative, this is a non-persisted channel. Ask for clarification on the scene, the story, or your options. This will not advance time or clocks. Press ESC or the × button to close.</p>
        </div>

        {messages.map((msg, i) => (
          <div key={i} className={`clarify-message clarify-message-${msg.role}`}>
            <span className="message-label">{msg.role.toUpperCase()}</span>
            <div className="message-text">{formatClarifyText(msg.text)}</div>
          </div>
        ))}

        {isThinking && (
          <div className="clarify-message clarify-message-gm thinking">
            <span className="message-label">GM</span>
            <div className="thinking-dots">
              <span>.</span><span>.</span><span>.</span>
            </div>
          </div>
        )}
      </div>

      <form className="clarify-sidebar-input" onSubmit={handleSubmit}>
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ask for clarification..."
          disabled={isThinking}
        />
        <button type="submit" disabled={isThinking || !inputValue.trim()}>
          →
        </button>
      </form>
    </aside>
  );
}
