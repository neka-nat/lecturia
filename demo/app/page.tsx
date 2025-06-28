import { Player, Manifest } from './components/Player';
import { Event } from './hooks/useTimeline';
import manifestData from '../public/lectures/demo/manifest.json';
import eventsData from '../public/lectures/demo/events.json';
import quizSectionsData from '../public/lectures/demo/result_quiz.json';

export default function DemoPage() {
  const manifest: Manifest = {
    ...manifestData,
    events: eventsData.events as Event[],
    quizSections: quizSectionsData.quiz_sections
  };
  return <Player manifest={manifest} />;
}
