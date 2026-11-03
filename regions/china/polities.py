"""China's polity tables for scripts/build.py: which historical-basemaps snapshots to use and how to read them.

Names are keyed by the source NAME. Display names for every language live in locales/<lang>.json under "names";
a few names change with the year (Western and Eastern Han) and get a variant key such as "Han|eastern".
Lineage ids must match the "lineages" in region.json, which gives each one its colour and timeline lane.

The source is coarse for China: it lumps the Zhou states together, misses whole dynasties and has no snapshot for
key years. The snapshots marked "redrawn" below are built from a nearby source layer (BASE), with borders drawn here
as lines (SPLIT) and areas moved between polities (CUT). Those borders are approximate, at the scale of the map; where a
border followed the Huai, the Yangtze or the Yellow River, it is drawn along the river (along()).
"""
from shapely.geometry import LineString, Point
from shapely.ops import substring

# the snapshots used; negative years are BC (-500 = 500 BC, file world_bc500.geojson).
# Redrawn: -1750, -1500, -1250, -1000, -800, -700, -650, -600, -500, -453, -350, -300, -260, -221, 262, 280, 320, 360, 383, 400, 420, 439, 500, 540, 560, 580, 589, 742, 910, 926, 938,
# 950, 958, 970, 1142, 1279, 1400, 1500, 1600, 1650 (and 1949).
# Left out: 1200 (Liao still stands, no Jin;
# 1142 replaces it), 1300 (= 1279), 1530 (= 1600), 1700 (keeps the Southern Ming, which ended in 1662), 1880 (= 1900).
YEARS = [-1750, -1500, -1250, -1000, -800, -700, -650, -600, -500, -453, -350, -300, -260, -221, -200, -100, -1, 100, 200, 262, 280, 320, 360, 383, 400, 420, 439, 500, 540, 560, 580,
         589, 700, 742, 800, 900, 910,
         926, 938, 950, 958, 970, 1000, 1100, 1142, 1279, 1400, 1500, 1600, 1650, 1715, 1800, 1900, 1914, 1920, 1930, 1938, 1945, 1949, 1960,
         2000]
# For now the timeline ends with the Qing (region.json "end"); the later snapshots stay listed above for when it is
# extended, and 2000 gives the "today's borders" layer.
YEARS = [y for y in YEARS if y < 1912]
MODERN = 2000
# snapshots built from another year's historical-basemaps file: year -> source year
BASE = {-1750: -1000, -1500: -1000, -1250: -1000, -800: -1000, -650: -500, -600: -500, -453: -400, -350: -400, -260: -300, -221: -200, 262: 200, 280: 300, 320: 300, 360: 300, 383: 400, 420: 400, 439: 500, 540: 600, 560: 600, 580: 600,
        589: 600,
        742: 700, 910: 1000, 926: 1000, 938: 1000, 950: 1000, 958: 1000, 970: 1000,
        1142: 1200, 1949: 1960}


# Lineage = a colour family that persists across renamings (and drives the timeline lanes). Dependencies whose overlord
# belongs to a lineage are drawn in a paler shade of its colour.
LINEAGE_NAMES = {
    # the orthodox line of dynasties; in times of division it runs through Wei, the Jin and the Southern dynasties,
    # the Five Dynasties and the Song
    "china": ["Xia (Erlitou)", "Shang", "Western Zhou", "Eastern Zhou", "Qin Empire", "Han", "Cao Wei", "Jin", "Liu Song", "Southern Qi", "Liang (Xiao)",
              "Chen", "Sui Empire",
              "Tang Empire", "Later Liang", "Later Tang", "Later Jin", "Later Han", "Later Zhou",
              "Song Empire", "Great Khanate", "Ming Chinese Empire", "Qing Empire",
              "Republic of China", "China"],
    # dynasties founded by northern peoples that held north China without uniting it
    # only those that held all or most of the north, so that neighbouring northern states keep distinct colours
    "north": ["Later Zhao", "Former Qin", "Toba Wei", "Khitans", "Liao", "Jurchen Jin"],
    "steppe": ["Xiongnu", "Ruanruan", "Göktürks", "Western Gokturk Khaganate", "Uyghurs", "Mongol Empire",
               "Chagatai Khanate", "Moghulistan", "Northern Yuan", "Khalkha", "Oirat Confederation", "Dzungar Khanate",
               "Mongolia"],
    "tibet": ["Zhangzhung Kingdom", "Tibetan Empire", "Tibet"],
    "korea": ["Gojoseon", "Silla", "Goryeo", "Korea", "Korea, Republic of", "Korea, Democratic People's Republic of"],
    "japan": ["Yamato", "Japan", "Imperial Japan (Fujiwara)", "Shogun Japan (Kamakura)", "Japan (Muromachi)",
              "Japan (Warring States)", "Tokugawa shogunate", "Imperial Japan", "Empire of Japan", "Japan (USA)"],
    "vietnam": ["Annam", "Đại Việt", "Vietnam"],
    "russia": ["Tsardom of Muscovy", "Russian Empire", "USSR", "Russia"],
}
# overlord strings that appear in SUBJECTO but differ from a polity name
OVERLORD_LINEAGES = {"Russia": "russia"}


# Identity = what counts as "the same state" when diffing snapshots (renamings are not territorial change).
# Following the traditional (orthodox) division of Chinese history, every dynasty is a state of its own, so a change
# of dynasty shows as land changing hands; the halves of one dynasty (Western and Eastern Han, Jin, Song) are one state.
IDENTITY_GROUPS = {
    "zhou": ["Zhou (pre-dynastic)", "Western Zhou", "Eastern Zhou"],  # the Zhou before the conquest, and its two halves
    "qin": ["Qin", "Qin Empire"],  # the state of Qin and the Qin dynasty
    "yuan": ["Great Khanate"],
    "northern_yuan": ["Northern Yuan", "Khalkha"],  # the Yuan court in Mongolia after 1368
    "qing": ["Qing Empire"],
    "roc": ["Republic of China"],
    "liao": ["Khitans", "Liao"],
    "xia": ["Dingnan", "Xixia"],
    "nanzhao": ["Nanzhao", "Dachanghe", "Dayining", "Dali"],
    "chagatai": ["Chagatai Khanate", "Moghulistan"],
    "oirats": ["Oirat Confederation", "Dzungar Khanate"],
    "korea": ["Silla", "Goryeo", "Korea"],  # Goryeo absorbed Silla in 935; Joseon replaced Goryeo in 1392
    "japan": LINEAGE_NAMES["japan"],
    "vietnam": LINEAGE_NAMES["vietnam"],
    "russia": LINEAGE_NAMES["russia"],
}

# Source labels that are wrong for a snapshot, or spelt differently from one snapshot to the next:
# NAME -> [(test(year), corrected NAME)], first match wins.
always = lambda y: True
RENAMES = {
    # the 1000 BC layer (also the base of the Xia and Shang snapshots) lumps the Zhou states and Wu together; before
    # the Zhou conquest the block is the peoples of the Chinese sphere, in which the Xia and Shang are drawn
    "Zhoa": [(lambda y: y < -1046, "Sinic"), (always, "Zhou states")],
    "Wu": [(lambda y: y < -1046, "Sinic")],
    "Han Empire": [(lambda y: y < -206, "Qin Empire"), (always, "Han")],  # VARIANTS tells Western from Eastern Han
    "Han": [(lambda y: 220 < y < 266, "Cao Wei")],
    # Emperor Wu conquered Nanyue in 111 BC and Minyue in 110 BC; the -100 layer still has both
    "Nan-Yue": [(lambda y: y < -204, "Baiyue"), (lambda y: y > -111, "Han")],
    "Min-Yue": [(lambda y: y < -204, "Baiyue"), (lambda y: y > -110, "Han")],
    "Sixteen Kingdoms": [(lambda y: y == 383, "Former Qin")],  # the Former Qin had united the north in 376
    "Northern Liang": [(lambda y: y == 383, "Former Qin")],
    "Jin Empire": [(lambda y: y < 479, "Liu Song"), (lambda y: y < 502, "Southern Qi")],  # the 500 layer's south
    # the 600 layer's Sui is the base of the Northern and Southern dynasties snapshots; the 700 layer still calls the
    # Tang "Sui"
    "Sui Empire": [(lambda y: y < 550, "Eastern Wei"), (lambda y: y < 577, "Northern Qi"), (lambda y: y < 581, "Northern Zhou"),
                   (lambda y: y > 618, "Tang Empire")],
    "Göktürks": [(lambda y: y < 552, "Ruanruan")],  # the Turks overthrew the Rouran in 552
    "Ruanruan": [(lambda y: y < 402, "Rouran tribes")],  # the Rouran khaganate dates from 402
    "Jin": [(lambda y: 419 < y < 479, "Liu Song")],  # the 400 layer's Jin, as the base of 420
    # the 300 layer's Han Zhao covers the Ordos and Shengle, the Tuoba capital; Liu Yuan rose in 304
    "Han Zhao": [(lambda y: y < 304, "Jin"), (lambda y: y > 310, "Dai")],
    "Western Gokturk Khaganate": [(lambda y: y > 704, "Türgesh")],
    "Sasanian Empire": [(lambda y: y > 651, "Umayyad Caliphate")],  # the 700 layer still has the Sasanians
    "Yamato": [(lambda y: y > 701, "Japan")],
    # the Five Dynasties snapshots start from the Song of the 1000 layer
    "Song Empire": [(lambda y: y < 923, "Later Liang"), (lambda y: y < 936, "Later Tang"), (lambda y: y < 947, "Later Jin"),
                    (lambda y: y < 951, "Later Han"), (lambda y: y < 960, "Later Zhou")],
    "Xixia": [(lambda y: y < 1038, "Dingnan")],  # the Tangut Xia before it took the imperial title
    "Liao": [(lambda y: y < 916, "Khitans"), (lambda y: y > 1125, "Jurchen Jin")],  # the 1200 layer still has the Liao, which fell in 1125
    "Mongol Empire": [(lambda y: y < 1206, "Mongols")],
    "Sultanate of Delhi": [(lambda y: y < 1206, "Rajput kingdoms")],
    "Buyid dynasty": [(lambda y: y < 1200, "Seljuk Empire")],
    "Paekche": [(lambda y: y > 660, "Silla")],  # Baekje fell to Silla and the Tang in 660
    "Koguryo": [(lambda y: y > 668, "Balhae")],  # Goguryeo fell in 668; by 700 its northern lands were Balhae
    "Parhae": [(always, "Balhae")],
    "Silia": [(always, "Silla")],
    "Korea": [(lambda y: y < 918, "Silla"), (lambda y: y < 1392, "Goryeo")],  # the 1000 and 1100 layers call Goryeo "Korea"
    "Annam": [(lambda y: y < 939, "Tĩnh Hải"), (lambda y: y < 1804, "Đại Việt")],  # a Chinese circuit until 939  # the 1000 layer's Chinese name for Đại Cồ Việt
    "Tufan Empire": [(always, "Tibetan Empire")],
    "Tibetan Empire": [(lambda y: y > 842, "Tibet")],  # the empire broke up after 842; the 900 layer still has it
    "Nan-Zhao": [(always, "Nanzhao")],
    "Nan Chao": [(lambda y: y < 902, "Nanzhao"), (lambda y: y < 929, "Dachanghe"), (lambda y: y < 937, "Dayining"),
                 (always, "Dali")],  # Nanzhao fell in 902; the kingdom of Dali from 937
    # the island belonged to the empire on the mainland
    "Hainan": [(lambda y: 700 <= y <= 900, "Tang Empire"), (lambda y: 905 < y < 971, "Southern Han"),
               (lambda y: 1000 <= y <= 1200, "Song Empire"), (lambda y: 1279 <= y < 1368, "Great Khanate"),
               (lambda y: 1368 <= y <= 1400, "Ming Chinese Empire")],
    "Great Khanate": [(lambda y: y > 1368, "Northern Yuan")],  # the 1400 layer still has the Yuan; see REASSIGN
    "Chagatai Khanate": [(lambda y: y > 1347, "Moghulistan")],  # the eastern Chagatai khanate
    "Shogun Japan (Kamakura)": [(lambda y: y > 1336, "Japan (Muromachi)")],
    "Pagan": [(lambda y: y > 1300, "Ava")],
    "central Asian khanates": [(lambda y: y == 1600, "Oirat Confederation"),
                               (lambda y: y in (1650, 1715), "Dzungar Khanate")],
    "Taiwan": [(lambda y: y < 1624, "Taiwanese Tribes"), (lambda y: 1683 < y < 1895, "Qing Empire"),
               (lambda y: y == 1945, "Republic of China")],  # a Qing prefecture from 1684; returned to China in 1945
    "Manchu Empire": [(lambda y: y < 1912, "Qing Empire"), (always, "Republic of China")],
    "Hong Kong": [(lambda y: y < 1841, "Qing Empire"), (lambda y: y >= 1997, "China")],  # British from 1841 to 1997
    # the Beiyang and then the Nationalist government, with the warlords who governed provinces under them
    "Chinese Warlords": [(always, "Republic of China")],
    "Chinese warlords": [(always, "Republic of China")],
    "Xinjiang": [(always, "Republic of China")],
    "Manchuria": [(lambda y: y in (1920, 1930, 1945), "Republic of China")],  # the Fengtian clique; back from Manchukuo in 1945
    "Mongolia": [(lambda y: y == 1920, "Republic of China")],  # occupied by Xu Shuzheng's army from 1919 to 1921
    "China": [(lambda y: y < 1949, "Republic of China")],
    "Tibet": [(lambda y: y > 1951, "China")],  # the 1960 layer still draws Tibet apart; the PRC took it in 1950-51
    "Japan": [(lambda y: 1945 <= y < 1952, "Japan (USA)")],
    "White Russia": [(lambda y: y == 1930, "USSR")],  # the 1930 layer labels the whole Soviet Union "White Russia"
    "Far Eastern SSR": [(lambda y: y > 1922, "USSR")],  # merged into Soviet Russia in 1922
}
# polygons named after the group they belong to (PARTOF) rather than their own label
GROUP_RENAMES = {}
# source polygons that are not polities at all; they are dropped
NOT_POLITIES = {"Hövsgöl Nuur"}  # the -100 layer draws Lake Khövsgöl as a polity
# misspelt overlords (SUBJECTO): source spelling -> NAME
# the Southern Xiongnu submitted to the Han in 50; the 400 layer makes Persia a dependency of "Persi"
OVERLORD_RENAMES = {"S. Xiongnu": "Han", "Persi": "Persia", "Manchu Empire": "Qing Empire"}
# overlords the source gets wrong, by NAME: [(year test, overlord NAME, or "" for none)]. The Yuan emperor was himself the
# Great Khan, and Tibet was governed from Dadu under the Yuan; by 1400 no Mongol Empire stood over the Northern Yuan, Tibet
# or the khanates; the Dutch, not the Qing, held the Middag Kingdom in 1650; Bactria owed the Scythians nothing in 221–200 BC.
# Also overlords for polities drawn here: the lords enfeoffed by the Western Zhou kings (and Qin, a Zhou dependency) are
# drawn in the Zhou's paler shade until 771 BC.
fief = [(lambda y: y < -771, "Western Zhou")]
OVERLORD_FIXES = {
    **{n: fief for n in ("Qi", "Lu", "Wey", "Song", "Yan", "Jin (Spring and Autumn)", "Qin")},
    "Great Khanate": [(lambda y: True, "")],
    "Tibet": [(lambda y: y == 1279, "Great Khanate"), (lambda y: y == 1400, "")],
    "Northern Yuan": [(lambda y: True, "")],
    "White Horde": [(lambda y: True, "")],
    "Moghulistan": [(lambda y: True, "")],
    "Middag Kingdom": [(lambda y: y == 1650, "Netherlands")],
    "Bactria": [(lambda y: True, "")],
}

# Peoples, tribes and archaeological cultures rather than states: drawn pale, and their spread between snapshots
# (often just the source mapping them in one year and not the next) is not counted as a territorial change.
PEOPLES = {
    "Sinic", "Proto-Shang", "Dongyi", "Ancient Shu", "Lower Xiajiadian culture", "Qijia culture", "Guifang", "Qiang",
    "Tibetans", "Proto-Tibetan cultures", "Gandhara grave culture", "Proto-Altaic pastoralists", "Paleo-Siberian hunter-gatherers",
    "Siberians", "Finno-Ugric taiga hunter-gatherers", "Karasuk culture", "Iranian pastoralists", "Scythians", "Saces", "Turcik tribes", "Donghu tribes",
    "Xianbei", "Rouran tribes", "Mongols", "Kurykans", "Bashkirs", "Tungus", "Tungusic Tribes", "Jurchens", "Paleo-Koreans",
    "Late Jomon culture", "Yayoi", "Ainu", "Ainus", "Austro-Asiatic rice cultures", "Proto-Thai cultures", "Thai",
    "Mon-Khmer", "Burmese", "Malays", "Malay", "Baiyue", "Hainan", "Taiwanese Tribes", "Dravidians", "Vedic Aryans",
    "Iron Age megalith cultures", "Iron Age chieftainships",
}

# year-dependent display names: NAME -> [(test(year), tag)], first match wins
VARIANTS = {
    "Han": [(lambda y: y < 9, "western"), (always, "eastern")],
    "Jin": [(lambda y: y < 317, "western"), (always, "eastern")],
    "Song Empire": [(lambda y: y > 1127, "southern")],
    "Korea": [(lambda y: 1897 <= y < 1910, "empire")],
    "Tibet": [(lambda y: y < 1279, "fragments")],  # after the empire broke up, before Yuan rule
}


# geometry fixes, applied by scripts/build.py:
# unnamed source polygons that are really a known state: (years, a point inside it, NAME)
UNNAMED = [((1900,), (121.0, 23.8), "Imperial Japan")]  # Taiwan, ceded to Japan in 1895
# polygons that swallow a neighbour: (year, NAME, neighbour NAME, a year whose outline of the neighbour is used);
# the part inside that outline goes back to the neighbour
REASSIGN = [(1400, "Northern Yuan", "Ming Chinese Empire", 1500)]  # the Ming of 1500 stands in for that of 1400

