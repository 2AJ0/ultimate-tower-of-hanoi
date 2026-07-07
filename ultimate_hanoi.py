import tkinter as tk
from tkinter import messagebox
import time
import json
import os
import platform
import random

# --- Themes Definition ---
THEMES = {
    "Dark": {
        "bg": "#1e1e2e",
        "fg": "#cdd6f4",
        "peg": "#6c7086",
        "btn_bg": "#313244",
        "btn_fg": "#cdd6f4",
        "discs": ["#f38ba8", "#fab387", "#f9e2af", "#a6e3a1", "#94e2d5", "#89dceb", "#74c7ec", "#89b4fa", "#b4befe", "#cba6f7"],
        "highlight": "#f9e2af",
        "list_bg": "#181825",
        "list_fg": "#a6adc8"
    },
    "Light": {
        "bg": "#eff1f5",
        "fg": "#4c4f69",
        "peg": "#9ca0b0",
        "btn_bg": "#ccd0da",
        "btn_fg": "#4c4f69",
        "discs": ["#d20f39", "#fe640b", "#df8e1d", "#40a02b", "#179299", "#04a5e5", "#209fb5", "#1e66f5", "#7287fd", "#8839ef"],
        "highlight": "#df8e1d",
        "list_bg": "#e6e9ef",
        "list_fg": "#5c5f77"
    },
    "Cyberpunk": {
        "bg": "#000000",
        "fg": "#00ffcc",
        "peg": "#ff00ff",
        "btn_bg": "#111111",
        "btn_fg": "#00ffcc",
        "discs": ["#ff0055", "#00ffff", "#ffff00", "#ff00ff", "#00ff00"],
        "highlight": "#ffffff",
        "list_bg": "#0a0a0a",
        "list_fg": "#00ffcc"
    }
}

