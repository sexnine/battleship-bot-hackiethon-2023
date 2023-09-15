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

    def __str__(self):
        return f"{chr(65 + self.x)}{self.y + 1}"

    def __repr__(self):
        return str(self)


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
        return self.board[coordinate.y][coordinate.x]


def register_latest_move(game_state: GameState, shot_sequence: List[tuple[int, int]], did_previous_shot_hit: bool):
    game_state.board.get_cell(Coordinate.from_hm_style(shot_sequence[-1])).set_checked(did_previous_shot_hit)


def set_probability(board: Board, probability_table: List[List[int]], ship_size: int, x: int, y: int,
                    inverted: bool = False):
    is_possible_placement = True

    for i in range(ship_size):
        if inverted:
            cell = board.get_cell(Coordinate(x, y + i))
        else:
            cell = board.get_cell(Coordinate(x + i, y))

        if cell.checked and not cell.hit:
            is_possible_placement = False
            break

    if is_possible_placement:
        for i in range(ship_size):
            if inverted:
                cell = board.get_cell(Coordinate(x, y + i))
            else:
                cell = board.get_cell(Coordinate(x + i, y))

            if cell.checked:
                continue

            if inverted:
                probability_table[y + i][x] += 1
            else:
                probability_table[y][x + i] += 1


def get_probability_table(board: Board, ship_sizes_to_check: List[int]) -> List[List[int]]:
    probability_table = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    for ship_size in ship_sizes_to_check:
        coords_to_check = list(range(BOARD_SIZE - ship_size + 1))

        for x in coords_to_check:
            for y in range(BOARD_SIZE):
                set_probability(board, probability_table, ship_size, x, y)
                set_probability(board, probability_table, ship_size, y, x, True)

    return probability_table


def probability_table_to_sorted_coordinate_list(probability_table: List[List[int]]) -> List[tuple[Coordinate, int]]:
    coordinate_list = []

    for y in range(len(probability_table)):
        for x in range(len(probability_table[y])):
            coordinate_list.append((Coordinate(x, y), probability_table[y][x]))

    coordinate_list.sort(key=lambda x: x[1], reverse=True)

    return coordinate_list


def get_next_move(game_state: GameState) -> Coordinate:
    probability_table = get_probability_table(game_state.board, SHIP_SIZES)
    coordinate_list = probability_table_to_sorted_coordinate_list(probability_table)

    print(coordinate_list)

    pass


def ShipLogic(round_number: int, ship_map, enemy_hp: int, hp: int, shot_sequence: List[tuple[int, int]],
              did_previous_shot_hit: bool, storage: List) -> tuple[tuple[int, int], List]:
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


def main():
    game_state = GameState()

    get_next_move(game_state)


if __name__ == "__main__":
    main()
