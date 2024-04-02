import time, os, sys
import random, math


try:  # import as appropriate for 2.x vs. 3.x
   import tkinter as tk
   #from tkinter import messagebox
   from tkinter.messagebox import *
except:
   import Tkinter as tk
   from tkMessageBox import *



class Puzzle:
    def __init__(self):
        self.N = 4
        self.size = 70
        self.board = [[None for j in range(self.N)] for i in range(self.N)]
        self.action_list = ["Right", "Left", "Up", "Down"]
        
        self.step = 0
        self.action = None
        self.score = 0
        self.gameState = None
        
        self.root = tk.Tk()
    
    def start(self):
        self.init_board()
        
        self.root.title("2048")
        #self.root.geometry('300x300')
        self.root.minsize(430,300)
        self.root.maxsize(430,300)
        
        self.canvas = tk.Canvas(self.root, bd=0, width=300, height=300)
        self.canvas.place(x=0,y=0)
        #self.canvas.pack()
        
        self.canvas.bind("<Button-1>", self._onClick)
        self.canvas.bind_all("<Key>", self._onKey)
        
        
        # right
        self.stepLabel = tk.Label(self.root, text="step: "+str(self.step))
        self.stepLabel.place(x=300,y=10)
        self.actionLabel = tk.Label(self.root, text="action: "+str(self.action))
        self.actionLabel.place(x=300,y=40)
        self.scoreLabel = tk.Label(self.root, text="score: "+str(self.score))
        self.scoreLabel.place(x=300,y=70)
        
        newGame = tk.Button(self.root, text="New Game", command=self.newGame)
        newGame.place(x=300,y=100)
        runAI = tk.Button(self.root, text="AI", command=self.runAI)
        runAI.place(x=300,y=130)
        pauseGame = tk.Button(self.root, text="Pause/Continue", command=self.pauseGame)
        pauseGame.place(x=300,y=160)
        
        
        self.paint()
        
        self.root.mainloop()
        
    
    def init_board(self):
        for i in range(self.N):
            for j in range(self.N):
                self.board[i][j] = None
        self.rand_generate_one_piece()
        self.rand_generate_one_piece()
        
        self.step = 0
        self.action = None
        self.score =0
        self.gameState = "running"
    
    def rand_generate_one_piece(self):
        P = []
        for i in range(self.N):
            for j in range(self.N):
                if self.board[i][j] == None:
                    P.append( (i,j) )
        
        if len(P) <= 0:
            return False
        else:
            r = random.randint(0, len(P)-1)
            self.board[P[r][0]][P[r][1]] = 2
            return True
    
    def newGame(self):
        self.init_board()
        self.paint()
    
    def pauseGame(self):
        #showinfo("End Game", "End game!")
        if self.gameState=='running':
            self.gameState = "stop"
        elif self.gameState=="stop":
            self.gameState = "running"
        #exit()
    
    def gameWin(self):
        for i in range(self.N):
            for j in range(self.N):
                if self.board[i][j]==2048:
                    return True
        return False
    
    def is_same(self, board1, board2):
        for i in range(self.N):
            for j in range(self.N):
                if board1[i][j] != board2[i][j]:
                    return False
        return True
    
    def get_all_possible_actions(self):
        board = [[self.board[i][j] for j in range(self.N)] for i in range(self.N)]
        action_list = []
        for action in self.action_list:
            # try to make the move, to see whether the board changed ?
            self.makeMove(action)
            if not self.is_same(self.board, board):
                action_list.append( action )
            # recover
            self.board = [[board[i][j] for j in range(self.N)] for i in range(self.N)]
        return action_list
    
    def get_score(self):
        score = 0
        for i in range(self.N):
            for j in range(self.N):
                if self.board[i][j]==None or self.board[i][j]==2:
                    continue
                
                if self.board[i][j]==4:
                    score += 4
                else:
                    score += self.board[i][j]*2
        return score                    
    
    def simulation(self, MaxStep=50):
        board = [[self.board[i][j] for j in range(self.N)] for i in range(self.N)]
        
        step = 0
        while step < MaxStep:
            action_list = self.get_all_possible_actions()
            # game over
            if len(action_list)==0:
                break
                
            # randomly pick an action
            action = action_list[random.randint(0,len(action_list)-1)]
            self.makeMove(action)
            step += 1
            
            # game over
            if not self.rand_generate_one_piece():
                break
        
        score = self.get_score()
        self.board = [[board[i][j] for j in range(self.N)] for i in range(self.N)]
        return score
    
    # score is the total score for the current node
    # Ni is the total simulation number for the current node
    # Np is the total simulation number for the parent node
    def get_UCT(self, score, Ni, Np, c=1.414):
        if Ni==0:
            return 100.0
        if Np==0:
            return 1.0
        
        return 0.5*math.log(score+1.0)/math.log(2048.0) + c*math.sqrt(math.log(1.0*Np)/Ni)
    
    def selection(self, tree_node, c=1.414, depth=0):
        # choose the one node with max UCT
        max_UCT, s_action = 0.0, None
        action_list = self.get_all_possible_actions()
        if len(action_list)==0:
            return 0
            
        for action in action_list:
            if str(action) in tree_node:
                (score, Ni) = tree_node[str(action)]['info']
            else:
                score, Ni = 0.0, 0
            Np = tree_node['info'][1]
            UCT = self.get_UCT(score, Ni, Np, c)
            if max_UCT <= UCT:
                max_UCT, s_action = UCT, action
        
        # make the action along the path
        self.makeMove(s_action)
        # generate a new piece
        self.rand_generate_one_piece()
        
        # it's not a leaf node
        if str(s_action) in tree_node:
            score = self.selection(tree_node[str(s_action)], c, depth+1)
        else:
            # new tree node
            tree_node[str(s_action)] = {'info':(0.0,0)}
            score = self.simulation()
        
        # update the score/Ni along the path from the leaf node to the root
        (_score, _Ni) = tree_node[str(s_action)]['info']
        tree_node[str(s_action)]['info'] = (_score+score, _Ni+1)
        
        return score
    
    def AI(self):
        start_time = time.time()
        
        # tree node: (score, Ni) (total score and total game number)
        root = {'info': (0,0)}
        # MCTS
        while True:
            # time out
            if time.time() - start_time > 1.0:
                break
            
            board = [[self.board[i][j] for j in range(self.N)] for i in range(self.N)]
            score = self.selection(root)
            self.board = [[board[i][j] for j in range(self.N)] for i in range(self.N)]
            
            (_score, _Ni) = root['info']
            root['info'] = (_score+score, _Ni+1)
        
        # choose the best action with max win rate
        best_action, avg_score, score_Ni = None, 0.0, None
        for action in self.get_all_possible_actions():
            if str(action) in root:
                (_score, _Ni) = root[str(action)]['info']
            else:
                (_score, _Ni) = 0, 1
            #print(action, _score, _Ni)
            
            if avg_score <= 1.0*_score/_Ni:
                best_action, avg_score, score_Ni = action, 1.0*_score/_Ni, (_score, _Ni)
        
        print(best_action, score_Ni)
        return best_action
    
    def runAI(self):
        step = 10
        while self.gameState == "running":
            self.action = self.AI()
            self.makeMove(self.action)
            self.step += 1
            self.paint()
            
            if self.gameWin():
                self.gameState = "win"
                showinfo("Win", "You meet 2048!")
                return
            
            if not self.rand_generate_one_piece():
                self.gameState = "lose"
                showinfo("Lose", "The board is full!")
                return
            self.paint()
            
            #step -= 1
            #if step==0:
            #    break
    
    
    def _onClick(self, e):
        if self.gameState != "running": return
        """        
        x, y = int(e.x/self.size), int(e.y/self.size)
        print(e.x, e.y, x, y)
        """
        
    def _onKey(self, event):
        key = event.keysym
        print(key)
        if self.gameState != "running":
            return
        if key not in ["Right",'a','Left','d','Up','w','Down','s']:
            return
        
        self.action = key
        self.makeMove(self.action)
        self.step += 1
        self.paint()
        
        if not self.rand_generate_one_piece():
            self.gameState = "over"
            showinfo("Lose", "The board is full!")
            return
        self.paint()
        
    
    def makeMove(self, action):
        if action in ["Right", 'a']:
            self.move_right()
        elif action in ["Left", 'd']:
            self.move_left()
        elif action in ["Up", 'w']:
            self.move_up()
        elif action in ["Down", 's']:
            self.move_down()
    
    def paint(self):
        self.stepLabel.config(text="step: "+str(self.step))
        self.actionLabel.config(text="action: "+str(self.action))
        self.score = self.get_score()
        self.scoreLabel.config(text="score: "+str(self.score))
        
        self.canvas.delete("all")
        color = {None:"gray", 2:"gray", 4:"pink", 8:"orange", 16:"gold", 32:"yellow", 64:"blue", 128:"red", 256:"red", 512:"green", 1024:"green", 2048:"green"}
        for j in range(self.N):
            for i in range(self.N):
                c = color[self.board[j][i]]
                self.canvas.create_rectangle(i*self.size, j*self.size, (i+1)*self.size-5, (j+1)*self.size-5, fill=c)
                if self.board[j][i] != None:
                    #print(j, i)
                    self.canvas.create_text(i*self.size+35, j*self.size+35, text=str(self.board[j][i]), font=("Purisa",20))
        self.canvas.update()
        
        time.sleep(.1)
    
    def move_right(self):
        for j in range(self.N):
            Q = []
            for i in range(self.N-1, -1, -1):
                if self.board[j][i] != None:
                    Q.append( self.board[j][i] )
                self.board[j][i] = None
            
            Qi, Qn = 0, len(Q)
            for i in range(self.N-1, -1, -1):
                if Qi < Qn:
                    self.board[j][i] = Q[Qi]
                    Qi += 1
                    
                    if Qi<Qn and Q[Qi-1]==Q[Qi]:
                        self.board[j][i] *= 2
                        Qi += 1
    
    def move_left(self):
        for j in range(self.N):
            Q = []
            for i in range(0, self.N, 1):
                if self.board[j][i] != None:
                    Q.append( self.board[j][i] )
                self.board[j][i] = None
            
            Qi, Qn = 0, len(Q)
            for i in range(0, self.N, 1):
                if Qi < Qn:
                    self.board[j][i] = Q[Qi]
                    Qi += 1
                    
                    if Qi<Qn and Q[Qi-1]==Q[Qi]:
                        self.board[j][i] *= 2
                        Qi += 1
    
    def move_up(self):
        for i in range(self.N):
            Q = []
            for j in range(0, self.N, 1):
                if self.board[j][i] != None:
                    Q.append( self.board[j][i] )
                self.board[j][i] = None
            
            Qi, Qn = 0, len(Q)
            for j in range(0, self.N, 1):
                if Qi < Qn:
                    self.board[j][i] = Q[Qi]
                    Qi += 1
                    
                    if Qi<Qn and Q[Qi-1]==Q[Qi]:
                        self.board[j][i] *= 2
                        Qi += 1
    
    def move_down(self):
        for i in range(self.N):
            Q = []
            for j in range(self.N-1, -1, -1):
                if self.board[j][i] != None:
                    Q.append( self.board[j][i] )
                self.board[j][i] = None
            
            Qi, Qn = 0, len(Q)
            for j in range(self.N-1, -1, -1):
                if Qi < Qn:
                    self.board[j][i] = Q[Qi]
                    Qi += 1
                    
                    if Qi<Qn and Q[Qi-1]==Q[Qi]:
                        self.board[j][i] *= 2
                        Qi += 1


if __name__ == "__main__":
    puzzle = Puzzle()
    puzzle.start()
