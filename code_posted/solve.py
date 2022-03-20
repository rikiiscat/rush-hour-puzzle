from board import *
from operator import attrgetter
import copy


def a_star(init_board, hfn):
    """
    Run the A_star search algorithm given an initial board and a heuristic function.

    If the function finds a goal state, it returns a list of states representing
    the path from the initial state to the goal state in order and the cost of
    the solution found.
    Otherwise, it returns am empty list and -1.

    :param init_board: The initial starting board.
    :type init_board: Board
    :param hfn: The heuristic function.
    :type hfn: Heuristic (a function that consumes a Board and produces a numeric heuristic value)
    :return: (the path to goal state, solution cost)
    :rtype: List[State], int
    """

    # the same generic search algorithm as dfs
    if hfn == 3:
        init_state = State (init_board, hfn, blocking_heuristic (init_board), 0, None)
    else:
        init_state = State (init_board, hfn, advanced_heuristic (init_board), 0, None)
    frontier = [init_state]
    explored = []
    while len(frontier) > 0:
        if frontier != [init_state]:
            frontier.sort (key=attrgetter ('f', 'id', 'parent.id'))
        removed_state = frontier[0]
        frontier.pop(0)
        is_explored = False
        for state0 in explored:
            if is_equal_state(removed_state, state0):
                is_explored = True
                break
        if not is_explored:
            explored.insert (0, removed_state)
            if is_goal (removed_state):
                return get_path (removed_state), removed_state.depth
            successors = get_successors (removed_state)
            for state in successors:
                frontier.insert (len (frontier), state)

    return [], -1

    # raise NotImplementedError


def is_equal_state(state1, state2):
    return state1.id == state2.id


def dfs(init_board):
    """
    Run the DFS algorithm given an initial board.

    If the function finds a goal state, it returns a list of states representing
    the path from the initial state to the goal state in order and the cost of
    the solution found.
    Otherwise, it returns am empty list and -1.

    :param init_board: The initial board.
    :type init_board: Board
    :return: (the path to goal state, solution cost)
    :rtype: List[State], int
    """

    "create the state of the current board"
    init_state = State(init_board, zero_heuristic(init_board), 0, 0, None)
    frontier = [init_state]
    explored = []
    "explored list is used for multi-path pruning"
    while len(frontier) > 0:
        "remove the last state in the frontier"
        removed_state = frontier[len(frontier)-1]
        frontier.pop(len(frontier)-1)
        is_explored = False
        for state0 in explored:
            if is_equal_state(removed_state, state0):
                is_explored = True
                break
        if not is_explored:
            explored.insert (0, removed_state)
            "if the removed one is the goal state then simply call return_path to return"
            if is_goal (removed_state):
                return get_path (removed_state), removed_state.depth
            "get all the successor states of the current state"
            successors = get_successors (removed_state)
            "sort them in decreasing order of hash IDs"
            successors.sort (key=attrgetter ('id'), reverse=True)
            for state in successors:
                frontier.insert (len (frontier), state)


    return [], -1

    # raise NotImplementedError


def number_of_cars_blocking_exit(board):
    cars = board.cars
    first_car = cars [0]
    for car in cars:
        if car.is_goal:
            first_car = car
            break
    number = 0
    if first_car.orientation == "h":
        y_coord = first_car.fix_coord
        x_coord = first_car.var_coord
        len = first_car.length
        largest_x = x_coord + len - 1
        for car in cars:
            if not car.is_goal:
                if (car.orientation == "h" and car.fix_coord == y_coord and car.var_coord > largest_x) or (
                        car.orientation == "v" and car.fix_coord > largest_x and (
                        car.var_coord <= y_coord <= car.var_coord + car.length - 1)):
                    number += 1
    else:
        x_coord = first_car.fix_coord
        y_coord = first_car.var_coord
        len = first_car.length
        largest_y = y_coord + len - 1
        for car in cars:
            if not car.is_goal:
                if (car.orientation == "v" and car.fix_coord == x_coord and car.var_coord > largest_y) or (
                        car.orientation == "h" and car.fix_coord > largest_y and (
                        car.var_coord <= x_coord <= car.var_coord + car.length - 1)):
                    number += 1
    return number


