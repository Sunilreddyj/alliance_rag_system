import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Bot, User, ExternalLink } from "lucide-react";

function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-1">
      <span className="typing-dot w-2 h-2 bg-gray-400 rounded-full inline-block" />
      <span className="typing-dot w-2 h-2 bg-gray-400 rounded-full inline-block" />
      <span className="typing-dot w-2 h-2 bg-gray-400 rounded-full inline-block" />
    </div>
  );
}

export default function Message({ role, content, sources, isTyping, darkMode }) {
  const isUser = role === "user";

  return (
    <div className={`message-appear flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"} items-start`}>
      {/* Avatar */}
      <div
        className={`shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold
          ${isUser ? "bg-primary-600" : "bg-gray-700"}`}
      >
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>

      {/* Bubble */}
      <div className={`max-w-[75%] ${isUser ? "items-end" : "items-start"} flex flex-col gap-1`}>
        <div
          className={`px-4 py-3 rounded-2xl text-sm leading-relaxed
            ${isUser
              ? "bg-primary-600 text-white rounded-tr-sm"
              : darkMode
                ? "bg-gray-800 text-gray-100 rounded-tl-sm"
                : "bg-white text-gray-900 shadow-sm border border-gray-100 rounded-tl-sm"
            }`}
        >
          {isTyping ? (
            <TypingIndicator />
          ) : isUser ? (
            <p className="whitespace-pre-wrap">{content}</p>
          ) : (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                ul: ({ children }) => <ul className="list-disc pl-4 mb-2 space-y-1">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal pl-4 mb-2 space-y-1">{children}</ol>,
                li: ({ children }) => <li>{children}</li>,
                strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                code: ({ children }) => (
                  <code className="bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded text-xs font-mono">
                    {children}
                  </code>
                ),
              }}
            >
              {content}
            </ReactMarkdown>
          )}
        </div>

        {/* Sources */}
        {sources && sources.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-1">
            {sources.map((src, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1 text-xs bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-700 px-2 py-0.5 rounded-full"
              >
                <ExternalLink className="w-2.5 h-2.5" />
                {src.length > 40 ? src.slice(0, 40) + "…" : src}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
