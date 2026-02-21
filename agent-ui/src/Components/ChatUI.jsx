import React, { useState } from "react";

const ChatUI = () => {
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [input, setInput] = useState("");

  const onSend = () => {
    if (!input.trim()) return;
    const handleStream = async () => {
      setIsStreaming(true);
      setMessages("");

      try {
        const response = await fetch("http://localhost:8000/api/agent");
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
          const { done, delta } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(delta);
          setMessages((prev) => prev + chunk);
        }
      } catch (error) {
        console.error("Stream error:", error);
      } finally {
        setIsStreaming(false);
      }
    };
    return (
      <div className="min-h-screen bg-gradient-to-br from-zinc-950 via-zinc-900 to-zinc-950 text-zinc-100 flex items-center justify-center p-4">
        <div className="w-full max-w-4xl h-[80vh] rounded-2xl border border-zinc-800 shadow-2xl overflow-hidden bg-zinc-950/60 backdrop-blur">
          <header className="px-6 py-4 border-b border-zinc-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-600 ring-2 ring-violet-400/40" />
              <div>
                <h1 className="text-lg font-semibold">Agent Alpha</h1>
                <p className="text-xs text-zinc-400">Secure • Online</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-xs text-zinc-400">
              <span className="h-2 w-2 rounded-full bg-emerald-400" />
              <span>Live</span>
            </div>
          </header>

          <main className="h-[calc(80vh-140px)] overflow-y-auto px-6 py-5 space-y-4">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm shadow-lg border ${
                    m.role === "user"
                      ? "bg-gradient-to-br from-violet-600 to-fuchsia-600 text-white border-violet-500/30"
                      : "bg-zinc-900 text-zinc-100 border-zinc-800"
                  }`}
                >
                  <div className="whitespace-pre-wrap leading-relaxed">
                    {m.text}
                  </div>
                  <div className="mt-2 text-[10px] text-zinc-300/70 text-right">
                    {m.time}
                  </div>
                </div>
              </div>
            ))}
          </main>

          <footer className="px-6 py-4 border-t border-zinc-800 bg-zinc-950/80">
            <div className="flex items-center gap-3">
              <div className="flex-1 flex items-center gap-3 bg-zinc-900/80 border border-zinc-800 rounded-2xl px-4 py-3">
                <span className="text-zinc-500">⌘</span>
                <input
                  className="flex-1 bg-transparent outline-none text-sm placeholder:text-zinc-500"
                  placeholder="Type a message..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && onSend()}
                />
              </div>
              <button
                onClick={onSend}
                className="px-5 py-3 rounded-2xl bg-gradient-to-br from-violet-600 to-fuchsia-600 text-white text-sm font-semibold shadow-lg hover:opacity-90 transition"
              >
                Send
              </button>
            </div>
          </footer>
        </div>
      </div>
    );
  };
};
export default ChatUI;
