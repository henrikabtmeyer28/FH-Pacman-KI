import importlib

import P_final.bfs_distanzen

importlib.reload(P_final.bfs_distanzen)

from P_final.bfs_distanzen import bfs_distanzen, begehbare_nachbarn
from game_core.config import powerpill_time_max  # = 10


def evaluate(pos, level, wertekarte, dot_positionen,
             geister, sackgassen, powerpill_timer=0, distanzen=None):
    """
    Bewertet eine Position mit allen Faktoren.
    pos ist durchgehend (y, x).
    """
    if distanzen is None:
        distanzen = bfs_distanzen(level, pos[0], pos[1])
        # pos[0] = y, pos[1] = x → passt zur neuen Signatur

    score = 0.0

    # ============================================
    # FEATURE 1: Strategischer Wert (Wertekarte)
    # ============================================
    score += wertekarte.get(pos, 0)

    # ============================================
    # FEATURE 2: Direkter Dot-Bonus
    # ============================================
    if pos in dot_positionen:
        score += 50

    # ============================================
    # FEATURE 3: Nächster Dot (Distanz)
    # ============================================
    dot_distanzen = []
    for dot in dot_positionen:
        if dot in distanzen:
            dot_distanzen.append(distanzen[dot])

    if dot_distanzen:
        score -= 5 * min(dot_distanzen)

    # ============================================
    # FEATURE 4: Geister (Gefahr vs. Jagd)
    # ============================================
    geister_sind_veraengstigt = powerpill_timer > 0

    for ghost in geister:
        gy, gx = ghost.get_position()
        ghost_pos = (gy, gx)                             # war: (gx, gy)
        ghost_typ = ghost.getType()
        ghost_tot = ghost.get_is_dead()
        respawn_zeit = ghost.get_respawn_time()

        if ghost_tot:
            if respawn_zeit <= 2:
                ry, rx = ghost.get_respawn_pos()
                respawn_pos = (ry, rx)                   # war: (rx, ry)
                if respawn_pos in distanzen:
                    respawn_dist = distanzen[respawn_pos]
                    if respawn_dist <= 2:
                        score -= 200
            continue

        # BFS-Distanz zum Geist
        if ghost_pos in distanzen:
            dist = distanzen[ghost_pos]
        else:
            dist = abs(pos[0] - ghost_pos[0]) + abs(pos[1] - ghost_pos[1])

        # ------ GEISTER SIND VERÄNGSTIGT ------
        if geister_sind_veraengstigt:
            if powerpill_timer > dist and dist > 0:
                score += 300 / (dist + 1)
            elif powerpill_timer <= 2 and dist <= 2:
                score -= 300

        # ------ GEISTER SIND NORMAL ------
        else:
            if dist <= 1:
                score -= 100000
            elif dist <= 2:
                score -= 1000
            elif dist <= 4:
                faktor = 2.5 if ghost_typ == 'H' else 1.0
                score -= faktor * 80 / dist

    # ============================================
    # FEATURE 5: Sackgassen-Strafe
    # ============================================
    if pos in sackgassen:
        naechster_geist = _naechster_geist_dist(geister, distanzen)
        if naechster_geist < 6:
            score -= 600
        elif naechster_geist < 10:
            score -= 100

    # ============================================
    # FEATURE 6: Bewegungsfreiheit
    # ============================================
    anzahl_nachbarn = len(begehbare_nachbarn(level, pos[0], pos[1]))
    # pos[0] = y, pos[1] = x → passt
    score += 3 * anzahl_nachbarn

    return score


def _naechster_geist_dist(geister, distanzen):
    """Kürzeste BFS-Distanz zum nächsten lebenden Geist."""
    min_dist = float('inf')
    for ghost in geister:
        if ghost.get_is_dead():
            continue
        ghost_pos = ghost.get_position()    # gibt (y, x) zurück → passt direkt
        if ghost_pos in distanzen:
            min_dist = min(min_dist, distanzen[ghost_pos])
    return min_dist