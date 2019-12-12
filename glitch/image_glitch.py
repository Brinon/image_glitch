""" Image glitchig functions """

from typing import Optional, Tuple
import numpy as np

NumpyArray = np.ndarray  # for typing


def move_channel(arr: NumpyArray, channel: int, deltax: int, deltay: int) -> NumpyArray:
    """ move the given channel in the direction (deltax, deltay) """
    w, h, c = arr.shape
    if channel >= c:
        raise ValueError(f"image only have {c} channels")

    if deltax < 0 and deltay < 0:
        arr[: w + deltax, : h + deltay, channel] = arr[-deltax:, -deltay:, channel]
    elif deltax > 0 and deltay > 0:
        arr[deltax:, deltay:, channel] = arr[:-deltax, :-deltay, channel]
    elif deltax > 0 and deltay < 0:
        arr[deltax:, : h + deltay, channel] = arr[:-deltax, -deltay:, channel]
    elif deltax < 0 and deltay > 0:
        arr[: w + deltax, deltay:, channel] = arr[-deltax:, :-deltay, channel]
    else:
        arr[..., channel] = arr[..., channel]
    return arr


def move_channels_random(
    arr: NumpyArray, min_delta: int = -50, max_delta: int = 50
) -> NumpyArray:
    """ move each channel a random amount between -val and val"""
    res = arr.copy()
    for channel in range(arr.shape[-1]):
        deltax, deltay = np.random.randint(min_delta, max_delta, (2,))
        res = move_channel(res, channel, deltax, deltay)
    return res


def swap_block(
    origin_arr: NumpyArray,
    dst_arr: NumpyArray,
    origin_block_x: int,
    origin_block_y: int,
    dst_block_x: int,
    dst_block_y: int,
    block_width: int,
    block_height: int,
    channel: Optional[int] = None,
) -> NumpyArray:
    """ swap the contents of the blocks. If channel is None, swap all the channels """
    channel = channel or ...
    dst_arr[
        origin_block_x : origin_block_x + block_width,
        origin_block_y : origin_block_y + block_height,
        channel,
    ] = origin_arr[
        dst_block_x : dst_block_x + block_width,
        dst_block_y : dst_block_y + block_height,
        channel,
    ]

    dst_arr[
        dst_block_x : dst_block_x + block_width,
        dst_block_y : dst_block_y + block_height,
        channel,
    ] = origin_arr[
        origin_block_x : origin_block_x + block_width,
        origin_block_y : origin_block_y + block_height,
        channel,
    ]

    return dst_arr


def move_random_blocks(
    arr: NumpyArray,
    max_blocksize: Tuple[int, int] = (5, 5),
    num_blocks: int = 5,
    per_channel: bool = False,
) -> NumpyArray:
    """ swap `num_blocks` of size `blocksize` in arr """
    res = arr.copy()
    w, h, n_channels = arr.shape
    max_block_size_x, max_block_size_y = max_blocksize
    for _ in range(num_blocks):
        block_size_x = np.random.randint(1, max_block_size_x)
        block_size_y = np.random.randint(1, max_block_size_y)

        block_origin_x = np.random.randint(0, w - block_size_x)
        block_origin_y = np.random.randint(0, h - block_size_y)

        block_dest_x = np.random.randint(0, w - block_size_x)
        block_dest_y = np.random.randint(0, h - block_size_y)

        if per_channel:
            channel = np.random.randint(0, n_channels)
        else:
            channel = None

        res = swap_block(
            arr,
            res,
            block_origin_x,
            block_origin_y,
            block_dest_x,
            block_dest_y,
            block_size_x,
            block_size_y,
            channel,
        )
    return res


def flip_block(
    arr: NumpyArray, blocksize: Tuple[int, int], per_channel: bool
) -> NumpyArray:
    """ Flips vertically and horizontally the content of a random block of `blocksize` size.
  if `per_channel` a random block is flipped in each channel """
    res = arr.copy()
    w, h, n_channels = arr.shape
    block_size_x, block_size_y = blocksize

    block_x = np.random.randint(0, w - block_size_x)
    block_y = np.random.randint(0, h - block_size_y)

    if per_channel:
        # each channel have 50% prob of flipping
        for c in range(n_channels):
            if np.random.randint(0, 1):
                flipped_block = arr[
                    block_x : block_x + block_size_x,
                    block_y : block_y + block_size_y,
                    c,
                ]
                flipped_block = flipped_block[::-1, ::-1]
                res[
                    block_x : block_x + block_size_x,
                    block_y : block_y + block_size_y,
                    c,
                ] = flipped_block
    else:
        flipped_block = arr[
            block_x : block_x + block_size_x, block_y : block_y + block_size_y, ...
        ]
        flipped_block = flipped_block[::-1, ::-1]
        res[
            block_x : block_x + block_size_x, block_y : block_y + block_size_y
        ] = flipped_block
    return res


def salt_and_pepper(
    arr: NumpyArray, intensity: float = 0.6, noise_frac: float = 0.02
) -> NumpyArray:
    """ replaces random pixels with 255,255,255 or 0,0,0"""
    if not 0 <= intensity <= 1.0:
        raise ValueError("intensity must be between 0 and 10!")
    w, h, c = arr.shape

    if c == 3:
        white = 255, 255, 255
        black = 0, 0, 0
    elif c == 4:
        white = 255, 255, 255, 255
        black = 0, 0, 0, 255

    # 2 of eac noise_frac pix is noisy
    prob_noise = int(1 / noise_frac)
    noise_mask = np.random.randint(0, prob_noise, (w, h))
    noise_rgb = arr.copy()

    noise_rgb[np.where(noise_mask == 0)] = black
    noise_rgb[np.where(noise_mask == 1)] = white

    return (arr.copy() * intensity + noise_rgb * (1 - intensity)).astype(np.uint8)
