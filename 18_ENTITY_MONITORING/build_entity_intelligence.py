# -*- coding: utf-8 -*-
import csv, json, hashlib, re
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
SITE = Path('/var/www/html')
OUT_REPO = BASE / 'entity-intelligence.json'
OUT_SITE = SITE / 'data' / 'entity-intelligence.json'

def nkey(value):
    return "".join(ch for ch in (value or "").lower() if ch.isalnum())

def read_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

# ---------- sources ----------
sources = [
 {"id":"S001","name":"Public Safety Canada — four new terrorist entities","date":"2025-12-10","type":"government","url":"https://www.canada.ca/en/public-safety-canada/news/2025/12/government-of-canada-lists-four-new-terrorist-entities0.html","use":"Canada lists 764; victim/recruitment description","confidence":"E"},
 {"id":"S002","name":"Canada Gazette — SOR/2025-263","date":"2025-12-17","type":"regulation","url":"https://gazette.gc.ca/rp-pr/p2/2025/2025-12-17/html/sor-dors263-eng.html","use":"Legal instrument listing 764","confidence":"E"},
 {"id":"S003","name":"NZ Gazette — Designation of Two Terrorist Entities (2025-au7135)","date":"2025-12-10","type":"government","url":"https://gazette.govt.nz/notice/id/2025-au7135","use":"O9A/ONA and Terrorgram Collective designated 2025-12-07","confidence":"E"},
 {"id":"S004","name":"NZ Gazette corrigendum 2025-au7194","date":"2025-12-11","type":"government","url":"https://gazette.govt.nz/notice/id/2025-au7194","use":"Corrigendum to O9A designation notice","confidence":"E"},
 {"id":"S005","name":"NZ Police — O9A statement of case (PDF)","date":"2025-12","type":"primary statement of case","url":"https://www.police.govt.nz/sites/default/files/publications/statement-of-case-order-of-nine-angles-terrorist-designation.pdf","use":"O9A structure, ideology, nexions, 764/NLM/MKY listing","confidence":"E"},
 {"id":"S006","name":"NZ DPMC — decision to designate Terrorgram/O9A","date":"2025","type":"government decision","url":"https://www.dpmc.govt.nz/publication/decision-designate-terrorgram-collective-and-order-nine-angles-terrorist-entities","use":"Reasoning for O9A designation","confidence":"E"},
 {"id":"S007","name":"FBI Boston — NVE warning","date":"2025-2026","type":"law enforcement","url":"https://www.fbi.gov/news/press-releases/fbi-boston-warns-of-nihilistic-violent-extremists-targeting-children-and-vulnerable-victims-online","use":"NVE targeting children/vulnerable victims","confidence":"E"},
 {"id":"S008","name":"DOJ — 764 member guilty plea","date":"2026","type":"court/DOJ","url":"https://www.justice.gov/usao-md/pr/violent-extremist-network-764-member-pleads-guilty-sexually-exploiting-minors-and","use":"764-linked sexual exploitation and cyberstalking","confidence":"E"},
 {"id":"S009","name":"DOJ — 764 defendant charged","date":"2026","type":"court/DOJ","url":"https://www.justice.gov/usao-ndny/pr/albany-county-man-and-alleged-member-nihilistic-violent-extremist-organization-764","use":"764-linked child-pornography charge","confidence":"E"},
 {"id":"S010","name":"RCMP — 764 peace bond","date":"2026-02","type":"law enforcement","url":"https://rcmp.ca/en/news/2026/02/youth-involved-terrorist-activities-764-network-placed-peace-bond-rcmp","use":"Canadian youth 764 case","confidence":"E"},
 {"id":"S011","name":"US House Oversight — 764 investigation","date":"2026","type":"congressional","url":"https://oversight.house.gov/release/comer-and-higgins-investigate-violent-online-network-764/","use":"Congressional interest in 764","confidence":"E"},
 {"id":"S012","name":"UNO NCTE — Prosecuting NVE","date":"2025-12","type":"academic/CT","url":"https://www.unomaha.edu/ncite/news/2025/12/img/prosecuting-nve-report.pdf","use":"764 prosecutions, FBI investigation volume, victim scale","confidence":"C/E"},
 {"id":"S013","name":"Sparx Intelligence — UTTP: From Internet Trolling to Violent Extremism","date":"2026-07-15","type":"independent analysis","url":"https://sparxintel.com/publications/the-uttp-from-internet-trolling-to-violent-extremism","use":"UTTP as NVE network; overlap with 764/NLM/MMC; grooming; fluid membership; joint Doxbin activity","confidence":"C"},
 {"id":"S014","name":"GNET — The Designation of 764 Network","date":"2026-03-16","type":"independent analysis","url":"https://gnet-research.org/2026/03/16/the-designation-of-764-network-why-does-it-matter/","use":"764/O9A designation context; exploitation/extremism intersection","confidence":"C"},
 {"id":"S015","name":"CTC West Point — Remotely Coerced Violence","date":"2026","type":"independent analysis","url":"https://ctc.westpoint.edu/remotely-coerced-violence-764-the-com-network-and-the-hybridization-of-threats/","use":"764/Com operational model","confidence":"C"},
 {"id":"S016","name":"GWU Program on Extremism — Holding 764 Accountable","date":"2025-2026","type":"independent analysis","url":"https://extremism.gwu.edu/holding-764-accountable","use":"764 accountability analysis","confidence":"C"},
 {"id":"S017","name":"ADL — 764 backgrounder","date":"2025-06-18","type":"research","url":"https://www.adl.org/resources/backgrounder/764","use":"764 recruitment/victim pattern; O9A influence","confidence":"C"},
 {"id":"S018","name":"ISD — 764","date":"2025-03-27","type":"research","url":"https://www.isdglobal.org/isd-explainer/764/","use":"764 origin, structure, O9A influence from court records","confidence":"C"},
 {"id":"S019","name":"ISD — The Order of Nine Angles","date":"2022-09-16","type":"research","url":"https://www.isdglobal.org/explainers/the-order-of-nine-angles-explainer/","use":"O9A origins, structure, ideology, cases","confidence":"C"},
 {"id":"S020","name":"HOPE not Hate — O9A incubator","date":"2021","type":"research","url":"https://hopenothate.org.uk/chapter/order-of-nine-angles-an-incubator-of-terrorism/","use":"O9A cases, networks, influence","confidence":"C"},
 {"id":"S021","name":"CBC — Canada lists 764","date":"2025-12-10","type":"journalism","url":"https://www.cbc.ca/news/politics/764-youth-extremist-group-9.7010571","use":"Canadian listing; O9A inspiration","confidence":"C"},
 {"id":"S022","name":"Bx Writes — Three Shootings in a Single Day","date":"2026-06-25","type":"journalism","url":"https://bxwrites.substack.com/p/three-shootings-in-a-single-day-linked","use":"UTTP/Foodist fusion with parts of Com/764; Sayer case","confidence":"C/A"},
 {"id":"S023","name":"Soyjak Wiki — UTTP","date":"2026-11-18","type":"community wiki","url":"https://soyjakwiki.org/UTTP","use":"Faction history, current-state, 2026 offshoots","confidence":"D"},
 {"id":"S024","name":"UTubeTrollPedia","date":"unknown","type":"community wiki","url":"https://tommyparky.com/index.php/UTubeTrollPolice","use":"Founding/history claims; self-published","confidence":"D"},
 {"id":"S025","name":"EverybodyWiki — UTubeTrollPolice","date":"2026-09-04","type":"user-generated wiki","url":"https://en.everybodywiki.com/UTubeTrollPolice","use":"2011 founding/background","confidence":"D"},
 {"id":"S026","name":"StyxNet validation (site)","date":"2026-11-19","type":"validation layer","url":"https://wintergate.org/styxnet/","use":"Platform-name blocklist; candidate caveats; not a member list","confidence":"E/A"},
 {"id":"S027","name":"DPOS deep dive (site/archive)","date":"2026-11-19","type":"analysis","url":"https://github.com/WinterGate-IC/UTTP/tree/main/04_OFFSHOOTS/DPOS%20-%20Degeneracy%20Police%20Order%20State","use":"DPOS structure, bridge analysis, connections","confidence":"C/A"},
 {"id":"S028","name":"UTTP archive — main repository","date":"2026-11-19","type":"archive","url":"https://github.com/WinterGate-IC/UTTP","use":"Claims, tracking, source index, evidence standards","confidence":"A/D"},
 {"id":"S029","name":"GateKeeper","date":"ongoing","type":"defence tooling","url":"https://github.com/WinterGate-IC/GateKeeper","use":"Blacklist/defence tracking of UTTP/DPOS actors","confidence":"E"},
 {"id":"S030","name":"WIC public intelligence posts","date":"2026-10-03","type":"WIC self-authored","url":"https://infosec.exchange/@WinterGateIC","use":"Methodology, FPE correction, provocation-as-collection","confidence":"A"},
 {"id":"S031","name":"US DOJ — Cherkaoui complaint","date":"2025-11","type":"court complaint","url":"https://www.justice.gov/usao-nj/media/1417486/dl?inline","use":"Individual statements referencing UTTP and 764; not an org link","confidence":"E"},
 {"id":"S032","name":"Soyjak Wiki — Operation Destroy Degenerates December","date":"2026-09-29","type":"community wiki","url":"https://soyjakwiki.org/Operation_Destroy_Degenerates_December","use":"UTTP raid/campaign documentation","confidence":"D"},
 {"id":"S033","name":"Soyjak Wiki — UTTP","date":"2026-11-18","type":"community wiki","url":"https://soyjakwiki.org/UTTP","use":"Faction history, 2026 offshoots, current state","confidence":"D"},
 {"id":"S034","name":"UTTP area intelligence register","date":"2026-11-19","type":"area register","url":"https://github.com/WinterGate-IC/UTTP/blob/main/02_CORE_INVESTIGATION/AREA_INTELLIGENCE/UTTP_AREA_REGISTER.csv","use":"200 platform/surface rows; no accounts","confidence":"C/A/D"},
 {"id":"S035","name":"General List v2 structured","date":"2026-11-19","type":"registry","url":"https://github.com/WinterGate-IC/UTTP/blob/main/02_CORE_INVESTIGATION/Members_List/General_List_v2_Structured_2026-11-19.md","use":"Groups, public handles, naming patterns, 2026 offshoots","confidence":"D/S"},
 {"id":"S036","name":"UTTP/764 final assessment","date":"2026-11-19","type":"analysis","url":"https://github.com/WinterGate-IC/UTTP/blob/main/13_UTTP_764_OVERLAP/FINAL_ASSESSMENT_2026-11-19.md","use":"Arm vs infiltration vs merger/edge-fusion finding","confidence":"C/A/X"},
 {"id":"S037","name":"O9A trace","date":"2026-11-19","type":"analysis","url":"https://github.com/WinterGate-IC/UTTP/tree/main/14_O9A_764_TRACE","use":"O9A profile, designations, nexion limits","confidence":"E/C/A"},
 {"id":"S038","name":"Validated claims register","date":"2026-11-19","type":"claim register","url":"https://github.com/WinterGate-IC/UTTP/tree/main/15_VALIDATED_CLAIMS","use":"Approved claims and confidence","confidence":"E/C/A/S/D"},
 {"id":"S039","name":"False claims quarantine","date":"2026-11-19","type":"claim register","url":"https://github.com/WinterGate-IC/UTTP/tree/main/16_VALIDATED_FALSE_CLAIMS","use":"Rejected claims and replacements","confidence":"X/S/D"},
 {"id":"S040","name":"Current-state package","date":"2026-11-19","type":"handoff","url":"https://github.com/WinterGate-IC/UTTP/tree/main/17_CURRENT_STATE_PACKAGE","use":"Short current-state and platform/authority handoff","confidence":"C/A/D"},
]

