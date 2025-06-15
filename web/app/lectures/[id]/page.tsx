import { Player } from '@/components/Player';
import { notFound } from 'next/navigation';
import Link from 'next/link';

export default async function LecturePage({
  params,
}: {
  params: { id: string };
}) {
  const { id } = await params;
  const r = await fetch(
    `${process.env.NEXT_PUBLIC_LECTURIA_API_ORIGIN}/api/lectures/${id}/manifest`,
    { cache: 'no-store' },
  );
  if (!r.ok) return notFound();

  const manifest = await r.json();
  const eventsResp = await fetch(
    `${process.env.NEXT_PUBLIC_LECTURIA_API_ORIGIN}${manifest.eventsUrl}`,
    { cache: 'no-store' },
  );
  let quizSections: any[] = [];
  try {
    const quizResp = await fetch(
      `${process.env.NEXT_PUBLIC_LECTURIA_API_ORIGIN}${manifest.quizUrl}`,
      { cache: 'no-store' },
    );
    if (quizResp.ok) {
      const { quiz_sections } = await quizResp.json();
      quizSections = quiz_sections ?? [];
    } else if (quizResp.status !== 404) {
      console.warn('quiz fetch error', quizResp.status);
    }
  } catch (e) {
    console.warn('quiz fetch failed (ignored)', e);
  }
  manifest.quizSections = quizSections;   // 404 時は []
  const { events } = await eventsResp.json();
  manifest.events = events;
  manifest.slideUrl = `${process.env.NEXT_PUBLIC_LECTURIA_API_ORIGIN}${manifest.slideUrl}`;
  manifest.audioUrls = manifest.audioUrls.map((url: string) => `${process.env.NEXT_PUBLIC_LECTURIA_API_ORIGIN}${url}`);

  return (
    <div className="relative">
      <Link
        href="/"
        className="absolute top-4 left-4 z-30 bg-white text-gray-700 px-4 py-2 rounded-lg shadow-md hover:bg-gray-50 transition-colors"
      >
        ← メインページに戻る
      </Link>
      <Player manifest={manifest} />
    </div>
  );
}
