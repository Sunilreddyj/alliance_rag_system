import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { adminLogin } from "../services/api";
import { Lock, LogIn } from "lucide-react";

export default function LoginPage() {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await adminLogin(password);
      localStorage.setItem("admin_token", data.token);
      navigate("/admin");
    } catch (err) {
      setError(err.response?.data?.detail || "Invalid password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-900 to-primary-700 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-sm">
        <div className="flex flex-col items-center mb-6">
          <div className="bg-primary-100 p-3 rounded-full mb-3">
            <Lock className="w-7 h-7 text-primary-700" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Admin Login</h1>
          <p className="text-gray-500 text-sm mt-1">Alliance Fees &amp; Policy Chatbot</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Admin Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              required
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          {error && (
            <p className="text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary-600 hover:bg-primary-700 disabled:opacity-60 text-white font-semibold py-2.5 rounded-lg flex items-center justify-center gap-2 transition"
          >
            <LogIn className="w-4 h-4" />
            {loading ? "Signing in…" : "Sign In"}
          </button>
        </form>

        <p className="text-center mt-4 text-sm text-gray-400">
          <a href="/" className="text-primary-600 hover:underline">
            Back to Chat
          </a>
        </p>
      </div>
    </div>
  );
}