# ---------- areas ----------
area_rows = read_csv(ROOT / '02_CORE_INVESTIGATION' / 'AREA_INTELLIGENCE' / 'UTTP_AREA_REGISTER.csv')
areas = []
for r in area_rows:
    areas.append({
        "id": r['area_id'],
        "platform": r['platform'],
        "surface": r['surface'],
        "status": r['presence_status'],
        "confidence": r['confidence'],
        "why": r['why_relevant'],
    })

# ---------- claims ----------
vc_rows = read_csv(ROOT / '15_VALIDATED_CLAIMS' / 'VALIDATED_CLAIMS.csv')
fc_rows = read_csv(ROOT / '16_VALIDATED_FALSE_CLAIMS' / 'FALSE_CLAIMS.csv')
claims = []
for r in vc_rows:
    claims.append({"id": r['id'], "type": "validated", "claim": r['claim'], "confidence": r['confidence'], "basis": r['evidence'], "source": r['source']})
for r in fc_rows:
    claims.append({"id": r['id'], "type": "false", "claim": r['false_claim'], "confidence": r['status'], "basis": r['why_false_or_unsupported'], "source": r['original_locations']})

# ---------- entities ----------
entities = [
 {
  "id":"UTTP","name":"UTTP / UTube Troll Police","type":"harassment brand/network","status":"persistent but fragmented","confidence":"C","summary":"Decentralised harassment brand originating in 2011; tactics include raids, mass reporting, doxxing threats, shock content, and youth-facing recruitment. No single command chain is established.","origin":"2011, YouTube/Google+ trolling group","current_state":"Community documentation describes UTTP as heavily reduced (‘complete DNB’/almost no members) while splinters and adjacent NVE networks continue. Brand remains reusable.","watch_priority":"high","related":["UTTP-EMPIRE","CIRCUSFALL","OFFICERSLAPPY","AFR","DPOS","764","O9A"],"tactics":["mass reporting","comment raids","doxxing/swat threats","shock content","bot automation","fandom infiltration","platform migration","status-through-harm"],"areas":["YouTube","Discord","X","Telegram","Roblox","TikTok","Instagram","Reddit","Kiwi Farms","Soyjak Wiki"],"evolution":[
   {"date":"2011","event":"Emerges as YouTube/Google+ troll/bait group","confidence":"C/D"},
   {"date":"2013-2018","event":"Leadership and faction changes; raids and harassment expand","confidence":"D"},
   {"date":"2014-2016","event":"Escalation toward account takeover, DoS, larger raids","confidence":"C"},
   {"date":"2020","event":"Gacha Life targeting, personal-information theft, extortion reported","confidence":"D/C"},
   {"date":"2023","event":"Nu-UTTP/UTTP Empire era; more extreme content and NVE overlap alleged","confidence":"A/D"},
   {"date":"2025","event":"764 recruitment/infiltration into UTTP high command alleged","confidence":"A/S"},
   {"date":"2026","event":"Circusfall revival, faction split, AFR splinter, community ‘DNB’ assessment","confidence":"D"}],
  "sources":["S013","S023","S024","S025","S033","S034","S035"],
  "not_supported":["UTTP is a designated terrorist entity","UTTP is 764","UTTP centrally commands 764","UTTP merged with 764","Every UTTP faction is 764-linked"],
  "learning":{"stage":"fragmented brand","risk_score":0.82,"next_likely":"smaller rebrands and migration to private/soycord spaces","basis":"decentralised brand, fluid membership, platform churn, documented overlap"}},
 {
  "id":"UTTP-EMPIRE","name":"UTTP Empire / Nu-UTTP","type":"faction","status":"active lineage","confidence":"D","summary":"Later UTTP faction associated with more extreme content, CSAM/gore spam allegations, and NVE overlap. Tied to ‘Emperor of Anime Sucks’ / Hyper Bat Mapping in community records.","origin":"2023","current_state":"Lineage associated with extreme-content era and subsequent 2026 revival claims.","watch_priority":"high","related":["UTTP","CIRCUSFALL","DPOS","764"],"tactics":["mass reporting","shock content","bot automation","fandom infiltration","platform migration"],"areas":["Discord","X","YouTube","Telegram"],"evolution":[
   {"date":"2023","event":"Nu-UTTP/UTTP Empire era; mass CSAM/gore spam and extremist recruitment alleged","confidence":"A/D"},
   {"date":"2026","event":"Circusfall revival attributed to returning figures","confidence":"D"}],
  "sources":["S013","S023"],"not_supported":["UTTP Empire is a formal organisation with verified command"],"learning":{"stage":"extreme faction lineage","risk_score":0.74,"next_likely":"faction splintering under platform pressure","basis":"extreme-content era, faction splits, community reports"}},
 {
  "id":"CIRCUSFALL","name":"Circusfall faction","type":"2026 faction/revival","status":"reported","confidence":"D","summary":"Early-2026 UTTP revival associated with shock/animal-gore spam on X. Split with OfficerSlappy faction; self-proclaimed unification claims.","origin":"2026","current_state":"Community-reported revival and split; not independently verified.","watch_priority":"high","related":["UTTP","UTTP-EMPIRE","OFFICERSLAPPY","AFR"],"tactics":["shock content","raids","mention spam","platform migration"],"areas":["X","Discord","YouTube"],"evolution":[
   {"date":"2026-01","event":"Operation Circusfall revival reported","confidence":"D"},
   {"date":"2026-07","event":"Civil war split with OfficerSlappy faction reported","confidence":"D"},
   {"date":"2026-07","event":"Soul Reaver/Warlock/Irin911 reported takeover and renunciation of gore spam","confidence":"D/S"}],
  "sources":["S023"],"not_supported":["Circusfall is independently verified","Circusfall unification is verified"],"learning":{"stage":"revival faction","risk_score":0.68,"next_likely":"rebrand or absorption into another faction","basis":"revival, split, self-proclaimed unification"}},
 {
  "id":"OFFICERSLAPPY","name":"OfficerSlappy faction / UTTP Forum","type":"2026 faction/website lineage","status":"reported","confidence":"D","summary":"UTTP Forum and website lineage; mention-spam campaigns; Deltafall renamed Rockstarfall; reported copyright-leak partnerships.","origin":"2018 revival","current_state":"Community-reported 2026 activity; no independent census.","watch_priority":"medium","related":["UTTP","CIRCUSFALL","RDF"],"tactics":["mention spam","comment spam","doxxing","swatting threats","platform migration"],"areas":["YouTube","Discord","X"],"evolution":[
   {"date":"2018","event":"UTTP revival under Officer Slappy","confidence":"D"},
   {"date":"2026-07-08","event":"Deltafall campaign reported","confidence":"D"},
   {"date":"2026-10","event":"Rockstarfall rename/copyright-leak partnership reported","confidence":"D"}],
  "sources":["S023"],"not_supported":["OfficerSlappy faction is a unified command"],"learning":{"stage":"forum/website faction","risk_score":0.62,"next_likely":"continued mention-spam under new labels","basis":"forum lineage, spam campaigns, platform bans"}},
 {
  "id":"AFR","name":"Anti-Fandom Resistance (AFR)","type":"2026 splinter","status":"reported","confidence":"D","summary":"Splinter from the Circusfall faction after infighting; antifandom.org reported shut down 2026-08-07; continues in decentralized soycord/COM spaces.","origin":"2026","current_state":"Reported forum shutdown and server nuke; decentralized after.","watch_priority":"medium","related":["UTTP","CIRCUSFALL","DPOS","764"],"tactics":["shock content","platform migration","soycord/COM movement","raids"],"areas":["Discord","X","soycords","Telegram"],"evolution":[
   {"date":"2026","event":"AFR splinter forms from Circusfall faction","confidence":"D"},
   {"date":"2026-08-07","event":"antifandom.org reported shut down; server nuked","confidence":"D"}],
  "sources":["S023"],"not_supported":["AFR is independently verified","AFR is a formal organisation"],"learning":{"stage":"splinter","risk_score":0.55,"next_likely":"absorption into adjacent spaces","basis":"splinter formation, shutdown, migration"}},
 {
  "id":"BN0R","name":"Bn0r Empire","type":"2026 subgroup","status":"reported","confidence":"D","summary":"Subgroup tied to Bn0r/Chizur; mention-spam ecosystem and subgroup branding.","origin":"2026","current_state":"Community-reported subgroup; no independent census.","watch_priority":"medium","related":["OFFICERSLAPPY","UTTP"],"tactics":["mention spam","comment spam","doxxing"],"areas":["YouTube","Discord","X"],"evolution":[{"date":"2026","event":"Reported subgroup activity","confidence":"D"}],
  "sources":["S023"],"not_supported":["Bn0r Empire is a stable organisation"],"learning":{"stage":"subgroup","risk_score":0.5,"next_likely":"rebrand or absorption","basis":"subgroup branding, spam campaigns"}},
 {
  "id":"RDF","name":"Reddit Defence Force (RDF)","type":"2025-2026 revival","status":"reported","confidence":"D","summary":"Reddit-facing UTTP revival with mention spam; RDFPARTY splinter. Leadership claims are self-reported.","origin":"2025","current_state":"Community-reported activity; no independent census.","watch_priority":"medium","related":["UTTP","OFFICERSLAPPY"],"tactics":["mention spam","comment spam","doxxing"],"areas":["Reddit","YouTube","Discord"],"evolution":[
   {"date":"2025","event":"RDF revival reported","confidence":"D"},
   {"date":"2026","event":"RDFPARTY splinter reported","confidence":"D"}],
  "sources":["S023"],"not_supported":["RDF is independently verified"],"learning":{"stage":"revival","risk_score":0.48,"next_likely":"fragmentation or decline","basis":"revival, splinter, community reporting"}},
 {
  "id":"DPOS","name":"Degeneracy Police Order State (DPOS)","type":"hardcore UTTP offshoot","status":"active/reforming","confidence":"C/D","summary":"Structured, police-state-themed Discord network with Empire/Task Force/ISA HQ/log units. Bridges UTTP raid culture to 764/Com-style grooming, blackmail, and shock content. Not a 764 unit and no merger is established.","origin":"mid-2023","current_state":"Rotating micro-servers and rebrand attempts reported; no independent census.","watch_priority":"high","related":["UTTP","764","O9A","SPAWNISM","FPE"],"tactics":["raids","doxxing/swat threats","mass reporting","shock/gore spam","blackmail/extortion allegations","grooming/self-harm coercion allegations","platform migration"],"areas":["Discord","X","Telegram","Roblox","Fandom spaces"],"evolution":[
   {"date":"2023","event":"DPOS emerges as hardcore UTTP offshoot","confidence":"C/D"},
   {"date":"2024-2025","event":"Escalation into doxxing, swatting threats, shock spam, grooming/blackmail allegations","confidence":"A/S/D"},
   {"date":"2025","event":"Public exposure campaigns; server disruptions","confidence":"D/S"},
   {"date":"2026","event":"Rotating micro-servers and rebrand attempts reported","confidence":"A/S/D"}],
  "sources":["S027","S023"],"not_supported":["DPOS is a 764 unit","764 commands DPOS","DPOS is a real police/state","1,750+ linked accounts verified"],"learning":{"stage":"bridge node","risk_score":0.78,"next_likely":"continued rebranding and migration","basis":"structured server model, 764 tactical overlap, platform pressure"}},
 {
  "id":"764","name":"764","type":"designated NVE network","status":"designated (Canada)","confidence":"E","summary":"Decentralised nihilistic violent extremist network in the Com ecosystem. Designated in Canada (2025). Tactical overlap with UTTP/DPOS; not a UTTP command.","origin":"2021, from the Com network","current_state":"Designated, decentralised, with cells/offshoots.","watch_priority":"high","related":["UTTP","DPOS","O9A","HARMNATION"],"tactics":["sextortion","CSAM production","animal abuse","self-harm coercion","swatting","grooming"],"areas":["Discord","Telegram","gaming platforms","social media"],"evolution":[
   {"date":"2021","event":"764 emerges from the Com network","confidence":"C"},
   {"date":"2023-2025","event":"Arrests, prosecutions, and designations","confidence":"E"},
   {"date":"2025-12-10","event":"Canada designates 764 (SOR/2025-263)","confidence":"E"}],
  "sources":["S001","S002","S013","S014","S017","S018"],"not_supported":["764 is identical to O9A","764 commands UTTP","764 is a conventional organisation"],"learning":{"stage":"designated network","risk_score":0.9,"next_likely":"cell/offshoot churn under enforcement","basis":"designation, prosecutions, decentralised structure"}},
 {
  "id":"O9A","name":"Order of Nine Angles (O9A / ONA)","type":"designated occult/NVE network","status":"designated (New Zealand)","confidence":"E","summary":"Decentralised, leaderless militant-accelerationist network. New Zealand designated O9A/ONA in 2025. 764 is listed as a nexion; nexions are operationally independent.","origin":"1970s, England","current_state":"Designated, decentralised, no headquarters.","watch_priority":"medium","related":["764","UTTP","DPOS"],"tactics":["militant accelerationism","esoteric Nazism","insight roles","leaderless resistance","textual influence"],"areas":["Telegram","X","Reddit","YouTube","TikTok","Instagram"],"evolution":[
   {"date":"1970s","event":"O9A philosophy emerges","confidence":"C"},
   {"date":"1990s","event":"Association with neo-Nazi infiltration","confidence":"C"},
   {"date":"2008","event":"Social-media activity and text spread","confidence":"C"},
   {"date":"2025-12-07","event":"New Zealand designates O9A/ONA","confidence":"E"}],
  "sources":["S003","S005","S006","S019","S020"],"not_supported":["O9A commands 764","O9A is a single organisation with a leader","09A Cult is O9A headquarters"],"learning":{"stage":"ideological ecosystem","risk_score":0.85,"next_likely":"influence through texts and nexions","basis":"leaderless design, text corpus, designation"}},
 {
  "id":"HARMNATION","name":"Harm Nation","type":"764 offshoot","status":"adjacent","confidence":"C/D","summary":"Documented 764 offshoot focused on normalising self-injurious behaviour among youth.","origin":"764 offshoot","current_state":"Fluid network; not a single organisation.","watch_priority":"medium","related":["764"],"tactics":["sextortion","self-harm coercion","CSAM-adjacent conduct"],"areas":["Discord","Telegram","gaming platforms"],"evolution":[{"date":"2024","event":"Documented as 764 offshoot","confidence":"C"}],
  "sources":["S017","S018"],"not_supported":["Harm Nation is a stable organisation"],"learning":{"stage":"offshoot","risk_score":0.7,"next_likely":"rebrand or absorption","basis":"offshoot fluidity"}},
 {
  "id":"SPAWNISM","name":"Spawnism","type":"self-harm/recruitment cult","status":"adjacent","confidence":"D/S","summary":"Self-harm/recruitment cult with alleged UTTP/DPOS crossover. Community and leak material, not independent confirmation.","origin":"2025","current_state":"Alleged crossover with DPOS/UTTP; no command confirmed.","watch_priority":"high","related":["UTTP","DPOS","764"],"tactics":["self-harm coercion","recruitment","grooming"],"areas":["Roblox","Discord"],"evolution":[{"date":"2025","event":"Spawnism emerges and is linked to UTTP/DPOS in community/leak material","confidence":"D/S"}],
  "sources":["S023"],"not_supported":["DPOS commands Spawnism","Spawnism is a UTTP offshoot"],"learning":{"stage":"adjacent cult","risk_score":0.72,"next_likely":"continued exploitation of youth spaces","basis":"self-harm recruitment, allegations"}},
 {
  "id":"AUTTP","name":"Anti-UTTP / AUTTP","type":"opposition coalition","status":"loose","confidence":"D","summary":"Loose opposition coalition to UTTP, not a single organisation.","origin":"2020s","current_state":"Community opposition; not WIC-controlled.","watch_priority":"low","related":["UTTP"],"tactics":["counter-reporting","documentation","opposition campaigns"],"areas":["Discord","YouTube"],"evolution":[{"date":"2020s","event":"AUTTP forms as opposition label","confidence":"D"}],
  "sources":["S023"],"not_supported":["AUTTP is a formal organisation"],"learning":{"stage":"opposition label","risk_score":0.2,"next_likely":"fragmentation","basis":"loose coalition"}},
 {
  "id":"FPE","name":"FPE (Fundamental Paper Education) ecosystem","type":"target ecosystem","status":"target","confidence":"A","summary":"Youth-heavy fandom ecosystem targeted by UTTP-linked activity. WIC documents an FPE incursion; WIC is not an FPE partner and does not govern the fandom.","origin":"2024+","current_state":"Target ecosystem; WIC defence/reporting role only.","watch_priority":"medium","related":["UTTP","DPOS"],"tactics":["fandom targeting","infiltration","harassment","doxxing"],"areas":["YouTube","Discord","X"],"evolution":[{"date":"2024","event":"FPE targeted by UTTP-linked activity","confidence":"A"}],
  "sources":["S028","S030"],"not_supported":["WIC is an FPE partner","WIC governs FPE"],"learning":{"stage":"target ecosystem","risk_score":0.45,"next_likely":"continued targeting of youth fandoms","basis":"youth-heavy spaces, UTTP targeting"}},
 {
  "id":"FPE-POLICE","name":"FPE-Police","type":"role-play/AU brand","status":"unverified formal entity","confidence":"D","summary":"FPE-Police branding within the FPE ecosystem. Role-play/AU, not an official police force. No verified member list.","origin":"2025","current_state":"Branding used; no formal organisation confirmed.","watch_priority":"low","related":["FPE"],"tactics":["role-play branding","community identity"],"areas":["Discord","YouTube"],"evolution":[{"date":"2025","event":"FPE-Police branding appears","confidence":"D"}],
  "sources":["S028"],"not_supported":["FPE-Police is an official police force"],"learning":{"stage":"role-play brand","risk_score":0.25,"next_likely":"brand reuse","basis":"unverified branding"}},
 {
  "id":"TNM","name":"TNM / The Militia","type":"adjacent network","status":"affiliate/lead","confidence":"D","summary":"Adjacent network with individual crossover and 2025 investigation material. Presence in the archive is documentation/lead, not proof of command.","origin":"2020s","current_state":"Lead material; relationship varies.","watch_priority":"low","related":["UTTP","DPOS"],"tactics":["affiliation/lead material","cross-server activity"],"areas":["Discord"],"evolution":[{"date":"2025","event":"2025 investigation material","confidence":"D"}],
  "sources":["S028"],"not_supported":["TNM commands UTTP"],"learning":{"stage":"adjacent network","risk_score":0.35,"next_likely":"continued individual crossover","basis":"lead material"}},
 {
  "id":"148","name":"148-1488","type":"adjacent network","status":"affiliate/lead","confidence":"D","summary":"Adjacent network represented by archive/export material. Command links are unproven.","origin":"2020s","current_state":"Lead material; relationship varies.","watch_priority":"low","related":["UTTP"],"tactics":["affiliation/lead material"],"areas":["Discord"],"evolution":[{"date":"2020s","event":"Archive/export material","confidence":"D"}],
  "sources":["S028"],"not_supported":["148 commands UTTP"],"learning":{"stage":"adjacent network","risk_score":0.3,"next_likely":"continued lead material","basis":"archive exports"}},
 {
  "id":"ENCLAVE","name":"Imperium of Enclave / UETR-GSR","type":"adjacent network","status":"affiliate/lead","confidence":"D","summary":"Adjacent network represented by UID lists and crossover. Command links are unproven.","origin":"2020s","current_state":"Lead material; relationship varies.","watch_priority":"low","related":["UTTP","DPOS"],"tactics":["affiliation/lead material"],"areas":["Discord"],"evolution":[{"date":"2020s","event":"UID lists and crossover","confidence":"D"}],
  "sources":["S028"],"not_supported":["Enclave commands UTTP"],"learning":{"stage":"adjacent network","risk_score":0.3,"next_likely":"continued lead material","basis":"UID lists"}},
 {
  "id":"SPWN","name":"SPWN / Spawnism","type":"affiliate/lead","status":"lead only","confidence":"D","summary":"Placeholder/lead folder. Do not overstate.","origin":"unknown","current_state":"Lead only.","watch_priority":"low","related":["UTTP"],"tactics":["lead material"],"areas":["unknown"],"evolution":[{"date":"unknown","event":"Placeholder/lead","confidence":"D"}],
  "sources":["S028"],"not_supported":["SPWN is a verified affiliate"],"learning":{"stage":"lead","risk_score":0.2,"next_likely":"unverified","basis":"placeholder"}},
 {
  "id":"E11","name":"11th Street","type":"offshoot/lead","status":"unverified lead","confidence":"D","summary":"Explicitly marked unverified lead.","origin":"unknown","current_state":"Lead only.","watch_priority":"low","related":["DPOS"],"tactics":["lead material"],"areas":["unknown"],"evolution":[{"date":"unknown","event":"Unverified lead","confidence":"D"}],
  "sources":["S028"],"not_supported":["11th Street is a verified offshoot"],"learning":{"stage":"lead","risk_score":0.2,"next_likely":"unverified","basis":"placeholder"}},
 {
  "id":"KKTK","name":"KuKluxTrollKlan (KKTK)","type":"historical group","status":"historical","confidence":"D","summary":"Early UTTP Google+ era group (2017).","origin":"2017","current_state":"Historical.","watch_priority":"low","related":["UTTP"],"tactics":["historical group"],"areas":["Google+"],"evolution":[{"date":"2017","event":"Founded by Officer MoonMan","confidence":"D"}],
  "sources":["S023"],"not_supported":["KKTK is a current organisation"],"learning":{"stage":"historical","risk_score":0.15,"next_likely":"none","basis":"historical"}},
 {
  "id":"YFGA","name":"YouTube Farm Gang Army (YFGA)","type":"historical splinter","status":"historical","confidence":"D","summary":"Gachafall-era group (2020-2021).","origin":"2020","current_state":"Historical.","watch_priority":"low","related":["UTTP"],"tactics":["historical splinter"],"areas":["YouTube","Discord"],"evolution":[{"date":"2020","event":"Founded during Gachafall era","confidence":"D"}],
  "sources":["S023"],"not_supported":["YFGA is a current organisation"],"learning":{"stage":"historical","risk_score":0.15,"next_likely":"none","basis":"historical"}},
 {
  "id":"VGCP","name":"VideoGameCartoonPolice (VGCP)","type":"historical opposition","status":"disbanded","confidence":"D","summary":"Oldest known UTTP splinter; anti-UTTP; disbanded for over a decade.","origin":"2012","current_state":"Disbanded; revival attempts low relevance.","watch_priority":"low","related":["UTTP"],"tactics":["historical opposition"],"areas":["YouTube","GoAnimate"],"evolution":[{"date":"2012","event":"Founded by FireMarioFireLuigi65","confidence":"D"}],
  "sources":["S023"],"not_supported":["VGCP is a current organisation"],"learning":{"stage":"historical","risk_score":0.1,"next_likely":"none","basis":"historical"}},
 {
  "id":"AFF","name":"Anti Fandom Front (AFF)","type":"opposition/adjacent","status":"historical/lead","confidence":"D","summary":"Anti-fandom front distinct from AFR; community-reported.","origin":"2020s","current_state":"Lead only.","watch_priority":"low","related":["UTTP"],"tactics":["opposition/adjacent"],"areas":["YouTube","Discord"],"evolution":[{"date":"2020s","event":"Community-reported activity","confidence":"D"}],
  "sources":["S023"],"not_supported":["AFF is independently verified"],"learning":{"stage":"lead","risk_score":0.2,"next_likely":"unverified","basis":"community report"}},
 {
  "id":"TND","name":"TND / The Group That Destroyed FPE","type":"FPE conflict group","status":"rival/destroyer","confidence":"D","summary":"FPE conflict group in the registry; no independent verification.","origin":"unknown","current_state":"Lead only.","watch_priority":"low","related":["FPE","UTTP"],"tactics":["fandom conflict"],"areas":["YouTube","Discord"],"evolution":[{"date":"unknown","event":"Reported FPE conflict","confidence":"D"}],
  "sources":["S028"],"not_supported":["TND is a verified organisation"],"learning":{"stage":"lead","risk_score":0.2,"next_likely":"unverified","basis":"registry"}},
 {
  "id":"ZETA","name":"Zeta","type":"UTTP ally (reported)","status":"reported ally","confidence":"D","summary":"Reported UTTP ally in the registry; no independent verification.","origin":"unknown","current_state":"Lead only.","watch_priority":"low","related":["UTTP"],"tactics":["reported ally"],"areas":["unknown"],"evolution":[{"date":"unknown","event":"Reported ally","confidence":"D"}],
  "sources":["S028"],"not_supported":["Zeta is a verified ally"],"learning":{"stage":"lead","risk_score":0.2,"next_likely":"unverified","basis":"registry"}},
 {
  "id":"YTDESTROYERS","name":"YouTube Troll Destroyers","type":"opposition","status":"anti-UTTP","confidence":"D","summary":"Primary UTTP opposition in the registry.","origin":"unknown","current_state":"Opposition label.","watch_priority":"low","related":["UTTP"],"tactics":["opposition"],"areas":["YouTube"],"evolution":[{"date":"unknown","event":"Opposition group","confidence":"D"}],
  "sources":["S028"],"not_supported":["YouTube Troll Destroyers is a formal organisation"],"learning":{"stage":"opposition","risk_score":0.15,"next_likely":"unverified","basis":"registry"}},
 {
  "id":"C09A","name":"09A Cult (legacy archive label)","type":"legacy archive label","status":"archive context","confidence":"D","summary":"Legacy archive label for O9A-adjacent material. Not a headquarters or proven parent; 09A is an alternate spelling.","origin":"archive label","current_state":"Legacy context only.","watch_priority":"low","related":["O9A"],"tactics":["archive label"],"areas":["archive"],"evolution":[{"date":"2026-11-19","event":"Label corrected as legacy archive context","confidence":"D"}],
  "sources":["S037"],"not_supported":["09A Cult is O9A headquarters","09A Cult is UTTP parent"],"learning":{"stage":"legacy label","risk_score":0.1,"next_likely":"none","basis":"archive label"}},
 {
  "id":"GATEKEEPER","name":"GateKeeper","type":"defence/blacklist platform","status":"active","confidence":"E","summary":"WIC community-protection tooling. Tracks UTTP/DPOS-linked actors in a global blacklist. Defence relationship, not affiliation.","origin":"WIC","current_state":"Active defence tooling.","watch_priority":"low","related":["UTTP","DPOS"],"tactics":["blacklist","threat intelligence","community defence"],"areas":["Discord"],"evolution":[{"date":"ongoing","event":"Maintains global blacklist of malicious actors","confidence":"E"}],
  "sources":["S029"],"not_supported":["GateKeeper is an affiliate of UTTP"],"learning":{"stage":"defence platform","risk_score":0.05,"next_likely":"continued defensive tracking","basis":"tooling"}},
 {
  "id":"WIC","name":"WinterGate Intelligence Collective (WIC)","type":"documenter","status":"maintainer","confidence":"E","summary":"Not a UTTP member. Documents, publishes, and tracks at group level. Maintains the archive, validation layers, and handoff packages.","origin":"WIC","current_state":"Active documenter.","watch_priority":"low","related":["UTTP","DPOS","764","O9A"],"tactics":["documentation","validation","threat intelligence","defensive engineering"],"areas":["web","GitHub","Discord"],"evolution":[{"date":"2026-09-17","event":"UTTP investigation status recorded ACTIVE","confidence":"A"},{"date":"2026-11-19","event":"Archive v3 and current-state package published","confidence":"E"}],
  "sources":["S028","S030"],"not_supported":["WIC is a UTTP member","WIC is an FPE partner"],"learning":{"stage":"documenter","risk_score":0.0,"next_likely":"continued documentation","basis":"archive and methodology"}},
]
entities = [e for e in entities if e['id'] not in {'GATEKEEPER', 'WIC'}]
for e in entities:
    e['related'] = [r for r in (e.get('related') or []) if r not in {'GATEKEEPER', 'WIC'}]


