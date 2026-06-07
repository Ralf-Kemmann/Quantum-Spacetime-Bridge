# QSB-CAUSALITY02A Concept Note

## Ausgangspunkt

Die Kandidatenfunktion

$$d_{ij} = -\ell_0 \log |K_{ij}|, \qquad K_{ij}=\langle\psi_i|\psi_j\rangle$$

wird im aktuellen Stand als relationales Unähnlichkeitsmaß behandelt. Sie ist nicht als Metrik und nicht als physikalischer Raumabstand zu lesen.

## Mathematischer Befund

Unter normierten Überlappungen ist $d_{ij}$ nichtnegativ, und es gilt $d_{ii}=0$. Die Symmetrie folgt aus $K_{ji}=K_{ij}^*$, also $|K_{ji}|=|K_{ij}|$. Für normierte reine Zustände gilt $|\langle\psi_i|\psi_j\rangle|=1$ genau dann, wenn $|\psi_j\rangle=e^{i\phi}|\psi_i\rangle$; auf dem projektiven Hilbertraum ist das dieselbe Zustandsrichtung. Die Dreiecksungleichung ist im Allgemeinen verletzt. Ein explizites Gegenbeispiel mit 0°, 30° und 60° ist:

$$|K_{12}|=|K_{23}|=\cos 30^\circ=\frac{\sqrt3}{2},\qquad |K_{13}|=\cos 60^\circ=\frac12.$$

Mit $\ell_0=1$ folgt

$$d_{12}=d_{23}=-\log\frac{\sqrt3}{2}\approx 0.1438,\qquad d_{13}=-\log\frac12\approx 0.6931,$$

also $d_{13}>d_{12}+d_{23}$, weil $0.6931>0.2876$.

## Rolle als Nachbarschaftsmaß

Die Form eignet sich bedingt zur Definition relationaler Nachbarschaften, etwa

$$\mathcal N_i(\delta)=\{j\mid d_{ij}\le \delta\}$$

oder äquivalent $|K_{ij}|\ge \kappa$. Diese Nachbarschaften sind thresholdabhängig und nicht automatisch räumliche Nachbarschaften.

## Rolle als Zulässigkeitsmaß

Die Distanz kann als Nebenbedingung zeitfreier Zulässigkeit dienen, etwa zur Beschränkung zulässiger Übergänge oder zur Gewichtung von Fortsetzungen. Sie erzeugt aber keine Kausalrichtung aus sich selbst heraus.

## Rolle als Ordnungsmaß

Aus $d_{ij}$ allein folgt kein streng monotones Ordnungsmaß und keine Azyklizität. Eine relationale Fixierung kann nur dann als Ordnungsträger dienen, wenn zusätzliche Struktur, etwa eine fortsetzungsinvariante Regel oder eine explizite Zulässigkeitsbedingung, hinzukommt.

## Verhältnis zu relationalen Fixierungen

Eine relationale Fixierung $\mathcal F(X)$ ist nicht bloß eine kleine Distanz oder eine Schwellenunterschreitung. Sie muss als invariant unter zulässigen Fortsetzungen verstanden werden.

## Verhältnis zu $\tau$

$\tau_{ij}$ kann $d_{ij}$ als lokalen Filter, als Kostenbeitrag oder als Latenzparameter verwenden, aber $d_{ij}$ erzeugt keine Richtung oder Zeit. Ein $\tau$-Beitrag ist erst dann sinnvoll, wenn eine bereits gerichtete zulässige Relation existiert.

## Offene Lücke

Die verbleibende Lücke ist die zusätzliche Struktur, die aus dem relationalen Unähnlichkeitsmaß eine robuste, zeitfreie Zulässigkeitsrelation und gegebenenfalls ein streng monotones Ordnungsmaß macht.

## Claim Boundary

Dieser Block stellt keine physikalische Distanz, keine Kausalrichtung, keine Eigenzeit und keine emergente Geometrie fest. Er beschreibt die formale Rolle von $d_{ij}$ als symmetrisches relationales Unähnlichkeitsmaß.
