import sys
import math

# -------------------------------------------------------
# make sure all imports resolve correctly
# -------------------------------------------------------
from board import *
from moves import *
from game import *
from utility import *
import alpha_beta as ab

passed = 0
failed = 0

def test(name, condition):
    global passed, failed
    if condition:
        print(f'  PASS: {name}')
        passed += 1
    else:
        print(f'  FAIL: {name}')
        failed += 1

# ============================================================
print('=' * 60)
print('SECTION 1: BOARD.PY')
print('=' * 60)

print()
print('--- constants ---')
test('EMPTY==0', EMPTY == 0)
test('ATTACKER==1', ATTACKER == 1)
test('DEFENDER==2', DEFENDER == 2)
test('KING==3', KING == 3)
test('BOARD_SIZE==11', BOARD_SIZE == 11)
test('THRONE==(5,5)', THRONE == (5, 5))
test('4 corners', len(CORNERS) == 4)
test('(0,0) corner', (0, 0) in CORNERS)
test('(0,10) corner', (0, 10) in CORNERS)
test('(10,0) corner', (10, 0) in CORNERS)
test('(10,10) corner', (10, 10) in CORNERS)
test('(5,5) not corner', (5, 5) not in CORNERS)
test('(0,5) not corner', (0, 5) not in CORNERS)

print()
print('--- create_initial_board ---')
board = create_initial_board()
att = sum(1 for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if board[r][c] == ATTACKER)
dff = sum(1 for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if board[r][c] == DEFENDER)
kng = sum(1 for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if board[r][c] == KING)
test('24 attackers', att == 24)
test('12 defenders', dff == 12)
test('1 king', kng == 1)
test('11 rows', len(board) == 11)
test('11 cols per row', all(len(r) == 11 for r in board))
test('king at (5,5)', board[5][5] == KING)
test('37 total pieces', att + dff + kng == 37)
test('corners empty at start', all(board[r][c] == EMPTY for r, c in CORNERS))
for pos in [(0,3),(0,4),(0,5),(0,6),(0,7),(1,5),(10,3),(10,4),(10,5),(10,6),(10,7),(9,5),(3,0),(4,0),(5,0),(6,0),(7,0),(5,1),(3,10),(4,10),(5,10),(6,10),(7,10),(5,9)]:
    test(f'attacker at {pos}', board[pos[0]][pos[1]] == ATTACKER)
for pos in [(3,5),(4,5),(6,5),(7,5),(5,3),(5,4),(5,6),(5,7),(4,4),(4,6),(6,4),(6,6)]:
    test(f'defender at {pos}', board[pos[0]][pos[1]] == DEFENDER)

print()
print('--- copy_board ---')
board = create_initial_board()
copy = copy_board(board)
test('copy matches original', all(copy[r][c] == board[r][c] for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)))
copy[5][5] = EMPTY
test('original unaffected', board[5][5] == KING)
test('copy changed', copy[5][5] == EMPTY)
copy[0][0] = ATTACKER
test('original corner unaffected', board[0][0] == EMPTY)
copy2 = copy_board(board)
copy2[0][3] = EMPTY
test('multiple copies independent', board[0][3] == ATTACKER)

