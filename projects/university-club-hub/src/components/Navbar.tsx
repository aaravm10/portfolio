import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";

export default function Navbar({
    school,
    onOpenSchoolPicker,
}: {
    school: string;
    onOpenSchoolPicker: () => void;
}) {
    const [isProfileOpen, setIsProfileOpen] = useState(false);
    const [isMobileOpen, setIsMobileOpen] = useState(false);

    const profileWrapRef = useRef<HTMLDivElement | null>(null);
    const mobileWrapRef = useRef<HTMLDivElement | null>(null);

    const isActive = (path: string) => window.location.pathname === path;

    useEffect(() => {
        const onPointerDown = (e: MouseEvent | TouchEvent) => {
            const target = e.target as Node | null;

            if (isProfileOpen && profileWrapRef.current && target && !profileWrapRef.current.contains(target)) {
                setIsProfileOpen(false);
            }

            if (isMobileOpen && mobileWrapRef.current && target && !mobileWrapRef.current.contains(target)) {
                setIsMobileOpen(false);
            }
        };

        const onKeyDown = (e: KeyboardEvent) => {
            if (e.key === "Escape") {
                setIsProfileOpen(false);
                setIsMobileOpen(false);
            }
        };

        document.addEventListener("touchstart", onPointerDown, { passive: true });
        document.addEventListener("keydown", onKeyDown);

        return () => {
            document.removeEventListener("touchstart", onPointerDown);
            document.removeEventListener("keydown", onKeyDown);
        };
    }, [isProfileOpen, isMobileOpen]);

    return (
        <nav className="w-[100vw] bg-primary">
            <div className="mx-auto px-2 md:px-6 lg:px-8">
                <div className="relative flex h-16 items-center justify-between">
                    <div className="absolute inset-y-0 left-0 flex items-center md:hidden">
                        <button
                            type="button"
                            aria-controls="mobile-menu"
                            aria-expanded={!!isMobileOpen}
                            onClick={() => setIsMobileOpen((v) => !v)}
                            className="relative inline-flex items-center justify-center rounded-md p-2 text-gray-100 hover:bg-white/10 hover:text-white focus:outline focus:outline-2 focus:-outline-offset-1 focus:outline-indigo-500"
                        >
                            <span className="absolute -inset-0.5" />
                            <span className="sr-only">Open main menu</span>

                            {!isMobileOpen ? (
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true" className="size-6">
                                    <path d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" strokeLinecap="round" strokeLinejoin="round" />
                                </svg>
                            ) : (
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true" className="size-6">
                                    <path d="M6 18 18 6M6 6l12 12" strokeLinecap="round" strokeLinejoin="round" />
                                </svg>
                            )}
                        </button>
                    </div>

                    <div className="flex flex-1 items-center justify-center md:items-stretch md:justify-start place-items-center gap-4">
                        <button
                            type="button"
                            onClick={onOpenSchoolPicker}
                            className="flex shrink-0 items-center rounded-md focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white/70"
                            aria-label="Switch school"
                            title="Switch school"
                        >
                            <img src={`${import.meta.env.BASE_URL}/${school.toLowerCase()}/logo.png`} alt={`${school} Logo`} className="h-10 w-auto" />
                        </button>

                        <h1 className="text-base md:text-xl font-bold self-center text-nowrap text-white">
                            Club {navName(window.location.pathname)} | {school}
                        </h1>
                    </div>

                    <div className="hidden md:ml-6 md:block">
                        <div className="flex space-x-4">
                            <Link
                                to="/clubs"
                                className={`rounded-md px-3 py-2 text-m font-medium ${isActive("/clubs") ? "font-bold text-white" : "text-gray-200 hover:bg-white/10 hover:text-white"
                                    }`}
                            >
                                Clubs
                            </Link>
                            <Link
                                to="/calendar"
                                className={`rounded-md px-3 py-2 text-m font-medium ${isActive("/calendar") ? "font-bold text-white" : "text-gray-200 hover:bg-white/10 hover:text-white"
                                    }`}
                            >
                                Calendar
                            </Link>
                        </div>
                    </div>

                    <div className="absolute inset-y-0 right-0 flex items-center pr-2 md:static md:inset-auto md:ml-6 md:pr-0">
                        <div className="relative ml-3" ref={profileWrapRef}>
                            <button
                                type="button"
                                aria-expanded={!!isProfileOpen}
                                aria-haspopup="menu"
                                onClick={() => setIsProfileOpen((v) => !v)}
                                className="relative flex rounded-full focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500"
                            >
                                <span className="absolute -inset-1.5" />
                                <span className="sr-only">Open user menu</span>
                                <img
                                    src={`${import.meta.env.BASE_URL}/avatar_temp.png`}
                                    alt=""
                                    className="size-8 rounded-full bg-gray-800 outline outline-1 -outline-offset-1 outline-white/10"
                                />
                            </button>

                            {isProfileOpen && (
                                <div role="menu" className="absolute right-0 mt-2 w-48 origin-top-right rounded-md bg-white shadow-lg outline outline-1 outline-black/5 z-50 dark:bg-gray-800">
                                    <Link to="/profile" role="menuitem" onClick={() => setIsProfileOpen(false)} className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700">
                                        Your profile
                                    </Link>
                                    <Link to="/settings" role="menuitem" onClick={() => setIsProfileOpen(false)} className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700">
                                        Settings
                                    </Link>
                                    <Link to="/sign-out" role="menuitem" onClick={() => setIsProfileOpen(false)} className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700">
                                        Sign out
                                    </Link>
                                    {/* restart demo */}
                                    <Link to="/restart-demo" role="menuitem" onClick={() => {
                                        // clear local storage and reload
                                        localStorage.clear();
                                        window.location.href = `${import.meta.env.BASE_URL}`;
                                    }} className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700">
                                        Restart demo
                                    </Link>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            <div id="mobile-menu" hidden={!isMobileOpen} className="md:hidden" ref={mobileWrapRef}>
                <div className="space-y-1 px-2 pb-3 pt-2">
                    <Link
                        to="/clubs"
                        className={`block rounded-md px-3 py-2 text-base font-medium ${isActive("/clubs") ? "bg-black/20 text-white" : "text-gray-200 hover:bg-white/10 hover:text-white"
                            }`}
                        onClick={() => setIsMobileOpen(false)}
                    >
                        Clubs
                    </Link>
                    <Link
                        to="/calendar"
                        className={`block rounded-md px-3 py-2 text-base font-medium ${isActive("/calendar") ? "bg-black/20 text-white" : "text-gray-200 hover:bg-white/10 hover:text-white"
                            }`}
                        onClick={() => setIsMobileOpen(false)}
                    >
                        Calendar
                    </Link>
                </div>
            </div>
        </nav>
    );
}

function navName(path: string) {
    switch (path) {
        case "/clubs":
        case "/":
            return "Hub";
        case "/calendar":
            return "Calendar";
        default:
            return "";
    }
}