ALIASES = {
    'uttputubetrollpolice': 'UTTP',
    'uttpempirenuuttp': 'UTTP-EMPIRE',
    'circusfallfaction': 'CIRCUSFALL',
    'officerslappyfactionuttpforum': 'OFFICERSLAPPY',
    'dposdegeneracypoliceorderstate': 'DPOS',
    'antifandomresistanceafr': 'AFR',
    'bn0rempire': 'BN0R',
    'redditdefenceforcerdf': 'RDF',
    'kktkkukluxtrollklan': 'KKTK',
    'yfga': 'YFGA',
    'vgcpvideogamecartoonpolice': 'VGCP',
    'affantifandomfront': 'AFF',
    'auttpantiuttp': 'AUTTP',
    '764': '764',
    'harmnation': 'HARMNATION',
    'o9aona': 'O9A',
    'spawnism': 'SPAWNISM',
    'fpepolice': 'FPE-POLICE',
    'fpeecosystem': 'FPE',
    'tnmthemilitia': 'TNM',
    '1481488': '148',
    'imperiumoftheenclavegrs': 'ENCLAVE',
    'gatekeeper': None,
}


def parse_general_list():
    path = ROOT / '02_CORE_INVESTIGATION' / 'Members_List' / 'General_List_v2_Structured_2026-11-19.md'
    if not path.exists():
        return []
    added = []
    known_ids = {e['id'] for e in entities}
    known_names = {nkey(e['name']) for e in entities}
    used_ids = set(known_ids)
    section = None
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.startswith('###'):
            section = line[4:].strip()
            continue
        if line.startswith('## '):
            section = line[3:].strip()
            continue
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 4:
            continue
        name = cells[0].strip()
        if not name or name.lower() in {'group', 'name', 'campaign', 'handle'} or set(name) <= set('-: '):
            continue
        key = nkey(name)
        if key in ALIASES:
            continue
        if key in known_names or key in used_ids:
            continue
        if section and section.startswith(('4.', '5.')):
            continue
        if section and 'campaign' in section.lower():
            continue
        if section and section.startswith('2.'):
            typ, status, confidence, note = cells[1], cells[2], cells[3], cells[4] if len(cells) > 4 else ''
        else:
            typ, status, confidence, note = cells[1], 'adjacent/lead', cells[2], cells[3] if len(cells) > 3 else ''
        eid = re.sub(r'[^A-Z0-9]+', '_', key.upper()).strip('_')[:40]
        base = eid
        suffix = 1
        while eid in used_ids:
            suffix += 1
            eid = f'{base}_{suffix}'
        used_ids.add(eid)
        entities.append({
            'id': eid,
            'name': name,
            'type': typ,
            'status': status,
            'confidence': confidence,
            'summary': note,
            'origin': 'General List v2 register',
            'current_state': status,
            'watch_priority': 'medium' if confidence in {'D', 'S', 'D/S'} else 'low',
            'related': {'TYRANNYRUTTP': ['UTTP', 'OFFICERSLAPPY'], 'RDFPARTY': ['RDF', 'UTTP'], 'THEFARTKNOCKERSTFK': ['UTTP']}.get(eid, []),
            'tactics': [],
            'areas': [],
            'evolution': [],
            'sources': ['S035'],
            'not_supported': [],
            'learning': {'stage': 'registry lead', 'risk_score': 0.3, 'next_likely': 'unverified', 'basis': 'General List v2 register'},
        })
        known_names.add(key)
        added.append(eid)
    return added

