import { useState, useEffect, useMemo, useRef } from "react";
import { capitalizeWords } from "./helper";
import { Link } from "react-router";
import type { SchoolInfoJson } from "./Form";

export interface Club {
  id?: number;
  name: string;
  abbreviation: string;
  description: string;
  tags: string[];
  majors: string[];
  commitment: string;
  color?: string;
  members?: number;
}

export default function Clubs({ school }: { school: string }) {
  const [clubs, setClubs] = useState<Club[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [commitments, setCommitments] = useState<string[]>([]);
  const [majors, setMajors] = useState<string[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<Set<string>>(new Set());
  const [selectedCommitments, setSelectedCommitments] = useState<Set<string>>(new Set());
  const [selectedMajors, setSelectedMajors] = useState<Set<string>>(new Set());
  const [searchQuery, setSearchQuery] = useState("");
  const [slogan, setSlogan] = useState("");

  // mobile filter drawer
  const [isFiltersOpen, setIsFiltersOpen] = useState(false);
  const filterPanelRef = useRef<HTMLDivElement | null>(null);

  // close on escape / click outside (mobile drawer)
  useEffect(() => {
    if (!isFiltersOpen) return;

    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setIsFiltersOpen(false);
    };

    const onPointerDown = (e: MouseEvent | TouchEvent) => {
      const target = e.target as Node | null;
      if (filterPanelRef.current && target && !filterPanelRef.current.contains(target)) {
        setIsFiltersOpen(false);
      }
    };

    document.addEventListener("keydown", onKeyDown);
    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("touchstart", onPointerDown, { passive: true });

    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("touchstart", onPointerDown);
    };
  }, [isFiltersOpen]);

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}/${school.toLowerCase()}/clubs.json`)
      .then((response) => response.json())
      .then((data) => {
        setClubs(data);

        const uniqueCategories = Array.from(new Set(data.flatMap((club: Club) => club.tags))) as string[];
        const uniqueCommitments = Array.from(new Set(data.map((club: Club) => club.commitment))) as string[];
        const uniqueMajors = Array.from(new Set(data.flatMap((club: Club) => club.majors))) as string[];

        setCategories(uniqueCategories.sort());
        setCommitments(uniqueCommitments.sort());
        setMajors(uniqueMajors.sort());

        // Reset filters when school changes
        setSelectedCategories(new Set());
        setSelectedCommitments(new Set());
        setSelectedMajors(new Set());
        setIsFiltersOpen(false);
        setSearchQuery("");
      })
      .catch((error) => console.error("Error fetching clubs data:", error));
  }, [school]);

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}/${school.toLowerCase()}/info.json`)
      .then((response) => response.json())
      .then((data: SchoolInfoJson) => {
        setSlogan(data.slogan || "");
      })
      .catch((error) => console.error("Error fetching school info:", error));
  }, [school]);

  const handleCheckboxChange = (
    value: string,
    set: Set<string>,
    setter: (s: Set<string>) => void
  ) => {
    const newSet = new Set(set);
    if (newSet.has(value)) newSet.delete(value);
    else newSet.add(value);
    setter(newSet);
  };

  const hasActiveFilters = useMemo(() => {
    return selectedCategories.size > 0 || selectedCommitments.size > 0 || selectedMajors.size > 0;
  }, [selectedCategories, selectedCommitments, selectedMajors]);

  const clearAll = () => {
    setSelectedCategories(new Set());
    setSelectedCommitments(new Set());
    setSelectedMajors(new Set());
  };

  const filteredClubs = clubs.filter((club) => {
    const matchesCategory = selectedCategories.size === 0 || club.tags.some((tag) => selectedCategories.has(tag));
    const matchesCommitment = selectedCommitments.size === 0 || selectedCommitments.has(club.commitment);
    const matchesMajor = selectedMajors.size === 0 || club.majors.some((major) => selectedMajors.has(major));
    const query = searchQuery.trim().toLowerCase();
    const matchesSearch =
      !query ||
      [
        club.name,
        club.abbreviation,
        club.commitment,
        club.tags.join(" "),
        club.majors.join(" "),
      ]
        .join(" ")
        .toLowerCase()
        .includes(query);
    return matchesCategory && matchesCommitment && matchesMajor && matchesSearch;
  });
  console.log(import.meta.env.BASE_URL);
  return (
    <div className="flex flex-col md:flex-row gap-6 md:gap-8 p-4 md:p-8">
      {/* Mobile filters button */}
      <div className="md:hidden flex items-center justify-between gap-3">
        <button
          type="button"
          onClick={() => setIsFiltersOpen(true)}
          className="inline-flex items-center gap-2 rounded-md border border-gray-300 bg-white px-3 py-2 text-sm font-semibold text-gray-900 hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-100 dark:hover:bg-gray-700"
        >
          Filters
          {hasActiveFilters && (
            <span className="ml-1 inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-primary px-1 text-xs font-bold text-white">
              {selectedCategories.size + selectedCommitments.size + selectedMajors.size}
            </span>
          )}
        </button>

        {hasActiveFilters && (
          <button
            type="button"
            onClick={clearAll}
            className="text-sm font-semibold text-gray-700 underline underline-offset-2 dark:text-gray-300"
          >
            Clear
          </button>
        )}
      </div>

      {/* Desktop filters sidebar */}
      <div className="hidden md:block w-full md:max-w-[260px]">
        <FilterPanel
          categories={categories}
          commitments={commitments}
          majors={majors}
          selectedCategories={selectedCategories}
          selectedCommitments={selectedCommitments}
          selectedMajors={selectedMajors}
          onToggleCategory={(v) => handleCheckboxChange(v, selectedCategories, setSelectedCategories)}
          onToggleCommitment={(v) => handleCheckboxChange(v, selectedCommitments, setSelectedCommitments)}
          onToggleMajor={(v) => handleCheckboxChange(v, selectedMajors, setSelectedMajors)}
          onClearAll={clearAll}
          showClear={hasActiveFilters}
        />
      </div>

      {/* Mobile filters drawer */}
      {isFiltersOpen && (
        <div className="md:hidden fixed inset-0 z-50">
          <div className="absolute inset-0 bg-black/40" />
          <div
            ref={filterPanelRef}
            className="absolute left-0 top-0 h-full w-[85%] max-w-sm bg-white dark:bg-gray-900 shadow-xl flex flex-col"
            role="dialog"
            aria-modal="true"
            aria-label="Filters"
          >
            <div className="flex items-center justify-between border-b border-gray-200 p-4">
              <div className="text-base font-bold text-gray-900 dark:text-gray-100">Filters</div>
              <button
                type="button"
                onClick={() => setIsFiltersOpen(false)}
                className="h-9 w-9 inline-flex items-center justify-center rounded-md hover:bg-gray-100 dark:hover:bg-gray-800"
                aria-label="Close filters"
              >
                <span aria-hidden="true">×</span>
              </button>
            </div>

            <div className="p-4 overflow-y-auto">
              <FilterPanel
                categories={categories}
                commitments={commitments}
                majors={majors}
                selectedCategories={selectedCategories}
                selectedCommitments={selectedCommitments}
                selectedMajors={selectedMajors}
                onToggleCategory={(v) => handleCheckboxChange(v, selectedCategories, setSelectedCategories)}
                onToggleCommitment={(v) => handleCheckboxChange(v, selectedCommitments, setSelectedCommitments)}
                onToggleMajor={(v) => handleCheckboxChange(v, selectedMajors, setSelectedMajors)}
                onClearAll={clearAll}
                showClear={hasActiveFilters}
              />
            </div>

            <div className="border-t border-gray-200 p-4 flex gap-2">
              {hasActiveFilters && (
                <button
                  type="button"
                  onClick={clearAll}
                  className="flex-1 rounded-md border border-gray-300 bg-white dark:bg-gray-800 px-3 py-2 text-sm font-semibold text-gray-900 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  Clear all
                </button>
              )}
              <button
                type="button"
                onClick={() => setIsFiltersOpen(false)}
                className="flex-1 rounded-md bg-primary px-3 py-2 text-sm font-semibold text-white hover:bg-primary/90"
              >
                Apply
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="flex flex-col gap-4 w-full">
        <div className="w-full flex flex-col items-center text-center gap-3">
          <div className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-gray-100">{slogan || "Find your people. Get involved."}</div>
          <div className="w-full max-w-2xl">
            <div className="flex items-center gap-2 rounded-full border border-gray-300 bg-white dark:bg-gray-800 px-4 py-2 shadow-sm">
              <input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search for tags, majors, commitments, or club names"
                className="w-full bg-transparent text-sm outline-none"
                aria-label="Search clubs"
              />
              <button
                type="button"
                className="h-9 w-9 inline-flex items-center justify-center rounded-full bg-primary text-white"
                aria-label="Search"
              >
                <svg viewBox="0 0 24 24" className="h-4 w-4" aria-hidden="true">
                  <path
                    d="M10 18a8 8 0 1 1 5.293-2.02l4.364 4.364-1.414 1.414-4.364-4.364A7.96 7.96 0 0 1 10 18Zm0-14a6 6 0 1 0 0 12 6 6 0 0 0 0-12Z"
                    fill="currentColor"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* CLUBS CARD DISPLAY */}
        <div className="grid grid-cols-1 xl:grid-cols-2 2xl:grid-cols-3 gap-6 pt-2 w-full">
          {filteredClubs.map((club: Club) => (
            <div key={club.id} className="border-t-4 border-primary rounded-[5px] shadow-md">
              <div className="flex flex-col py-3 px-5 gap-3">
                <div className="flex justify-between text-center gap-2">
                  <div className="h-16 w-20 rounded-[25px] border-2 border-gray-300 place-items-center flex justify-center min-w-14">
                    <img
                      src={`${import.meta.env.BASE_URL}/${school.toLowerCase()}/club_logo/${club.abbreviation.toLowerCase()}.png`}
                      alt={`${club.name} Logo`}
                      className="h-12 w-12 aspect-square"
                    />
                  </div>
                  <div className="flex gap-2">
                    <span className="bg-secondary text-secondaryText px-3 py-1 rounded-full text-[0.75em] md:text-sm self-start font-bold min-w-22 line-clamp-1 truncate text-clip overflow-hidden max-w-28">
                      {club.tags[0]?.toUpperCase() || ""}
                    </span>
                    <span className="bg-secondary text-secondaryText px-3 py-1 rounded-full text-[0.75em] md:text-sm self-start font-bold min-w-13">
                      {club.majors[0] || "ANY"}
                    </span>
                  </div>
                </div>

                <h2 className="text-xl font-bold mb-2 line-clamp-2 leading-tight max-h-12 min-h-12">{club.name}</h2>

                <div className="h-24 overflow-y-auto">
                  <p className="text-gray-700 dark:text-white mb-4">{club.description}</p>
                </div>

                <div className="flex justify-between">
                  <div className="flex place-items-center">
                    <img src="clock.svg" alt="clock icon" className="h-4 w-4 dark:invert" />
                    <span className="ml-1 text-sm text-gray-500 dark:text-gray-400">{capitalizeWords(club.commitment)}</span>
                  </div>
                  <div className="flex place-items-center">
                    <img src="members.svg" alt="members icon" className="h-4 w-4" />
                    <span className="ml-1 text-sm text-gray-500 dark:text-gray-400">{memberText(club.members)}</span>
                  </div>
                </div>
              </div>

              <Link to={`/clubs/${club.id}`} className="cursor-pointer w-full h-8 bg-primary text-white rounded-b-[5px] transition-colors text-sm font-medium self-start flex items-center justify-center">
                More Detail →
              </Link>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function FilterPanel({
  categories,
  commitments,
  majors,
  selectedCategories,
  selectedCommitments,
  selectedMajors,
  onToggleCategory,
  onToggleCommitment,
  onToggleMajor,
  onClearAll,
  showClear,
}: {
  categories: string[];
  commitments: string[];
  majors: string[];
  selectedCategories: Set<string>;
  selectedCommitments: Set<string>;
  selectedMajors: Set<string>;
  onToggleCategory: (v: string) => void;
  onToggleCommitment: (v: string) => void;
  onToggleMajor: (v: string) => void;
  onClearAll: () => void;
  showClear: boolean;
}) {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="text-sm font-bold text-gray-900 dark:text-gray-100">Filter</div>
        {showClear && (
          <button
            type="button"
            onClick={onClearAll}
            className="text-sm font-semibold text-gray-700 underline underline-offset-2 dark:text-gray-300"
          >
            Clear
          </button>
        )}
      </div>

      <div>
        <h3 className="font-semibold mb-2">Categories</h3>
        <div className="flex flex-col gap-1">
          {categories.map((category) => (
            <label key={category} className="inline-flex items-center">
              <input
                type="checkbox"
                className="form-checkbox"
                checked={selectedCategories.has(category)}
                onChange={() => onToggleCategory(category)}
              />
              <span className="ml-2">{capitalizeWords(category)}</span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <h3 className="font-semibold mb-2">Commitment</h3>
        <div className="flex flex-col gap-1">
          {commitments.map((commitment) => (
            <label key={commitment} className="inline-flex items-center">
              <input
                type="checkbox"
                className="form-checkbox"
                checked={selectedCommitments.has(commitment)}
                onChange={() => onToggleCommitment(commitment)}
              />
              <span className="ml-2">{capitalizeWords(commitment)}</span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <h3 className="font-semibold mb-2">Majors</h3>
        <div className="flex flex-col gap-1 max-h-48 overflow-y-auto">
          {majors.map((major) => (
            <label key={major} className="inline-flex items-center">
              <input
                type="checkbox"
                className="form-checkbox"
                checked={selectedMajors.has(major)}
                onChange={() => onToggleMajor(major)}
              />
              <span className="ml-2">{major}</span>
            </label>
          ))}
        </div>
      </div>
    </div>
  );
}

function memberText(members?: number): string {
  if (members === undefined) return "";
  return Math.floor(members / 10) * 10 + (members % 10 === 0 ? "" : "+") + " members";
}
