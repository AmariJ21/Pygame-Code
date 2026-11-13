"""
2x2 Cube Solver (works for picture cubes like the $100-bill cube too!)

HOW TO USE
1. Pick a "picture" color at the bottom of the window, then click squares
   to paint them. Each of the 6 colors stands for one of the 6 pictures
   your cube shows when it is solved. (Tip: on a picture cube it helps to
   put a tiny sticky dot on each piece first.)
2. Hold your real cube so the FRONT faces you and the TOP points up,
   and paint the drawing to match: U = top, F = front, R = right,
   L = left, B = back, D = bottom.
3. Press SOLVE. Then press NEXT (or the right arrow) and do each turn
   on your real cube. The squares that move are outlined in yellow.
   Don't turn the whole cube while you follow along!

KEYS
  R / U / F         turn that side  (hold SHIFT to turn the other way)
  Right / Left      next / previous step of the solution
  Space             solve
"""

import random
import sys
from collections import Counter
from operator import itemgetter

import pygame

# ---------------------------------------------------------------------------
# The cube model
#
# A 2x2 cube has 24 little squares ("stickers"), 4 on each of 6 faces.
# Each sticker lives at a corner position (x, y, z), where every number is
# -1 or +1, and points out in one direction (its "normal").
# To turn a side we just rotate the positions and normals of the stickers
# on that side, and see where each sticker ends up.
# ---------------------------------------------------------------------------

FACES = "URFDLB"
NORMALS = {
    "U": (0, 1, 0), "D": (0, -1, 0),
    "R": (1, 0, 0), "L": (-1, 0, 0),
    "F": (0, 0, 1), "B": (0, 0, -1),
}


def spot_on_face(face, x, y, z):
    """Which (column, row) a sticker sits in when you look at its face."""
    if face == "F":
        return (x + 1) // 2, (1 - y) // 2
    if face == "B":
        return (1 - x) // 2, (1 - y) // 2
    if face == "R":
        return (1 - z) // 2, (1 - y) // 2
    if face == "L":
        return (z + 1) // 2, (1 - y) // 2
    if face == "U":
        return (x + 1) // 2, (z + 1) // 2
    if face == "D":
        return (x + 1) // 2, (1 - z) // 2


# Build the list of all 24 stickers: index -> (position, face letter)
STICKERS = [None] * 24
for face_number, face in enumerate(FACES):
    nx, ny, nz = NORMALS[face]
    for x in (-1, 1):
        for y in (-1, 1):
            for z in (-1, 1):
                # the sticker is on this face if the piece touches that side
                if (nx and x == nx) or (ny and y == ny) or (nz and z == nz):
                    col, row = spot_on_face(face, x, y, z)
                    STICKERS[face_number * 4 + row * 2 + col] = ((x, y, z), face)

FIND_STICKER = {sticker: i for i, sticker in enumerate(STICKERS)}
NORMAL_TO_FACE = {v: k for k, v in NORMALS.items()}


def quarter_turn(face):
    """Return a recipe (list) for turning one side a quarter turn clockwise."""

    def spin(p):
        x, y, z = p
        if face == "R":
            return (x, z, -y)
        if face == "U":
            return (-z, y, x)
        if face == "F":
            return (y, -x, z)

    axis = "xyz".index({"R": "x", "U": "y", "F": "z"}[face])
    new_from_old = [0] * 24
    for old_index, (pos, sticker_face) in enumerate(STICKERS):
        if pos[axis] == 1:  # this sticker is on the side that turns
            new_pos = spin(pos)
            new_face = NORMAL_TO_FACE[spin(NORMALS[sticker_face])]
            new_index = FIND_STICKER[(new_pos, new_face)]
        else:
            new_index = old_index
        new_from_old[new_index] = old_index
    return new_from_old


def combine(first, second):
    """Doing recipe `first` and then recipe `second`."""
    return [first[i] for i in second]


