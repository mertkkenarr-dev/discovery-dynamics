"""r01: Steam etiket taksonomisi → data/referans/etiket_taksonomi.csv (elle kodlanmış referans; bu betik tek doğru kaynaktır).

Kullanım: cd scripts && python r01_etiket_taksonomi.py
Boyutlar (KAPSAM §5.1): A tür · B mekanik · C görsel/bakış/ses · D tema/atmosfer/karakter · E oyuncu yapısı · F kapsam/yapı · H teknik.
Ek gruplar: X_degerlendirme (sonradan oluşan yargı; başarıyla döngüsel, içerik niteliği olarak KULLANILMAZ),
            X_uygulama (oyun dışı yazılım işareti), X_meta (dağıtım/üretim bilgisi).
Motivasyon: Quantic Foundry'nin 12 motivasyonu; etiket başına en fazla 2, yalnız bağlantı açıksa. Kodlayıcı 1 = claude_taslak;
ikinci kodlayıcı (Mert) bağımsız kodlar, uyum Cohen κ ile ölçülür (ANALIZ_PLANI §3).
"""

from __future__ import annotations

import csv

import pandas as pd
from ortak import INTERIM, KOK

M = {"Ds": "Destruction", "Ex": "Excitement", "Cp": "Competition", "Cm": "Community", "Ch": "Challenge", "St": "Strategy",
     "Co": "Completion", "Pw": "Power", "Fa": "Fantasy", "Sy": "Story", "De": "Design", "Di": "Discovery"}  # fmt: skip

