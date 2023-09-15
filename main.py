from typing import List

SHIP_SIZES = [5, 3, 3, 2, 2]
BOARD_SIZE = 10


class GameState:
    def __init__(self):
        self.board = Board()


class Board:
    def __init__(self):
        self.board = [[BoardCell() for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]


class BoardCell:
    def __init__(self):
        self.checked = False
        self.hit = False

    def set_checked(self):
        self.checked = True

    def set_hit(self):
        self.checked = True
        self.hit = True


def ShipLogic(round: int, map, enemy_hp: int, hp: int, shot_sequence: List[(int, int)],
              did_previous_shot_hit: bool, storage: List) -> (int, int):
    game_state = None

    if len(storage) > 0:
        game_state = storage[0]
    else:
        game_state = GameState()
        storage.append(game_state)
