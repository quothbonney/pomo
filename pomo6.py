import curses
import time
import sys
from datetime import datetime, timedelta
import os
import platform
from ascii_art import ARTS

class ColorScheme:
    def __init__(self):
        curses.start_color()
        curses.use_default_colors()
        
        # Extended color palette
        curses.init_pair(1, curses.COLOR_GREEN, -1)     # Status: Work
        curses.init_pair(2, curses.COLOR_CYAN, -1)      # Status: Break
        curses.init_pair(3, curses.COLOR_YELLOW, -1)    # Warning
        curses.init_pair(4, curses.COLOR_RED, -1)       # Urgent
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)   # Headers
        curses.init_pair(6, curses.COLOR_BLUE, -1)      # Info
        curses.init_pair(7, curses.COLOR_WHITE, -1)     # Normal text
        curses.init_pair(8, 232, curses.COLOR_WHITE)    # Inverse (dark gray bg)
        
        self.attrs = {
            'work': curses.color_pair(1),
            'break': curses.color_pair(2),
            'warning': curses.color_pair(3),
            'urgent': curses.color_pair(4),
            'header': curses.color_pair(5),
            'info': curses.color_pair(6),
            'normal': curses.color_pair(7) | curses.A_BOLD,
            'inverse': curses.color_pair(8),
            'bold': curses.color_pair(1) | curses.A_BOLD,
            'title': curses.color_pair(5) | curses.A_BOLD,
            'blue': curses.color_pair(6),
            'green': curses.color_pair(1),
            'cyan': curses.color_pair(2),
            'red': curses.color_pair(4),
            'magenta': curses.color_pair(5),
            'yellow': curses.color_pair(3),
            'white': curses.color_pair(7),
        }

