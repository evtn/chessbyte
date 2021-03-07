# examples
Examples in form of binary .chss files

You can use it from python module like this:

```python
import chessbyte

with open("examples/default.chss", "rb") as file:
    board = chessbyte.decode(file.read())

```

Examples include:
- `default.chss`: Starting position, **19 bytes**
- `kings.chss`: The most lightweight example - two kings in the corners, **4 bytes** (int32: `2969436415`)
- `checkers.chss`: The heaviest example - the board filled with pawns checkerwise, **46 bytes**