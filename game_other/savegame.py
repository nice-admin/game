# Standard library imports
import os
import inspect
from typing import Optional, Tuple, List, Any

# Local imports
from game_core.entity_state import EntityStateList
from game_core.entity_definitions import to_type_from_classname, BaseEntity
from game_core import entity_definitions
import dill

# Constants
SAVE_FOLDER = '_save'
SAVE_FILE = 'save.pkl'
DEFAULT_CELL_SIZE = 50
DEFAULT_CAMERA_OFFSET = [0, 0]

# Build a type map from all subclasses of BaseEntity using class name
# This allows automatic mapping of entity type strings to their classes for save/load
def _build_entity_type_map() -> dict:
    """Dynamically build a map from type string to entity class."""
    return {
        to_type_from_classname(cls.__name__): cls
        for name, cls in inspect.getmembers(entity_definitions, inspect.isclass)
        if issubclass(cls, BaseEntity) and cls is not BaseEntity
    }

ENTITY_TYPE_MAP = _build_entity_type_map()

def ensure_save_folder() -> str:
    """Ensure the save folder exists and return its path."""
    save_folder = os.path.join(os.getcwd(), SAVE_FOLDER)
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    return save_folder

def save_game(
    entity_states: EntityStateList,
    camera_offset: Optional[List[int]] = None,
    cell_size: Optional[int] = None
) -> None:
    """Save the current game state to disk, including camera position and zoom level if provided."""
    save_folder = ensure_save_folder()
    save_path = os.path.join(save_folder, SAVE_FILE)
    save_data = {
        'entities': entity_states.to_list(),
        'camera_offset': camera_offset if camera_offset is not None else DEFAULT_CAMERA_OFFSET,
        'cell_size': cell_size if cell_size is not None else DEFAULT_CELL_SIZE
    }
    try:
        with open(save_path, 'wb') as save_file:
            dill.dump(save_data, save_file)
        print(f"Game saved to {save_path}")
    except Exception as e:
        print(f"Error saving game: {e}")

def load_game(
    grid: List[List[Any]]
) -> Tuple[EntityStateList, List[int], int]:
    """Load the game state from disk and populate the grid. Returns (entity_states, camera_offset, cell_size)."""
    save_folder = ensure_save_folder()
    save_path = os.path.join(save_folder, SAVE_FILE)
    if not os.path.exists(save_path):
        print("No save file found. Starting with an empty state.")
        return EntityStateList(), DEFAULT_CAMERA_OFFSET.copy(), DEFAULT_CELL_SIZE

    try:
        with open(save_path, 'rb') as save_file:
            data = dill.load(save_file)
    except Exception as e:
        print(f"Error loading save file: {e}")
        return EntityStateList(), DEFAULT_CAMERA_OFFSET.copy(), DEFAULT_CELL_SIZE

    if not data:
        return EntityStateList(), DEFAULT_CAMERA_OFFSET.copy(), DEFAULT_CELL_SIZE

    # Backward compatibility: support old save format
    entities_data = data['entities'] if 'entities' in data else data
    camera_offset = data.get('camera_offset', DEFAULT_CAMERA_OFFSET.copy())
    cell_size = data.get('cell_size', DEFAULT_CELL_SIZE)

    entity_states = EntityStateList.from_list(entities_data, ENTITY_TYPE_MAP)
    for entity_state in entity_states.entities:
        entity = entity_state.entity  # Use the real entity object
        y, x = entity.y, entity.x
        if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
            grid[y][x] = entity
        else:
            print(f"Warning: Entity at ({x}, {y}) out of grid bounds. Skipping grid placement.")
    print(f"Game loaded from {save_path}")
    return entity_states, camera_offset, cell_size