parse_general_list()
methods = [
 {"id":"M001","name":"Open-source intelligence (OSINT)","use":"Public records, archives, screenshots, exports, and public posts","confidence":"E/C/A"},
 {"id":"M002","name":"Source-ledger verification","use":"Every claim tied to a source and confidence label","confidence":"E/C/A"},
 {"id":"M003","name":"Claim-ledger correction","use":"False/superseded claims quarantined and replaced","confidence":"E/X"},
 {"id":"M004","name":"StyxNet validation","use":"Platform-name blocklist; row/handle classification; no ownership assumption","confidence":"E/A"},
 {"id":"M005","name":"TEL-style entity mapping","use":"Multi-parent cluster mapping and cross-referencing","confidence":"A/C"},
 {"id":"M006","name":"Area intelligence","use":"Platform/surface mapping without account lists","confidence":"C/A/D"},
 {"id":"M007","name":"Tracking registers","use":"Group/faction register, board, snapshot, collection plan, open leads","confidence":"A/D"},
 {"id":"M008","name":"Evidence hashing","use":"SHA-256 manifest and chain-of-custody records","confidence":"E"},
 {"id":"M009","name":"Confidence labelling","use":"E/C/A/S/D/X labels on claims and entities","confidence":"E/C/A"},
 {"id":"M010","name":"Negative-finding discipline","use":"No evidence located is not proof of absence","confidence":"A"},
 {"id":"M011","name":"No-target-list rule","use":"Group-level only; no private identifiers","confidence":"E"},
 {"id":"M012","name":"Adaptive scoring","use":"Rule-based risk and morphology scoring from current data","confidence":"A"},
 {"id":"M013","name":"Overtime monitoring","use":"Scheduled refresh, source checks, and snapshot deltas","confidence":"A"},
 {"id":"M014","name":"Handoff packaging","use":"Short current-state brief for platforms and authorities","confidence":"A"},
 {"id":"M015","name":"Raw-evidence preservation","use":"Original captures retained; corrections added, not silent deletion","confidence":"E"},
]

