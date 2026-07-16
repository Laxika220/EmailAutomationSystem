import { useCallback, useState } from "react";
import { fetchConversations, fetchConversation } from "../api";
import usePolling from "../hooks/usePolling";
import { MessageSquare, ChevronRight, User, Bot } from "lucide-react";
import "./Conversations.css";

export default function Conversations() {
  const getData = useCallback(() => fetchConversations(), []);
  const { data: conversations = [], loading } = usePolling(getData, 5000);
  const [selected, setSelected] = useState(null);
  const [messages, setMessages] = useState([]);

  async function handleSelect(conv) {
    setSelected(conv);
    if (conv.messages) {
      setMessages(conv.messages);
    } else {
      try {
        const data = await fetchConversation(conv.order_id);
        setMessages(data.messages || []);
      } catch {
        setMessages([]);
      }
    }
  }

  const enriched = (conversations || []).map((c) => ({
    ...c,
    message_count: c.message_count ?? (c.messages ? c.messages.length : 0),
    order_status: c.order_status || "Unknown",
  }));

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="page-content">
      <div className="page-header">
        <h2>Conversations</h2>
        <p>View full conversation threads per order</p>
      </div>

      <div className="conv-layout">
        <div className="conv-list">
          {enriched.map((c) => (
            <div
              key={c.conversation_id}
              className={`conv-item ${selected?.conversation_id === c.conversation_id ? "active" : ""}`}
              onClick={() => handleSelect(c)}
            >
              <div className="conv-item-icon">
                <MessageSquare size={18} />
              </div>
              <div className="conv-item-info">
                <div className="conv-item-header">
                  <span className="conv-order-id">{c.order_id}</span>
                  <span className={`badge badge-${c.order_status?.toLowerCase().replace(/\s/g, "-")}`}>
                    {c.order_status}
                  </span>
                </div>
                <div className="conv-item-meta">
                  {c.message_count} message{c.message_count !== 1 ? "s" : ""}
                  <ChevronRight size={14} />
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="conv-messages">
          {selected ? (
            <>
              <div className="conv-messages-header">
                <h3>{selected.order_id} - Conversation Thread</h3>
                <span className={`badge badge-${selected.order_status?.toLowerCase().replace(/\s/g, "-")}`}>
                  {selected.order_status}
                </span>
              </div>
              <div className="messages-list">
                {messages.map((m, i) => (
                  <div key={i} className={`message-bubble message-${m.direction}`}>
                    <div className="message-header">
                      <div className="message-avatar">
                        {m.direction === "incoming" ? <User size={14} /> : <Bot size={14} />}
                      </div>
                      <div className="message-info">
                        <span className="message-sender">
                          {m.sender || (m.direction === "incoming" ? "Customer" : "Elemental Concept")}
                        </span>
                        <span className="message-direction-label">
                          {m.direction === "incoming" ? "Customer Email" : "AI Reply"}
                        </span>
                      </div>
                      <span className="message-time">{m.timestamp}</span>
                    </div>
                    {m.subject && <div className="message-subject">{m.subject}</div>}
                    <div className="message-body">{m.body}</div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="conv-empty">
              <MessageSquare size={48} strokeWidth={1} />
              <p>Select a conversation to view messages</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
