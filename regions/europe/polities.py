"""Europe's polity tables for scripts/build.py: which historical-basemaps snapshots to use and how to read them.

Names are keyed by the source NAME. Display names for every language live in locales/<lang>.json under "names";
a few names change with the year (Germany 1914 vs 1938) and get a variant key such as "Germany|weimar".
Lineage ids must match the "lineages" in region.json, which gives each one its colour and timeline lane.
"""

# the historical-basemaps snapshots used; negative years are BC (-500 = 500 BC, file world_bc500.geojson)
YEARS = [-700, -500, -400, -323, -300, -200, -100, -1, 100, 200, 300, 400, 500, 600, 700, 800, 900,
         1000, 1100, 1200, 1279, 1300, 1400, 1492, 1500, 1530, 1600, 1650, 1700, 1715, 1783, 1800, 1815,
         1878, 1880, 1900, 1914, 1920, 1930, 1938, 1945, 1960, 1994, 2000]


# Lineage = a colour family that persists across renamings (and drives the timeline lanes). Dependencies whose overlord
# belongs to a lineage are drawn in a paler shade of its colour.
LINEAGE_NAMES = {
    "greek": ["Greek city-states", "Greek colonies", "Macedon and Hellenic League", "Empire of Alexander",
              "Kingdom of Antigonus", "Kingdom of Kassander", "Kingdom of Lysimachus", "Seleucid Kingdom",
              "Ptolemaic Kingdom"],  # the Greek world and Alexander's successor kingdoms
    "rome": ["Roman Republic", "Roman Empire", "Western Roman Empire", "Eastern Roman Empire", "Byzantine Empire"],
    "persia": ["Achaemenid Empire", "Parthia", "Parthian Empire", "Sasanian Empire", "Safavid Empire", "Persia", "Iran"],
    "franks": ["Franks", "Frankish Kingdom", "Carolingian Empire", "Middle Francia"],
    "russia": ["Principality of Vladimir-Suzdal", "Grand Duchy of Moscow", "Tsardom of Muscovy", "Russian Empire",
               "USSR", "Russia"],
    "ottoman": ["Ottoman Empire", "Ottoman Sultanate", "Republic of Turkey", "Turkey"],
    "mongol": ["Mongol Empire", "Khanate of the Golden Horde", "Golden Horde", "Blue Horde", "White Horde",
               "Ilkhanate", "Chagatai Khanate"],
    "hre": ["East Francia", "Holy Roman Empire"],
    "germany": ["Brandenburg", "Prussia", "German Empire", "Germany", "East Prussia", "West Germany", "East Germany"],
    "austria": ["Austrian Empire", "Austria Hungary", "Austro-Hungarian Empire", "Austria", "Habsburg Austria"],
    "france": ["West Francia", "Kingdom of France", "France"],
    "britain": ["Wessex", "England", "English territory", "Angevin Empire", "England and Ireland", "United Kingdom",
                "United Kingdom of Great Britain and Ireland"],
    "spain": ["Castilla", "Castile", "Castille", "Spain", "Spanish Habsburg", "Habsburg Netherlands"],
    "italy": ["Savoy", "Sardinia-Piedmont", "Kingdom of Sardinia", "Kingdom of Italy", "Italy", "Savoy-Piedmont"],
    "poland": ["Poland", "Poland-Lithuania", "Polish–Lithuanian Commonwealth"],
    "sweden": ["Swedes", "Swedes and Goths", "Sweden", "Sweden–Norway"],
    "denmark": ["Danes", "Denmark", "Denmark-Norway", "Kalmar Union"],
}
# overlord strings that appear in SUBJECTO but differ from a polity name
OVERLORD_LINEAGES = {"UK": "britain", "Austria": "austria", "Russia": "russia", "Habsburg Austria": "austria"}


