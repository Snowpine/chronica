"""China's rivers and mountain ranges for scripts/build_physical.py, by their Natural Earth names.

All lakes in the map window are drawn; display names live in locales/<lang>.json under "rivers" and "ranges"."""

# river labels go on the part of the river inside this box (west, south, east, north), well inside the frame
RIVER_LABEL_BOX = (72, 14, 140, 53)

RIVERS = {  # label key (English) -> Natural Earth segment names; display names live in locales/<lang>.json "rivers"
    "Yellow River": ["Huang"], "Yangtze": ["Chang Jiang", "Yangtze"], "Huai": ["Huai"], "Wei": ["Wei"],
    "Han": ["Han"], "Pearl River": ["Xi"], "Gan": ["Gan"], "Xiang": ["Xiang"], "Jialing": ["Jialing"],
    "Hai": ["Hai"], "Qiantang": ["Fuchun"], "Liao": ["Liao", "Xiliao"], "Songhua": ["Songhua", "Di’er Songhua"],
    "Amur": ["Amur", "Heilong Jiang"], "Ussuri": ["Ussuri"], "Yalu": ["Yalu"], "Nakdong": ["Nakdong"],
    "Tarim": ["Tarim"], "Ili": ["Ile"], "Irtysh": ["Irtysh", "Ertis", "Ertix"], "Selenga": ["Selenga"],
    "Orkhon": ["Orhon"], "Onon": ["Onon"], "Angara": ["Angara"], "Amu Darya": ["Amu  Darya", "Panj"],
    "Syr Darya": ["Syr  Darya", "Naryn"], "Indus": ["Indus"], "Ganges": ["Ganges"],
    "Yarlung Tsangpo": ["Yarlung"], "Brahmaputra": ["Brahmaputra", "Dihang"], "Irrawaddy": ["Ayeyarwady"],
    "Salween": ["Salween", "Nu"], "Mekong": ["Mekong", "Lancang"], "Red River": ["Hong", "Yuan"],
    "Chao Phraya": ["Chao Phraya"],
}
# smaller rivers drawn although Natural Earth ranks them minor (scalerank above 7)
EXTRA = {"Wei", "Jing", "Luan", "Shandian", "Nen", "Di’er Songhua", "Yalu", "Nakdong", "Orhon", "Onon"}

# Natural Earth NAME -> (label key or "" for an unlabelled shape, label rank: 1 shows first);
# display names live in locales/<lang>.json "ranges"
RANGES = {
    "HIMALAYAS": ("Himalayas", 1), "TIAN SHAN": ("Tian Shan", 1), "KUNLUN MOUNTAINS": ("Kunlun Mountains", 2),
    "KARAKORAM RA.": ("Karakoram", 2), "PAMIRS": ("Pamirs", 2), "HINDU KUSH": ("Hindu Kush", 2),
    "ALTAY MOUNTAINS": ("Altai Mountains", 2), "GREATER KHINGAN RANGE": ("Greater Khingan", 2),
    "QUILIAN MOUNTAINS": ("Qilian Mountains", 2), "Qinling Mountains": ("Qinling Mountains", 2),
    "ALTUN MTS.": ("Altyn-Tagh", 3), "Taihang Mts.": ("Taihang Mountains", 3), "Yin Mts.": ("Yin Mountains", 3),
    "Nan Ling Mts.": ("Nanling Mountains", 3), "Hangayn Mts.": ("Khangai Mountains", 3),
    "EASTERN SAYAN MTS.": ("Sayan Mountains", 3), "STANOVOY RANGE": ("Stanovoy Range", 3),
    "CHAÎNE ANNAMITIQUE": ("Annamite Range", 3), "WESTERN GHATS": ("Western Ghats", 3),
    "Lüliang Mts.": ("Lüliang Mountains", 4), "Dabie Mts.": ("Dabie Mountains", 4), "Wuyi Mts.": ("Wuyi Mountains", 4),
    "Hentiyn Mts.": ("Khentii Mountains", 4), "Lesser Khingan Range": ("Lesser Khingan", 4),
    "SIKHOTE-ALIN’ RANGE": ("Sikhote-Alin", 4), "Dalou Mts.": ("", 4), "Hamgyong Mts.": ("", 4),
    "Western Sayan Mts.": ("", 4), "YABLONOVYY RANGE": ("", 4), "Siwalik Hills": ("", 4), "Arakan Yoma": ("", 4),
    "Sulaiman Ra.": ("", 4), "EASTERN GHATS": ("", 4), "Vindhya Range": ("", 4), "Tannu-Ola Ra.": ("", 5),
    "Borohoro Mts.": ("", 5), "Alataw Mts.": ("", 5), "Tarbagatay Ra.": ("", 5), "Chin Hills": ("", 5),
    "Naga Hills": ("", 5), "Khasi Hills": ("", 5), "Central Highlands": ("", 5), "Dângrêk Ra.": ("", 5),
    "Paropamisus Ra.": ("", 5), "Karatau Range": ("", 5), "Bureinskiy Ra.": ("", 5), "Yam Alin’ Range": ("", 5),
    "Dzhugdzhur Range": ("", 5), "Satpura Range": ("", 5), "Arvalli Ra.": ("", 5), "Southern Ghats": ("", 5),
}