print()
print('--- helpers ---')
board = create_initial_board()
test('get_piece king', get_piece(board, 5, 5) == KING)
test('get_piece attacker', get_piece(board, 0, 3) == ATTACKER)
test('get_piece defender', get_piece(board, 3, 5) == DEFENDER)
test('get_piece empty', get_piece(board, 2, 2) == EMPTY)
test('is_empty true', is_empty(board, 2, 2))
test('is_empty false occupied', not is_empty(board, 5, 5))
test('is_corner (0,0)', is_corner(0, 0))
test('is_corner (10,10)', is_corner(10, 10))
test('is_corner false (5,5)', not is_corner(5, 5))
test('is_corner false (0,1)', not is_corner(0, 1))
test('is_throne (5,5)', is_throne(5, 5))
test('is_throne false (5,4)', not is_throne(5, 4))
test('is_throne false (0,0)', not is_throne(0, 0))
test('in_bounds (0,0)', is_within_bounds(0, 0))
test('in_bounds (10,10)', is_within_bounds(10, 10))
test('out_bounds (-1,0)', not is_within_bounds(-1, 0))
test('out_bounds (0,-1)', not is_within_bounds(0, -1))
test('out_bounds (11,0)', not is_within_bounds(11, 0))
test('out_bounds (0,11)', not is_within_bounds(0, 11))
test('out_bounds (11,11)', not is_within_bounds(11, 11))
test('is_king true', is_king(board, 5, 5))
test('is_king false attacker', not is_king(board, 0, 3))
test('find_king (5,5)', find_king(board) == (5, 5))
b = create_initial_board()
b[5][5] = EMPTY
test('find_king None', find_king(b) is None)
b2 = create_initial_board()
b2[5][5] = EMPTY
b2[2][2] = KING
test('find_king relocated', find_king(b2) == (2, 2))

print()
print('--- check_king_escaped ---')
board = create_initial_board()
test('not escaped at start', not check_king_escaped(board))
for corner in CORNERS:
    b = create_initial_board()
    b[5][5] = EMPTY
    b[corner[0]][corner[1]] = KING
    test(f'escaped at {corner}', check_king_escaped(b))
b = create_initial_board()
b[5][5] = EMPTY
test('no king = false', not check_king_escaped(b))
b2 = create_initial_board()
b2[5][5] = EMPTY
b2[2][2] = KING
test('not escaped mid-board', not check_king_escaped(b2))

print()
print('--- check_king_captured ---')
board = create_initial_board()
test('not captured at start', not check_king_captured(board))
b = create_initial_board()
b[5][5] = EMPTY
b[3][3] = KING
b[2][3] = ATTACKER
b[4][3] = ATTACKER
b[3][2] = ATTACKER
b[3][4] = ATTACKER
test('4 attackers = captured', check_king_captured(b))
b2 = create_initial_board()
b2[5][5] = EMPTY
b2[0][3] = KING
b2[1][3] = ATTACKER
b2[0][2] = ATTACKER
b2[0][4] = ATTACKER
test('wall + 3 attackers = captured', check_king_captured(b2))
b3 = create_initial_board()
b3[5][5] = EMPTY
b3[5][0] = KING
b3[4][0] = ATTACKER
b3[6][0] = ATTACKER
b3[5][1] = ATTACKER
test('left wall + 3 attackers = captured', check_king_captured(b3))
b4 = create_initial_board()
b4[5][5] = EMPTY
b4[0][1] = KING
b4[1][1] = ATTACKER
b4[0][2] = ATTACKER
test('near corner + 2 attackers = captured', check_king_captured(b4))
b5 = create_initial_board()
b5[5][5] = EMPTY
b5[5][4] = KING
b5[4][4] = ATTACKER
b5[6][4] = ATTACKER
b5[5][3] = ATTACKER
test('empty throne = hostile', check_king_captured(b5))
b6 = create_initial_board()
b6[5][5] = EMPTY
b6[0][0] = KING
test('king on corner not captured', not check_king_captured(b6))
b7 = create_initial_board()
b7[5][5] = EMPTY
test('no king = captured', check_king_captured(b7))
b8 = create_initial_board()
b8[5][5] = EMPTY
b8[3][3] = KING
b8[2][3] = ATTACKER
b8[4][3] = ATTACKER
b8[3][2] = ATTACKER
test('one free side = not captured', not check_king_captured(b8))

# ============================================================
print()
print('=' * 60)
print('SECTION 2: MOVES.PY')
print('=' * 60)