# Identity = what counts as "the same state" when diffing snapshots (renamings are not territorial change).
IDENTITY_GROUPS = {
    "greeks": ["Greek city-states", "Greek colonies"],
    "macedon": ["Empire of Alexander", "Kingdom of Kassander", "Macedon and Hellenic League"],
    "rome": ["Roman Republic", "Roman Empire", "Western Roman Empire"],
    "byzantine": ["Eastern Roman Empire", "Byzantine Empire"],
    "persia": ["Parthia", "Parthian Empire", "Sasanian Empire", "Safavid Empire", "Persia", "Iran"],
    "franks": ["Franks", "Frankish Kingdom", "Carolingian Empire", "Middle Francia"],  # Middle Francia kept the imperial title
    "carthage": ["Carthaginian Empire", "Carthage"],
    "numidia": ["Kingdom of Syphax", "Numidia"],
    "dacia": ["Dacians", "Dacia"],
    "bosporus": ["Bosporan Kingdom", "Bosporian Kingdom"],
    "visigoths": ["Visigoths", "Visigothic Kingdom"],
    "lombards": ["Lombard principalities", "Lombard duchies"],
    "dumnonia": ["Dumonii", "Dumnonia"],
    "kent": ["Cantia", "Kent"],
    "brittany": ["Armorica", "Broërec", "Britany"],
    "norse": ["Norsemen", "Northmen"],
    "moravia": ["Moravians", "Great Moravia"],
    "bulgaria": ["Danube Bulgars", "Bulgar Khanate"],  # the First Bulgarian Empire
    "leon": ["Asturias", "León"],
    "cordoba": ["Emirate of Córdoba", "Caliphate of Córdoba"],
    "croatia": ["Croatian kingdom", "Croatia"],
    "norway": ["Kingdom of Norway", "Norway"],
    "pechenegs": ["Pechenegs", "Peshemegs"],
    "france": LINEAGE_NAMES["france"],
    "britain": LINEAGE_NAMES["britain"],
    "spain": ["Castilla", "Castile", "Castille", "Spain"],
    "hre": LINEAGE_NAMES["hre"],
    "prussia": ["Brandenburg", "Prussia"],
    "germany": ["German Empire", "Germany", "West Germany"],
    "austria": LINEAGE_NAMES["austria"],
    "italy": LINEAGE_NAMES["italy"],
    "ottoman": LINEAGE_NAMES["ottoman"],
    "russia": ["Grand Duchy of Moscow", "Tsardom of Muscovy", "Russian Empire", "USSR", "Russia"],
    "poland": LINEAGE_NAMES["poland"],
    "sweden": LINEAGE_NAMES["sweden"],
    "denmark": LINEAGE_NAMES["denmark"],
    "hungary": ["Magyars", "Hungary", "Kingdom of Hungary", "Imperial Hungary"],
    "golden_horde": ["Khanate of the Golden Horde", "Golden Horde"],
    "kyivan_rus": ["Rus' Khaganate", "Kyivan Rus", "Kievan Rus"],
    "sami": ["Saami", "Sami", "Samis", "Sámi"],
    "uk_ireland": [],
    "algeria": ["Algeria", "Algeria (FR)", "Algeria (France)"],
    "morocco": ["Morocco", "Morocco (France)", "Wattasid Caliphate", "Watassid Morocco"],
    "libya": ["Libya", "Libya (IT)"],
    "novgorod": ["Novgorod", "Principality of Novgorod"],
    "belarus": ["White Russia", "Byelarus"],
    "tuareg": ["Touareg", "Tuareg Nomadic Tribes"],
    "zayyanid": ["Zayyanid Caliphate", "Abdelouadides"],
    "netherlands": ["Dutch Republic", "Batavian Republic", "Netherlands", "United Kingdom of Netherlands"],
    "switzerland": ["Swiss Confederation", "Helvetic Republic", "Switzerland"],
    "two_sicilies": ["Naples", "Kingdom of the Two Sicilies"],
    "tuscany": ["Florence", "Tuscany"],  # the Grand Duchy of Tuscany grew out of the Florentine state
    "milan": ["Milan", "Milano (Austria)"],
    "georgia": ["Georgian Kingdom", "Kingdom of Georgia", "Georgia"],
    "rus": ["Other Rus Principalities", "Rus Principalities"],
    "western_sahara": ["Spanish Sahara", "Western Sahara"],
}