# We only ever turn R, U and F. That way the Down-Back-Left piece never
# moves, so it tells us which way the solved cube should face.
MOVES = {}
for side in "RUF":
    once = quarter_turn(side)
    twice = combine(once, once)
    MOVES[side] = once
    MOVES[side + "2"] = twice
    MOVES[side + "'"] = combine(twice, once)

MOVE_NAMES = list(MOVES)
TURNERS = {name: itemgetter(*recipe) for name, recipe in MOVES.items()}


def do_move(state, name):
    return TURNERS[name](state)


def opposite_move(name):
    if name.endswith("2"):
        return name
    if name.endswith("'"):
        return name[0]
    return name + "'"


# The 8 corner pieces, each as a list of its 3 sticker numbers
CORNERS = []
for x in (-1, 1):
    for y in (-1, 1):
        for z in (-1, 1):
            corner = []
            for face, (nx, ny, nz) in NORMALS.items():
                if (nx and x == nx) or (ny and y == ny) or (nz and z == nz):
                    corner.append(FIND_STICKER[((x, y, z), face)])
            CORNERS.append(corner)

SOLVED = tuple(i // 4 for i in range(24))


def solved_version_of(state):
    """
    Work out what this cube looks like when it's solved, using the
    Down-Back-Left piece (which never moves) as our guide.
    Returns (solved_state, None) or (None, error message).
    """
    if -1 in state:
        return None, "Paint every square first!"
    counts = Counter(state)
    for color, n in counts.items():
        if n != 4:
            return None, f"{COLOR_NAMES[color]} is used {n} times (needs 4)."
    if len(counts) != 6:
        return None, "You need to use all 6 colors."

    # Which colors sit next to each other on some corner?
    neighbors = {c: set() for c in counts}
    for corner in CORNERS:
        colors = {state[i] for i in corner}
        if len(colors) != 3:
            return None, "A corner has the same color twice."
        for c in colors:
            neighbors[c] |= colors - {c}

    # Opposite colors never touch
    opposite = {}
    for c in counts:
        far = set(counts) - neighbors[c] - {c}
        if len(far) != 1:
            return None, "Those colors can't all be on a real cube."
        opposite[c] = far.pop()

    face_color = {}
    for face in "DBL":
        face_color[face] = state[FIND_STICKER[((-1, -1, -1), face)]]
    face_color["U"] = opposite[face_color["D"]]
    face_color["F"] = opposite[face_color["B"]]
    face_color["R"] = opposite[face_color["L"]]
    solved = tuple(face_color[FACES[i // 4]] for i in range(24))

    want = sorted(sorted(solved[i] for i in c) for c in CORNERS)
    have = sorted(sorted(state[i] for i in c) for c in CORNERS)
    if want != have:
        return None, "Some corner pieces don't exist on a real cube."
    return solved, None


def find_solution(start, goal):
    """
    Search from both ends at once (from the mixed-up cube AND from the
    solved cube) until the two searches meet in the middle.
    Any 2x2 can be solved in 11 turns or fewer, so this is quick.
    """
    if start == goal:
        return []
    came_from_start = {start: None}
    came_from_goal = {goal: None}
    start_edge = [start]
    goal_edge = [goal]

    for _ in range(12):
        grow_start = len(start_edge) <= len(goal_edge)
        edge = start_edge if grow_start else goal_edge
        mine = came_from_start if grow_start else came_from_goal
        theirs = came_from_goal if grow_start else came_from_start
        new_edge = []
        for state in edge:
            for name in MOVE_NAMES:
                nxt = do_move(state, name)
                if nxt in mine:
                    continue
                mine[nxt] = (state, name)
                new_edge.append(nxt)
                if nxt in theirs:
                    return build_path(nxt, came_from_start, came_from_goal)
        if grow_start:
            start_edge = new_edge
        else:
            goal_edge = new_edge
        if not new_edge:
            break
    return None  # impossible: a corner is probably twisted


def build_path(middle, came_from_start, came_from_goal):
    first_half = []
    state = middle
    while came_from_start[state] is not None:
        state, name = came_from_start[state]
        first_half.append(name)
    first_half.reverse()

    second_half = []
    state = middle
    while came_from_goal[state] is not None:
        state, name = came_from_goal[state]
        second_half.append(opposite_move(name))
    return first_half + second_half


def explain(name):
    side = name[0]
    if name.endswith("2"):
        how = "TWICE (half turn)"
    elif side == "R":
        how = "toward you (DOWN)" if "'" in name else "away from you (UP)"
    elif side == "U":
        how = "to the RIGHT" if "'" in name else "to the LEFT"
    else:
        how = "counter-clockwise" if "'" in name else "clockwise"
    where = {"R": "Right side", "U": "Top", "F": "Front"}[side]
    return f"{where}: turn {how}"


# ---------------------------------------------------------------------------
# The window
# ---------------------------------------------------------------------------

COLORS = [(245, 245, 245), (255, 213, 0), (0, 155, 72),
          (0, 80, 190), (200, 20, 40), (255, 120, 0)]
COLOR_NAMES = ["White", "Yellow", "Green", "Blue", "Red", "Orange"]
BLANK = (90, 90, 90)
BACKGROUND = (30, 32, 40)
TEXT = (230, 230, 230)
HIGHLIGHT = (255, 230, 60)

WIDTH, HEIGHT = 980, 640
SQ = 54                # size of one little square
FACE_SIZE = 2 * SQ + 12
NET_X, NET_Y = 30, 40
FACE_SPOTS = {"U": (1, 0), "L": (0, 1), "F": (1, 1),
              "R": (2, 1), "B": (3, 1), "D": (1, 2)}


def sticker_rect(i):
    face = FACES[i // 4]
    row, col = divmod(i % 4, 2)
    fx, fy = FACE_SPOTS[face]
    return pygame.Rect(NET_X + fx * FACE_SIZE + col * SQ,
                       NET_Y + fy * FACE_SIZE + row * SQ, SQ - 3, SQ - 3)


def stickers_that_move(name):
    recipe = MOVES[name]
    return {i for i in range(24) if recipe[i] != i}


class Button:
    def __init__(self, label, x, y, w=130, h=42):
        self.label = label
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, screen, font):
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (90, 110, 160) if hover else (65, 75, 110),
                         self.rect, border_radius=8)
        words = font.render(self.label, True, TEXT)
        screen.blit(words, words.get_rect(center=self.rect.center))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("2x2 Cube Solver")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    small = pygame.font.SysFont(None, 22)
    big = pygame.font.SysFont(None, 40)

    cube = list(SOLVED)
    picked_color = 0
    solution = []
    step = 0
    message = "Paint your cube, then press SOLVE."

    panel_x = 560
    buttons = {
        "solve": Button("SOLVE", panel_x, 30),
        "next": Button("NEXT >", panel_x + 145, 30),
        "back": Button("< BACK", panel_x + 290, 30),
        "scramble": Button("Scramble", panel_x, 85),
        "solved": Button("Solved", panel_x + 145, 85),
        "clear": Button("Clear", panel_x + 290, 85),
    }
    swatches = [pygame.Rect(NET_X + i * 75, 440, 60, 60) for i in range(6)]

    def forget_solution():
        nonlocal solution, step
        solution, step = [], 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            pressed = None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, swatch in enumerate(swatches):
                    if swatch.collidepoint(event.pos):
                        picked_color = i
                for i in range(24):
                    if sticker_rect(i).collidepoint(event.pos):
                        cube[i] = picked_color
                        forget_solution()
                        message = "Painting... press SOLVE when done."
                for name, button in buttons.items():
                    if button.rect.collidepoint(event.pos):
                        pressed = name

            if event.type == pygame.KEYDOWN:
                shift = event.mod & pygame.KMOD_SHIFT
                side = {pygame.K_r: "R", pygame.K_u: "U", pygame.K_f: "F"}.get(event.key)
                if side and -1 not in cube:
                    cube = list(do_move(tuple(cube), side + ("'" if shift else "")))
                    forget_solution()
                    message = "You turned the cube. Press SOLVE to solve it."
                elif event.key == pygame.K_RIGHT:
                    pressed = "next"
                elif event.key == pygame.K_LEFT:
                    pressed = "back"
                elif event.key == pygame.K_SPACE:
                    pressed = "solve"

            if pressed == "solve":
                solved, problem = solved_version_of(tuple(cube))
                if problem:
                    message = problem
                else:
                    message = "Thinking..."
                    answer = find_solution(tuple(cube), solved)
                    if answer is None:
                        message = "Can't solve: a corner looks twisted. Double-check your colors."
                    elif not answer:
                        message = "It's already solved!"
                    else:
                        solution, step = answer, 0
                        message = f"Solved in {len(answer)} turns! Press NEXT for each turn."
            elif pressed == "next" and step < len(solution):
                cube = list(do_move(tuple(cube), solution[step]))
                step += 1
                if step == len(solution):
                    message = "All done - your cube is solved!"
            elif pressed == "back" and step > 0:
                step -= 1
                cube = list(do_move(tuple(cube), opposite_move(solution[step])))
                message = "Went back one step."
            elif pressed == "scramble":
                cube = list(SOLVED)
                for _ in range(25):
                    cube = list(do_move(tuple(cube), random.choice(MOVE_NAMES)))
                forget_solution()
                message = "Scrambled! Press SOLVE."
            elif pressed == "solved":
                cube = list(SOLVED)
                forget_solution()
                message = "Reset to solved."
            elif pressed == "clear":
                cube = [-1] * 24
                forget_solution()
                message = "Cleared. Paint all 24 squares."

        # ----- draw everything -----
        screen.fill(BACKGROUND)

        upcoming = solution[step] if step < len(solution) else None
        glowing = stickers_that_move(upcoming) if upcoming else set()

        for face, (fx, fy) in FACE_SPOTS.items():
            label = small.render(face, True, (150, 150, 160))
            screen.blit(label, (NET_X + fx * FACE_SIZE + SQ - 5,
                                NET_Y + fy * FACE_SIZE - 17))
        for i in range(24):
            rect = sticker_rect(i)
            color = BLANK if cube[i] == -1 else COLORS[cube[i]]
            pygame.draw.rect(screen, color, rect, border_radius=6)
            if i in glowing:
                pygame.draw.rect(screen, HIGHLIGHT, rect, 4, border_radius=6)

        screen.blit(font.render("Paint with:", True, TEXT), (NET_X, 412))
        for i, swatch in enumerate(swatches):
            pygame.draw.rect(screen, COLORS[i], swatch, border_radius=8)
            if i == picked_color:
                pygame.draw.rect(screen, HIGHLIGHT, swatch.inflate(8, 8), 4,
                                 border_radius=10)

        for button in buttons.values():
            button.draw(screen, font)

        screen.blit(font.render(message, True, HIGHLIGHT), (NET_X, 530))

        if upcoming:
            screen.blit(font.render(f"Step {step + 1} of {len(solution)}:",
                                    True, TEXT), (panel_x, 150))
            screen.blit(big.render(upcoming, True, HIGHLIGHT), (panel_x, 180))
            screen.blit(font.render(explain(upcoming), True, TEXT),
                        (panel_x + 60, 186))

        if solution:
            y = 240
            for n, name in enumerate(solution):
                done = n < step
                color = (110, 110, 120) if done else (HIGHLIGHT if n == step else TEXT)
                line = f"{n + 1:>2}. {name:<3} {explain(name)}"
                screen.blit(small.render(line, True, color), (panel_x, y))
                y += 24

        help_lines = [
            "Hold the cube with FRONT facing you, TOP up.",
            "Keys: R U F to turn (SHIFT = other way),",
            "arrows = next/back, SPACE = solve.",
        ]
        for n, line in enumerate(help_lines):
            screen.blit(small.render(line, True, (150, 150, 160)), (NET_X, 565 + n * 22))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
