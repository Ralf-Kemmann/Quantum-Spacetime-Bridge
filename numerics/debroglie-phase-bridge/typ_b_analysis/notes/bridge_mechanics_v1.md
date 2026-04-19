# bridge_mechanics_v1

## 1. Problemstellung

Dieses Dokument formuliert das erste explizite Mechanikmodell der de-Broglie-Brücke.  
Es baut auf `bridge_minimal_model_v1` auf, geht aber einen entscheidenden Schritt weiter:

Nicht nur einen geometrie-kompatiblen Brückenzustand beschreiben, sondern eine **kleine testbare Kopplungsmechanik** zwischen interferenzieller Struktur und geometrienahem coarse-grained Träger explizit machen.

Leitfrage:

> Welche minimale Kopplung zwischen `theta` und `A` erzeugt oder stabilisiert einen geometrie-kompatiblen Brückenzustand?

---

## 2. Ausgangslage

Das Minimalmodell der Brücke führte die Größen

- `A`
- `theta`
- `phi_geom`
- `d_eff`

ein und arbeitete mit der Grundlesart:

- `A` = geometrienaher Proxy
- `theta` = interferenzieller Strukturkanal
- `A ↔ theta` = Brücke

Zugleich zeigte der bisherige Projektstand:

- robuster Oberblock `negative ≈ abs > positive`
- kein belastbarer Nachweis `negative > abs`
- Hinweise darauf, dass die Brücke nicht als singuläre Einzelfaser, sondern eher als überlappte Mehrkanal-Struktur zu lesen ist

Insbesondere deutet die bisherige Kanal-Lesart darauf hin, dass geometrienahe Bindung/Stabilisierung und informationsartige Übergangsstruktur nicht vollständig identisch sind.

---

## 3. Ziel des Mechanikmodells

`bridge_mechanics_v1` soll testen,

1. ob `theta` auf `A` kontrolliert und nichttrivial wirkt,
2. ob unterschiedliche Kopplungsformen unterschiedliche Brückenzustände erzeugen,
3. ob sich Bindung/Stabilisierung und Informations-/Übergangsstruktur partiell trennen lassen,
4. ob die Kopplung die geometrische Lesbarkeit von `phi_geom` bzw. `d_eff` verbessert, erhält oder beschädigt.

Das Modell ist bewusst **minimal**:
keine volle Feldtheorie, keine Lagrange-Dichte, keine GR-Closure.  
Es ist ein operatives Arbeitsmodell für die Mechanik der Brücke.

---

## 4. Freiheitsgrade

### 4.1 `A0`
Ungekoppelter coarse-grained Kohärenz-/Amplitudenproxy.

Interpretation:
- geometrienahe Tragfähigkeit
- Bindungs-/Stabilisierungskandidat

### 4.2 `theta0`
Ungekoppelter Phasen-/Interferenzproxy.

Interpretation:
- interferenzielle Modulation
- Struktur- und Übergangseinfluss
- nicht selbst direkt Geometrie

### 4.3 `A_eff`
Effektiver, durch Kopplung modulierter Kohärenzproxy.

Interpretation:
- resultierender Brückenträger nach Mechanikschicht

### 4.4 `A_bind`
Optionaler bindungs-/stabilisierungsnaher Kanal.

### 4.5 `B_info`
Optionaler informations-/übergangsnaher Kanal.

### 4.6 `phi_geom`
Geometrienahe Projektion aus `A_eff` bzw. `A_bind`.

### 4.7 `d_eff`
Effektiver Distanzkandidat.

---

## 5. Mechanikhypothese

Das Modell setzt als Arbeitshypothese:

> Die de-Broglie-Brücke ist keine Einzelfaser, sondern eine überlappte Mehrkanal-Struktur.  
> `A` trägt primär geometrienahe Bindung/Stabilisierung, während `theta` über eine Kopplung die Ausbildung, Stabilität oder Verschiebung dieser Struktur beeinflusst.  
> Zusätzlich kann eine informationsartige Übergangsstruktur teilweise getrennt vom geometrienahen Bindungskanal auftreten.

Kurz:

- `A` = Bindung / Stabilisierung / geometrische Tragfähigkeit
- `theta` = interferenzielle Modulation
- `B_info` = Informations-/Übergangsstruktur
- Brücke = überlappte Kopplungsarchitektur

---

## 6. Regime-Trennung

### 6.1 `macro`
- `theta` wird teilweise ausgemittelt
- `A` dominiert
- Ziel: stabile geometrische Lesbarkeit

### 6.2 `coherent`
- `theta` bleibt aktiv
- Interferenzstruktur wirkt sichtbar in die Kopplung hinein
- Ziel: Übergangs- und Feinstruktur der Brücke

