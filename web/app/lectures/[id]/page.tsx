import { Player } from '@/components/Player';
import { notFound } from 'next/navigation';

export default async function LecturePage({
  params,
}: {
  params: { id: string };
}) {
  const r = await fetch(`${process.env.LECTURIA_API_ORIGIN}/api/lectures/${params.id}/manifest`);
  if (!r.ok) return notFound();
  const manifest = await r.json();
  const eventsResp = await fetch(`${process.env.LECTURIA_API_ORIGIN}${manifest.eventsUrl}`);
  manifest.events = await eventsResp.json();

  return <Player manifest={manifest} />;
}
