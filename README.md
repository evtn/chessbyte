
# chessbyte
Compact chess board format (.chss).    
The format is somewhat similar to FEN, but is more compact, because bytes (one quartet to denote a piece, two to skip up to 63 tiles) are used efficiently.    

## Direction

The board is encoded starting at the rank 1 and ending with rank 8.    
Within each rank, the contents of each square are described from file "a" through file "h".

## Chunks

Data packed in chunks of 4 bits (quartets).

- Empty tiles defined by "skips" - pairs of quartets in this format: *11__ ____*
- If there's no piece at the tile #64, a skip to that tile must be added
- Except for alignment chunk (explained below), last 3 chunks contain board properties:
    - one bit defines possibility of en passant (0 if not possible, 1 otherwise)
    - three bits defines possible en passant (0 to 7, corresponds to files a to h) for current side to move
    - one bit defines side to move (0 for white, 1 for black)
    - three bits for alignment, could be used later for any useful information
    - four bits for castling possibility: [kingside black], [queenside black], [kingside white], [queenside black]
- If needed for alignment, a "lonely" *1111* chunk is added at the end, just ignore it when decoding.
- Other chunks define pieces.

## Pieces Notation

The least significant bit [*___x*] defines color of a piece. 0 for white, 1 for black.    
Other bits define the type of a piece:    
0 [*000*] - pawn    
1 [*001*] - knight    
2 [*010*] - bishop    
3 [*011*] - rook    
4 [*100*] - queen    
5 [*101*] - king    

## Skip notation
If there are empty tiles between two pieces, a skip used.    
Skip is a pair of chunks (which is a byte) - the first chunk is 11__, the second is ____    

Skip defines a distance between pieces (in other words, how much tiles you should skip).    
*Note: as the first chunk starts with 11.., those bits are not used, which leaves 6 meaningful bits or maximum of 63 tiles to be skipped.*    

Example:

0001 11000010 0001 - two black pawns [*0001*] with two empty tiles [*000010*] between them

## Implementation
Reference implementation can be found under `chessbyte.py` file

### Input format
Input for python .chss encoder is a dictionary with these pairs:
- **(x, y)**: **piece**, where:
     - **x** is an integer from 0 to 7, corresponds to files a to h
     - **y** is an integer from 0 to 7, corresponds to ranks 1 to 8
     - **piece** is a string of two characters: w/b for side and p/n/b/r/q/k for piece
- "en_passant": **file**, if en passant is possible (if not, don't include this field)
- "side": "w"/"b"
- "castling": array of castling possibilites, containing each possible castling:
    - "wk": kingside castling of white king
    - "bk": kingside castling of black king
    - "wq": queenside castling of white king
    - "bq": queenside castling of black king

### methods
`chessbyte.decode(chss_bytes: bytes) -> dict`    
`chessbyte.encode(data: dict) -> bytes`    

## Examples
Examples can be found in `examples` folder of repo.