# boyut → alt grup → {etiket: motivasyon kısaltmaları}
T: dict[str, dict[str, dict[str, str]]] = {
    "A_tur": {
        "ana": {"Action": "Ex", "Adventure": "Di", "Casual": "", "Simulation": "", "Strategy": "St", "RPG": "Pw Sy", "Puzzle": "St", "Arcade": "Ex",
                "Sports": "Cp", "Racing": "Ex Cp", "Action-Adventure": "Ex Di"},
        "platform": {"Platformer": "Ch", "2D Platformer": "Ch", "3D Platformer": "Ch Di", "Puzzle Platformer": "St Ch", "Precision Platformer": "Ch",
                     "Metroidvania": "Di Pw", "Runner": "Ex", "Lemmings": "St"},
        "nisanci": {"Shooter": "Ds Ex", "FPS": "Ds Ex", "Third-Person Shooter": "Ds Ex", "Top-Down Shooter": "Ds Ex", "Arena Shooter": "Ds Cp",
                    "Shoot 'Em Up": "Ds Ch", "Twin Stick Shooter": "Ds Ex", "Bullet Hell": "Ch Ex", "Bullet Heaven": "Pw Ds", "Boomer Shooter": "Ds Ex",
                    "Hero Shooter": "Cp Cm", "Looter Shooter": "Pw Co", "Extraction Shooter": "Cp Ch", "On-Rails Shooter": "Ds Ex", "Battle Royale": "Cp Ex"},
        "anlati": {"Visual Novel": "Sy", "Interactive Fiction": "Sy", "Choose Your Own Adventure": "Sy", "Dating Sim": "Sy Fa", "Otome": "Sy Fa",
                   "Point & Click": "Sy Di", "Hidden Object": "Co Di", "Walking Simulator": "Sy Di", "Survival Horror": "Ex Ch", "Escape Room": "St Di"},
        "roguelike": {"Roguelike": "Ch St", "Roguelite": "Ch Pw", "Action Roguelike": "Ch Ex", "Traditional Roguelike": "Ch St",
                      "Roguelike Deckbuilder": "St Ch", "Mystery Dungeon": "Ch St", "Dungeon Crawler": "Di Pw"},
        "rpg": {"Action RPG": "Pw Ex", "JRPG": "Sy Pw", "CRPG": "Sy St", "Strategy RPG": "St Pw", "Tactical RPG": "St", "Party-Based RPG": "St Sy",
                "MMORPG": "Cm Pw", "Souls-like": "Ch", "Creature Collector": "Co Pw"},
        "dovus": {"Hack and Slash": "Ds Ex", "Beat 'em up": "Ds Ex", "Character Action Game": "Ex Ch", "Spectacle fighter": "Ex Ch", "Musou": "Pw Ds",
                  "Fighting": "Cp Ch", "2D Fighter": "Cp Ch", "3D Fighter": "Cp Ch", "Boss Rush": "Ch"},
        "kart_masa": {"Card Game": "St", "Card Battler": "St", "Trading Card Game": "St Co", "Board Game": "St Cm", "Tabletop": "St Cm", "Chess": "St Cp",
                      "Solitaire": "St", "Mahjong": "St", "Poker": "Cp St", "Pinball": "Ex", "Match 3": "Co", "Word Game": "St", "Trivia": "Cp",
                      "Logic": "St", "Sokoban": "St", "Falling Blocks": "Ch", "Spelling": "", "Dice": "St"},
        "strateji": {"Tower Defense": "St", "RTS": "St Cp", "Action RTS": "St Ex", "Turn-Based Strategy": "St", "Turn-Based Tactics": "St",
                     "Grand Strategy": "St", "Tactical": "St", "4X": "St Pw", "Wargame": "St", "Real Time Tactics": "St", "Auto Battler": "St", "MOBA": "Cp Cm"},
        "sim": {"City Builder": "De St", "Colony Sim": "St De", "God Game": "Pw De", "Management": "St", "Life Sim": "Fa De", "Farming Sim": "Co De",
                "Space Sim": "Di Fa", "Automobile Sim": "Fa", "Job Simulator": "Fa", "Medical Sim": "Fa", "Outbreak Sim": "St", "Political Sim": "St",
                "Hobby Sim": "Fa De", "Immersive Sim": "Di Fa", "Open World Survival Craft": "De Di", "Survival": "Ch", "Sandbox": "De Di",
                "Incremental": "Co Pw", "Idler": "Co Pw", "Flight": "Fa", "Shop Keeper": "St", "Desktop Companion": "", "Education": "",
                "Party Game": "Cm", "Rhythm": "Ch", "Minigames": "Ex"},
        "spor_yaris": {"Driving": "Ex", "Combat Racing": "Ex Ds", "Offroad": "Ex", "Motocross": "Ex", "Football (Soccer)": "Cp", "Football (American)": "Cp",
                       "Basketball": "Cp", "Baseball": "Cp", "Golf": "Ch", "Mini Golf": "Ch", "Tennis": "Cp", "Boxing": "Cp", "Wrestling": "Cp",
                       "Hockey": "Cp", "Billiards": "Ch", "Bowling": "Ch", "Skating": "Ch", "Skateboarding": "Ch", "Skiing": "Ch", "Snowboarding": "Ch",
                       "BMX": "Ch", "Cycling": "Ch", "Volleyball": "Cp", "Cricket": "Cp", "Rugby": "Cp", "Fishing": "Co", "Hunting": "Ch"},
    },
    "B_mekanik": {
        "anlati": {"Choices Matter": "Sy", "Multiple Endings": "Sy Co", "Dialogue Heavy": "Sy", "Dynamic Narration": "Sy", "Narrative": "Sy",
                   "Investigation": "Di", "Quick-Time Events": "Ex", "Exploration": "Di"},
        "uretim_yonetim": {"Crafting": "De Co", "Base Building": "De St", "Building": "De", "Resource Management": "St", "Automation": "St De",
                           "Economy": "St", "Trading": "St", "Time Management": "St Ch", "Inventory Management": "St", "Mining": "Co", "Farming": "Co",
                           "Agriculture": "Co", "Cooking": "De", "Decorating": "De", "Organizing": "Co", "Cleaning": "Co", "Diplomacy": "St",
                           "Programming": "De St", "Hacking": "St"},
        "dovus": {"Combat": "Ds", "Turn-Based Combat": "St", "Turn-Based": "St", "Real-Time": "Ex", "Real-Time with Pause": "St", "Loot": "Pw Co",
                  "Swordplay": "Ds", "Archery": "Ch", "Sniper": "Ch", "Vehicular Combat": "Ds", "Naval Combat": "St", "Bullet Time": "Ex",
                  "Gun Customization": "De Pw", "Destruction": "Ds", "Class-Based": "St Cm", "Stealth": "St Ch", "Parkour": "Ch Ex"},
        "yapi": {"Procedural Generation": "Di", "Music-Based Procedural Generation": "Di", "Perma Death": "Ch", "Character Customization": "De",
                 "Physics": "Di", "Grid-Based Movement": "St", "Hex Grid": "St", "Deckbuilding": "St", "Score Attack": "Cp Ch", "Time Attack": "Ch Cp",
                 "Time Manipulation": "Di", "Collectathon": "Co", "Level Editor": "De", "Typing": "Ch", "Gambling": "Ex", "Jump Scare": "Ex",
                 "Intentionally Awkward Controls": "Ch", "6DOF": "Ch"},
        "zorluk_tempo": {"Difficult": "Ch", "Fast-Paced": "Ex"},
    },
    "C_gorsel": {
        "boyut": {"2D": "", "3D": "", "2.5D": ""},
        "bakis": {"First-Person": "", "Third Person": "", "Top-Down": "", "Side Scroller": "", "Isometric": ""},
        "stil": {"Pixel Graphics": "", "Colorful": "", "Cute": "", "Stylized": "", "Cartoony": "", "Cartoon": "", "Realistic": "", "Minimalist": "",
                 "Hand-drawn": "", "Anime": "", "Abstract": "", "Retro": "", "Old School": "", "Voxel": "", "Cinematic": "", "Comic Book": "",
                 "Psychedelic": "", "FMV": "", "Text-Based": "", "Experimental": "Di"},
        "ses": {"8-bit Music": "", "Electronic Music": "", "Rock Music": "", "Instrumental Music": "", "Music": ""},
    },
    "D_tema": {
        "kurgu_turu": {"Fantasy": "Fa", "Sci-fi": "Fa Di", "Horror": "Ex", "Psychological Horror": "Ex Sy", "Mystery": "Di Sy", "Thriller": "Ex Sy",
                       "Dark Fantasy": "Fa", "Post-apocalyptic": "Fa", "Cyberpunk": "Fa", "Steampunk": "Fa", "Dystopian ": "Fa Sy", "Lovecraftian": "Sy",
                       "Noir": "Sy", "Western": "Fa", "Superhero": "Pw Fa", "Gothic": "Fa", "Alternate History": "Fa", "Crime": "Sy", "Detective": "Sy Di",
                       "Espionage": "Fa", "Heist": "St", "Wuxia": "Fa", "Xianxia": "Fa Pw", "Time Travel": "Sy"},
        "atmosfer": {"Atmospheric": "Fa", "Relaxing": "", "Cozy": "", "Wholesome": "", "Family Friendly": "", "Emotional": "Sy", "Dark": "",
                     "Surreal": "Di", "Psychological": "Sy", "Philosophical": "Sy", "Funny": "", "Comedy": "", "Dark Humor": "", "Dark Comedy": "",
                     "Satire": "", "Parody ": "", "Memes": "", "Story Rich": "Sy", "Lore-Rich": "Sy Di", "Romance": "Sy"},
        "donem_mekan": {"Space": "Di", "Futuristic": "Fa", "Medieval": "Fa", "Modern": "", "Historical": "Fa", "1990's": "", "1980s": "", "World War II": "Fa",
                        "World War I": "Fa", "Cold War": "Fa", "Rome": "Fa", "Nature": "Di", "Underwater": "Di", "Underground": "Di", "Snow": "",
                        "Mars": "Di", "War": "Ds", "Military": "Ds"},
        "varlik_nesne": {"Magic": "Fa Pw", "Zombies": "Ds", "Supernatural": "Fa", "Demons": "Fa", "Aliens": "Fa", "Mythology": "Fa Sy", "Dragons": "Fa",
                         "Vampires": "Fa", "Werewolves": "Fa", "Ninja": "Fa", "Pirates": "Fa", "Assassins": "Fa", "Mechs": "Pw", "Dinosaurs": "Fa",
                         "Robots": "Fa", "Cats": "", "Dogs": "", "Horses": "", "Animals": "", "Birds": "", "Foxes": "", "Wolves": "", "Capybaras": "",
                         "Zoo": "De", "Elves": "Fa", "Dwarves": "Fa", "Vikings": "Fa", "Samurai": "Fa", "Martial Arts": "Ch", "Naval": "Fa",
                         "Trains": "Fa", "Transportation": "St", "Sailing": "Di", "Submarine": "Di", "Spaceships": "Fa", "Tanks": "Ds", "Motorbike": "Ex",
                         "Bikes": "Ex", "ATV": "Ex", "Artificial Intelligence": "Sy", "Transhumanism": "Sy", "Science": "Di", "Faith": "Sy",
                         "Conspiracy": "Sy", "Cult": "Sy", "Capitalism": "St", "Gaming": ""},
        "karakter": {"Female Protagonist": "Fa", "Silent Protagonist": "", "Villain Protagonist": "Fa", "LGBTQ+": ""},
        "icerik_uyarisi": {"Sexual Content": "", "Nudity": "", "Hentai": "", "Gore": "Ds", "Violent": "Ds"},
    },
    "E_oyuncu": {
        "tek_cok": {"Singleplayer": "", "Multiplayer": "Cm", "Massively Multiplayer": "Cm"},
        "isbirligi": {"Co-op": "Cm", "Online Co-Op": "Cm", "Local Co-Op": "Cm", "Co-op Campaign": "Cm", "PvE": "Cm"},
        "rekabet": {"PvP": "Cp", "Competitive": "Cp", "eSports": "Cp", "Team-Based": "Cm Cp", "Social Deduction": "Cm Cp", "Asymmetric VR": "Cm"},
        "yerel_parti": {"Local Multiplayer": "Cm", "4 Player Local": "Cm", "Split Screen": "Cm", "Party": "Cm"},
        "asenkron": {"Asynchronous Multiplayer": "Cm"},
    },
    "F_kapsam": {
        "yapi": {"Open World": "Di", "Linear": "Sy", "Nonlinear": "Di", "Episodic": "Sy"},
        "uzunluk": {"Short": ""},
    },
    "H_teknik": {
        "erisim": {"VR": "Fa", "Controller": "", "Mouse Only": "", "Touch-Friendly": "", "Voice Control": "", "TrackIR": "", "Moddable": "De"},
    },
    "X_degerlendirme": {
        "yargi": {"Great Soundtrack": "", "Beautiful": "", "Addictive": "", "Classic": "", "Epic": "", "Immersive": "", "Replay Value": "",
                  "Nostalgia": ""},
    },
    "X_uygulama": {
        "yazilim": {"Software": "", "Utilities": "", "Design & Illustration": "", "Animation & Modeling": "", "Audio Production": "",
                    "Video Production": "", "Photo Editing": "", "Software Training": "", "Game Development": "", "Benchmark": "", "Hardware": "",
                    "360 Video": "", "Language Learning": "", "Soundtrack": ""},
    },
    "X_meta": {
        "dagitim": {"Indie": "", "Early Access": "", "Free to Play": "", "Tutorial": "", "Sequel": "", "Remake": "", "Reboot": "",
                    "Based On A Novel": "", "Mod": ""},
    },
}  # fmt: skip