sources += [
 {"id":"S041","name":"Encyclopedia Dramatica — Foodistzen","date":"2026-07-29","type":"community wiki","url":"https://edramatica.com/Foodistzen","use":"UTTP/Foodist/764/Skibidi Farms ecosystem context","confidence":"D"},
 {"id":"S042","name":"Soyjak Wiki — Operation Destroy Degenerates December","date":"2026-09-29","type":"community wiki","url":"https://soyjakwiki.org/Operation_Destroy_Degenerates_December","use":"UTTP raid/campaign documentation","confidence":"D"},
 {"id":"S043","name":"NoTrac3 / CyberCrimeDB — Operation Silent Forge","date":"2025-10","type":"third-party OSINT","url":"https://github.com/NoTrac3/CyberCrimeDB","use":"UCS/Spawnism/UTTP-DPOS raid coordination (third-party; unverified)","confidence":"D/S"},
 {"id":"S044","name":"Spawnism explainer — Ultimate Pop Culture Wiki","date":"2025-07-14","type":"community wiki","url":"https://ultimatepopculture.fandom.com/wiki/Spawnism","use":"Spawnism practices and alleged UTTP/764 infiltration","confidence":"D/S"},
 {"id":"S045","name":"Rina’s reports — Spawnism","date":"2025-08-01","type":"community reporting","url":"https://rinakochireports.lykhari.com/the-dark-side-of-spawnism-a-dangerous-roblox-trend-leading-kids-to-self-harm","use":"Spawnism, UTTP, and 764 crossover claims","confidence":"D/S"},
 {"id":"S046","name":"Krebs on Security — The Dark Nexus Between Harm Groups and The Com","date":"2024-09-13","type":"journalism","url":"https://krebsonsecurity.com/2024/09/the-dark-nexus-between-harm-groups-and-the-com","use":"Com/764 ecosystem and recruitment pathways","confidence":"C"},
 {"id":"S047","name":"Global Project Against Hate and Extremism — 764 Network","date":"2026-03-13","type":"research","url":"https://globalextremism.org/post/764-network/","use":"764 network scope and child exploitation","confidence":"C"},
 {"id":"S048","name":"Our Rescue — 6-7 is Silly, 764 is Deadly","date":"2025-12-23","type":"research","url":"https://ourrescue.org/resources/news-media/our-perspectives/6-7-is-silly-764-is-deadly-the-rise-of-decentralized-online-exploitation-terrorism","use":"Decentralised online exploitation terrorism","confidence":"C"},
 {"id":"S049","name":"YouTube — ‘The UTTP Is Back in 2026’","date":"2026","type":"community video","url":"https://www.youtube.com/watch?v=IpQ8_vJIswY","use":"UTTP revival, 764/Spawnism connections (community)","confidence":"D"},
 {"id":"S050","name":"YouTube — ‘YouTube’s Worst Troll Army - The UTTP 2026’","date":"2026-03-27","type":"community video","url":"https://www.youtube.com/watch?v=0oLInedw394","use":"UTTP 2026 activity and targets","confidence":"D"},
]
sources += [{'id': 'SL001', 'name': 'Canada Gazette, SOR/2025-263', 'date': '2025-12-17', 'type': 'Regulation', 'url': 'https://gazette.gc.ca/rp-pr/p2/2025/2025-12-17/html/sor-dors263-eng.html', 'use': 'Legal instrument adding 764 to the Canadian list', 'confidence': 'E'}, {'id': 'SL002', 'name': 'NZ Gazette 2025-au7135', 'date': '2025-12-10', 'type': 'Government notice', 'url': 'https://gazette.govt.nz/notice/id/2025-au7135', 'use': 'New Zealand designation of O9A/ONA and Terrorgram Collective on 2025-12-07', 'confidence': 'E'}, {'id': 'SL003', 'name': 'NZ Police — O9A statement of case', 'date': '2025-12', 'type': 'Primary statement of case', 'url': 'https://www.police.govt.nz/sites/default/files/publications/statement-of-case-order-of-nine-angles-terrorist-designation.pdf', 'use': 'O9A structure, nexions, and 764/NLM/MKY listing', 'confidence': 'E'}, {'id': 'SL004', 'name': 'NZ DPMC decision — Terrorgram/O9A', 'date': '2025', 'type': 'Government decision', 'url': 'https://www.dpmc.govt.nz/publication/decision-designate-terrorgram-collective-and-order-nine-angles-terrorist-entities', 'use': 'Reasoning for O9A designation', 'confidence': 'E'}, {'id': 'SL005', 'name': 'FBI — Maine juvenile 764 case', 'date': '2025-2026', 'type': 'Law enforcement', 'url': 'https://www.fbi.gov/news/press-releases/maine-teenager-is-first-juvenile-in-the-nation-to-be-federally-charged-adjudicated-and-detained-for-acts-related-to-nihilistic-violent-extremist-groups-in-the-764-network', 'use': 'Federal 764-linked case involving a minor', 'confidence': 'E'}, {'id': 'SL006', 'name': 'DOJ — Cherkaoui complaint', 'date': '2025-11', 'type': 'Court complaint', 'url': 'https://www.justice.gov/usao-nj/media/1417486/dl?inline', 'use': 'Individual statements referencing UTTP and 764; not an organizational link', 'confidence': 'E'}]

