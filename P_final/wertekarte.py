from P3.bfs import begehbare_nachbarn


def value_iteration(level, begehbare_felder, dot_positionen,
                    gamma=0.85, iterationen=40):
    """
    Berechnet eine Wertekarte für die gesamte Map.

    Jedes Feld bekommt einen Wert:
      - Hoch wenn viele Dots in der Nähe sind
      - Niedrig wenn das Feld weit weg von Dots liegt

    Pacman folgt dem Gradienten: er geht immer zum
    Nachbarfeld mit dem höchsten Wert.

    Parameter:
        level:             Das Spielfeld (env.view)
        begehbare_felder:  Set aller (x,y) die keine Wand sind
        dot_positionen:    Set aller (x,y) wo aktuell Dots liegen
        gamma:             Discount-Faktor (0.0-1.0)
                           0.85 = Dots die 10 Felder weg sind
                           zählen noch ~20% vom Originalwert
        iterationen:       Anzahl der Updates. 40 reicht für
                           typische Pacman-Karten locker aus

    Returns:
        dict: {(x,y): float} — Wert für jedes begehbare Feld
    """
    V = {feld: 0.0 for feld in begehbare_felder}
    # Jedes begehbare Feld kriegt den 0.0 am Anfang

    for _ in range(iterationen):
        V_neu = {}
        for feld in begehbare_felder:
            # Reward: Dot = lohnt sich, leer = leichte Strafe
            if feld in dot_positionen:
                reward = 10.0
            else:
                reward = -0.1

            # Nachbar mit dem höchsten Wert finden
            nachbar_werte = []
            for nachbar in begehbare_nachbarn(level, feld[0], feld[1]):
                if nachbar in V:
                    nachbar_werte.append(V[nachbar])

            if nachbar_werte:
                V_neu[feld] = reward + gamma * max(nachbar_werte)
            else:
                V_neu[feld] = reward

        V = V_neu

    return V