# Areas and border lines for CUT and SPLIT, as (longitude, latitude). Lines run a little past the polity they cut.
WORLD = [(62, 8), (148, 8), (148, 57), (62, 57)]

# River courses for borders that followed a river, traced from Natural Earth's 10 m rivers (public domain) at about the
# detail of the rivers drawn on the map
# the Huai from its upper course down to Xuyi (where its old course, used until 1194, turned north-east to the sea)
HUAI = [(113.72, 32.42), (113.85, 32.41), (113.9, 32.28), (113.95, 32.24), (114.02, 32.25), (114.13, 32.45),
        (114.31, 32.36), (114.36, 32.29), (114.66, 32.31), (114.66, 32.29), (114.72, 32.32), (114.93, 32.27),
        (115.08, 32.31), (115.11, 32.37), (115.22, 32.33), (115.43, 32.43), (115.65, 32.4), (115.69, 32.49),
        (115.79, 32.47), (115.88, 32.57), (115.99, 32.61), (116.11, 32.52), (116.17, 32.43), (116.29, 32.52),
        (116.44, 32.44), (116.56, 32.53), (116.64, 32.54), (116.73, 32.61), (116.69, 32.67), (116.73, 32.69),
        (116.73, 32.73), (116.88, 32.63), (117.01, 32.67), (117.08, 32.7), (117.1, 32.82), (117.17, 32.85),
        (117.19, 32.94), (117.53, 32.97), (117.65, 32.9), (117.76, 33.05), (117.89, 33.05), (117.91, 33.16),
        (118.13, 33.17), (118.18, 33.21), (118.22, 33.18), (118.22, 33.08), (118.29, 32.98), (118.39, 32.98),
        (118.47, 33.03)]
# the Yangtze from Chenglingji (Yueyang) down to Zhenjiang; the estuary below is drawn by hand
YANGTZE = [(113.12, 29.46), (113.42, 29.76), (113.66, 29.95), (113.75, 29.92), (113.79, 29.93), (113.92, 30.03),
           (114.06, 30.09), (114.06, 30.12), (113.98, 30.18), (113.87, 30.18), (113.86, 30.23), (113.97, 30.29),
           (114.05, 30.24), (114.11, 30.35), (114.31, 30.61), (114.43, 30.69), (114.5, 30.67), (114.6, 30.57),
           (114.84, 30.61), (114.81, 30.53), (114.83, 30.44), (115.05, 30.37), (115.07, 30.24), (115.19, 30.21),
           (115.46, 29.87), (115.7, 29.86), (115.74, 29.81), (115.89, 29.73), (116.11, 29.79), (116.27, 29.79),
           (116.39, 29.88), (116.51, 29.89), (116.64, 30.04), (116.81, 30.1), (116.91, 30.27), (116.89, 30.42),
           (117.01, 30.48), (117.21, 30.51), (117.23, 30.67), (117.43, 30.7), (117.7, 30.8), (117.79, 31.12),
           (117.86, 31.14), (117.91, 31.09), (117.95, 31.09), (117.99, 31.12), (118.01, 31.24), (118.31, 31.31),
           (118.3, 31.44), (118.38, 31.56), (118.43, 31.72), (118.77, 32.19), (118.91, 32.17), (119.08, 32.23),
           (119.25, 32.2), (119.5, 32.24), (119.61, 32.2)]
# the Yellow River between Shanxi and Shaanxi, from Togtoh down to Tongguan
YELLOW = [(111.12, 40.24), (111.3, 40.16), (111.4, 40.05), (111.44, 39.92), (111.36, 39.75), (111.46, 39.62),
          (111.42, 39.62), (111.42, 39.52), (111.34, 39.44), (111.16, 39.42), (111.11, 39.38), (111.23, 39.3),
          (111.12, 39.07), (110.97, 38.97), (111.0, 38.9), (110.87, 38.62), (110.9, 38.53), (110.85, 38.46),
          (110.79, 38.44), (110.66, 38.31), (110.58, 38.29), (110.57, 38.23), (110.5, 38.17), (110.52, 37.95),
          (110.58, 37.93), (110.65, 37.81), (110.74, 37.77), (110.74, 37.73), (110.7, 37.71), (110.79, 37.66),
          (110.77, 37.62), (110.79, 37.56), (110.74, 37.47), (110.64, 37.42), (110.63, 37.38), (110.69, 37.36),
          (110.67, 37.28), (110.42, 37.03), (110.44, 37.02), (110.37, 37.02), (110.42, 36.97), (110.37, 36.89),
          (110.42, 36.82), (110.38, 36.77), (110.44, 36.73), (110.39, 36.69), (110.48, 36.59), (110.5, 36.52),
          (110.45, 36.14), (110.62, 35.6), (110.56, 35.51), (110.55, 35.44), (110.33, 35.2), (110.24, 34.8),
          (110.27, 34.64)]


def along(river, a, b):
    """the river's course from the point on it nearest a to the point nearest b"""
    line = LineString(river)
    da, db = line.project(Point(a)), line.project(Point(b))
    pts = list(substring(line, min(da, db), max(da, db)).coords)
    return pts if da <= db else pts[::-1]

# the Western Regions held by the Tang from 692: the Tarim Basin, Turfan, Hami, Dunhuang and Beiting
WESTERN_REGIONS = [(73.5, 39.0), (75.0, 40.6), (78.0, 41.8), (80.5, 42.2), (83.0, 42.8), (84.5, 43.6), (86.0, 44.6),
                   (88.5, 45.0), (91.0, 45.0), (93.5, 44.2), (95.5, 43.0), (96.8, 41.5), (97.5, 40.0), (96.0, 38.6),
                   (93.5, 38.3), (90.0, 37.4), (86.0, 36.4), (82.0, 35.8), (79.0, 36.0), (76.5, 36.6), (75.0, 37.2),
                   (73.8, 38.2)]
# the Qaidam Basin and the Kunlun, south of the Western Regions; Tibetan from 663
QAIDAM = [(75.0, 35.0), (101.0, 35.0), (100.5, 38.5), (97.5, 40.0), (96.0, 38.6), (93.5, 38.3), (90.0, 37.4), (86.0, 36.4),
          (82.0, 35.8), (79.0, 36.0), (76.5, 36.6), (75.0, 37.2)]
MONGOLIA = [(87.5, 49.5), (90.0, 51.5), (95.0, 52.5), (100.0, 52.5), (104.0, 52.0), (108.0, 52.0), (112.0, 51.0),
            (116.0, 50.5), (119.5, 50.0), (120.5, 47.5), (120.0, 45.0), (118.5, 43.0), (116.0, 41.5), (112.0, 40.0),
            (108.0, 38.0), (104.0, 38.0), (100.0, 40.0), (96.5, 42.0), (93.0, 44.5), (90.0, 46.5)]
# Manchuria east of the Greater Khingan, up to the Stanovoy Range, outside the Ming wall around Liaodong
MANCHURIA = [(118.5, 43.0), (120.0, 45.0), (120.5, 47.5), (119.5, 50.0), (121.0, 53.3), (126.0, 54.0), (135.0, 55.0),
             (141.5, 55.0), (141.5, 42.0), (130.7, 42.5), (129.0, 42.0), (128.0, 41.5), (126.5, 41.6), (125.0, 40.9),
             (124.6, 42.0), (123.5, 42.6), (122.0, 42.6), (120.5, 42.3)]
KOREA = [(124.0, 39.6), (124.6, 40.1), (125.5, 40.6), (126.6, 41.6), (127.5, 41.5), (128.3, 41.9), (128.9, 42.3),
         (129.7, 42.4), (130.4, 42.6), (131.0, 42.0), (131.0, 33.0), (124.0, 33.0)]

# the Warring States around 300 BC; the source block also covers Qin's lands east of its own polygon
QIN_E_300 = [(107.5, 37.6), (109.0, 37.7), *along(YELLOW, (110.4, 37.5), (110.27, 34.64)), (111.0, 34.5),
             (111.2, 34.0), (110.8, 33.4), (110.3, 32.9), (110.2, 31.2), (109.6, 30.0), (108.8, 29.0), (108.0, 28.3),
             (106.0, 28.0)]
YAN_300 = [(114.6, 42.5), (115.0, 40.8), (115.2, 39.7), (115.7, 39.0), (116.6, 38.6), (117.6, 38.35), (119.5, 38.3)]
ZHONGSHAN_300 = [(113.95, 38.05), (114.25, 38.85), (115.05, 38.95), (115.45, 38.4), (114.95, 37.85), (113.95, 38.05)]
ZHAO_300 = [(110.0, 36.7), (111.6, 36.6), (112.4, 36.95), (113.4, 36.95), (113.9, 36.6), (114.4, 36.45), (115.0, 36.45),
            (115.6, 36.6), (116.2, 37.3), (116.6, 38.0), (116.7, 38.8)]
HAN_W_300 = [(112.1, 37.2), (112.0, 35.9), (112.25, 35.15), (111.3, 34.85), (109.5, 34.5)]  # Han and Wei's Hedong
HAN_E_300 = [(114.1, 36.7), (113.6, 35.6), (113.2, 35.15), (113.9, 34.7), (114.0, 33.9), (113.9, 33.2)]
WEI_QI_300 = [(115.7, 37.0), (115.5, 35.9), (115.0, 35.4), (114.7, 35.0)]
SONG_QI_300 = [(114.7, 35.2), (116.3, 35.05), (117.6, 34.6), (118.3, 34.2)]
WEI_SONG_300 = [(114.9, 35.3), (114.9, 34.2), (115.0, 33.4)]
CHU_300 = [(110.0, 33.6), (111.2, 33.6), (112.0, 33.5), (113.0, 33.45), (113.9, 33.45), (114.6, 33.6), (115.4, 33.75),
           (116.0, 33.65), (116.7, 33.85), (117.4, 34.05), (118.2, 34.35), (118.7, 34.9), (119.4, 35.25), (120.2, 35.4)]
ZHOU_300 = [(112.1, 34.55), (112.3, 34.85), (112.95, 34.82), (113.0, 34.55), (112.6, 34.4), (112.1, 34.55)]

# the early Warring States after Jin was partitioned (453 BC; the same map serves 350 BC, after Han took Zheng): Qin and Ba-Shu as in 500 BC, Zheng and Lu still
# standing, Yue holding the old lands of Wu; the other borders as in 300 BC
ZHAO_400 = [(109.3, 36.7)] + ZHAO_300[1:-1] + [(116.8, 39.1)]
ZHENG_400 = [(111.9, 35.3), (112.6, 35.0), (113.8, 35.1)]  # the Yellow River between Han's Shangdang and Zheng
# Zheng's west border, east of the Zhou domain: the lands west and south of Luoyang (Yiyang) were Han's
ZHENG_W_453 = [(113.2, 35.2), (113.1, 34.5), (113.2, 34.0), (113.3, 33.2)]
YUE_400 = [(116.3, 34.0), (116.6, 32.6), (117.2, 31.5), (117.0, 30.3), (117.6, 29.2), (118.3, 28.2), (118.6, 26.9)]

# Xia, Shang and Western Zhou (1750-800 BC), drawn from the archaeology and the traditional accounts; all approximate.
# 1750 BC: the Erlitou culture (taken to be the late Xia) in western Henan and southern Shanxi, and the cultures around it
XIA_1750 = [(110.6, 34.3), (110.4, 34.75), (110.7, 35.2), (111.3, 35.7), (111.9, 35.75), (112.3, 35.3), (112.9, 35.15),
            (113.6, 34.95), (114.0, 34.5), (113.9, 33.9), (113.4, 33.55), (112.7, 33.6), (112.0, 33.75), (111.3, 33.95), (110.6, 34.3)]
PROTO_SHANG_1750 = [(113.75, 35.15), (114.0, 36.2), (114.2, 37.3), (114.6, 38.3), (115.4, 38.4), (115.6, 37.3), (115.4, 36.0),
                    (114.8, 35.3), (114.1, 35.0), (113.75, 35.15)]  # the Xiaqiyuan culture
DONGYI_1750 = [(115.8, 36.6), (116.6, 37.6), (118.0, 38.0), (119.5, 37.6), (121.0, 37.6), (122.6, 37.4), (122.6, 36.8),
               (120.8, 35.8), (119.6, 34.9), (118.8, 34.3), (117.6, 34.2), (116.6, 34.5), (115.9, 35.4), (115.8, 36.6)]  # Yueshi
# the Chengdu plain, which the source gives to the Tibetans, to no one or to the rice cultures until Qin took Shu in 316 BC:
# the Sanxingdui culture, then Shu
SHU = [(103.3, 30.2), (103.4, 31.4), (104.2, 31.8), (105.4, 31.6), (105.4, 30.0), (104.2, 29.7), (103.3, 30.2)]
XIAJIADIAN_1750 = [(115.5, 40.0), (116.0, 41.4), (117.5, 42.6), (119.5, 43.2), (121.0, 42.5), (121.5, 41.3), (120.0, 40.2),
                   (118.5, 39.7), (117.0, 39.6), (115.5, 40.0)]
QIJIA_1750 = [(102.6, 35.0), (102.8, 36.6), (104.0, 37.3), (105.6, 36.8), (106.4, 35.9), (106.0, 34.8), (104.6, 34.4), (103.4, 34.5),
              (102.6, 35.0)]
# 1500 BC: the early Shang (Erligang) from eastern Guanzhong to western Shandong and central Hebei, with Panlongcheng on the
# Yangtze
SHANG_1500 = [(108.8, 34.0), (108.9, 34.6), (109.8, 34.95), (110.6, 35.4), (111.4, 35.8), (112.2, 36.1), (113.0, 36.6), (113.6, 37.5),
              (114.2, 38.3), (115.0, 38.6), (115.9, 38.0), (116.5, 37.3), (117.5, 37.0), (117.7, 36.3), (117.3, 35.5), (117.0, 34.7),
              (116.7, 33.8), (116.1, 32.9), (115.4, 32.1), (114.9, 31.3), (114.6, 30.5), (114.0, 30.4), (113.8, 31.1), (113.6, 31.9),
              (113.0, 32.6), (112.2, 33.0), (111.4, 33.4), (110.4, 33.7), (109.6, 33.8), (108.8, 34.0)]
DONGYI_1500 = [(116.6, 37.6), (118.0, 38.1), (119.5, 37.6), (121.0, 37.6), (122.6, 37.4), (122.6, 36.8), (120.8, 35.8), (119.6, 34.9),
               (118.8, 34.3), (117.8, 34.0), (117.0, 34.7), (117.3, 35.5), (117.7, 36.3), (117.5, 37.0), (116.5, 37.3), (116.6, 37.6)]
# 1250 BC: the late Shang under Wu Ding, out of Guanzhong and the Yangtze; the Zhou on the Jing River and at Zhouyuan, the
# Guifang in the northern loess plateau, the Qiang in the west, the Yi in the east
SHANG_1250 = [(112.0, 34.3), (112.2, 35.1), (112.8, 35.5), (113.3, 36.3), (113.7, 37.3), (114.2, 38.2), (114.9, 38.8), (115.8, 38.6),
              (116.5, 37.8), (117.2, 37.3), (118.0, 37.2), (118.7, 36.8), (118.5, 35.9), (117.8, 35.1), (117.4, 34.2), (116.8, 33.4),
              (115.9, 32.8), (114.8, 32.6), (113.8, 32.8), (113.0, 33.3), (112.3, 33.7), (112.0, 34.3)]
ZHOU_1250 = [(107.0, 34.5), (107.3, 35.6), (108.2, 35.9), (108.8, 35.5), (108.7, 34.5), (108.0, 34.3), (107.0, 34.5)]
GUIFANG_1250 = [(108.4, 36.6), (108.6, 38.4), (109.6, 39.5), (111.0, 40.0), (112.4, 39.5), (112.9, 38.5), (112.6, 37.5), (111.8, 36.9),
                (110.6, 36.6), (109.4, 36.4), (108.4, 36.6)]
QIANG_1250 = [(103.6, 34.4), (103.8, 36.3), (105.0, 36.9), (106.3, 36.4), (106.8, 35.4), (106.4, 34.7), (105.2, 34.2), (103.6, 34.4)]
DONGYI_1250 = [(117.2, 37.5), (118.5, 38.0), (119.5, 37.6), (121.0, 37.6), (122.6, 37.4), (122.6, 36.8), (120.8, 35.8), (119.6, 34.9),
               (118.8, 34.0), (118.0, 33.6), (117.4, 34.2), (117.8, 35.1), (118.5, 35.9), (118.7, 36.8), (118.0, 37.2), (117.2, 37.5)]
# the rest of the block: the peoples of the Chinese sphere
SINIC_SEEDS = [(110.0, 29.5), (113.5, 27.5), (107.0, 38.0), (117.0, 31.0), (119.8, 29.0), (106.0, 26.0), (124.0, 42.0), (113.5, 40.6),
               (101.0, 37.5), (110.0, 33.0)]
# 1000 and 800 BC: the Western Zhou royal domain from Zongzhou (Guanzhong) to Chengzhou (Luoyi), and the major fiefs; the
# others as in 700 BC. Jin and Chu were smaller in 1000 BC; Qin was a Zhou dependency in the far west by 800 BC
WZHOU_1000 = [(106.6, 34.2), (106.8, 34.9), (107.6, 35.2), (108.6, 35.1), (109.6, 34.95), (110.4, 34.85), (111.2, 34.9), (111.7, 34.95),
              (112.9, 35.05), (113.1, 34.6), (112.9, 34.1), (112.0, 34.0), (111.0, 34.1), (110.2, 33.9), (109.2, 33.8), (108.0, 33.85),
              (107.2, 34.0), (106.6, 34.2)]
JIN_1000 = [(111.15, 35.35), (111.25, 36.15), (111.9, 36.35), (112.35, 35.95), (112.15, 35.4), (111.6, 35.25), (111.15, 35.35)]
CHU_1000 = [(110.8, 31.6), (110.9, 32.7), (111.6, 33.2), (112.3, 32.7), (112.3, 31.6), (111.6, 31.1), (110.8, 31.6)]
QIN_800 = [(104.6, 34.0), (104.7, 35.0), (105.8, 35.2), (106.5, 34.9), (106.5, 34.25), (105.6, 33.9), (104.6, 34.0)]

