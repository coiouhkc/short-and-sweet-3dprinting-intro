"""Generate a model-kit style card (frame + sprues) holding a slot-together brown bear.

Parts: one side-profile body plate + two leg plates (front, hind) that slide
into the body's slots crosswise. Print in brown filament, flat, no supports.
Usage: python brown_bear_kit_card.py  (requires: trimesh manifold3d numpy)
"""
from functools import reduce
from operator import add

import numpy as np
import trimesh
from manifold3d import CrossSection, JoinType, Manifold

SEG = 64                               # circle resolution
T = 3.0                                # part thickness (= slot partner thickness)
SLOT = T + 0.3                         # slot width incl. clearance
FRAME_W, FRAME_T = 4.0, 3.0            # frame bar width / thickness
SPRUE_W, SPRUE_T = 1.6, 1.6            # sprue cross-section
GATE_W, GATE_L = 0.8, 1.5              # thin snap-off point at each part
BAY_GAP = 7.0                          # space between parts and frame

FRONT_SLOT_X, HIND_SLOT_X = 36.0, 14.0  # where the leg plates cross the body


def circle(x, y, r):
    return CrossSection.circle(r, SEG).translate((x, y))


def rect(x0, y0, x1, y1):
    return CrossSection.square((x1 - x0, y1 - y0)).translate((x0, y0))


def fillet(cs, r):
    """Round concave corners (morphological closing)."""
    return cs.offset(r, JoinType.Round, circular_segments=SEG).offset(-r, JoinType.Round, circular_segments=SEG)


def body_plate():
    """Side view of a brown bear facing right; ground is y=0 (legs come from the leg plates)."""
    body = CrossSection.batch_hull([circle(12, 28, 11), circle(34, 32, 12), circle(24, 24, 10)])
    neck = CrossSection.batch_hull([circle(42, 32, 9), circle(52, 36, 7)])
    head = CrossSection.batch_hull([circle(52, 36, 8), circle(63, 31, 4.5)])
    ear, tail = circle(48.5, 44.5, 3.2), circle(1.5, 31, 2.5)
    bear = fillet(body + neck + head + ear + tail, 1.5)
    return bear - circle(55, 38, 1.1)  # eye


def extent_y(cs, x):
    b = (cs ^ rect(x - 0.05, -1e3, x + 0.05, 1e3)).bounds()
    return b[1], b[3]


def extent_x(cs, y):
    inter = cs ^ rect(-1e3, y - 0.05, 1e3, y + 0.05)
    return None if inter.is_empty() else (inter.bounds()[0], inter.bounds()[2])


def leg_plate(body, slot_x):
    """Front view of a leg pair; top arc matches the body height at slot_x."""
    bot, top = extent_y(body, slot_x)
    mid, r = (bot + top) / 2, (top - bot) / 2
    torso = circle(0, mid, r)
    spread, half_w = 0.6 * r, 4.0  # legs sit under the outer part of the torso
    legs = rect(-spread - half_w, 0, -spread + half_w, mid) + rect(spread - half_w, 0, spread + half_w, mid)
    plate = fillet(torso + legs, 2.0)
    return plate - rect(-SLOT / 2, mid, SLOT / 2, top + 1), mid  # slot from the top down to mid


def build():
    body = body_plate()
    front, front_mid = leg_plate(body, FRONT_SLOT_X)
    hind, hind_mid = leg_plate(body, HIND_SLOT_X)
    body = (body - rect(FRONT_SLOT_X - SLOT / 2, -1, FRONT_SLOT_X + SLOT / 2, front_mid)
                 - rect(HIND_SLOT_X - SLOT / 2, -1, HIND_SLOT_X + SLOT / 2, hind_mid))
    parts = [body, front, hind]

    # normalise each part to start at the origin, then lay them out left to right
    sizes = []
    for i, p in enumerate(parts):
        b = p.bounds()
        parts[i] = p.translate((-b[0], -b[1]))
        sizes.append((b[2] - b[0], b[3] - b[1]))
    card_h = max(h for _, h in sizes) + 2 * (BAY_GAP + FRAME_W)
    x = FRAME_W
    frame = [rect(0, 0, FRAME_W, card_h)]
    placed, sprues = [], []
    for p, (w, h) in zip(parts, sizes):
        x0, y0 = x + BAY_GAP, (card_h - h) / 2
        bay_l, bay_r = x, x + w + 2 * BAY_GAP
        p = p.translate((x0, y0))
        placed.append(p)
        # horizontal sprues at the part's vertical middle, vertical ones at 1/4 and 3/4 width
        ex = extent_x(p, y0 + h / 2)
        if ex:
            sprues += sprue(bay_l, ex[0], y0 + h / 2, horizontal=True)
            sprues += sprue(bay_r, ex[1], y0 + h / 2, horizontal=True)
        for fx in (0.25, 0.75):
            xs = x0 + w * fx
            lo, hi = extent_y(p, xs)
            sprues += sprue(FRAME_W, lo, xs, horizontal=False)
            sprues += sprue(card_h - FRAME_W, hi, xs, horizontal=False)
        x = bay_r
        frame.append(rect(x, 0, x + FRAME_W, card_h))
        x += FRAME_W
    frame += [rect(0, 0, x, FRAME_W), rect(0, card_h - FRAME_W, x, card_h)]

    solid = Manifold.extrude(reduce(add, frame), FRAME_T) + Manifold.extrude(reduce(add, placed), T)
    return reduce(add, sprues, solid)


def sprue(start, end, at, horizontal):
    """Sprue from a frame edge (start) to a part edge (end), thinning to a gate at the part."""
    eps = 0.3
    sgn = 1 if end > start else -1
    s, e = start - sgn * eps, end + sgn * eps
    g = end - sgn * GATE_L

    def bar(a, b, width, height):
        lo, hi = min(a, b), max(a, b)
        cs = rect(lo, at - width / 2, hi, at + width / 2) if horizontal else rect(at - width / 2, lo, at + width / 2, hi)
        return Manifold.extrude(cs, height)

    return [bar(s, g, SPRUE_W, SPRUE_T), bar(g, e, GATE_W, SPRUE_T * 0.6)]


if __name__ == "__main__":
    import os
    mesh = build().to_mesh()
    tm = trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3], faces=np.asarray(mesh.tri_verts))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brown_bear_kit_card.stl")
    tm.export(out)
    print(f"wrote {out}: {len(tm.faces)} faces, watertight={tm.is_watertight}, "
          f"bounds={tm.bounds.round(2).tolist()}")
