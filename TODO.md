# TODO — OPPS Generator

## ✅ URAĐENO

### v15.5 — Više podnosioca
- [x] Migracija tabele podnosioc (godina PK → id PK)
- [x] Selektor podnosioca (combobox)
- [x] Upravljanje podnosiocima (+ Novi / - Obriši / Aktivan)
- [x] XML import (podnosioc iz XML-a)
- [x] XML export (aktivni podnosilac)
- [x] Migracija postojeće baze

### v15.6 — Napredni filteri i sortiranje
- [x] Filter po datumu ("Samo ove godine", "Samo ovog meseca")
- [x] Sortiranje tabele sa status label

### v15.7 — Tabovi, grafikoni, dark theme
- [x] Notebook sa 5 tabova
- [x] Matplotlib grafikoni
- [x] Dark theme

### v15.8 — Performanse
- [x] Indeksi u bazi
- [x] Lazy loading (paginacija)
- [x] Keširanje XSD seme

### Popravke
- [x] Bug sa `_izabran_podnosioca` popravljen
- [x] Dugmad + Novi i Aktivan uklonjena, ostaje - Obriši
- [x] Backup fajlovi, testovi, baza, docs/superpowers uklonjeni sa GitHub-a

---

## ❌ PREOSTALO

### v15.9 — Planirano
- [ ] Refaktoring na MVC pattern (Model, View, Controller)
- [ ] Export u PDF (ReportLab ili WeasyPrint)
- [ ] Napredni filteri (range slider za iznos)
- [ ] Sortiranje tabele — tooltip
- [ ] Pregled unosa — kartici
- [ ] Grafikoni (matplotlib)
- [ ] Dark theme

### Sigurnost (odloženo)
- [ ] Lozinka za pristup bazi
- [ ] Enkripcija baze (SQLCipher)
- [ ] Audit log

### Refaktoring (odloženo)
- [ ] MVC pattern