# ---------- discovered area surfaces ----------
discovered_areas = json.loads((BASE / 'discovered_areas.json').read_text(encoding='utf-8')) if (BASE / 'discovered_areas.json').exists() else []
discovered_watchlist = json.loads((BASE / 'discovered_watchlist.json').read_text(encoding='utf-8')) if (BASE / 'discovered_watchlist.json').exists() else []
# Discovered area surfaces remain internal leads until validated. They are
# counted in monitor.archive but are not published as area intelligence.

# ---------- areas aggregate ----------
area_by_platform = {}
for r in area_rows:
    p = r['platform']
    area_by_platform.setdefault(p, {"platform": p, "rows": 0, "statuses": {}, "confidence": r['confidence']})
    area_by_platform[p]["rows"] += 1
    area_by_platform[p]["statuses"][r['presence_status']] = area_by_platform[p]["statuses"].get(r['presence_status'],0)+1
areas = list(area_by_platform.values())
# ---------- offshoot watchlist ----------
watch_rows = read_csv(ROOT / '17_CURRENT_STATE_PACKAGE' / 'OFFSHOOT_WATCHLIST.csv')
watchlist = []
seen_watch = set()
for r in watch_rows:
    key = nkey(r['name'])
    if key in seen_watch:
        continue
    seen_watch.add(key)
    watchlist.append({"name": r['name'], "type": r['type'], "status": r['status'], "confidence": r['confidence'], "indicators": r['watch_indicators'], "limits": r['limits']})
