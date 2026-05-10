import React, { useState, useRef, useEffect, useCallback } from "react";
import { Send, Sparkles } from "lucide-react";
import Sidebar from "../components/Sidebar";
import Message from "../components/Message";
import { sendQuery } from "../services/api";

const WELCOME = {
  role: "assistant",
  content:
    "Hello! I'm the **Alliance Fees & Policy Chatbot**. I can answer questions about fees, admission policies, courses, and more. How can I help you today?",
  sources: [],
};

let chatIdCounter = Date.now();
function newChatId() { return ++chatIdCounter; }

function newChat() {
  return { id: newChatId(), title: "", messages: [WELCOME] };
}

export default function ChatPage({ darkMode, setDarkMode }) {
  const [chats, setChats] = useState(() => [newChat()]);
  const [activeId, setActiveId] = useState(() => chats[0].id);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  const activeChat = chats.find((c) => c.id === activeId) || chats[0];

  const scrollBottom = () =>
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });

  useEffect(scrollBottom, [activeChat.messages, loading]);

  const updateChat = useCallback((id, updater) => {
    setChats((prev) => prev.map((c) => (c.id === id ? updater(c) : c)));
  }, []);

  const handleSend = async () => {
    const q = input.trim();
    if (!q || loading) return;
    setInput("");
    setLoading(true);

    const userMsg = { role: "user", content: q, sources: [] };
    updateChat(activeId, (c) => {
      const title = c.title || q.slice(0, 40);
      return { ...c, title, messages: [...c.messages, userMsg] };
    });

    try {
      const data = await sendQuery(q);
      const botMsg = {
        role: "assistant",
        content: data.answer,
        sources: data.sources || [],
      };
      updateChat(activeId, (c) => ({ ...c, messages: [...c.messages, botMsg] }));
    } catch (err) {
      const errMsg = {
        role: "assistant",
        content: "Sorry, something went wrong. Please try again.",
        sources: [],
      };
      updateChat(activeId, (c) => ({ ...c, messages: [...c.messages, errMsg] }));
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleNewChat = () => {
    const chat = newChat();
    setChats((prev) => [chat, ...prev]);
    setActiveId(chat.id);
  };

  const handleDeleteChat = (id) => {
    setChats((prev) => {
      const updated = prev.filter((c) => c.id !== id);
      if (updated.length === 0) {
        const fresh = newChat();
        setActiveId(fresh.id);
        return [fresh];
      }
      if (id === activeId) setActiveId(updated[0].id);
      return updated;
    });
  };

  const SUGGESTIONS = [
    "What are the admission criteria?",
    "Tell me about fee structure",
    "What courses are available?",
    "What are the hostel facilities?",
  ];

  return (
    <div className={`flex h-screen overflow-hidden ${darkMode ? "dark" : ""}`}>
      <Sidebar
        chats={chats}
        activeId={activeId}
        onSelect={setActiveId}
        onNew={handleNewChat}
        onDelete={handleDeleteChat}
        darkMode={darkMode}
        setDarkMode={setDarkMode}
      />

      {/* Main */}
      <div className="flex flex-col flex-1 bg-gray-50 dark:bg-gray-900 overflow-hidden">
        {/* Top bar */}
        <header className="px-6 py-3 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-primary-600" />
            <span className="font-semibold text-gray-900 dark:text-white text-sm">
              {activeChat.title || "New conversation"}
            </span>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto scrollbar-thin px-4 py-6 space-y-5">
          {activeChat.messages.map((msg, i) => (
            <Message key={i} {...msg} darkMode={darkMode} />
          ))}
          {loading && (
            <Message role="assistant" content="" isTyping darkMode={darkMode} />
          )}
          <div ref={bottomRef} />
        </div>

        {/* Suggestions (only on first message) */}
        {activeChat.messages.length === 1 && !loading && (
          <div className="px-4 pb-2 flex flex-wrap gap-2 justify-center">
            {SUGGESTIONS.map((s, i) => (
              <button
                key={i}
                onClick={() => { setInput(s); textareaRef.current?.focus(); }}
                className="text-xs bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 px-3 py-1.5 rounded-full hover:border-primary-400 hover:text-primary-600 transition"
              >
                {s}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <div className="px-4 pb-5 pt-2">
          <div className="flex items-end gap-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-2xl px-4 py-2 shadow-sm focus-within:ring-2 focus-within:ring-primary-400 transition">
            <textarea
              ref={textareaRef}
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about admissions, courses, fees…"
              className="flex-1 bg-transparent text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 resize-none focus:outline-none max-h-40 py-1.5"
              style={{ height: "auto", overflowY: "auto" }}
              onInput={(e) => {
                e.target.style.height = "auto";
                e.target.style.height = e.target.scrollHeight + "px";
              }}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || loading}
              className="shrink-0 bg-primary-600 disabled:bg-gray-300 hover:bg-primary-700 text-white p-2 rounded-xl transition"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          <p className="text-xs text-center text-gray-400 mt-2">
            Answers are based on indexed documents and websites only.
          </p>
        </div>
      </div>
    </div>
  );
}
