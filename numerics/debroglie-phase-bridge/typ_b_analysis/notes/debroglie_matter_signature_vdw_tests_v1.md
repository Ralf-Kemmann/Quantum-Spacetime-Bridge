# debroglie_matter_signature_vdw_tests_v1

## 1. Direkt aus `debroglie_matter_signature_vdw_extension_v1` folgende Claims

### Claim VDW1
Die van-der-Waals-Erweiterung erzeugt mindestens eine zusätzliche stoffsensitive Differenzierungsachse gegenüber dem idealen Gasmodell.

### Claim VDW2
`interaction_score` und/oder `excluded_volume_score` liefern nichttriviale Unterschiede zwischen den Spezies.

### Claim VDW3
Die VDW-erweiterte Signaturordnung weicht stärker oder strukturierter von bloßer Massenordnung ab als die reine de-Broglie-Minimalarchitektur.

### Claim VDW4
Die kombinierte Wellen- plus Stoff-Signatur ist physikalisch informationsreicher als die reine Wellen-Signatur.

### Claim VDW5
Die VDW-Erweiterung lohnt sich als nächster Ausbau nur dann, wenn sie überhaupt zusätzliche strukturierte Differenzierung sichtbar macht.

---

## 2. Unmittelbare Minimalerwartung

Für den ersten VDW-Block ist zunächst zu erwarten:

- die reine Wellen-Signatur bleibt sichtbar
- `a` und `b` führen mindestens formale stoffspezifische Unterschiede ein
- die spannende Frage ist, ob diese Unterschiede im Surrogatraum wirklich strukturell wirksam werden
- nicht garantiert ist, dass `tau` sofort stark profitiert
- möglich ist, dass die Erweiterung zunächst nur schwache, aber konsistente Zusatzstruktur erzeugt

Diese Minimalerwartung ist noch keine Bestätigung, sondern die Sollbruchkarte des Blocks.

---

## 3. Pflichttests

### 3.1 Ideal vs. VDW-Basisvergleich

Vergleich von:

- `gas_model = ideal_gas`
- `gas_model = van_der_waals`

Leitfrage:

> Öffnet die Stoff-Erweiterung überhaupt eine neue Differenzierungsachse?

### 3.2 VDW-Stoffsurrogate

Vergleich von:

- `interaction_score`
- `excluded_volume_score`
- `vdw_signature_score`

Leitfrage:

> Sind `a` und `b` nur formale Zusatzgrößen oder erzeugen sie lesbare Signaturstruktur?

### 3.3 Wellen- vs. Stoff-Signatur

Vergleich von:

- `signature_score_wave`
- `signature_score_vdw`
- optional `signature_score_combined`

Leitfrage:

> Bleibt die de-Broglie-Längenskala allein dominant oder tritt eine zweite materielle Schicht hinzu?

### 3.4 Massen- vs. Materiesensitivität

Vergleich von:

- Massenordnung
- reine Wellen-Signaturordnung
- VDW-Signaturordnung
- `matter_sensitive_delta_vdw`

Leitfrage:

> Wird die materiesensitive Abweichung von bloßer Massenordnung stärker oder robuster?

### 3.5 Tau-Fenstervergleich

Vergleich von:

- `tau_response_score`
- optionale `vdw_tau_response_score`

Leitfrage:

> Reagieren `tau`-Fenster auf die erweiterte Signatur anders als auf die reine Wellen-Signatur?

---

## 4. Weiterführende Tests

### 4.1 Gewichtungsvariation

Für `signature_score_combined` kleine Variationen der Gewichte zwischen:

- Wellen-Schicht
- Stoff-Schicht

Leitfrage:

> Trägt die zusätzliche Struktur robust oder nur unter feiner Gewichtung?

### 4.2 Stoffsensitivitätsprofil

Prüfen:

- welche Spezies im VDW-Raum am stärksten auseinanderlaufen
- ob dies mit chemisch/physikalischer Intuition zumindest grob kompatibel bleibt

Leitfrage:

> Erzeugt die Erweiterung plausible oder nur numerisch beliebige Unterschiede?

### 4.3 Optional später

- alternative Spezieslisten
- reale Molekülmodi
- alternative nicht-ideale Zustandsgleichungen

---

## 5. Entscheidungslogik

### Unterstützt

Der Block gilt als unterstützt, wenn:

- VDW-Surrogate reproduzierbar berechnet werden
- mindestens eine zusätzliche stoffliche Differenzierungsachse sichtbar wird
- die erweiterte Signaturordnung nicht trivial auf die bisherige Wellenordnung kollabiert
- und die materiesensitive Struktur gegenüber Massenskalierung gewinnt oder robuster wird

### Teilweise unterstützt

Der Block gilt als teilweise unterstützt, wenn:

- Unterschiede sichtbar, aber schwach oder stark modellabhängig bleiben
- die Stoffschicht zwar formal da ist, aber nur begrenzt zusätzlichen Informationsgewinn bringt
- `tau` weiter weitgehend stumm bleibt

### Nicht unterstützt

Der Block gilt als nicht unterstützt, wenn:

- die VDW-Erweiterung praktisch keine neue Struktur liefert
- alles auf die bisherige de-Broglie-Längenskala zurückfällt
- oder die Stoffparameter nur numerisches Rauschen hinzufügen

---

## 6. Arbeitsfrage

Die zentrale Frage dieses Blocks lautet:

> Öffnet eine van-der-Waals-Erweiterung der materialspezifischen Signatur überhaupt eine zweite materielle Achse — oder bleibt die aktuelle Brückensignatur im Wesentlichen ein de-Broglie-Längenskalenmodell?

Genau diese Frage entscheidet, ob die Stoff-Skala weiter ausgebaut werden sollte.

---

## 7. Bottom line

`debroglie_matter_signature_vdw_tests_v1` dient dazu, nicht nur zusätzliche Stoffparameter einzuführen, sondern ihren wirklichen physikalischen Mehrwert gegen den bisherigen Grundblock zu testen.

Die operative Leitformel lautet:

> Wir prüfen, ob die VDW-Erweiterung die Signaturidee wirklich verbreitert — oder ob die Brücke vorerst weiterhin fast vollständig auf der de-Broglie-Längenskala lebt.