# The early Spring and Autumn period (700, 650 and 600 BC): the major states drawn as closed outlines; the rest of the
# source's block stays "Zhou states", the many small states and the Rong, Di and Yi peoples among them
ZHOU_700 = [(111.6, 34.4), (111.9, 35.05), (113.1, 35.1), (113.1, 34.3), (112.1, 34.1), (111.6, 34.4)]
ZHENG_700 = [(113.2, 34.95), (114.4, 34.95), (114.6, 34.2), (113.9, 33.9), (113.2, 34.2), (113.2, 34.95)]
WEY_700 = [(114.0, 36.2), (115.3, 36.2), (115.6, 35.5), (114.9, 35.15), (114.0, 35.4), (114.0, 36.2)]
SONG_700 = [(115.0, 34.9), (116.4, 34.8), (116.6, 34.0), (115.6, 33.8), (115.0, 34.2), (115.0, 34.9)]
LU_700 = [(116.4, 35.9), (117.6, 35.9), (117.7, 35.1), (116.6, 35.0), (116.4, 35.9)]
QI_700 = [(116.8, 37.3), (117.4, 36.1), (118.8, 35.9), (119.6, 36.5), (119.4, 37.3), (118.3, 37.8), (116.8, 37.3)]
JIN_700 = [(110.9, 35.1), (110.8, 36.0), (111.6, 36.4), (112.4, 36.1), (112.3, 35.4), (111.6, 35.0), (110.9, 35.1)]
QIN_700 = [(104.5, 35.8), (106.5, 35.6), (108.7, 35.0), (108.9, 34.0), (107.5, 33.7), (105.5, 33.9), (104.5, 34.5), (104.5, 35.8)]
CHU_700 = [(110.8, 32.6), (112.6, 32.6), (113.6, 31.8), (113.8, 30.6), (113.2, 29.6), (111.8, 29.6), (110.8, 30.5), (110.8, 32.6)]
YAN_700 = [(115.3, 40.6), (115.5, 39.3), (116.6, 38.9), (117.9, 39.2), (118.4, 40.0), (117.2, 40.8), (115.3, 40.6)]
# 650 BC: Qi under Duke Huan, Jin under Duke Xian, Chu north to the Nanyang basin, Qin under Duke Mu; Wey moved south
QI_650 = [(116.3, 37.8), (116.6, 36.4), (117.6, 36.0), (118.8, 35.9), (119.8, 36.2), (119.9, 37.0), (119.2, 37.9), (117.8, 38.2),
          (116.3, 37.8)]
JIN_650 = [(110.5, 34.6), (110.5, 36.0), (111.0, 37.2), (112.0, 37.4), (112.8, 36.6), (112.6, 35.4), (111.9, 35.1), (111.2, 34.6),
           (110.5, 34.6)]
QIN_650 = [(104.5, 35.8), (106.5, 35.9), (108.5, 35.5), (109.9, 35.0), (110.0, 34.3), (108.9, 33.8), (107.5, 33.7), (105.5, 33.9),
           (104.5, 34.5), (104.5, 35.8)]
CHU_650 = [(110.6, 33.0), (111.8, 33.3), (113.0, 33.5), (114.2, 33.0), (115.0, 32.4), (114.8, 31.2), (114.0, 30.3), (113.2, 29.2),
           (111.8, 29.3), (110.6, 30.4), (110.6, 33.0)]
WEY_650 = [(114.3, 35.2), (114.4, 35.8), (115.2, 35.8), (115.4, 35.3), (114.9, 35.0), (114.3, 35.2)]
WU_650 = [(117.8, 32.8), (119.2, 33.6), (121.0, 33.0), (121.6, 31.5), (121.0, 30.8), (119.6, 30.6), (118.6, 30.6), (117.8, 31.4),
          (117.8, 32.8)]
YUE_650 = [(119.6, 30.6), (121.0, 30.8), (122.0, 30.0), (121.5, 28.8), (120.2, 28.6), (119.4, 29.3), (119.6, 30.6)]
BASHU = [(103.5, 33.4), (107.5, 33.3), (110.2, 32.4), (110.4, 31.4), (109.8, 30.5), (109.3, 29.0), (108.6, 27.0), (103.5, 27.0),
         (103.5, 33.4)]
# 600 BC: Jin and Chu at their contest, Qin master of the western Rong
JIN_600 = [(110.4, 34.6), (110.4, 36.5), (110.8, 38.0), (112.2, 38.4), (113.6, 38.0), (114.2, 36.8), (114.6, 35.6), (113.6, 35.1),
           (112.5, 34.95), (111.6, 34.7), (110.4, 34.6)]
CHU_600 = [(110.6, 33.4), (111.8, 33.6), (113.2, 33.8), (114.6, 33.6), (115.8, 33.0), (116.6, 32.2), (117.2, 31.0), (116.6, 29.6),
           (115.0, 28.8), (113.4, 28.6), (111.6, 28.8), (110.4, 30.0), (110.6, 33.4)]
QIN_600 = [(103.8, 36.4), (106.0, 36.4), (108.5, 35.6), (109.9, 35.0), (110.0, 34.3), (108.9, 33.8), (107.5, 33.7), (105.5, 33.9),
           (103.8, 34.6), (103.8, 36.4)]
WEY_600 = [(114.7, 35.3), (114.7, 36.1), (115.6, 36.1), (115.9, 35.6), (115.5, 35.1), (114.7, 35.3)]
ZHOU_600 = [(111.9, 34.5), (112.2, 34.95), (112.95, 34.92), (113.05, 34.5), (112.6, 34.25), (111.9, 34.5)]
# the rest of the block: the small states and the peoples among them
OTHERS = [(113.0, 37.8), (115.5, 37.5), (109.5, 37.0), (106.0, 36.8), (115.6, 32.6), (117.0, 30.0), (112.0, 27.8), (110.0, 39.5),
          (117.0, 34.0)]
OTHERS_600 = [(113.0, 39.2), (115.5, 37.5), (109.5, 37.0), (106.0, 37.0), (117.0, 33.6), (118.2, 29.5), (112.0, 27.5), (110.0, 39.5)]

# the late Warring States in 260 BC, before Changping: Qin holds Hedong, Nanyang and the Chu heartland around Ying
QIN_E_260 = [(107.5, 39.0), (110.0, 38.6), (110.6, 37.5), (111.0, 36.8), (112.0, 36.3), (112.6, 35.6), (113.0, 35.15), (112.7, 34.6),
             (112.3, 34.0), (112.6, 33.3), (113.4, 32.6), (113.8, 31.5), (113.6, 30.2), (113.0, 29.2), (111.5, 28.5), (110.0, 27.5),
             (108.0, 25.0)]
ZHAO_260 = [(110.0, 36.7), (111.6, 36.4), (112.4, 35.9), (113.2, 35.5), (113.9, 36.2), (114.4, 36.45), (115.0, 36.45), (115.6, 36.6),
            (116.2, 37.3), (116.6, 38.0), (116.7, 38.8)]  # Zhao with Shangdang (262)
HAN_260 = [(112.9, 34.7), (113.9, 34.8), (114.2, 34.2), (113.9, 33.6), (113.0, 33.6), (112.7, 34.1), (112.9, 34.7)]
CHU_260 = [(112.4, 33.6), (113.6, 33.6), (114.6, 33.9), (115.6, 34.2), (116.6, 34.6), (117.6, 35.0), (118.6, 35.4), (120.6, 35.6)]
WEI_QI_260 = [(115.7, 37.0), (115.5, 35.9), (115.9, 35.1), (116.4, 34.4)]

# the Spring and Autumn states around 500 BC
QIN_500 = [(109.6, 41.0), (110.0, 37.5), (109.9, 35.6), (110.1, 34.6), (110.6, 33.9), (109.0, 33.7), (107.0, 33.6),
           (105.5, 33.7), (103.8, 33.5)]
BA_500 = [(110.5, 34.2), (110.4, 31.6), (109.8, 30.5), (109.3, 29.0), (108.6, 26.8)]
YAN_500 = [(114.0, 41.5), (114.6, 40.2), (115.3, 39.4), (116.2, 38.9), (117.3, 38.6), (119.0, 38.4)]
JIN_S_500 = [(109.8, 34.7), (111.3, 34.85), (112.2, 35.0), (113.0, 35.05), (114.0, 35.15), (114.8, 35.3), (115.6, 35.5),
             (116.1, 35.8), (116.6, 36.0)]
JIN_QI_500 = [(116.2, 39.3), (116.4, 38.0), (116.3, 37.0), (116.0, 36.3), (116.1, 35.6)]
CHU_500 = [(110.4, 34.0), (111.3, 33.8), (112.3, 33.6), (113.3, 33.75), (114.2, 34.0), (115.0, 33.95), (115.8, 33.6),
           (116.4, 33.2), (116.8, 32.8), (117.0, 32.0), (116.8, 31.0), (116.3, 30.0), (116.6, 29.0), (117.2, 28.0),
           (117.4, 26.8)]
WU_N_500 = [(116.0, 33.2), (117.2, 33.8), (118.2, 34.3), (119.2, 34.6), (120.5, 34.7)]
WU_YUE_500 = [(116.2, 30.3), (117.5, 30.4), (118.6, 30.6), (119.6, 30.7), (120.3, 30.75), (122.5, 30.8)]
ZHENG_SONG_500 = [(114.75, 35.4), (114.7, 34.6), (114.6, 33.8)]
QI_S_500 = [(115.9, 36.2), (116.8, 36.0), (117.5, 36.05), (118.0, 35.6), (118.2, 34.9), (118.6, 34.3)]
LU_SONG_500 = [(116.0, 36.0), (116.3, 35.1), (116.9, 34.75), (117.45, 33.85)]
ZHOU_500 = [(111.9, 34.5), (112.2, 34.95), (112.95, 34.92), (113.05, 34.5), (112.6, 34.25), (111.9, 34.5)]
QI_S_400 = [(115.3, 36.3)] + QI_S_500[1:]

# the Three Kingdoms in 262, the year before Wei conquered Shu; T is where the three met
T_262 = (110.0, 31.5)
WEI_SHU_262 = [T_262, (108.3, 32.4), (108.0, 33.6), (107.2, 33.8), (106.4, 34.0), (105.6, 33.9), (104.8, 34.0),
               (104.0, 33.7), (103.2, 33.2), (102.6, 32.0), (101.5, 31.0), (99.5, 30.5), (97.0, 30.0)]
WEI_WU_262 = [(122.5, 32.5), (120.5, 32.5), (119.3, 32.45), (118.6, 32.35), (118.0, 31.75), (117.3, 31.5), (116.6, 31.0),
              (116.0, 30.9), (115.3, 30.85), (114.6, 31.0), (113.8, 31.0), (113.0, 31.05), (112.4, 31.3), (111.7, 31.35),
              (110.9, 31.45), (110.3, 31.5), T_262]  # north of the Yangtze: Wu held Jianye, Ruxu and Jiangling
SHU_WU_262 = [T_262, (109.6, 31.0), (109.4, 30.0), (109.0, 29.0), (108.6, 27.5), (107.5, 25.5), (106.2, 24.2),
              (105.0, 23.3), (103.8, 22.7), (103.0, 21.0), (102.0, 20.0)]

# Liaodong, held by Goguryeo from 404 until 668
LIAODONG = [(121.0, 38.6), (121.8, 40.2), (122.3, 41.0), (122.8, 42.2), (123.8, 43.4), (125.5, 44.5), (129.5, 44.5), (129.5, 38.5)]

# the Sixteen Kingdoms around 320: the Eastern Jin, the two Zhaos, the Cheng Han in Shu, the Former Liang in Hexi,
# the Tuoba of Dai and the Murong in Liaoxi; the Cheng Han borders follow those of Shu Han in 262
EJIN_N_320 = [(120.6, 34.4), (119.2, 33.9), (118.0, 33.7), (116.8, 34.0), (115.8, 34.2), (114.8, 34.3), (113.8, 33.9), (112.9, 33.2),
              (112.0, 32.7), (111.0, 32.6), (110.3, 32.5), T_262]
ZHAOS_320 = [(110.9, 41.5), *along(YELLOW, (111.12, 40.24), (110.27, 34.64)), (111.3, 34.5), (111.8, 34.2),
             (112.3, 33.6), (112.7, 32.7)]  # Han Zhao in Guanzhong, Later Zhao east of the Yellow River
LIANG_E = [(105.5, 41.0), (104.8, 38.5), (104.4, 37.0), (104.2, 35.8), (103.6, 34.9), (102.5, 34.4), (100.5, 30.0)]  # Former Liang
DAI_S = [(110.3, 39.6), (111.5, 39.4), (112.6, 39.2), (113.6, 39.4), (114.5, 40.2), (115.0, 41.0), (115.3, 43.0)]  # Tuoba Dai
MURONG_W = [(118.6, 43.0), (119.2, 41.0), (119.7, 40.0), (120.2, 39.5)]
# around 360: the Former Yan in the east, the Former Qin in Guanzhong; the Eastern Jin has Shu (347) and Luoyang (356)
EJIN_N_360 = [(120.6, 34.4), (119.2, 33.9), (118.0, 33.7), (116.8, 33.9), (115.6, 33.6), (114.6, 33.4), (113.6, 33.4), (113.2, 34.0),
              (112.9, 34.9), (112.0, 34.9), (111.8, 34.3), (111.0, 33.8), (110.4, 33.5), (109.0, 33.6), (107.2, 33.8), (106.4, 34.0),
              (105.6, 33.9), (104.8, 34.0), (104.0, 33.7), (103.2, 33.2), (102.6, 32.0), (101.5, 31.0), (99.5, 30.5), (97.0, 30.0)]
QIN_YAN_360 = [*along(YELLOW, (111.12, 40.24), (110.27, 34.64)), (111.3, 34.6), (111.9, 34.0)]
# around 400, after the Former Qin broke up: the Northern Wei, the Later Yan in Liaoxi, the Southern Yan in Shandong,
# the Later Qin in Guanzhong and Henan, the Liang states in Hexi, the Eastern Jin to the Huai and the Qinling
JIN_N_400 = [(120.6, 35.0), (119.4, 34.9), (118.4, 34.7), (117.6, 34.6), (116.6, 34.4), (115.6, 34.0), (114.6, 33.8), (113.6, 33.6),
             (112.6, 33.3), (111.6, 33.1), (110.6, 33.2), (110.2, 33.5), (109.0, 33.7), (107.2, 33.8), (106.4, 34.0), (105.6, 33.9),
             (104.8, 34.0), (104.0, 33.7), (103.2, 33.2), (101.0, 32.8)]
YAN_S_400 = [(118.8, 38.2), (117.6, 37.4), (116.5, 36.7), (115.7, 35.9), (115.4, 35.0), (115.2, 33.6)]  # the Southern Yan
WEI_QIN_400 = [(113.4, 38.0), (113.8, 36.5), (114.2, 35.4), (114.8, 34.9), (115.6, 34.8)]
YAN_WEI_400 = [(118.2, 43.0), (118.4, 41.0), (119.0, 40.0), (119.6, 39.5)]  # the Later (then Northern) Yan in Liaoxi
WEI_W_400 = [(110.8, 43.0), *along(YELLOW, (111.12, 40.24), (110.27, 34.64)), (110.3, 34.0)]  # the Yellow River below the Ordos
LLIANG_400 = [(104.8, 41.0), (104.2, 38.5), (103.6, 37.3), (102.0, 37.4), (100.5, 37.8), (99.5, 38.5)]  # the Later Liang at Guzang
SLIANG_400 = [(100.6, 37.3), (102.6, 37.2), (103.2, 36.4), (102.6, 35.6), (100.8, 35.7), (100.4, 36.6), (100.6, 37.3)]
NL_WL = [(97.4, 42.0), (97.6, 39.5), (97.2, 37.0)]  # the Northern Liang at Zhangye, the Western Liang at Dunhuang
# 420: the Liu Song holds the land to the Yellow River and Luoyang; the Xia holds Guanzhong (418)
SONG_N_420 = [(118.8, 38.2), (117.6, 37.4), (116.5, 36.7), (115.4, 35.9), (114.6, 35.45), (113.5, 35.05), (112.6, 34.95), (111.6, 34.8),
              (110.6, 34.6), (110.3, 34.0), (110.0, 33.6), (109.0, 33.7), (107.2, 33.8), (106.4, 34.0), (105.6, 33.9), (104.8, 34.0),
              (104.0, 33.7), (103.2, 33.2), (101.0, 32.8)]
XIA_WEI_420 = [*along(YELLOW, (111.12, 40.24), (110.27, 34.64)), (110.7, 34.3)]
XIA_QIN_420 = [(104.0, 38.8), (105.5, 37.2), (106.5, 36.0), (107.5, 35.0), (107.8, 34.0)]  # the Xia and the Western Qin
# north Shaanxi, below the Ordos: the south of the 300 layer's Han Zhao polygon
HZ_S = [(105.5, 35.5), (110.6, 35.5), (110.5, 38.0), (105.5, 38.0)]
# its part east of the Yellow River, in south-west Shanxi around Pingyang
HZ_E = [(110.55, 35.4), (112.6, 35.4), (112.6, 39.2), (110.55, 39.2)]
# 439: the Liu Song still holds Shandong and the land north of the Huai, lost to the Northern Wei in 466-469
HUAIBEI_440 = [(114.0, 32.8), (114.3, 34.0), (114.8, 35.2), (115.8, 36.0), (116.8, 36.9), (117.8, 37.6), (118.8, 38.0), (123.0, 38.0),
               (123.0, 32.5)]
# 540: the Eastern and Western Wei, and the Liang to the Huai, Hanzhong and Shu
WEI_SPLIT_540 = [(110.6, 43.5), *along(YELLOW, (111.12, 40.24), (110.6, 36.0)), (111.0, 35.6), (110.9, 35.0), (111.4, 34.6), (112.0, 34.2),
                 (112.3, 33.5), (112.5, 32.8), (112.6, 32.1)]
