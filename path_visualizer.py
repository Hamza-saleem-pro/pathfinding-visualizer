# Version 1.1 - Code Refactoring and Optimization
import tkinter as tk
import heapq
import random
import time
import math

THEME = {
    "background": "#B2B2B2",
    "panel": "#C8C8C8",
    "textDark": "#111111",
    "cellEmpty": "#DCDCDC",
    "cellWall": "#666666",
    "startColor": "#00AA66",
    "goalColor": "#CC3344",
    "visitedColor": "#3366CC",
    "pathColor": "#00CC88",
    "agentColor": "#8844CC",
}

CELL_SIZE = 28


# ---------------- HEURISTICS ----------------
def h_manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def h_euclidean(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def h_chebyshev(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

# Added heuristic optimization logic

HEURISTIC_MAP = {
    "Manhattan": h_manhattan,
    "Euclidean": h_euclidean,
    "Chebyshev": h_chebyshev,
}


# ---------------- SEARCH ALGORITHMS ----------------
def run_gbfs(source, target, rows, cols, blocks, heuristic, allowDiag):
    frontier = [(heuristic(source, target), source)]
    parent = {source: None}
    explored = []

    while frontier:
        _, current = heapq.heappop(frontier)
        explored.append(current)

        if current == target:
            break

        for neighbor in generate_neighbors(current, rows, cols, blocks, allowDiag):
            if neighbor not in parent:
                parent[neighbor] = current
                heapq.heappush(frontier, (heuristic(neighbor, target), neighbor))

    return build_path(parent, target), explored


def run_astar(source, target, rows, cols, blocks, heuristic, allowDiag):
    g_cost = {source: 0}
    parent = {source: None}
    closed = set()
    frontier = [(heuristic(source, target), 0, source)]
    explored = []

    while frontier:
        _, costSoFar, current = heapq.heappop(frontier)

        if current in closed:
            continue

        closed.add(current)
        explored.append(current)

        if current == target:
            break

        for neighbor in generate_neighbors(current, rows, cols, blocks, allowDiag):
            stepCost = math.hypot(neighbor[0] - current[0],
                                  neighbor[1] - current[1]) if allowDiag else 1

            newCost = costSoFar + stepCost

            if newCost < g_cost.get(neighbor, float("inf")):
                g_cost[neighbor] = newCost
                parent[neighbor] = current
                heapq.heappush(frontier,
                               (newCost + heuristic(neighbor, target),
                                newCost,
                                neighbor))

    return build_path(parent, target), explored


# ---------------- UTILITIES ----------------
def generate_neighbors(node, rows, cols, blocks, diagonal):
    r, c = node
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    if diagonal:
        directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            if (nr, nc) not in blocks:
                yield (nr, nc)


def build_path(parent, endNode):
    if endNode not in parent:
        return None

    path = []
    step = endNode

    while step is not None:
        path.append(step)
        step = parent[step]

    return path[::-1]


# ---------------- GUI APPLICATION ----------------
class PathfinderGUI:

    def __init__(self, window):
        self.window = window
        self.window.title("Pathfinding Visualizer")
        self.window.configure(bg=THEME["background"])

        self.gridRows = 15
        self.gridCols = 20

        self.startNode = (0, 0)
        self.goalNode = (14, 19)

        self.obstacleSet = set()
        self.finalPath = []
        self.exploredNodes = []

        self.algorithmChoice = tk.StringVar(value="A*")
        self.heuristicChoice = tk.StringVar(value="Manhattan")
        self.diagonalAllowed = tk.BooleanVar(value=False)

        self._build_interface()
        self._render_grid()

    # ---------------- UI ----------------
    def _build_interface(self):

        controlFrame = tk.Frame(self.window, bg=THEME["panel"])
        controlFrame.pack(fill=tk.X, pady=5)

        tk.Button(controlFrame,
                  text="RUN",
                  command=self._execute_search).pack(side=tk.LEFT, padx=5)

        tk.Button(controlFrame,
                  text="CLEAR",
                  command=self._clear_board).pack(side=tk.LEFT, padx=5)

        self.canvas = tk.Canvas(self.window,
                                width=self.gridCols * CELL_SIZE,
                                height=self.gridRows * CELL_SIZE,
                                bg=THEME["background"],
                                highlightthickness=0)

        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self._handle_click)

    # ---------------- GRID RENDER ----------------
    def _render_grid(self):

        self.canvas.delete("all")

        for r in range(self.gridRows):
            for c in range(self.gridCols):
                cell = (r, c)

                x1 = c * CELL_SIZE
                y1 = r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                if cell == self.startNode:
                    color = THEME["startColor"]
                elif cell == self.goalNode:
                    color = THEME["goalColor"]
                elif cell in self.obstacleSet:
                    color = THEME["cellWall"]
                elif cell in self.finalPath:
                    color = THEME["pathColor"]
                elif cell in self.exploredNodes:
                    color = THEME["visitedColor"]
                else:
                    color = THEME["cellEmpty"]

                self.canvas.create_rectangle(x1, y1, x2, y2,
                                             fill=color,
                                             outline=THEME["background"])

    # ---------------- EVENTS ----------------
    def _handle_click(self, event):

        r = event.y // CELL_SIZE
        c = event.x // CELL_SIZE
        node = (r, c)

        if node in (self.startNode, self.goalNode):
            return

        if node in self.obstacleSet:
            self.obstacleSet.remove(node)
        else:
            self.obstacleSet.add(node)

        self._render_grid()

    # ---------------- SEARCH EXECUTION ----------------
    def _execute_search(self):

        heuristicFn = HEURISTIC_MAP[self.heuristicChoice.get()]

        if self.algorithmChoice.get() == "A*":
            path, visited = run_astar(self.startNode,
                                      self.goalNode,
                                      self.gridRows,
                                      self.gridCols,
                                      self.obstacleSet,
                                      heuristicFn,
                                      self.diagonalAllowed.get())
        else:
            path, visited = run_gbfs(self.startNode,
                                     self.goalNode,
                                     self.gridRows,
                                     self.gridCols,
                                     self.obstacleSet,
                                     heuristicFn,
                                     self.diagonalAllowed.get())

        self.finalPath = path or []
        self.exploredNodes = visited
        self._render_grid()

    def _clear_board(self):
        self.obstacleSet.clear()
        self.finalPath = []
        self.exploredNodes = []
        self._render_grid()


if __name__ == "__main__":
    root = tk.Tk()
    PathfinderGUI(root)

    root.mainloop()

