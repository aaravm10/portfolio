// src/components/AdminDashboard.tsx
import { useEffect, useMemo, useState } from "react";
import type { ClubApplication } from "./Form";
import { Link } from "react-router-dom";

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

export default function ClubManagerDashboard({ school }: { school: string }) {
    const [apps, setApps] = useState<ClubApplication[]>([]);
    const [query, setQuery] = useState("");
    const [status, setStatus] = useState<"all" | ClubApplication["status"]>("all");

    useEffect(() => {
        setApps(loadApplications(school));
    }, [school]);

    const filtered = useMemo(() => {
        const q = query.trim().toLowerCase();
        return apps.filter((a) => {
            const matchesStatus = status === "all" || a.status === status;
            if (!matchesStatus) return false;
            if (!q) return true;

            const hay = [
                a.clubName,
                a.abbreviation,
                a.description,
                a.tags,
                a.majors,
                a.commitment,
                a.contactName,
                a.contactEmail,
                a.website ?? "",
                a.notes ?? "",
            ]
                .join(" ")
                .toLowerCase();

            return hay.includes(q);
        });
    }, [apps, query, status]);

    function updateStatus(id: string, next: ClubApplication["status"]) {
        setApps((prev) => {
            const updated = prev.map((a) => (a.id === id ? { ...a, status: next } : a));
            saveApplications(school, updated);
            return updated;
        });
    }

    function removeRequest(id: string) {
        setApps((prev) => {
            const updated = prev.filter((a) => a.id !== id);
            saveApplications(school, updated);
            return updated;
        });
    }

    const counts = useMemo(() => {
        const c = { pending: 0, approved: 0, rejected: 0 };
        for (const a of apps) {
            if (a.status in c) c[a.status as keyof typeof c]++;
        }
        return c;
    }, [apps]);

    return (
        <div className="mx-auto w-full max-w-6xl p-4">
            <div className="rounded-lg border border-gray-200 bg-white p-5">
                <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
                    <div>
                        <h1 className="text-lg font-bold text-gray-900">Admin dashboard</h1>
                        <div className="mt-1 text-sm text-gray-700">School: {school.toUpperCase()}</div>
                        <div className="mt-2 flex flex-wrap gap-2 text-xs">
                            <Badge label={`Pending: ${counts.pending}`} />
                            <Badge label={`Approved: ${counts.approved}`} />
                            <Badge label={`Rejected: ${counts.rejected}`} />
                        </div>
                    </div>

                    <div className="flex flex-col gap-2 md:flex-row md:items-center text-black!">
                        <input
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Search requests..."
                            className="w-full md:w-72 rounded-md border border-gray-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black/10"
                        />

                        <select
                            value={status}
                            onChange={(e) => setStatus(e.target.value as "all" | ClubApplication["status"])}
                            className="w-full md:w-48 rounded-md border border-gray-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black/10"
                        >
                            <option value="all">All statuses</option>
                            <option value="pending">Pending</option>
                            <option value="approved">Approved</option>
                            <option value="rejected">Rejected</option>
                        </select>

                        <button
                            type="button"
                            onClick={() => setApps(loadApplications(school))}
                            className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm font-semibold text-gray-900 hover:bg-gray-50"
                        >
                            Refresh
                        </button>
                    </div>
                </div>

                <div className="mt-5 overflow-x-auto">
                    <table className="min-w-[900px] w-full border-collapse">
                        <thead>
                            <tr className="text-left text-xs font-bold text-gray-700 border-b border-gray-200">
                                <th className="py-2 pr-3">Submitted</th>
                                <th className="py-2 pr-3">Club</th>
                                <th className="py-2 pr-3">Contact</th>
                                <th className="py-2 pr-3">Status</th>
                                <th className="py-2 pr-3">Actions</th>
                            </tr>
                        </thead>

                        <tbody>
                            {filtered.length === 0 ? (
                                <tr>
                                    <td colSpan={5} className="py-6 text-sm text-gray-600">
                                        No requests found.
                                    </td>
                                </tr>
                            ) : (
                                filtered.map((a) => (
                                    <tr key={a.id} className="border-b border-gray-100 align-top">
                                        <td className="py-3 pr-3 text-sm text-gray-700 whitespace-nowrap">
                                            {new Date(a.createdAt).toLocaleString()}
                                        </td>

                                        <td className="py-3 pr-3">
                                            <div className="text-sm font-semibold text-gray-900">{a.clubName}</div>
                                            <div className="text-xs text-gray-600">{a.abbreviation}</div>
                                            <div className="mt-2 text-xs text-gray-700 line-clamp-3">{a.description}</div>

                                            <div className="mt-2 flex flex-wrap gap-2 text-xs">
                                                {a.tags
                                                    .map((t: string) => t.trim())
                                                    .filter(Boolean)
                                                    .slice(0, 6)
                                                    .map((t: string) => (
                                                        <span key={t} className="rounded-full bg-gray-100 px-2 py-0.5 text-gray-700">
                                                            {t}
                                                        </span>
                                                    ))}
                                            </div>
                                        </td>

                                        <td className="py-3 pr-3 text-sm text-gray-700">
                                            <div className="font-semibold text-gray-900">{a.contactName}</div>
                                            <div className="text-xs text-gray-700">{a.contactEmail}</div>
                                            {a.website ? (
                                                <div className="mt-1 text-xs">
                                                    <Link className="text-blue-700 underline" to={a.website} target="_blank" rel="noreferrer">
                                                        Website
                                                    </Link>
                                                </div>
                                            ) : null}
                                        </td>

                                        <td className="py-3 pr-3">
                                            <StatusPill status={a.status} />
                                        </td>

                                        <td className="py-3 pr-3">
                                            <div className="flex flex-col gap-2">
                                                <div className="flex flex-wrap gap-2">
                                                    <button
                                                        type="button"
                                                        onClick={() => updateStatus(a.id, "approved")}
                                                        className="rounded-md bg-primary px-3 py-1.5 text-xs font-semibold text-white hover:bg-primary/90"
                                                    >
                                                        Approve
                                                    </button>
                                                    <button
                                                        type="button"
                                                        onClick={() => updateStatus(a.id, "rejected")}
                                                        className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-xs font-semibold text-gray-900 hover:bg-gray-50"
                                                    >
                                                        Reject
                                                    </button>
                                                    <button
                                                        type="button"
                                                        onClick={() => updateStatus(a.id, "pending")}
                                                        className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-xs font-semibold text-gray-900 hover:bg-gray-50"
                                                    >
                                                        Mark pending
                                                    </button>
                                                </div>

                                                <button
                                                    type="button"
                                                    onClick={() => removeRequest(a.id)}
                                                    className="self-start text-xs font-semibold text-red-700 underline underline-offset-2"
                                                >
                                                    Delete
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

function Badge({ label }: { label: string }) {
    return <span className="rounded-full bg-gray-100 px-2 py-1 text-gray-700">{label}</span>;
}

function StatusPill({ status }: { status: ClubApplication["status"] }) {
    const cls =
        status === "approved"
            ? "bg-green-100 text-green-900"
            : status === "rejected"
                ? "bg-red-100 text-red-900"
                : "bg-yellow-100 text-yellow-900";

    return <span className={`inline-flex rounded-full px-2 py-1 text-xs font-bold ${cls}`}>{status}</span>;
}