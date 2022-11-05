## 1. SAMOSTATNÁ PRÁCE

### Zadání:
Implementujte distribuovanou aplikaci pro volbu 1 uzlu jako mastera z N identických uzlů. Ve druhé fázi master uzel
řídí “obarvení“ 1/3 uzlů jako „zelený“ a zbylých 2/3 jako „červený“. Master uzel je vždy obarvený jako „zelený“,
počet „zelených“ uzlů se zaokrouhluje směrem nahoru.

### Základní podmínky:
- Zdrojový kód včetně dokumentace bude uložen v repozitáři https: //github.com/ nebo https://gitlab.kiv.zcu.cz/
- Dokumentace v souboru README.md v kořenovém adresáři. Musí obsahovat:
- Popis způsobu řešení/algoritmy jednotlivých problémů (volba mastera, barvení uzlů)
- Pokud není zajištěno automatické sestavení aplikace před jejím spuštěním, popis sestavení
- Popis spuštění a ověření funkčnosti aplikace
- Minimální počet uzlů systému je 3 a je možné jej změnou hodnoty parametru změnit.
- Každý uzel vypisuje do logu (standardní výstup) zřetelně každou změnu svého stavu, včetně stavu v jakém
začal (např. “init”, “master”, “green”, “red”)
- Po ukončení volby mastera a obarvení uzlů, vypíše master do logu přehled uzlů a jejich obarvení.

### Technické podmínky:
- Využití nástrojů Vagrant a Docker pro vytvoření a spuštění infrastruktury.
- Sestavení aplikace musí být možné v prostředí Unix/Linux


## Možné nedostatky aplikace


## Popis aplikace


## Sestavení a spuštění


## Testování aplikace


