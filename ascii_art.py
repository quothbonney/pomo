# ascii_art.py

# Each art piece is a tuple of (art, color_map)
# Color map is a list of (y_offset, x_offset, length, color_name) tuples
# Colors available: blue, green, cyan, red, magenta, yellow, white

ARTS = {
    "bunny": ("""
    .---.
   /.@.@.\\
  ( (*^*) )
   '-----'
    /   \\
   /     \\
""", [
    (1, 2, 5, "blue"),    # Eyes
    (2, 3, 3, "magenta"), # Nose
]),

    "coffee": ("""
    )  (
   (   ) )
    ) ( (
  ______)_
 |       |
 |/\\/\\/\\/|
 |/\\/\\/\\/|
 |_______|
  '-----'
""", [
    (4, 1, 7, "yellow"),   # Top of cup
    (5, 1, 7, "yellow"),   # Middle of cup
    (6, 1, 7, "yellow"),   # Bottom of cup
    (0, 4, 3, "cyan"),     # Steam
]),

    "cat": ("""
   /\\___/\\
  (  o o  )
  (  =^=  ) 
   (______)
     |  |
     |  |
    _|  |_
""", [
    (1, 3, 5, "green"),    # Eyes
    (2, 3, 5, "magenta"),  # Nose
]),

    "terminal": ("""
  +--------+
  |$_      |
  |        |
  | [====] |
  |        |
  +--------+
""", [
    (3, 3, 6, "green"),    # Progress bar
    (1, 2, 2, "cyan"),     # Prompt
]),

    "penguin": ("""
    .---.
   /     \\
   \\.@.@./
  (  (^)  )
   '-----'
   /     \\
  /       \\
""", [
    (2, 3, 5, "blue"),     # Eyes
    (3, 4, 3, "yellow"),   # Beak
]),
}