def main() -> None:
    e = pd.read_parquet(INTERIM / "oyun_etiket.parquet")
    kohort = pd.read_parquet(INTERIM / "oznitelik.parquet", columns=["appid", "kohort"])
    ek = e[e.appid.isin(kohort.appid[kohort.kohort])]
    say = ek.groupby(["tagid", "ad"]).appid.nunique().reset_index(name="kohort_oyun")
    rows, gorulen = [], {}
    for boyut, gruplar in T.items():
        for alt, etiketler in gruplar.items():
            for ad, mot in etiketler.items():
                assert ad not in gorulen, f"iki kez eşlendi: {ad} ({gorulen[ad]} ve {boyut})"
                gorulen[ad] = boyut
                kod = mot.split()
                assert len(kod) <= 2 and all(k in M for k in kod), f"motivasyon hatalı: {ad} → {mot}"
                rows.append({"ad": ad, "boyut": boyut, "alt_grup": alt, "motivasyon": ";".join(M[k] for k in kod)})
    t = pd.DataFrame(rows)
    eksik = sorted(set(say.ad) - set(t.ad))
    fazla = sorted(set(t.ad) - set(say.ad))
    assert not eksik, f"eşlenmemiş etiket: {eksik}"
    assert not fazla, f"veride olmayan etiket: {fazla}"
    t = say.merge(t, on="ad").assign(kodlayici="claude_taslak").sort_values(["boyut", "alt_grup", "kohort_oyun"], ascending=[True, True, False])
    yol = KOK / "data" / "referans" / "etiket_taksonomi.csv"
    t[["tagid", "ad", "boyut", "alt_grup", "motivasyon", "kohort_oyun", "kodlayici"]].to_csv(yol, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"[ok] {len(t)} etiket → {yol.relative_to(KOK)}")
    print(t.groupby("boyut").agg(etiket=("ad", "size"), kohort_kullanim=("kohort_oyun", "sum")).to_string())
    print(f"motivasyonu olan etiket: {(t.motivasyon != '').sum()}")


if __name__ == "__main__":
    main()
