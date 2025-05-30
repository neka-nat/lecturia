import { Player } from '@/components/Player';
import { notFound } from 'next/navigation';

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
  const { events } = await eventsResp.json();
  manifest.events = events;
  manifest.slideUrl = `${process.env.NEXT_PUBLIC_LECTURIA_API_ORIGIN}${manifest.slideUrl}`;
  manifest.audioUrl = `${process.env.NEXT_PUBLIC_LECTURIA_API_ORIGIN}${manifest.audioUrl}`;

  return <Player manifest={manifest} />;
}
