import random
import time
import threading
class Tetromino:
    """Represents a tetris piece with its different rotations"""
    
    # All tetromino shapes and their rotations (each letter represents a different color)
    SHAPES = {
        'I': [
            [[1, 1, 1, 1]],
            [[1], [1], [1], [1]]
        ],
        'O': [
            [[1, 1], [1, 1]]
        ],
        'T': [
            [[0, 1, 0], [1, 1, 1]],
            [[1, 0], [1, 1], [1, 0]],
            [[1, 1, 1], [0, 1, 0]],
            [[0, 1], [1, 1], [0, 1]]
        ],
        'S': [
            [[0, 1, 1], [1, 1, 0]],
            [[1, 0], [1, 1], [0, 1]]
        ],
        'Z': [
            [[1, 1, 0], [0, 1, 1]],
            [[0, 1], [1, 1], [1, 0]]
        ],
        'J': [
            [[1, 0, 0], [1, 1, 1]],
            [[1, 1], [1, 0], [1, 0]],
            [[1, 1, 1], [0, 0, 1]],
            [[0, 1], [0, 1], [1, 1]]
        ],
        'L': [
            [[0, 0, 1], [1, 1, 1]],
            [[1, 0], [1, 0], [1, 1]],
            [[1, 1, 1], [1, 0, 0]],
            [[1, 1], [0, 1], [0, 1]]
        ]
    }
    
    # Color mapping for each piece type
    COLORS = {
        'I': 'C',  # Cyan
        'O': 'Y',  # Yellow
        'T': 'M',  # Magenta
        'S': 'G',  # Green
        'Z': 'R',  # Red
        'J': 'B',  # Blue
        'L': 'O'   # Orange
    }
    
    def __init__(self, piece_type):
        self.Type = piece_type
        self.rotationIndex = 0
        self.Shape = self.SHAPES[piece_type]
        self.Color = self.COLORS[piece_type]
    
    def GetCurrentShape(self):
        """Returns the current rotation of the piece"""
        return self.Shape[self.rotationIndex]
    
    def Rotate(self):
        """Rotates the piece to the next rotation"""
        self.rotationIndex = (self.rotationIndex + 1) % len(self.Shape)
    
    def GetWidth(self):
        """Returns the width of the current rotation"""
        return len(self.GetCurrentShape()[0])
    
    def GetHeight(self):
        """Returns the height of the current rotation"""
        return len(self.GetCurrentShape())


