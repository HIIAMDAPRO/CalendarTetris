"""Simple demo showing Tetris gameplay"""
from tetris import Tetris

def RunDemo():
    """Run a non-interactive demo"""
    game = Tetris()
    
    print("=" * 60)
    print("TETRIS DEMO - Watch the pieces fall!")
    print("=" * 60)
    
    # Simulate some moves
    moves = ['d', 'd', 'w', 'd', 's', 's', 'a', 'a', 'w', 's']
    
    for i in range(20):
        game.Render()
        
        # Apply a move
        if i < len(moves):
            move = moves[i]
            print(f"\nApplying move: {move}")
            
            if move == 'a':
                game.TryMove(-1, 0)
            elif move == 'd':
                game.TryMove(1, 0)
            elif move == 's':
                game.TryMove(0, 1)
            elif move == 'w':
                game.TryRotate()
        
        # Game tick
        game.Tick()
        
        if game.gameOver:
            break
        
        print("\n" + "-" * 60)
        
        # Small delay for readability
        import time
        time.sleep(0.5)
    
    # Final state
    game.Render()
    print(f"\nDemo complete! Final score: {game.score}, Lines: {game.linesCleared}")

if __name__ == "__main__":
    RunDemo()

