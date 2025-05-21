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
    cw, ch = sw//cols, sh//rows

    frames = []
    centers_x = []
    baselines = []

    # extract frames
    for r in range(rows):
        for c in range(cols):
            frame = sheet.crop((c * cw, r * ch, (c + 1) * cw, (r + 1) * ch))
            arr = np.array(frame)
            bg = arr[[0, 0, -1, -1], [0, -1, 0, -1], :3].astype(float).mean(0)
            diff = np.linalg.norm(arr[:,:,:3]-bg, axis=2)
            mask = diff > thresh
            ys, xs = np.nonzero(mask)
            cx = xs.mean() if xs.size else cw / 2
            baseline = ys.max() if ys.size else ch - 1
            frames.append(frame)
            centers_x.append(cx)
            baselines.append(baseline)

    aligned_frames = []
    idx = 0
    for r in range(rows):
        row_centers = centers_x[idx:idx+cols]
        row_baselines = baselines[idx:idx+cols]
        target_baseline = np.max(row_baselines)
        for j in range(cols):
            frame = frames[idx + j]
            cx = row_centers[j]
            baseline = row_baselines[j]
            dx = int(round(cw / 2 - cx))
            dy = int(round(target_baseline - baseline))
            canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            canvas.paste(frame, (dx, dy), frame)
            aligned_frames.append(canvas)
        idx += cols

    out_sheet = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    idx = 0
    for r in range(rows):
        for c in range(cols):
            out_sheet.paste(aligned_frames[idx], (c * cw, r * ch), aligned_frames[idx])
            idx +=1
    return out_sheet


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
