from enum import Enum
from tempfile import TemporaryFile
from typing import List, Tuple

#  Board layout:
#    0  1  2
#    3  4  5
#    6  7  8
#

UPPER_LEFT = 0
UPPER_MIDDLE = 1
UPPER_RIGHT = 2
MIDDLE_LEFT = 3
CENTER = 4
MIDDLE_RIGHT = 5
BOTTOM_LEFT = 6
BOTTOM_MIDDLE = 7
BOTTOM_RIGHT = 8

class Color(Enum):
    RED = 0
    GREEN = 1
    BLUE = 2
    YELLOW = 3

class BodyPart(Enum):
    HEAD = 0
    TAIL = 1

class Direction(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

def get_opposite(dir: Direction):
    return Direction((dir.value + 2) % 4)

class Frog:
    color: Color
    part: BodyPart

    def __init__(self, color: Color, part: BodyPart):
        self.color = color
        self.part = part

    def match(self, other):
        return self.color == other.color and self.part != other.part

    def __str__(self) -> str:
        return f'{self.color.name[:1]}{"H" if self.part.value == 0 else "T"}'

    def __repr__(self) -> str:
        return str(self)

class Card:
    frogs: List[Frog]

    def __init__(self, frogs: List[Frog]) -> None:
        self.frogs = frogs

    def get_frog(self, dir: Direction) -> Frog:
        return self.frogs[dir.value]

    def has_frog(self, color: Color, part: BodyPart):
        for frog in self.frogs:
            if frog.color == color and frog.part == part:
                return True
        return False

    def has_frog_antipart(self, color: Color, part: BodyPart):
        for frog in self.frogs:
            if frog.color == color and frog.part != part:
                return True
        return False

    def rotate(self):
        frogs = [self.frogs[-1]]
        frogs += self.frogs[:-1]
        self.frogs = frogs

    def __str__(self) -> str:
        return  f'  {self.frogs[0]}     \n' \
                f'{self.frogs[3]}  {self.frogs[1]}   \n' \
                f'  {self.frogs[2]}     \n' \

    def __repr__(self) -> str:
        return "".join([str(frog) for frog in self.frogs])


all_cards: List[Card] = [
    Card([Frog(Color.BLUE, BodyPart.TAIL), Frog(Color.YELLOW, BodyPart.HEAD), Frog(Color.RED, BodyPart.HEAD), Frog(Color.RED, BodyPart.TAIL)]),
    Card([Frog(Color.RED, BodyPart.TAIL), Frog(Color.GREEN, BodyPart.HEAD), Frog(Color.BLUE, BodyPart.HEAD), Frog(Color.YELLOW, BodyPart.HEAD)]),
    Card([Frog(Color.BLUE, BodyPart.TAIL), Frog(Color.BLUE, BodyPart.HEAD), Frog(Color.GREEN, BodyPart.HEAD), Frog(Color.RED, BodyPart.TAIL)]),
    Card([Frog(Color.BLUE, BodyPart.TAIL), Frog(Color.RED, BodyPart.HEAD), Frog(Color.GREEN, BodyPart.HEAD), Frog(Color.RED, BodyPart.HEAD)]),
    Card([Frog(Color.YELLOW, BodyPart.TAIL), Frog(Color.BLUE, BodyPart.HEAD), Frog(Color.GREEN, BodyPart.HEAD), Frog(Color.GREEN, BodyPart.TAIL)]),
    Card([Frog(Color.YELLOW, BodyPart.TAIL), Frog(Color.YELLOW, BodyPart.TAIL), Frog(Color.GREEN, BodyPart.TAIL), Frog(Color.RED, BodyPart.TAIL)]),
    Card([Frog(Color.YELLOW, BodyPart.HEAD), Frog(Color.BLUE, BodyPart.HEAD), Frog(Color.GREEN, BodyPart.HEAD), Frog(Color.YELLOW, BodyPart.HEAD)]),
    Card([Frog(Color.YELLOW, BodyPart.TAIL), Frog(Color.GREEN, BodyPart.TAIL), Frog(Color.YELLOW, BodyPart.HEAD), Frog(Color.BLUE, BodyPart.TAIL)]),
    Card([Frog(Color.GREEN, BodyPart.TAIL), Frog(Color.RED, BodyPart.TAIL), Frog(Color.BLUE, BodyPart.TAIL), Frog(Color.RED, BodyPart.HEAD)])
]

board: List[Card] = []

def get_empty_board():
    return [
        None, None, None, \
        None, None, None, \
        None, None, None  \
    ]

def print_board(board: List[Card]):
    def _print_sub_row(row):
        for sub_row in range(3):
            for card in row:
                if card:
                    print(card[sub_row], end="")
                else:
                    print("------", end="")
            print("")

    # Print first row
    row_cards = [str(card).split("\n") if card else None for card in board[:3]]
    _print_sub_row(row_cards)
    print("")

    # Print second row
    row_cards = [str(card).split("\n") if card else None for card in board[3:6]]
    _print_sub_row(row_cards)
    print("")

    # Print third row
    row_cards = [str(card).split("\n") if card else None for card in board[6:]]
    _print_sub_row(row_cards)
    print("")

    print("")

def get_possible_cards_from_frog(cards: List[Card], existing_frog: Frog):
    possible = []
    for card in cards:
        if card.has_frog_antipart(existing_frog.color, existing_frog.part):
            possible.append(card)
    return possible

check_cross_position = [
    (UPPER_MIDDLE, Direction.NORTH),
    (MIDDLE_RIGHT, Direction.EAST),
    (BOTTOM_MIDDLE, Direction.SOUTH),
    (MIDDLE_LEFT, Direction.WEST)
]

check_corner_position = [
    UPPER_LEFT, UPPER_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT
]

number_cross = 0
number_solves = 0


def solve_corners(board: List[Card], i_cards: List[Card], current_pos: int) -> bool:
    if i_cards == []:
        return True

    if current_pos == 4:
        return True
    
    check_corner = check_corner_position[current_pos]

    for p_card in i_cards:

        # Rotate
        rotation = 0
        test_card = p_card

        while rotation < 4:
            
            # Upper left
            if check_corner == UPPER_LEFT:
                east_frog = board[UPPER_MIDDLE].get_frog(Direction.WEST)
                south_frog = board[MIDDLE_LEFT].get_frog(Direction.NORTH)

                if test_card.get_frog(Direction.EAST).match(east_frog) and \
                    test_card.get_frog(Direction.SOUTH).match(south_frog):
                    # Card works

                    cards = i_cards.copy()
                    cards.remove(test_card)
                    board[check_corner] = test_card
                    if solve_corners(board, cards, current_pos+1):
                        return True


            # Upper right
            if check_corner == UPPER_RIGHT:
                west_frog = board[UPPER_MIDDLE].get_frog(Direction.EAST)
                south_frog = board[MIDDLE_RIGHT].get_frog(Direction.NORTH)


                if test_card.get_frog(Direction.WEST).match(west_frog) and \
                    test_card.get_frog(Direction.SOUTH).match(south_frog):
                    # Card works

                    cards = i_cards.copy()
                    cards.remove(test_card)
                    board[check_corner] = test_card
                    if solve_corners(board, cards, current_pos+1):
                        return True

            # Bottom left
            if check_corner == BOTTOM_LEFT:
                north_frog = board[MIDDLE_LEFT].get_frog(Direction.SOUTH)
                east_frog = board[BOTTOM_MIDDLE].get_frog(Direction.WEST)


                if test_card.get_frog(Direction.NORTH).match(north_frog) and \
                    test_card.get_frog(Direction.EAST).match(east_frog):
                    # Card works

                    cards = i_cards.copy()
                    cards.remove(test_card)
                    board[check_corner] = test_card
                    if solve_corners(board, cards, current_pos+1):
                        return True

            # Bottom right
            if check_corner == BOTTOM_RIGHT:
                north_frog = board[MIDDLE_RIGHT].get_frog(Direction.SOUTH)
                west_frog = board[BOTTOM_MIDDLE].get_frog(Direction.EAST)

                if test_card.get_frog(Direction.NORTH).match(north_frog) and \
                    test_card.get_frog(Direction.WEST).match(west_frog):
                    # Card works

                    cards = i_cards.copy()
                    cards.remove(test_card)
                    board[check_corner] = test_card
                    if solve_corners(board, cards, current_pos+1):
                        return True

            # Rotate card
            test_card.rotate()
            rotation += 1
    
    return False


def solve_cross(board: List[Card], i_cards: List[Card], current_pos: int) -> bool:
    if current_pos > 3:
        return True

    center_card = board[CENTER]
    pos, dir = check_cross_position[current_pos]
    dir_frog = center_card.get_frog(dir)

    possible_cards = get_possible_cards_from_frog(i_cards, dir_frog)

    p_card: Card
    for p_card in possible_cards:
        new_cards = i_cards.copy()
        new_cards.remove(p_card)

        p_card_direction = get_opposite(dir)
        p_card_frog = p_card.get_frog(p_card_direction)

        rotation = 0
        while rotation < 4:
            p_card_frog = p_card.get_frog(p_card_direction)

            if dir_frog.match(p_card_frog):
                # The opposite frog is a match

                board[pos] = p_card
                board_copy = board.copy()
                if solve_cross(board_copy, new_cards, current_pos+1):
                    # Time to solve for corners
                    if solve_corners(board_copy, new_cards, 0):
                        print("Solution:")
                        print_board(board_copy)
                        global number_solves
                        number_solves += 1
            
            p_card.rotate()
            rotation += 1
        
    return False


if __name__ == "__main__":
    test_no = 0
    for idx, center_card in enumerate(all_cards):
        cards = all_cards.copy()
        cards.pop(idx)

        board: List[Card] = get_empty_board()
        board[CENTER] = center_card
        
        if solve_cross(board, cards, 0):
            print_board(board)

    print("Done")
    print(f"Number of solves: {number_solves}")
