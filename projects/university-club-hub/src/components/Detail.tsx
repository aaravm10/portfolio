import type { Club } from "./Clubs";
import { useEffect, useState } from "react";
import { capitalizeWords } from "./helper";

export default function Detail({ school }: { school: string }) {
    const clubId = window.location.hash.split("/").pop() || "";
    const [club, setClub] = useState<Club | null>(null);

    useEffect(() => {
        fetch(`${import.meta.env.BASE_URL}/${school.toLowerCase()}/clubs.json`)
            .then(response => {
                return response.json();
            })
            .then(data => {
                const found = data.find((c: Club) => String(c.id) === clubId);
                if (found) {
                    setClub(found);
                } else {
                    console.error('Club not found:', clubId);
                }
            })
            .catch(error => console.error('Error fetching club data:', error));
    }, [clubId, school]);

    if (!club) {
        return <div className="p-8">Loading...</div>;
    }

    return (
        <div className="px-8 py-12 md:px-12 max-w-3xl mx-auto">
            {/* back button */}
            <button onClick={() => window.history.back()} className="absolute left-10 -translate-y-8 mb-4 text-accent hover:underline">
                ← Back to Clubs
            </button>

            <img src={`${import.meta.env.BASE_URL}/${school.toLowerCase()}/club_logo/${club.abbreviation.toLowerCase()}.png`} alt={`${club.name} Logo`} className="h-16 w-auto mb-4 mt-4" />
            <h1 className="text-3xl font-bold mb-4">{club.name} ({club.abbreviation})</h1>
            <p className="mb-4">{club.description}</p>
            <div className="mb-4">

                <h2 className="text-xl font-semibold mb-2">Tags</h2>
                <div className="flex gap-2 flex-wrap">
                    {club.tags.map(tag => (
                        <span key={tag} className="bg-gray-200 text-gray-800 px-2 py-1 rounded">{tag}</span>
                    ))}
                </div>
            </div>
            <div className="mb-4">
                <h2 className="text-xl font-semibold mb-2">Majors</h2>
                <div className="flex gap-2 flex-wrap">
                    {club.majors.map(major => (
                        <span key={major} className="bg-gray-200 text-gray-800 px-2 py-1 rounded">{major}</span>
                    ))}
                </div>
            </div>
            <div>
                <h2 className="text-xl font-semibold mb-2">Commitment</h2>
                <p>{capitalizeWords(club.commitment)}</p>
            </div>
        </div>
    )

}