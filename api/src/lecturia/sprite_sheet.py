from pathlib import Path

import numpy as np
from PIL import Image


def align_sprite_sheet_with_baseline(
    in_image: Image.Image,
    grid: tuple[int, int] = (3, 3),
    thresh: int = 25,
) -> Image.Image:
    sheet = in_image.convert("RGBA")
    sw, sh = sheet.size
    cols, rows = grid
    cw, ch = sw // cols, sh // rows

    frames, cx_list, bl_list = [], [], []

    for r in range(rows):
        for c in range(cols):
            frame = sheet.crop((c*cw, r*ch, (c+1)*cw, (r+1)*ch))
            alpha = np.array(frame)[:, :, 3]
            mask  = alpha > 0
            ys, xs = np.nonzero(mask)
            cx = xs.mean() if xs.size else cw / 2
            baseline = ys.max() if ys.size else ch - 1
            frames.append(frame)
            cx_list.append(cx)
            bl_list.append(baseline)

    aligned = []
    idx = 0
    for r in range(rows):
        row_cx = cx_list[idx:idx+cols]
        row_bl = bl_list[idx:idx+cols]
        tgt_cx = np.mean(row_cx)
        tgt_bl = np.max(row_bl)

        for j in range(cols):
            frame   = frames[idx+j]
            dx      = int(round(cw/2 - row_cx[j]))
            dy      = int(round(tgt_bl - row_bl[j]))
            canvas  = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            canvas.paste(frame, (dx, dy), frame)
            aligned.append(canvas)
        idx += cols

    sheet_aligned = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    idx = 0
    for r in range(rows):
        for c in range(cols):
            sheet_aligned.paste(aligned[idx],
                                (c*cw, r*ch),
                                aligned[idx])
            idx += 1
    return sheet_aligned


def make_gif(image: Image.Image, out_path: str | Path) -> None:
    cols, rows = 3, 1
    cw, ch = image.width // cols, image.height // rows

    gif_frames = []
    duration_ms = 150

    for r in range(rows):
        for c in range(cols):
            box = (c * cw, r * ch, (c + 1) * cw, (r + 1) * ch)
            gif_frames.append(image.crop(box))

    gif_frames[0].save(
        out_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=duration_ms,
        loop=0,
        disposal=2,
    )
