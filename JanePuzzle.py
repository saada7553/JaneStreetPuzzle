import math
from collections import deque
"""
bounds: (i, j, k, l) -> 
i  j
k  l

Hook directions -> 
(dir, dic, dlr, dlc)
"""
grid_size = 9
num_rem = set([i for i in range(1, grid_size + 1)])
grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
orig_bounds = [(0, 0), (len(grid) - 1, len(grid[0]) - 1)]
hook_directions = [(1, 1, 0, 0), 
                   (1, 0, 0, -1), 
                   (0, 1, -1, 0), 
                   (0, 0, -1, -1)]
clue_grid_5 = {
    (0, 0) : 0, 
    (1, 2) : 9, (1, 4) : 7, 
    (2, 0) : 8,
    (3, 2) : 15, (3, 4) : 12, 
    (4, 0) : 10 }
clue_grid_9 = {
    (0, 1) : 18, (0, 6) : 7, 
    (1, 4) : 12, 
    (2, 2) : 9, (2, 7) : 31, 
    (4, 1) : 5, (4, 3) : 11, (4, 5) : 22, (4, 7) : 22, 
    (6, 1) : 9, (6, 6) : 19, 
    (7, 4) : 14, 
    (8, 2) : 22, (8, 7) : 15 }
dfs_directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
check_directions = [(0, -1), (-1, 0), (0, 1), (1, 0)]
encodings = [[0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [0, 0, 1, 1], 
             [0, 1, 0, 0], [0, 1, 0, 1], [0, 1, 1, 0], [0, 1, 1, 1], 
             [1, 0, 0, 0], [1, 0, 0, 1], [1, 0, 1, 0], [1, 0, 1, 1], 
             [1, 1, 0, 0], [1, 1, 0, 1], [1, 1, 1, 0], [1, 1, 1, 1]]
skip_cache = set([ # impossible configurations (r, c, num)
    (0, 0, 1), (0, 0, 2), (0, 0, 3), (0, 0, 4), (0, 0, 6),
    (0, 8, 1), (0, 8, 2), (0, 8, 3), (0, 8, 4), (0, 8, 6),
    (8, 0, 1), (8, 0, 2), (8, 0, 3), (8, 0, 4), (8, 0, 5), (8, 0, 6),
    (8, 8, 1), (8, 8, 2), (8, 8, 3), (8, 8, 4), (8, 8, 5), (8, 8, 6)
])
loading_percentage = 0.001
cycle, solutions = 0, 0
sum_cache = {}

def calc():
    res = 1
    for i in range(grid_size, 1, -1):
        curr = (i * 4)
        res *= curr
    return res
num_instructions = 122145247909 / 3
 
with open('/Users/saadata/Desktop/puzzleSolution5.txt', 'w') as f: 
    f.write('')

def write_file():
    with open('/Users/saadata/Desktop/puzzleSolution5.txt', 'a') as f: 
        f.write('\n--------------------\n')
        for lst in grid:
            f.write('\n')
            lst = [str(num) for num in lst]
            f.write(' '.join(lst))
            f.write('\n')
        f.write('\n--------------------\n')

def print_grid(grid):
    print('----------------')
    for lst in grid: 
        print(*lst)
    print('----------------')

def dfs(bounds, num_rem):

    global loading_percentage
    global cycle
    global solutions

    if not num_rem:
        cycle += 1
        if check_grid(): 
            write_file()
            solutions += 1
            print(f'[FOUND #{solutions} SOLUTION]')
        if cycle >= num_instructions * loading_percentage and loading_percentage != 1: 
            print(f"LOADING [{loading_percentage * 100:.1f}%]")
            loading_percentage = min(1, loading_percentage + 0.001)
        return 

    four_points = [
        bounds[0], 
        (bounds[0][0], bounds[1][1]), 
        (bounds[1][0], bounds[0][1]), 
        bounds[1]
    ]

    loop_count = 4 if len(num_rem) > 1 else 1
    for h in range(loop_count):
        r, c = four_points[h]
        dri, dci, drl, dcl = hook_directions[h] 
        new_bounds = [(dri + bounds[0][0], dci + bounds[0][1]),
                      (drl + bounds[1][0], dcl + bounds[1][1])]

        for num in num_rem:

            if (r, c, num) in skip_cache and (len(num_rem) == 9 or (
                ((r, c) == (8, 0) and len(num_rem) in [8, 7, 6, 5, 4])) or # hints
                ((r, c) == (0, 0) and len(num_rem) in [8, 7, 6, 5, 4, 3])  # more hints
            ): 
                continue

            update_matrix(r, c, h, 0, num)
            dfs(new_bounds, [num2 for num2 in num_rem if num2 != num])
            update_matrix(r, c, h, num, 0)

def update_matrix(orig_r, orig_c, hook_direction, orig_num, new_num):
    dr, dc = dfs_directions[hook_direction]
    r, c = orig_r, orig_c

    while 0 <= r < len(grid):
        if r == orig_r:
            r += dr 
            continue
        if grid[r][orig_c] == orig_num: 
            grid[r][orig_c] = new_num
            r += dr
        else: break
    
    while 0 <= c < len(grid[0]): 
        if c == orig_c: 
            c += dc
            continue
        if grid[orig_r][c] == orig_num: 
            grid[orig_r][c] = new_num
            c += dc
        else: break
    
    grid[orig_r][orig_c] = new_num

def check_grid():

    clue_grid = clue_grid_5 if grid_size == 5 else clue_grid_9
    for location, value in clue_grid.items(): 
        r, c = location
        usable_nums = []

        for dr, dc in check_directions: 
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                usable_nums.append(grid[nr][nc])
        if not check_sum(value, tuple(usable_nums)):
            return False
        
    return True

def check_grid_clue_list(grid):

    clue_grid = clue_grid_5 if grid_size == 5 else clue_grid_9
    for r, c, value in clue_grid: 
        usable_nums = []

        for dr, dc in check_directions: 
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                usable_nums.append(grid[nr][nc])
        if not check_sum(value, tuple(usable_nums)):            
            return False
        
    return True

def check_sum(target, n):

    n = list(n)
    while len(n) < 4: 
        n.append(0)
    n = tuple(n)

    if (target, n) in sum_cache:
        return sum_cache[(target, n)]

    if target == 0: 
        sum_cache[(target, n)] = True
        return sum_cache[(target, n)]
    
    possible_sums = [
        n[0], n[1], n[2], n[3],  
        n[0]+n[1], n[0]+n[2], n[0]+n[3], n[1]+n[2], n[1]+n[3], n[2]+n[3], 
        n[0]+n[1]+n[2], n[0]+n[1]+n[3], n[0]+n[2]+n[3], n[1]+n[2]+n[3], 
        sum(n) 
    ]
    
    sum_cache[(target, n)] = target in possible_sums
    return sum_cache[(target, n)]

grids = []
def read_grids():
    global grids
    global clue_grid_5, clue_grid_9
    with open(f'/Users/saadata/Desktop/found_grids{grid_size}.txt', 'r') as f:
        lines = f.readlines()
        lines = [item for item in lines if item != '\n']
        curr_grid = []

    for item in lines: 
        if item == '--------------------\n': 
            grids.append(curr_grid)
            curr_grid = []
        else: 
            curr_grid.append(item.split(' '))
    
    for grid in grids: 
        for lst in grid: 
            lst[-1] = lst[-1][::-1][1:][::-1]
            for index in range(len(lst)): 
                lst[index] = int(lst[index])
    
    grids = [grid for grid in grids if grid]

def reset_clue():
    global clue_grid_5, clue_grid_9
    clue_grid = clue_grid_9 if grid_size == 9 else clue_grid_5
    for grid in grids:
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if (i, j) in clue_grid:
                    grid[i][j] = 0
    clue_grid_9 = [(key[0], key[1], val) for key, val in clue_grid_9.items()]
    clue_grid_5 = [(key[0], key[1], val) for key, val in clue_grid_5.items()]

def dfs_zero(grid, i): 
    clue_grid = clue_grid_9 if grid_size == 9 else clue_grid_5
    if i >= len(clue_grid):
        filtered_grids.append(grid)
        return 
    
    neighbors = [0, 0, 0, 0]
    r, c, val = clue_grid[i]
    for n in range(4):
        dr, dc = check_directions[n]
        nr, nc = r + dr, c + dc

        if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
            neighbors[n] = grid[nr][nc]
    
    all_new_nums = []
    for encoding in encodings:
        new_nums = [x * y for x, y in zip(neighbors, encoding)]
        all_new_nums.append(new_nums)
    all_new_nums = list(set([tuple(lst) for lst in all_new_nums])) # delete duplicates

    for nums in all_new_nums:
        if sum(nums) == val:
            new_grid = [lst[:] for lst in grid]
            for n in range(4):
                dr, dc = check_directions[n]
                nr, nc = r + dr, c + dc
                if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                    new_grid[nr][nc] = nums[n]
            dfs_zero(new_grid, i + 1)

def check_connected(grid):
    visited = set()
    q = deque()

    def add_first_non_zero_element():
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] != 0: 
                    q.append((i, j))
                    visited.add((i, j))
                    return True
        return False
    add_first_non_zero_element()
    
    while q:
        curr_i, curr_j = q.popleft()

        for di, dj in check_directions:
            ni, nj = curr_i + di, curr_j + dj

            if (
                0 <= ni < len(grid) and 
                0 <= nj < len(grid[0]) and 
                grid[ni][nj] != 0 and 
                (ni, nj) not in visited
            ): 
                visited.add((ni, nj))
                q.append((ni, nj))

    res = 0
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] != 0 and (i, j) not in visited:
                res += 1
    
    return res == 0

