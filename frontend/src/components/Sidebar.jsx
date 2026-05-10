import React from "react";
import { MessageSquare, Shield, Sun, Moon, Trash2 } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Sidebar({ chats, activeId, onSelect, onNew, onDelete, darkMode, setDarkMode }) {
  const navigate = useNavigate();

  return (
    <aside className="flex flex-col w-64 shrink-0 bg-gray-900 text-gray-100 h-screen">
      {/* Header */}
      <div className="px-4 py-4 border-b border-gray-700">
        <h1 className="text-lg font-bold text-white leading-tight">Alliance Fees &amp; Policy</h1>
        <p className="text-xs text-gray-400 mt-0.5">Chatbot</p>
      </div>

      {/* New Chat */}
      <div className="px-3 pt-3">
        <button
          onClick={onNew}
          className="w-full bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium py-2 rounded-lg flex items-center gap-2 px-3 transition"
        >
          <MessageSquare className="w-4 h-4" />
          New Chat
        </button>
      </div>

      {/* Chat history */}
      <div className="flex-1 overflow-y-auto scrollbar-thin px-3 py-2 space-y-1">
        {chats.length === 0 && (
          <p className="text-xs text-gray-500 px-2 py-3">No conversations yet</p>
        )}
        {chats.map((chat) => (
          <div
            key={chat.id}
            onClick={() => onSelect(chat.id)}
            className={`group flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer text-sm transition ${
              chat.id === activeId
                ? "bg-gray-700 text-white"
                : "text-gray-300 hover:bg-gray-800"
            }`}
          >
            <span className="truncate flex-1">{chat.title || "New conversation"}</span>
            <button
              onClick={(e) => { e.stopPropagation(); onDelete(chat.id); }}
              className="opacity-0 group-hover:opacity-100 ml-1 text-gray-500 hover:text-red-400 transition"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>

      {/* Footer actions */}
      <div className="px-3 py-3 border-t border-gray-700 space-y-1">
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 rounded-lg transition"
        >
          {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          {darkMode ? "Light mode" : "Dark mode"}
        </button>
        <button
          onClick={() => navigate("/admin")}
          className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 rounded-lg transition"
        >
          <Shield className="w-4 h-4" />
          Admin Panel
        </button>
      </div>
    </aside>
  );
}