class Tetris:
    """Main Tetris game class"""
    
    def __init__(self, width=10, height=24):
        self.width = width
        self.height = height
        self.board = [['.' for _ in range(width)] for _ in range(height)]
        self.currentPiece = None
        self.pieceX = 0
        self.pieceY = 0
        self.score = 0
        self.linesCleared = 0
        self.gameOver = False
        self.gameRunning = False
        self.SpawnNewPiece()
    
    def SpawnNewPiece(self):
        """Spawns a new random tetromino at the top center"""
        pieces = list(Tetromino.SHAPES.keys())
        piece_type = random.choice(pieces)
        self.currentPiece = Tetromino(piece_type)
        
        # Center the piece horizontally at the top
        self.pieceX = self.width // 2 - self.currentPiece.GetWidth() // 2
        self.pieceY = 0
        
        # Check if the game is over (no room to spawn)
        if self.CheckCollision(self.pieceX, self.pieceY):
            self.gameOver = True
    
    def CheckCollision(self, x, y, piece=None):
        """Checks if the piece at position (x, y) collides with anything"""
        if piece is None:
            piece = self.currentPiece.GetCurrentShape()
        
        for row_idx, row in enumerate(piece):
            for col_idx, cell in enumerate(row):
                if cell:
                    board_y = y + row_idx
                    board_x = x + col_idx
                    
                    # Check boundaries
                    if board_x < 0 or board_x >= self.width or board_y >= self.height:
                        return True
                    
                    # Check if there's already a piece there (but allow negative y for spawning)
                    if board_y >= 0 and self.board[board_y][board_x] != '.':
                        return True
        
        return False
    
    def PlacePiece(self):
        """Places the current piece on the board"""
        piece = self.currentPiece.GetCurrentShape()
        for row_idx, row in enumerate(piece):
            for col_idx, cell in enumerate(row):
                if cell:
                    board_y = self.pieceY + row_idx
                    board_x = self.pieceX + col_idx
                    if board_y >= 0:
                        self.board[board_y][board_x] = self.currentPiece.Color
    
    def ClearLines(self):
        """Clears completed lines and updates score"""
        lines_cleared_this_frame = 0
        new_board = []
        
        for row in self.board:
            # If the row has no empty cells, it's a completed line
            if all(cell != '.' for cell in row):
                lines_cleared_this_frame += 1
            else:
                new_board.append(row)
        
        # Add empty rows at the top
        while len(new_board) < self.height:
            new_board.insert(0, ['.' for _ in range(self.width)])
        
        self.board = new_board
        self.linesCleared += lines_cleared_this_frame
        
        # Scoring: 100 points for 1 line, 300 for 2, 500 for 3, 800 for 4
        if lines_cleared_this_frame == 1:
            self.score += 100
        elif lines_cleared_this_frame == 2:
            self.score += 300
        elif lines_cleared_this_frame == 3:
            self.score += 500
        elif lines_cleared_this_frame == 4:
            self.score += 800
    
    def TryMove(self, dx, dy):
        """Attempts to move the current piece by (dx, dy)"""
        new_x = self.pieceX + dx
        new_y = self.pieceY + dy
        
        if not self.CheckCollision(new_x, new_y):
            self.pieceX = new_x
            self.pieceY = new_y
            return True
        return False
    
    def TryRotate(self):
        """Attempts to rotate the current piece"""
        self.currentPiece.Rotate()
        
        if self.CheckCollision(self.pieceX, self.pieceY):
            # If rotation causes collision, try wall kicks
            if self.TryMove(-1, 0):  # Try moving left
                return True
            elif self.TryMove(1, 0):  # Try moving right
                return True
            else:
                # Rotate back if wall kick failed
                self.currentPiece.Rotate()
                self.currentPiece.Rotate()
                self.currentPiece.Rotate()
                return False
        return True
    
    def Tick(self):
        """Main game tick - moves piece down"""
        if self.gameOver:
            return
        
        # Try to move down
        if not self.TryMove(0, 1):
            # If we can't move down, place the piece
            self.PlacePiece()
            self.ClearLines()
            
            # Spawn next piece
            self.SpawnNewPiece()


    def Render(self):

    
        """Renders the current game state"""
        # Create a copy of the board
        render_board = [row[:] for row in self.board]
        
        # Draw the current piece
        if self.currentPiece and not self.gameOver:
            piece = self.currentPiece.GetCurrentShape()
            for row_idx, row in enumerate(piece):
                for col_idx, cell in enumerate(row):
                    if cell:
                        board_y = self.pieceY + row_idx
                        board_x = self.pieceX + col_idx
                        if 0 <= board_y < self.height and 0 <= board_x < self.width:
                            render_board[board_y][board_x] = self.currentPiece.Color
        
        # Print the board
        print("\n" + "=" * 50)
        print(f"Score: {self.score} | Lines: {self.linesCleared}")
        print("=" * 50)
        
        for row in render_board:
            print(' '.join(row))
        
        if self.gameOver:
            print("\n" + "=" * 50)
            print("GAME OVER!")
            print("=" * 50)
    
    def tick_loop(self):
        """Runs the game tick every second, independent of input"""
        while self.gameRunning and not self.gameOver:
            time.sleep(1)  # tick every 1 second
            self.Tick()
            self.Render()


def main():
    """Main game loop"""
    import sys
    import os

    if os.name == 'nt':
        import msvcrt

        def GetChar():
            """Gets a single character from stdin without Enter (Windows)"""
            ch = msvcrt.getch()
            # Decode bytes to string if necessary (Python 3)
            if isinstance(ch, bytes):
                ch = ch.decode('utf-8', errors='ignore')
            return ch

    else:
        import termios
        import tty

        def GetChar():
            """Gets a single character from stdin without Enter (Unix)"""
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

    # Example usage:
    print("Press any key (q to quit):")
    while True:
        c = GetChar()
        print(f"You pressed: {c}")
        if c.lower() == 'q':
            break

    
    game = Tetris()
    
    print("=" * 50)
    print("TETRIS")
    print("=" * 50)
    print("\nControls:")
    print("  a/d - Move left/right")
    print("  s - Move down faster")
    print("  w - Rotate")
    print("  q - Quit")
    print("\nColors:")
    print("  C = Cyan (I-piece), Y = Yellow (O-piece)")
    print("  M = Magenta (T-piece), G = Green (S-piece)")
    print("  R = Red (Z-piece), B = Blue (J-piece)")
    print("  O = Orange (L-piece), . = Empty")
    print("\nPress Enter to start...")
    input()


    game.gameRunning = True
    tick_thread = threading.Thread(target= game.tick_loop, daemon=True)
    tick_thread.start()
    
    while not game.gameOver:
        print("\nNext move (a/d/s/w/q): ", end='', flush=True)
        move = GetChar().lower()
        print(move)  # Echo input

        if move == 'q':
            print("\nQuitting game...")
            break
        elif move == 'a':
            game.TryMove(-1, 0)
        elif move == 'd':
            game.TryMove(1, 0)
        elif move == 's':
            game.TryMove(0, 1)
        elif move == 'w':
            game.TryRotate()

        # Render after each input too
        game.Render()

    # Stop ticking thread
    game.gameRunning = False
    tick_thread.join(timeout=1)

    print("\nFinal game state:")
    game.Render()


if __name__ == "__main__":
    main()

