from typing import List

SHIP_SIZES = [5, 3, 3, 2, 2]
BOARD_SIZE = 10


class GameState:
    def __init__(self):
        self.board = Board()


class Coordinate:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    @staticmethod
    def from_hm_style(coord: (int, int)):
        return Coordinate(coord[0] - 1, coord[1] - 1)

    def to_hm_style(self):
        return self.x + 1, self.y + 1


class BoardCell:
    def __init__(self):
        self.checked = False
        self.hit = False

    def set_checked(self, hit: bool = False):
        self.checked = True
        self.hit = hit

    def set_hit(self):
        self.checked = True
        self.hit = True


class Board:
    def __init__(self):
        self.board = [[BoardCell() for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    def get_cell(self, coordinate: Coordinate) -> BoardCell:
        return self.board[coordinate.x][coordinate.y]


def register_latest_move(game_state: GameState, shot_sequence: List[(int, int)], did_previous_shot_hit: bool):
    game_state.board.get_cell(Coordinate.from_hm_style(shot_sequence[-1])).set_checked(did_previous_shot_hit)


def get_next_move(game_state: GameState) -> Coordinate:
    pass


def ShipLogic(round_number: int, ship_map, enemy_hp: int, hp: int, shot_sequence: List[(int, int)],
              did_previous_shot_hit: bool, storage: List) -> ((int, int), List):
    game_state = None

    if len(storage) > 0:
        game_state = storage[0]
    else:
        game_state = GameState()
        storage.append(game_state)

    if len(shot_sequence) > 0:
        register_latest_move(game_state, shot_sequence, did_previous_shot_hit)

    move = get_next_move(game_state)

    return move.to_hm_style(), storage