LIANG_N_540 = [(120.6, 34.3), (119.0, 33.6), *along(HUAI, (118.4, 33.1), (113.72, 32.42)), (112.6, 32.4), (111.6, 32.6), (110.6, 33.0), (110.0, 33.5), (109.0, 33.7), (107.2, 33.8), (106.4, 34.0), (105.6, 33.9),
               (104.8, 34.0), (104.0, 33.7), (103.2, 33.2), (101.0, 32.8), (99.0, 33.0), (96.0, 33.5), (94.0, 34.0)]
# 560 and 580: the Chen south of the Yangtze, the Western Liang at Jiangling under the Zhou, the Northern Zhou with Shu
QI_ZHOU_560 = WEI_SPLIT_540[:-1] + [(113.2, 31.8), (113.9, 30.0)]
CHEN_N_560 = [(121.8, 31.75), (120.3, 31.95), *along(YANGTZE, (119.61, 32.2), (113.12, 29.46)), (112.4, 29.7),
              (111.6, 29.9), (110.8, 30.2), (110.0, 30.4), (109.4, 30.0), (109.0, 29.0), (108.6, 27.5), (107.5, 25.5),
              (106.2, 24.2), (105.0, 23.3), (103.8, 22.7), (103.0, 21.0), (102.0, 20.0)]
WLIANG_LOOP = [(111.5, 31.0), (112.7, 31.0), (112.9, 30.3), (112.2, 30.0), (111.5, 30.1), (111.5, 31.0)]
CHANGAN, YE, XIANGGUO, GUZANG, PINGCHENG, LONGCHENG = (108.94, 34.27), (114.62, 36.33), (114.5, 37.07), (102.64, 37.93), \
    (113.3, 40.09), (120.45, 41.57)

# the Former Qin and the Eastern Jin before the battle of the Fei River (383)
QIN_JIN_383 = [(120.6, 34.3), (119.0, 33.6), *along(HUAI, (118.4, 33.1), (114.6, 32.3)), (113.6, 31.9), (112.6, 31.65), (111.6, 31.6), (110.6, 31.2), (109.8, 30.6), (109.0, 29.5), (107.8, 28.3),
               (106.0, 27.6), (104.0, 27.3), (102.0, 26.5), (98.5, 26.0)]

# the Five Dynasties and Ten Kingdoms in 950: the Later Han, the Later Shu, the Southern Tang, Wuyue, Chu,
# the Southern Han and Jingnan
HAN_S_950 = [(121.0, 34.6), (119.9, 34.15), (119.0, 33.6), *along(HUAI, (118.5, 33.05), (115.5, 32.45)), (114.8, 32.15), (114.6, 31.5), (114.3, 30.95), (113.6, 30.75), (113.0, 30.55),
             (112.7, 30.7), (112.1, 30.85), (111.4, 31.2), (110.6, 31.5), (110.0, 31.9), (109.3, 32.5), (108.6, 33.4),
             (108.0, 33.8), (107.2, 34.2), (106.9, 34.4), (106.4, 34.75), (105.6, 34.95), (104.8, 35.0), (103.8, 34.8),
             (102.0, 34.5), (99.0, 34.0)]
SHU_E_950 = [(109.9, 32.4), (109.6, 31.3), (109.4, 29.8), (108.8, 29.0), (108.3, 28.0), (107.5, 27.3), (106.2, 27.4),
             (104.5, 27.0), (103.0, 26.5), (100.0, 27.0)]
CHU_W_950 = [(109.0, 29.6), (109.4, 28.0), (109.3, 27.0), (108.8, 26.0), (108.0, 24.5)]
SHAN_N_950 = [(103.0, 25.5), (104.0, 25.8), (105.3, 26.2), (106.5, 26.0), (107.6, 25.7), (108.5, 24.8), (109.5, 24.5), (110.5, 24.2), (111.4, 24.4), (112.2, 24.9),
              (113.2, 25.1), (114.0, 25.2), (114.6, 24.9), (115.3, 24.7), (116.2, 24.6), (116.9, 24.3), (117.4, 23.8),
              (117.9, 23.4)]
CHU_E_950 = [(113.9, 31.1), (113.8, 30.2), (113.6, 29.6), (113.9, 28.9), (114.0, 28.0), (113.9, 27.0), (114.0, 26.2),
             (114.3, 25.6), (114.5, 24.6)]
JINGNAN_950 = [(110.8, 30.95), (111.5, 30.95), (112.1, 30.75), (112.6, 30.6), (112.9, 30.3), (112.6, 29.85),
               (111.6, 29.9), (110.8, 30.3), (110.8, 30.95)]
WUYUE_950 = [(121.8, 31.7), (120.45, 31.55), (119.95, 31.2), (119.6, 30.6), (119.0, 30.0), (118.4, 29.2), (118.2, 28.3),
             (118.9, 27.4), (119.1, 26.7), (118.9, 26.0), (119.8, 25.3)]

# the other Five Dynasties years reuse the 950 lines, with these
JIN_910 = [(113.6, 41.6), (113.5, 40.2), (113.8, 39.3), (114.0, 38.6), (114.1, 37.5), (113.9, 36.6), (113.4, 35.9), (112.5, 35.8),
           (111.6, 36.0), *along(YELLOW, (110.4, 37.0), (111.12, 40.24)), (111.0, 40.8), (111.2, 41.6)]  # Li Cunxu's Hedong
YAN_910 = [(113.3, 40.0), (114.2, 39.9), (114.8, 39.5), (115.4, 39.2), (116.0, 38.8), (116.6, 38.6), (117.5, 38.4), (118.5, 38.3),
           (119.5, 38.3)]  # Liu Shouguang's Youzhou
QI_910 = [(108.5, 33.2), (108.3, 34.6), (108.0, 35.2), (107.8, 36.0), (107.3, 36.8), (106.5, 37.5), (105.0, 37.3), (103.5, 36.5),
          (101.0, 36.0)]  # Li Maozhen's Fengxiang
WUYUE_910 = [(121.8, 31.7), (120.45, 31.55), (119.95, 31.2), (119.6, 30.6), (119.0, 30.0), (118.4, 29.2), (118.2, 28.3),
             (118.9, 27.6), (119.6, 27.3), (120.6, 27.1)]  # before Wuyue took Fuzhou in 947
MIN_910 = [(118.5, 28.6), (117.6, 27.9), (117.0, 27.3), (116.4, 26.3), (116.3, 25.3), (116.8, 24.0)]  # Min, until 945
QINGYUAN = [(120.0, 25.6), (118.6, 25.6), (117.8, 25.4), (117.3, 25.0), (116.8, 24.1)]  # Quanzhou and Zhangzhou, 949-978
NHAN_958 = [(114.2, 41.0), (114.1, 39.6), (114.0, 38.6), (113.9, 37.6), (113.5, 36.9), (112.6, 36.6), (111.6, 36.7),
            *along(YELLOW, (110.9, 37.3), (111.12, 40.24)), (111.0, 41.0)]  # the Northern Han, 951-979
# the Later Zhou border after it took the land north of the Yangtze from the Southern Tang (958) and Qin, Feng, Cheng
# and Jie from the Later Shu (955)
ZHOU_S_958 = [(121.8, 31.75), (120.3, 31.95), *along(YANGTZE, (119.61, 32.2), (114.3, 30.55)), (113.6, 30.75), (113.0, 30.55), (112.7, 30.7),
              (112.1, 30.85), (111.4, 31.2), (110.6, 31.5), (110.0, 31.9), (109.3, 32.5), (108.6, 33.4), (108.0, 33.8),
              (107.4, 33.5), (106.6, 33.2), (105.8, 33.0), (105.0, 32.8), (104.3, 32.9), (103.5, 33.4), (102.0, 33.8), (99.0, 34.0)]
SHAN_N_958 = [(103.0, 25.5), (104.0, 25.8), (105.3, 26.2), (106.5, 26.0), (107.6, 25.7), (108.5, 24.8), (109.5, 25.95), (110.6, 25.9), (111.5, 25.5), (112.2, 25.2), (113.2, 25.1),
              (114.0, 25.2), (114.6, 24.9), (115.3, 24.7), (116.2, 24.6), (116.9, 24.3), (117.4, 23.8), (117.9, 23.4)]  # after 951
# the Sixteen Prefectures, ceded to the Khitans in 938; the 1000 layer already draws them as Liao
SIXTEEN = [(111.3, 39.0), (111.6, 40.6), (113.2, 41.2), (115.4, 41.1), (116.8, 40.9), (118.0, 40.4), (118.5, 39.6), (117.8, 38.8)]
# Balhae, destroyed by the Khitans in 926
BALHAE = [(122.5, 40.6), (123.3, 42.5), (124.5, 44.5), (126.0, 46.5), (129.0, 47.5), (133.0, 48.0), (135.5, 47.0), (135.0, 43.0),
          (130.7, 42.3), (128.0, 40.0), (127.3, 39.6), (126.0, 39.5), (124.5, 39.7), (123.5, 39.8)]
# the Hexi Corridor, held by the Ganzhou Uyghurs and the Guiyi circuit until the Tangut Xia took it (1028-1036)
HEXI = [(93.0, 36.5), (103.8, 36.5), (103.8, 42.5), (93.0, 42.5)]
# GUIZHOU: the strip between the Shu and Southern Han lines, given to the Shu side every year
GUIZHOU = (105.5, 26.8)
YANGZHOU, FUZHOU, QUANZHOU, CHANGSHA, GUANGZHOU, JIANGLING, TAIYUAN = (119.42, 32.39), (119.3, 26.08), (118.68, 24.87), \
    (112.98, 28.2), (113.26, 23.13), (112.2, 30.35), (112.55, 37.87)

# the Song and the Jin after the peace of Shaoxing (1142): the Huai, then west along the Qinling to the Dasan Pass
SHAOXING = [(121.0, 34.6), (119.9, 34.15), (119.0, 33.6), *along(HUAI, (118.5, 33.05), (113.72, 32.42)), (113.4, 32.45), (112.6, 32.35), (111.8, 32.65), (111.0, 33.0),
            (110.3, 33.2), (109.5, 33.5), (108.5, 33.8), (107.5, 34.05), (106.95, 34.3), (106.3, 34.35), (105.6, 34.4),
            (104.9, 34.5), (104.2, 34.55), (103.5, 34.5), (102.0, 34.3), (99.0, 34.0)]

LUOYANG, CHENGDU, JIANKANG, KAIFENG, HANGZHOU = (112.45, 34.62), (104.07, 30.67), (118.8, 32.05), (114.3, 34.8), (120.16, 30.25)

