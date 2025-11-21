import random
from src.utils.definition import Monster

class MonsterFactory:
    MONSTER_NAMES = [
        "Bulbasaur", "Charmander", "Squirtle", "Pikachu", 
        "Jigglypuff", "Meowth", "Psyduck", "Machop",
        "Geodude", "Slowpoke", "Magnemite", "Doduo",
        "Seel", "Grimer", "Shellder", "Gastly"
    ]
    
    SPRITE_TEMPLATE = "sprites/sprite{}_idle.png"
    
    @staticmethod
    def create_random_monster(level_range: tuple[int, int] = (5, 10)) -> Monster:
        level = random.randint(*level_range)
        max_hp = 20 + level * 5 + random.randint(0, 10)
        
        # Pick a random sprite index (1-16 based on previous file listing)
        sprite_idx = random.randint(1, 16)
        sprite_path = MonsterFactory.SPRITE_TEMPLATE.format(sprite_idx)
        
        # Pick a random name or use a generic one based on sprite
        name = random.choice(MonsterFactory.MONSTER_NAMES)
        
        return {
            "name": name,
            "hp": max_hp,
            "max_hp": max_hp,
            "level": level,
            "sprite_path": sprite_path,
            "id": sprite_idx
        }

    @staticmethod
    def create_monster(name: str, level: int, sprite_idx: int) -> Monster:
        max_hp = 20 + level * 5
        sprite_path = MonsterFactory.SPRITE_TEMPLATE.format(sprite_idx)
        return {
            "name": name,
            "hp": max_hp,
            "max_hp": max_hp,
            "level": level,
            "sprite_path": sprite_path,
            "id": sprite_idx
        }
