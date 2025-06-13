export interface Character {
  name: string;
  role: string;
  sprite_name: string;
  voice_type: string;
}

export const AVAILABLE_CHARACTERS: Character[] = [
  {
    name: "teacher",
    role: "先生",
    sprite_name: "sprite_woman.png",
    voice_type: "woman"
  },
  {
    name: "cat",
    role: "猫",
    sprite_name: "sprite_cat.png",
    voice_type: "cat"
  },
  {
    name: "ancient_scholar",
    role: "学者",
    sprite_name: "sprite_ancient_scholar.png",
    voice_type: "senior_male"
  }
];