# CUT: (years, NAME or None for unrecorded land, area, new NAME or None): the part of NAME inside the area goes to new NAME;
# the area is a ring of points or the NAME of another polity, whose outline in that snapshot is used
CUT = [
    *[((-1750, -1500, -1250), n, SHU, "Ancient Shu") for n in ("Tibetans", "Sinic")],
    *[((-1000, -800, -700, -650, -600, -500, -453, -350), n, SHU, "Ba and Shu")
      for n in ("Tibetans", "Sinic", None, "Austro-Asiatic rice cultures", "Proto-Thai cultures")],
    # the 400 layer's Jin overlaps its Sixteen Kingdoms across the north; there the north wins
    ((400,), "Jin", "Sixteen Kingdoms", "Sixteen Kingdoms"),
    ((420,), "Liu Song", "Sixteen Kingdoms", "Sixteen Kingdoms"),
    ((262,), "Southern Xiongnu", WORLD, "Xianbei"),  # the 200 layer's Southern Xiongnu, north of the Hexi Corridor
    *[((700, 742), n, WESTERN_REGIONS, "Tang Empire") for n in ("Tibetan Empire", "Karluks", "Göktürks", "Uyghurs", None)],
    ((700, 742), "Göktürks", QAIDAM, "Tibetan Empire"),
    ((910,), "Khitans", SIXTEEN, "Later Liang"),
    ((926,), "Liao", SIXTEEN, "Later Tang"),
    *[((910,), n, BALHAE, "Balhae") for n in ("Khitans", "Silla", None)],
    ((910, 926, 938, 950, 958, 970, 1000), "Dingnan", HEXI, "Ganzhou Uyghurs"),
    ((420,), "Sixteen Kingdoms", LIAODONG, "Koguryo"),
    ((439, 500), "Toba Wei", LIAODONG, "Koguryo"),
    ((540,), "Eastern Wei", LIAODONG, "Koguryo"),
    ((560,), "Northern Qi", LIAODONG, "Koguryo"),
    ((580,), "Northern Zhou", LIAODONG, "Koguryo"),
    ((589,), "Sui Empire", LIAODONG, "Koguryo"),
    ((439,), "Toba Wei", HUAIBEI_440, "Liu Song"),
    ((500,), "Southern Qi", HUAIBEI_440, "Toba Wei"),  # the 500 layer still gives the south Shandong, lost in 466-469
    ((320,), "Dai", HZ_S, "Han Zhao"),
    ((320,), "Dai", HZ_E, "Later Zhao"),
    ((360,), "Dai", HZ_S, "Former Qin"),
    ((360,), "Dai", HZ_E, "Former Yan"),
    ((1142,), "Mongols", MANCHURIA, "Jurchen Jin"),
    ((1279,), "Great Khanate", KOREA, "Goryeo"),  # a Yuan vassal; the 1279 layer draws it inside the Yuan
    ((1400,), "Northern Yuan", KOREA, "Korea"),
    ((1400,), "Northern Yuan", MANCHURIA, "Jurchens"),
    ((1500,), "Moghulistan", MONGOLIA, "Northern Yuan"),  # the 1500 layer gives Mongolia to the Chagatai khanate
    ((1500,), "Moghulistan", MANCHURIA, "Jurchens"),
    ((1600,), "Oirat Confederation", MONGOLIA, "Northern Yuan"),
    ((1600,), "Oirat Confederation", WESTERN_REGIONS, "Yarkent Khanate"),
    ((1600,), "Oirat Confederation", MANCHURIA, "Jurchens"),
    ((1600,), "Ming Chinese Empire", MANCHURIA, "Jurchens"),  # the 1600 layer stretches the Ming over the Jurchens
    ((1650,), "Dzungar Khanate", MONGOLIA, "Khalkha"),
    ((1650,), "Dzungar Khanate", WESTERN_REGIONS, "Yarkent Khanate"),
    ((1650,), "Dzungar Khanate", MANCHURIA, "Qing Empire"),
]
# SPLIT: (years, NAME, border lines, {NAME: [seed points]}): NAME is cut along the lines; each piece goes to the name
# whose seed it holds, a piece without a seed (an island) to the piece nearest to it
SPLIT = [
    ((-1750,), "Sinic", [XIA_1750, PROTO_SHANG_1750, DONGYI_1750, XIAJIADIAN_1750, QIJIA_1750],
     {"Xia (Erlitou)": [(112.69, 34.69)], "Proto-Shang": [(114.6, 36.8)], "Dongyi": [(118.6, 36.2)],
      "Lower Xiajiadian culture": [(118.9, 41.8)], "Qijia culture": [(104.8, 35.8)], "Sinic": SINIC_SEEDS}),
    ((-1500,), "Sinic", [SHANG_1500, DONGYI_1500, XIAJIADIAN_1750],
     {"Shang": [(113.67, 34.76)], "Dongyi": [(119.5, 36.4)], "Lower Xiajiadian culture": [(118.9, 41.8)],
      "Sinic": SINIC_SEEDS}),
    ((-1250,), "Sinic", [SHANG_1250, ZHOU_1250, GUIFANG_1250, QIANG_1250, DONGYI_1250],
     {"Shang": [(114.31, 36.12)], "Zhou (pre-dynastic)": [(107.9, 35.0)], "Guifang": [(110.6, 38.2)], "Qiang": [(105.0, 35.6)],
      "Dongyi": [(120.0, 36.5)], "Sinic": SINIC_SEEDS}),
    ((-1000,), "Zhou states", [WZHOU_1000, QI_700, LU_700, WEY_700, SONG_700, YAN_700, JIN_1000, CHU_1000, BASHU],
     {"Western Zhou": [(108.9, 34.3), LUOYANG], "Qi": [(118.35, 36.85)], "Lu": [(117.0, 35.6)], "Wey": [(114.6, 35.7)],
      "Song": [(115.65, 34.4)], "Yan": [(116.4, 39.9)], "Jin (Spring and Autumn)": [(111.7, 35.8)], "Chu": [(111.6, 32.2)],
      "Ba and Shu": [(106.55, 29.56)], "Zhou states": OTHERS}),
    ((-800,), "Zhou states", [WZHOU_1000, QI_700, LU_700, WEY_700, SONG_700, YAN_700, JIN_700, CHU_700, QIN_800, BASHU],
     {"Western Zhou": [(108.9, 34.3), LUOYANG], "Qi": [(118.35, 36.85)], "Lu": [(117.0, 35.6)], "Wey": [(114.6, 35.7)],
      "Song": [(115.65, 34.4)], "Yan": [(116.4, 39.9)], "Jin (Spring and Autumn)": [(111.4, 35.65)], "Chu": [(112.2, 31.0)],
      "Qin": [(106.2, 34.7)], "Ba and Shu": [(106.55, 29.56)], "Zhou states": OTHERS}),
    ((-500,), "Zhou states", [QIN_500, BA_500, YAN_500, JIN_S_500, JIN_QI_500, CHU_500, WU_N_500, WU_YUE_500,
                              ZHENG_SONG_500, QI_S_500, LU_SONG_500, ZHOU_500],
     {"Qin": [(107.4, 34.5)], "Ba and Shu": [(106.55, 29.56)], "Jin (Spring and Autumn)": [(111.3, 35.6), (114.5, 36.6)],
      "Qi": [(118.35, 36.85)], "Lu": [(117.0, 35.6)], "Song": [(115.65, 34.4)], "Zheng": [(113.7, 34.4)],
      "Eastern Zhou": [LUOYANG], "Chu": [(112.2, 30.4)], "Wu": [(120.6, 31.3)], "Yue": [(120.58, 30.0)],
      "Yan": [(116.4, 39.9)]}),
    ((-700,), "Zhou states", [ZHOU_700, ZHENG_700, WEY_700, SONG_700, LU_700, QI_700, JIN_700, QIN_700, CHU_700, YAN_700, BASHU],
     {"Eastern Zhou": [LUOYANG], "Zheng": [(113.7, 34.4)], "Wey": [(114.6, 35.7)], "Song": [(115.65, 34.4)], "Lu": [(117.0, 35.6)],
      "Qi": [(118.35, 36.85)], "Jin (Spring and Autumn)": [(111.4, 35.65)], "Qin": [(107.6, 34.4)], "Chu": [(112.2, 31.0)],
      "Yan": [(116.4, 39.9)], "Ba and Shu": [(106.55, 29.56)], "Zhou states": OTHERS}),
    ((-1000, -800, -700), "Wu", [WU_YUE_500], {"Wu": [(120.6, 31.3)], "Yue": [(120.58, 30.0)]}),
    ((-650,), "Zhou states", [ZHOU_700, ZHENG_700, WEY_650, SONG_700, LU_700, QI_650, JIN_650, QIN_650, CHU_650, YAN_700, WU_650,
                              YUE_650, BASHU],
     {"Eastern Zhou": [LUOYANG], "Zheng": [(113.7, 34.4)], "Wey": [(114.8, 35.4)], "Song": [(115.65, 34.4)], "Lu": [(117.0, 35.6)],
      "Qi": [(118.35, 36.85)], "Jin (Spring and Autumn)": [(111.4, 35.65)], "Qin": [(107.4, 34.5)], "Chu": [(112.2, 31.0)],
      "Yan": [(116.4, 39.9)], "Wu": [(120.6, 31.3)], "Yue": [(120.58, 30.0)], "Ba and Shu": [(106.55, 29.56)], "Zhou states": OTHERS}),
    ((-600,), "Zhou states", [ZHOU_600, ZHENG_700, WEY_600, SONG_700, LU_700, QI_650, JIN_600, QIN_600, CHU_600, YAN_700, WU_650,
                              YUE_650, BASHU],
     {"Eastern Zhou": [LUOYANG], "Zheng": [(113.7, 34.4)], "Wey": [(115.1, 35.7)], "Song": [(115.65, 34.4)], "Lu": [(117.0, 35.6)],
      "Qi": [(118.35, 36.85)], "Jin (Spring and Autumn)": [(111.4, 35.65), (113.0, 37.0)], "Qin": [(107.4, 34.5)],
      "Chu": [(112.2, 31.0)], "Yan": [(116.4, 39.9)], "Wu": [(120.6, 31.3)], "Yue": [(120.58, 30.0)], "Ba and Shu": [(106.55, 29.56)],
      "Zhou states": OTHERS_600}),
    ((-350,), "Zhou states", [QIN_500, BA_500, YAN_500, ZHONGSHAN_300, ZHAO_400, HAN_W_300, HAN_E_300, WEI_QI_300,
                              SONG_QI_300, WEI_SONG_300, CHU_300, YUE_400, QI_S_400, ZHENG_400, ZHOU_300],
     {"Qin": [(107.4, 34.5)], "Ba and Shu": [(106.55, 29.56)], "Wei": [(111.2, 35.1), (114.35, 34.8)],
      "Zhao": [(112.55, 37.85), (114.5, 36.6)], "Han (Warring States)": [(113.1, 36.2), (113.7, 34.4)],
      "Qi": [(118.35, 36.85)], "Lu": [(117.0, 35.6)], "Song": [(115.65, 34.4)], "Chu": [(112.2, 30.4)],
      "Yue": [(120.58, 30.0)], "Yan": [(116.4, 39.9)], "Zhongshan": [(114.4, 38.3)], "Eastern Zhou": [LUOYANG]}),
    ((-260,), "Zhou states", [QIN_E_260, YAN_300, ZHAO_260, HAN_260, CHU_260, WEI_QI_260, ZHOU_300],
     {"Qin": [(111.2, 35.1), (112.5, 33.0), (112.2, 30.4), (109.6, 36.0)], "Zhao": [(114.5, 36.6), (112.55, 37.85), (113.1, 36.2)],
      "Yan": [(116.4, 39.9), (123.2, 41.3)], "Qi": [(118.35, 36.85)], "Wei": [(114.35, 34.8)], "Han (Warring States)": [(113.7, 34.4)],
      "Chu": [(114.9, 33.7), (117.0, 31.0), (113.0, 28.2)], "Eastern Zhou": [LUOYANG]}),
    ((-453,), "Zhou states", [QIN_500, BA_500, YAN_500, ZHONGSHAN_300, ZHAO_400, HAN_W_300, HAN_E_300, WEI_QI_300,
                              SONG_QI_300, WEI_SONG_300, CHU_300, YUE_400, QI_S_400, ZHENG_400, ZHENG_W_453, ZHOU_300],
     {"Qin": [(107.4, 34.5)], "Ba and Shu": [(106.55, 29.56)], "Wei": [(111.2, 35.1), (114.35, 34.8)],
      "Zhao": [(112.55, 37.85), (114.5, 36.6)], "Han (Warring States)": [(113.1, 36.2), (111.9, 34.3)], "Zheng": [(113.7, 34.4)],
      "Qi": [(118.35, 36.85)], "Lu": [(117.0, 35.6)], "Song": [(115.65, 34.4)], "Chu": [(112.2, 30.4)],
      "Yue": [(120.58, 30.0)], "Yan": [(116.4, 39.9)], "Zhongshan": [(114.4, 38.3)], "Eastern Zhou": [LUOYANG]}),
    ((-300,), "Zhou states", [QIN_E_300, YAN_300, ZHONGSHAN_300, ZHAO_300, HAN_W_300, HAN_E_300, WEI_QI_300, SONG_QI_300,
                              WEI_SONG_300, CHU_300, ZHOU_300],
     {"Qin": [(109.6, 36.0), (108.5, 33.0), (107.5, 30.0)], "Yan": [(116.4, 39.9), (123.2, 41.3)], "Zhongshan": [(114.4, 38.3)],
      "Zhao": [(114.5, 36.6), (112.55, 37.85), (113.3, 40.1)], "Wei": [(114.35, 34.8), (111.2, 35.1)],
      "Han (Warring States)": [(113.7, 34.4), (113.1, 36.2)], "Song": [(115.65, 34.4)], "Qi": [(118.35, 36.85)],
      "Chu": [(112.2, 30.4)], "Eastern Zhou": [LUOYANG]}),
    ((262,), "Cao Wei", [WEI_SHU_262, WEI_WU_262, SHU_WU_262],
     {"Cao Wei": [LUOYANG], "Shu Han": [CHENGDU], "Eastern Wu": [JIANKANG, (113.26, 23.13)]}),
    ((320,), "Jin", [EJIN_N_320, WEI_SHU_262, SHU_WU_262, ZHAOS_320, LIANG_E, DAI_S, MURONG_W],
     {"Jin": [JIANKANG], "Han Zhao": [CHANGAN], "Later Zhao": [XIANGGUO], "Cheng Han": [CHENGDU],
      "Former Liang (Zhang)": [GUZANG], "Dai": [PINGCHENG], "Murong": [(121.5, 41.5)]}),
    ((360,), "Jin", [EJIN_N_360, QIN_YAN_360, LIANG_E, DAI_S],
     {"Jin": [JIANKANG, CHENGDU, LUOYANG], "Former Qin": [CHANGAN], "Former Yan": [YE], "Former Liang (Zhang)": [GUZANG],
      "Dai": [PINGCHENG]}),
    ((400,), "Jin", [JIN_N_400, YAN_S_400, WEI_QIN_400],
     {"Jin": [JIANKANG, CHENGDU], "Later Qin": [CHANGAN, LUOYANG, (105.7, 34.58)], "Southern Yan": [(118.47, 36.69)],
      "Toba Wei": [YE]}),
    ((400,), "Sixteen Kingdoms", [YAN_WEI_400, WEI_W_400, LLIANG_400, SLIANG_400],
     {"Toba Wei": [PINGCHENG, (112.55, 37.87)], "Later Yan": [LONGCHENG, (123.2, 41.27)], "Later Qin": [(108.5, 37.5), (103.83, 36.06)],
      "Later Liang (Lü)": [GUZANG], "Southern Liang (Tufa)": [(102.4, 36.5)]}),
    ((400, 420), "Northern Liang", [NL_WL], {"Northern Liang": [(100.45, 38.93)], "Western Liang (Li)": [(95.8, 40.5)]}),
    ((420,), "Liu Song", [SONG_N_420, XIA_WEI_420],
     {"Liu Song": [JIANKANG, LUOYANG, (118.47, 36.69)], "Xia (Helian)": [CHANGAN], "Toba Wei": [YE]}),
    ((420,), "Sixteen Kingdoms", [YAN_WEI_400, WEI_W_400, LLIANG_400, XIA_QIN_420],
     {"Toba Wei": [PINGCHENG, (112.55, 37.87)], "Northern Yan": [LONGCHENG], "Xia (Helian)": [(108.5, 37.5)],
      "Northern Liang": [GUZANG], "Western Qin": [(103.83, 36.06), (101.78, 36.62)]}),
    ((540,), "Eastern Wei", [WEI_SPLIT_540, LIANG_N_540],
     {"Eastern Wei": [YE], "Western Wei": [CHANGAN], "Liang (Xiao)": [JIANKANG, CHENGDU]}),
    ((560,), "Northern Qi", [QI_ZHOU_560, CHEN_N_560, WLIANG_LOOP],
     {"Northern Qi": [YE, (116.78, 32.58)], "Northern Zhou": [CHANGAN, CHENGDU, (112.12, 32.01)],
      "Western Liang (Xiao)": [JIANGLING], "Chen": [JIANKANG, CHANGSHA]}),
    ((580,), "Northern Zhou", [CHEN_N_560, WLIANG_LOOP],
     {"Northern Zhou": [CHANGAN, YE, CHENGDU], "Western Liang (Xiao)": [JIANGLING], "Chen": [JIANKANG, CHANGSHA]}),
    ((383,), "Jin", [QIN_JIN_383], {"Former Qin": [(112.1, 32.05), CHENGDU, (117.2, 34.25)], "Jin": [JIANKANG]}),
    ((910,), "Later Liang", [HAN_S_950, SHU_E_950, CHU_W_950, SHAN_N_950, CHU_E_950, JINGNAN_950, WUYUE_910, MIN_910, JIN_910,
                             YAN_910, QI_910],
     {"Later Liang": [KAIFENG], "Jin (Hedong)": [TAIYUAN], "Yan (Youzhou)": [(116.4, 39.9)], "Qi (Fengxiang)": [(107.4, 34.5)],
      "Former Shu": [CHENGDU, GUIZHOU], "Wu (Yang)": [YANGZHOU], "Wuyue": [HANGZHOU], "Min": [FUZHOU], "Ma Chu": [CHANGSHA],
      "Southern Han": [GUANGZHOU], "Jingnan": [JIANGLING]}),
    ((926,), "Later Tang", [HAN_S_950, SHU_E_950, CHU_W_950, SHAN_N_950, CHU_E_950, JINGNAN_950, WUYUE_910, MIN_910],
     {"Later Tang": [KAIFENG, CHENGDU, GUIZHOU], "Wu (Yang)": [YANGZHOU], "Wuyue": [HANGZHOU], "Min": [FUZHOU], "Ma Chu": [CHANGSHA],
      "Southern Han": [GUANGZHOU], "Jingnan": [JIANGLING]}),
    ((938,), "Later Jin", [HAN_S_950, SHU_E_950, CHU_W_950, SHAN_N_950, CHU_E_950, JINGNAN_950, WUYUE_910, MIN_910],
     {"Later Jin": [KAIFENG], "Later Shu": [CHENGDU, GUIZHOU], "Southern Tang": [JIANKANG], "Wuyue": [HANGZHOU], "Min": [FUZHOU],
      "Ma Chu": [CHANGSHA], "Southern Han": [GUANGZHOU], "Jingnan": [JIANGLING]}),
    ((950,), "Later Han", [HAN_S_950, SHU_E_950, CHU_W_950, SHAN_N_950, CHU_E_950, JINGNAN_950, WUYUE_950, QINGYUAN],
     {"Later Han": [KAIFENG], "Later Shu": [CHENGDU, GUIZHOU], "Southern Tang": [JIANKANG], "Wuyue": [HANGZHOU], "Qingyuan": [QUANZHOU],
      "Ma Chu": [CHANGSHA], "Southern Han": [GUANGZHOU], "Jingnan": [JIANGLING]}),
    ((958,), "Later Zhou", [ZHOU_S_958, SHU_E_950, CHU_W_950, SHAN_N_958, CHU_E_950, JINGNAN_950, WUYUE_950, QINGYUAN, NHAN_958],
     {"Later Zhou": [KAIFENG], "Northern Han": [TAIYUAN], "Later Shu": [CHENGDU, GUIZHOU], "Southern Tang": [JIANKANG],
      "Wuyue": [HANGZHOU], "Qingyuan": [QUANZHOU], "Wuping": [CHANGSHA], "Southern Han": [GUANGZHOU], "Jingnan": [JIANGLING]}),
    ((970,), "Song Empire", [ZHOU_S_958, CHU_E_950, SHAN_N_958, WUYUE_950, QINGYUAN, NHAN_958],
     {"Song Empire": [KAIFENG, CHENGDU, CHANGSHA, JIANGLING, GUIZHOU], "Northern Han": [TAIYUAN], "Southern Tang": [JIANKANG],
      "Wuyue": [HANGZHOU], "Qingyuan": [QUANZHOU], "Southern Han": [GUANGZHOU]}),
    ((1142,), "Song Empire", [SHAOXING], {"Jurchen Jin": [KAIFENG], "Song Empire": [HANGZHOU]}),
]

# ASSIGN: (years, area, NAME or None, keep): all land inside the area (a ring of points) goes to NAME, or becomes unrecorded
# land for None, whoever held it, except the polities named in keep. Applied after CUT and SPLIT, in order.
ASSIGN = []

# ---------------------------------------------------------------------------------------------------------------------
# Corrections from the map audit of November 2026: polities the source puts in the wrong place, under a name they did
# not yet bear or beyond their real extent, and polities it leaves out. Areas are rough outlines, or boxes where the edge
# runs through steppe, desert or sea.
rect = lambda w, s, e, n: [(w, s), (e, s), (e, n), (w, n)]

LINEAGE_NAMES["vietnam"] += ["Vạn Xuân", "Ngô dynasty", "Đại Cồ Việt", "Đại Ngu"]  # also their identity group
IDENTITY_GROUPS["nanzhao"].append("Six Zhaos")
PEOPLES |= {"Northern Hu peoples", "Rong and Di", "Sushen", "Tarim basin cultures", "Western Regions oasis states", "Dingling",
            "Wuhuan", "Samhan", "Tatar tribes", "Andronovo culture", "Mon-Khmer", "Qiang", "Kurykans"}
VARIANTS["Southern Tang"] = [(lambda y: y == 938, "qi")]  # the state was called Qi until 939
RENAMES.update({
    "Xiongnu": [(lambda y: y in (-453, -350), "Northern Hu peoples")],  # the Xiongnu are attested from the 3rd century BC
    "Proto-Thai cultures": [(lambda y: y in (-453, -350), "Rong and Di")],  # the 400 layer puts them in north China
    "Donghu tribes": [(lambda y: y in (-453, -350), "Sushen")],  # the 400 layer puts the Donghu on the Amur
    "Achaemenid Empire": [(lambda y: y < -550, "Median Empire")],
    "Karasuk culture": [(lambda y: y < -1500, "Andronovo culture")],
    "Turcik tribes": [(lambda y: y < 500, "Dingling")],
    "Mauryan Empire": [(lambda y: y > -185, "Shunga Empire")],
    "Kushan Empire": [(lambda y: y < 30, "Yuezhi")],  # the Da Yuezhi in Bactria before the Kushans
    "Gupta Empire": [(lambda y: y < 320, "Hindu kingdoms")],
    "Silia": [(lambda y: y == -1, "Samhan"), (always, "Silla")],
    "Silla": [(lambda y: y == -1, "Samhan")],  # Silla was then a statelet around Gyeongju
    "Uyghurs": [(lambda y: y in (700, 742), "Tibetan Empire"),  # the 700 layer's "Uyghurs" sit in the Qaidam
                (lambda y: y == 900, "Tatar tribes")],  # the khaganate fell in 840
    "Rajput Clans and Small States": [(lambda y: y == 800, "Mon-Khmer")],  # the 800 layer's label for mainland South-East Asia
    "Annam": [(lambda y: y < 939, "Tĩnh Hải"), (lambda y: y < 968, "Ngô dynasty"), (lambda y: y < 1054, "Đại Cồ Việt"),
              (lambda y: y == 1400, "Đại Ngu"), (lambda y: y < 1804, "Đại Việt")],
    "Đại Việt": [(lambda y: y == 1400, "Đại Ngu")],  # the Hồ dynasty's name, 1400–1407
    "Pyu state": [(lambda y: y >= 1000, "Pagan")],  # the Pyu city-states were gone by then
    "Bagan": [(always, "Pagan")],
    "Kingdom of Pagan": [(always, "Pagan")],
    "Kingdom of Sukhotai": [(lambda y: y < 1238, "Mon-Khmer")],  # founded 1238
    "Bundelkhand": [(lambda y: y == 1800, "East India Company")],  # the 1800 layer's polygon is mostly Bengal and Bihar
})
OVERLORD_FIXES.update({
    "Protectorate of the Western Regions": [(always, "Han")],
    "Goryeo": [(lambda y: y == 1279, "Great Khanate")],  # a Yuan vassal from 1270
    "Kingdom of Qocho": [(lambda y: y == 1142, "Kara Khitai Khaganate")],
    "Chagatai Khanate": [(lambda y: y == 1279, "")],  # Kaidu's ally, at war with Kublai
    "Khoshut Khanate": [(lambda y: y == 1715, "Qing Empire")],
})

