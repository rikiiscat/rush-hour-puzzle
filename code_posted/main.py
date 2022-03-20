from solve import *

boards = from_file("jams_posted.txt")
board = boards[3]
print(board.display())
print(board.grid)
#dfs(board)
a_star(board, blocking_heuristic(board))
#a_star(board, advanced_heuristic(board))