class UltimateHanoi:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultimate Tower of Hanoi")
        self.root.geometry("1000x700") # Wider to accommodate history log
        
        # State
        self.num_discs = 5
        self.pegs = [[], [], []]
        self.history = []
        self.moves = 0
        self.min_moves = 0
        self.is_hardcore = tk.BooleanVar(value=False)
        
        # Timer
        self.start_time = None
        self.elapsed_time = 0
        self.timer_id = None
        self.is_won = False
        
        # Drag/Drop & Hint & Confetti
        self.drag_data = {"disc": None, "source_peg": None, "x": 0, "y": 0}
        self.auto_solve_id = None
        self.auto_moves = []
        self.hint_peg_source = None
        self.hint_peg_target = None
        self.hint_timer_id = None
        self.confetti_particles = []
        self.confetti_id = None
        
        # Theme & Scoring
        self.current_theme_name = "Dark"
        self.theme = THEMES[self.current_theme_name]
        self.scores_file = "scores.json"
        self.high_scores = self.load_scores()
        
        self.setup_ui()
        self.apply_theme()
        self.reset_game()

    def load_scores(self):
        if os.path.exists(self.scores_file):
            try:
                with open(self.scores_file, "r") as f:
                    return json.load(f)
            except:
                pass
        return {}
        
    def save_score(self, discs, moves, time_taken):
        d_str = str(discs)
        is_new_best = False
        if d_str not in self.high_scores:
            is_new_best = True
        else:
            old_time = self.high_scores[d_str]["time"]
            if time_taken < old_time:
                is_new_best = True
                
        if is_new_best:
            self.high_scores[d_str] = {"moves": moves, "time": time_taken}
            try:
                with open(self.scores_file, "w") as f:
                    json.dump(self.high_scores, f)
            except:
                pass
        return is_new_best

    def play_sound(self, sound_type):
        if platform.system() == "Darwin":
            sounds = {
                "pickup": "/System/Library/Sounds/Glass.aiff",
                "drop": "/System/Library/Sounds/Pop.aiff",
                "win": "/System/Library/Sounds/Hero.aiff"
            }
            if sound_type in sounds:
                os.system(f"afplay {sounds[sound_type]} &")

    def setup_ui(self):
        # Top Control Frame
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(pady=10)
        
        # Row 0: Primary Controls
        self.lbl_discs = tk.Label(self.control_frame, text="Discs:", font=("Helvetica", 14))
        self.lbl_discs.grid(row=0, column=0, padx=5)
        
        self.disc_var = tk.StringVar(value=str(self.num_discs))
        self.disc_entry = tk.Entry(self.control_frame, textvariable=self.disc_var, width=5, font=("Helvetica", 14), justify="center")
        self.disc_entry.grid(row=0, column=1, padx=5)
        
        self.reset_btn = tk.Button(self.control_frame, text="Reset", command=self.reset_game, font=("Helvetica", 12))
        self.reset_btn.grid(row=0, column=2, padx=5)
        
        self.undo_btn = tk.Button(self.control_frame, text="Undo", command=self.undo_move, font=("Helvetica", 12))
        self.undo_btn.grid(row=0, column=3, padx=5)
        
        self.hint_btn = tk.Button(self.control_frame, text="Hint", command=self.show_hint, font=("Helvetica", 12))
        self.hint_btn.grid(row=0, column=4, padx=5)
        
        self.auto_btn = tk.Button(self.control_frame, text="Auto Solve", command=self.toggle_auto_solve, font=("Helvetica", 12))
        self.auto_btn.grid(row=0, column=5, padx=5)
        
        # Row 1: Secondary Controls
        self.theme_btn = tk.Button(self.control_frame, text="Theme", command=self.cycle_theme, font=("Helvetica", 12))
        self.theme_btn.grid(row=1, column=1, columnspan=2, pady=5, sticky="ew")
        
        self.leaderboard_btn = tk.Button(self.control_frame, text="Leaderboard", command=self.show_leaderboard, font=("Helvetica", 12))
        self.leaderboard_btn.grid(row=1, column=3, columnspan=2, pady=5, sticky="ew")
        
        self.hardcore_chk = tk.Checkbutton(self.control_frame, text="Hardcore Mode", variable=self.is_hardcore, command=self.draw, font=("Helvetica", 12))
        self.hardcore_chk.grid(row=1, column=5, pady=5, sticky="w")
        
        # Info Frame
        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack(pady=5)
        
        self.moves_var = tk.StringVar(value="Moves: 0 / 0")
        self.lbl_moves = tk.Label(self.info_frame, textvariable=self.moves_var, font=("Helvetica", 14, "bold"))
        self.lbl_moves.pack(side=tk.LEFT, padx=15)
        
        self.timer_var = tk.StringVar(value="Time: 00:00")
        self.lbl_timer = tk.Label(self.info_frame, textvariable=self.timer_var, font=("Helvetica", 14, "bold"))
        self.lbl_timer.pack(side=tk.LEFT, padx=15)
        
        self.best_var = tk.StringVar(value="Best: --")
        self.lbl_best = tk.Label(self.info_frame, textvariable=self.best_var, font=("Helvetica", 14))
        self.lbl_best.pack(side=tk.LEFT, padx=15)
        
        # Main Area (Canvas + History)
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas
        self.canvas = tk.Canvas(self.main_frame, width=700, height=450, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind drag events
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_release)
        
        # History Log Frame
        self.history_frame = tk.Frame(self.main_frame, width=250)
        self.history_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        self.lbl_history = tk.Label(self.history_frame, text="Move History", font=("Helvetica", 12, "bold"))
        self.lbl_history.pack(anchor="w")
        
        self.history_listbox = tk.Listbox(self.history_frame, font=("Helvetica", 11), width=25, borderwidth=0, highlightthickness=0)
        self.history_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Status Label
        self.status_var = tk.StringVar(value="Drag and drop discs to play!")
        self.lbl_status = tk.Label(self.root, textvariable=self.status_var, font=("Helvetica", 14))
        self.lbl_status.pack(pady=5)

    def show_leaderboard(self):
        top = tk.Toplevel(self.root)
        top.title("Leaderboard")
        top.geometry("300x400")
        t = self.theme
        top.configure(bg=t["bg"])
        
        tk.Label(top, text="🏆 All-Time Bests 🏆", font=("Helvetica", 16, "bold"), bg=t["bg"], fg=t["highlight"]).pack(pady=15)
        
        if not self.high_scores:
            tk.Label(top, text="No scores yet! Beat the game to record one.", bg=t["bg"], fg=t["fg"], wraplength=250).pack(pady=20)
        else:
            # Sort by disc count
            sorted_discs = sorted(self.high_scores.keys(), key=lambda x: int(x))
            for d in sorted_discs:
                data = self.high_scores[d]
                m, s = divmod(data['time'], 60)
                text = f"{d} Discs: {m:02d}:{s:02d} ({data['moves']} moves)"
                tk.Label(top, text=text, font=("Helvetica", 14), bg=t["bg"], fg=t["fg"]).pack(pady=5)

    def cycle_theme(self):
        themes = list(THEMES.keys())
        idx = (themes.index(self.current_theme_name) + 1) % len(themes)
        self.current_theme_name = themes[idx]
        self.theme = THEMES[self.current_theme_name]
        self.apply_theme()
        
    def apply_theme(self):
        t = self.theme
        self.root.configure(bg=t["bg"])
        self.control_frame.configure(bg=t["bg"])
        self.info_frame.configure(bg=t["bg"])
        self.main_frame.configure(bg=t["bg"])
        self.history_frame.configure(bg=t["bg"])
        self.canvas.configure(bg=t["bg"])
        
        self.history_listbox.configure(bg=t["list_bg"], fg=t["list_fg"])
        self.hardcore_chk.configure(bg=t["bg"], fg=t["fg"], selectcolor=t["bg"], activebackground=t["bg"], activeforeground=t["fg"])
        
        labels = [self.lbl_discs, self.lbl_moves, self.lbl_timer, self.lbl_best, self.lbl_history, self.lbl_status]
        for lbl in labels:
            lbl.configure(bg=t["bg"], fg=t["fg"])
            
        self.lbl_timer.configure(fg=t["peg"])
            
        if platform.system() != "Darwin":
            buttons = [self.reset_btn, self.undo_btn, self.hint_btn, self.auto_btn, self.theme_btn, self.leaderboard_btn]
            for btn in buttons:
                btn.configure(bg=t["btn_bg"], fg=t["btn_fg"])
            self.disc_entry.configure(bg=t["btn_bg"], fg=t["btn_fg"])
            
        self.draw()

    def stop_confetti(self):
        if self.confetti_id:
            self.root.after_cancel(self.confetti_id)
            self.confetti_id = None
        self.confetti_particles = []

    def spawn_confetti(self):
        t = self.theme
        for _ in range(50):
            x = random.randint(0, int(self.canvas['width']))
            y = random.randint(-300, 0)
            color = random.choice(t["discs"])
            dx = random.uniform(-2, 2)
            dy = random.uniform(3, 8)
            self.confetti_particles.append({"x": x, "y": y, "dx": dx, "dy": dy, "color": color})
            
        self.animate_confetti()
            
    def animate_confetti(self):
        # We draw confetti over the existing discs, so we need to just update their positions
        self.draw() # redraws base canvas
        for p in self.confetti_particles:
            p['x'] += p['dx']
            p['y'] += p['dy']
            if p['y'] < int(self.canvas['height']):
                self.canvas.create_rectangle(p['x'], p['y'], p['x']+8, p['y']+8, fill=p['color'], outline="")
                
        # Keep animating if any particle is visible
        if any(p['y'] < int(self.canvas['height']) for p in self.confetti_particles):
            self.confetti_id = self.root.after(30, self.animate_confetti)

    def reset_game(self):
        self.stop_auto_solve()
        self.stop_timer()
        self.clear_hint()
        self.stop_confetti()
        
        try:
            self.num_discs = int(self.disc_var.get())
            if self.num_discs < 1 or self.num_discs > 15:
                messagebox.showerror("Error", "Please enter a number between 1 and 15")
                self.num_discs = 5
                self.disc_var.set("5")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer")
            self.num_discs = 5
            self.disc_var.set("5")
            
        self.pegs = [list(range(self.num_discs, 0, -1)), [], []]
        self.history = []
        self.moves = 0
        self.min_moves = (2 ** self.num_discs) - 1
        
        self.start_time = None
        self.elapsed_time = 0
        self.timer_var.set("Time: 00:00")
        self.is_won = False
        
        self.history_listbox.delete(0, tk.END)
        
        d_str = str(self.num_discs)
        if d_str in self.high_scores:
            best_t = self.high_scores[d_str]["time"]
            m, s = divmod(best_t, 60)
            self.best_var.set(f"Best: {m:02d}:{s:02d}")
        else:
            self.best_var.set("Best: --")
        
        self.update_labels()
        self.status_var.set("Drag and drop discs to play!")
        self.draw()

    def update_labels(self):
        self.moves_var.set(f"Moves: {self.moves} / {self.min_moves}")
        
    def add_history_log(self, source, target):
        self.history_listbox.insert(tk.END, f"Move {self.moves}: Peg {source+1} → Peg {target+1}")
        self.history_listbox.yview(tk.END)

    def start_timer(self):
        if self.start_time is None and not self.is_won:
            self.start_time = time.time()
            self.update_timer()

    def stop_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
            
    def update_timer(self):
        if self.start_time and not self.is_won:
            self.elapsed_time = int(time.time() - self.start_time)
            mins, secs = divmod(self.elapsed_time, 60)
            self.timer_var.set(f"Time: {mins:02d}:{secs:02d}")
            self.timer_id = self.root.after(1000, self.update_timer)

    def get_peg_from_x(self, x):
        if x < 233: return 0
        if x < 466: return 1
        return 2

    def on_drag_start(self, event):
        if self.is_won or self.auto_solve_id: return
        self.clear_hint()
        
        peg_idx = self.get_peg_from_x(event.x)
        if self.pegs[peg_idx]:
            self.drag_data["source_peg"] = peg_idx
            self.drag_data["disc"] = self.pegs[peg_idx].pop()
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            self.play_sound("pickup")
            self.start_timer()
            self.draw()

    def on_drag_motion(self, event):
        if self.drag_data["disc"] is not None:
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            self.draw()

    def on_drag_release(self, event):
        if self.drag_data["disc"] is not None:
            target_peg_idx = self.get_peg_from_x(event.x)
            disc = self.drag_data["disc"]
            source_peg_idx = self.drag_data["source_peg"]
            
            target_peg = self.pegs[target_peg_idx]
            
            if not target_peg or target_peg[-1] > disc:
                target_peg.append(disc)
                self.play_sound("drop")
                if target_peg_idx != source_peg_idx:
                    self.history.append((source_peg_idx, target_peg_idx))
                    self.moves += 1
                    self.update_labels()
                    self.add_history_log(source_peg_idx, target_peg_idx)
                    self.check_win()
            else:
                self.pegs[source_peg_idx].append(disc)
                self.status_var.set("Invalid move! Can't place large disc on small disc.")
                
            self.drag_data["disc"] = None
            self.drag_data["source_peg"] = None
            self.draw()

    def undo_move(self):
        if self.is_won or self.auto_solve_id or not self.history:
            return
        self.clear_hint()
        source, target = self.history.pop()
        disc = self.pegs[target].pop()
        self.pegs[source].append(disc)
        self.moves -= 1
        self.play_sound("pickup")
        self.update_labels()
        
        # Remove from history log
        self.history_listbox.delete(tk.END)
        self.status_var.set("Move undone.")
        self.draw()

    def check_win(self):
        if len(self.pegs[2]) == self.num_discs:
            self.is_won = True
            self.stop_timer()
            self.play_sound("win")
            self.spawn_confetti()
            
            if self.moves == self.min_moves:
                is_new_best = self.save_score(self.num_discs, self.moves, self.elapsed_time)
                if is_new_best:
                    self.status_var.set(f"🏆 NEW PERSONAL BEST! Won in {self.elapsed_time}s 🏆")
                else:
                    self.status_var.set("🎉 PERFECT WIN! 🎉")
            else:
                self.status_var.set(f"🎉 Won in {self.moves} moves! (Optimal is {self.min_moves}) 🎉")

    def generate_solution_from_state(self):
        pos = {}
        for peg_idx, peg in enumerate(self.pegs):
            for disc in peg:
                pos[disc] = peg_idx
                
        moves = []
        def solve_state(d, target):
            if d == 0: return
            if pos.get(d, -1) == target:
                solve_state(d - 1, target)
            else:
                current = pos[d]
                aux = 3 - current - target
                solve_state(d - 1, aux)
                moves.append((current, target))
                pos[d] = target
                solve_state(d - 1, target)
                
        solve_state(self.num_discs, 2)
        return moves

    def toggle_auto_solve(self):
        self.clear_hint()
        if self.auto_solve_id:
            self.stop_auto_solve()
        else:
            if self.is_won: return
            self.auto_btn.config(text="Stop Auto")
            self.auto_moves = self.generate_solution_from_state()
            self.start_timer()
            self.auto_solve_step()

    def stop_auto_solve(self):
        if self.auto_solve_id:
            self.root.after_cancel(self.auto_solve_id)
            self.auto_solve_id = None
            self.auto_btn.config(text="Auto Solve")

    def auto_solve_step(self):
        if not self.auto_moves:
            self.stop_auto_solve()
            return
            
        source, target = self.auto_moves.pop(0)
        disc = self.pegs[source].pop()
        self.pegs[target].append(disc)
        self.history.append((source, target))
        self.moves += 1
        self.add_history_log(source, target)
        self.play_sound("drop")
        self.update_labels()
        self.draw()
        self.check_win()
        
        if not self.is_won:
            self.auto_solve_id = self.root.after(300, self.auto_solve_step)

    def show_hint(self):
        if self.is_won or self.auto_solve_id: return
        moves = self.generate_solution_from_state()
        if moves:
            self.hint_peg_source, self.hint_peg_target = moves[0]
            self.draw()
            if self.hint_timer_id:
                self.root.after_cancel(self.hint_timer_id)
            self.hint_timer_id = self.root.after(1500, self.clear_hint)

    def clear_hint(self):
        if self.hint_peg_source is not None:
            self.hint_peg_source = None
            self.hint_peg_target = None
            self.draw()

    def get_disc_width(self, disc):
        max_disc_width = 140
        if self.is_hardcore.get():
            return max_disc_width # Hardcore: All discs look identical in size
        min_disc_width = 40
        return min_disc_width + (max_disc_width - min_disc_width) * (disc / max(1, self.num_discs))

    def draw(self):
        self.canvas.delete("all")
        t = self.theme
        
        peg_width = 12
        peg_height = 250
        peg_y = 350
        
        # Draw Pegs
        for i in range(3):
            x = 150 + i * 200
            p_color = t["highlight"] if i == self.hint_peg_target else t["peg"]
            self.canvas.create_rectangle(x - peg_width/2, peg_y - peg_height, x + peg_width/2, peg_y, fill=p_color, outline="")
            self.canvas.create_rectangle(x - 80, peg_y, x + 80, peg_y + 15, fill=t["peg"], outline="")
            
        disc_height = 20
        
        # Draw Discs on Pegs
        for peg_index, peg in enumerate(self.pegs):
            x = 150 + peg_index * 200
            for i, disc in enumerate(peg):
                width = self.get_disc_width(disc)
                y = peg_y - (i * disc_height) - disc_height
                color = t["discs"][disc % len(t["discs"])]
                
                outline_color = t["bg"]
                outline_width = 2
                
                if peg_index == self.hint_peg_source and i == len(peg) - 1:
                    outline_color = t["highlight"]
                    outline_width = 4
                
                self.canvas.create_oval(x - width/2, y, x + width/2, y + disc_height, fill=color, outline=outline_color, width=outline_width)
                
        # Draw dragged disc
        if self.drag_data["disc"] is not None:
            disc = self.drag_data["disc"]
            x = self.drag_data["x"]
            y = self.drag_data["y"]
            width = self.get_disc_width(disc)
            color = t["discs"][disc % len(t["discs"])]
            self.canvas.create_oval(x - width/2, y - disc_height/2, x + width/2, y + disc_height/2, fill=color, outline=t["highlight"], width=3)

if __name__ == "__main__":
    root = tk.Tk()
    app = UltimateHanoi(root)
    root.mainloop()