### 6.3 `mixed`
- Zwischenbereich
- beide Kanäle tragen gemeinsam

---

## 7. Zulässige Kopplungsformen

### 7.1 `additive`
`A_eff = A0 + lambda * F(theta0)`

Lesart:
`theta0` liefert einen zusätzlichen Strukturbeitrag.

### 7.2 `multiplicative`
`A_eff = A0 * (1 + lambda * F(theta0))`

Lesart:
`theta0` moduliert vorhandene Kohärenz.

### 7.3 `regime_gated`
`A_eff = A0 * M(theta0, regime, tau, lambda)`

Lesart:
Die Kopplung hängt vom Regime ab.

### 7.4 `competitive`
`A_eff = H(A0, theta0, lambda)`

Lesart:
Zu starke Interferenz kann geometrische Lesbarkeit auch stören.

### 7.5 `dual_channel`
- `A_bind = H1(A0, theta0, lambda)`
- `B_info = H2(A0, theta0, lambda)`

Lesart:
Bindung/Stabilisierung und Informations-/Übergangsstruktur werden explizit getrennt verfolgt.

---

## 8. Mechanische Arbeitslogik

Die interne Mechanik folgt der Kette:

- Mikrostruktur
- coarse-graining
- Basiskonstruktion von `A0` und `theta0`
- Kopplungsschicht
- resultierender Brückenträger `A_eff`
- Projektion `A_eff -> phi_geom -> d_eff`

Beim `dual_channel`-Modus zusätzlich:

- `A_bind` als geometrienaher Bindungskanal
- `B_info` als informationsartiger Parallelkanal

Die Mechanik ist damit nicht bloß ein Markeraufsatz, sondern die explizite Zwischenschicht zwischen Interferenzstruktur und geometrischer Lesbarkeit.

---

## 9. Diagnostische Lesart

Das Modell verlangt mindestens folgende Diagnoseebenen:

- `phase_influence_score`
- `structure_stability_score`
- `binding_channel_score`
- `information_channel_score`
- `geometry_readability_score`
- `delta_vs_baseline`

Arbeitslesart:

- gute Mechanik = kontrollierte, nichttriviale Kopplung
- schlechte Mechanik = Rauschen, Destruktion oder Irrelevanz
- starke Mechanik = kleine, aber wirksame Kopplung mit erkennbarer funktionaler Gliederung

---

## 10. Erste testbare Claims

### Claim M1
Mindestens eine kleine Kopplungsform koppelt `theta` und `A` nichttrivial und kontrolliert.

### Claim M2
Eine tragfähige Kopplungsform verbessert oder stabilisiert den Brückenzustand relativ zur ungekoppelten Baseline.

### Claim M3
Bindung/Stabilisierung und Informations-/Übergangsstruktur sind nicht vollständig deckungsgleich.

### Claim M4
`negative` und `abs` reagieren auf brauchbare Kopplung günstiger als `positive`.

### Claim M5
Eine physikalisch plausible Brückenmechanik zeigt `phase_influence` klein, aber nicht null, zumindest in signalhaltigen Fällen.

---

## 11. Erwartbare erste Lesart

Auf Basis des bisherigen Projektstands ist zunächst plausibel zu erwarten:

- `multiplicative` und `dual_channel` sind die interessantesten ersten Kopplungsformen
- `negative` und `abs` bleiben im Vorteil
- `positive` bleibt schwächer, instabiler oder kanalärmer
- `macro` zeigt eher kleine stabile Kopplung
- `coherent` zeigt stärkere, aber noch kontrollierte Kopplung

Diese Erwartung ist keine Bestätigung, sondern eine saubere Sollbruchkarte.

---

## 12. Bewusst offene Punkte

`bridge_mechanics_v1` löst ausdrücklich noch nicht:

- mikroskopische Herleitung der Kopplungsform
- eindeutige physikalische Interpretation aller Kanäle
- volle Metrikrekonstruktion
- GR-Closure
- Materiesektor
- vollständige Kausalstruktur
- experimentelle Realisierung

---

## 13. Nächster Schritt

Der nächste operative Test ist jetzt:

- kleine Kopplungssweeps
- Baseline-vs-Coupling
- Exportklassenvergleich
- Regimevergleich
- Kanaltrennung
- Geometry-response auf `d_eff`

---

## 14. Bottom line

`bridge_mechanics_v1` markiert den Übergang von

> Brückenzustand beschreiben

zu

> Brückenmechanik testbar machen

Die zentrale Arbeitslesart lautet:

> Die de-Broglie-Brücke erscheint derzeit nicht als einzelner Verbindungsstrang, sondern als überlappte Mehrkanal-Struktur, deren minimale Kopplungsmechanik jetzt explizit gegen Stabilität, Kanaltrennung und geometrische Lesbarkeit getestet werden muss.
