import random

from shallowBlue import ChessEngine


class Agent:
    def getAction(self, gameState):
        return None


class RandomAgent(Agent):
    def getAction(self, gameState):
        validMoves = gameState.getValidMoves()
        return validMoves[random.randint(0, len(validMoves) - 1)]


class GreedyAgent(Agent):
    def __init__(self, eFunction):
        self.evalFunction = eFunction

    def getAction(self, gameState):
        moves = gameState.getValidMoves()
        if gameState.checkmate or gameState.stalemate:
            return None
        scores = []
        for move in moves:
            gameState.makeMove(move)
            scores.append(self.evalFunction(gameState))
            gameState.undoMove()
        bestScore = max(scores)
        bestMoves = [moves[i] for i in range(0, len(moves)) if scores[i] == bestScore]
        return random.choice(bestMoves)


class EAgent(Agent):
    def __init__(self, eFunction,depth=32):
        self.evalFunction = eFunction
        self.depth = depth

    def maxValue(self, gameState, depth):
        if gameState.isWin() or gameState.isLose() or depth > self.depth:
            return self.evalFunction(gameState)
        return max([self.minValue(gameState.generateSuccessor(0, action), 1, depth)
                    for action in gameState.getLegalActions(0)])

    def minValue(self, gameState, index, depth):
        if gameState.isWin() or gameState.isLose():
            return self.evalFunction(gameState)
        if index != (gameState.getNumAgents() - 1):
            return sum([self.minValue(gameState.generateSuccessor(index, action), index + 1, depth)
                        for action in gameState.getLegalActions(index)]) / len(gameState.getLegalActions(index))
        else:
            return sum([self.maxValue(gameState.generateSuccessor(index, action), depth + 1)
                        for action in gameState.getLegalActions(index)]) / len(gameState.getLegalActions(index))

    def getAction(self, gameState):
        optAction = gameState.getLegalActions(0)[0]
        optValue = float("-inf")
        for action in gameState.getLegalActions(0):
            newValue = self.minValue(gameState.generateSuccessor(0, action), 1, 1)
            if newValue > optValue:
                optValue = newValue
                optAction = action
        return optAction




class ABAgent(Agent):
    def __init__(self, eFunction):
        self.evalFunction = eFunction

    def maxValue(self, gameState, depth, alpha0, beta0):
        if gameState.isWin() or gameState.isLose() or depth > self.depth:
            return self.evalFunction(gameState)
        val = float("-inf")
        alpha = alpha0
        for action in gameState.getLegalActions(0):
            val = max(val, self.minValue(gameState.generateSuccessor(0, action), 1, depth, alpha, beta0))
            if val > beta0:
                return val
            alpha = max(alpha, val)
        return val

    def minValue(self, gameState, index, depth, alpha0, beta0):
        if gameState.isWin() or gameState.isLose():
            return self.evalFunction(gameState)
        val = float("inf")
        beta = beta0
        if index != (gameState.getNumAgents() - 1):
            for action in gameState.getLegalActions(index):
                val = min(val,
                          self.minValue(gameState.generateSuccessor(index, action), index + 1, depth, alpha0, beta))
                if val < alpha0:
                    return val
                beta = min(beta, val)
            return val
        else:
            # only increment depth at the maximizers
            for action in gameState.getLegalActions(index):
                val = min(val, self.maxValue(gameState.generateSuccessor(index, action), depth + 1, alpha0, beta))
                if val < alpha0:
                    return val
                beta = min(beta, val)
            return val

    def getAction(self, gameState):
        optAction = gameState.getLegalActions(0)[0]
        optValue = float("-inf")
        alpha = float("-inf")
        for action in gameState.getLegalActions(0):
            newValue = self.minValue(gameState.generateSuccessor(0, action), 1, 1, alpha, float("inf"))
            if newValue > optValue:
                optValue = newValue
                optAction = action
            alpha = max(alpha, optValue)
        return optAction