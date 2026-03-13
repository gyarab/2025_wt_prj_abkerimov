# MelodyStream

MelodyStream je webová aplikace postavená na frameworku **Django**, která slouží jako platforma pro poslech hudby a organizaci vlastních hudebních sbírek. Aplikace umožňuje plynulé přehrávání hudby přímo v prohlížeči a snadné objevování nových interpretů.

---

## Odborný článek

MelodyStream je <u>webová aplikace</u> zaměřená na <u>streamování</u> hudebního obsahu a správu osobního <u>katalogu</u> skladeb. Aplikace využívá moderní webové technologie pro zprostředkování kvalitního <u>audio formátu</u> bez nutnosti instalace desktopového klienta. Přehrávání probíhá asynchronně v HTML5 přehrávači, takže uživatel může plynule procházet aplikací bez přerušení hudby.

Pro správnou organizaci obsahu systém pracuje s komplexními <u>metadaty</u>. Každá skladba je striktně vázána na konkrétní <u>album</u> a <u>interpreta</u> a obsahuje informace jako je délka stopy, cover art a zařazení do <u>žánru</u>. 

Systém rozlišuje tři <u>uživatelské role</u>. <u>Anonymní návštěvník</u> má přístup pouze na úvodní landing page s nabídkou registrace a nevidí detailní obsah knihovny. <u>Registrovaný uživatel</u> může vyhledávat v hudební databázi, spouštět přehrávání a především vytvářet vlastní <u>playlisty</u>, do kterých si ukládá oblíbené skladby. <u>Administrátor</u> má navíc přístup do administračního rozhraní, kde řídí celou <u>databázi</u> – nahrává nové skladby, upravuje informace o interpretech a moderuje uživatelské účty.

Základní architektura je postavena na relační databázi, která se skládá z několika vzájemně provázaných <u>entit</u>. Entita *Artist* uchovává informace o hudebnících a je vázána s entitou *Album* vztahem 1:M. Entita *Track* (skladba) obsahuje fyzickou cestu k audio souboru a patří do konkrétního alba (vztah M:1). Entita *Playlist* agreguje skladby pomocí vazby M:N a je navázána na entitu *User*, která zajišťuje autentizaci a správu profilů.

---

## Databázový návrh

| Entita | Atributy a vazby |
| :--- | :--- |
| **Artist** | id, name, bio, image_url |
| **Album** | id, title, release_date, cover_url → Artist (M:1) |
| **Track** | id, title, duration, audio_file_url, genre → Album (M:1) |
| **Playlist** | id, name, is_public, created_at → User (M:1) ↔ Track (M:N) |
| **User** | id, username, email, password, is_admin |

---

## User Flow

![UserFlow](img/IMG_19793.heic)

---

## Wireframy

### Mobilní verze

![Wireframe1](img/IMG_1979.heic)

### Desktopová verze

![Wireframe2](img/IMG_19792.heic)


### E-R diagram

![Diagram](img/IMG_19794.heic)