print()
print('--- get_valid_moves ---')
board = create_initial_board()
test('surrounded king no moves', get_valid_moves(board, 5, 5) == [])
test('fully blocked attacker no moves', get_valid_moves(board, 0, 5) == [])
moves = get_valid_moves(board, 1, 5)
test('attacker has moves', len(moves) > 0)
test('all in bounds', all(is_within_bounds(r, c) for r, c in moves))
test('no diagonals', all(r == 1 or c == 5 for r, c in moves))
test('no landing on pieces', all(is_empty(board, r, c) for r, c in moves))
b = create_initial_board()
b[5][3] = EMPTY
b[5][4] = EMPTY
b[5][5] = EMPTY
b[4][4] = EMPTY
b[6][4] = EMPTY
b[5][2] = ATTACKER
moves = get_valid_moves(b, 5, 2)
test('attacker blocked from throne', (5, 5) not in moves)
test('attacker can reach before throne', (5, 4) in moves)
b2 = create_initial_board()
b2[5][5] = EMPTY
b2[5][3] = KING
b2[5][4] = EMPTY
test('king can stop on throne', (5, 5) in get_valid_moves(b2, 5, 3))
b3 = create_initial_board()
b3[0][4] = EMPTY
b3[0][3] = EMPTY
b3[0][2] = EMPTY
b3[0][1] = EMPTY
b3[0][5] = ATTACKER
test('attacker blocked from corner', (0, 0) not in get_valid_moves(b3, 0, 5))
b4 = create_initial_board()
b4[5][5] = EMPTY
b4[0][2] = KING
b4[0][1] = EMPTY
test('king can reach corner', (0, 0) in get_valid_moves(b4, 0, 2))
b5 = create_initial_board()
b5[5][5] = EMPTY
b5[2][4] = DEFENDER
b5[4][4] = DEFENDER
b5[3][2] = ATTACKER
b5[3][3] = EMPTY
b5[3][4] = EMPTY
moves5 = get_valid_moves(b5, 3, 2)
test('sandwich prevention works', (3, 4) not in moves5)
test('can stop before sandwich', (3, 3) in moves5)
b6 = create_initial_board()
b6[5][5] = EMPTY
b6[3][3] = KING
b6[2][3] = ATTACKER
b6[4][3] = ATTACKER
test('king exempt from sandwich rule', len(get_valid_moves(b6, 3, 3)) > 0)
b7 = create_initial_board()
b7[5][3] = EMPTY
b7[5][4] = EMPTY
b7[4][4] = EMPTY
b7[6][4] = EMPTY
b7[5][2] = ATTACKER
test('king on throne no false block', (5, 4) in get_valid_moves(b7, 5, 2))

print()
print('--- get_all_moves ---')
board = create_initial_board()
att_m = get_all_moves(board, ATTACKER)
def_m = get_all_moves(board, DEFENDER)
test('116 attacker moves', len(att_m) == 116)
test('60 defender moves', len(def_m) == 60)
test('attacker sources are attackers', all(board[fr][fc] == ATTACKER for fr, fc, _, _ in att_m))
test('defender sources valid', all(board[fr][fc] in (DEFENDER, KING) for fr, fc, _, _ in def_m))
test('no landing on pieces', all(is_empty(board, tr, tc) for _, _, tr, tc in att_m))
b2 = create_initial_board()
b2[5][4] = EMPTY
b2[5][6] = EMPTY
king_m = [(fr, fc, tr, tc) for fr, fc, tr, tc in get_all_moves(b2, DEFENDER) if fr == 5 and fc == 5]
test('king moves included', len(king_m) > 0)
b3 = create_initial_board()
for r in range(BOARD_SIZE):
    for c in range(BOARD_SIZE):
        b3[r][c] = EMPTY
test('empty board no moves', get_all_moves(b3, ATTACKER) == [] and get_all_moves(b3, DEFENDER) == [])

