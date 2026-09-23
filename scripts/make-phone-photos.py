"""Make the two photos the phone mockups use, from one studio portrait.

Run from website/:  python3 scripts/make-phone-photos.py
Writes public/img/scan-face.webp, and ../app/src/androidTest/assets/website/enrol-preview.webp,
which is the camera image the app render uses (scripts/capture-app-screens.sh). Needs cwebp.

scan-face      the background scan: teal-graded, on the scan screen's dark field.
enrol-preview  the enrolment camera preview: natural colour, mirrored like the
               app's front-camera preview, on a dim room-like backdrop.

The cut-out is a trimap matte, not a hard mask. Deep inside the subject alpha is 1,
far outside it is 0, and in a thin band along the edge alpha is solved per pixel by
projecting its colour onto the line between the local background and the local
subject colour. The background white is then subtracted back out of those edge
pixels (colour decontamination), which is what removes the light line around hair.
"""
import subprocess

import numpy as np
from PIL import Image
from scipy import ndimage

SRC = '../docs/image.png'
OUT = 'scan-face.png'
W, H = 600, 1300          # the scan screen's aspect ratio (284 x 613 at design size)

img = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float32) / 255.0
lum = img.mean(2)
chroma = img.max(2) - img.min(2)

# ── 1. Trimap ──────────────────────────────────────────────────────────
# Background: bright, neutral, and connected to the border (keeps the collar).
bgish = (lum > 0.86) & (chroma < 0.10)
lab, _ = ndimage.label(bgish)
edge_labels = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
bg = ndimage.binary_opening(np.isin(lab, edge_labels[edge_labels > 0]), iterations=2)
# Small enclosed white spots are backdrop showing between hair strands; the collar
# is enclosed too but thousands of pixels, so size tells them apart.
sizes = ndimage.sum(np.ones_like(lum), lab, index=np.arange(lab.max() + 1))
bg |= (sizes[lab] < 600) & (lab > 0) & ~np.isin(lab, edge_labels)
fg = ~bg
sure_fg = ndimage.binary_erosion(fg, iterations=14)   # wide enough to include backlit hair tips
sure_bg = ndimage.binary_erosion(bg, iterations=7)
unknown = ~(sure_fg | sure_bg)

# ── 2. Local colour estimates for the edge band ────────────────────────
def local_mean(mask, sigma):
    w = ndimage.gaussian_filter(mask.astype(np.float32), sigma)
    c = np.stack([ndimage.gaussian_filter(img[..., k] * mask, sigma) for k in range(3)], -1)
    return c / np.maximum(w, 1e-4)[..., None]

B = local_mean(sure_bg, 10)     # the backdrop as it actually is near each pixel
F = local_mean(sure_fg, 6)      # the hair / skin colour just inside the edge

# ── 3. Alpha by projection, only where it is unknown ───────────────────
d = F - B
a = ((img - B) * d).sum(-1) / np.maximum((d * d).sum(-1), 1e-4)
alpha = np.where(sure_fg, 1.0, np.where(sure_bg, 0.0, np.clip(a, 0, 1)))
# Tiny smoothing so the solved band has no speckle; then a slight gamma so
# near-transparent white wisps drop out instead of glowing.
alpha = ndimage.gaussian_filter(alpha, 0.7)
alpha = np.where(unknown, np.clip(alpha, 0, 1) ** 1.25, alpha)

# ── 4. Decontaminate: remove the white that bled into edge pixels ──────
safe = np.maximum(alpha, 0.08)[..., None]
recovered = np.clip(B + (img - B) / safe, 0, 1)
# Dividing by a small alpha amplifies noise into bright specks. An edge pixel is
# never much lighter than the subject just inside it, so cap it there.
recovered = np.minimum(recovered, F + 0.12)
# Where alpha is low the recovered colour is noisy; lean on the local subject colour.
w = np.clip((alpha - 0.08) / 0.5, 0, 1)[..., None]
colour = np.where(unknown[..., None], recovered * w + F * (1 - w), img)


