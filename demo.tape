Output demo.gif
Set FontSize 14
Set Width 1200
Set Height 700
Set Theme "Catppuccin Mocha"
Set Shell "bash"

# Install dependencies (hidden)
Hide
Type "pip install -e . --quiet 2>/dev/null"
Enter
Sleep 5s
Type "clear"
Enter
Sleep 500ms
Show

# Launch dashboard with test sessions
Type "factory-dashboard -d ./test_sessions"
Enter
Sleep 3s

# Overview tab - show heatmap and stats
Sleep 2s

# Switch to Groups tab
Type "2"
Sleep 2s

# Switch to Projects tab
Type "3"
Sleep 2s

# Switch to Sessions tab
Type "4"
Sleep 2s

# Navigate down through sessions
Down
Sleep 500ms
Down
Sleep 500ms
Down
Sleep 1s

# Toggle favorite
Type "f"
Sleep 1s

# Switch to Favorites tab
Type "5"
Sleep 2s

# Toggle dark mode
Type "d"
Sleep 2s

# Quit
Type "q"
Sleep 500ms
