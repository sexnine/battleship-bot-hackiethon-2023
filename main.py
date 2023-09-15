from typing import List, Union, Literal

SHIP_SIZES = [5, 3, 3, 2, 2]
BOARD_SIZE = 10


class GameState:
    def __init__(self):
        self.board = Board()
        self.remaining_ship_sizes = SHIP_SIZES.copy()


class Coordinate:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    @staticmethod
    def from_hm_style(coord: (int, int)):
        return Coordinate(coord[0] - 1, coord[1] - 1)

    def to_hm_style(self):
        return self.x + 1, self.y + 1

    def is_valid(self):
        return 0 <= self.x < BOARD_SIZE and 0 <= self.y < BOARD_SIZE

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        return f"{chr(65 + self.x)}{self.y + 1}"

    def __repr__(self):
        return str(self)


class BoardCell:
    def __init__(self):
        self.checked = False
        self.hit = False
        self.confirmed_ship = False

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

        if cell.checked and (not cell.hit or cell.confirmed_ship):
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


def adjacent_coords(coordinate: Coordinate, filter_valid: bool = False, x_axis: bool = True, y_axis: bool = True) -> \
        List[Coordinate]:
    coords = []

    if x_axis:
        coords += [
            Coordinate(coordinate.x - 1, coordinate.y),
            Coordinate(coordinate.x + 1, coordinate.y),
        ]
    if y_axis:
        coords += [
            Coordinate(coordinate.x, coordinate.y - 1),
            Coordinate(coordinate.x, coordinate.y + 1),
        ]

    if filter_valid:
        coords = [x for x in coords if x.is_valid()]

    return coords


def weight_adjacent_cells(probability_table: List[List[int]], board: Board):
    coordinate_list = probability_table_to_sorted_coordinate_list(probability_table)
    coordinate_list = [x for x in coordinate_list if board.get_cell(x[0]).hit]
    print("weight_adjacent_cells coordinate_list: ", coordinate_list)

    for coordinate, _ in coordinate_list:
        coords_to_check = adjacent_coords(coordinate, True)

        print("coords_to_check: ", coords_to_check)

        coords_to_apply_weight_to = [x for x in coords_to_check if
                                     not board.get_cell(x).checked and probability_table[x.y][
                                         x.x] != 0]

        print("coords_to_apply_weight_to: ", coords_to_apply_weight_to)

        for coord in coords_to_apply_weight_to:
            probability_table[coord.y][coord.x] += 20


def probability_table_to_sorted_coordinate_list(probability_table: List[List[int]]) -> List[tuple[Coordinate, int]]:
    coordinate_list = []

    for y in range(len(probability_table)):
        for x in range(len(probability_table[y])):
            coordinate_list.append((Coordinate(x, y), probability_table[y][x]))

    coordinate_list.sort(key=lambda x: x[1], reverse=True)

    return coordinate_list


def get_grouped_coordinates(game_state: GameState, coordinate: Coordinate, axis: Literal["x", "y"],
                            ignore_list: set[Coordinate] = set()) -> set[Coordinate]:
    ret = {coordinate}

    adjacent = adjacent_coords(coordinate, True, axis == "x", axis == "y")
    # print(adjacent)
    adjacent = [x for x in adjacent if x not in ignore_list and game_state.board.get_cell(x).hit]
    # print(adjacent)

    for coord in adjacent:
        ret = ret.union(get_grouped_coordinates(game_state, coord, axis, ret))

    return ret


def confirm_ships(game_state: GameState):
    all_coordinates = [Coordinate(x, y) for x in range(BOARD_SIZE) for y in range(BOARD_SIZE)]
    hit_coords = [x for x in all_coordinates if
                  game_state.board.get_cell(x).hit and not game_state.board.get_cell(x).confirmed_ship]

    groups = []

    skip_coords_x = []
    skip_coords_y = []

    for coordinate in hit_coords:
        if coordinate not in skip_coords_x:
            bla = get_grouped_coordinates(game_state, coordinate, "x")
            skip_coords_x += list(bla)
            groups.append(bla)
        if coordinate not in skip_coords_y:
            bla = get_grouped_coordinates(game_state, coordinate, "y")
            skip_coords_y += list(bla)
            groups.append(bla)

    groups = [x for x in groups if len(x) > 1]

    print("groups: ", groups)

    # TODO: finish


def get_next_move(game_state: GameState) -> Coordinate:
    confirm_ships(game_state)

    probability_table = get_probability_table(game_state.board, game_state.remaining_ship_sizes)
    weight_adjacent_cells(probability_table, game_state.board)
    coordinate_list = probability_table_to_sorted_coordinate_list(probability_table)

    print(coordinate_list)

    return coordinate_list[0][0]


def ShipLogic(round_number: int, ship_map, enemy_hp: int, hp: int,  # Why not snake_case? :(
              shot_sequence: List[tuple[int, int]],
              did_previous_shot_hit: bool, storage: List) -> tuple[tuple[int, int], List]:
    try:
        game_state = None

        if len(storage) > 0 and storage[0] is not None:
            game_state = storage[0]
        else:
            game_state = GameState()
            storage.append(game_state)

        if len(shot_sequence) > 0:
            register_latest_move(game_state, shot_sequence, did_previous_shot_hit)

        move = get_next_move(game_state)

        return move.to_hm_style(), storage
    except Exception:
        return (1, 1), storage  # Will prompt a random move if an unexpected error occurs


def main():
    game_state = GameState()

    while True:
        move = get_next_move(game_state)

        print(f"\u001b[31m-> {move}\u001b[0m")

        user_input = input("Hit (h) / Miss (m) / Quit (q): ")
        was_hit = None

        match user_input.strip().lower():
            case "h":
                was_hit = True
            case "m":
                was_hit = False
            case "q":
                exit(0)
            case other:
                print(f"{other} not recognised, please try again.")
                continue

        game_state.board.get_cell(move).set_checked(was_hit)


if __name__ == "__main__":
    main()
