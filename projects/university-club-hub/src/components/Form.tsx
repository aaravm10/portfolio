import React, { useMemo, useState } from "react";
import { Link } from "react-router-dom";

export type SchoolInfoJson = {
    name: string;
    abbreviation: string;
    "primary-color": string;
    "secondary-color": string;
    "accent-color": string;
    "secondary-text-color"?: string;
    slogan: string;
    majors: Record<string, string>;
    tags: Record<string, string>;
    commitments: Record<string, string>;
};

export type ClubApplication = {
    id: string;
    school: string;
    createdAt: string; // ISO
    status: "pending" | "approved" | "rejected";

    clubName: string;
    abbreviation: string;
    description: string;

    tags: string[]; // keys from info.tags (single select -> array of one)
    majors: string[]; // [primaryMajor, ...altMajors] keys from info.majors
    commitment: string; // key from info.commitments

    contactName: string;
    contactEmail: string;
    website?: string;
    notes?: string;

    logoDataUrl?: string;
    logoFileName?: string;
};

function storageKey(school: string) {
    return `clubApplications:${school.toUpperCase()}`;
}

function loadApplications(school: string): ClubApplication[] {
    try {
        const raw = localStorage.getItem(storageKey(school));
        if (!raw) return [];
        const parsed = JSON.parse(raw);
        return Array.isArray(parsed) ? (parsed as ClubApplication[]) : [];
    } catch {
        return [];
    }
}

function saveApplications(school: string, apps: ClubApplication[]) {
    localStorage.setItem(storageKey(school), JSON.stringify(apps));
}

function uid() {
    return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function readFileAsDataUrl(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onerror = () => reject(new Error("Failed to read file"));
        reader.onload = () => resolve(String(reader.result || ""));
        reader.readAsDataURL(file);
    });
}

