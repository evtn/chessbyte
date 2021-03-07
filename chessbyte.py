debug = False

pieces = "pnbrqk"

def xy_to_i(xy: tuple) -> int:
    return xy[0] + 8 * xy[1]

def i_to_xy(i: int) -> tuple:
    return (i % 8, i // 8) 


def add_chunk(result: list, offset: int, chunk: int):
    if not offset:
        result[-1] |= chunk
    else:
        result.append(chunk << 4)


def encode(data: dict) -> bytes:
    result = []
    offset = 1
    last = None
    for (x, y) in sorted(filter(lambda key: isinstance(key, tuple), data), key=xy_to_i) + ([(7, 7)] * ((7, 7) not in data)):
        if last:
            distance = xy_to_i((x, y)) - xy_to_i(last) - 1
            if distance:
                skip = 0xC0 + distance
                # print("writing a skip with {distance} distance. Skipdata: {skip:08b}".format(distance=distance, skip=skip))
                if not offset:
                    add_chunk(
                        result,
                        offset,
                        skip >> 4
                    )
                    add_chunk(
                        result,
                        1 - offset,
                        skip & 0xF
                    )
                else:
                    result.append(skip)

        if (x, y) not in data:
            break

        piece = (data[x, y][0] == "b") | (pieces.index(data[x, y][1]) << 1)
        last = (x, y)

        # print("writing chunk {chunk:04b}: PIECE-{piece} at {coords}.".format(chunk=piece, piece=data[x, y], coords=(x, y)))
        
        add_chunk(
            result,
            offset,
            piece
        )

        offset = 1 - offset

    side = (data.get("side", "w") == "b")
    en_passant = "abcdefgh".index(data.get("en_passant", "a")) 
    en_passant_possible = "en_passant" in data

    add_chunk(
        result,
        offset,
        en_passant | (en_passant_possible << 3)
    )
    offset = 1 - offset 

    add_chunk(
        result,
        offset,
        (side << 3)
    )
    offset = 1 - offset 

    add_chunk(
        result,
        offset,
        sum([
            (1 << x) for x in map(
                lambda i: (["bk", "bq", "wk", "wq"][3 - i] in data.get("castling", ["bk", "bq", "wk", "wq"])) * i,
                range(4)
            )
        ])
    )
    offset = 1 - offset 

    if not offset:
        add_chunk(
            result,
            offset,
            0xF
        )

    return bytes(result)


def decode(chss_bytes: bytes) -> dict:
    data = list(chss_bytes)
    result = {}
    i = 0
    is_aligned = (data[-1] & 0xF == 0xF)
    skip_buf = 0
    mode = 0
    for j in range(len(data) * 2):
        if j % 2:
            chunk = data[j // 2] & 0xF
        else:
            chunk = data[j // 2] >> 4 

        if not mode:
            if chunk > 11 and not skip_buf:
                skip_buf = chunk 
                continue

            if skip_buf:
                skip = ((skip_buf << 4) | chunk) ^ 0xC0
                i += skip
                skip_buf = 0
                continue 

            (x, y) = i_to_xy(i) 
            side = "wb"[chunk % 2]
            piece = pieces[chunk >> 1]
            # print(f"Reading PIECE-{side}{piece} at {(x, y)}, j: {j}, i: {i}")
            result[x, y] = side + piece 

            if i == 63:
                mode += 1 

            i += 1

            continue
        
        if mode == 1:
            en_passant_possible = chunk >> 3
            result["en_passant"] = "abcdef"[chunk & 0x7]
            if not en_passant_possible:
                result.pop("en_passant")
        elif mode == 2:
            result["side"] = "wb"[chunk >> 3]
        elif mode == 3:
            castling = []
            possible = ["bk", "bq", "wk", "wq"]
            for i in range(4):
                if chunk & (1 << i):
                    castling.append(possible[3 - i]) 
            result["castling"] = castling
        else:
            break

        mode += 1
    return result








