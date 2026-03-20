import { useEffect, useMemo, useState } from "react";

export default function Calendar({ school }: { school: string }) {
    const today = new Date();

    // make month/year navigable
    const [viewYear, setViewYear] = useState(today.getFullYear());
    const [viewMonthIndex, setViewMonthIndex] = useState(today.getMonth());

    // keep selected day within the currently viewed month
    const [selectedDay, setSelectedDay] = useState(today.getDate());
    const [events, setEvents] = useState<Event[]>([]);

    useEffect(() => {
        fetch(`${import.meta.env.BASE_URL}/${school?.toLowerCase()}/club_events.json`)
            .then((response) => response.json())
            .then((data) => setEvents(data))
            .catch((error) => console.error("Error fetching events data:", error));
    }, [school]);

    const monthLabel = new Date(viewYear, viewMonthIndex, 1).toLocaleString(undefined, {
        month: "long",
        year: "numeric",
    });

    const weeks = useMemo(() => buildMonthGrid(viewYear, viewMonthIndex), [viewYear, viewMonthIndex]);

    const eventsByDay = useMemo(() => {
        const map = new Map<number, Event[]>();
        for (const e of events) {
            const d = parseLocalYMD(e.date);
            if (Number.isNaN(d.getTime())) continue;
            if (d.getFullYear() !== viewYear || d.getMonth() !== viewMonthIndex) continue;
            const day = d.getDate();
            if (!map.has(day)) map.set(day, []);
            map.get(day)!.push(e);
        }
        return map;
    }, [events, viewYear, viewMonthIndex]);

    function toneFromDate(dateStr: string): "muted" | "soft" | "primary" {
        const d = parseLocalYMD(dateStr);
        if (Number.isNaN(d.getTime())) return "muted";

        const a = new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();
        const b = new Date(today.getFullYear(), today.getMonth(), today.getDate()).getTime();

        if (a < b) return "muted";
        if (a > b) return "soft";
        return "primary";
    }

    function toneClasses(tone: "muted" | "soft" | "primary") {
        if (tone === "primary") return "bg-accent border-red-900 text-white";
        if (tone === "soft") return "bg-primary/10 border-red-900 text-gray-900 dark:text-white";
        return "bg-gray-200 border-gray-500 text-gray-700 ";
    }

    const selectedDateObj = useMemo(
        () => new Date(viewYear, viewMonthIndex, selectedDay),
        [viewYear, viewMonthIndex, selectedDay]
    );

    const selectedEvents = useMemo(() => eventsByDay.get(selectedDay) || [], [eventsByDay, selectedDay]);

    function clampSelectedDay(nextYear: number, nextMonth: number) {
        const dim = new Date(nextYear, nextMonth + 1, 0).getDate();
        setSelectedDay((d) => Math.min(Math.max(1, d), dim));
    }

    function goPrevMonth() {
        setViewMonthIndex((m) => {
            const next = m - 1;
            if (next >= 0) {
                clampSelectedDay(viewYear, next);
                return next;
            }
            const newYear = viewYear - 1;
            clampSelectedDay(newYear, 11);
            setViewYear(newYear);
            return 11;
        });
    }

    function goNextMonth() {
        setViewMonthIndex((m) => {
            const next = m + 1;
            if (next <= 11) {
                clampSelectedDay(viewYear, next);
                return next;
            }
            const newYear = viewYear + 1;
            clampSelectedDay(newYear, 0);
            setViewYear(newYear);
            return 0;
        });
    }

    return (
        <div className="w-full p-4">
            <div className="flex flex-col lg:flex-row w-full gap-4">
                <div className="w-full lg:w-[220px]">
                    <div className="grid grid-cols-3 lg:flex lg:flex-col gap-2">
                        <button
                            type="button"
                            className="px-1 md:px-4 py-2 bg-accent text-white rounded-md text-sm md:text-base font-medium"
                        >
                            Calendar
                        </button>
                        <button
                            type="button"
                            className="px-1 md:px-4 py-2 bg-gray-200 text-gray-700 rounded-md text-sm md:text-base font-medium"
                        >
                            My RSVPs
                        </button>
                        <button
                            type="button"
                            className="px-1 md:px-4 py-2 bg-gray-200 text-gray-700 rounded-md text-sm md:text-base font-medium"
                        >
                            Organizations
                        </button>
                    </div>
                </div>

                <div className="flex-1 min-w-0 max-w-4xl">
                    <CalendarView />

                    <div className="mt-4 rounded-lg border border-gray-200 p-3">
                        <div className="flex items-baseline justify-between gap-2">
                            <div className="text-sm font-bold text-gray-900 dark:text-white">
                                {selectedDateObj.toLocaleDateString(undefined, {
                                    weekday: "long",
                                    month: "long",
                                    day: "numeric",
                                })}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-white">
                                {selectedEvents.length} event{selectedEvents.length === 1 ? "" : "s"}
                            </div>
                        </div>

                        <div className="mt-2 flex flex-col gap-2">
                            {selectedEvents.length === 0 ? (
                                <div className="text-sm text-gray-600">No events</div>
                            ) : (
                                selectedEvents.map((ev, idx) => {
                                    const tone = toneFromDate(ev.date);
                                    return (
                                        <div
                                            key={`${ev.title}-${idx}`}
                                            className={`border-l-3 rounded px-2 py-2 text-sm font-semibold ${toneClasses(tone)}`}
                                            title={ev.title}
                                        >
                                            {ev.title}
                                        </div>
                                    );
                                })
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );

    function CalendarView() {
        return (
            <div className="w-full rounded-lg max-w-4xl">
                <div className="pb-2.5 border-b border-gray-300 mb-2 flex items-center justify-between gap-3 px-2 pt-2">
                    <div className="flex items-center gap-2 justify-between w-full">
                        <div className="text-lg font-bold tracking-wide">{monthLabel}</div>
                        <div className="flex gap-1">
                            {/* today button */}
                            <button
                                type="button"
                                onClick={() => {
                                    setViewYear(today.getFullYear());
                                    setViewMonthIndex(today.getMonth());
                                    setSelectedDay(today.getDate());
                                }
                                }
                                className="bg-white px-4 h-9 items-center justify-center rounded-md border border-gray-200 text-gray-700 hover:bg-gray-50 hidden md:block"
                            >
                                <span className="text-xs">Today</span>
                            </button>

                            <button
                                type="button"
                                onClick={goPrevMonth}
                                aria-label="Previous month"
                                className="bg-white h-9 w-9 inline-flex items-center justify-center rounded-md border border-gray-200 text-gray-700 hover:bg-gray-50"
                            >
                                <span aria-hidden="true">‹</span>
                            </button>


                            <button
                                type="button"
                                onClick={goNextMonth}
                                aria-label="Next month"
                                className="bg-white h-9 w-9 inline-flex items-center justify-center rounded-md border border-gray-200 text-gray-700 hover:bg-gray-50"
                            >
                                <span aria-hidden="true">›</span>
                            </button>
                        </div>
                    </div>
                </div >

                <div className="grid grid-cols-7 border-b border-gray-300 bg-gray-50">
                    {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((d) => (
                        <div
                            key={d}
                            className="px-1 sm:px-3 py-2 text-[10px] sm:text-xs font-bold text-gray-700 border-r border-gray-300 last:border-r-0 text-center sm:text-left"
                        >
                            <span className="sm:hidden">{d[0]}</span>
                            <span className="hidden sm:inline">{d}</span>
                        </div>
                    ))}
                </div>

                <div className="grid grid-cols-7">
                    {weeks.map((week, wi) =>
                        week.map((cell, ci) => {
                            const isEmpty = cell == null;
                            const isSelected = !isEmpty && cell === selectedDay;
                            const dayEvents = !isEmpty ? eventsByDay.get(cell) || [] : [];

                            return (
                                <button
                                    key={`${wi}-${ci}`}
                                    type="button"
                                    className={[
                                        "flex flex-col relative text-left border-r border-b border-gray-300 last:border-r-0 outline-none",
                                        "px-1.5 sm:px-2.5 py-1.5 sm:py-2",
                                        "h-[64px] sm:h-[92px] lg:h-[118px]",
                                        isEmpty ? "cursor-default" : "hover:bg-blue-50 dark:hover:bg-gray-700 cursor-pointer",
                                        isSelected ? "bg-gray-100 dark:bg-gray-700" : "",
                                    ].join(" ")}
                                    onClick={() => {
                                        if (!isEmpty) setSelectedDay(cell);
                                    }}
                                    disabled={isEmpty}
                                    aria-label={isEmpty ? "Empty day" : `Day ${cell}`}
                                >
                                    {!isEmpty && (
                                        <>
                                            <div className="flex items-start justify-start min-h-[22px] sm:min-h-[26px]">
                                                <div
                                                    className={
                                                        isSelected
                                                            ? "w-6 h-6 sm:w-7 sm:h-7 rounded-full inline-flex items-center justify-center bg-accent text-white text-xs sm:text-sm font-bold"
                                                            : "text-sm sm:text-lg font-bold text-gray-500"
                                                    }
                                                >
                                                    {cell}
                                                </div>
                                            </div>

                                            <div className="mt-1 flex-1">
                                                <div className="sm:hidden flex flex-wrap gap-1">
                                                    {dayEvents.slice(0, 6).map((ev, idx) => {
                                                        const tone = toneFromDate(ev.date);
                                                        const dotClass =
                                                            tone === "primary"
                                                                ? "bg-accent"
                                                                : tone === "soft"
                                                                    ? "bg-red-300"
                                                                    : "bg-gray-300";
                                                        return <span key={`${ev.title}-${idx}`} className={`h-2 w-2 rounded-full ${dotClass}`} />;
                                                    })}
                                                    {dayEvents.length > 6 && (
                                                        <span className="text-[10px] text-gray-500">+{dayEvents.length - 6}</span>
                                                    )}
                                                </div>

                                                <div className="hidden sm:flex flex-col gap-1.5 mt-1.5">
                                                    {dayEvents.slice(0, 2).map((ev: Event, idx: number) => {
                                                        const tone = toneFromDate(ev.date);
                                                        return (
                                                            <div
                                                                key={`${ev.title}-${idx}`}
                                                                className={`border-l-3 rounded px-2 py-1 text-[11px] lg:text-xs font-semibold whitespace-nowrap overflow-hidden text-ellipsis ${toneClasses(
                                                                    tone
                                                                )}`}
                                                                title={ev.title}
                                                            >
                                                                {ev.title}
                                                            </div>
                                                        );
                                                    })}

                                                    {dayEvents.length > 2 && (
                                                        <div className="text-[11px] text-gray-600 pl-0.5">+{dayEvents.length - 2} more</div>
                                                    )}
                                                </div>
                                            </div>
                                        </>
                                    )}
                                </button>
                            );
                        })
                    )}
                </div>
            </div >
        );
    }
}

interface Event {
    date: string;
    title: string;
}

function buildMonthGrid(year: number, monthIndex: number) {
    const first = new Date(year, monthIndex, 1);
    const daysInMonth = new Date(year, monthIndex + 1, 0).getDate();
    const leadingEmpty = first.getDay();

    const cells: Array<number | null> = [];
    for (let i = 0; i < leadingEmpty; i++) cells.push(null);
    for (let d = 1; d <= daysInMonth; d++) cells.push(d);

    const num_weeks = Math.max((cells.length / 7), 5);
    // fill trailing empty cells to make a complete grid
    while (cells.length < num_weeks * 7) cells.push(null);

    const weeks: Array<Array<number | null>> = [];
    for (let i = 0; i < num_weeks; i++) weeks.push(cells.slice(i * 7, i * 7 + 7));
    return weeks;
}

function parseLocalYMD(dateStr: string) {
    const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(dateStr);
    if (!m) return new Date(dateStr);
    const y = Number(m[1]);
    const mo = Number(m[2]) - 1;
    const d = Number(m[3]);
    return new Date(y, mo, d);
}