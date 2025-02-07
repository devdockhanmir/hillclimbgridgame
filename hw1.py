import time
import numpy as np
from gridgame import *

##############################################################################################################################
# You can visualize what your code is doing by setting the GUI argument in the following line to true.
# The render_delay_sec argument allows you to slow down the animation, to be able to see each step more clearly.
#
# For your final submission, please set the GUI option to False.
#
# The gs argument controls the grid size. You should experiment with various sizes to ensure your code generalizes.
# Please do not modify or remove lines 18 and 19.
##############################################################################################################################

game = ShapePlacementGrid(GUI=True, render_delay_sec=0.1, gs=6, num_colored_boxes=5)
shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')
np.savetxt('initial_grid.txt', grid, fmt="%d")

##############################################################################################################################
# Initialization
##############################################################################################################################

# shapePos = [x, y] -> x=column, y=row
# grid[row, col]

shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')
print(shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done)

# For timing
start = time.time()

##########################################
# Write all your code in the area below.
##########################################

# -- Movement Functions --

def move(direction):
    """Moves the brush in the given direction (up, down, left, right)."""
    global shapePos
    previous_position = shapePos
    shapePos, _, _, _, _, _ = game.execute(direction)
    return shapePos != previous_position

def switch_color():
    """Cycles to the next available color."""
    global currentColorIndex
    _, _, currentColorIndex, _, _, _ = game.execute('switchcolor')

def switch_shape():
    """Cycles to the next brush shape."""
    global currentShapeIndex
    _, currentShapeIndex, _, _, _, _ = game.execute('switchshape')


# -- Evaluation Function --

def evaluate_grid():
    """Evaluates the grid by counting adjacent color conflicts."""
    _, _, _, grid, _, _ = game.execute('export')
    conflicts = 0
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            if grid[row][col] != -1:  # Only check filled cells
                # Check right neighbor
                if col < len(grid[row]) - 1 and grid[row][col] == grid[row][col + 1]:
                    conflicts += 1
                # Check below neighbor
                if row < len(grid) - 1 and grid[row][col] == grid[row + 1][col]:
                    conflicts += 1
    print(f"⚠️ Found {conflicts} conflicts.")
    return conflicts

# -- Place Color Safely --

def place_color():
    """Places the current color at the current brush position only if all covered cells are empty."""
    global placedShapes
    _, _, _, grid, _, _ = game.execute('export')
    
    # shapePos = [x, y]
    x, y = shapePos

    # Don't place if the cell is already filled
    if grid[y, x] != -1:
        return  # Skip placement

    brush_shape = game.shapes[currentShapeIndex]

    # Check if all covered cells by brush_shape are empty
    can_place = True
    rows = brush_shape.shape[0]
    cols = brush_shape.shape[1]

    for i in range(rows):      # i is the row offset of the shape
        for j in range(cols):  # j is the col offset of the shape
            if brush_shape[i, j] == 1:
                # new_y = y + i  (vertical offset)
                # new_x = x + j  (horizontal offset)
                new_y = y + i
                new_x = x + j

                # Bounds check
                if not (0 <= new_y < len(grid) and 0 <= new_x < len(grid[0])):
                    can_place = False
                    break

                # Cell must be empty
                if grid[new_y, new_x] != -1:
                    can_place = False
                    break
        if not can_place:
            break

    if can_place:
        try:
            _, _, _, _, placedShapes, _ = game.execute('place')
            print(f"✅ Placed at {shapePos} - Shape: {currentShapeIndex} - Color: {currentColorIndex}")
        except AttributeError:
            print("Warning: Invalid grid check encountered. Ignoring error.")


# -- Available Colors --

def get_available_colors(grid, row, col):
    """
    Returns a list of valid colors for (row, col) so that no adjacent cell
    has the same color. row=y, col=x in the grid array.
    """
    adjacent_colors = set()

    # Up
    if row > 0 and grid[row - 1][col] != -1:
        adjacent_colors.add(grid[row - 1][col])
    # Down
    if row < len(grid) - 1 and grid[row + 1][col] != -1:
        adjacent_colors.add(grid[row + 1][col])
    # Left
    if col > 0 and grid[row][col - 1] != -1:
        adjacent_colors.add(grid[row][col - 1])
    # Right
    if col < len(grid[0]) - 1 and grid[row][col + 1] != -1:
        adjacent_colors.add(grid[row][col + 1])

    all_colors = list(range(len(game.colors)))
    return [c for c in all_colors if c not in adjacent_colors]

def set_color(color_index):
    """Sets the brush to a specific color."""
    global currentColorIndex
    while currentColorIndex != color_index:
        switch_color()
        # Update currentColorIndex after each switch
        _, _, currentColorIndex, _, _, _ = game.execute('export')


# -- Hill Climb / Greedy Coloring --

def hill_climb(max_iterations=1000):
    """Color the grid ensuring no adjacent cells share the same color."""
    for _ in range(max_iterations):
        _, _, _, grid, _, _ = game.execute('export')

        # Find all empty cells (-1)
        uncolored_positions = [(r, c) for r in range(len(grid)) 
                                      for c in range(len(grid[r])) 
                                      if grid[r][c] == -1]
        if not uncolored_positions:
            print("✅ All cells are filled. Exiting...")
            break

        for row, col in uncolored_positions:
            move_attempts = 0

            # Move brush to (col, row)
            while (shapePos[1] != row or shapePos[0] != col) and move_attempts < 20:
                # shapePos[1] = current brush's y
                if shapePos[1] < row:
                    move('down')
                elif shapePos[1] > row:
                    move('up')
                # shapePos[0] = current brush's x
                if shapePos[0] < col:
                    move('right')
                elif shapePos[0] > col:
                    move('left')

                move_attempts += 1

            # After moving, check if it's still uncolored
            if grid[row, col] != -1:
                continue

            # Get valid colors
            valid_colors = get_available_colors(grid, row, col)
            if valid_colors:
                chosen_color = valid_colors[0]
                set_color(chosen_color)
                place_color()
                print(f"✅ Placed color {chosen_color} at ({row},{col})")
            else:
                print(f"⚠️ No valid color found for ({row},{col}), skipping.")

        # Check for conflicts
        no_conflicts = (evaluate_grid() == 0)
        # Check if any uncolored remain
        still_uncolored = any(-1 in rowvals for rowvals in grid)

        # Stop only if no conflicts AND no unfilled cells remain
        if no_conflicts and not still_uncolored:
            print("🎉 Fully Colored with No Conflicts!")
            break

# Run the AI
hill_climb()

# Print final
_, _, _, final_grid, _, _ = game.execute('export')
print("Final Grid State:\n", final_grid)

##########################################
# Additional code
##########################################

end = time.time()

np.savetxt('grid.txt', final_grid, fmt="%d")
with open("shapes.txt", "w") as outfile:
    outfile.write(str(placedShapes))
with open("time.txt", "w") as outfile:
    outfile.write(str(end-start))
