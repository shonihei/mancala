import copy

class Move:
        def __init__(self, player_index, tile_index):
            self.player_index = player_index
            self.tile_index = tile_index

        def __str__(self):
            return f"Player index: {self.player_index}, Tile index: {self.tile_index}"

class Board:

    def __init__(self, initial_board_state, initial_score = [0, 0]):
        self.board = initial_board_state
        self.score = initial_score
        self.tile_count = len(self.board[0])

    def move(self, move):
        if self.board[move.player_index][move.tile_index] == 0:
            raise ValueError('Cannot move from an empty tile')
        
        num_beans = self.board[move.player_index][move.tile_index]
        self.board[move.player_index][move.tile_index] = 0

        player_side = move.player_index
        cur_tile_index = move.tile_index
        while num_beans:
            # at the final tile
            if cur_tile_index == self.tile_count - 1:
                if player_side == move.player_index:
                    num_beans -= 1
                    self.score[move.player_index] += 1
                    if num_beans == 0:
                        # the current player can go again
                        return True
                player_side = 1 if player_side == 0 else 0
                cur_tile_index = -1
            else:
                self.board[player_side][cur_tile_index + 1] += 1
                num_beans -= 1
                cur_tile_index += 1

            if num_beans == 0 and self.board[player_side][cur_tile_index] != 1:
                num_beans = self.board[player_side][cur_tile_index]
                self.board[player_side][cur_tile_index] = 0
        return False

    def get_beans(self, player, tile_index):
        return self.board[player][tile_index]

    def get_score(self, player):
        return self.score[player]

    def make_copy(self):
        return Board(copy.deepcopy(self.board), copy.deepcopy(self.score))

    def is_finished(self):
        return True if sum(self.board[0]) == 0 or sum(self.board[1]) == 0 else False
    
    def __str__(self):
        s = f'({self.score[1]}) '
        for beans in reversed(self.board[1]):
            s += str(beans) + " "
        s += "\n "
        for beans in self.board[0]:
            s += str(beans) + " "
        s += f'({self.score[0]})'
        return s

class Player:
    def __init__(self, board: Board, player_index):
        self.board = board
        self.player_index = player_index

    def make_move(self):
        tile_index = int(input('Type in your move: '))
        return Move(self.player_index, tile_index)
    
    def report_opponent_move(self, opponent_move_index):
        pass

