import pygame

from shallowBlue import ChessEngine
from shallowBlue import Agents

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION  # // for ints rather than float
MAX_FPS = 15
IMAGES = {}  # a python dictionary for images, indexing by IMAGES['bP']
Agent = Agents.GreedyAgent(ChessEngine.materialBalance)
RAgent = Agents.RandomAgent()
"""
initialize a global dictionary of images
this will be called exactly one time in a game of chess
"""


def load_images():
    pieces = ['wP', 'bP', 'wR', 'bR', 'wN', 'bN', 'wB', 'bB', 'wK', 'bK', 'wQ', 'bQ']
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(
            pygame.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    screen.fill(pygame.Color("white"))
    state = ChessEngine.GameState()
    valid_moves = state.getValidMoves()
    move_made = False  # only regenerate when a valid move is made
    gameOver = False
    playerWhite = True  # if real person - True, if AI false
    playerBlack = True

    load_images()
    running = True
    sq_selected = ()
    clicks = []
    while running:
        humanTurn = (state.whiteToMove and playerWhite) or (not state.whiteToMove and playerBlack)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            # mouse events
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if not gameOver:
                    # if human player's turn
                    if not gameOver and humanTurn:
                        location = pygame.mouse.get_pos()  # (x,y) of mouse event
                        row = location[1] // SQ_SIZE
                        col = location[0] // SQ_SIZE
                        if sq_selected == (row, col):
                            # click the same square twice --> unselect
                            sq_selected = ()
                            clicks = []
                        else:
                            sq_selected = (row, col)
                            clicks.append(sq_selected)
                        if len(clicks) == 2:
                            move = ChessEngine.Move(clicks[0], clicks[1], state.board)
                            print(move.getChessNotation())
                            for i in range(len(valid_moves)):
                                if move == valid_moves[i]:
                                    state.makeMove(valid_moves[i])
                                    move_made = True
                                    if state.checkmate or state.stalemate:
                                        gameOver = True
                                    sq_selected = ()
                                    clicks = []
                            if not move_made:
                                clicks = [sq_selected]
            # key events
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_z:  # if z is pressed
                    state.undoMove()
                    move_made = True
                # reset the board
                if e.key == pygame.K_r:  # if r is pressed
                    state = ChessEngine.GameState()
                    sq_selected = ()
                    clicks = []
                    move_made = False

        # ai move finder (no events needed
        if not gameOver and not humanTurn:
            valid_moves = state.getValidMoves()
            if state.checkmate or state.stalemate:
                state.gameOver = True
                return
            moveAI = Agent.getAction(state)
            if moveAI is None:
                moveAI = RAgent.getAction(state)
            state.makeMove(moveAI)
            move_made = True

        if move_made:
            valid_moves = state.getValidMoves()
            move_made = False

        draw(screen, state, valid_moves, sq_selected)

        # TODO check gameOVer
        if gameOver:
            if state.checkmate:
                if state.whiteToMove:
                    drawText(screen, "black wins - checkmate")
                else:
                    drawText(screen, "white wins - checkmate")
            elif state.stalemate:
                drawText(screen, "stalemate")

        clock.tick(MAX_FPS)
        pygame.display.flip()


def draw_squares(screen):
    colors = [pygame.Color("white"), pygame.Color("lightblue")]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            pygame.draw.rect(screen, colors[(row + col) % 2],
                             pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, game_state):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = game_state.board[row][col]
            if piece != "ES":
                screen.blit(IMAGES[piece], pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def highlight(screen, gameState, validMoves, sqSelected):
    if sqSelected == ():
        return
    row, col = sqSelected
    if (gameState.whiteToMove and gameState.board[row][col][0] == "w") or (
            not gameState.whiteToMove and gameState.board[row][col][0] == "b"):
        # highlight sq
        surface = pygame.Surface((SQ_SIZE, SQ_SIZE))
        surface.set_alpha(100)  # 0->transparent, 255->opaque
        surface.fill(pygame.Color("gold"))
        screen.blit(surface, (col * SQ_SIZE, row * SQ_SIZE))
        # highlight moves
        surface.fill(pygame.Color("aquamarine"))
        for move in validMoves:
            if move.row0 == row and move.col0 == col:
                screen.blit(surface, (move.col1 * SQ_SIZE, move.row1 * SQ_SIZE))


def draw(screen, game_state, validMoves, sqSelected):
    draw_squares(screen)
    highlight(screen, game_state, validMoves, sqSelected)
    draw_pieces(screen, game_state)  # draw pieces on top of squares


def drawText(screen, text):
    print(text)
    font = pygame.font.SysFont("Helvtica", 30, True, False)
    textAdded = font.render(text, 0, pygame.Color("Black"))
    textLocation = pygame.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH / 2 - textAdded.get_width() / 2, HEIGHT / 2 - textAdded.get_height() / 2)
    screen.blit(textAdded, textLocation)


if __name__ == "__main__":
    main()