# Source labels that are wrong for a snapshot: NAME -> [(test(year), corrected NAME)], first match wins.
RENAMES = {
    "Rome": [(lambda y: y < -27, "Roman Republic"), (lambda y: True, "Roman Empire")],
    # the 300 layer splits the empire among the four tetrarchs; drawn here as one empire
    **{f"Rome ({t})": [(lambda y: True, "Roman Empire")] for t in ("Maximian", "Diocletianus", "Constantinus", "Galerius")},
    "Parthian Empire": [(lambda y: y > 224, "Sasanian Empire")],  # the Sasanians replaced the Parthians in 224
    "Persia": [(lambda y: y < 700, "Sasanian Empire")],
    "Sasanian Empire": [(lambda y: y > 651, "Umayyad Caliphate")],  # the 700 layer still shows Iran as Sasanian
    "Bulgars": [(lambda y: y in (800, 900), "Danube Bulgars")],  # the First Bulgarian Empire; earlier "Bulgars" are on the steppe
    "Western Roman Empire": [(lambda y: y > 476, "Brittonic kingdoms")],  # the 500 layer's name for post-Roman western Britain
    "Carolingian Empire": [(lambda y: y > 843, "Middle Francia")],  # what was left after the Treaty of Verdun
    "Hittites": [(lambda y: y == -700, "Neo-Hittite states")],
    "Kingdom of David and Solomon": [(lambda y: y == -700, "Kingdom of Judah")],  # Israel fell to Assyria in 722 BC
    "White Russia": [(lambda y: y == 1930, "USSR")],  # the 1930 layer labels the whole Soviet Union "White Russia"
    "Luxembourg": [(lambda y: y in (1650, 1700), "Habsburg Netherlands")],  # the polygon is the whole Spanish Netherlands
    "Buwayhid Emirates": [(lambda y: y == 1200, "Khwarazmian Empire")],  # the Buyids fell in 1062
    "Ryazan": [(lambda y: y in (1279, 1300), "Rus Principalities")],  # one polygon for most of Rus under the Horde
    "Venetia": [(lambda y: y < 1797, "Venice")],  # still the Republic of Venice
    "Western Sahara": [(lambda y: y < 1976, "Spanish Sahara")],
    "Raška": [(lambda y: True, "Serbia")],  # the 1300 layer's name for the Serbian kingdom
}
# polygons named after the group they belong to (PARTOF) rather than their own label
GROUP_RENAMES = {"Baltic archeological cultures": "Baltic tribes"}
# source polygons that are not polities at all; they are dropped
NOT_POLITIES = {"Lake Segozerskoye", "Lake Vygozero"}  # the 700 layer draws two Karelian lakes as polities
# misspelt overlords (SUBJECTO): source spelling -> NAME
OVERLORD_RENAMES = {"Persi": "Persia"}  # the 400 layer makes Persia a dependency of "Persi"

# Peoples, tribes and archaeological cultures rather than states: drawn pale, and their spread between snapshots
# (often just the source mapping them in one year and not the next) is not counted as a territorial change.
PEOPLES = {
    "Urnfield cultures", "N. European Bronze Age cultures", "Lusatian culture", "Chernoles culture", "Milograd culture",
    "La Tène culture", "Hallstatt culture", "Karasuk culture", "Proto-Scythian culture",
    "Finno-Ugric taiga hunter-gatherers", "Paleo-Siberian hunter-gatherers", "Saharan pastoral nomads",
    "Saharan Nomadic Tribes", "Arabian pastoral nomads", "Iranian pastoralists", "Tuaregs", "Tuareg Nomadic Tribes",
    "Touareg", "Bedouins", "Arabs", "Berbers", "Berber Tribes", "Saami", "Sami", "Samis", "Sámi", "Guanches",
    "Celts", "Germanic tribes", "Scythians", "Sarmates", "Cimerians", "Illyrians", "Norsemen", "Northmen",
    "Proto-Slavs", "Slavs", "Slavic tribes", "Slavonic tribes", "Baltic tribes", "Balts", "Finns", "Karelians", "Veps",
    "Permians", "Mari", "Mordvinians", "Bashkirs", "Chuds", "Ests", "Kryvichs", "Severians", "Polanes", "Polyanians",
}

# year-dependent display names: NAME -> [(test(year), tag)], first match wins
VARIANTS = {
    "Tsardom of Muscovy": [(lambda y: y < 1547, "early")],
    "Austrian Empire": [(lambda y: y < 1804, "habsburg")],
    "United Kingdom": [(lambda y: y < 1801, "great-britain")],
    "Germany": [(lambda y: y <= 1914, "empire"), (lambda y: y <= 1930, "weimar"), (lambda y: y == 1938, "nazi")],
    "Moldova": [(lambda y: y < 1900, "moldavia")],
    "Israel": [(lambda y: y < 1948, "mandate")],
    "Kingdom of the Two Sicilies": [(lambda y: y < 1816, "naples")],
}


# geometry fixes, applied by scripts/build.py:
# unnamed source polygons that are really a known state: (years, a point inside it, NAME)
UNNAMED = [((1994, 2000), (7.45, 46.95), "Switzerland")]  # the source draws Switzerland as a sliver in these years
# polygons that swallow a neighbour: (year, NAME, neighbour NAME, a year whose outline of the neighbour is used);
# the part inside that outline goes back to the neighbour
REASSIGN = [(1530, "Astrakhan Khanate", "Georgia", 1500)]  # the 1530 layer stretches Astrakhan over Georgia
