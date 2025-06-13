import { Users } from 'lucide-react';
import { Character, AVAILABLE_CHARACTERS } from '../types/character';

interface CharacterSelectorProps {
  selectedCharacter: Character;
  onCharacterChange: (character: Character) => void;
}

export function CharacterSelector({ selectedCharacter, onCharacterChange }: CharacterSelectorProps) {
  const handleSelectChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedName = event.target.value;
    const character = AVAILABLE_CHARACTERS.find(c => c.name === selectedName);
    if (character) {
      onCharacterChange(character);
    }
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-semibold text-slate-700">
        <div className="flex items-center gap-2">
          <Users className="w-4 h-4" />
          キャラクター選択
        </div>
      </label>
      <select
        value={selectedCharacter.name}
        onChange={handleSelectChange}
        className="w-full px-3 py-2 bg-white border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-slate-800"
      >
        {AVAILABLE_CHARACTERS.map((character) => (
          <option key={character.name} value={character.name}>
            {character.role}
          </option>
        ))}
      </select>
    </div>
  );
}