# Pflanzis 🌿

Giessplan-Web-App für den Homescreen (iPhone), für zwei Personen mit geteiltem Haushalt.
Live: https://jnhbr.github.io/pflanzis/ · Repo: `jnhbr/pflanzis` (GitHub Pages, Branch `main`)

## Funktionen
- **Heute**: Giessrunde nach Räumen sortiert, «Gegossen» mit Rückgängig, Düngen, Umtopfen prüfen, Vorschau 7 Tage
- **Pflanzen**: Raumplan (Regal pro Raum), Figur oder Foto, Wassertropfen-Anzeige, Figur welkt bei Durst
- **Detail**: Wasservorrat, Pflegeinfos, Tagebuch mit Notizen/Fotos, wer zuletzt gegossen hat
- **Plan**: 21 Tage, Knopf «An Erinnerungen senden» (iOS-Kurzbefehl), Kalenderdatei (.ics)
- **Mehr**: Haushalt teilen (Einladungslink), Erinnerungszeit, Pl@ntNet-Schlüssel, Jahreszeiten-Anpassung, Ferienmodus (Plan für Sitter: teilen/drucken), Räume, Sicherung

## Technik
- Eine Datei `index.html` (Vanilla JS), `db.js` = Pflegedatenbank (~60 Gattungen → Figur, Giessabstand, Saisontyp, Dünger, Licht, Tipp)
- Daten: localStorage + Firestore-Abgleich im Firebase-Projekt **meine-r** (Rezepte-App!) unter `pflanzis/<code>/<pflanzen|tagebuch|raeume|einstellungen|export>`.
  Kein eigenes Projekt, weil das Google-Projektkontingent voll ist (21.11.2026).
- `firestore.rules` gilt für das **ganze** Projekt meine-r (Rezepte + Pflanzis). Beim Ändern beide Blöcke behalten, deployen mit `firebase deploy --only firestore:rules --project meine-r`.
- Schutz = geheimer Haushalts-Code (20 Zeichen) im Pfad, Auflisten gesperrt.
- Erinnerungen: App schreibt bei jeder Änderung `pflanzis/<code>/export/erinnerungen` (Feld `json` = Tage → titel/notiz/zeit/url, 31 Tage). Der iOS-Kurzbefehl «Pflanzis» liest das per Firestore-REST und legt die nächsten 7 Tage an (siehe Abschnitt Kurzbefehl unten).
- Pflanzenerkennung: Pl@ntNet API (gratis, 500/Tag). Schlüssel steht in Firestore (`einstellungen/haushalt.plantnetKey`), nicht im Repo; in my.plantnet.org Domain `jnhbr.github.io` freigeben.
- Bilder: Logo + 10 Figuren mit Higgsfield (nano_banana_2), Originale in `design/` (PNG nicht im Repo), Web-Versionen in `img/fig/`.
- Service Worker `sw.js`: Netz zuerst, offline aus Cache. Bei neuen Dateien Cache-Version erhöhen.

## iOS-Kurzbefehl «Pflanzis» (Erinnerungen, Stand 22.11.2026)
- Erzeugen: `/usr/bin/python3 tools/kurzbefehl.py <haushalts-code> roh.shortcut && shortcuts sign --mode anyone -i roh.shortcut -o Pflanzis.shortcut` (System-Python, nicht Homebrew). `*.shortcut` ist in .gitignore (enthält den Code).
- Ablauf: Export lesen → alle Pflanzis-Erinnerungen als Text (Doppelt-Prüfung über den Titel) → 7 Tagesblöcke (heute bis +6) → «Add New Reminder» mit Alarm `zeit`. Löscht nie etwas (iOS fragt bei jedem Löschen, Filter waren unzuverlässig).
- Nach dem Import auf dem iPhone von Hand: in allen 7 «Add …»-Aktionen Liste **Pflanzis** wählen und bei «Find Reminders» Filter **List is Pflanzis** setzen (ohne Filter hängt die Suche über alle Erinnerungen). Die Liste lässt sich per Datei nicht vorgeben (interne Listen-ID).
- Automation auf Rachels iPhone: täglich 07:00, Sofort ausführen.
- Grenze: Wird früher gegossen, bleibt die alte Erinnerung stehen (abhaken); der neue Termin kommt am nächsten Morgen dazu.
