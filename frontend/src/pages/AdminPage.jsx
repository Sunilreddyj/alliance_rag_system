import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import {
  UploadCloud, Globe, FileSpreadsheet, FileText, Trash2,
  LogOut, RefreshCw, CheckCircle, XCircle, Loader, Shield,
  BarChart2, ChevronDown, ChevronUp, Sun, Moon
} from "lucide-react";
import {
  uploadPDF, uploadExcel, indexWebsite,
  listPDFs, listExcels, listWebsites,
  deletePDF, deleteExcel, deleteWebsite,
  getStats, clearCollection,
} from "../services/api";

function StatusBadge({ status, message }) {
  const map = {
    indexed: { color: "bg-green-100 text-green-700", icon: <CheckCircle className="w-3.5 h-3.5" /> },
    error:   { color: "bg-red-100 text-red-700",   icon: <XCircle className="w-3.5 h-3.5" /> },
    skipped: { color: "bg-yellow-100 text-yellow-700", icon: <XCircle className="w-3.5 h-3.5" /> },
  };
  const s = map[status] || { color: "bg-gray-100 text-gray-600", icon: null };
  return (
    <span className={`inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full ${s.color}`}>
      {s.icon}{message || status}
    </span>
  );
}

function Section({ title, icon, children, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      <button
        className="w-full flex items-center justify-between px-5 py-4 text-left font-semibold text-gray-800 dark:text-white hover:bg-gray-50 dark:hover:bg-gray-750 transition"
        onClick={() => setOpen(!open)}
      >
        <span className="flex items-center gap-2">{icon}{title}</span>
        {open ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>
      {open && <div className="px-5 pb-5 pt-1">{children}</div>}
    </div>
  );
}

export default function AdminPage({ darkMode, setDarkMode }) {
  const navigate = useNavigate();
  const pdfRef = useRef(null);
  const excelRef = useRef(null);

  const [stats, setStats] = useState({});
  const [pdfs, setPdfs] = useState([]);
  const [excels, setExcels] = useState([]);
  const [websites, setWebsites] = useState([]);
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [includePdfs, setIncludePdfs] = useState(true);

  const [uploading, setUploading] = useState(false);
  const [indexing, setIndexing] = useState(false);
  const [messages, setMessages] = useState([]);

  const addMsg = (type, text) =>
    setMessages((prev) => [{ type, text, id: Date.now() }, ...prev].slice(0, 20));

  const loadAll = async () => {
    try {
      const [s, p, e, w] = await Promise.all([getStats(), listPDFs(), listExcels(), listWebsites()]);
      setStats(s);
      setPdfs(p.files || []);
      setExcels(e.files || []);
      setWebsites(w.sites || []);
    } catch {}
  };

  useEffect(() => { loadAll(); }, []);

  const handleLogout = () => {
    localStorage.removeItem("admin_token");
    navigate("/admin/login");
  };

  // PDF upload
  const handlePdfUpload = async (e) => {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;
    setUploading(true);
    for (const file of files) {
      try {
        const r = await uploadPDF(file);
        addMsg("success", `${r.filename}: ${r.chunks} chunks indexed`);
      } catch (err) {
        addMsg("error", `PDF upload failed: ${err.response?.data?.detail || err.message}`);
      }
    }
    setUploading(false);
    loadAll();
  };

  // Excel upload
  const handleExcelUpload = async (e) => {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;
    setUploading(true);
    for (const file of files) {
      try {
        const r = await uploadExcel(file);
        addMsg("success", `${r.filename}: ${r.chunks} chunks indexed`);
      } catch (err) {
        addMsg("error", `Excel upload failed: ${err.response?.data?.detail || err.message}`);
      }
    }
    setUploading(false);
    loadAll();
  };

  // Website indexing
  const handleIndexWebsite = async () => {
    const url = websiteUrl.trim();
    if (!url) return;
    setIndexing(true);
    try {
      const r = await indexWebsite(url, includePdfs);
      addMsg("success", `${url}: ${r.page_chunks} page chunks + ${r.pdf_chunks} PDF chunks`);
      setWebsiteUrl("");
    } catch (err) {
      addMsg("error", `Website indexing failed: ${err.response?.data?.detail || err.message}`);
    }
    setIndexing(false);
    loadAll();
  };

  const handleDeletePdf = async (name) => {
    try {
      await deletePDF(name);
      addMsg("success", `Deleted PDF: ${name}`);
      loadAll();
    } catch { addMsg("error", `Failed to delete ${name}`); }
  };

  const handleDeleteExcel = async (name) => {
    try {
      await deleteExcel(name);
      addMsg("success", `Deleted Excel: ${name}`);
      loadAll();
    } catch { addMsg("error", `Failed to delete ${name}`); }
  };

  const handleDeleteWebsite = async (url) => {
    try {
      await deleteWebsite(url);
      addMsg("success", `Deleted website: ${url}`);
      loadAll();
    } catch { addMsg("error", `Failed to delete website`); }
  };

  const handleClearCollection = async (name) => {
    if (!window.confirm(`Clear all ${name} data?`)) return;
    try {
      const r = await clearCollection(name);
      addMsg("success", `Cleared ${name}: ${r.chunks_removed} chunks removed`);
      loadAll();
    } catch { addMsg("error", `Clear failed`); }
  };

  return (
    <div className={`min-h-screen bg-gray-50 dark:bg-gray-900 ${darkMode ? "dark" : ""}`}>
      {/* Topbar */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-3 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-primary-600" />
          <h1 className="font-bold text-gray-900 dark:text-white">Admin Panel</h1>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => setDarkMode(!darkMode)} className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition">
            {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
          <button onClick={loadAll} className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition">
            <RefreshCw className="w-4 h-4" />
          </button>
          <a href="/" className="text-sm text-primary-600 hover:underline px-2">Chat</a>
          <button onClick={handleLogout} className="flex items-center gap-1 text-sm text-red-500 hover:text-red-700 transition">
            <LogOut className="w-4 h-4" />Logout
          </button>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-6 space-y-5">
        {/* Stats */}
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: "PDF Chunks", key: "pdf_documents", color: "text-blue-600" },
            { label: "Excel Chunks", key: "excel_documents", color: "text-green-600" },
            { label: "Website Chunks", key: "website_documents", color: "text-purple-600" },
          ].map(({ label, key, color }) => (
            <div key={key} className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 text-center">
              <p className={`text-3xl font-bold ${color}`}>{stats[key] ?? "—"}</p>
              <p className="text-xs text-gray-500 mt-1">{label}</p>
            </div>
          ))}
        </div>

        {/* Activity log */}
        {messages.length > 0 && (
          <div className="space-y-1">
            {messages.slice(0, 5).map((m) => (
              <div
                key={m.id}
                className={`text-xs px-3 py-2 rounded-lg ${m.type === "error" ? "bg-red-50 text-red-700 border border-red-200" : "bg-green-50 text-green-700 border border-green-200"}`}
              >
                {m.text}
              </div>
            ))}
          </div>
        )}

        {/* PDF Section */}
        <Section title="PDF Documents" icon={<FileText className="w-4 h-4 text-blue-600" />}>
          <div className="space-y-3">
            <div className="flex gap-2">
              <button
                onClick={() => pdfRef.current?.click()}
                disabled={uploading}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-sm font-medium px-4 py-2 rounded-lg transition"
              >
                {uploading ? <Loader className="w-4 h-4 animate-spin" /> : <UploadCloud className="w-4 h-4" />}
                Upload PDFs
              </button>
              <input ref={pdfRef} type="file" accept=".pdf" multiple className="hidden" onChange={handlePdfUpload} />
              <button
                onClick={() => handleClearCollection("pdf")}
                className="flex items-center gap-1 text-sm text-red-500 hover:text-red-700 border border-red-200 px-3 py-2 rounded-lg transition"
              >
                <Trash2 className="w-3.5 h-3.5" />Clear all
              </button>
            </div>
            {pdfs.length === 0 ? (
              <p className="text-sm text-gray-400">No PDFs indexed yet.</p>
            ) : (
              <ul className="divide-y divide-gray-100 dark:divide-gray-700 text-sm">
                {pdfs.map((f) => (
                  <li key={f} className="flex items-center justify-between py-2">
                    <span className="text-gray-700 dark:text-gray-300 truncate">{f}</span>
                    <button onClick={() => handleDeletePdf(f)} className="text-red-400 hover:text-red-600 ml-2">
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </Section>

        {/* Excel Section */}
        <Section title="Excel / CSV Files" icon={<FileSpreadsheet className="w-4 h-4 text-green-600" />}>
          <div className="space-y-3">
            <div className="flex gap-2">
              <button
                onClick={() => excelRef.current?.click()}
                disabled={uploading}
                className="flex items-center gap-2 bg-green-600 hover:bg-green-700 disabled:opacity-60 text-white text-sm font-medium px-4 py-2 rounded-lg transition"
              >
                {uploading ? <Loader className="w-4 h-4 animate-spin" /> : <UploadCloud className="w-4 h-4" />}
                Upload Excel / CSV
              </button>
              <input ref={excelRef} type="file" accept=".xlsx,.xls,.csv" multiple className="hidden" onChange={handleExcelUpload} />
              <button
                onClick={() => handleClearCollection("excel")}
                className="flex items-center gap-1 text-sm text-red-500 hover:text-red-700 border border-red-200 px-3 py-2 rounded-lg transition"
              >
                <Trash2 className="w-3.5 h-3.5" />Clear all
              </button>
            </div>
            {excels.length === 0 ? (
              <p className="text-sm text-gray-400">No Excel/CSV files indexed yet.</p>
            ) : (
              <ul className="divide-y divide-gray-100 dark:divide-gray-700 text-sm">
                {excels.map((f) => (
                  <li key={f} className="flex items-center justify-between py-2">
                    <span className="text-gray-700 dark:text-gray-300 truncate">{f}</span>
                    <button onClick={() => handleDeleteExcel(f)} className="text-red-400 hover:text-red-600 ml-2">
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </Section>

        {/* Website Section */}
        <Section title="Websites" icon={<Globe className="w-4 h-4 text-purple-600" />}>
          <div className="space-y-3">
            <div className="flex gap-2">
              <input
                type="url"
                value={websiteUrl}
                onChange={(e) => setWebsiteUrl(e.target.value)}
                placeholder="https://example.com/page"
                className="flex-1 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-400"
              />
              <button
                onClick={handleIndexWebsite}
                disabled={indexing || !websiteUrl.trim()}
                className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-60 text-white text-sm font-medium px-4 py-2 rounded-lg transition"
              >
                {indexing ? <Loader className="w-4 h-4 animate-spin" /> : <Globe className="w-4 h-4" />}
                Index
              </button>
            </div>
            <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
              <input
                type="checkbox"
                checked={includePdfs}
                onChange={(e) => setIncludePdfs(e.target.checked)}
                className="rounded"
              />
              Also download and index linked PDFs
            </label>
            <div className="flex gap-2">
              <button
                onClick={() => handleClearCollection("website")}
                className="flex items-center gap-1 text-sm text-red-500 hover:text-red-700 border border-red-200 px-3 py-2 rounded-lg transition"
              >
                <Trash2 className="w-3.5 h-3.5" />Clear all websites
              </button>
            </div>
            {websites.length === 0 ? (
              <p className="text-sm text-gray-400">No websites indexed yet.</p>
            ) : (
              <ul className="divide-y divide-gray-100 dark:divide-gray-700 text-sm">
                {websites.map((w, i) => (
                  <li key={i} className="flex items-center justify-between py-2">
                    <span className="text-gray-700 dark:text-gray-300 truncate text-xs">{w.url}</span>
                    <button onClick={() => handleDeleteWebsite(w.url)} className="text-red-400 hover:text-red-600 ml-2">
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </Section>
      </div>
    </div>
  );
}
