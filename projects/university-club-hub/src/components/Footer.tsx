import { Link } from "react-router-dom";

export default function Footer({ school }: { school: string }) {
  const year = new Date().getFullYear();

  return (
    <footer className="mt-10 border-t border-gray-200">
      <div className="mx-auto w-full max-w-6xl px-4 py-8">
        <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-3">
            <img
              src={`${import.meta.env.BASE_URL}/${school.toLowerCase()}/logo.png`}
              alt={`${school} logo`}
              className="h-9 w-auto"
            />
            <div className="min-w-0">
              <div className="text-sm font-bold text-gray-900 dark:text-white truncate">Club Hub</div>
              <div className="text-xs text-gray-600 dark:text-gray-400 truncate">{school}</div>
            </div>
          </div>

          <nav className="flex flex-wrap gap-x-6 gap-y-2 text-sm">
            <Link className="text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white font-semibold" to="/apply">
              Apply a new club
            </Link>
            <Link className="text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white" to="/admin">
              Admin dashboard
            </Link>
          </nav>
        </div>

        <div className="mt-6 flex flex-col gap-2 border-t border-gray-100 pt-4 md:flex-row md:items-center md:justify-between">
          <div className="text-xs text-gray-600 dark:text-gray-400">
            © {year} Club Hub. All rights reserved.
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">
            Theme: <span className="font-semibold">{school}</span>
          </div>
        </div>
      </div>
    </footer>
  );
}