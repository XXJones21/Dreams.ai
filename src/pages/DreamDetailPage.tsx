import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import DreamCard from "../components/feed/DreamCard";

// Import the Dream interface from DreamCard for type safety
import type { Dream } from "../components/feed/DreamCard";

const DreamDetailPage: React.FC = () => {
  const { dreamId } = useParams<{ dreamId: string }>();
  const [dream, setDream] = useState<Dream | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!dreamId) return;
    setLoading(true);
    setError(null);
    fetch(`http://localhost:8000/api/dreams/${dreamId}`)
      .then((res) => {
        if (!res.ok) throw new Error("Dream not found");
        return res.json();
      })
      .then((data) => {
        setDream(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [dreamId]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;
  if (!dream) return <div>Dream not found.</div>;

  return (
    <div className="flex justify-center mt-8">
      <DreamCard
        dream={dream}
        onInteraction={() => {}}
        isAuthenticated={true}
      />
    </div>
  );
};

export default DreamDetailPage; 