# Discovered watch leads remain internal until validated. The public watchlist
# is built from the curated offshoot register only.

strict_summary = json.loads((BASE / 'strict_validation_summary.json').read_text(encoding='utf-8'))
strict_validation = {
 "raw_rows": strict_summary.get('raw_rows', 0),
 "strict_valid": strict_summary.get('strict_valid', 0),
 "rejected": strict_summary.get('rejected', 0),
 "broken_internal_links": strict_summary.get('broken_internal_links', 0),
 "bad_json_files": strict_summary.get('bad_json_files', []),
 "non_strict_json_exports": strict_summary.get('non_strict_json_exports', []),
 "bad_csv_files": strict_summary.get('bad_csv_files', []),
 "bad_manifest_rows": strict_summary.get('bad_manifest_rows', []),
 "manifest_hash_ok": strict_summary.get('manifest_hash_ok', False),
 "rejection_reasons": strict_summary.get('rejection_reasons', {}),
}
monitor_feed_path = BASE / 'monitor_feed.json'
monitor_feed = json.loads(monitor_feed_path.read_text(encoding='utf-8')) if monitor_feed_path.exists() else {}

tel_intake_path = BASE / 'tel_intake.json'
tel_intake = json.loads(tel_intake_path.read_text(encoding='utf-8')) if tel_intake_path.exists() else {'count': 0, 'entries': []}
cold_status_path = BASE / 'cold_storage_status.json'
cold_status = json.loads(cold_status_path.read_text(encoding='utf-8')) if cold_status_path.exists() else {}
cold_status_path = BASE / 'cold_storage_status.json'
cold_status = json.loads(cold_status_path.read_text(encoding='utf-8')) if cold_status_path.exists() else {}

# ---------- source index ingestion ----------
source_index = json.load(open(ROOT / '10_SOURCES' / 'UTTP_INVESTIGATION_SOURCE_INDEX.json'))['sources']
conf_map = {
 'Government Designation':'E',
 'Government Statement':'E',
 'Government Legal Document':'E',
 'FBI Press Release':'E',
 'DOJ Press Release':'E',
 'Law Enforcement Press Release':'E',
 'Law Enforcement Publication':'E',
 'Congressional Investigation':'E',
 'Academic Panel Discussion':'C',
 'GNET Research':'C',
 'CTC West Point Research':'C',
 'Think Tank Analysis':'C',
 'Investigative Analysis':'C/A',
 'OSINT Publication':'C/A',
 'News Coverage':'C',
 'News Coverage (ISD Cited)':'C',
 'Community Wiki':'D',
 'Community Documentation':'D',
 'Public Petition':'D',
 'Primary Archive':'A',
 'Official Fediverse Account':'A',
}
seen = {nkey(x['name']) for x in sources}
for i, src in enumerate(source_index, 1):
    key = nkey(src['name'])
    if key in seen:
        continue
    seen.add(key)
    sources.append({
        "id": f"SI{i:03d}",
        "name": src['name'],
        "date": "2026-09-21",
        "type": src.get('type','source'),
        "url": src.get('link',''),
        "use": "Legacy source-index entry; verify before citation. Retained for provenance.",
        "confidence": conf_map.get(src.get('type',''), 'D'),
    })

manifest_rows = sum(1 for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts and p.name not in ('MANIFEST.csv', 'MANIFEST.sha256'))
styx_summary_path = ROOT / '09_STYXNET_REPORTS' / 'validation' / 'styxnet_validation_summary.json'
styx_summary = json.loads(styx_summary_path.read_text(encoding='utf-8')) if styx_summary_path.exists() else {}
styx_path = ROOT / '09_STYXNET_REPORTS' / 'styxnet_UTTP_csv_1789803261.csv'
styx_rows = read_csv(styx_path) if styx_path.exists() else []
search_types = styx_summary.get('search_types', {})
row_classes = styx_summary.get('row_classes', {})

