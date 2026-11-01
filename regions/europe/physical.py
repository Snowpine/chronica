"""Europe's rivers and mountain ranges for scripts/build_physical.py, by their Natural Earth names.

All lakes in the map window are drawn; display names live in locales/<lang>.json under "rivers" and "ranges"."""

# river labels go on the part of the river inside this box (west, south, east, north), well inside the frame
RIVER_LABEL_BOX = (-12, 30, 50, 66)

RIVERS = {  # label key (English) -> Natural Earth segment names; display names live in locales/<lang>.json "rivers"
    "Danube": ["Danube", "Donau", "Soroksari Duna"], "Rhine": ["Rhine", "Rhein", "Rhin"], "Elbe": ["Elbe"],
    "Oder": ["Oder"], "Vistula": ["Vistula"], "Dnieper": ["Dnipro", "Dnepre"], "Dniester": ["Dniester"],
    "Don": ["Don"], "Volga": ["Volga"], "Seine": ["Seine"], "Loire": ["Loire"], "Rhône": ["Rhône", "Rhne"],
    "Garonne": ["Garonne"], "Thames": ["Thames"], "Po": ["Po"], "Tagus": ["Tajo", "Tejo"], "Ebro": ["Ebro"],
    "Douro": ["Duero"], "Daugava": ["Daugava"], "Neman": ["Neman"], "Nile": ["Nile"],
    "Euphrates": ["Euphrates", "Firat", "Al Furat"], "Tigris": ["Tigris", "Dicle"], "Tisza": ["Tisa"],
    "Northern Dvina": ["Severnaya Dvina"], "Weser": ["Weser"], "Sava": ["Sava"], "Tiber": ["Tevere"],
    "Prut": ["Prut"], "Marne": ["Marne"], "Meuse": ["Maas"], "Vltava": ["Vltava"], "Main": ["Main"],
    "Bug": ["Bug"], "Guadalquivir": ["Guadalquivir"], "Kama": ["Kama"], "Oka": ["Oka"],
    "Kuban": ["Kuban"], "Drava": ["Drau"], "Moselle": ["Mosel"], "Guadiana": ["Guadiana"],
}
# smaller rivers drawn although Natural Earth ranks them minor (scalerank above 7)
EXTRA = {"Main", "Bug", "Guadalquivir", "Maas", "Marne", "Vltava", "Warta", "Inn", "Adige", "Schelde", "Severn",
         "Shannon", "Drina", "Kura", "Aras"}

# Natural Earth NAME -> (label key or "" for an unlabelled shape, label rank: 1 shows first);
# display names live in locales/<lang>.json "ranges"
RANGES = {
    "ALPS": ("Alps", 1), "URAL MOUNTAINS": ("Ural Mountains", 1), "CAUCASUS MTS.": ("Caucasus", 1),
    "ZAGROS MOUNTAINS": ("Zagros Mountains", 2), "ATLAS MOUNTAINS": ("Atlas Mountains", 2), "ATLAS SAHARIEN": ("", 3),
    "HAUT ATLAS": ("", 3), "Anti Atlas": ("", 4), "Moyen Atlas": ("", 5), "Er Rif": ("", 5), "Atlas Tellien": ("", 5),
    "ELBURZ MTS.": ("Alborz", 3), "KJØLEN MOUNTAINS": ("Scandinavian Mountains", 2),
    "CARPATHIAN MOUNTAINS": ("Carpathians", 2), "APPENNINI": ("Apennines", 2), "PYRENEES": ("Pyrenees", 2),
    "Lesser Caucasus": ("", 4), "PONTIC MOUNTAINS": ("Pontic Mountains", 3), "Balkan Mts.": ("Balkan Mountains", 3),
    "Dinaric Alps": ("Dinaric Alps", 3), "Cord. Cantábrica": ("Cantabrian Mountains", 4), "S. Nevada": ("Sierra Nevada", 4),
    "Sierra Morena": ("Sierra Morena", 4), "Taurus Mts.": ("Taurus Mountains", 3), "Transylvanian Alps": ("", 4),
    "Tatra Mts.": ("", 5), "Pindus Mts.": ("Pindus", 4), "Calabria": ("", 5), "Harz": ("Harz", 5),
    "Vosges": ("Vosges", 5), "Sudetes Mts.": ("Sudetes", 4), "Erzgebirge": ("Ore Mountains", 5),
    "Ardennes": ("Ardennes", 4), "Jura": ("Jura", 5), "Böhmerwald": ("Bohemian Forest", 5),
    "Grampian Mts.": ("Grampians", 4), "Cambrian Mts.": ("Cambrian Mountains", 5), "Lebanon Mts.": ("Mount Lebanon", 4),
}
