import json
import os
import shutil

DICTIONARY = {
  "anivia": {
    "children": ["aniviaegg", "aniviaiceblock"]
  },
  "annie": {
    "children": ["annietibbers"]
  },
  "aphelios": {
    "children": ["apheliosturret"]
  },
  "aurora": {
    "children": ["auroraspirits"]
  },
  "azir": {
    "children": ["azirsoldier", "azirsundisc", "azirtowerclicker", "azirultsoldier"]
  },
  "bard": {
    "children": ["bardfollower", "bardhealthshrine", "bardpickup", "bardpickupnoicon", "bardportalclickable"]
  },
  "belveth": {
    "children": ["belvethspore", "belvethvoidling"]
  },
  "caitlyn": {
    "children": ["caitlyntrap"]
  },
  "cassiopeia": {
    "children": ["cassiopeia_death"]
  },
  "elise": {
    "children": ["elisespider", "elisespiderling"]
  },
  "fiddlesticks": {
    "children": ["fiddlestickseffigy"]
  },
  "fizz": {
    "children": ["fizzbait", "fizzshark"]
  },
  "gangplank": {
    "children": ["gangplankbarrel"]
  },
  "gnar": {
    "children": ["gnarbig"]
  },
  "heimerdinger": {
    "children": ["heimertblue", "heimertyellow"]
  },
  "illaoi": {
    "children": ["illaoiminion"]
  },
  "irelia": {
    "children": ["ireliablades"]
  },
  "ivern": {
    "children": ["ivernminion", "iverntotem"]
  },
  "jarvaniv": {
    "children": ["jarvanivstandard", "jarvanivwall"]
  },
  "jhin": {
    "children": ["jhintrap"]
  },
  "jinx": {
    "children": ["jinxmine"]
  },
  "kalista": {
    "children": ["kalistaaltar", "kalistaspawn"]
  },
  "kindred": {
    "children": ["kindredjunglebountyminion", "kindredwolf"]
  },
  "kled": {
    "children": ["kledmount", "kledrider"]
  },
  "kogmaw": {
    "children": ["kogmawdead"]
  },
  "lissandra": {
    "children": ["lissandrapassive"]
  },
  "lulu": {
    "children": ["lulufaerie", "lulupolymorphcritter"]
  },
  "lux": {
    "children": ["luxair", "luxdark", "luxfire", "luxice", "luxmagma", "luxmystic", "luxnature", "luxstorm", "luxwater"]
  },
  "malzahar": {
    "children": ["malzaharvoidling"]
  },
  "maokai": {
    "children": ["maokaisproutling"]
  },
  "milio": {
    "children": ["miliominion"]
  },
  "monkeyking": {
    "children": ["monkeykingclone", "monkeykingflying"]
  },
  "naafiri": {
    "children": ["naafiripackmate"]
  },
  "nasus": {
    "children": ["nasusult"]
  },
  "nidalee": {
    "children": ["nidaleecougar", "nidaleespear"]
  },
  "nunu": {
    "children": ["nunusnowball"]
  },
  "olaf": {
    "children": ["olafaxe"]
  },
  "orianna": {
    "children": ["oriannaball", "oriannanoball"]
  },
  "ornn": {
    "children": ["ornnram"]
  },
  "quinn": {
    "children": ["quinnvalor"]
  },
  "rammus": {
    "children": ["rammusdbc", "rammuspb"]
  },
  "reksai": {
    "children": ["reksaitunnel"]
  },
  "senna": {
    "children": ["sennasoul"]
  },
  "shaco": {
    "children": ["shacobox"]
  },
  "shen": {
    "children": ["shenspirit"]
  },
  "shyvana": {
    "children": ["shyvanadragon"]
  },
  "sona": {
    "children": ["sonadjgenre01", "sonadjgenre02", "sonadjgenre03"]
  },
  "swain": {
    "children": ["swaindemonform"]
  },
  "syndra": {
    "children": ["syndraorbs", "syndrasphere"]
  },
  "taliyah": {
    "children": ["taliyahwallchunk"]
  },
  "teemo": {
    "children": ["teemomushroom"]
  },
  "thresh": {
    "children": ["threshlantern"]
  },
  "trundle": {
    "children": ["trundlewall"]
  },
  "viktor": {
    "children": ["viktorsingularity"]
  },
  "yorick": {
    "children": ["yorickbigghoul", "yorickghoulmelee", "yorickwghoul", "yorickwinvisible"]
  },
  "zac": {
    "children": ["zacrebirthbloblet"]
  },
  "zed": {
    "children": ["zedshadow"]
  },
  "zoe": {
    "children": ["zoeorbs"]
  },
  "zyra": {
    "children": ["zyragraspingplant", "zyrapassive", "zyraseed", "zyrathornplant"]
  }
}

def load_dictionary(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def process_folders(dictionary):
    for parent, data in dictionary.items():
        for child in data['children']:
            process_child_folder(parent, child)

def process_child_folder(parent, child):
    parent_skins_path = f"process_champions/{parent}/skins_extracted"
    child_skins_path = f"process_champions/{child}/skins_extracted"

    if not (os.path.exists(parent_skins_path) and os.path.exists(child_skins_path)):
        print(f"Skipping {child}: Required paths not found")
        return

    for skin_id in os.listdir(child_skins_path):
        source_path = f"{child_skins_path}/{skin_id}/{child}_{skin_id}/data/characters"
        destination_path = f"{parent_skins_path}/{skin_id}/{parent}_{skin_id}/data/characters"

        if not os.path.exists(source_path):
            print(f"Skipping {child}/{skin_id}: Source path not found")
            continue

        if not os.path.exists(destination_path):
            print(f"Skipping {parent}/{skin_id}: Destination path not found")
            continue

        move_folders(source_path, destination_path)

def move_folders(source, destination):
    for item in os.listdir(source):
        s = os.path.join(source, item)
        d = os.path.join(destination, item)
        if os.path.isdir(s):
            if os.path.exists(d):
                print(f"Skipping {item}: Already exists in destination")
            else:
                shutil.move(s, d)
                print(f"Moved {item} to {destination}")

def main():
    process_folders(DICTIONARY)

if __name__ == "__main__":
    main()