discovery_dir = BASE
discovered_sources = json.loads((discovery_dir / 'discovered_sources.json').read_text(encoding='utf-8')) if (discovery_dir / 'discovered_sources.json').exists() else []
rebrands = json.loads((discovery_dir / 'rebrands.json').read_text(encoding='utf-8')) if (discovery_dir / 'rebrands.json').exists() else []
migration_events = json.loads((discovery_dir / 'migration_events.json').read_text(encoding='utf-8')) if (discovery_dir / 'migration_events.json').exists() else []
styxnet_profiles = json.loads((discovery_dir / 'styxnet_profiles.json').read_text(encoding='utf-8')) if (discovery_dir / 'styxnet_profiles.json').exists() else []
osint_findings = json.loads((BASE / 'styxnet_osint.json').read_text(encoding='utf-8')) if (BASE / 'styxnet_osint.json').exists() else []
# discovered_areas already loaded above
potential_claims = json.loads((discovery_dir / 'potential_claims.json').read_text(encoding='utf-8')) if (discovery_dir / 'potential_claims.json').exists() else []
# discovered_watchlist already loaded above
discovered_tactics = json.loads((discovery_dir / 'discovered_tactics.json').read_text(encoding='utf-8')) if (discovery_dir / 'discovered_tactics.json').exists() else []
discovery_events = json.loads((discovery_dir / 'discovery_events.json').read_text(encoding='utf-8')) if (discovery_dir / 'discovery_events.json').exists() else []
osint_state = json.loads((BASE / 'styxnet_osint_state.json').read_text(encoding='utf-8')) if (BASE / 'styxnet_osint_state.json').exists() else {}
discovery_state = json.loads((discovery_dir / 'discovery_state.json').read_text(encoding='utf-8')) if (discovery_dir / 'discovery_state.json').exists() else {}

def norm_url(value):
    value = (value or '').strip().lower().rstrip('/')
    value = re.sub(r'^https?://', '', value)
    value = re.sub(r'^www\.', '', value)
    return value

# Auto-discovered source URLs remain internal leads until validated. They are
# counted in monitor.archive but are not published in the source library.

monitor = {
 "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
 "styxnet": {
  "raw_rows": len(styx_rows) or styx_summary.get('raw_rows', 0),
  "exact_rows": search_types.get('exact', 0),
  "similarity_rows": search_types.get('similarity', 0),
  "unique_platform_labels": len({r['platform'] for r in styx_rows}),
  "unique_handle_values": styx_summary.get('unique_handles', 0),
  "platform_variants": styx_summary.get('platform_variants', 0),
  "platform_normalized_keys": styx_summary.get('platform_normalized_keys', 0),
  "candidate_handles": strict_summary.get('candidate_handles', len({r.get('aliases') or r.get('similar_username') for r in styx_rows})),
  "ownership_verified": strict_summary.get('ownership_verified', 0),
  "profile_path_unverified": row_classes.get('profile_path_unverified', 0),
  "search_or_query_pages": row_classes.get('search_or_query_page', 0),
  "error_or_gated_pages": row_classes.get('error_or_gated_page', 0),
  "unclear_rows": row_classes.get('unclear', 0),
 },
 "archive": {
  "manifest_files": manifest_rows,
  "discovered_source_count": len(discovered_sources),
  "rebrand_count": len(rebrands),
  "migration_event_count": len(migration_events),
  "discovered_area_count": len(discovered_areas),
  "potential_claim_count": len(potential_claims),
  "discovered_watchlist_count": len(discovered_watchlist),
  "discovered_tactic_count": len(discovered_tactics),
  "discovery_event_count": len(discovery_events),
  "styxnet_profile_count": len(styxnet_profiles),
  "osint_finding_count": len(osint_findings),
  "osint_exact_count": sum(1 for x in osint_findings if x.get('search_type') == 'exact' or x.get('similar_username') == x.get('username')),
  "osint_high_confidence_count": sum(1 for x in osint_findings if int(x.get('confidence') or 0) >= 70),
  "osint_new_7d": sum(1 for x in osint_findings if (x.get('first_seen') or '') >= (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')),
  "last_osint": osint_state.get('last_hunt'),
  "new_sources_7d": sum(1 for s in discovered_sources if (s.get('first_seen') or '') >= (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')),
  "new_styxnet_profiles_7d": sum(1 for s in styxnet_profiles if (s.get('first_seen') or '') >= (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')),
  "last_discovery": discovery_state.get('last_run'),
  "public_release_gb": 6,
  "entity_count": len(entities),
  "source_count": len(sources),
  "area_rows": len(area_rows),
  "area_platforms": len(areas),
  "claim_count": len(claims),
  "potential_claim_count": len(potential_claims),
  "watchlist_count": len(watchlist),
  "discovered_area_count": len(discovered_areas),
  "discovered_watchlist_count": len(discovered_watchlist),
  "discovered_tactic_count": len(discovered_tactics),
  "discovery_event_count": len(discovery_events),
  "evolution_events": sum(len(e.get("evolution",[])) for e in entities) + len(discovery_events),
  "unique_tactics": len(set(t for e in entities for t in e.get("tactics",[])) | set(discovered_tactics)),
 },
 "monitor_feed": monitor_feed,
 "tel_records": monitor_feed.get("tel_records"),
 "tel_intake": tel_intake.get("count", 0),
 "cold_storage": cold_status,
 "overtime": {
  "mode": "rule-based scheduled refresh",
  "refresh_seconds": 30,
  "last_refresh": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
  "next_checks": ["offshoot survival","platform removals","new brands","designation/arrest changes","archive integrity"],
 },
}


data = {
 "meta": {
  "title": "WinterGateIC Entity Intelligence",
  "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
  "scope": "Group-level entity monitoring. No usernames, account IDs, invite links, victim data, or private identifiers.",
  "entity_count": len(entities),
  "area_rows": len(area_rows),
  "area_platforms": len(areas),
  "source_count": len(sources),
  "claim_count": len(claims),
  "potential_claim_count": len(potential_claims),
  "watchlist_count": len(watchlist),
  "discovered_area_count": len(discovered_areas),
  "discovered_watchlist_count": len(discovered_watchlist),
  "discovered_tactic_count": len(discovered_tactics),
  "discovery_event_count": len(discovery_events),
  "privacy": "No target list. Areas are platforms/surfaces, not people. Handles are leads, not identities.",
  "learning_model": "Rule-based adaptive scoring from confidence, source density, tactical indicators, area footprint, and evolution timeline. Not a predictive AI model and not a claim of future certainty.",
 },
 "entities": entities,
 "areas": areas,
 "area_rows": areas and area_rows and [dict(r) for r in area_rows],
 "sources": sources,
 "claims": claims,
 "watchlist": watchlist,
 "potential_claims": potential_claims,
 "discovery_events": discovery_events,
 "discovered_tactics": discovered_tactics,
 "rebrands": rebrands,
 "migration_events": migration_events,
 "styxnet_profiles": styxnet_profiles,
 "osint_findings": osint_findings,
 "strict_validation": strict_validation,
 "monitor_feed": monitor_feed,
 "tel_intake": tel_intake,
 "cold_storage": cold_status,
 "methods": methods,
 "tel_records": monitor_feed.get("tel_records"),
 "monitor": monitor,
 "evolution_model": {
  "stages": ["origin","escalation","fragmentation","bridge","decline","successor"],
  "rules": [
   "Stage is derived from the documented evolution timeline, not inferred from a single event.",
   "Risk score is a weighted sum of confidence, source density, tactical indicators, area footprint, and recency.",
   "A high risk score means 'more evidence and more severe harm indicators'; it is not a probability of future violence.",
   "Morphology predictions are assessments, not facts: a fragmented brand is likely to rebrand, migrate, or splinter.",
   "No individual identity, membership, or command relationship is inferred from a handle, nickname, or group name.",
  ],
  "morphology": [
   {"pattern":"fragmented brand","prediction":"rebrand, migration, or micro-splinter formation","basis":"UTTP 2026 record"},
   {"pattern":"hardcore offshoot","prediction":"structured rebrand and tactical overlap","basis":"DPOS record"},
   {"pattern":"designated network","prediction":"cell/offshoot churn under enforcement","basis":"764 record"},
   {"pattern":"ideological ecosystem","prediction":"influence through texts and autonomous nexions","basis":"O9A record"},
  ],
 },
}
# write repo + site
OUT_REPO.parent.mkdir(parents=True, exist_ok=True)
OUT_SITE.parent.mkdir(parents=True, exist_ok=True)
text = json.dumps(data, indent=2, ensure_ascii=False)
OUT_REPO.write_text(text, encoding='utf-8')
if SITE.exists():
    OUT_SITE.parent.mkdir(parents=True, exist_ok=True)
    OUT_SITE.write_text(text, encoding='utf-8')
print('entities', len(entities), 'areas', len(areas), 'area_rows', len(area_rows), 'sources', len(sources), 'claims', len(claims), 'watchlist', len(watchlist))