# the Tarim basin (without the Hexi end of WESTERN_REGIONS)
TARIM = [(73.5, 39.0), (75.0, 40.6), (78.0, 41.8), (80.5, 42.2), (83.0, 42.8), (86.0, 43.2), (89.0, 43.6), (91.5, 43.2), (92.0, 41.5),
         (91.0, 39.5), (89.0, 38.5), (86.0, 37.0), (82.0, 36.0), (79.0, 36.0), (76.5, 36.6), (75.0, 37.2), (73.8, 38.2)]
HEXI_CORRIDOR = [(92.8, 39.6), (93.5, 41.0), (96.5, 41.2), (99.0, 40.6), (101.5, 39.7), (103.8, 38.6), (104.2, 37.0), (103.0, 36.4),
                 (101.5, 37.0), (100.0, 38.0), (98.0, 38.9), (95.5, 39.4)]
ORDOS = [(105.8, 37.6), (106.0, 41.6), (110.9, 41.6), (110.9, 40.3), (110.6, 39.0), (110.4, 37.8), (108.6, 37.3), (107.0, 37.3)]
LINGNAN = [(104.6, 22.9), (105.2, 24.4), (107.6, 25.2), (110.0, 25.8), (112.6, 25.5), (114.6, 25.0), (116.2, 24.8), (117.2, 24.0),
           (117.3, 23.4), (116.6, 22.6), (114.0, 22.0), (111.0, 21.0), (109.6, 21.4), (108.0, 21.5), (106.6, 21.9)]
HAINAN_ISLAND = [(108.4, 18.0), (108.4, 20.3), (110.3, 20.3), (111.2, 19.5), (110.0, 18.0)]
DONGHU = [(116.0, 41.2), (116.2, 43.6), (118.2, 45.6), (121.5, 45.9), (123.6, 44.4), (123.4, 42.4), (121.5, 41.2), (118.8, 40.9)]
GOJOSEON = [(123.6, 40.4), (124.6, 41.6), (126.2, 41.6), (127.6, 40.4), (127.4, 38.6), (126.4, 38.0), (125.0, 38.2), (124.0, 39.2)]
DIAN = [(102.0, 24.0), (101.9, 25.5), (102.7, 26.0), (103.6, 25.6), (103.6, 24.3), (102.8, 23.8)]
YELANG = [(104.2, 25.0), (104.4, 26.8), (105.4, 27.8), (106.8, 27.6), (107.6, 26.6), (107.2, 25.2), (105.8, 24.8)]
AU_LAC = [(104.6, 20.0), (104.7, 21.6), (105.8, 22.5), (107.0, 22.0), (107.4, 21.5), (106.6, 20.3), (106.0, 19.8)]
BUYEO = [(124.0, 43.0), (124.2, 45.6), (125.6, 46.6), (127.6, 46.4), (128.6, 45.0), (127.8, 43.3), (126.0, 42.8)]
XIANBEI = [(98.0, 41.5), (98.0, 49.5), (110.0, 50.5), (120.0, 50.5), (125.0, 48.5), (124.5, 44.5), (122.0, 42.6), (118.0, 41.8),
           (114.0, 41.7), (111.5, 41.4), (107.5, 41.6), (104.0, 42.0), (101.0, 42.0)]
NORTH_FRONTIER_262 = [(105.8, 37.6), (105.9, 41.9), (114.2, 42.2), (114.3, 40.7), (113.0, 39.8), (111.6, 39.3), (110.8, 38.4), (110.2, 37.5),
                      (108.5, 37.1), (107.0, 37.2)]  # the Hetao and Ordos, given up by Cao Cao in 215
HWANGHAE = [(125.3, 37.6), (125.3, 38.9), (126.5, 39.2), (127.6, 38.8), (127.6, 37.7), (126.6, 37.6)]  # southern Lelang, Daifang
SAMHAN = [(125.8, 34.0), (126.0, 37.0), (126.6, 37.6), (127.6, 37.7), (128.6, 37.9), (129.6, 37.0), (129.8, 35.0), (128.5, 34.4)]
# Korea in the Three Kingdoms period: Goguryeo's southern edge before 475, from 475 to 551, and after Silla took the Han basin
KOG_S_439 = [(124.0, 37.6), (124.0, 39.6), (129.8, 39.6), (129.8, 37.3), (128.5, 37.4), (127.2, 37.8), (126.4, 37.9), (125.5, 37.7)]
KOG_S_500 = [(124.0, 37.0), (124.0, 39.6), (129.8, 39.6), (129.8, 36.9), (128.6, 36.8), (127.6, 37.0), (126.7, 37.1), (125.8, 36.9)]
KOG_S_560 = [(124.0, 37.7), (124.0, 39.6), (128.0, 39.6), (128.2, 38.6), (127.4, 38.2), (126.6, 37.9), (125.6, 37.7)]
SILLA_439 = [(127.4, 34.6), (127.9, 35.6), (127.8, 36.6), (128.4, 37.0), (129.8, 37.3), (129.8, 35.0), (129.0, 34.6)]
SILLA_560 = [(127.4, 34.6), (127.9, 35.6), (127.3, 36.3), (126.7, 36.9), (126.3, 37.3), (126.6, 37.9), (127.4, 38.2), (128.2, 38.6),
             (128.0, 39.6), (129.8, 39.6), (129.8, 35.0), (129.0, 34.6)]
PAEKCHE_439 = [(125.8, 34.2), (126.0, 36.7), (126.4, 37.6), (127.3, 37.8), (127.8, 37.0), (127.9, 35.6), (127.4, 34.6), (126.6, 34.2)]
PAEKCHE_500 = [(125.8, 34.2), (126.0, 36.7), (126.7, 37.1), (127.6, 37.0), (127.9, 35.6), (127.4, 34.6), (126.6, 34.2)]
PAEKCHE_560 = [(125.8, 34.2), (126.0, 36.6), (126.6, 36.9), (127.3, 36.3), (127.9, 35.6), (127.4, 34.6), (126.6, 34.2)]
GAYA = [(127.8, 34.8), (127.7, 35.6), (128.4, 35.9), (128.9, 35.3), (128.8, 34.9), (128.3, 34.7)]
TUYUHUN = [(94.0, 35.2), (94.5, 37.9), (97.0, 38.6), (99.5, 38.0), (100.6, 37.2), (100.8, 36.0), (101.5, 34.8), (101.0, 33.6), (98.5, 33.3),
           (96.0, 33.9)]
GAOCHANG = [(88.2, 42.4), (88.0, 43.3), (89.5, 43.6), (91.2, 43.2), (91.3, 42.3), (89.8, 42.0)]
VAN_XUAN = [(104.0, 21.0), (104.2, 22.4), (105.6, 22.9), (106.8, 22.4), (107.4, 21.6), (106.6, 20.5), (106.0, 19.6), (105.2, 19.4), (104.3, 20.2)]
CUAN = [(100.4, 23.0), (100.2, 26.4), (102.0, 26.8), (104.0, 26.6), (106.5, 26.2), (106.5, 23.0)]
NANZHAO_742 = [(98.6, 24.0), (98.5, 25.2), (99.0, 26.4), (99.6, 27.4), (100.6, 27.6), (101.3, 26.8), (101.5, 25.6), (101.2, 24.5), (100.4, 23.8),
               (99.4, 23.6)]
SIX_ZHAOS = [(99.7, 24.9), (99.6, 25.9), (100.0, 26.6), (100.6, 26.5), (100.9, 25.6), (100.6, 24.8), (100.1, 24.6)]
NANZHAO_800 = [(97.5, 24.0), (97.8, 25.8), (98.6, 27.2), (99.4, 28.3), (100.6, 28.0), (101.4, 27.3), (102.2, 26.8), (103.0, 26.6), (104.0, 26.3),
               (104.5, 25.0), (104.4, 23.6), (103.6, 22.6), (102.3, 21.8), (101.0, 21.6), (100.0, 21.9), (99.0, 22.3), (98.2, 23.0)]
TANG_SW_800 = [(104.4, 21.6), (104.4, 26.9), (106.5, 27.0), (109.5, 26.5), (109.5, 21.6)]  # Guangxi, Guizhou and east Yunnan
BALHAE_700 = [(127.0, 42.0), (126.8, 43.4), (127.6, 44.6), (129.0, 44.8), (130.2, 44.0), (130.0, 42.6), (128.6, 41.9)]
BALHAE_742 = [(125.0, 41.5), (125.4, 43.6), (126.5, 45.6), (128.5, 46.4), (131.5, 46.2), (134.0, 45.0), (133.0, 42.8), (130.7, 42.3),
              (129.5, 41.0), (128.0, 40.2), (126.5, 40.0), (125.0, 40.3)]
LIAODONG_PEN = [(121.0, 38.6), (121.2, 40.0), (122.2, 41.2), (123.6, 41.9), (124.6, 41.0), (124.2, 39.8), (122.5, 39.0)]
MANCHURIA_N = [(121.5, 46.0), (121.5, 53.5), (137.5, 54.0), (141.5, 52.5), (141.5, 46.0), (134.0, 45.0), (131.5, 46.2), (128.5, 46.4),
               (126.5, 45.6)]
QOCHO = [(86.0, 41.6), (85.5, 43.0), (86.5, 44.6), (88.5, 45.2), (91.0, 45.0), (93.5, 44.2), (95.0, 43.0), (94.5, 41.8), (92.0, 41.5),
         (89.0, 41.3)]
KHOTAN = [(78.0, 36.4), (78.0, 37.8), (80.0, 38.2), (82.0, 38.0), (83.5, 37.6), (83.5, 36.3), (80.5, 35.9)]
KASHGAR = [(73.5, 39.0), (75.0, 40.6), (77.5, 41.3), (78.5, 40.2), (78.0, 38.4), (76.0, 37.8), (74.5, 38.0)]
GUIYI = [(93.0, 39.4), (92.8, 40.6), (94.5, 41.2), (96.5, 41.0), (97.6, 40.3), (97.3, 39.4), (95.0, 39.1)]
GANZHOU = [(97.6, 39.6), (98.5, 40.3), (100.5, 39.9), (101.8, 39.2), (101.5, 38.2), (99.5, 38.4), (98.0, 39.0)]
KYRGYZ = [(86.5, 50.5), (87.0, 53.5), (89.5, 55.6), (92.5, 56.0), (95.5, 54.5), (98.5, 52.6), (99.0, 50.6), (96.0, 49.8), (92.0, 49.9),
          (89.0, 49.6)]  # the Minusinsk basin and Tuva
XIONGNU_221 = [(104.5, 41.0), (104.0, 43.5), (106.5, 46.0), (110.5, 47.0), (113.5, 45.5), (113.8, 42.5), (113.0, 40.8), (110.9, 40.3),
               (107.0, 40.6)]
DONGHU_221 = [(113.5, 41.0), (113.0, 45.0), (115.5, 48.5), (119.5, 50.5), (123.5, 50.0), (126.5, 47.0), (125.0, 44.0), (123.5, 42.0),
              (120.0, 41.0), (116.5, 41.0)]
YUEZHI_221 = [(92.0, 38.5), (90.5, 42.0), (91.0, 45.5), (95.0, 47.0), (100.0, 46.0), (104.5, 43.0), (104.5, 38.5), (100.0, 37.6), (96.0, 37.8)]
EAST_OF_KHINGAN = [(121.5, 41.0), (122.3, 44.0), (121.2, 46.5), (120.0, 48.5), (120.5, 51.0), (122.5, 54.0), (141.0, 56.0), (141.0, 40.0)]
NORTHERN_HU = [(100.0, 41.5), (98.5, 44.0), (99.5, 47.0), (103.0, 49.2), (108.0, 50.0), (113.0, 49.6), (116.5, 47.8), (117.5, 45.0),
               (116.0, 42.6), (113.5, 41.4), (110.9, 41.6), (106.0, 41.6), (103.0, 41.4)]  # the Mongolian plateau
PLATEAU = [(78.0, 35.5), (80.0, 32.5), (82.0, 30.0), (85.0, 28.5), (88.0, 27.8), (92.0, 27.6), (95.0, 28.0), (97.5, 27.5), (99.0, 26.5),
           (101.5, 26.8), (103.0, 28.5), (104.5, 31.0), (104.0, 34.0), (102.0, 36.0), (99.0, 37.0), (96.0, 37.5), (92.0, 37.8), (88.0, 37.0),
           (84.0, 36.5), (80.0, 36.0)]  # the Tibetan plateau
EAST_OF_LIAO = [(120.5, 38.4), (121.5, 41.0), (122.0, 43.5), (121.0, 47.0), (136.0, 47.0), (136.0, 38.4)]
TAEBONG = [(124.0, 37.0), (124.0, 39.6), (127.6, 39.6), (129.0, 38.6), (129.6, 37.2), (128.6, 37.0), (127.9, 36.6), (127.5, 36.6), (126.8, 36.9),
           (125.8, 36.6)]
LATER_BAEKJE = [(125.6, 33.9), (125.8, 36.6), (126.8, 36.9), (127.5, 36.6), (127.9, 35.6), (127.6, 34.5), (126.8, 33.9)]
SILLA_SE = [(127.6, 34.5), (127.9, 35.6), (127.9, 36.6), (128.6, 37.0), (129.6, 37.2), (129.8, 35.0), (129.0, 34.5)]
KOREA_N_900 = [(124.0, 39.6), (124.0, 42.0), (130.0, 43.0), (130.5, 42.0), (129.0, 40.5), (127.6, 39.6)]
KOREA_S = [(124.5, 33.0), (124.5, 38.0), (126.5, 38.3), (129.0, 38.0), (130.2, 37.3), (130.2, 34.5), (128.0, 33.0)]
LIAO_N_EARLY = [(110.5, 41.2), (108.0, 43.0), (108.5, 46.5), (111.0, 48.5), (116.0, 49.5), (120.5, 50.0), (124.0, 49.5), (126.5, 48.0),
                (127.6, 46.5), (126.8, 44.8), (125.5, 43.8), (123.0, 43.4), (120.0, 43.4), (117.0, 43.0), (114.0, 42.2)]
LIAO_N = [(110.5, 41.2), (106.5, 42.5), (104.0, 45.0), (103.8, 47.8), (106.0, 49.0), (111.0, 49.8), (116.0, 50.0), (120.5, 50.5), (124.0, 50.0),
          (126.5, 48.5), (127.6, 46.5), (126.8, 44.8), (125.5, 43.8), (123.0, 43.4), (120.0, 43.4), (117.0, 43.0), (114.0, 42.2)]
JURCHENS_1100 = [(126.6, 44.0), (126.8, 46.5), (128.5, 48.0), (132.0, 48.0), (134.5, 46.5), (133.0, 43.5), (130.5, 42.5), (128.5, 42.5)]
YINCHUAN = [(105.4, 36.9), (105.2, 38.0), (105.8, 39.6), (106.9, 39.9), (107.3, 38.8), (107.0, 37.3), (106.2, 36.7)]
EJIN = [(99.8, 40.2), (99.8, 42.4), (102.2, 42.4), (102.2, 40.2)]
HEHUANG = [(100.8, 35.3), (100.8, 37.3), (102.5, 37.4), (104.0, 36.6), (104.2, 35.4), (102.5, 35.0)]
XINING_1142 = [(100.8, 36.0), (100.8, 37.3), (103.0, 37.3), (103.0, 36.0)]
JIANCHANG = [(101.2, 26.3), (101.4, 27.6), (102.2, 28.6), (102.6, 29.3), (103.2, 29.2), (103.6, 28.3), (104.3, 27.8), (104.6, 27.0), (104.2, 26.4),
             (103.0, 26.1), (102.0, 26.0)]
TENGCHONG = [(97.8, 24.0), (97.6, 25.2), (98.2, 26.6), (99.0, 26.4), (99.3, 25.0), (98.8, 24.0)]
NW_YUNNAN = [(98.5, 25.5), (98.6, 27.6), (100.4, 27.8), (101.2, 26.9), (100.8, 25.6)]
DIQING = [(98.6, 27.6), (98.8, 29.0), (100.5, 28.9), (100.4, 27.8)]
HARIPUNJAYA = [(98.2, 17.6), (98.0, 19.6), (99.0, 20.4), (100.6, 20.0), (100.4, 17.8), (99.2, 17.2)]
UPPER_BURMA = [(94.0, 21.5), (94.2, 24.5), (96.0, 26.5), (97.4, 25.8), (97.6, 23.6), (96.6, 21.5)]
KOREA_NW_1279 = [(124.0, 38.6), (124.0, 40.8), (126.0, 41.0), (127.2, 40.0), (126.8, 38.8)]
KOREA_NE_1279 = [(127.2, 39.2), (127.2, 41.6), (129.0, 42.6), (130.5, 42.5), (129.8, 41.0), (128.4, 39.6)]
# Ming and Qing
MING_WALL_N = [(97.5, 40.3), (98.2, 39.8), (99.6, 39.4), (100.9, 38.9), (102.6, 38.2), (104.2, 37.6), (105.2, 37.5), (106.3, 38.5),
               (107.8, 38.0), (109.7, 38.3), (110.8, 39.0), (111.5, 39.4), (112.5, 40.1), (113.3, 40.4), (114.9, 40.9), (116.0, 40.6),
               (117.2, 40.7), (118.5, 40.4), (119.8, 40.1), (120.6, 40.8), (121.6, 41.7), (122.6, 42.3), (123.8, 42.6), (124.3, 42.3),
               (124.3, 47.0), (97.5, 47.0)]  # north of the Ming Great Wall and the Liaodong border wall
ORDOS_1500 = [(106.2, 38.4), (106.0, 41.5), (111.6, 41.6), (111.6, 39.6), (110.9, 39.0), (110.0, 38.4), (108.0, 37.9)]
JIUQUAN = [(97.6, 38.8), (97.6, 40.6), (100.2, 40.2), (100.2, 38.8)]
KOKONOR = [(90.0, 35.5), (90.5, 38.6), (93.5, 39.4), (96.5, 39.2), (98.5, 38.8), (100.5, 38.0), (101.4, 37.0), (101.6, 35.5), (100.8, 34.2),
           (98.0, 33.8), (94.5, 34.0), (91.5, 34.5)]
