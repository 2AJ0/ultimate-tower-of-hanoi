# Ultimate Tower of Hanoi - Python GUI

Welcome to the **Ultimate Tower of Hanoi**! This is a feature-rich, deeply polished implementation of the classic mathematical puzzle, built entirely in Python using the built-in `tkinter` library. 

This project evolved from a simple auto-solver into a full-fledged interactive game with drag-and-drop mechanics, a dynamic algorithmic solver, a high score system, and a robust theme engine.

## 🌟 Features

- **True Drag and Drop:** Seamlessly click, hold, and drag discs across the screen with a fluid visual update system.
- **Dynamic Auto-Solver:** An algorithmic state solver that can take over from *any* position. Stuck halfway? Hit "Auto Solve" and watch the computer gracefully finish the puzzle for you.
- **High Scores & Leaderboard:** Built-in local saving (`scores.json`) automatically tracks your best completion times and optimal move counts for every difficulty. Check your all-time bests in the Leaderboard window!
- **Hint Engine:** Unsure of your next move? Click "Hint" to briefly highlight the mathematically optimal disc and its destination peg.
- **Hardcore Mode:** For the true Hanoi masters. Enable this to draw every disc at the exact same width—forcing you to memorize their relative sizes by color!
- **Live Move History:** A scrolling transcript on the right side of the screen tracks your exact move sequence.
- **Timer & Undo:** Speedrun the puzzle against a live stopwatch, and use the Undo button to erase mistakes (removes time from the clock implicitly by logging the extra time taken).
- **Theme Engine:** Instantly swap the entire color palette of the game between **Dark**, **Light**, and glowing **Cyberpunk** themes!
- **Native macOS Audio & Particles:** Enjoy satisfying tactile sounds when moving discs, and a celebratory particle confetti simulation when you win!
- **Zero Dependencies:** Relies entirely on Python's standard library. No `pip install` required!

## 🚀 How to Run

1. Ensure you have Python 3.x installed on your system.
2. Clone this repository or download the `ultimate_hanoi.py` file.
3. Open your terminal or command prompt.
4. Navigate to the directory containing the file.
5. Run the following command:
   ```bash
   python ultimate_hanoi.py
   ```
   *(Note: Depending on your system, you may need to use `python3 ultimate_hanoi.py`)*

## 🎮 How to Play

- **Goal:** Move the entire stack of discs from the first peg to the last peg.
- **Rules:** 
  1. You can only move one disc at a time.
  2. You can only pick up the top disc from a stack.
  3. You **cannot** place a larger disc on top of a smaller disc!
- **Controls:** Change the number of discs in the top input box (1-15) and click **Reset** to change the difficulty.

## 📸 Screenshots

*(Add screenshots here showing off the different themes, the leaderboard, and the confetti!)*

## 📝 License

Feel free to use, modify, and distribute this code. It's a great demonstration of state management, recursive algorithms, and GUI design in Python!