print()
print('--- is_hostile ---')
board = create_initial_board()
test('wall top hostile', is_hostile(board, -1, 0, ATTACKER))
test('wall right hostile', is_hostile(board, 0, 11, ATTACKER))
test('wall bottom hostile', is_hostile(board, 11, 0, ATTACKER))
test('wall left hostile', is_hostile(board, 0, -1, ATTACKER))
test('king not hostile to attacker', not is_hostile(board, 5, 5, ATTACKER))
test('king not hostile to defender', not is_hostile(board, 5, 5, DEFENDER))
b = create_initial_board()
b[5][5] = EMPTY
test('empty throne hostile', is_hostile(b, 5, 5, ATTACKER))
test('corner hostile', is_hostile(board, 0, 0, ATTACKER))
test('own piece hostile', is_hostile(board, 0, 3, ATTACKER))
test('enemy not hostile own-side', not is_hostile(board, 0, 3, DEFENDER))
test('empty square not hostile', not is_hostile(board, 2, 2, ATTACKER))

print()
print('--- check_captures ---')
b = create_initial_board()
b[5][5] = EMPTY
b[3][3] = DEFENDER
b[3][2] = ATTACKER
b[3][4] = ATTACKER
check_captures(b, 3, 2, ATTACKER)
test('custodial capture', b[3][3] == EMPTY)
b2 = create_initial_board()
b2[5][5] = EMPTY
b2[5][4] = DEFENDER
b2[5][3] = ATTACKER
check_captures(b2, 5, 3, ATTACKER)
test('throne capture', b2[5][4] == EMPTY)
b3 = create_initial_board()
b3[5][5] = EMPTY
b3[0][2] = DEFENDER
b3[1][2] = ATTACKER
check_captures(b3, 1, 2, ATTACKER)
test('wall capture', b3[0][2] == EMPTY)
b4 = create_initial_board()
b4[0][1] = DEFENDER
b4[0][2] = ATTACKER
check_captures(b4, 0, 2, ATTACKER)
test('corner capture', b4[0][1] == EMPTY)
b5 = create_initial_board()
b5[5][5] = EMPTY
b5[3][3] = KING
b5[3][2] = ATTACKER
b5[3][4] = ATTACKER
check_captures(b5, 3, 4, ATTACKER)
test('king not removed', b5[3][3] == KING)
b6 = create_initial_board()
b6[5][5] = EMPTY
b6[3][3] = KING
b6[3][4] = DEFENDER
b6[3][2] = ATTACKER
check_captures(b6, 3, 2, ATTACKER)
test('king unarmed', b6[3][4] == DEFENDER)
b7 = create_initial_board()
b7[5][5] = EMPTY
b7[3][3] = ATTACKER
b7[3][4] = DEFENDER
check_captures(b7, 3, 3, ATTACKER)
test('incomplete no capture', b7[3][4] == DEFENDER)
b8 = create_initial_board()
b8[3][3] = DEFENDER
b8[3][4] = ATTACKER
b8[3][5] = DEFENDER
check_captures(b8, 3, 5, DEFENDER)
test('defender captures attacker', b8[3][4] == EMPTY)
b9 = create_initial_board()
b9[5][5] = EMPTY
b9[3][3] = KING
b9[3][4] = ATTACKER
b9[3][2] = DEFENDER
check_captures(b9, 3, 3, DEFENDER)
test('king cannot capture', b9[3][4] == ATTACKER)
b10 = create_initial_board()
b10[5][5] = EMPTY
b10[3][3] = DEFENDER
b10[3][2] = ATTACKER
check_captures(b10, 3, 2, ATTACKER)
test('free side no capture', b10[3][3] == DEFENDER)

# ============================================================
print()
print('=' * 60)
print('SECTION 3: GAME.PY')
print('=' * 60)

print()
print('--- apply_move ---')
b = create_initial_board()
apply_move(b, 0, 3, 0, 2)
test('piece at destination', b[0][2] == ATTACKER)
test('source empty', b[0][3] == EMPTY)
b2 = create_initial_board()
b2[5][4] = EMPTY
apply_move(b2, 5, 5, 5, 4)
test('king moved', b2[5][4] == KING)
test('king source empty', b2[5][5] == EMPTY)
b3 = create_initial_board()
b3[5][5] = EMPTY
b3[3][3] = DEFENDER
b3[3][4] = ATTACKER
b3[3][1] = ATTACKER
b3[3][2] = EMPTY
apply_move(b3, 3, 1, 3, 2)
test('apply_move triggers capture', b3[3][3] == EMPTY)
b4 = create_initial_board()
b4[3][3] = DEFENDER
b4[3][4] = ATTACKER
b4[3][6] = DEFENDER
b4[3][5] = EMPTY
apply_move(b4, 3, 6, 3, 5)
test('defender apply triggers capture', b4[3][4] == EMPTY)
b5 = create_initial_board()
b5[5][5] = EMPTY
b5[3][3] = KING
b5[3][4] = ATTACKER
b5[3][2] = DEFENDER
b5[3][1] = EMPTY
apply_move(b5, 3, 3, 3, 2)
test('king move does not capture', b5[3][4] == ATTACKER)

