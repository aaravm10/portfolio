// App.tsx
import { HashRouter, Route, Routes } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";
import Navbar from "./components/Navbar";
import Clubs from "./components/Clubs";
import Calendar from "./components/Calandar";
import Detail from "./components/Detail";
import Footer from "./components/Footer";
import Form from "./components/Form";
import ClubManagerDashboard from "./components/Dashboard";
import type { SchoolInfoJson } from "./components/Form";

type SchoolOption = { code: string; name: string };

const SCHOOLS: SchoolOption[] = [
  { code: "SCU", name: "Santa Clara University" },
  { code: "UCB", name: "University of California, Berkeley" },
];

function applyThemeVars(info: SchoolInfoJson) {
  const root = document.documentElement;

  root.style.setProperty("--primary", info["primary-color"]);
  root.style.setProperty("--secondary", info["secondary-color"]);
  root.style.setProperty("--accent", info["accent-color"]);

  if (info["secondary-text-color"]) {
    root.style.setProperty("--secondary-text-color", info["secondary-text-color"]);
  }
}

function loadSavedSchool(): string | null {
  try {
    return localStorage.getItem("schoolCode");
  } catch {
    return null;
  }
}

function saveSchool(code: string) {
  try {
    localStorage.setItem("schoolCode", code);
  } catch {
    // ignore
  }
}

export default function App() {
  const [schoolCode, setSchoolCode] = useState<string>(() => loadSavedSchool() || "");
  const [schoolInfo, setSchoolInfo] = useState<SchoolInfoJson | null>(null);
  const [showSchoolPicker, setShowSchoolPicker] = useState<boolean>(() => !loadSavedSchool());

  const currentSchool = useMemo(() => {
    return SCHOOLS.find((s) => s.code === schoolCode) || null;
  }, [schoolCode]);

  // Load school theme whenever school changes
  useEffect(() => {
    if (!schoolCode) return;

    fetch(`${import.meta.env.BASE_URL}/${schoolCode.toLowerCase()}/info.json`)
      .then((r) => r.json())
      .then((data: SchoolInfoJson) => {
        applyThemeVars(data);
        setSchoolInfo(data);
      })
      .catch((err) => console.error("Error fetching school info:", err));
  }, [schoolCode]);

  // Set favicon based on school
  useEffect(() => {
    if (!schoolCode) return;

    const href = `${import.meta.env.BASE_URL}/${schoolCode.toLowerCase()}/logo.png`;
    let link = document.querySelector("link[rel='icon']") as HTMLLinkElement | null;
    if (!link) {
      link = document.createElement("link");
      link.rel = "icon";
      document.head.appendChild(link);
    }
    link.href = href;
  }, [schoolCode]);

  function chooseSchool(code: string) {
    setSchoolCode(code);
    saveSchool(code);
    setShowSchoolPicker(false);
  }

  return (
    <HashRouter>
      {currentSchool && (
        <Navbar
          school={schoolCode || "Select"}
          onOpenSchoolPicker={() => setShowSchoolPicker(true)}
        />
      )}

      {showSchoolPicker && (
        <SchoolPickerModal
          schools={SCHOOLS}
          onClose={() => {
            if (schoolCode) setShowSchoolPicker(false);
          }}
          onSelect={chooseSchool}
          canClose={!!schoolCode}
        />
      )}

      {currentSchool && (
        <>
          <Routes>
            <Route path="/" element={<Clubs school={currentSchool.code} />} />
            <Route path="/clubs" element={<Clubs school={currentSchool.code} />} />
            <Route path="/clubs/:id" element={<Detail school={currentSchool.code} />} />
            <Route path="/calendar" element={<Calendar school={currentSchool.code} />} />
            <Route
              path="/apply"
              element={
                schoolInfo ? (
                  <Form school={currentSchool.code} info={schoolInfo} />
                ) : null
              }
            />
            <Route
              path="/admin"
              element={<ClubManagerDashboard school={currentSchool.code} />}
            />
          </Routes>

          <Footer school={currentSchool.code} />
        </>
      )}
    </HashRouter>
  );
}

function SchoolPickerModal({
  schools,
  onSelect,
  onClose,
  canClose,
}: {
  schools: SchoolOption[];
  onSelect: (code: string) => void;
  onClose: () => void;
  canClose: boolean;
}) {
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return schools;
    return schools.filter((s) => {
      const a = s.code.toLowerCase();
      const b = s.name.toLowerCase();
      return a.includes(q) || b.includes(q);
    });
  }, [query, schools]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center px-4"
      role="dialog"
      aria-modal="true"
      aria-label="Select your school"
    >
      <div className="absolute inset-0 bg-black/40" onClick={() => (canClose ? onClose() : null)} />

      <div className="relative w-full max-w-md rounded-lg bg-white shadow-xl border border-gray-200">
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="text-base font-bold text-gray-900">Select your school</div>
          <button
            type="button"
            className="h-9 w-9 inline-flex items-center justify-center rounded-md hover:bg-gray-100"
            onClick={() => (canClose ? onClose() : null)}
            aria-label="Close"
            disabled={!canClose}
          >
            <span aria-hidden="true">×</span>
          </button>
        </div>

        <div className="p-4">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by name or code (e.g., SCU)"
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black/10"
          />

          <div className="mt-3 max-h-72 overflow-auto rounded-md border border-gray-200">
            {filtered.length === 0 ? (
              <div className="p-3 text-sm text-gray-600">No matches.</div>
            ) : (
              filtered.map((s) => (
                <button
                  key={s.code}
                  type="button"
                  onClick={() => onSelect(s.code)}
                  className="w-full text-left px-3 py-2 hover:bg-gray-50 flex items-center justify-between"
                >
                  <div className="min-w-0">
                    <div className="text-sm font-semibold text-gray-900 truncate">{s.name}</div>
                    <div className="text-xs text-gray-600">{s.code}</div>
                  </div>
                  <span className="text-gray-400" aria-hidden="true">
                    →
                  </span>
                </button>
              ))
            )}
          </div>

          {!canClose && (
            <div className="mt-3 text-xs text-gray-600">
              Choose a school to continue.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}