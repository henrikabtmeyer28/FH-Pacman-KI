import importlib

import P_final.bfs_distanzen

importlib.reload(P_final.bfs_distanzen)

from P_final.bfs_distanzen import bfs_distanzen, begehbare_nachbarn
from game_core.config import powerpill_time_max  # = 10


# Das neue Feld kriegt einen Score anhand von den folgenden Kriterien
def evaluate(pos, level, wertekarte, dot_positionen,
             geister, sackgassen, powerpill_timer=0,
             distanzen=None, geister_distanzen=None,
             pac_pos=None):

    if distanzen is None:
        distanzen = bfs_distanzen(level, pos[0], pos[1])

    score = 0.0

    # 1. grundlegender Score der Wertekarte
    score += wertekarte.get(pos, 0)

    # 2. direkter Dot -> +50
    if pos in dot_positionen:
        score += 50

    # 3. wie weit ist der nächste Dot entfernt?
    # hohe nächste Distanz -> niedriger Wert
    dot_distanzen = []
    for dot in dot_positionen:
        if dot in distanzen:
            dot_distanzen.append(distanzen[dot])

    if dot_distanzen:
        score -= 5 * min(dot_distanzen)

    # 4. Geister Gefahr vs. Jagd mit der Powerpille
    geister_sind_veraengstigt = powerpill_timer > 0

    nahe_geister = 0       # Zähler für Geister in Reichweite <= 5
    naechste_geist_dist = float('inf')
    naechster_geist_typ = None

    for ghost in geister:
        gy, gx = ghost.get_position()
        ghost_pos = (gy, gx)
        ghost_typ = ghost.getType()
        ghost_tot = ghost.get_is_dead()
        respawn_zeit = ghost.get_respawn_time()

        # falls Geist tot -> gucken wo und wann er respawnt
        if ghost_tot:
            if respawn_zeit <= 2:
                ry, rx = ghost.get_respawn_pos()
                respawn_pos = (ry, rx)
                if respawn_pos in distanzen:
                    respawn_dist = distanzen[respawn_pos]
                    if respawn_dist <= 2:
                        score -= 300
            continue

        # Distanz von der Position zum nächsten Geist
        dist = _ghost_dist(ghost, pos, ghost_pos, geister_distanzen, distanzen)

        if dist < naechste_geist_dist:
            naechste_geist_dist = dist
            naechster_geist_typ = ghost_typ

        if dist <= 5:
            nahe_geister += 1

        # veraengstigte Geister
        if geister_sind_veraengstigt:
            if powerpill_timer > dist + 1 and dist > 0:
                # Geist kann waehrend der Zeit gegessen werden
                score += 300 / (dist + 1)
            elif powerpill_timer <= 3 and dist <= 3:
                # Powerpill reicht nicht mehr aus
                score -= 500
        # Geisterdistanzen bewerten
        else:
            if dist <= 1:
                score -= 100000
            elif dist <= 2:
                score -= 3000
            elif dist <= 3:
                score -= 800
            elif dist <= 5:
                # Hunter ist gefährlicher
                faktor = 3.0 if ghost_typ == 'H' else 1.0
                score -= faktor * 150 / dist
            elif dist <= 8:
                # Hunter aus mittlerer Distanz beachten
                faktor = 2.0 if ghost_typ == 'H' else 0.5
                score -= faktor * 60 / dist
            elif dist <= 12 and ghost_typ == 'H':
                # Hunter auch aus großer Distanz leicht beachten
                score -= 20 / dist

    # 5. 2 Geister sind in der Nähe -> Sandwich-Gefahr
    if nahe_geister >= 2 and not geister_sind_veraengstigt:
        score -= 400 * nahe_geister

    # 6. Sackgassen sind tödlich
    # sackgassen ist ein Dict {pos: tiefe}
    # tiefe = Schritte bis zum Ausgang (Kreuzung)
    # Sicher wenn ghost_dist > 2 * tiefe + Puffer (rein + raus)
    verbleibende_dots = len(dot_positionen)

    if pos in sackgassen and not geister_sind_veraengstigt:
        tiefe = sackgassen[pos]
        hunter_puffer = 5 if naechster_geist_typ == 'H' else 0

        # wie viele der letzten Dots liegen in Sackgassen?
        dots_in_sackgassen = sum(1 for d in dot_positionen if d in sackgassen)
        ist_endgame = verbleibende_dots <= 5 and dots_in_sackgassen > 0

        if ist_endgame and pos in dot_positionen:
            # ENDGAME: Pacman muss nur REIN, nicht zurück!
            # Spiel endet sofort wenn alle Dots gefressen
            # -> Sicherheitsgrenze = nur Hinweg (tiefe statt 2*tiefe)
            sicherheits_grenze = tiefe + hunter_puffer

            if naechste_geist_dist <= tiefe:
                # Geist ist schneller am Dot als wir
                score -= 500
            elif naechste_geist_dist <= sicherheits_grenze:
                # Knapp, aber der letzte Dot ist es wert
                score -= 50
            else:
                # Sicher erreichbar -> anziehen
                score += 80
        else:
            # NORMALFALL: Pacman muss rein UND wieder raus
            sicherheits_grenze = 2 * tiefe + hunter_puffer

            if naechste_geist_dist <= tiefe + 1:
                # Geist kann uns abschneiden
                score -= 1500
            elif naechste_geist_dist <= sicherheits_grenze:
                # Knapp -> lieber vermeiden
                score -= 300
            else:
                # Sicher -> Dots attraktiv machen
                if pos in dot_positionen:
                    score += 25

    # 7. Flucht aus Sackgasse
    # Wenn Pacman AKTUELL in einer Sackgasse steckt:
    # -> Richtung Ausgang (niedrigere Tiefe) bevorzugen
    # -> Tiefer rein nur wenn wirklich sicher
    def _dots_tiefer_in_sackgasse(ab_tiefe):
        # Zählt Dots die tiefer in der Sackgasse liegen
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
                # -> Richtung Ausgang!
                if endgame_sammeln:
                    pass  # NICHT fliehen! Die letzten Dots liegen tiefer drin
                elif naechste_geist_dist < 2 * pac_tiefe + hunter_puffer:
                    score += 250     # Starker Flucht-Bonus
                else:
                    score += 30      # Leichter Bonus auch wenn sicher
            elif pos_tiefe > pac_tiefe:
                # -> Tiefer rein
                if endgame_sammeln:
                    # Endgame: tiefer rein ist gewollt
                    score += 150
                else:
                    sicherheits_grenze_tief = 2 * pos_tiefe + hunter_puffer
                    if naechste_geist_dist < sicherheits_grenze_tief:
                        score -= 500     # Gefährlich, nicht noch tiefer!
        else:
            # pos ist RAUS aus der Sackgasse -> Ausgang erreicht
            if naechste_geist_dist < 2 * pac_tiefe + hunter_puffer + 3:
                score += 350         # Bonus fürs Rauskommen

    # 8. Fluchtweg-Analyse und Bewegungsfreiheit
    nachbarn = begehbare_nachbarn(level, pos[0], pos[1])
    anzahl_nachbarn = len(nachbarn)
    score += 3 * anzahl_nachbarn

    # Fluchtweg-Analyse: Wie viele Wege sind geisterfrei
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

                # Wenn der Geist nah am Ausgang ist
                if ghost_dist_zum_ausgang is not None and ghost_dist_zum_ausgang <= 2:
                    ausgang_sicher = False
                    break
            if ausgang_sicher:
                sichere_ausgaenge += 1

        if sichere_ausgaenge == 0:
            score -= 2000      # Komplett eingekreist
        elif sichere_ausgaenge == 1 and naechste_geist_dist <= 3:
            score -= 500       # Nur ein Ausweg und Geist sehr nah

    # 9. Korridor Gefahr -> nur 2 Nachbarn
    if anzahl_nachbarn <= 2 and not geister_sind_veraengstigt:
        if naechste_geist_dist <= 4:
            score -= 200
        elif naechste_geist_dist <= 6:
            score -= 40

    return score


def _ghost_dist(ghost, pos, ghost_pos, geister_distanzen, distanzen):

    # Beste verfügbare Distanz vom Geist (ghost_pos) zur Position (pos)
    # 1. BFS vom Geist (geister_distanzen)
    # 2. BFS von Pacman (distanzen)
    # 3. Manhattan-Distanz (Fallback)

    if geister_distanzen is not None and ghost in geister_distanzen:
        ghost_bfs = geister_distanzen[ghost]
        if pos in ghost_bfs:
            return ghost_bfs[pos]

    if ghost_pos in distanzen:
        return distanzen[ghost_pos]

    return abs(pos[0] - ghost_pos[0]) + abs(pos[1] - ghost_pos[1])


def _ghost_dist_to(ghost, target, geister_distanzen):
    # Distanz eines Geistes zu einem bestimmten Feld (aus Ghost-BFS)
    if geister_distanzen is not None and ghost in geister_distanzen:
        ghost_bfs = geister_distanzen[ghost]
        if target in ghost_bfs:
            return ghost_bfs[target]
    return None