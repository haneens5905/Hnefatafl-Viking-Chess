from board import *
from moves import *


def apply_move(board, from_row, from_col, to_row, to_col):
    # moves a piece from (from_row, from_col) to (to_row, to_col)
    # immediately checks for any captures at the new position
    # state mutation is never split — everything happens in one call

    # get the piece being moved
    piece = get_piece(board, from_row, from_col)

    # move the piece to the destination and clear the source square
    board[to_row][to_col] = piece
    board[from_row][from_col] = EMPTY

    # determine which player just moved
    if piece == ATTACKER:
        player = ATTACKER
    else:
        player = DEFENDER

    # immediately check for any captures triggered by this move
    check_captures(board, to_row, to_col, player)


def check_game_over(board):
    # returns 'defender' if the king escaped to a corner
    # returns 'attacker' if the king is fully surrounded
    # returns None if the game is still ongoing

    # check escape first — king on corner means defenders win
    if check_king_escaped(board):
        return 'defender'

    # check if the king is captured
    if check_king_captured(board):
        return 'attacker'

    # game is still going
    return None


def display_board_with_legend(board):
    # prints the board with spacing around it
    print()
    print_board(board)
    print()


def validate_move(move_input, all_valid_moves):
    # parses and validates a move string in the format "row1 col1 row2 col2"
    # returns (from_row, from_col, to_row, to_col) if valid, or None if not

    try:
        parts = move_input.split()

        # check if we have exactly 4 numbers
        if len(parts) != 4:
            print("  ERROR: Invalid format. Use: row1 col1 row2 col2")
            return None

        from_row = int(parts[0])
        from_col = int(parts[1])
        to_row = int(parts[2])
        to_col = int(parts[3])

        # check if all coordinates are within the board
        if not (is_within_bounds(from_row, from_col) and is_within_bounds(to_row, to_col)):
            print("  ERROR: Coordinates out of bounds (0-10).")
            return None

        move = (from_row, from_col, to_row, to_col)

        # check if the move is actually legal
        if move not in all_valid_moves:
            print("  ERROR: That move is not legal.")
            return None

        return move

    except ValueError:
        print("  ERROR: Invalid input. Please enter four integers.")
        return None


def get_human_move(board, player):
    # keeps asking the human for a move until a valid one is entered

    # get all valid moves for this player
    all_valid_moves = get_all_moves(board, player)

    if not all_valid_moves:
        print("  WARNING: No valid moves available!")
        return None

    while True:
        player_name = "Attackers" if player == ATTACKER else "Defenders"
        move_input = input(f"\n{player_name}'s turn. Enter move (row1 col1 row2 col2): ").strip()

        move = validate_move(move_input, all_valid_moves)
        if move is not None:
            return move


def get_computer_move(board, player, difficulty):
    # uses the alpha-beta AI to get the best move for the computer
    # difficulty controls how many moves ahead the AI looks

    # map difficulty level to search depth
    depth_map = {
        'easy': 1,
        'medium': 3,
        'hard': 5
    }

    depth = depth_map.get(difficulty.lower(), 3)

    # call the alpha-beta function from person 5
    try:
        from alpha_beta import get_best_move
        move = get_best_move(board, player, depth)
        return move
    except ImportError:
        # fallback to random move if alpha_beta is not available
        print("  AI module not found. Using random move.")
        all_valid_moves = get_all_moves(board, player)
        if all_valid_moves:
            import random
            return random.choice(all_valid_moves)
        return None


def format_move_display(from_row, from_col, to_row, to_col):
    # formats a move as a readable string like "(3,5) -> (3,8)"
    return f"({from_row},{from_col}) -> ({to_row},{to_col})"


def main():
    # main game loop — handles setup, turn alternation, and end detection

    print("\n" + "=" * 60)
    print("  HNEFATAFL - Strategic Board Game")
    print("=" * 60)
    print()
    print("The King (K) must reach a corner (*) to escape.")
    print("Attackers (A) must surround the King to capture him.")
    print("Defenders (D) must protect the King until he escapes.")
    print()

    # ask human which side they want to play
    while True:
        side_choice = input("Which side do you want? (attacker/defender): ").strip().lower()
        if side_choice in ['attacker', 'defender', 'a', 'd']:
            human_side = ATTACKER if side_choice in ['attacker', 'a'] else DEFENDER
            break
        print("  ERROR: Please enter 'attacker' or 'defender'.")

    # the computer plays the opposite side
    computer_side = DEFENDER if human_side == ATTACKER else ATTACKER

    # ask for difficulty level
    while True:
        difficulty = input("Choose difficulty (easy/medium/hard): ").strip().lower()
        if difficulty in ['easy', 'medium', 'hard', 'e', 'm', 'h']:
            difficulty = {'e': 'easy', 'm': 'medium', 'h': 'hard'}.get(difficulty, difficulty)
            break
        print("  ERROR: Please enter 'easy', 'medium', or 'hard'.")

    # create and display the starting board
    board = create_initial_board()
    print("\n" + "=" * 60)
    print("  Initial Board")
    print("=" * 60)
    display_board_with_legend(board)

    # attackers always go first
    current_player = ATTACKER
    move_count = 0

    # main game loop
    while True:
        move_count += 1

        # figure out if it is the human or computer's turn
        is_human_turn = (current_player == human_side)

        # build a label showing who is playing this turn
        if is_human_turn and current_player == ATTACKER:
            player_name = "Attackers (Human)"
        elif is_human_turn and current_player == DEFENDER:
            player_name = "Defenders (Human)"
        elif not is_human_turn and current_player == ATTACKER:
            player_name = "Attackers (Computer)"
        else:
            player_name = "Defenders (Computer)"

        print(f"\n-- Move {move_count}: {player_name}'s Turn --")

        # get the move from human or computer
        if is_human_turn:
            move = get_human_move(board, current_player)
            if move is None:
                print("  No valid moves available. Game Over!")
                break
        else:
            print(f"  (Difficulty: {difficulty.capitalize()}, Thinking...)")
            move = get_computer_move(board, current_player, difficulty)
            if move is None:
                print("  Computer has no valid moves. Game Over!")
                break
            from_row, from_col, to_row, to_col = move
            print(f"  Computer plays: {format_move_display(from_row, from_col, to_row, to_col)}")

        # apply the move to the board
        from_row, from_col, to_row, to_col = move
        apply_move(board, from_row, from_col, to_row, to_col)

        # show the updated board
        display_board_with_legend(board)

        # check if the game has ended
        winner = check_game_over(board)

        if winner is not None:
            print("=" * 60)
            if winner == 'defender':
                print("Defenders Win! The King escaped to a corner!")
            else:
                print("Attackers Win! The King has been captured!")
            print("=" * 60)
            print(f"\nGame ended after {move_count} moves.")
            break

        # switch to the other player
        current_player = DEFENDER if current_player == ATTACKER else ATTACKER


# run the game when this file is executed directly
if __name__ == "__main__":
    main()