class PomodoroTimer:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.work_duration = 25 * 60
        self.break_duration = 5 * 60
        self.long_break_duration = 15 * 60
        self.current_session = 1
        self.total_sessions = 4
        self.is_break = False
        self.is_paused = False
        self.remaining_time = self.work_duration
        self.end_time = None
        self.colors = ColorScheme()
        self.current_art = "bunny"
        self.show_help = False
        self.total_work_time = 0
        self.total_break_time = 0
        self.session_start_time = datetime.now()
        self.completed_pomodoros = 0
        
        # Hide cursor
        curses.curs_set(0)
        self.stdscr.keypad(1)

    def format_time(self, seconds):
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def format_duration(self, seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes:02d}m"

    def get_status_color(self):
        if self.is_paused:
            return self.colors.attrs['warning']
        if self.is_break:
            return self.colors.attrs['break']
        elif self.remaining_time < 60:
            return self.colors.attrs['urgent']
        elif self.remaining_time < 5 * 60:
            return self.colors.attrs['warning']
        return self.colors.attrs['work']

    def cycle_art(self, direction=1):
        arts = list(ARTS.keys())
        current_idx = arts.index(self.current_art)
        self.current_art = arts[(current_idx + direction) % len(arts)]

    def draw_progress_bar(self, y, x, width, progress):
        filled = int(width * progress)
        empty = width - filled
        
        # Draw progress bar with box drawing characters
        bar = "█" * filled + "░" * empty
        self.stdscr.addstr(y, x, bar, self.colors.attrs['white'])

    def draw_box(self, y, x, height, width, title=""):
        # Draw top border with title
        self.stdscr.addstr(y, x, "╭" + "─" * (width-2) + "╮", self.colors.attrs['header'])
        if title:
            self.stdscr.addstr(y, x + 2, f" {title} ", self.colors.attrs['title'])
        
        # Draw sides
        for i in range(1, height-1):
            self.stdscr.addstr(y+i, x, "│", self.colors.attrs['header'])
            self.stdscr.addstr(y+i, x + width-1, "│", self.colors.attrs['header'])
        
        # Draw bottom border
        self.stdscr.addstr(y+height-1, x, "╰" + "─" * (width-2) + "╯", self.colors.attrs['header'])

    def draw_ascii_art(self, start_y, start_x):
        art, color_map = ARTS[self.current_art]
        art_lines = art.split('\n')[1:-1]  # Remove first and last empty lines
        
        # Draw the base ASCII art in white
        for i, line in enumerate(art_lines):
            self.stdscr.addstr(start_y + i, start_x, line, self.colors.attrs['white'])
        
        # Apply colors from the color map
        for y_offset, x_offset, length, color in color_map:
            self.stdscr.addstr(
                start_y + y_offset, 
                start_x + x_offset, 
                art_lines[y_offset][x_offset:x_offset+length],
                self.colors.attrs[color]
            )

    def draw(self):
        self.stdscr.clear()
        
        # Fixed dimensions
        box_width = 40
        box_height = 12
        art_width = 15
        
        # Calculate center positions
        total_width = box_width + art_width + 4
        start_x = (curses.COLS - total_width) // 2
        start_y = (curses.LINES - box_height) // 2

        # Draw ASCII art
        self.draw_ascii_art(start_y + 2, start_x)
        
        # Draw main info box
        info_x = start_x + art_width + 4
        self.draw_box(start_y, info_x, box_height, box_width, 
                     f"{os.getlogin()}@{platform.node()}")
        
        # Draw information inside box
        info = [
            ("Timer", f"{'Break' if self.is_break else 'Work'}"),
            ("Time Left", f"{self.format_time(self.remaining_time)}"),
            ("Session", f"{self.current_session}/4"),
            ("Status", f"{'PAUSED' if self.is_paused else 'RUNNING'}"),
            ("Completed", f"{self.completed_pomodoros}"),
            ("Work Time", f"{self.format_duration(self.total_work_time)}"),
            ("Break Time", f"{self.format_duration(self.total_break_time)}"),
            ("Progress", ".")
        ]

        for i, (label, value) in enumerate(info):
            y = start_y + i + 2
            # Draw label in bold green
            self.stdscr.addstr(y, info_x + 2, f"{label}:", self.colors.attrs['bold'])
            # Draw value in white
            if value:  # Skip for progress bar
                value_x = info_x + 14  # Fixed position for values
                self.stdscr.addstr(y, value_x, value, self.colors.attrs['white'])

        # Draw progress bar
        progress = 1 - (self.remaining_time / 
            (self.work_duration if not self.is_break else 
             self.long_break_duration if (self.current_session - 1) % 4 == 0 
             else self.break_duration))
        self.draw_progress_bar(start_y + 9, info_x + 2, box_width - 4, progress)
        
        # Draw controls at the bottom
        controls = [
            ("p", "pause/resume", 'work'),
            ("s", "skip", 'warning'),
            ("a", "art", 'info'),
            ("h", "help", 'normal'),
            ("q", "uit", 'urgent')
        ]
        
        # Draw bottom border
        bottom_y = start_y + box_height + 2
        self.stdscr.addstr(bottom_y, 0, "─" * curses.COLS, self.colors.attrs['header'])
        
        # Center controls
        total_control_width = sum(len(f"[{key}]{text} ") for key, text, _ in controls) - 1
        control_x = (curses.COLS - total_control_width) // 2
        
        for key, text, color in controls:
            self.stdscr.addstr(bottom_y + 1, control_x, "[", self.colors.attrs['header'])
            self.stdscr.addstr(key, self.colors.attrs[color])
            self.stdscr.addstr("]", self.colors.attrs['header'])
            self.stdscr.addstr(text, self.colors.attrs[color])
            if text != "uit":  # Don't add separator after last control
                self.stdscr.addstr(" ", self.colors.attrs['header'])
            control_x += len(f"[{key}]{text} ")
        
        self.stdscr.refresh()

    def run(self):
        if not self.end_time:
            self.end_time = datetime.now() + timedelta(seconds=self.remaining_time)
            self.session_start_time = datetime.now()
            
        while True:
            if not self.is_paused and self.end_time:
                self.remaining_time = max(0, int((self.end_time - datetime.now()).total_seconds()))
                
                if self.remaining_time <= 0:
                    session_duration = int((datetime.now() - self.session_start_time).total_seconds())
                    
                    if not self.is_break:
                        self.completed_pomodoros += 1
                        self.total_work_time += session_duration
                        self.current_session += 1
                        if self.current_session > self.total_sessions:
                            self.current_session = 1
                    else:
                        self.total_break_time += session_duration
                    
                    self.is_break = not self.is_break
                    if self.is_break:
                        if (self.current_session - 1) % 4 == 0:
                            self.remaining_time = self.long_break_duration
                        else:
                            self.remaining_time = self.break_duration
                    else:
                        self.remaining_time = self.work_duration
                    
                    self.end_time = datetime.now() + timedelta(seconds=self.remaining_time)
                    self.session_start_time = datetime.now()
            
            self.draw()
            
            self.stdscr.timeout(100)
            try:
                key = self.stdscr.getch()
                if key != -1:
                    if self.show_help:
                        self.show_help = False
                        continue
                        
                    if chr(key) == 'q':
                        break
                    elif chr(key) == 'p':
                        self.is_paused = not self.is_paused
                        if not self.is_paused:
                            self.end_time = datetime.now() + timedelta(seconds=self.remaining_time)
                    elif chr(key) == 's':
                        self.remaining_time = 0
                    elif chr(key) == 'a':
                        self.cycle_art(1)
                    elif chr(key) == 'A':
                        self.cycle_art(-1)
                    elif chr(key) == 'h':
                        self.show_help = True
            except (ValueError, KeyError):
                pass  # Ignore non-character keys

def main():
    try:
        # Initialize the screen
        stdscr = curses.initscr()
        
        # Check terminal size
        if curses.LINES < 24 or curses.COLS < 80:
            curses.endwin()
            print("Terminal window too small. Please resize to at least 80x24 characters.")
            sys.exit(1)
            
        timer = PomodoroTimer(stdscr)
        timer.run()
    except KeyboardInterrupt:
        pass  # Handle Ctrl+C gracefully
    finally:
        curses.endwin()

if __name__ == "__main__":
    main()
