import pandas as pd

def reverse_search(x):
    df = pd.DataFrame(conversions.items(), columns=["code","authority"])
    return df[df["authority"] == x]["code"].iloc[0]

conversions = {
      "BL":"Barnsley",

      "DY":"Derbyshire",

      "MK":"Milton Keynes",

      "SO":"City of Southampton",



      "BS":"Bath and North East Somerset",

      "DN":"Devon",

      "NK":"Norfolk",

      "SN":"St Helens",



      "BF":"Bedford",

      "DR":"Doncaster",

      "NI":"North Lincolnshire",

      "SF":"Staffordshire",



      "BX":"Bexley",

      "DT":"Dorset",

      "NS":"North Somerset",

      "YY":"Stockport",



      "BI":"Birmingham",

      "DZ":"Dudley",

      "NY":"North Yorkshire",

      "SM":"Stockton on Tees",



      "BB":"Blackburn with Darwen",

      "DU":"Durham",

      "NN":"Northamptonshire",

      "SK":"Suffolk",



      "BP":"Blackpool",

      "EY":"East Riding of Yorkshire",

      "ND":"Northumberland",

      "SU":"Surrey",



      "BG":"Blaenau Gwent",

      "ES":"East Sussex",

      "NG":"City of Nottingham",

      "SS":"Swansea",



      "BO":"Bolton",

      "EX":"Essex",

      "NT":"Nottinghamshire",

      "TS":"Tameside",



      "BU":"Bournemouth",

      "FL":"Flintshire",

      "OH":"Oldham",

      "TU":"Thurrock",



      "BC":"Bracknell Forest",

      "GH":"Gateshead",

      "ON":"Oxfordshire",

      "TB":"Torbay",



      "BA":"Bradford",

      "GR":"Gloucestershire",

      "PB":"Pembrokeshire",

      "TF":"Torfaen",



      "B1":"Brecon Beacons National Park",

      "GY":"Gwynedd",

      "PE":"City of Peterborough",

      "TR":"Trafford",



      "BH":"City of Brighton and Hove",

      "HP":"Hampshire",

      "PY":"City of Plymouth",

      "VG":"Vale of Glamorgan",



      "BZ":"City of Bristol",

      "HE":"Herefordshire",

      "PL":"Poole",

      "WE":"Wakefield",



      "BR":"Bromley",

      "HD":"Hertfordshire",

      "PO":"City of Portsmouth",

      "WA":"Walsall",



      "BM":"Buckinghamshire",

      "KH":"City of Kingston upon Hull",

      "PW":"Powys",

      "WG":"Warrington",



      "BY":"Bury",

      "IA":"Isle of Anglesey",

      "RG":"Reading",

      "WK":"Warwickshire",



      "CF":"Caerphilly",

      "IW":"Isle of Wight",

      "RC":"Redcar and Cleveland",

      "WB":"West Berkshire",



      "CA":"Calderdale",

      "KT":"Kent",

      "RH":"Rhondda Cynon Taff",

      "WS":"West Sussex",



      "CB":"Cambridgeshire",

      "KL":"Kirklees",

      "RD":"Rochdale",

      "WN":"Wigan",



      "CD":"Cardiff",

      "KN":"Knowsley",

      "RO":"Rotherham",

      "WT":"Wiltshire",



      "CT":"Carmarthenshire",

      "L1":"Lake District National Park",

      "RL":"Rutland",

      "WC":"Windsor and Maidenhead",



      "BK":"Central Bedfordshire",

      "LA":"Lancashire",

      "SC":"Salford",

      "WR":"Wirral",



      "CE":"Ceredigion",

      "LD":"Leeds",

      "SE":"Sefton",

      "WJ":"Wokingham",



      "CH":"Cheshire East",

      "LC":"City of Leicester",

      "SP":"Sheffield",

      "WO":"Worcestershire",



      "CC":"Cheshire West and Chester",

      "LT":"Leicestershire",

      "SH":"Shropshire",

      "WX":"Wrexham",



      "CW":"Conwy",

      "LL":"Lincolnshire",

      "YT":"Slough",

      "YK":"York",



      "CN":"Cornwall",

      "MA":"Manchester",

      "SQ":"Solihull",

      "CU":"Cumbria",

      "ME":"Medway",

      "ST":"Somerset",


      "DE":"Denbighshire",

      "MT":"Merthyr Tydfil",

      "SG":"South Gloucestershire",
}