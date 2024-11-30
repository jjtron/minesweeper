import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        n = 0
        while len(self.mines) != 1:
            i = 2 #random.randrange(height)
            j = 2 #random.randrange(width)
            #n += 1
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        raise NotImplementedError

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        raise NotImplementedError

    def mark_mine(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        # 1 Mark the cell as a move that has been made
        self.moves_made.add(cell)
        # 2 Mark the cell as safe
        self.mark_safe(cell)
        # 3 Add a new sentence to the AI's knowledge base ...
        neighbors = self.get_neighbors(cell)
        new_sentence = Sentence(neighbors, count)
        self.knowledge.append(new_sentence)

        # 4 Mark any additional cells as safe or as mines ...
        for i in range(0, len(self.knowledge)):
            if self.knowledge[i].count == 0:
                safe_cells = self.knowledge[i].cells.copy()
                for cell in safe_cells:
                    self.mark_safe(cell)
                del self.knowledge[i]

        for i in range(0, len(self.knowledge)):
            print(self.knowledge[i].cells)

        
        '''
        common_cells = set()
        common_subset = set()
        for i in range(0, len(self.knowledge)):
            for j in range(1 + i, len(self.knowledge)):
                for k in self.knowledge[i].cells:
                    for l in self.knowledge[j].cells:
                        if k == l:
                            common_subset.add(k)
                print(common_subset)
                print("i: ", self.knowledge[i].cells)
                print("diff: ", self.knowledge[i].cells.difference(common_subset)) 
                print("j: ",self.knowledge[j].cells)
                print("diff: ", self.knowledge[j].cells.difference(common_subset))
                print()  
        '''
        
        '''
        for i in range(len(self.knowledge)):
            print("i = ",i)
            print(self.knowledge[i])
            print()
        '''

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        raise NotImplementedError

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        raise NotImplementedError
    
    def get_neighbors(self, cell):
        neighbors = set()
        # check nw
        if cell[0] - 1 >= 0 and cell[1] - 1 >= 0:
            neighbors.add((cell[0] - 1, cell[1] - 1))

        # check n
        if cell[0] - 1 >= 0:
            neighbors.add((cell[0] - 1, cell[1]))

        # check ne
        if cell[0] - 1 >= 0 and cell[1] + 1 <= 7:
            neighbors.add((cell[0] - 1, cell[1] + 1))

        # check e
        if cell[1] + 1 <= 7:
            neighbors.add((cell[0], cell[1] + 1))

        # check se
        if cell[0] + 1 <= 7 and cell[1] + 1 <= 7:
            neighbors.add((cell[0] + 1, cell[1] + 1))

        # check s
        if cell[0] + 1 <= 7:
            neighbors.add((cell[0] + 1, cell[1]))

        # check sw
        if cell[0] + 1 <= 7 and cell[1] - 1 >= 0:
            neighbors.add((cell[0] + 1, cell[1] - 1))

        # check w
        if cell[1] - 1 >= 0:
            neighbors.add((cell[0], cell[1] - 1))  

        return neighbors

    def remove_safe_from_knowledge(self, safe):
        for i in range(0, len(self.knowledge)):
            for cell in self.knowledge[i].cells:
                if safe == cell:
                    return [i, safe]
        return None

    def remove_safe_cells_recursive(self):
        for c in self.safes:
            knowledge_index = self.remove_safe_from_knowledge(c)
            if knowledge_index != None:
                #print(c)
                #print("before", self.knowledge[knowledge_index[0]].cells)
                self.knowledge[knowledge_index[0]].cells.remove(c)
                #print("after", self.knowledge[knowledge_index[0]].cells)
                self.remove_safe_cells_recursive()
            else:
                return None
