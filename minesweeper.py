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
        while len(self.mines) != 8:
            i = random.randrange(height)
            j = random.randrange(width)
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
        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()
    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        return self.mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        return self.safes

    def mark_mine(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1
            self.mines.add(cell)

    def mark_safe(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)
            self.safes.add(cell)

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
        print("add_knowledge: ", cell)
        # 1 Mark the cell as a move that has been made
        self.moves_made.add(cell)
        # 2 Mark the cell as safe
        self.mark_safe(cell)
        # 3 Add a new sentence to the AI's knowledge base ...
        neighbors = self.get_neighbors(cell)
        new_sentence = Sentence(neighbors, count)
        self.knowledge.append(new_sentence)

        # 4 Mark any additional cells as safe or as mines ...

        # Remove subsets where possible
        subset_pairs = []
        for i in range(0, len(self.knowledge)):
            for j in range(1 + i, len(self.knowledge)):
                # test if self.knowledge[i] is a subset of self.knowledge[j]
                if self.test_for_subset(self.knowledge[i].cells, self.knowledge[j].cells):
                    subset_pairs.append((i, j))
        # remove duplicate subset_pairs values
        subset_pairs_no_duplicates = list(dict.fromkeys(subset_pairs))
        # 
        if len(subset_pairs_no_duplicates) > 0:
            for pair in subset_pairs_no_duplicates:
                self.diff_sentences(pair)

        # Mark safe cells that are in statements of count == 0
        # and delete the statement
        indexes = [] 
        for i in range(0, len(self.knowledge)):
            if self.knowledge[i].count == 0:
                indexes.append(i)
                safe_cells = self.knowledge[i].cells.copy()
                for cell in safe_cells:
                    self.mark_safe(cell)
        for i in reversed(indexes):   
            del self.knowledge[i]
        
        # Mark mines that are in statements of count == 1
        # and delete the statement
        indexes = [] 
        for i in range(0, len(self.knowledge)):
            if self.knowledge[i].count == 1 and len(self.knowledge[i].cells) == 1:
                indexes.append(i)
                mine_cell = self.knowledge[i].cells.copy()
                for cell in mine_cell:
                    print("mine found: ", self.knowledge[i], cell)
                    self.mark_mine(cell)
        for i in reversed(indexes):            
            del self.knowledge[i]

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        safes_copy = self.safes.copy()
        if not bool(safes_copy):
            return None
        for i in self.moves_made:
            safes_copy.remove(i)
        if not bool(safes_copy):
            return None
        return next(iter(safes_copy))

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        print("RANDOM MOVE")
        all_cells = set()
        safes_copy = self.safes.copy()
        for i in range(self.height):
            for j in range(self.width):
                all_cells.add((i, j))
        for i in self.moves_made:
            all_cells.remove(i)
        for i in self.mines:
            all_cells.remove(i)
        return next(iter(all_cells))
    
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

    def test_for_subset(self, a, b):
        isSubset = True
        for cell in a:
            if not cell in b:
                isSubset = False
        return isSubset

    def diff_sentences(self, index_pair):
        # subtract cells
        for cell in self.knowledge[index_pair[0]].cells:
            self.knowledge[index_pair[1]].cells.remove(cell)
        # subtract count
        count1 = self.knowledge[index_pair[1]].count
        count0 = self.knowledge[index_pair[0]].count
        self.knowledge[index_pair[1]].count = count1 - count0
        self.knowledge[index_pair[1]].count = self.knowledge[index_pair[1]].count