# Mr. Bean
class SmartPlayer(Player):

    class Node:
        def __init__(self, board: Board, move: Move):
            # current state of the board
            self.board = board
            # move used to get to self.board
            self.move = move
            # all possible next state that can be played by the opponent from
            # self.board
            self.children = []
            # all possible consecutive plays that can be played from this board
            self.consecutive_moves = []
        
        def has_children(self):
            return len(self.children) == 0

    def __init__(self, board: Board, player_index, look_ahead):
        super(SmartPlayer, self).__init__(board, player_index)
        self.look_ahead = look_ahead
        self.opponent_index = 1 if self.player_index == 0 else 0
        self.is_tree_stale = True
    
    def initialize_tree(self):
        print("Generating new tree, please wait...")
        initial_state = self.board.make_copy()
        self.root = self.generate_tree(initial_state, None, self.look_ahead, float('-inf'), float('inf'), True)
        print("Finished generating tree")

    def pick_best_move(self):
        if self.is_tree_stale:
            self.initialize_tree()
        max_score = self.root.score
        for consecutive_move in self.root.consecutive_moves:
            if consecutive_move.score == max_score:
                self.root = consecutive_move
                self.is_tree_stale = False
                return consecutive_move.move
        # it's possible that there's no way to do a consecutive move or
        # letting the opponent go is the best choice.
        for child in self.root.children:
            if child.score == max_score:
                self.is_tree_stale = True
                return child.move
        raise ValueError("Generated a faulty tree")

    def make_move(self):
        best_move = self.pick_best_move()
        print(f"Smart Player is doing this move: {best_move}")
        return best_move

    def generate_potential_moves(self, current_board: Board, for_player: int):
        moves = []
        for tile_index, num_beans in enumerate(current_board.board[for_player]):
            if num_beans:
                board_copy = current_board.make_copy()
                moves.append((board_copy, Move(for_player, tile_index)))
        return moves

    def generate_tree(self, board: Board, move: Move, depth, alpha, beta, maximizing_player):
        node = self.Node(board, move)
        if depth == 0 or board.is_finished():
            node.score = self.get_heuristic_score(board)
            return node
        if maximizing_player:
            value = float('-inf')
            explore_stack = self.generate_potential_moves(board, self.player_index)
            while explore_stack:
                (board_copy, move) = explore_stack.pop()

                # make the move
                can_go_again = board_copy.move(move)

                if can_go_again:
                    consecutive_move_node = self.generate_tree(board_copy, move, depth, alpha, beta, True)
                    node.consecutive_moves.append(consecutive_move_node)
                    value = max(value, consecutive_move_node.score)
                else:
                    child_node = self.generate_tree(board_copy, move, depth - 1, alpha, beta, False)
                    node.children.append(child_node)
                    value = max(value, child_node.score)
                
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            node.score = value
            return node
        else:
            value = float('inf')
            explore_stack = self.generate_potential_moves(board, self.opponent_index)
            while explore_stack:
                (board_copy, move) = explore_stack.pop()

                # make the move
                can_go_again = board_copy.move(move)

                if can_go_again:
                    consecutive_move_node = self.generate_tree(board_copy, move, depth, alpha, beta, False)
                    node.consecutive_moves.append(consecutive_move_node)
                    value = min(value, consecutive_move_node.score)
                else:
                    child_node = self.generate_tree(board_copy, move, depth - 1, alpha, beta, True)
                    node.children.append(child_node)
                    value = min(value, child_node.score)

                beta = min(beta, value)
                if beta <= alpha:
                    break
            node.score = value
            return node

    def get_heuristic_score(self, board: Board):
        opponent = 1 if self.player_index == 0 else 0
        relative_score = board.get_score(self.player_index) - board.get_score(opponent)
        if board.is_finished():
            if relative_score == 0:
                return 0
            elif relative_score > 0:
                return float('inf')
            else:
                return float('-inf')
        return relative_score

class Game:
    def __init__(self, board, players):
        self.game_board = board
        self.players = players
        self.current_player = 0

    def start(self):
        print("Starting game...")
        print(f"Initial board state:\n{self.game_board}")
        while not self.game_board.is_finished():
            player_move = self.players[self.current_player].make_move()
            try:
                can_go_again = self.game_board.move(player_move)
                print(f"Moved:\n{self.game_board}")
                if can_go_again:
                    print(f"Player {self.current_player} can go again!")
                    continue
                else:
                    self.current_player = 1 if self.current_player == 0 else 0
                    print(f"Player {self.current_player}'s turn")
            except ValueError:
                print(f"Invalid move, try a different tile")
        print("Game finished. Final Score:")
        print(f"Player 0: {self.game_board.get_score(0)}")
        print(f"Player 1: {self.game_board.get_score(1)}")
    
    @staticmethod
    def make_board(tile_count, beans_per_tile):
        return Board([[beans_per_tile for i in range(tile_count)] for i in range(2)])

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_tiles_per_player", help="Number of tiles on each player's sides. 6 by default", type=int, default=6)
    parser.add_argument("--num_beans_per_tile", help="Number of beans per tile. 4 by default", type=int, default=4)
    parser.add_argument("--ai_first", help="Whether or not the AI player goes first. False by default", action="store_true", default=False)
    parser.add_argument("--num_lookahead", help="How many lookaheads the AI player will do. 5 by default", type=int, default=5)
    args = parser.parse_args()

    b = Game.make_board(args.num_tiles_per_player, args.num_beans_per_tile)
    g = Game(b, [Player(b, 0), SmartPlayer(b, 1, 5)])
    if args.ai_first:
      g = Game(b, [SmartPlayer(b, 0, args.num_lookahead), Player(b, 1)])
    g.start()