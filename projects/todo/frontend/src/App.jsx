import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import { CalendarDays, CheckCircle2, ListTodo, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

function formatDate(iso) {
  return new Intl.DateTimeFormat("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(iso));
}

function App() {
  const [data, setData] = useState({ groupedByCourse: {}, allTodos: [] });
  const [completedIds, setCompletedIds] = useState(() => new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchTodos = async () => {
      setLoading(true);
      setError("");

      try {
        const response = await axios.get(`${apiBaseUrl}/api/todos`);
        setData(response.data);
      } catch (err) {
        setError(err.response?.data?.error || "Failed to load assignments.");
      } finally {
        setLoading(false);
      }
    };

    fetchTodos();
  }, []);

  const stats = useMemo(() => {
    const total = data.allTodos.length;
    const done = completedIds.size;
    return { total, done, remaining: total - done };
  }, [completedIds, data.allTodos.length]);

  const toggleComplete = (todoKey) => {
    setCompletedIds((prev) => {
      const next = new Set(prev);
      if (next.has(todoKey)) next.delete(todoKey);
      else next.add(todoKey);
      return next;
    });
  };

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8 sm:py-12">
      <div className="mx-auto w-full max-w-5xl space-y-8">
        <header className="space-y-3">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-900 sm:text-4xl">
            My Assignments
          </h1>
          <p className="text-sm text-slate-600 sm:text-base">
            A clean overview of upcoming Canvas work, grouped by course.
          </p>
        </header>

        <section className="grid gap-4 sm:grid-cols-3">
          <StatCard icon={ListTodo} label="Total" value={stats.total} />
          <StatCard icon={CheckCircle2} label="Completed" value={stats.done} />
          <StatCard icon={CalendarDays} label="Upcoming" value={stats.remaining} />
        </section>

        {loading ? (
          <Card className="rounded-2xl border-slate-200 shadow-sm">
            <CardContent className="flex items-center justify-center gap-3 py-10 text-slate-600">
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading assignments...
            </CardContent>
          </Card>
        ) : null}

        {error ? (
          <Card className="rounded-2xl border-red-200 bg-red-50 shadow-sm">
            <CardContent className="py-6 text-sm text-red-700">{error}</CardContent>
          </Card>
        ) : null}

        {!loading && !error && data.allTodos.length === 0 ? (
          <Card className="rounded-2xl border-slate-200 shadow-sm">
            <CardContent className="py-10 text-center text-slate-600">
              No upcoming assignments with due dates.
            </CardContent>
          </Card>
        ) : null}

        {!loading && !error ? (
          <div className="space-y-8">
            {Object.entries(data.groupedByCourse).map(([courseName, todos]) => (
              <section key={courseName} className="space-y-3">
                <h2 className="text-lg font-semibold text-slate-900">{courseName}</h2>
                <div className="grid gap-3 sm:grid-cols-2">
                  {todos.map((todo) => {
                    const todoKey = `${courseName}-${todo.id}`;
                    const isComplete = completedIds.has(todoKey);

                    return (
                      <Card
                        key={todoKey}
                        className="rounded-2xl border-slate-200 bg-white shadow-sm transition-all duration-150 hover:-translate-y-0.5 hover:shadow-md"
                      >
                        <CardHeader className="flex flex-row items-start justify-between space-y-0 gap-3 pb-2">
                          <CardTitle
                            className={`text-base font-medium leading-snug ${
                              isComplete ? "text-slate-400 line-through" : "text-slate-900"
                            }`}
                          >
                            {todo.title}
                          </CardTitle>
                          <Checkbox
                            checked={isComplete}
                            onCheckedChange={() => toggleComplete(todoKey)}
                            aria-label={`Mark ${todo.title} as complete`}
                          />
                        </CardHeader>
                        <CardContent className="pt-0">
                          <p className="text-sm text-slate-600">{formatDate(todo.dueDate)}</p>
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              </section>
            ))}
          </div>
        ) : null}
      </div>
    </main>
  );
}

function StatCard({ icon: Icon, label, value }) {
  return (
    <Card className="rounded-2xl border-slate-200 bg-white shadow-sm">
      <CardContent className="flex items-center justify-between py-5">
        <div>
          <p className="text-sm text-slate-500">{label}</p>
          <p className="text-2xl font-semibold text-slate-900">{value}</p>
        </div>
        <div className="rounded-xl bg-indigo-50 p-2 text-indigo-600">
          <Icon className="h-4 w-4" />
        </div>
      </CardContent>
    </Card>
  );
}

export default App;
