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
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
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
        if len(self.cells) == self.count:
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.count -= 1
            self.cells.remove(cell)

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
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
        self.mines = list()
        self.safes = list()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.append(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.append(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        """
        self.moves_made.add(cell)  # 1 Marks the cell as a move that has been made
        self.mark_safe(cell)  # 2 Marks the cell as safe
        cells = list()
        known_mines = 0
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Ignore the cell itself
                if (i, j) == cell:
                    continue
                if 0 <= i and i < self.height and 0 <= j and j < self.width:
                    if (i, j) not in self.safes:
                        cells.append((i, j))  # Fill the empty set with the unrevealed cells
                    if (i, j) in self.mines:
                        known_mines += 1

        new_sentence = Sentence(cells, count - known_mines)
        self.knowledge.append(new_sentence)  # 3 Add a new sentence to the knowledge base
        removed_sentences = []
        safe_cells = set()
        mine_cells = set()
        for sentence in self.knowledge:  # 4 For loop that marks cells as safe or mines based on the AI's knowledge base
            for cell in sentence.known_safes():
                safe_cells.add(cell)
            for cell in sentence.known_mines():
                mine_cells.add(cell)
            if sentence.cells == set():
                removed_sentences.append(sentence)
        for safe_cell in safe_cells:
            self.mark_safe(safe_cell)
        for mine_cell in mine_cells:
            self.mark_mine(mine_cell)
        for sentence in removed_sentences:
            self.knowledge.remove(sentence)
        c = 0
        removed_sentences_2 = []
        added_sentences = []
        for i in range(0, len(self.knowledge) - 1):  # 5 For loop that adds new sentences to the knowledge based using subset inferences
            for j in range(i + 1, len(self.knowledge)):
                if self.knowledge[i] == self.knowledge[j]:
                    removed_sentences_2.append(self.knowledge[j])
                    continue
                if self.knowledge[i].cells & self.knowledge[j].cells == self.knowledge[j].cells:
                    added_sentences.append(Sentence(self.knowledge[i].cells - self.knowledge[j].cells,self.knowledge[i].count - self.knowledge[j].count))

                elif self.knowledge[j].cells & self.knowledge[i].cells == self.knowledge[i].cells:
                    added_sentences.append(Sentence(self.knowledge[j].cells - self.knowledge[i].cells,self.knowledge[j].count - self.knowledge[i].count))

        for sentence in removed_sentences_2:
            if sentence in self.knowledge:
                self.knowledge.remove(sentence)
        for sentence in added_sentences:
            if sentence not in self.knowledge:
                self.knowledge.append(sentence)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.
        """
        for move in self.safes:
            if move not in self.moves_made and move not in self.mines:
                return move
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        """
        for i in range(0, 500):
            move = (random.randrange(0, self.height), random.randrange(0, self.width))
            if move not in self.mines and move not in self.moves_made:
                return move
        return None

    def make_very_safe_move(self,minesweeper_obj):
        """
        Returns a safe cell that's not next to any mines
        Called only once, at the start of each run, to assure the AI doesn't select a mine
        """
        for i in range(0, 500):
            move = (random.randrange(0, self.height), random.randrange(0, self.width))
            if minesweeper_obj.board[move[0]][move[1]] == False and minesweeper_obj.nearby_mines(move) == 0:
                return move
        return None