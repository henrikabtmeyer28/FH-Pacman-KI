import importlib

import P_final.bfs_distanzen

importlib.reload(P_final.bfs_distanzen)

from P_final.bfs_distanzen import bfs_distanzen, begehbare_nachbarn
from game_core.config import powerpill_time_max  # = 10


def evaluate(pos, level, wertekarte, dot_positionen,
             geister, sackgassen, powerpill_timer=0,
             distanzen=None, geister_distanzen=None,
             pac_pos=None):
    """
    Bewertet eine Position mit allen Faktoren.

    Parameter:
        pos:               (y, x) — das zu bewertende Feld
        level:             Spielfeld (env.view)
        wertekarte:        Dict aus value_iteration()
        dot_positionen:    Set der aktuellen Dot-Positionen
        geister:           Liste aus env.ghost_list
        sackgassen:        Dict {(y,x): tiefe} aus finde_sackgassen()
        powerpill_timer:   Verbleibende Züge der Powerpill-Wirkung
        distanzen:         Dict aus bfs_distanzen() von Pacmans Position
        geister_distanzen: Dict {ghost_obj: bfs_dict}
        pac_pos:           (y, x) aktuelle Position von Pacman
                           (für Flucht-aus-Sackgasse Logik)

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

    nahe_geister = 0
    naechste_geist_dist = float('inf')
    naechster_geist_typ = None

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
        dist = _ghost_dist(ghost, pos, ghost_pos, geister_distanzen, distanzen)

        if dist < naechste_geist_dist:
            naechste_geist_dist = dist
            naechster_geist_typ = ghost_typ

        if dist <= 5:
            nahe_geister += 1

        # ------ GEISTER SIND VERÄNGSTIGT ------
        if geister_sind_veraengstigt:
            if powerpill_timer > dist + 1 and dist > 0:
                score += 300 / (dist + 1)
            elif powerpill_timer <= 3 and dist <= 3:
                score -= 500
        # ------ GEISTER SIND NORMAL ------
        else:
            if dist <= 1:
                score -= 100000
            elif dist <= 2:
                score -= 3000
            elif dist <= 3:
                score -= 800
            elif dist <= 5:
                faktor = 3.0 if ghost_typ == 'H' else 1.0
                score -= faktor * 150 / dist
            elif dist <= 8:
                faktor = 2.0 if ghost_typ == 'H' else 0.5
                score -= faktor * 60 / dist
            elif dist <= 12 and ghost_typ == 'H':
                score -= 20 / dist

    # ============================================
    # FEATURE 5: Multi-Geist Zangen-Gefahr
    # ============================================
    if nahe_geister >= 2 and not geister_sind_veraengstigt:
        score -= 400 * nahe_geister

    # ============================================
    # FEATURE 6: Sackgassen — tiefenbasiert
    # ============================================
    # sackgassen ist jetzt ein Dict {pos: tiefe}
    # tiefe = Schritte bis zum Ausgang (Kreuzung)
    # Kernidee: Sicher wenn ghost_dist > 2 * tiefe + Puffer
    #           (rein + raus bevor Geist am Ausgang ist)
    #           Geister sind außerdem langsamer als Pacman!
    verbleibende_dots = len(dot_positionen)

    if pos in sackgassen and not geister_sind_veraengstigt:
        tiefe = sackgassen[pos]
        hunter_puffer = 5 if naechster_geist_typ == 'H' else 0

        # --- ENDGAME-ERKENNUNG ---
        # Zähle wie viele der verbleibenden Dots in Sackgassen liegen
        dots_in_sackgassen = sum(1 for d in dot_positionen if d in sackgassen)
        ist_endgame = verbleibende_dots <= 5 and dots_in_sackgassen > 0

        if ist_endgame and pos in dot_positionen:
            # ENDGAME: Pacman muss nur REIN, nicht zurück!
            # Spiel endet sofort wenn alle Dots gefressen sind.
            # → Sicherheitsgrenze = nur Hinweg (tiefe statt 2*tiefe)
            sicherheits_grenze = tiefe + hunter_puffer

            if naechste_geist_dist <= tiefe:
                # Geist ist schneller am Dot als wir → zu riskant
                score -= 500
            elif naechste_geist_dist <= sicherheits_grenze:
                # Knapp, aber der letzte Dot ist es wert!
                score -= 50
            else:
                # Sicher erreichbar → stark anziehen
                score += 80
        else:
            # NORMALFALL: Pacman muss rein UND wieder raus
            sicherheits_grenze = 2 * tiefe + hunter_puffer

            if naechste_geist_dist <= tiefe + 1:
                # Geist kann uns abschneiden!
                score -= 1500
            elif naechste_geist_dist <= sicherheits_grenze:
                # Knapp — lieber vermeiden
                score -= 300
            else:
                # Sicher → Dots attraktiv machen
                if pos in dot_positionen:
                    score += 25

    # ============================================
    # FEATURE 7: Flucht aus Sackgasse
    # ============================================
    # Wenn Pacman AKTUELL in einer Sackgasse steckt:
    # → Richtung Ausgang (niedrigere Tiefe) stark bevorzugen
    # → Tiefer rein nur wenn wirklich sicher
    # Prüfe ob es tiefer in der Sackgasse noch Dots gibt (Endgame-Relevanz)
    def _dots_tiefer_in_sackgasse(ab_tiefe):
        """Zählt Dots die tiefer in der Sackgasse liegen als ab_tiefe."""
        anzahl = 0
        for d in dot_positionen:
            if d in sackgassen and sackgassen[d] >= ab_tiefe:
                anzahl += 1
        return anzahl

    if pac_pos is not None and pac_pos in sackgassen and not geister_sind_veraengstigt:
        pac_tiefe = sackgassen[pac_pos]
        hunter_puffer = 5 if naechster_geist_typ == 'H' else 0

        # Endgame-Check: Liegen die letzten Dots tiefer in dieser Sackgasse?
        dots_tiefer = _dots_tiefer_in_sackgasse(pac_tiefe)
        endgame_sammeln = verbleibende_dots <= 5 and dots_tiefer >= verbleibende_dots

        if pos in sackgassen:
            pos_tiefe = sackgassen[pos]

            if pos_tiefe < pac_tiefe:
                # → Richtung Ausgang!
                if endgame_sammeln:
                    pass  # NICHT fliehen! Die letzten Dots liegen tiefer drin
                elif naechste_geist_dist < 2 * pac_tiefe + hunter_puffer:
                    score += 250     # Starker Flucht-Bonus
                else:
                    score += 30      # Leichter Bonus auch wenn sicher
            elif pos_tiefe > pac_tiefe:
                # → Tiefer rein
                if endgame_sammeln:
                    # Endgame: tiefer rein ist gewollt → Bonus statt Strafe!
                    score += 150
                else:
                    sicherheits_grenze_tief = 2 * pos_tiefe + hunter_puffer
                    if naechste_geist_dist < sicherheits_grenze_tief:
                        score -= 500     # Gefährlich, nicht noch tiefer!
        else:
            # pos ist RAUS aus der Sackgasse → Ausgang erreicht!
            if naechste_geist_dist < 2 * pac_tiefe + hunter_puffer + 3:
                score += 350         # Starker Bonus fürs Rauskommen

    # ============================================
    # FEATURE 8: Bewegungsfreiheit & Fluchtweg-Analyse
    # ============================================
    nachbarn = begehbare_nachbarn(level, pos[0], pos[1])
    anzahl_nachbarn = len(nachbarn)
    score += 3 * anzahl_nachbarn

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
            score -= 2000
        elif sichere_ausgaenge == 1 and naechste_geist_dist <= 3:
            score -= 500

    # ============================================
    # FEATURE 9: Korridor-Gefahr
    # ============================================
    if anzahl_nachbarn <= 2 and not geister_sind_veraengstigt:
        if naechste_geist_dist <= 4:
            score -= 200
        elif naechste_geist_dist <= 6:
            score -= 40

    return score


def _ghost_dist(ghost, pos, ghost_pos, geister_distanzen, distanzen):
    """
    Beste verfügbare Distanz vom Geist zur Kandidatenposition.
    """
    if geister_distanzen is not None and ghost in geister_distanzen:
        ghost_bfs = geister_distanzen[ghost]
        if pos in ghost_bfs:
            return ghost_bfs[pos]

    if ghost_pos in distanzen:
        return distanzen[ghost_pos]

    return abs(pos[0] - ghost_pos[0]) + abs(pos[1] - ghost_pos[1])


def _ghost_dist_to(ghost, target, geister_distanzen):
    """Distanz eines Geistes zu einem bestimmten Feld."""
    if geister_distanzen is not None and ghost in geister_distanzen:
        ghost_bfs = geister_distanzen[ghost]
        if target in ghost_bfs:
            return ghost_bfs[target]
    return None