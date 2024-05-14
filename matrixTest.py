



'''
This is a test file for diagonal matrix constraint-satisfaction
'''

def printMatrix(matrix):
    for row in matrix:
        for elem in row:
            print(elem, end='\t')
        print()
def printMatrixAtInd(matrix, row, col):
    print("at mat position [",row," ",col,"] we have: ", matrix[row][col])

def backwardDiagonal(Arr):
    accum = 0
    for colIndex in range(9):
        for rowIndex in range(9):
            if colIndex == rowIndex:
                Arr[rowIndex][colIndex] = 72
            else:
                Arr[colIndex][rowIndex] = accum
                accum += 1

def forwardDiagonal(Arr):
    accum = 0
    for colIndex in range(9):
        for rowIndex in range(9):
            if 8 == colIndex + rowIndex:
                Arr[rowIndex][colIndex] = 72
            else:
                Arr[colIndex][rowIndex] = accum
                accum += 1

if "__main__" == __name__:

    Arr = [[0 for _ in range(9)] for _ in range(9)]

    # backDiagonal(Arr)
    forwardDiagonal(Arr)

    printMatrix(Arr)
    print("")
    printMatrixAtInd(Arr,0,2)