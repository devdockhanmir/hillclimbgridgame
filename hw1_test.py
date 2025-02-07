
# Paste the full content of hw1.py here


import time
import numpy as np
from gridgame import *

##############################################################################################################################

# You can visualize what your code is doing by setting the GUI argument in the following line to true.
# The render_delay_sec argument allows you to slow down the animation, to be able to see each step more clearly.

# For your final submission, please set the GUI option to False.

# The gs argument controls the grid size. You should experiment with various sizes to ensure your code generalizes.
# Please do not modify or remove lines 18 and 19.

##############################################################################################################################

game = ShapePlacementGrid(GUI=False, render_delay_sec=0.1, gs=6, num_colored_boxes=5)
shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')
np.savetxt('initial_grid.txt', grid, fmt="%d")

##############################################################################################################################

# Initialization

# shapePos is the current position of the brush.

# currentShapeIndex is the index of the current brush type being placed (order specified in gridgame.py, and assignment instructions).

# currentColorIndex is the index of the current color being placed (order specified in gridgame.py, and assignment instructions).

# grid represents the current state of the board.

    # -1 indicates an empty cell
    # 0 indicates a cell colored in the first color (indigo by default)
    # 1 indicates a cell colored in the second color (taupe by default)
    # 2 indicates a cell colored in the third color (veridian by default)
    # 3 indicates a cell colored in the fourth color (peach by default)

# placedShapes is a list of shapes that have currently been placed on the board.

    # Each shape is represented as a list containing three elements: a) the brush type (number between 0-8),
    # b) the location of the shape (coordinates of top-left cell of the shape) and c) color of the shape (number between 0-3)

    # For instance [0, (0,0), 2] represents a shape spanning a single cell in the color 2=veridian, placed at the top left cell in the grid.

# done is a Boolean that represents whether coloring constraints are satisfied. Updated by the gridgames.py file.

##############################################################################################################################

shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')

#input()   # <-- workaround to prevent PyGame window from closing after execute() is called, for when GUI set to True. Uncomment to enable.
print(shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done)


####################################################
# Timing your code's execution for the leaderboard.
####################################################

start = time.time()  # <- do not modify this.



##########################################
# Write all your code in the area below.
##########################################
import time
import numpy as np
import random
from gridgame import *

game = ShapePlacementGrid(GUI=False, render_delay_sec=0.1, gs=6, num_colored_boxes=5)
shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')
np.savetxt('initial_grid.txt', grid, fmt="%d")

##########################################
# Write all your code in the area below.
##########################################

# Improved Simulated Annealing for Grid Coloring
def simulated_annealing(max_iterations=5000, temp=3.0, cooling_rate=0.9995):
    """Uses simulated annealing to color the grid optimally while reducing conflicts."""
    def energy(grid):
        """Calculates the number of conflicts in the grid (adjacent same colors). Penalizes uncolored cells."""
        conflicts = 0
        uncolored_penalty = 0
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if grid[i][j] == -1:  # Penalize uncolored cells
                    uncolored_penalty += 1
                else:  # Count adjacent conflicts
                    if j < len(grid[i]) - 1 and grid[i][j] == grid[i][j + 1]:  # Right neighbor
                        conflicts += 1
                    if i < len(grid) - 1 and grid[i][j] == grid[i + 1][j]:  # Below neighbor
                        conflicts += 1
        return conflicts + uncolored_penalty

    for iteration in range(max_iterations):
        _, _, _, current_grid, _, _ = game.execute('export')
        current_energy = energy(current_grid)

        # Debug: Log iteration and energy
        print(f"Iteration: {iteration}, Temperature: {temp:.4f}, Current Energy: {current_energy}")

        # Select a random uncolored cell
        uncolored_positions = [(i, j) for i in range(len(grid)) for j in range(len(grid[i])) if grid[i][j] == -1]
        if not uncolored_positions:
            break  # Stop if all cells are colored
        x, y = random.choice(uncolored_positions)

        # Debug: Log selected cell
        print(f"Selected Cell: ({x}, {y})")

        # Move to position
        while shapePos[0] != x or shapePos[1] != y:
            if shapePos[0] < x:
                game.execute('down')
            elif shapePos[0] > x:
                game.execute('up')
            elif shapePos[1] < y:
                game.execute('right')
            elif shapePos[1] > y:
                game.execute('left')

        # Choose a valid color avoiding adjacent colors
        _, _, _, current_grid, _, _ = game.execute('export')
        adjacent_colors = set()

        if x > 0:
            adjacent_colors.add(current_grid[x-1][y])
        if x < len(grid) - 1:
            adjacent_colors.add(current_grid[x+1][y])
        if y > 0:
            adjacent_colors.add(current_grid[x][y-1])
        if y < len(grid[0]) - 1:
            adjacent_colors.add(current_grid[x][y+1])

        available_colors = [c for c in range(4) if c not in adjacent_colors]
        if available_colors:
            # Force placement to ensure all cells are colored
            print(f"Available colors for ({x}, {y}): {available_colors}")
            new_color = random.choice(available_colors)
            for _ in range(4):
                game.execute('switchcolor')
                _, _, selected_color, _, _, _ = game.execute('export')
                if selected_color == new_color:
                    break
            game.execute('place')
            print(f"Placement forced at ({x}, {y}) with color {new_color}")
            # Force placement if available colors exist to ensure coverage
            print(f"Available colors for ({x}, {y}): {available_colors}")
            new_color = random.choice(available_colors)
            for _ in range(4):
                game.execute('switchcolor')
                _, _, selected_color, _, _, _ = game.execute('export')
                if selected_color == new_color:
                    break
            try:
                game.execute('place')
                if hasattr(game, 'CheckGrid') and game.CheckGrid(game.grid):
                    print(f"Valid placement at ({x}, {y})")
            except AttributeError as e:
                print(f"Error during placement: {e}")
        else:
            print(f"No valid colors available for ({x}, {y}). Skipping placement.")

        # Evaluate new state
        _, _, _, new_grid, _, _ = game.execute('export')
        new_energy = energy(new_grid)

        # Debug: Log energy change
        print(f"New Energy: {new_energy}, Delta Energy: {new_energy - current_energy}")

        # Acceptance probability with reduced undo frequency
        delta_energy = new_energy - current_energy
        if delta_energy > 0 and random.random() > np.exp(-delta_energy / temp) and temp > 0.1:
            game.execute('undo')  # Revert change only if temperature is still high
            print("Undo operation performed.")  # Debug: Log undo operation

        # Gradual temperature decay to allow more exploration
        temp *= cooling_rate

        # Stop if solution is found
        if new_energy == 0:
            print("Solution found with no conflicts!")  # Debug: Log success
            break

    # Debug: Print final grid state
    _, _, _, final_grid, _, _ = game.execute('export')
    print("Final Grid State:")
    print(final_grid)

# Run Improved Simulated Annealing
simulated_annealing()

########################################
# Do not modify any of the code below.
########################################

########################################

# Do not modify any of the code below.

########################################

end=time.time()

np.savetxt('grid.txt', grid, fmt="%d")
with open("shapes.txt", "w") as outfile:
    outfile.write(str(placedShapes))
with open("time.txt", "w") as outfile:
    outfile.write(str(end-start))