def check_grid_arg(grid):

    clue_grid = clue_grid_5 if grid_size == 5 else clue_grid_9
    for r, c, value in clue_grid: 
        usable_nums = []

        for dr, dc in check_directions: 
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                usable_nums.append(grid[nr][nc])
        if not check_sum(value, tuple(usable_nums)):            
            return False
        
    return True

def deep_check(grid):
    clue_grid = clue_grid_5 if grid_size == 5 else clue_grid_9
    for r, c, value in clue_grid: 
        usable_nums = []

        for dr, dc in check_directions: 
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                usable_nums.append(grid[nr][nc])
        if not sum(usable_nums) == value:            
            return False
        
    return True

def check_count(grid):
    checks = [i for i in range(1, 10)]
    res = []
    for num in checks: 
        curr_count = 0
        for lst in grid: 
            curr_count += lst.count(num)
        if curr_count != num:
            res.append(num)
    return res

filtered_grids = []
def run_post_processing():
    global filtered_grids
    read_grids()
    reset_clue()

    for grid in grids: 
        dfs_zero([lst[:] for lst in grid], 0)
    
    # more hints
    for grid in filtered_grids:
        grid[5][0] = 0
        grid[8][0] = 0
        grid[6][8] = 0
        grid[3][4] = 0
        grid[2][5] = 0
        grid[6][3] = 0
    
    filtered_grids = [connected for connected in filtered_grids if (check_grid_arg(connected) and 
                                                                    check_connected(connected) and 
                                                                    deep_check(connected) and 
                                                                    check_count(connected))]

# dfs(orig_bounds, [i for i in range(1, grid_size + 1)][::-1]) # <- phase 1, ~8 hours for 9 x 9
# run_post_processing() # <- phase 2 ~1 second for 9 x 9

for grid in filtered_grids: # every grid in this list has strong chance of being the answer after some manual work
    print_grid(grid)