DZUNGAR_EAST_1715 = [(92.6, 37.0), (92.6, 43.0), (93.0, 44.6), (95.0, 46.0), (95.0, 51.0), (106.0, 51.0), (106.0, 37.0)]
# the whole island with Green and Orchid Islands: Taiwan Prefecture of Fujian from 1684 (the Qing settled the western plains;
# the mountains and the east coast were left to the indigenous peoples until 1875, but lay within the prefecture)
TAIWAN = [(120.55, 21.6), (119.95, 22.5), (119.9, 23.4), (120.4, 25.0), (121.4, 25.5), (122.15, 25.15), (121.95, 24.0), (121.75, 22.0),
          (121.0, 21.6)]
LAN_XANG = [(100.4, 19.5), (101.0, 21.6), (102.2, 22.4), (103.4, 21.6), (104.2, 20.7), (104.8, 19.4), (105.8, 18.0), (106.0, 16.5), (105.4, 15.0),
            (104.0, 14.6), (103.0, 15.6), (102.0, 17.8), (101.0, 17.9), (100.5, 18.6)]
LAN_NA = [(97.6, 17.6), (97.8, 19.6), (98.8, 20.6), (100.4, 20.5), (100.8, 19.0), (100.3, 17.6), (99.0, 17.2)]
TUMEN_S = [(126.0, 41.0), (126.4, 41.8), (127.4, 41.6), (128.3, 42.0), (129.0, 42.4), (129.8, 42.9), (130.6, 42.4), (130.2, 41.6), (128.5, 40.8)]
YANBIAN = [(127.5, 42.2), (127.8, 44.0), (131.6, 44.0), (131.0, 42.6), (129.8, 42.9), (129.0, 42.4), (128.3, 42.0)]
VN_NORTH = [(102.2, 21.5), (102.4, 22.4), (103.4, 22.8), (104.4, 22.9), (105.4, 23.2), (106.6, 22.9), (107.0, 22.4), (108.0, 21.6), (107.6, 21.4),
            (106.0, 21.4)]
SICHUAN_S_1650 = [(101.5, 28.0), (101.8, 30.6), (103.5, 30.9), (105.5, 30.8), (107.5, 30.6), (109.5, 30.2), (109.0, 28.5), (107.0, 28.2), (104.5, 27.8)]
LIJIANG = [(98.8, 26.3), (98.9, 28.6), (100.5, 28.6), (101.5, 27.4), (101.0, 26.3)]
ARUNACHAL = [(91.6, 27.8), (91.7, 29.0), (94.0, 29.4), (96.0, 29.5), (97.4, 28.4), (96.9, 27.9), (96.0, 27.9), (95.3, 27.8), (94.5, 27.6),
             (93.8, 27.35), (92.8, 27.1), (92.0, 26.95)]  # the hills north of the Brahmaputra valley
RYUKYU = rect(123.4, 24.0, 130.4, 28.6)
DYNASTY = {910: "Later Liang", 926: "Later Tang", 938: "Later Jin", 950: "Later Han", 958: "Later Zhou", 970: "Song Empire", 1000: "Song Empire"}
FIVE = tuple(DYNASTY)

CUT += [
    # 1000–700 BC: Wu was a small polity south of the Yangtze; the rest of the source's Sinic block was Rong, Di, Yi and Yue
    *[(ys, "Wu", a, "Zhou states") for ys in [(-1000, -800, -700)] for a in (rect(115, 32.3, 123, 36), rect(115, 29, 118.5, 32.3))],
    ((-1000, -800, -700), "Sinic", EAST_OF_LIAO, "Sushen"),
    ((-1000, -800, -700), "Sinic", rect(100, 38.4, 136, 47), "Rong and Di"),
    ((-1000, -800, -700), "Sinic", rect(100, 18, 124, 29.6), "Baiyue"),
    # 453 and 350 BC: Gojoseon between the Liao and the Taedong
    ((-453, -350), "Gojoseon", rect(127.8, 30, 145, 56), "Sushen"),
    ((-453, -350), "Gojoseon", rect(118, 42.8, 127.8, 56), "Sushen"),
    ((-453, -350), "Gojoseon", rect(118, 30, 127.8, 38.4), "Paleo-Koreans"),
    ((-300,), "Qin", rect(95, 26, 103, 35), "Qiang"),
    # 221 BC: before Modu the Xiongnu held the Yinshan and Ordos; the Donghu the east, the Yuezhi the west
    ((-221,), "Xiongnu", WORLD, "Dingling"),  # redrawn below: the Xiongnu, the Donghu and the Yuezhi
    *[((y,), "Xiongnu", EAST_OF_KHINGAN, "Tungus") for y in (-200, -100, -1)],  # Manchuria was Buyeo, Wuhuan and others
    *[((y,), n, PLATEAU, "Qiang") for y in (-221, -200) for n in ("Thai", "Yuezhi")],
    *[((y,), "Yuezhi", TARIM, "Western Regions oasis states") for y in (-221, -200)],
    ((100, 200), "Southern Xiongnu", WORLD, None),  # drawn in the Alxa Gobi; redrawn in the Ordos and Shanxi below
    ((-1,), "Koguryo", rect(127.3, 37, 135, 46), None),  # Goguryeo was then on the Hun and middle Yalu
    # 320–900
    ((320,), "Cheng Han", rect(95, 15, 110, 27.0), "Jin"),  # Ningzhou fell to the Cheng Han only in 334
    *[((y,), "Thai Kingdoms", CUAN, "Cuan clan") for y in (540, 560, 580, 589, 700, 742)],
    ((700,), "Balhae", WORLD, None),  # the 700 layer gives Balhae all of Goguryeo; it was founded small in 698
    ((700, 742), "Karluks", rect(96.5, 39.2, 102, 41.6), "Göktürks"),
    ((700, 742), "Nanzhao", WORLD, None),  # drawn in northern Burma; redrawn at Erhai below
    ((900,), "Oghuz Turks", rect(97, 45, 120, 58), "Kurykans"),
    ((900,), "Oghuz Turks", rect(75, 44, 97, 58), "Kimek-Kipchak khaganate"),
    # 910–1142: Dingnan held only Xia, Sui, Yin, You and Jingbian; the source's Xia reaches to Lop Nor
    *[((y,), "Dingnan", a, None) for y in FIVE for a in (rect(80, 36, 94.5, 44), rect(104, 39.7, 112, 43))],
    *[((y,), "Dingnan", YINCHUAN, DYNASTY[y]) for y in FIVE],  # Lingzhou was Chinese until 1002
    ((1100, 1142), "Xixia", rect(80, 36, 93.5, 44), None),
    ((1142,), "Kamarupa", WORLD, None),  # drawn over Kachin and north-west Yunnan; it was in Assam
    # 1400–1900
    ((1400,), "Ava", rect(97.0, 20.5, 102, 27.5), "Shan states"),
    ((1400,), "Ava", rect(94, 23.6, 97, 28), "Shan states"),
    ((1400,), "Champa", rect(105, 16.2, 109, 18), "Đại Ngu"),  # Thuận Hóa had been Vietnamese since 1306
    ((1500,), "Moghulistan", rect(88, 51, 140, 58), "Siberians"),  # the 1500 layer's stray Moghulistan pieces in Siberia
    ((1500,), "Moghulistan", rect(88, 49, 100, 51), "Oirat Confederation"),
    ((1500,), "Moghulistan", rect(100, 48, 140, 51), "Northern Yuan"),
    ((1500,), "Moghulistan", rect(110, 40.5, 125, 44), "Northern Yuan"),
    ((1600,), "Oirat Confederation", rect(100, 52, 145, 60), "Siberians"),
    ((1600,), "Oirat Confederation", rect(100, 40, 145, 52), "Northern Yuan"),
    ((1650,), "Dzungar Khanate", rect(100, 52.5, 145, 60), "Siberians"),
    ((1650,), "Dzungar Khanate", rect(100, 40, 145, 52.5), "Khalkha"),
    ((1600,), "Ming Chinese Empire", rect(124, 53.5, 132, 58), "Jurchens"),  # the Ming never held the upper Zeya
    ((1600,), "Tsardom of Muscovy", rect(60, 40, 75, 55.8), "Quazaq Khanate"),  # Russia's frontier was the Tara–Narym line
    ((1600,), "Tsardom of Muscovy", rect(75, 40, 92, 55.8), "Oirat Confederation"),
    ((1600,), "Tsardom of Muscovy", rect(92, 40, 150, 55.8), "Siberians"),
    ((1650,), "Tsardom of Muscovy", rect(85, 45, 100, 53.5), "Dzungar Khanate"),
    ((1650,), "Tsardom of Muscovy", rect(100, 45, 125, 53.5), "Khalkha"),
    ((1715,), "Dzungar Khanate", DZUNGAR_EAST_1715, "Qing Empire"),  # Hami, Barkol, Hexi, Alxa and Khalkha were Qing
    ((1800,), "central Asian khanates", rect(74, 36, 80, 42), "Qing Empire"),  # Kashgar was Qing from 1759
    ((1600,), "Laos", rect(98.8, 20.5, 100.3, 22), "Burmese kingdoms"),  # Kengtung
    ((1600,), "Laos", rect(99, 21.2, 101.6, 23), "Ming Chinese Empire"),  # Sipsongpanna
    ((1800,), "Rattanakosin Kingdom", rect(97, 21, 101.5, 24.5), "Burma"),
    ((1900,), "Rattanakosin Kingdom", rect(97, 21, 101.5, 24.5), "British Raj"),
    ((1900,), "British Raj", ARUNACHAL, "Qing Empire"),  # the McMahon Line dates from 1914
]

ASSIGN += [
    # 1750–260 BC
    *[((y,), TARIM, "Tarim basin cultures", ()) for y in (-1750, -1500, -1250, -1000, -800, -700, -650, -600, -500, -453, -350)],
    *[((y,), TARIM, "Western Regions oasis states", ()) for y in (-300, -260)],
    ((-500, -453), [(107.8, 35.9), (108.0, 37.8), (110.5, 37.9), (110.4, 35.8), (109.2, 35.6)], "Rong and Di",
     {"Jin (Spring and Autumn)", "Wei", "Zhao"}),  # the north Shaanxi plateau was not Qin's
    ((-500,), [(110.1, 34.0), (110.1, 34.9), (111.9, 34.95), (111.9, 34.0)], "Jin (Spring and Autumn)", ()),  # Xiao and Han passes
    ((-500,), [(111.9, 33.8), (111.9, 34.4), (113.1, 34.5), (113.1, 33.8)], "Zhou states", ()),  # the Yi and Luo valleys
    ((-700,), rect(115, 24, 123, 29.0), "Baiyue", ()),
    ((-453, -350, -300, -260), HEXI_CORRIDOR, "Yuezhi", {"Qin"}),
    ((-453, -350, -300), [(105.3, 35.4), (105.5, 37.0), (106.4, 37.9), (107.6, 37.8), (108.3, 36.8), (108.2, 35.6), (107.2, 35.2), (106.0, 35.1)],
     "Yiqu", ()),
    ((-453, -350), DONGHU, "Donghu tribes", {"Yan"}),
    ((-350,), [(109.4, 34.75), (109.3, 35.6), (109.4, 36.6), (109.6, 37.6), (110.0, 38.4), *along(YELLOW, (110.9, 38.4), (110.27, 34.64)),
               (109.9, 34.6)], "Wei", ()),  # Wei's west-of-the-river lands and Shang commandery, regained by Qin c. 330
    ((-453,), [(110.0, 26.0), (110.0, 28.8), (113.0, 29.0), (116.0, 29.2), (117.2, 28.8), (116.8, 27.5), (114.0, 27.5)], "Chu", {"Yue", "Ba and Shu"}),
    ((-350,), [(110.0, 26.0), (110.0, 28.8), (113.0, 29.0), (116.0, 29.2), (117.2, 28.8), (116.8, 27.0), (114.0, 26.0)], "Chu", {"Yue", "Ba and Shu"}),
    ((-300, -260), ORDOS, "Northern Hu peoples", {"Zhao"}),  # Linhu and Loufan; Qin took the Ordos only in 215
    ((-300, -260), NORTHERN_HU, "Northern Hu peoples", {"Zhao", "Yan"}),
    ((-300, -260), DONGHU, "Donghu tribes", {"Yan", "Zhao"}),
    ((-300, -260), GOJOSEON, "Gojoseon", {"Yan"}),
    ((-300, -260), LINGNAN, "Baiyue", {"Chu"}),
    ((-260,), DIAN, "Dian", ()),
    # 221 BC – AD 280
    ((-221,), DONGHU_221, "Donghu tribes", {"Qin Empire", "Tungus"}),
    ((-221,), YUEZHI_221, "Yuezhi", {"Qin Empire"}),
    ((-221,), XIONGNU_221, "Xiongnu", {"Qin Empire"}),
    ((-221, -200), ORDOS, "Xiongnu", ()),
    ((-221,), LINGNAN, "Baiyue", ()),  # Qin conquered Lingnan in 214
    ((-200,), LINGNAN, "Nan-Yue", ()),
    ((-200,), HAINAN_ISLAND, "Hainan", ()),
    ((-200,), [(119.2, 27.3), (119.0, 28.6), (120.0, 29.3), (121.6, 29.2), (121.5, 28.0), (120.6, 27.1)], "Dong'ou", ()),
    ((-221, -200), AU_LAC, "Âu Lạc", ()),
    ((-221, -200), GOJOSEON, "Gojoseon", {"Qin Empire", "Han"}),
    ((-221, -200), DIAN, "Dian", ()),
    ((-221, -200), YELANG, "Yelang", ()),
    ((-100,), HEXI_CORRIDOR, "Han", ()),
    ((-100,), [(124.0, 37.6), (124.2, 40.0), (125.5, 41.8), (127.5, 42.2), (129.8, 42.4), (129.8, 40.5), (128.6, 38.6), (127.0, 37.8), (126.0, 37.6)],
     "Han", ()),  # the four Korean commanderies
    ((-100,), [(100.0, 24.6), (100.4, 26.2), (101.3, 27.6), (102.2, 28.8), (103.5, 28.9), (104.5, 27.5), (104.6, 25.0), (103.8, 23.3), (102.5, 23.0),
               (101.2, 23.4)], "Han", ()),  # Yizhou and Yuexi
    ((-100,), [(104.6, 19.8), (106.0, 20.4), (106.6, 19.6), (107.3, 17.6), (108.4, 16.2), (107.8, 15.9), (106.6, 17.0), (105.6, 18.4), (104.8, 19.2)],
     "Han", ()),  # Jiuzhen and Rinan
    ((-1,), [(124.2, 37.6), (124.3, 39.0), (124.8, 40.3), (126.0, 40.5), (127.5, 40.0), (127.6, 38.6), (126.9, 37.8), (126.0, 37.6)], "Han", ()),
    ((-1,), [(128.7, 35.4), (128.7, 36.3), (129.5, 36.4), (129.6, 35.4)], "Silla", ()),
    ((-100, -1), [(117.0, 42.0), (117.2, 45.0), (119.5, 47.2), (121.8, 47.0), (122.6, 44.0), (121.5, 42.0), (119.0, 41.6)], "Wuhuan", {"Han"}),
    ((-100, -1, 100, 200, 262, 280), BUYEO, "Buyeo", {"Koguryo"}),
    ((-100, -1, 100), [(73.5, 42.2), (74.0, 44.0), (77.0, 45.6), (80.5, 46.4), (84.0, 45.6), (84.5, 43.6), (82.0, 42.6), (78.0, 41.8), (75.0, 41.6)],
     "Wusun", ()),
    ((-1, 100), TARIM, "Protectorate of the Western Regions", {"Han"}),
    ((100,), [(106.5, 37.6), (106.3, 40.2), (107.5, 41.3), (110.5, 41.4), (111.6, 40.6), (111.4, 39.2), (110.6, 38.0), (109.0, 37.4)],
     "Southern Xiongnu", ()),  # the chanyu's court at Meiji, in the Ordos
    ((200,), [(110.6, 36.0), (110.8, 38.6), (111.8, 39.4), (113.0, 39.0), (112.8, 37.6), (112.2, 36.2)], "Southern Xiongnu", ()),  # Pingyang
    ((100, 200), XIANBEI, "Xianbei", {"Han", "Southern Xiongnu", "Koguryo", "Buyeo"}),
    ((262, 280), XIANBEI, "Xianbei", {"Cao Wei", "Jin", "Koguryo", "Buyeo"}),
    ((262, 280), NORTH_FRONTIER_262, "Xianbei", ()),
    ((100, 200), HWANGHAE, "Han", ()),
    ((262,), HWANGHAE, "Cao Wei", ()),
    ((280,), HWANGHAE, "Jin", ()),
    ((100, 200, 262, 280), SAMHAN, "Samhan", {"Han", "Cao Wei", "Jin"}),  # the Han basin was Mahan, not Goguryeo
    ((100, 200, 262, 280), [(128.7, 35.4), (128.7, 36.3), (129.5, 36.4), (129.6, 35.4)], "Silla", ()),  # Saro, around Gyeongju
    ((280,), [(126.5, 36.9), (126.5, 37.75), (127.0, 37.85), (127.6, 37.7), (127.7, 37.2), (127.2, 36.85)], "Paekche", ()),
    ((200, 262, 280), [(107.0, 16.6), (107.6, 17.2), (108.6, 16.3), (109.5, 14.0), (108.8, 13.6), (108.0, 14.6)], "Linyi", ()),
    # 320–900
    *[((y,), TUYUHUN, "Tuyuhun", {"Southern Liang (Tufa)", "Western Qin"}) for y in (360, 383, 400, 420, 439, 500, 540, 560, 580, 589)],
    *[((y,), a, n, ()) for y in (383, 400, 420, 439) for a, n in ((KOG_S_439, "Koguryo"), (SILLA_439, "Silla"), (PAEKCHE_439, "Paekche"),
                                                                    (GAYA, "Gaya"))],
    *[((y,), a, n, ()) for y in (500, 540) for a, n in ((KOG_S_500, "Koguryo"), (SILLA_439, "Silla"), (PAEKCHE_500, "Paekche"), (GAYA, "Gaya"))],
    *[((y,), a, n, ()) for y in (560, 580, 589) for a, n in ((KOG_S_560, "Koguryo"), (SILLA_560, "Silla"), (PAEKCHE_560, "Paekche"))],
    ((560,), GAYA, "Gaya", ()),  # Gaya fell to Silla in 562
    ((500, 540, 560, 580, 589), GAOCHANG, "Gaochang", ()),
    ((560, 580, 589), VAN_XUAN, "Vạn Xuân", ()),  # the Early Lý, 544–602
    ((700,), SIX_ZHAOS, "Six Zhaos", ()),
    ((742,), NANZHAO_742, "Nanzhao", ()),
    ((700,), BALHAE_700, "Balhae", ()),
    ((700, 742), LIAODONG_PEN, "Tang Empire", ()),
    ((800, 900), LIAODONG_PEN, None, ()),  # Andong was given up in 758–761
    ((742, 800, 900), BALHAE_742, "Balhae", ()),
    ((700, 742, 800, 900), MANCHURIA_N, "Tungus", ()),  # Mohe and Shiwei, not Turks or Uyghurs
    ((800, 900), rect(104.4, 19.5, 109, 21.6), None, {"Tang Empire", "Champa"}),
    ((800, 900), TANG_SW_800, "Tang Empire", ()),
    ((800, 900), NANZHAO_800, "Nanzhao", ()),  # Nanzhao held Erhai and western Yunnan, not Guangxi
    ((900,), WESTERN_REGIONS, None, ()),  # the Tibetan empire had broken up by 842
    ((900,), QOCHO, "Kingdom of Qocho", ()),
    ((900,), KHOTAN, "Khotan", ()),
    ((900,), KASHGAR, "Karkhanids", ()),
    ((900,), GUIYI, "Guiyi Circuit", ()),
    ((900,), GANZHOU, "Ganzhou Uyghurs", ()),
    ((900, 910, 926, 938, 950, 958, 970, 1000, 1100), KYRGYZ, "Yenisei Kirghiz", ()),
    # 910–1279
    ((910,), TAEBONG, "Taebong", ()),
    ((910, 926), LATER_BAEKJE, "Later Baekje", ()),
    ((926,), SILLA_SE, "Silla", ()),
    ((910, 926), KOREA_N_900, None, ()),
    ((1100,), KOREA_S, "Goryeo", ()),
    ((926, 938, 950, 958, 970), LIAO_N_EARLY, "Liao", ()),
    ((1000, 1100), LIAO_N, "Liao", ()),
    ((1100,), JURCHENS_1100, "Jurchens", ()),
    ((1100,), MANCHURIA_N, "Tungus", ()),
    ((1100,), rect(83, 41.5, 107, 52), "Mongols", {"Xixia", "Liao", "Tibet"}),  # Naiman and Kereit lands, not Kipchak
    *[((y,), QOCHO, "Kingdom of Qocho", ()) for y in (910, 926, 938, 950, 958, 970, 1000, 1100, 1142)],
    *[((y,), KASHGAR, "Karkhanids", ()) for y in (910, 926, 938, 950, 958, 970, 1000)],
    *[((y,), KHOTAN, "Khotan", ()) for y in (910, 926, 938, 950, 958, 970, 1000)],
    ((1100,), rect(81.5, 41.0, 84.5, 42.5), "Karkhanids", ()),  # Kucha, Kara-Khanid by 1096
    ((1100, 1142), EJIN, "Xixia", ()),  # Kara-Khoto
    ((910, 926), HEHUANG, "Tibet", ()),
    ((1000,), HEHUANG, "Tsongkha", ()),
    ((1142,), XINING_1142, "Xixia", ()),  # taken from the Jin in 1136
    ((910, 926), JIANCHANG, "Dachanghe", ()),  # the Song–Dali border was the Dadu River
    ((938, 950, 958, 970, 1000, 1100, 1142), JIANCHANG, "Dali", ()),
    ((1100, 1142), NW_YUNNAN, "Dali", ()),
    ((1100, 1142), DIQING, "Tibet", ()),
    ((1142,), TENGCHONG, "Dali", ()),
    ((1279,), TENGCHONG, "Great Khanate", ()),
    ((1100,), HARIPUNJAYA, "Haripunjaya", ()),
    ((1100,), UPPER_BURMA, "Pagan", ()),
    ((1279,), KOREA_NW_1279, "Great Khanate", ()),  # Dongnyeong prefecture
    ((1279,), KOREA_NE_1279, "Great Khanate", ()),  # Ssangseong prefecture
    ((1279,), QOCHO, "Great Khanate", ()),  # the Qocho idiqut under the Yuan
    # 1400–1900
    ((1400,), LAN_XANG, "Lan Xang", {"Sukhothai"}),
    ((1400,), LAN_NA, "Lan Na", ()),
    ((1400,), VN_NORTH, "Đại Ngu", {"Lan Xang"}),
    ((1500,), VN_NORTH, "Đại Việt", {"Laos"}),
    ((1400, 1500), YANBIAN, "Jurchens", ()),
    ((1500,), TUMEN_S, "Korea", ()),
    ((1400, 1500, 1600), JIUQUAN, "Ming Chinese Empire", ()),
    ((1650, 1715), JIUQUAN, "Qing Empire", ()),
    ((1500,), ORDOS_1500, "Northern Yuan", ()),
    ((1600,), MING_WALL_N, "Northern Yuan", {"Jurchens", "Korea"}),
    ((1500, 1600), HAINAN_ISLAND, "Ming Chinese Empire", ()),
    ((1600,), KOKONOR, "Northern Yuan", {"Ming Chinese Empire"}),  # the Tümed in Kokonor
    ((1650, 1715), KOKONOR, "Khoshut Khanate", {"Qing Empire"}),
    ((1650,), SICHUAN_S_1650, "Post-Ming Warlords", ()),
    ((1650,), LIJIANG, "Post-Ming Warlords", ()),
    ((1715, 1800), TAIWAN, "Qing Empire", ()),
    ((1500, 1600, 1650, 1715, 1800), RYUKYU, "Ryukyu Kingdom", ()),
    ((1900,), RYUKYU, "Imperial Japan", ()),
    ((1900,), rect(120.9, 38.6, 122.3, 39.5), "Kwantung Leased Territory", ()),
    ((1900,), rect(119.9, 35.85, 120.6, 36.4), "Kiautschou Bay", ()),
    ((1900,), rect(121.9, 37.25, 122.4, 37.6), "Weihaiwei", ()),
    ((1900,), rect(110.1, 20.85, 110.6, 21.45), "Kwangchowan", ()),
]

