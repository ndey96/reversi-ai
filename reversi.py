from copy import deepcopy
import sys, traceback, os, datetime

BOARD_DIRECTIONS = (
    (1,0),
    (1,-1),
    (0,-1),
    (-1,-1),
    (-1,0),
    (-1,1),
    (0,1),
    (1,1),
)

def is_in_board(board, x, y):
    board_width, board_height = get_board_dims(board)
    return 0 <= x < board_width and 0 <= y < board_height

def is_valid_move(board, player, x, y):
    if not is_in_board(board, x, y) or board[y][x] != 0:
        return None
    other_player = get_other_player(player)

    board[y][x] = player # Temporarily place tile at x,y
    tiles_to_flip = []
    global BOARD_DIRECTIONS
    for x_delta, y_delta in BOARD_DIRECTIONS:
        x_curr = x + x_delta
        y_curr = y + y_delta
        if not is_in_board(board, x_curr, y_curr):
            continue
        tile_buffer = []
        while board[y_curr][x_curr] == other_player:
            tile_buffer.append((x_curr, y_curr))
            x_curr += x_delta
            y_curr += y_delta
            if not is_in_board(board, x_curr, y_curr):
                break
        if is_in_board(board, x_curr, y_curr) and board[y_curr][x_curr] == player:
            tiles_to_flip.extend(tile_buffer)
    board[y][x] = 0 # Remove temporary tile at x,y
    if len(tiles_to_flip) == 0:
        return None
    return tiles_to_flip

def get_board_dims(board):
    # returns (cols, rows)
    return (len(board[0]), len(board))

def get_valid_moves(board, player):
    cols, rows = get_board_dims(board)
    moves_dict = {}
    for x in range(cols):
        for y in range(rows):
            if board[y][x] == 0:
                tiles_to_flip = is_valid_move(board, player, x, y)
                if tiles_to_flip != None:
                    moves_dict[(x,y)] = tiles_to_flip
    return moves_dict

def flip_tiles_on_board(board, player, tiles_to_flip):
    for x,y in tiles_to_flip:
        board[y][x] = player

def get_other_player(player):
    if player == 1:
        return 2
    return 1

def evaluate_board(board, player):
    cols, rows = get_board_dims(board)
    other_player = get_other_player(player)
    num_tiles_for_player = 0
    num_tiles_for_other_player = 0
    for x in range(cols):
        for y in range(rows):
            tile = board[y][x]
            if tile == player:
                num_tiles_for_player += 1
            if tile == other_player:
                num_tiles_for_other_player += 1
    return num_tiles_for_player - num_tiles_for_other_player

class Node(object):
    def __init__(self):
        self.children = []
        self.parent = None
        self.eval_val = None
        self.propagated_val = None
        self.move = None # (x, y, player)
        self.board = None

def get_num_of_parent_nodes(node):
    depth = 0
    curr_node = node
    while curr_node.parent != None:
        depth += 1
        curr_node = curr_node.parent
    return depth

def get_num_of_child_nodes(node):
    depth = 0
    curr_node = node
    while curr_node.children != []:
        depth += 1
        curr_node = curr_node.children[0]
    return depth

def print_board(board):
    cols, rows = get_board_dims(board)
    for y in range(rows):
        line = '|'
        for x in range(cols):
            line += str(board[y][x]) + '|'
        print(line)

def build_tree(node, board, player, depth_limit=None, curr_player=None):
    if depth_limit != None and get_num_of_parent_nodes(node) >= depth_limit:
        return
    if curr_player == None:
        curr_player = player
    moves_dict = get_valid_moves(board, curr_player)
    for x,y in moves_dict.keys():
        board_copy = deepcopy(board)
        board_copy[y][x] = curr_player # Place player's tile at x,y
        flip_tiles_on_board(board_copy, curr_player, moves_dict[(x,y)])

        new_node = Node()
        new_node.parent = node
        new_node.eval_val = evaluate_board(board_copy, player)
        new_node.move = (x, y, curr_player)
#         new_node.board = board_copy # For debugging purposes
        node.children.append(new_node)

        build_tree(new_node, board_copy, player, depth_limit, curr_player=get_other_player(curr_player))

def get_path_from_parent(node):
    path_to_parent = []
    curr = node
    while curr != None:
        path_to_parent.append(curr.move)
        curr = curr.parent
    return list(reversed(path_to_parent))[1:]