export default function Form({
    school,
    info,
}: {
    school: string;
    info: SchoolInfoJson;
}) {
    // Build dropdown lists (sorted by label)
    const majorsList = useMemo(() => {
        return Object.entries(info.majors || {})
            .map(([key, label]) => ({ key, label }))
            .sort((a, b) => a.label.localeCompare(b.label));
    }, [info]);

    const tagsList = useMemo(() => {
        return Object.entries(info.tags || {})
            .map(([key, label]) => ({ key, label }))
            .sort((a, b) => a.label.localeCompare(b.label));
    }, [info]);

    const commitmentsList = useMemo(() => {
        return Object.entries(info.commitments || {})
            .map(([key, label]) => ({ key, label }))
            .sort((a, b) => a.label.localeCompare(b.label));
    }, [info]);

    // Form state
    const [formData, setFormData] = useState({
        clubName: "",
        abbreviation: "",
        description: "",
        tagKey: tagsList[0]?.key || "",
        commitmentKey: commitmentsList[0]?.key || "",
        primaryMajorKey: majorsList[0]?.key || "",
        contactName: "",
        contactEmail: "",
        website: "",
        notes: "",
    });

    const [altMajorKeys, setAltMajorKeys] = useState<Set<string>>(new Set());
    const [logoFile, setLogoFile] = useState<File | null>(null);
    const [logoPreview, setLogoPreview] = useState<string>("");
    const [submittedId, setSubmittedId] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const { clubName, abbreviation, description, tagKey, commitmentKey, primaryMajorKey, contactName, contactEmail, website, notes } = formData;

    const updateFormData = (updates: Partial<typeof formData>) => {
        setFormData((prev) => ({ ...prev, ...updates }));
    };

    const emailValid = useMemo(() => {
        if (!contactEmail.trim()) return false;
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(contactEmail.trim());
    }, [contactEmail]);

    function toggleAltMajor(key: string) {
        setAltMajorKeys((prev) => {
            const next = new Set(prev);
            if (next.has(key)) next.delete(key);
            else next.add(key);
            return next;
        });
    }

    async function onLogoChange(file: File | null) {
        setError(null);
        setLogoFile(file);
        setLogoPreview("");

        if (!file) return;

        if (!file.type.startsWith("image/")) {
            setError("Logo must be an image file.");
            setLogoFile(null);
            return;
        }

        // Keep localStorage safe (demo)
        if (file.size > 2 * 1024 * 1024) {
            setError("Logo must be under 2MB.");
            setLogoFile(null);
            return;
        }

        try {
            const dataUrl = await readFileAsDataUrl(file);
            setLogoPreview(dataUrl);
        } catch {
            setError("Could not read logo file.");
            setLogoFile(null);
        }
    }

    function majorsForStorage(): string[] {
        const primary = primaryMajorKey;
        const alts = Array.from(altMajorKeys).filter((k) => k !== primary);
        return primary ? [primary, ...alts] : alts;
    }

    async function onSubmit(e: React.FormEvent) {
        e.preventDefault();
        setError(null);
        setSubmittedId(null);

        if (!clubName.trim()) return setError("Club name is required.");
        if (!abbreviation.trim()) return setError("Abbreviation is required.");
        if (!description.trim()) return setError("Description is required.");
        if (!contactName.trim()) return setError("Contact name is required.");
        if (!emailValid) return setError("A valid contact email is required.");

        if (!primaryMajorKey) return setError("Primary major is required.");
        if (!tagKey) return setError("Tag is required.");
        if (!commitmentKey) return setError("Commitment is required.");

        setIsSubmitting(true);

        const app: ClubApplication = {
            id: uid(),
            school: school.toUpperCase(),
            createdAt: new Date().toISOString(),
            status: "pending",

            clubName: clubName.trim(),
            abbreviation: abbreviation.trim(),
            description: description.trim(),

            tags: [tagKey],
            majors: majorsForStorage(),
            commitment: commitmentKey,

            contactName: contactName.trim(),
            contactEmail: contactEmail.trim(),
            website: website.trim() ? website.trim() : undefined,
            notes: notes.trim() ? notes.trim() : undefined,

            logoDataUrl: logoPreview || undefined,
            logoFileName: logoFile?.name || undefined,
        };

        const existing = loadApplications(school);
        saveApplications(school, [app, ...existing]);

        setSubmittedId(app.id);
        setIsSubmitting(false);

        // clear the form but keep defaults
        setFormData({
            clubName: "",
            abbreviation: "",
            description: "",
            tagKey: tagsList[0]?.key || "",
            commitmentKey: commitmentsList[0]?.key || "",
            primaryMajorKey: majorsList[0]?.key || "",
            contactName: "",
            contactEmail: "",
            website: "",
            notes: "",
        });
        setAltMajorKeys(new Set());
        setLogoFile(null);
        setLogoPreview("");
    }

    return (
        <div className="mx-auto w-full max-w-3xl p-4">
            <div className="rounded-lg border border-gray-200 bg-white p-5">
                <div className="flex items-center justify-between gap-3">
                    <h1 className="text-lg font-bold text-gray-900">Apply to add a new club</h1>
                    <div className="text-xs text-gray-600">
                        School: {info.abbreviation || school.toUpperCase()}
                    </div>
                </div>

                <p className="mt-2 text-sm text-gray-700">
                    This creates a request for admin review. For now, requests are stored locally (demo).
                </p>

                {submittedId && (
                    <div className="mt-4 rounded-md border border-green-200 bg-green-50 p-3 text-sm text-green-900">
                        Submitted. Request ID: <span className="font-mono">{submittedId}</span>
                    </div>
                )}

                {error && (
                    <div className="mt-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-900">
                        {error}
                    </div>
                )}

                <form className="mt-5 grid grid-cols-1 gap-4 text-black!" onSubmit={onSubmit}>
                    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                        <Field label="Club name" required>
                            <input
                                value={clubName}
                                onChange={(e) => updateFormData({ clubName: e.target.value })}
                                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black/10 "
                                placeholder="e.g., Computer Vision Club"
                            />
                        </Field>

                        <Field label="Abbreviation" required>
                            <input
                                value={abbreviation}
                                onChange={(e) => updateFormData({ abbreviation: e.target.value })}
                                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black/10"
                                placeholder="e.g., CVC"
                            />
                        </Field>
                    </div>

                    <Field label="Description" required>
                        <textarea
                            value={description}
                            onChange={(e) => updateFormData({ description: e.target.value })}
                            className="min-h-[120px] w-full rounded-md border border-gray-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black/10"
                            placeholder="What does the club do?"
                        />
                    </Field>

                    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                        <Field label="Tag" required>
                            <select
                                value={tagKey}
                                onChange={(e) => updateFormData({ tagKey: e.target.value })}
                                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black/10"
                            >
                                {tagsList.map((t) => (
                                    <option key={t.key} value={t.key}>
                                        {t.label}
                                    </option>
                                ))}
                            </select>
                        </Field>

                        <Field label="Commitment" required>
                            <select
                                value={commitmentKey}
                                onChange={(e) => updateFormData({ commitmentKey: e.target.value })}
                                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black/10"
                            >
                                {commitmentsList.map((c) => (
                                    <option key={c.key} value={c.key}>
                                        {c.label}
                                    </option>
                                ))}
                            </select>
                        </Field>
                    </div>

                    <div className="rounded-md border border-gray-200 p-4">
                        <div className="text-sm font-bold text-gray-900">Majors</div>

                        <div className="mt-3 grid grid-cols-1 gap-4 md:grid-cols-2">
                            <Field label="Primary Major (choose one)" required>
                                <select
                                    value={primaryMajorKey}
                                    onChange={(e) => {
                                        const nextPrimary = e.target.value;
                                        updateFormData({ primaryMajorKey: nextPrimary });
                                        setAltMajorKeys((prev) => {
                                            const next = new Set(prev);
                                            next.delete(nextPrimary);
                                            return next;
                                        });
                                    }}
                                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black/10"
                                >
                                    {majorsList.map((m) => (
                                        <option key={m.key} value={m.key}>
                                            {m.label}
                                        </option>
                                    ))}
                                </select>
                            </Field>

                            <div>
                                <label className="block text-sm font-semibold text-gray-900">Alternative majors (optional)</label>
                                <div className="mt-2 max-h-56 overflow-auto rounded-md border border-gray-200 p-2">
                                    <div className="flex flex-col gap-1">
                                        {majorsList.map((m) => {
                                            const disabled = m.key === primaryMajorKey;
                                            return (
                                                <label
                                                    key={m.key}
                                                    className={`inline-flex items-center gap-2 px-1 py-1 ${disabled ? "opacity-50" : ""}`}
                                                >
                                                    <input
                                                        type="checkbox"
                                                        className="form-checkbox"
                                                        checked={altMajorKeys.has(m.key)}
                                                        onChange={() => toggleAltMajor(m.key)}
                                                        disabled={disabled}
                                                    />
                                                    <span className="text-sm text-gray-800">{m.label}</span>
                                                    <span className="ml-auto text-xs text-gray-500">{m.key}</span>
                                                </label>
                                            );
                                        })}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="rounded-md border border-gray-200 p-4">
                        <div className="text-sm font-bold text-gray-900">Club logo</div>
                        <div className="mt-3 grid grid-cols-1 gap-4 md:grid-cols-2">
                            <div>
                                <label className="block text-sm font-semibold text-gray-900">Upload logo (optional)</label>
                                <input
                                    type="file"
                                    accept="image/*"
                                    onChange={(e) => onLogoChange(e.target.files?.[0] || null)}
                                    id="logo-upload"
                                    className="mt-2 block w-full text-sm gap-2 text-gray-700 border border-gray-300 rounded-md cursor-pointer focus:outline-none focus:ring-2 focus:ring-black/10"
                                />
                                <div className="mt-2 text-xs text-gray-600">PNG/JPG recommended. Max 2MB (demo storage).</div>
                            </div>

                            <div className="rounded-md border border-dashed border-gray-300 bg-gray-50 p-3 flex items-center justify-center min-h-[120px]">
                                {logoPreview ? (
                                    <img src={logoPreview} alt="Logo preview" className="max-h-32 object-contain" />
                                ) : (
                                    <div className="text-xs text-gray-600 text-center">
                                        No logo selected
                                        <div className="mt-1 text-[11px] text-gray-500">Preview will appear here</div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                        <Field label="Contact name" required>
                            <input
                                value={contactName}
                                onChange={(e) => updateFormData({ contactName: e.target.value })}
                                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black/10"
                                placeholder="e.g., Joe Smith"
                            />
                        </Field>

                        <Field label="Contact email" required>
                            <input
                                value={contactEmail}
                                onChange={(e) => updateFormData({ contactEmail: e.target.value })}
                                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black/10"
                                placeholder={`e.g., akim5@${info.abbreviation.toLowerCase()}.edu`}
                            />
                            {!emailValid && contactEmail.trim().length > 0 && (
                                <div className="mt-1 text-xs text-red-700">Enter a valid email.</div>
                            )}
                        </Field>
                    </div>

                    <Field label="Website (optional)">
                        <input
                            value={website}
                            onChange={(e) => updateFormData({ website: e.target.value })}
                            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black/10"
                            placeholder="https://..."
                        />
                    </Field>

                    <Field label="Please provide evidence of ownership of this club for your school admin to review.">
                        <textarea
                            value={notes}
                            onChange={(e) => updateFormData({ notes: e.target.value })}
                            className="min-h-[80px] w-full rounded-md border border-gray-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black/10"
                            placeholder="Evidence for admin (e.g., a link with your title on an official school page)"
                        />
                    </Field>

                    <div className="mt-2 flex items-center gap-2">
                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white hover:bg-primary/90 disabled:opacity-60"
                        >
                            {isSubmitting ? "Submitting..." : "Submit request"}
                        </button>

                        <Link
                            to="/clubs"
                            className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-semibold text-gray-900 hover:bg-gray-50"
                        >
                            Back to clubs
                        </Link>
                    </div>
                </form>
            </div>
        </div>
    );
}

function Field({
    label,
    required,
    children,
}: {
    label: string;
    required?: boolean;
    children: React.ReactNode;
}) {
    return (
        <div>
            <label className="block text-sm font-semibold text-gray-900">
                {label} {required ? <span className="text-red-700">*</span> : null}
            </label>
            <div className="mt-1">{children}</div>
        </div>
    );
}