# Second pass of the audit: smaller misplacements, mostly at the edges of the map
IDENTITY_GROUPS["Göktürks"] = ["Göktürks", "Eastern Turkic Khaganate"]  # the key keeps the identity the stories use
PEOPLES |= {"Northern Zone cultures", "Northeastern cultures", "Proto-Baiyue", "Tiefu Xiongnu"}
OVERLORD_FIXES["Kumul Khanate"] = [(always, "Qing Empire")]  # the Hami begs submitted in 1697
# the Ordos inside the Yellow River loop, closed to the south along the Great Wall line
ORDOS_LOOP = [*along(YELLOW, (111.12, 40.24), (110.42, 37.03)), (109.5, 36.8), (108.0, 36.8), (106.6, 37.1), (105.8, 37.5), (106.0, 37.9),
              (106.4, 38.5), (106.6, 39.0), (106.8, 39.6), (106.9, 40.2), (107.3, 40.6), (108.0, 40.65), (109.0, 40.45), (110.0, 40.45)]
NORTH_OF_TAEDONG = [(123.5, 38.6), (125.2, 38.7), (125.75, 39.05), (126.4, 39.25), (127.5, 39.25), (131.0, 39.4), (131.0, 42.0), (123.5, 42.0)]
GORYEO_N_970 = [(124.0, 39.55), (125.5, 39.6), (126.2, 39.8), (126.9, 39.7), (127.5, 39.45), (131.0, 39.45), (131.0, 43.5), (124.0, 43.5)]
CHEOLLI_N = [(124.9, 41.0), (125.4, 40.55), (125.9, 40.2), (126.6, 39.9), (127.4, 39.8), (127.7, 39.7), (131.0, 39.7), (131.0, 43.5),
             (124.9, 43.5)]  # beyond the Thousand-li Wall of 1033–1044, Jurchen land until 1107
PENGCHENG = [(116.7, 33.9), (116.7, 34.6), (117.5, 34.75), (117.9, 34.5), (117.7, 34.0), (117.2, 33.8)]
NEPAL = [(83.9, 27.6), (84.0, 28.4), (84.9, 28.6), (85.6, 28.3), (86.4, 27.95), (87.0, 27.7), (86.8, 27.2), (85.8, 27.2), (84.8, 27.4)]
LADAKH = [(75.6, 34.4), (76.0, 35.0), (77.0, 35.6), (78.0, 35.5), (79.4, 34.6), (79.5, 33.0), (78.8, 32.4), (77.8, 32.5), (76.8, 33.2),
          (76.0, 33.7)]
KASHMIR = [(73.7, 33.2), (73.6, 34.6), (74.5, 35.0), (75.6, 34.4), (75.6, 33.6), (75.0, 33.1)]
# the Brahmaputra valley from Sadiya down to Goalpara, in four stretches, and Manipur
AS_UP = [(93.2, 26.2), (93.2, 27.15), (93.8, 27.35), (94.5, 27.6), (95.3, 27.8), (96.0, 27.9), (96.2, 27.5), (95.8, 27.0), (95.2, 26.7),
         (94.4, 26.3), (93.6, 26.05)]
AS_MID = [(92.2, 25.95), (92.2, 27.0), (92.8, 27.1), (93.2, 27.15), (93.2, 26.2), (92.4, 25.95)]
AS_KAMRUP = [(90.9, 25.85), (90.9, 26.85), (91.5, 26.85), (92.2, 27.0), (92.2, 25.95), (91.6, 25.95)]
AS_GOALPARA = [(89.0, 25.9), (89.0, 26.7), (90.0, 26.8), (90.9, 26.85), (90.9, 25.85), (90.0, 25.8)]
MANIPUR = [(93.0, 23.9), (93.0, 25.6), (93.9, 25.7), (94.6, 25.5), (94.6, 24.0), (93.9, 23.8)]
KUMUL = [(91.5, 42.2), (91.8, 43.6), (93.0, 44.0), (94.8, 43.8), (96.2, 42.9), (95.6, 41.9), (93.5, 41.6)]
WEST_OF_PATKAI = rect(89, 22.5, 94.3, 28.5)  # Assam, Manipur and the Naga, Chin and Mizo hills
SINO_EARLY = (-1750, -1500, -1250)
NORTH_EARLY = [(100.0, 38.4), (114.0, 38.4), (114.8, 39.6), (115.8, 40.2), (117.5, 40.4), (119.0, 40.2), (120.0, 40.3), (121.5, 41.0),
               (122.0, 43.5), (121.0, 47.0), (100.0, 47.0)]  # north of the Yan mountains and of 38.4N further west
EARLY_OTHERS = {"Ainu", "Ancient Shu", "Andronovo culture", "Austro-Asiatic rice cultures", "Burmese", "Dongyi", "Dravidians",
                "Finno-Ugric taiga hunter-gatherers", "Gandhara grave culture", "Guifang", "Iranian pastoralists", "Karasuk culture",
                "Late Jomon culture", "Lower Xiajiadian culture", "Paleo-Koreans", "Paleo-Siberian hunter-gatherers",
                "Proto-Altaic pastoralists", "Proto-Shang", "Qiang", "Qijia culture", "Shang", "Tarim basin cultures", "Tibetans",
                "Vedic Aryans", "Xia (Erlitou)", "Zhou (pre-dynastic)"}  # everything but the Sinic block in those years
WEST_ZHOU = (-1000, -800, -700)
VIETNAM_FIVE = ("Tĩnh Hải", "Ngô dynasty", "Đại Cồ Việt")

CUT += [
    # 1000–700 BC: what is left of the source's "Sinitic peoples" block outside the Zhou states
    (WEST_ZHOU, "Sinic", rect(100, 30.15, 112.5, 38.4), "Rong and Di"),  # Gansu, Ningxia and the Lüliang
    (WEST_ZHOU, "Sinic", rect(100, 29, 106, 30.15), "Ba and Shu"),
    (WEST_ZHOU, "Sinic", rect(112.5, 30.8, 120, 33.5), "Zhou states"),  # the Zhou fiefs north of the Han and Huai
    (WEST_ZHOU, "Sinic", rect(112.5, 29, 120, 30.8), "Baiyue"),
    # 320–742
    ((320,), "Dai", ORDOS_LOOP, "Tiefu Xiongnu"),  # Liu Hu's Tiefu held the Ordos; the Tuoba were north of the river
    *[((y,), None, TARIM, "Western Regions oasis states") for y in (320, 360, 383, 400, 420, 439, 500, 540, 560, 580, 589)],
    *[((y,), None, rect(60, 40.5, 93, 52), "Göktürks") for y in (560, 580)],  # the western wing, from the Altai to the Aral
    ((589,), "Göktürks", rect(60, 35, 92.5, 60), "Western Gokturk Khaganate"),  # the khaganate split in 581–583
    ((589,), None, rect(60, 40.5, 93, 52), "Western Gokturk Khaganate"),
    ((589,), "Göktürks", WORLD, "Eastern Turkic Khaganate"),
    ((742,), "Türgesh", rect(60, 30, 68.6, 41.0), "Umayyad Caliphate"),  # Sogdia, retaken by Nasr ibn Sayyar by 741
    ((742,), "Türgesh", rect(68.6, 30, 80, 41.0), None),  # Ferghana and the Pamirs
    ((742,), None, rect(70, 41.0, 82.5, 47), "Türgesh"),  # the Chu and Ili valleys, the Türgesh homeland
    ((800, 900), "Silla", NORTH_OF_TAEDONG, None),  # Silla's frontier was the Taedong
    # 910–1142
    *[((y,), n, rect(104, 14, 109.5, 17.95), "Champa") for y in FIVE for n in VIETNAM_FIVE],  # the Hoành Sơn pass, until 1069
    *[((y,), "Kimek-Kipchak khaganate", rect(87.5, 42, 100, 58), "Tatar tribes") for y in FIVE],  # the Kimek were on the Irtysh
    *[((y,), None, rect(88, 42.5, 120, 52), "Tatar tribes") for y in FIVE],  # the Zubu of Liao sources
    *[((y,), "Goryeo", GORYEO_N_970, "Jurchens") for y in (926, 938, 950, 958, 970)],
    *[((y,), "Goryeo", CHEOLLI_N, "Jurchens") for y in (1000, 1100, 1142)],
    # 1400–1800
    ((1400,), "Northern Yuan", rect(80, 34, 92.8, 41.6), "Moghulistan"),  # Lop Nor and the Kunlun foothills
    ((1400,), "Northern Yuan", rect(92.8, 35, 97.7, 41.2), "Mongols"),  # Shazhou and the Qaidam, soon Ming garrisons
    ((1400,), "Moghulistan", rect(86, 45.5, 100, 52), "Oirat Confederation"),
    ((1400,), "Northern Yuan", rect(86, 45.5, 97, 53), "Oirat Confederation"),
    ((1400,), None, rect(87.5, 21.5, 92.0, 25.2), "Bengal"),  # the Ilyas Shahi sultanate
    ((1400,), "Sultanate of Delhi", rect(87.8, 21.5, 92.6, 27), "Bengal"),
    ((1400,), "Ava", WEST_OF_PATKAI, None),
    ((1500,), "Burmese kingdoms", WEST_OF_PATKAI, None),
    *[((y,), "Shan states", WEST_OF_PATKAI, None) for y in (1600, 1650, 1715)],
    ((1800,), "Burma", WEST_OF_PATKAI, None),  # Burma invaded Assam in 1817 and Manipur in 1819
]

ASSIGN += [
    # 1750–1250 BC: the source's "Sinitic peoples" block reaches from Jilin to Guizhou; only that block is redrawn, after the
    # Xia, Shang and their neighbours have been split from it
    *[((y,), a, n, EARLY_OTHERS) for y in SINO_EARLY for a, n in (
        (NORTH_EARLY, "Northern Zone cultures"), (EAST_OF_LIAO, "Northeastern cultures"),
        (rect(100, 18, 124, 29.6), "Proto-Baiyue"), (rect(117.5, 29.6, 123, 31.9), "Proto-Baiyue"))],
    ((-500,), PENGCHENG, "Song", ()),  # Pengcheng was Song's
    *[((y,), NEPAL, "Nepal", ()) for y in (1400, 1500, 1600, 1650, 1715)],  # the Malla kingdoms
    *[((y,), LADAKH, "Ladakh", ()) for y in (1500, 1600, 1650, 1715, 1800)],  # the Namgyal kingdom, independent until 1834
    ((1500,), KASHMIR, "Kashmir Sultanate", ()),
    ((1800,), KASHMIR, "Afghanistan", ()),  # Durrani Kashmir; the Sikhs took it in 1819
    ((1400,), AS_UP, "Ahom kingdom", ()),
    *[((1400,), a, "Kamata kingdom", ()) for a in (AS_KAMRUP, AS_GOALPARA)],
    *[((1500,), a, "Ahom kingdom", ()) for a in (AS_UP, AS_MID)],
    ((1500,), AS_KAMRUP, "Bengal", ()),  # Husain Shah took Kamata in 1498
    *[((1600, 1650), a, "Ahom kingdom", ()) for a in (AS_UP, AS_MID)],
    *[((1600,), a, "Koch kingdom", ()) for a in (AS_KAMRUP, AS_GOALPARA)],
    *[((1650,), a, "Mughal Empire", ()) for a in (AS_KAMRUP, AS_GOALPARA)],  # Mughal Kamrup, 1639–1658
    *[((1715, 1800), a, "Ahom kingdom", ()) for a in (AS_UP, AS_MID, AS_KAMRUP)],
    ((1715,), AS_GOALPARA, "Mughal Empire", ()),
    *[((y,), MANIPUR, "Manipur", ()) for y in (1400, 1500, 1600, 1650, 1715, 1800)],
    ((1715,), KUMUL, "Kumul Khanate", ()),
]
