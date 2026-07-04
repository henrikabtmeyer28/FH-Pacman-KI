from P3.bfs import bfs_distanzen, begehbare_nachbarn
from game_core.config import powerpill_time_max  # = 10


def evaluate(pos, level, wertekarte, dot_positionen,
             geister, sackgassen, powerpill_timer=0, distanzen=None):
    """
    Bewertet eine Position mit allen Faktoren.

    Parameter:
        pos:              (x, y) — das zu bewertende Feld
        level:            Spielfeld (env.view)
        wertekarte:       Dict aus value_iteration()
        dot_positionen:   Set der aktuellen Dot-Positionen
        geister:          Liste aus env.ghostlist()
        sackgassen:       Set der Sackgassen-Felder
        powerpill_timer:  Verbleibende Züge der Powerpill-Wirkung
                          (0 = keine aktiv). Kommt von der Pacman-Entität
        distanzen:        Dict aus bfs_distanzen() — optional

    Returns:
        float: Score — je höher, desto besser
    """
    if distanzen is None:
        distanzen = bfs_distanzen(level, pos[0], pos[1])

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
        ghost_pos = ghost.get_position()       # (x, y) Tuple
        ghost_typ = ghost.getType()             # 'R', 'H' oder 'E'
        ghost_tot = ghost.get_is_dead()         # True/False
        respawn_zeit = ghost.get_respawn_time()  # int

        # Tote Geister sind keine Gefahr — aber Respawn beachten!
        if ghost_tot:
            # Geist respawnt bald an seiner Startposition
            if respawn_zeit <= 2:
                respawn_pos = ghost.get_respawn_pos()
                if respawn_pos in distanzen:
                    respawn_dist = distanzen[respawn_pos]
                    if respawn_dist <= 2:
                        score -= 200  # Respawn in der direkten nähe
            continue  # Rest überspringen, Geist ist tot

        # BFS-Distanz zum Geist
        if ghost_pos in distanzen:
            dist = distanzen[ghost_pos]
        else:
            dist = abs(pos[0] - ghost_pos[0]) + abs(pos[1] - ghost_pos[1])

        # ------ GEISTER SIND VERÄNGSTIGT ------
        if geister_sind_veraengstigt:
            # Können wir ihn noch rechtzeitig erreichen?
            if powerpill_timer > dist and dist > 0:
                score += 300 / (dist + 1)  # Je näher, desto besser
            # Timer fast abgelaufen aber Geist nah → Gefahr!
            elif powerpill_timer <= 2 and dist <= 2:
                score -= 300

        # ------ GEISTER SIND NORMAL ------
        else:
            if dist <= 1:
                score -= 10000
            elif dist <= 2:
                score -= 500
            elif dist <= 4:
                # Hunter verfolgt gezielt → gefährlicher
                faktor = 2.5 if ghost_typ == 'H' else 1.0
                score -= faktor * 80 / dist
            # Distanz > 4: Geist wird ignoriert

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
    score += 3 * anzahl_nachbarn

    return score


def _naechster_geist_dist(geister, distanzen):
    """Kürzeste BFS-Distanz zum nächsten lebenden Geist."""
    min_dist = float('inf')
    for ghost in geister:
        if ghost.get_is_dead():
            continue
        ghost_pos = ghost.get_position()
        if ghost_pos in distanzen:
            min_dist = min(min_dist, distanzen[ghost_pos])
    return min_dist