def grade(rgb, keep, duo_mix, lift):
    """Blend toward a teal duotone. keep = saturation kept, duo_mix = duotone share."""
    gray = (rgb * [0.299, 0.587, 0.114]).sum(2, keepdims=True)
    desat = gray + (rgb - gray) * keep
    shadow, light = np.array([0.02, 0.06, 0.075]), np.array([0.70, 0.86, 0.90])
    duo = shadow + (light - shadow) * gray
    return np.clip((desat * (1 - duo_mix) + duo * duo_mix - 0.5) * 1.12 + 0.5 + lift, 0, 1)


def radial(w, h, cx, cy, rx, ry, c0, c1, reach):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - w * cx) / (w * rx)) ** 2 + ((yy - h * cy) / (h * ry)) ** 2)
    t = np.clip(d / reach, 0, 1)[..., None]
    return c0 + (c1 - c0) * t, xx, yy


def place(canvas_rgb, person_rgba, scale, face_x, face_y, fade_from, mirror=False, side_fade=0.0):
    """Composite the subject so the face centre (source 627, 560) lands at (face_x, face_y)."""
    h, w = canvas_rgb.shape[:2]
    canvas = Image.fromarray((canvas_rgb * 255).astype(np.uint8), 'RGB').convert('RGBA')
    pw = round(1254 * scale)
    p = person_rgba.resize((pw, pw), Image.LANCZOS)
    if mirror:
        p = p.transpose(Image.FLIP_LEFT_RIGHT)
    pa = np.asarray(p).astype(np.float32)
    fy = np.arange(pw, dtype=np.float32)
    pa[..., 3] *= (np.clip(1 - (fy - pw * fade_from) / (pw * 0.28), 0, 1) ** 1.4)[:, None]
    if side_fade:
        # The source photo is cropped at its own left and right edges (the hoodie
        # runs off them); fade the subject out before those edges so they never show.
        e = np.minimum(fy, pw - 1 - fy) / (pw * side_fade)
        pa[..., 3] *= (np.clip(e, 0, 1) ** 1.2)[None, :]
    canvas.alpha_composite(Image.fromarray(pa.astype(np.uint8), 'RGBA'),
                           (round(w * face_x - 627 * scale), round(h * face_y - 560 * scale)))
    return np.asarray(canvas.convert('RGB')).astype(np.float32)


def save(arr, name, dest='public/img'):
    png = f'{name}.png'
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(png)
    subprocess.run(['cwebp', '-quiet', '-q', '82', png, '-o', f'{dest}/{name}.webp'], check=True)
    pathlib.Path(png).unlink()
    print('wrote %s/%s.webp' % (dest, name))


import pathlib

# ── Scan screen: teal duotone on the scan screen's own field ───────────
W, H = 600, 1300          # the scan screen's aspect ratio (284 x 613 at design size)
person = Image.fromarray((np.dstack([grade(colour, 0.62, 0.42, -0.14), alpha]) * 255).astype(np.uint8), 'RGBA')
field, xx, yy = radial(W, H, 0.5, 0.25, 1.30, 0.90,
                       np.array([0x16, 0x26, 0x2b]) / 255, np.array([0x07, 0x0d, 0x0f]) / 255, 0.72)
out = place(field, person, 0.52, 0.5, 0.44, 0.70)
v = np.clip(1 - (np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.44) / (H * 0.62)) ** 2) - 0.55) * 1.3, 0.55, 1)[..., None]
save(out * v, 'scan-face')

# ── Enrolment preview: what the front camera actually shows ────────────
# The preview box is 262 x 190 at design size; make it at 3x.
W, H = 786, 570
person = Image.fromarray((np.dstack([grade(colour, 0.92, 0.12, -0.04), alpha]) * 255).astype(np.uint8), 'RGBA')
# A dim room: cool grey wall, a soft warm lamp glow at top left, darker floor side.
room, xx, yy = radial(W, H, 0.5, 0.35, 1.1, 1.1,
                      np.array([0.20, 0.23, 0.24]), np.array([0.07, 0.08, 0.09]), 0.95)
lamp = np.exp(-(((xx - W * 0.16) / (W * 0.30)) ** 2 + ((yy - H * 0.10) / (H * 0.42)) ** 2))[..., None]
room = np.clip(room + lamp * np.array([0.16, 0.12, 0.07]), 0, 1)
out = place(room, person, 0.38, 0.5, 0.47, 0.60, mirror=True, side_fade=0.22)
save(out, 'enrol-preview', '../app/src/androidTest/assets/website')
