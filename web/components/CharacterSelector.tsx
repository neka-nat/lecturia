import { Users } from 'lucide-react';
import { Character, AVAILABLE_CHARACTERS } from '../types/character';

interface CharacterSelectorProps {
  selectedCharacter: Character;
  onCharacterChange: (character: Character) => void;
}

export function CharacterSelector({ selectedCharacter, onCharacterChange }: CharacterSelectorProps) {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-semibold text-slate-700">
        <div className="flex items-center gap-2">
          <Users className="w-4 h-4" />
          キャラクター選択
        </div>
      </label>
      <div className="grid grid-cols-1 gap-3">
        {AVAILABLE_CHARACTERS.map((character) => (
          <div
            key={character.name}
            className={`relative p-3 rounded-lg border-2 cursor-pointer transition-all duration-200 ${
              selectedCharacter.name === character.name
                ? 'border-indigo-500 bg-indigo-50/50 shadow-md'
                : 'border-slate-200 bg-white/70 hover:border-slate-300 hover:bg-slate-50/50'
            }`}
            onClick={() => onCharacterChange(character)}
          >
            <div className="flex items-center space-x-3">
              <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                selectedCharacter.name === character.name
                  ? 'border-indigo-500 bg-indigo-500'
                  : 'border-slate-300'
              }`}>
                {selectedCharacter.name === character.name && (
                  <div className="w-2 h-2 rounded-full bg-white"></div>
                )}
              </div>
              <div className="flex-1">
                <div className="font-medium text-slate-800">{character.role}</div>
                <div className="text-sm text-slate-500">
                  {character.name} ({character.voice_type})
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}