

Program function flow:
1. start() display the game interface, you can manually operate the game by pressing button Right/Left/Up/Down.
2. When user clicks AI button, AI takes over the game. Enter runAI() function, which will always call function AI() to get the next operation. 3.
3. function AI(), the algorithm used is MCTS strategy + UCT optimisation, in four stages: selection, expansion, simulation, backtracking.
	The related functions are selection(), get_UCT(), simulation().
4. According to the target operation returned by AI(), go to the functions move_right()/move_left()/move_up()/move_down().
5. After that, use the gameWin() function to judge if you win (2048?).
6. If you win, game over. If you don't, add a 2 at a random location via the rand_generate_one_piece() function. 7.
7. Continue until the end of the game.



MCTS strategy + UCT optimisation Algorithmic flow:
1. initially one root node
2. move down the child node with the largest UCT each time until it reaches a leaf node
3. expand a new node on that leaf node, and then perform a game simulation (randomly perform game operations up to a maximum of 50 steps, and return the score of the final game)
4. take the simulated game score and update it to the overall path for UCT calculation
5. Repeat steps 2-5 until a certain time.
6. When finished, select the optimal one child node under the root node, the corresponding operation, can be.

The base UCT formula is Vi + c * sqrt(log(Np)/Ni), where Vi is the child node win rate, c is a constant, NP is the number of parent node simulations, and Ni is the number of child node simulations.
Here Vi is replaced with the average child node score (normalised) and c takes the default value sqrt(2).



Among them, the difficulty lies in the construction of the tree and the implementation of the four-stage procedure, which requires a deep understanding of the algorithm connotation. In addition, there are several parameters in it:
1. The maximum simulation step size is 50 steps, which is not too large and not too small. Too small simulation results are meaningless, too large simulation time is too long.
2. The score is calculated as 4 points for 2 and 2 combined, 8 points for 4 and 4 combined, and others similar.
3. Vi is the average simulation score, which needs to be normalised. In the base formula is the sub-node win rate, which ranges from 0-1, just normalise the average simulation score in this range.