class AI:
    def __init__(self):
        self.best_score = float("-inf")
        self.best_path = []
        self.parent_node = Node()

    def minimax(self):
        self._minimax(self.parent_node)

    def _minimax(self, node):
        if len(node.children) and node.children[0].children == []:
            local_min = float("inf")
            min_node = None
            for child in node.children:
                if child.eval_val < self.best_score: # alpha-beta pruning
                    local_min = float("-inf")
                    break
                if child.eval_val < local_min:
                    local_min = child.eval_val
                    min_node = child
            if local_min > self.best_score:
                self.best_score = local_min
                self.best_path = get_path_from_parent(min_node)
        else:
            for child in node.children:
                self._minimax(child)

def get_cartesian_from_standard(standard):
    return (ord(standard[0]) - 97, int(standard[1]) - 1)

def get_standard_from_cartesian(cartesian):
    x,y = cartesian
    return str(unichr(x + 97)) + str(y + 1)

AVG_TIMES = [2, 8, 250, 3700, 15000, 75000] # Milliseconds
def get_depth_from_time(secs):
    time_limit = secs * 1000
    depth_limit = 6 # Default value in case time_limit exceeds all AVG_TIMES
    for idx, time in enumerate(AVG_TIMES):
        if time > time_limit:
            depth_limit = idx
            break
    return depth_limit

class Game:
    def __init__(self):
        self.board = [
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,1,2,0,0,0],
            [0,0,0,2,1,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0]
        ]
        self.curr_player = 1
        self.human = None
        self.ai = None
        self.depth_limit = None

    def game_over(self):
        c1, c2 = 0, 0
        cols, rows = get_board_dims(self.board)
        for x in range(cols):
            for y in range(rows):
                if self.board[y][x] == 1:
                    c1 += 1
                if self.board[y][x] == 2:
                    c2 += 1
        if c1 > c2:
            print('Player 1 wins with ' + str(c1) + ' pieces!')
        elif c2 > c1:
            print('Player 2 wins with ' + str(c2) + ' pieces!')
        else:
            print('Game tied!')
        sys.exit(0)

    def flip_tiles(self, tiles_to_flip):
        for x,y in tiles_to_flip:
            self.board[y][x] = self.curr_player

    def make_move(self, move, tiles_to_flip):
        x,y = move
        self.board[y][x] = self.curr_player # Place player's tile at x,y
        self.flip_tiles(tiles_to_flip)

    def print_board(self):
        cols, rows = get_board_dims(self.board)
        print(' a b c d e f g h')
        for y in range(rows):
            line = '|'
            for x in range(cols):
                line += str(self.board[y][x]) + '|'
            line += ' ' + str(y+1)
            print(line)

    def ai_turn(self):
        self.print_board()
        moves_dict = get_valid_moves(self.board, self.ai)
        ai = AI()
        #time1 = datetime.datetime.now()
        build_tree(node=ai.parent_node, board=self.board, player=self.ai, depth_limit=self.depth_limit, curr_player=self.curr_player)
        ai.minimax()
        #time2 = datetime.datetime.now()
        #delta = time2-time1
        x,y,_ = ai.best_path[0]
        best_move = (x,y)
        self.make_move(best_move, moves_dict[best_move])

    def human_turn(self):
        self.print_board()
        moves_dict = get_valid_moves(self.board, self.human)
        possible_moves_str = 'Possible moves: '
        for cart in moves_dict.keys():
            possible_moves_str += get_standard_from_cartesian(cart) + ' '
        print(possible_moves_str)

        move_str = ''
        move = None
        while True:
            move_str = raw_input('Please enter move: ')
            if len(move_str) == 2:
                move = get_cartesian_from_standard(move_str)
                if move in moves_dict:
                    break
            print('Move not valid!')
            print(possible_moves_str)
        self.make_move(move, moves_dict[move])

    def board_full(self):
        cols, rows = get_board_dims(self.board)
        for x in range(cols):
            for y in range(rows):
                if self.board[y][x] == 0:
                    return False
        return True

    def game_is_not_over(self):
        human_moves = get_valid_moves(self.board, self.human)
        ai_moves = get_valid_moves(self.board, self.ai)
        return len(human_moves) or len(ai_moves)

def main():
    try:
        game = Game()
        print('Welcome to Reversi!')
        game.human = int(raw_input('Please select player (1/2): '))
        game.ai = get_other_player(game.human)
        time_limit = int(raw_input('Please specify time limit (in seconds): '))
        game.depth_limit = get_depth_from_time(time_limit)
        while game.game_is_not_over():
            os.system('clear')
            print('Player ' + str(game.curr_player) + "'s turn!")
            if game.curr_player == game.human:
                game.human_turn()
            if game.curr_player == game.ai:
                game.ai_turn()
            game.curr_player = get_other_player(game.curr_player)
        game.game_over()

    except KeyboardInterrupt:
        print('Exiting game...')
        sys.exit(0)

if __name__ == "__main__":
    main()