def get_successors(state):
    """
    Return a list containing the successor states of the given state.
    The states in the list may be in any arbitrary order.

    :param state: The current state.
    :type state: State
    :return: The list of successor states.
    :rtype: List[State]
    """

    # we need to find all the successors states of the given state,
    # which means all the state that can be reached within one eligible move
    global new_state, new_board
    cur_board = state.board
    cur_grid = cur_board.grid
    cars = cur_board.cars.copy ()
    new_states = []
    for car in cars:
        "if the car is horizontal"
        if car.orientation == "h":
            y_coord = car.fix_coord
            x_coord = car.var_coord
            len1 = car.length
            upper_right = x_coord + len1 - 1
            if x_coord > 0:
                for i in range (1, x_coord + 1):
                    "create new states and add to the list of successor states"
                    if cur_grid[y_coord][x_coord-i] != '.':
                        break
                    car.set_coord (x_coord - i)
                    cars_cp = copy.deepcopy (cars)
                    new_board = Board(cur_board.name, 6, cars_cp)
                    if state.hfn == 3:
                        "calculate the two h values"
                        original_number_of_blocking = number_of_cars_blocking_exit (cur_board)
                        new_number_of_blocking = number_of_cars_blocking_exit (new_board)
                        new_state = State(new_board, state.hfn,
                              state.depth+1+1+new_number_of_blocking, state.depth + 1, state)
                        new_states.insert(0, new_state)

                    elif state.hfn == advanced_heuristic (cur_board):
                        new_state = State(new_board, state.hfn, advanced_heuristic(cur_board)+state.depth+1, state.depth+1, state)
                        new_states.insert (0, new_state)

                    else:
                        new_state = State(new_board, state.hfn, 0, state.depth + 1, state)
                        new_states.insert (0, new_state)

            car.set_coord (x_coord)

            if upper_right < 5:
                for i in range (upper_right + 1, 6):
                    "create new states and add to the list of successor states"
                    if cur_grid [y_coord] [i] != '.':
                        break
                    car.set_coord (x_coord + i - upper_right)
                    # cars_cp = cars.copy()
                    cars_cp = copy.deepcopy (cars)
                    new_board = Board(cur_board.name, 6, cars_cp)
                    if state.hfn == 3:
                        "calculate the h value"
                        original_number_of_blocking = number_of_cars_blocking_exit (cur_board)
                        new_number_of_blocking = number_of_cars_blocking_exit (new_board)
                        new_state = State(new_board, state.hfn,
                                          state.depth+1+1+new_number_of_blocking,
                                          state.depth + 1, state)
                        new_states.insert (0, new_state)

                    elif state.hfn == advanced_heuristic (cur_board):
                        new_state = State(new_board, state.hfn, advanced_heuristic(cur_board)+state.depth+1, state.depth+1, state)
                        new_states.insert (0, new_state)

                    else:
                        new_state = State(new_board, state.hfn, 0, state.depth + 1, state)
                        new_states.insert (0, new_state)

            car.set_coord (x_coord)


        if car.orientation == "v":
            x_coord = car.fix_coord
            y_coord = car.var_coord
            len1 = car.length
            lower_left = y_coord + len1 - 1
            if y_coord > 0:
                "we can move the car up if there is no car blocking upside"
                for i in range (1, y_coord + 1):
                    if cur_grid [y_coord-i] [x_coord] != '.':
                        break
                    car.set_coord (y_coord - i)
                    #cars_cp = cars.copy()
                    cars_cp = copy.deepcopy(cars)
                    new_board = Board(cur_board.name, 6, cars_cp)
                    if state.hfn == 3:
                        original_number_of_blocking = number_of_cars_blocking_exit (cur_board)
                        new_number_of_blocking = number_of_cars_blocking_exit (new_board)
                        new_state = State(new_board, state.hfn,
                                          state.depth+1+1+new_number_of_blocking,
                                          state.depth + 1, state)
                        new_states.insert (0, new_state)

                    elif state.hfn == advanced_heuristic (cur_board):
                        new_state = State(new_board, state.hfn, advanced_heuristic(cur_board)+state.depth+1, state.depth+1, state)
                        new_states.insert (0, new_state)

                    else:
                        new_state = State(new_board, state.hfn, 0, state.depth + 1, state)
                        new_states.insert (0, new_state)
            car.set_coord (y_coord)

            if lower_left < 5:
                for i in range (lower_left + 1, 6):
                    if cur_grid [i] [x_coord] != '.':
                        break
                    car.set_coord (i - lower_left + y_coord)
                    # cars_cp = cars.copy()
                    cars_cp = copy.deepcopy (cars)
                    new_board = Board(cur_board.name, 6, cars_cp)
                    if state.hfn == 3:
                        original_number_of_blocking = number_of_cars_blocking_exit (cur_board)
                        new_number_of_blocking = number_of_cars_blocking_exit (new_board)
                        new_state = State(new_board, state.hfn, state.depth+1+new_number_of_blocking+1,
                                          state.depth + 1, state)
                        new_states.insert (0, new_state)

                    elif state.hfn == advanced_heuristic (cur_board):
                        new_state = State(new_board, state.hfn, advanced_heuristic(cur_board)+state.depth+1, state.depth+1, state)
                        new_states.insert(0, new_state)

                    else:
                        new_state = State(new_board, state.hfn, 0, state.depth + 1, state)
                        new_states.insert (0, new_state)
            car.set_coord (y_coord)

    return new_states

    # raise NotImplementedError


def is_goal(state):
    """
    Returns True if the state is the goal state and False otherwise.

    :param state: the current state.
    :type state: State
    :return: True or False
    :rtype: bool
    """
    cars = state.board.cars
    "find the goal car"
    goal_car = cars[0]
    for car in cars:
        if car.is_goal:
            goal_car = car
            break
    len = goal_car.length
    upper_left = goal_car.var_coord
    return upper_left+len-1 == 5

    # raise NotImplementedError


def get_path(state):
    """
    Return a list of states containing the nodes on the path 
    from the initial state to the given state in order.

    :param state: The current state.
    :type state: State
    :return: The path.
    :rtype: List[State]
    """

    states = []
    while state is not None:
        states.insert(0, state)
        state = state.parent
    return states

    # raise NotImplementedError


def blocking_heuristic(board):
    """
    Returns the heuristic value for the given board
    based on the Blocking Heuristic function.

    Blocking heuristic returns zero at any goal board,
    and returns one plus the number of cars directly
    blocking the goal car in all other states.

    :param board: The current board.
    :type board: Board
    :return: The heuristic value.
    :rtype: int
    """

    number_of_cars_blocking = number_of_cars_blocking_exit(board)
    if number_of_cars_blocking == 0:
        "this is the goal state"
        return 0
    else:
        return 1+number_of_cars_blocking

    # raise NotImplementedError


def advanced_heuristic(board):
    """
    An advanced heuristic of your own choosing and invention.

    :param board: The current board.
    :type board: Board
    :return: The heuristic value.
    :rtype: int
    """


    # raise NotImplementedError