print()
print('--- check_game_over ---')
b = create_initial_board()
test('not over at start', check_game_over(b) is None)
for corner in CORNERS:
    b = create_initial_board()
    b[5][5] = EMPTY
    b[corner[0]][corner[1]] = KING
    test(f'defender wins at {corner}', check_game_over(b) == 'defender')
b = create_initial_board()
b[5][5] = EMPTY
b[3][3] = KING
b[2][3] = ATTACKER
b[4][3] = ATTACKER
b[3][2] = ATTACKER
b[3][4] = ATTACKER
test('attacker wins surrounded', check_game_over(b) == 'attacker')
b2 = create_initial_board()
b2[5][5] = EMPTY
b2[0][0] = KING
b2[1][0] = ATTACKER
b2[0][1] = ATTACKER
test('escape before capture', check_game_over(b2) == 'defender')
b3 = create_initial_board()
b3[5][5] = EMPTY
b3[2][2] = KING
test('king mid-board = ongoing', check_game_over(b3) is None)

print()
print('--- validate_move ---')
b = create_initial_board()
all_m = get_all_moves(b, ATTACKER)
test('valid move accepted', validate_move('0 3 0 2', all_m) == (0, 3, 0, 2))
test('too few parts', validate_move('0 3 0', all_m) is None)
test('too many parts', validate_move('0 3 0 2 5', all_m) is None)
test('out of bounds', validate_move('0 3 0 11', all_m) is None)
test('negative coords', validate_move('-1 3 0 2', all_m) is None)
test('illegal move', validate_move('5 5 5 6', all_m) is None)
test('non-integer', validate_move('a b c d', all_m) is None)
test('empty string', validate_move('', all_m) is None)
test('spaces only', validate_move('   ', all_m) is None)
test('from empty square', validate_move('2 2 2 3', all_m) is None)

# ============================================================
print()
print('=' * 60)
print('SECTION 4: UTILITY.PY')
print('=' * 60)

print()
board = create_initial_board()
test('scores are opposites', evaluate(board, DEFENDER) == -evaluate(board, ATTACKER))
b1 = create_initial_board()
b1[5][5] = EMPTY
b1[0][1] = KING
b2 = create_initial_board()
test('king near corner > center', king_distance_score(b1) > king_distance_score(b2))
b3 = create_initial_board()
b3[5][5] = EMPTY
b3[0][0] = KING
test('king at corner = max dist score', king_distance_score(b3) >= king_distance_score(b1))
b4 = create_initial_board()
b4[5][5] = EMPTY
test('no king dist = -1000', king_distance_score(b4) == -1000)
b5 = create_initial_board()
b6 = create_initial_board()
b6[5][4] = EMPTY
b6[5][6] = EMPTY
b6[4][5] = EMPTY
b6[6][5] = EMPTY
test('open > surrounded mobility', king_mobility_score(b6) > king_mobility_score(b5))
test('surrounded king mobility <= 0', king_mobility_score(b5) <= 0)
b7 = create_initial_board()
b7[5][5] = EMPTY
test('no king mobility = -1000', king_mobility_score(b7) == -1000)
b8 = create_initial_board()
b8[5][5] = EMPTY
b8[0][1] = KING
b8[0][0] = EMPTY
b9 = create_initial_board()
test('escape path scores higher', king_escape_score(b8) >= king_escape_score(b9))
b10 = create_initial_board()
b10[5][5] = EMPTY
test('no king escape = -1000', king_escape_score(b10) == -1000)
b11 = create_initial_board()
b11[5][5] = EMPTY
b11[3][3] = KING
b11[2][3] = ATTACKER
b11[4][3] = ATTACKER
b11[3][2] = ATTACKER
b11[3][4] = ATTACKER
b12 = create_initial_board()
b12[5][5] = EMPTY
b12[3][3] = KING
test('surrounded < free encirclement', king_encirclement_score(b11) < king_encirclement_score(b12))
test('fully surrounded = -4*weight', king_encirclement_score(b11) == -4 * ENCIRCLEMENT_WEIGHT)
test('free king = 0 encirclement', king_encirclement_score(b12) == 0)
b13 = create_initial_board()
b13[5][5] = EMPTY
test('no king encirclement = -1000', king_encirclement_score(b13) == -1000)
board = create_initial_board()
test('more attackers = neg piece score', piece_count_score(board) < 0)
b14 = create_initial_board()
for r in range(BOARD_SIZE):
    for c in range(BOARD_SIZE):
        b14[r][c] = EMPTY
