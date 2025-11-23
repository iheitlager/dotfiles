GREP_COLORS Environment Variable
The GREP_COLORS variable controls specific color settings:

```bash
# Default GREP_COLORS (if not set, grep uses these defaults)
export GREP_COLORS='ms=01;31:mc=01;31:sl=:cx=:fn=35:ln=32:bn=32:se=36'

# Color codes breakdown:
ms=01;31    # Matching text (bold red)
mc=01;31    # Matching text in context lines (bold red)
sl=         # Selected line (no color)
cx=         # Context line (no color)
fn=35       # Filename (magenta)
ln=32       # Line number (green)
bn=32       # Byte offset (green)
se=36       # Separator (cyan)
```

Color Code Reference
Text Attributes

```bash
00          # Normal (reset)
01          # Bold/bright
02          # Dim
04          # Underline
05          # Blink
07          # Reverse/inverse
08          # Hidden
```

Foreground Colors
```bash
30          # Black
31          # Red
32          # Green
33          # Yellow
34          # Blue
35          # Magenta
36          # Cyan
37          # White
```

Background Colors
```bash
40          # Black background
41          # Red background
42          # Green background
43          # Yellow background
44          # Blue background
45          # Magenta background
46          # Cyan background
47          # White background
```
