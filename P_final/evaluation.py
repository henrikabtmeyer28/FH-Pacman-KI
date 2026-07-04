import importlib

import P_final.bfs_distanzen

importlib.reload(P_final.bfs_distanzen)

from P_final.bfs_distanzen import bfs_distanzen, begehbare_nachbarn
from game_core.config import powerpill_time_max  # = 10


def evaluate(pos, level, wertekarte, dot_positionen,
             geister, sackgassen, powerpill_timer=0,
             distanzen=None, geister_distanzen=None):
    """
    Bewertet eine Position mit allen Faktoren.

    Parameter:
        pos:               (y, x) — das zu bewertende Feld
        level:             Spielfeld (env.view)
        wertekarte:        Dict aus value_iteration()
        dot_positionen:    Set der aktuellen Dot-Positionen
        geister:           Liste aus env.ghost_list
        sackgassen:        Set der Sackgassen-Felder
        powerpill_timer:   Verbleibende Züge der Powerpill-Wirkung
        distanzen:         Dict aus bfs_distanzen() von Pacmans Position
        geister_distanzen: Dict {ghost_obj: bfs_dict} — BFS von jedem
                           lebenden Geist. Gibt die echte Labyrinth-Distanz
                           vom Geist zu jeder Position.

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

    nahe_geister = 0       # Zähler für Geister in Reichweite <= 5
    naechste_geist_dist = float('inf')

    for ghost in geister:
        gy, gx = ghost.get_position()
        ghost_pos = (gy, gx)
        ghost_typ = ghost.getType()
        ghost_tot = ghost.get_is_dead()
        respawn_zeit = ghost.get_respawn_time()

        # --- Tote Geister: nur Respawn-Gefahr ---
        if ghost_tot:
            if respawn_zeit <= 2:
                ry, rx = ghost.get_respawn_pos()
                respawn_pos = (ry, rx)
                if respawn_pos in distanzen:
                    respawn_dist = distanzen[respawn_pos]
                    if respawn_dist <= 2:
                        score -= 300
            continue

        # --- Distanz vom Geist zur Kandidatenposition ---
        # Priorität: BFS vom Geist (genau) > BFS von Pacman (Näherung) > Manhattan
        dist = _ghost_dist(ghost, pos, ghost_pos, geister_distanzen, distanzen)

        if dist < naechste_geist_dist:
            naechste_geist_dist = dist

        if dist <= 5:
            nahe_geister += 1

        # ------ GEISTER SIND VERÄNGSTIGT ------
        if geister_sind_veraengstigt:
            if powerpill_timer > dist + 1 and dist > 0:
                # Genug Zeit, Geist zu jagen
                score += 300 / (dist + 1)
            elif powerpill_timer <= 3 and dist <= 3:
                # Timer läuft bald ab, Geist nah -> Gefahr!
                score -= 500
        # ------ GEISTER SIND NORMAL ------
        else:
            if dist <= 1:
                score -= 100000       # Tödlich
            elif dist <= 2:
                score -= 3000
            elif dist <= 3:
                score -= 800
            elif dist <= 5:
                # Hunter ist gefährlicher (verfolgt aktiv)
                faktor = 3.0 if ghost_typ == 'H' else 1.0
                score -= faktor * 150 / dist
            elif dist <= 8:
                # Hunter aus mittlerer Distanz beachten
                faktor = 2.0 if ghost_typ == 'H' else 0.5
                score -= faktor * 60 / dist
            elif dist <= 12 and ghost_typ == 'H':
                # Hunter auch aus großer Distanz leicht beachten
                score -= 20 / dist

    # ============================================
    # FEATURE 5: Multi-Geist Zangen-Gefahr
    # ============================================
    if nahe_geister >= 2 and not geister_sind_veraengstigt:
        score -= 400 * nahe_geister

    # ============================================
    # FEATURE 6: Sackgassen-Strafe
    # ============================================
    if pos in sackgassen and not geister_sind_veraengstigt:
        if naechste_geist_dist < 6:
            score -= 1500
        elif naechste_geist_dist < 10:
            score -= 400
        elif naechste_geist_dist < 15:
            score -= 100

    # ============================================
    # FEATURE 7: Bewegungsfreiheit & Fluchtweg-Analyse
    # ============================================
    nachbarn = begehbare_nachbarn(level, pos[0], pos[1])
    anzahl_nachbarn = len(nachbarn)
    score += 3 * anzahl_nachbarn

    # Fluchtweg-Analyse: Wie viele Ausgänge sind geisterfrei?
    if not geister_sind_veraengstigt and naechste_geist_dist <= 6:
        sichere_ausgaenge = 0
        for nachbar in nachbarn:
            ausgang_sicher = True
            for ghost in geister:
                if ghost.get_is_dead():
                    continue
                ghost_dist_zum_ausgang = _ghost_dist_to(
                    ghost, nachbar, geister_distanzen
                )
                if ghost_dist_zum_ausgang is not None and ghost_dist_zum_ausgang <= 2:
                    ausgang_sicher = False
                    break
            if ausgang_sicher:
                sichere_ausgaenge += 1

        if sichere_ausgaenge == 0:
            score -= 2000      # Komplett eingekreist
        elif sichere_ausgaenge == 1 and naechste_geist_dist <= 3:
            score -= 500       # Nur ein Ausweg und Geist sehr nah

    # ============================================
    # FEATURE 8: Korridor-Gefahr
    # ============================================
    if anzahl_nachbarn <= 2 and not geister_sind_veraengstigt:
        if naechste_geist_dist <= 4:
            score -= 300
        elif naechste_geist_dist <= 6:
            score -= 80

    return score


def _ghost_dist(ghost, pos, ghost_pos, geister_distanzen, distanzen):
    """
    Beste verfügbare Distanz vom Geist zur Kandidatenposition.
    1. BFS vom Geist (geister_distanzen) — am genauesten
    2. BFS von Pacman (distanzen) — Näherung
    3. Manhattan-Distanz — Fallback
    """
    if geister_distanzen is not None and ghost in geister_distanzen:
        ghost_bfs = geister_distanzen[ghost]
        if pos in ghost_bfs:
            return ghost_bfs[pos]

    if ghost_pos in distanzen:
        return distanzen[ghost_pos]

    return abs(pos[0] - ghost_pos[0]) + abs(pos[1] - ghost_pos[1])


def _ghost_dist_to(ghost, target, geister_distanzen):
    """Distanz eines Geistes zu einem bestimmten Feld (aus Ghost-BFS)."""
    if geister_distanzen is not None and ghost in geister_distanzen:
        ghost_bfs = geister_distanzen[ghost]
        if target in ghost_bfs:
            return ghost_bfs[target]
    return None