b14[0][0] = DEFENDER
b14[0][1] = ATTACKER
test('equal pieces = 0', piece_count_score(b14) == 0)
b14[0][2] = DEFENDER
test('more defenders = pos score', piece_count_score(b14) > 0)
b15 = create_initial_board()
b15[5][5] = EMPTY
b15[0][3] = KING
b15[0][2] = EMPTY
b15[0][1] = EMPTY
test('clear horiz path true', is_path_clear(b15, (0, 3), (0, 0)))
b16 = create_initial_board()
b16[5][5] = EMPTY
b16[2][5] = KING
test('blocked vert path false', not is_path_clear(b16, (2, 5), (0, 5)))
test('diagonal always false', not is_path_clear(board, (0, 0), (5, 5)))
b17 = create_initial_board()
b17[5][5] = EMPTY
b17[0][1] = KING
b18 = create_initial_board()
test('king near corner = higher defender eval', evaluate(b17, DEFENDER) > evaluate(b18, DEFENDER))
b19 = create_initial_board()
b19[5][5] = EMPTY
b19[3][3] = KING
b19[2][3] = ATTACKER
b19[4][3] = ATTACKER
b19[3][2] = ATTACKER
b19[3][4] = ATTACKER
test('surrounded king = lower defender eval', evaluate(b19, DEFENDER) < evaluate(b18, DEFENDER))
test('attacker = negation of defender', evaluate(b19, ATTACKER) == -evaluate(b19, DEFENDER))

# ============================================================
print()
print('=' * 60)
print('SECTION 5: ALPHA_BETA.PY')
print('=' * 60)

print()
test('normalize attacker int', ab._normalize_player(ATTACKER) == ATTACKER)
test('normalize defender int', ab._normalize_player(DEFENDER) == DEFENDER)
test('normalize attacker str', ab._normalize_player('attacker') == ATTACKER)
test('normalize defender str', ab._normalize_player('defender') == DEFENDER)
try:
    ab._normalize_player('unknown')
    test('invalid raises error', False)
except ValueError:
    test('invalid raises error', True)
test('opponent attacker=defender', ab._opponent(ATTACKER) == DEFENDER)
test('opponent defender=attacker', ab._opponent(DEFENDER) == ATTACKER)
test('easy=1', ab.get_depth_for_difficulty('easy') == 1)
test('medium=3', ab.get_depth_for_difficulty('medium') == 3)
test('hard=5', ab.get_depth_for_difficulty('hard') == 5)
test('uppercase works', ab.get_depth_for_difficulty('Easy') == 1)
try:
    ab.get_depth_for_difficulty('extreme')
    test('bad difficulty raises', False)
except ValueError:
    test('bad difficulty raises', True)
