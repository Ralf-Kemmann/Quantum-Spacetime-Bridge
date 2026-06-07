# QSB-CAUSALITY02B Concept Note

## Ziel

Dieser Block entwickelt eine zeitfreie Rahmenstruktur für

$$X=(V,K,\mathcal E)$$

als Konfiguration, für

$$X\rightsquigarrow_0 Y\iff \mathcal A_0(X,Y)=1$$

als primitive Zulässigkeit, für

$$\Omega_0(X)=\{Y\mid X\rightsquigarrow_0^*Y\}$$

als Fortsetzungsraum und für

$$X\rightsquigarrow_1 Y$$

als verfeinerte Zulässigkeit unter zusätzlicher Fixierungsbedingung.

## Zeitfreie Zulässigkeit

Eine primitive Zulässigkeitskante $X\rightsquigarrow_0 Y$ ist genau dann gegeben, wenn:

1. $Y$ nur lokal von $X$ abweicht,
2. die Änderung mit der vorhandenen relationalen Kompatibilitätsstruktur vereinbar ist,
3. Konsistenz- und Erhaltungsbedingungen erfüllt sind,
4. keine relationale Fixierung als Voraussetzung angenommen wird,
5. keine externe Hintergrundzeit eingeführt wird.

Die Formulierung ist daher als definitorischer Rahmen zu lesen; sie ist nicht als Beweis für emergente Zeit, Geometrie oder Kausalität.

## Fortsetzungsraum und Fixierung

Ein Fortsetzungsraum ist die Menge aller durch transitive primitive Zulässigkeit erreichbaren Zustände. Eine relationale Eigenschaft $f$ wird durch das unabhängige Prädikat $P_f(X)\in\{0,1\}$ beschrieben. Erst danach kann Fixierung formuliert werden:

$$f\in\mathcal F_0(X) \iff \forall Y\in\Omega_0(X): P_f(Y)=1.$$

Dies ist nicht zirkulär; $P_f$ ist unabhängig von der Fixierungsdefinition. Stabilität ist ein lokales Verhalten, Fixierung ist eine Eigenschaft des gesamten Fortsetzungsraums.

## Richtungskandidat

Der Kandidat

$$X\prec_0 Y \iff X\rightsquigarrow_1 Y \land \Omega_1(Y)\subsetneq\Omega_1(X)$$

ist nur ein formaler Richtungskandidat. Er ist nicht automatisch eine vollständige oder physikalische Ordnung. Die stärkere Aussage

$$\mathcal F_0(X)\subsetneq\mathcal F_0(Y)$$

ist nur unter Zusatzannahmen äquivalent zu einer echten Verengung des Fortsetzungsraums: Vollständigkeit, Wirksamkeit, Nichtredundanz und Trennschärfe.

## Verhältnis zur Distanz aus CAUSALITY02A

Die Distanz aus dem vorangehenden Block darf nur als Nachbarschafts- oder Zulässigkeitsfilter dienen. Sie ist keine Richtungsquelle und erzeugt keine Eigenzeit.

## Offene Lücke

Die verbleibende Lücke ist die zusätzliche Struktur, die aus einem zulässigen Fortsetzungsrahmen eine robuste, zeitfreie Fixierungslogik und gegebenenfalls eine strengere Ordnung macht. Azyklizität ist damit nicht gleichbedeutend mit Wohlfundiertheit; letzteres erfordert zusätzliche Bedingungen wie lokale Endlichkeit oder eine Rangfunktion.

## Claim Boundary

Dieser Block formuliert einen formalen Rahmen für zeitfreie Zulässigkeit, Fortsetzungsräume und relationale Fixierung. Er behauptet keine emergente Zeit, keine emergente Geometrie, keine vollständige Kausalität und keine physikalische Ordnung aus dem Rahmen allein.
