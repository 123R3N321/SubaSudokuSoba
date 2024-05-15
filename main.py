
'''
Need to get used to attrgetter as this is faster than lambda expression
(only used in algorithmx anyways)
'''

'''
Areas of improvemet:
    separate compilation
    use numpy for parallel computation to max runtime speed
'''

from operator import attrgetter


def gamePrint(arr):
    for i in range(9):
        for j in range(9):
            if arr[i][j] == 0:
                print("_", end=" ")
            else:
                print(arr[i][j], end=" ")
        print()

class Solver:
    def checkvalidpuzzle(self, arr):
        boxCheckPoints = [[0, 0], [0, 3], [0, 6],
                          [3, 0], [3, 3], [3, 6],
                          [6, 0], [6, 3], [6, 6]
                          ]

        indHashMap = [0 for _ in range(9)]
        # make sure no repetition in each row
        for row in range(9):
            for col in range(9):
                if arr[row][col] == 0:  # we allow 0 to pass. This also implies additional constraint in solver
                    continue
                if indHashMap[arr[row][col]]>0:
                    return False
                indHashMap[arr[row][col]] += 1

        indHashMap = [0 for _ in range(9)]
        # Checking column validity of every column
        for col in range(9):    #flip row-col iteration order
            for row in range(9):
                if arr[row][col] == 0:
                    continue
                if indHashMap[arr[row][col]]>0:
                    return False
                indHashMap[arr[row][col]] += 1

        indHashMap = [0 for _ in range(9)]
        # Checking box validity
        for rowCheckPoint, colCheckPoint in boxCheckPoints:
            for row in range(3):
                for col in range(3):
                    if arr[rowCheckPoint+row][colCheckPoint+col] == 0:
                        continue
                    if indHashMap[arr[rowCheckPoint+row][colCheckPoint+col]]>0:
                        return False
                    indHashMap[(arr[rowCheckPoint+row][colCheckPoint+col])]+=1
        indHashMap = [0 for _ in range(9)]
        # check backward diagonal
        start = 0
        while start < 9:
            if arr[start][start] == 0:
                continue
            if indHashMap[arr[start][start]]>0:
                return False
            indHashMap[arr[start][start]] += 1
            start += 1

        indHashMap = [0 for _ in range(9)]
        # check forward diagonal
        start = 0
        while start < 9:
            if arr[8-start][start] == 0:
                continue
            if indHashMap[arr[8-start][start]] > 0:
                return False
            indHashMap[arr[8-start][start]] += 1
            start += 1

        return True




    @staticmethod
    def solve_sudoku(arr):
        """
        Create a binary matrix to convert to an exact cover problem.

        Choices: 729 (state space including illegal)
        Each cell can have any value from 1 to 9. 9*9*9

        Constraints: 81 * 6 = 486
        1. Each row must have all the values from 1 to 9, total: 81
        2. Each column must have all the values from 1 to 9, total: 81
        3. Each block must have all the values from 1 to 9, total: 81
        4. Each cell must be filled, total: 81
        5. Each diagonal \ and / must have all the values from 1 to 9, total: 81

        Choices are ordered by row --> col --> value --> diagonal
        the order does not matter in success cases, but
        diagonal --> col or row --> value gives faster failure
        due to degree heuristic!
        """
        # Represent the binary matrix as sparse matrix (has < 729 * 6 ones in a matrix of 729 * 486
        positions = []

        '''
        This method is the crux of the entire project!
        :params:
            ch - goes from 0 to 728 consec, represents each elem in matrix
            r - row ind
            c - col ind
            x - variable key, strictly speaking x_ij for each matrix position
        '''
        def add_position(ch, r, c, x):

            ########add double diagonal constraint###########
            forwardDiagMap = [[0 for _ in range(9)] for _ in range(9)]  # / shaped
            backwardDiagMap = [[0 for _ in range(9)] for _ in range(9)] # \ shaped

            accum = 0
            for colIndex in range(9):
                for rowIndex in range(9):
                    if 8 == colIndex + rowIndex:    # / diag has ind sum of 8
                        backwardDiagMap[rowIndex][colIndex] = 72
                    else:
                        backwardDiagMap[colIndex][rowIndex] = accum
                        accum += 1

            accum = 0
            for colIndex in range(9):
                for rowIndex in range(9):
                    if colIndex == rowIndex:    # \ has square shaped ind
                        forwardDiagMap[rowIndex][colIndex] = 72
                    else:
                        forwardDiagMap[colIndex][rowIndex] = accum
                        accum += 1


            positions.append([ch, [

                # on each row, x must be diff numbers
                # but if we on diff row, x can remain the same
                9 * r + x,  # Row constraint

                #add 81 as the first 81 constraints are on each row, already used the IDs
                #same concept, within each column, x must be diff
                #but once we move onto diff colum, x can repeat
                81 + 9 * c + x,  # Col constraint

                #now this is our biggest hope in devising a diag constraint
                # this says, if r or c differ more than 3, x can repeat
                # but if r and c both do not differ more than 3,
                # x must be unique, which essentially is saying
                # x within each 3by3 box is unique
                162 + 9 * ((r // 3) * 3 + (c // 3)) + x,  # Block constraint

                #lastly, we have a cell cnstraint
                # this says each r and c position must
                # be filled with non-zero,
                # because our other constraint check
                # conditions allow 0 to pass.
                243 + 9 * r + c,  # Cell constraint

                # and we can add new constraint here,
                # which in human terms dictates that:
                # if r==c, x must be different
                # in other positions, x can repeat
                # this in theory should add 81 constraints

                #I am certain we have +x, we start with 324,
                #but the rest... See matrixTest.py for mathematical details
                #and, the overall sum must be 81 in each diagonal constraint!
                324 + (forwardDiagMap[r][c] if r != c else 72+x),  # Cell constraint
                405 + (backwardDiagMap[r][c] if 8 != r + c else 72+x)
            ]])

        choice_row = 0
        for i in range(9):  # Row
            for j in range(9):  # Column
                if arr[i][j] == 0:
                    for k in range(9):  # Value
                        add_position(choice_row, i, j, k)
                        choice_row += 1
                else:
                    k = arr[i][j] - 1
                    add_position(choice_row + k, i, j, k)
                    choice_row += 9

##################################the 2 lines below are testcode. internal use only##############
##################################print out the constraint IDs###################################
        # for eachRow in positions:
        #     print(eachRow)
#################################################################################################

        # as discussed above, total 6 constraints, each affects all 81 elems in output matrix
        xSolver = AlgorithmX(486, positions)
        if not xSolver.solve():
            return False
        rows = xSolver.solution
        if len(rows) != 81:
            return False
        for row in rows:
            i, row = divmod(row, 81)
            j, value = divmod(row, 9)
            arr[i][j] = value + 1  # value is 0-8
        return True


class AlgorithmXNode:
    def __init__(self, value=0):
        """
        Create a node with self links.
        :param value: Serves multiple purposes:
            - nothing for root node
            - the number of cells in column for all header nodes
            - the row id in all other nodes
        """
        self.value = value
        self.left = self.right = self.up = self.down = self.top = self

    def insert_h(self):
        """
        Insert this node in the row, using left and right links.
        """
        self.left.right = self.right.left = self

    def insert_v(self, update_top=True):
        """
        Insert this node in the column.
        :param update_top: If true, update the counter in the header.
        """
        self.up.down = self.down.up = self
        if update_top:
            self.top.value += 1

    def insert_above(self, node):
        """
        Insert this node above the given node, in the column, updating the top.
        """
        self.top = node.top
        self.up = node.up
        self.down = node
        self.insert_v()

    def insert_after(self, node):
        """
        Insert this node to the right the given node.
        """
        self.right = node.right
        self.left = node
        self.insert_h()

    def remove_h(self):
        """
        Remove this node from the row. Inverse of insert_h.
        """
        self.left.right = self.right
        self.right.left = self.left

    def remove_v(self, update_top=True):
        """
        Remove this node from the column. Inverse of insert_v.
        :param update_top: If true, update the counter in the header.
        """
        self.up.down = self.down
        self.down.up = self.up
        if update_top:
            self.top.value -= 1

    def cover(self):
        self.top.remove_h()
        for row in self.top.loop('down'):
            for node in row.loop('right'):
                node.remove_v()

    def uncover(self):
        for row in self.top.loop('up'):
            for node in row.loop('left'):
                node.insert_v()
        self.top.insert_h()

    def loop(self, direction):
        """
        Yield each node from self to self, following the direction, excluding self.
        :param direction: One of 'left', 'right', 'up', 'down'.
        :return: Nodes from self to self (both exclusive), one at a time.
        """
        if direction not in {'left', 'right', 'up', 'down'}:
            raise ValueError(f"Direction must be one of 'left', 'right', 'up', 'down', got {direction}")
        next_node = attrgetter(direction)
        node = next_node(self)
        while node != self:
            yield node
            node = next_node(node)


class AlgorithmX:
    """
    Use Algorithm X with dancing links to solve a constraint satisfaction problem
    represented in the form of Exact Cover.

    Refer to https://en.wikipedia.org/wiki/Dancing_Links and
    https://en.wikipedia.org/wiki/Algorithm_X for the algorithm.
    """

    def __init__(self, constraint_count, matrix):
        matrix.sort()
        headers = [AlgorithmXNode() for _ in range(constraint_count)]
        for row, cols in matrix:
            first = None  # first node in row
            for col in cols:
                node = AlgorithmXNode(row)
                # Insert in column
                node.insert_above(headers[col])
                # Insert in row
                if first is None:
                    first = node
                else:
                    node.insert_after(first)
        # Header row
        self.root = AlgorithmXNode()
        last = self.root
        for header in headers:
            header.insert_after(last)
            last = header
        self.solution = []

    def solve(self):
        if self.root.right == self.root:    #empty matrix
            # All constraints have been satisfied
            return True
        # Find column with least number of nodes
        header = min(self.root.loop('right'), key=attrgetter('value'))
        if header.value == 0:
            # No valid solution exists
            return False
        header.cover()
        for row in header.loop('down'):
            for node in row.loop('right'):
                node.cover()
            if self.solve():
                # Add row to solution
                self.solution.append(row.value)
                return True
            # Try a different value
            for node in row.loop('left'):
                node.uncover()
        header.uncover()
        # Backtrack
        return False

#checker for the sudoku puzzle to see if solution is correct
def sudokuChecker(arr):
    

    #horizontal check
    for i in range(len(Arr)):
        for j in Arr[i]:
            if Arr[i].count(j) == 2:
                print("Horizontal error at line", i+1)
                print("There is a duplicate of", j)
                return False
    
    #vertical check
    for col in range(9):
        lst = []
        for row in Arr:
            lst.append(row[col])
        for i in range(9):
            if lst.count(lst[i]) == 2:
                print("Vertical error at line", i+1)
                print("There is a duplicate of", lst[i])
                return False
        
    #box check
    boxes = []
    for i in range(0, 9,3):
        box = []
        lst = [Arr[thing] for thing in range(i,i+3)]
        for j in range(0, 9,  3):
            box = [lst[count][ind] for count in range(3) for ind in range(j,j+3)]
            boxes.append(box)
    for box in range(9):
        if sum(boxes[box]) != 45:
            print("Duplicate at box", box)
            return False
    
    #rightDiagonal check
    rightDiag = 0
    for i in range(9):
        rightDiag +=(Arr[i][i])
    if rightDiag != 45:
        print("Right Diagnoal has duplicates")
        return False
    
    #Left Diagonal check
    leftDiag = 0
    for i in range(8,-1,-1):
        leftDiag +=(Arr[i][i])
    if leftDiag != 45:
        print("Left Diagnoal has duplicates")
        return False

    print("Everything Good")
    return True

if __name__ == '__main__':
    #reading input file
    f = open("Input3.txt", "r")
    lst = f.read().splitlines()
    Arr = []
    
    #appending each line into the array 
    for line in lst:
        line = [int(j) for j in line if j != " "]
        Arr.append(line)

    f.close()
    print("before: ")
    gamePrint(Arr)
    print()
    print("after: ")
    Solver.solve_sudoku(Arr)
    gamePrint(Arr)
    sudokuChecker(Arr)
    thing = ""

    #converting the line into string and correct format for out[ut]
    for i in Arr:
        i = [str(j) for j in i]
        n = 1
        while(n < len(i)):
            i.insert(n, " ")
            n +=(2)
        thing += "".join(i)
        thing += "\n"
    print(thing)
    f = open("Output 3", "w")
    f.write(thing)
    f.close()
            
    