b1 = create_initial_board()
b1[5][5] = EMPTY
b1[0][0] = KING
s1 = ab.alpha_beta(b1, 3, -math.inf, math.inf, True, DEFENDER)
s2 = ab.alpha_beta(b1, 3, -math.inf, math.inf, True, ATTACKER)
test('defender win +inf for defender', s1 == math.inf)
test('defender win -inf for attacker', s2 == -math.inf)
b2 = create_initial_board()
b2[5][5] = EMPTY
b2[3][3] = KING
b2[2][3] = ATTACKER
b2[4][3] = ATTACKER
b2[3][2] = ATTACKER
b2[3][4] = ATTACKER
s3 = ab.alpha_beta(b2, 3, -math.inf, math.inf, True, ATTACKER)
s4 = ab.alpha_beta(b2, 3, -math.inf, math.inf, True, DEFENDER)
test('attacker win +inf for attacker', s3 == math.inf)
test('attacker win -inf for defender', s4 == -math.inf)
board = create_initial_board()
s = ab.alpha_beta(board, 0, -math.inf, math.inf, True, DEFENDER)
test('depth 0 = evaluate', s == evaluate(board, DEFENDER))
move = ab.get_best_move(board, ATTACKER, 1)
test('returns move', move is not None)
test('is 4-tuple', isinstance(move, tuple) and len(move) == 4)
fr, fc, tr, tc = move
test('source is attacker', board[fr][fc] == ATTACKER)
test('destination empty', is_empty(board, tr, tc))
test('move is legal', move in get_all_moves(board, ATTACKER))
move2 = ab.get_best_move(board, DEFENDER, 1)
test('defender returns move', move2 is not None)
fr2, fc2, tr2, tc2 = move2
test('defender source valid', board[fr2][fc2] in (DEFENDER, KING))
b = create_initial_board()
b[5][5] = EMPTY
b[0][1] = KING
b[0][0] = EMPTY
for r in range(1, 5):
    b[r][1] = EMPTY
move = ab.get_best_move(b, DEFENDER, 1)
test('picks winning corner move', move is not None and move == (0, 1, 0, 0))
b = create_initial_board()
for r in range(BOARD_SIZE):
    for c in range(BOARD_SIZE):
        b[r][c] = EMPTY
test('no moves returns None', ab.get_best_move(b, ATTACKER, 1) is None)
board = create_initial_board()
move = ab.get_best_move(board, ATTACKER, 2)
test('depth 2 legal', move in get_all_moves(board, ATTACKER))
move = ab.get_best_move(board, DEFENDER, 2)
test('depth 2 defender legal', move in get_all_moves(board, DEFENDER))

# ============================================================
print()
print('=' * 60)
print('SECTION 6: INTEGRATION')
print('=' * 60)

print()
print('--- 30-move simulated game ---')
board = create_initial_board()
current_player = ATTACKER
game_over = False
moves_played = 0
for _ in range(30):
    move = ab.get_best_move(board, current_player, 1)
    if move is None:
        break
    if move not in get_all_moves(board, current_player):
        break
    apply_move(board, *move)
    moves_played += 1
    winner = check_game_over(board)
    if winner is not None:
        game_over = True
        break
    current_player = DEFENDER if current_player == ATTACKER else ATTACKER

test('30 moves without crash', moves_played >= 30 or game_over)
test('king valid or game over', find_king(board) is not None or game_over)
att_f = sum(1 for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if board[r][c] == ATTACKER)
dff_f = sum(1 for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if board[r][c] == DEFENDER)
test('attacker count valid', 0 <= att_f <= 24)
test('defender count valid', 0 <= dff_f <= 12)
test('no invalid pieces', all(board[r][c] in (EMPTY, ATTACKER, DEFENDER, KING) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)))

print()
print('--- AI does not corrupt real board ---')
board = create_initial_board()
backup = copy_board(board)
ab.get_best_move(board, ATTACKER, 2)
test('board unchanged after AI search', all(board[r][c] == backup[r][c] for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)))

print()
print('=' * 60)
print(f'TOTAL: {passed} passed, {failed} failed out of {passed + failed} tests')
print('=' * 60)