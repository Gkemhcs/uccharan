"""Seeds Level 3 ("Real-World Fluency", Days 61-90) of the 90-day roadmap into
Firestore: lessons for each day plus one multiple-choice quiz per day.

Level 3 picks up where Level 2 (seed_days_31_to_60_content.py) left off — B1/B2
independent-user fluency. Same design principles as Levels 1 and 2:
  - Every target sentence is a genuine, high-frequency spoken-English phrase,
    not textbook-stiff filler. Level 3 sentences are longer and more complex
    (subordinate clauses, connectors, multi-clause reasoning) than Level 1-2.
  - Grammar notes target real, published L1-interference patterns for
    Telugu speakers (dropped articles/prepositions, literal calques, word
    order, double negatives, etc).
  - Every target sentence and vocab word carries a Telugu translation.
  - Quiz distractors are unambiguously wrong (a genuine grammar error), and
    explanations never concede that a "wrong" option is actually valid
    alternate phrasing — see the Day 27 fix in seed_weeks_2_to_5_content.py
    for why that matters.

Telugu text here was written by Claude (not a certified native reviewer) —
correct standard Telugu to the best of that ability, but worth a native
speaker's read-through before this is the only Telugu a learner sees.

This upserts (PATCH-with-full-fields, not skip-on-exists) so re-running is safe.

Usage:
    python3 backend/scripts/seed_days_61_to_90_content.py
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

PROJECT_ID = "uccharan-87bcf"
DB_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"


def to_firestore_value(value):
    if isinstance(value, bool):
        return {"booleanValue": value}
    if isinstance(value, int):
        return {"integerValue": str(value)}
    if isinstance(value, str):
        return {"stringValue": value}
    if isinstance(value, list):
        return {"arrayValue": {"values": [to_firestore_value(v) for v in value]}}
    if isinstance(value, dict):
        return {"mapValue": {"fields": {k: to_firestore_value(v) for k, v in value.items()}}}
    raise TypeError(f"Unsupported type for Firestore value: {type(value)}")


def upsert(collection: str, doc_id: str, fields: dict) -> None:
    """PATCH creates-or-replaces a document at a known id — safe to re-run."""
    body = {"fields": {k: to_firestore_value(v) for k, v in fields.items()}}
    url = f"{DB_URL}/{collection}/{doc_id}"
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="PATCH",
    )
    try:
        with urllib.request.urlopen(request) as response:
            response.read()
        print(f"seeded {collection}/{doc_id}")
    except urllib.error.HTTPError as e:
        print(f"FAILED {collection}/{doc_id}: {e.code} {e.read().decode('utf-8')}")


# ---------------------------------------------------------------------------
# Lessons — one list per day. Each tuple:
# (id, order, targetSentence, nativeTranslation, focusSounds, vocabWord,
#  vocabMeaning, vocabNativeMeaning, grammarNote)
# ---------------------------------------------------------------------------

DAY61_LESSONS = [
    ("day61-debate-01", 1, "In my opinion, public transport should be free for students.", "నా అభిప్రాయం ప్రకారం, విద్యార్థులకు ప్రజా రవాణా ఉచితంగా ఉండాలి.",
     ["/tr/ cluster in 'transport'", "/fr/ cluster in 'free'"], "public transport", "buses, trains, etc. that anyone can use for a fee", "ప్రజా రవాణా వ్యవస్థ",
     "'In my opinion, ...' is used to introduce a personal view politely at the start of a sentence; Telugu speakers often skip this framing phrase and state opinions as flat facts, which can sound blunt in English."),
    ("day61-debate-02", 2, "I understand why you think that, but I don't fully agree.", "మీరు అలా ఎందుకు అనుకుంటున్నారో నాకు అర్థమైంది, కానీ నేను పూర్తిగా ఏకీభవించను.",
     ["/ð/ in 'that'", "/f/ in 'fully'"], "agree", "to have the same opinion as someone", "ఏకీభవించడం",
     "'I understand why you think that, but...' acknowledges the other person's view before disagreeing — a politeness pattern; Telugu speakers often disagree directly with 'no, that's wrong', which can sound rude in an English debate."),
    ("day61-debate-03", 3, "I see your point, but I think the evidence says something different.", "మీ వాదన నాకు అర్థమైంది, కానీ ఆధారాలు వేరేగా చెప్తున్నాయని నేను అనుకుంటున్నాను.",
     ["/v/ vs /w/ in 'evidence'", "/θ/ in 'think'"], "evidence", "facts or proof that show something is true", "ఆధారాలు",
     "'I see your point' is a fixed phrase acknowledging an argument before countering it; note that 'evidence' takes no article and no plural '-s' because it is uncountable, unlike its Telugu equivalent which speakers sometimes pluralize by analogy."),
    ("day61-debate-04", 4, "Some people believe exams are necessary, while others feel they cause too much stress.", "పరీక్షలు అవసరమని కొందరు నమ్ముతారు, మరికొందరు అవి చాలా ఒత్తిడిని కలిగిస్తాయని భావిస్తారు.",
     ["/z/ in 'exams'", "/s/ vs /ʃ/ in 'stress'"], "necessary", "needed; required", "అవసరమైన",
     "'Some people believe..., while others feel...' presents two opposing opinions in one balanced sentence using 'while' as a contrast connector; Telugu speakers often chain contrasting ideas with repeated 'but' instead of varying connectors like 'while' or 'whereas'."),
    ("day61-debate-05", 5, "With all due respect, I have to disagree with that argument.", "మీ అభిప్రాయాన్ని గౌరవిస్తూనే, ఆ వాదనతో నేను ఏకీభవించలేను.",
     ["/d/ in 'due'", "/g/ in 'argument'"], "argument", "a reason or set of reasons given to support an opinion (not a fight)", "వాదన",
     "'With all due respect' is a fixed polite opener used before a firm disagreement; Telugu speakers sometimes skip such softening phrases entirely, since Telugu conveys respect more through tone and honorifics than through set English phrases."),
]

DAY62_LESSONS = [
    ("day62-negotiate-01", 1, "If you can give me a better price, I'll buy two of them.", "మీరు నాకు మంచి ధర ఇస్తే, నేను రెండు కొంటాను.",
     ["/b/ in 'better'", "/pr/ cluster in 'price'"], "price", "the amount of money something costs", "ధర",
     "'If you can do X, I'll do Y' is a first conditional used for realistic offers; Telugu speakers often drop 'will' in the result clause, saying 'I buy' instead of 'I'll buy', because Telugu future tense doesn't require a separate auxiliary word."),
    ("day62-negotiate-02", 2, "I'm sorry, but I can't go any lower than this.", "క్షమించండి, కానీ నేను దీని కంటే తక్కువకు ఇవ్వలేను.",
     ["/l/ in 'lower'", "/ð/ in 'this'"], "lower", "to reduce (a price)", "తగ్గించడం",
     "'I can't go any lower' is a polite-but-firm way to refuse further reduction; softening it with 'I'm sorry, but' models polite firmness, a pattern Telugu speakers often replace with a blunt, direct refusal."),
    ("day62-negotiate-03", 3, "If you include free delivery, we have a deal.", "మీరు ఉచిత డెలివరీ కలిపితే, ఒప్పందం కుదిరినట్టే.",
     ["/f/ in 'free'", "/d/ in 'deal'"], "deal", "an agreement, especially in business", "ఒప్పందం",
     "This conditional states a specific condition for agreement; the result clause 'we have a deal' needs no 'will' because it describes an immediate result, not a future one — a nuance often missed when Telugu speakers force 'will' into every conditional result."),
    ("day62-negotiate-04", 4, "Would you be willing to accept payment in two installments?", "మీరు రెండు వాయిదాలలో చెల్లింపు తీసుకోవడానికి ఒప్పుకుంటారా?",
     ["/w/ in 'willing'", "/st/ cluster in 'installments'"], "installment", "one of several parts a payment is divided into", "వాయిదా",
     "'Would you be willing to...?' is a polite, indirect way to ask for flexibility in negotiation; Telugu speakers often ask directly with 'Can I pay in parts?', which is grammatically fine but less diplomatically softened for formal negotiation."),
    ("day62-negotiate-05", 5, "If we order in bulk, will you reduce the price per unit?", "మేము పెద్ద మొత్తంలో ఆర్డర్ చేస్తే, మీరు యూనిట్‌కు ధర తగ్గిస్తారా?",
     ["/r/ in 'reduce'", "/b/ in 'bulk'"], "bulk", "a large quantity", "పెద్ద మొత్తం/టోకు",
     "In a first conditional question, the if-clause uses present tense ('we order') while the question clause uses 'will' ('will you reduce'); Telugu speakers sometimes put 'will' in the if-clause too, saying 'If we will order', which is incorrect in English."),
]

DAY63_LESSONS = [
    ("day63-interview-01", 1, "Tell me about yourself and your work experience.", "మీ గురించి మరియు మీ పని అనుభవం గురించి చెప్పండి.",
     ["/rs/ cluster in 'yourself'", "/w/ in 'work'"], "experience", "knowledge or skill gained from doing a job over time", "అనుభవం",
     "'Tell me about yourself' uses the reflexive pronoun 'yourself' to ask for a self-introduction; Telugu speakers often translate literally as 'tell about you', dropping the reflexive '-self' form entirely."),
    ("day63-interview-02", 2, "My greatest strength is that I stay calm under pressure.", "నా అతిపెద్ద బలం ఏమిటంటే, ఒత్తిడిలో కూడా నేను ప్రశాంతంగా ఉండగలను.",
     ["/str/ cluster in 'strength'", "/pr/ cluster in 'pressure'"], "strength", "a good quality or skill someone has", "బలం, సానుకూల లక్షణం",
     "'My greatest strength is that + clause' is a fixed interview pattern; Telugu speakers often drop 'that' and say 'My strength is I stay calm', which sounds informal — 'that' is required here before a full clause acting as a noun complement."),
    ("day63-interview-03", 3, "One area I'm working to improve is my time management.", "నేను మెరుగుపరచుకోవాలని అనుకుంటున్న ఒక విషయం నా సమయపాలన.",
     ["/r/ in 'area'", "/pr/ cluster in 'improve'"], "improve", "to make something better", "మెరుగుపరచడం",
     "This softened phrasing for a weakness uses present continuous ('am working to improve') instead of a blunt static statement, signaling ongoing effort; Telugu speakers often state weaknesses as fixed facts ('I am weak in time management'), which sounds more negative in an interview."),
    ("day63-interview-04", 4, "I'm looking for a role where I can grow and take on more responsibility.", "నేను ఎదగగలిగే మరియు ఎక్కువ బాధ్యతలు తీసుకోగలిగే ఉద్యోగం కోసం చూస్తున్నాను.",
     ["/r/ in 'role'", "/g/ in 'grow'"], "responsibility", "a duty or task that you are expected to handle", "బాధ్యత",
     "'a role where I can...' uses 'where' as a relative pronoun referring to a job or position, not a physical place; Telugu speakers sometimes avoid this structure and use two separate sentences instead of joining them with a relative clause."),
    ("day63-interview-05", 5, "Why should we hire you over other candidates?", "ఇతర అభ్యర్థుల కంటే మేము మిమ్మల్ని ఎందుకు నియమించుకోవాలి?",
     ["/h/ in 'hire'", "/k/ in 'candidates'"], "candidate", "a person applying for a job", "అభ్యర్థి",
     "'over other candidates' uses 'over' to mean 'in preference to', a common interview comparison structure; Telugu speakers often substitute 'than' here by analogy with regular comparatives, but 'over' is the idiomatically correct choice in this hiring context."),
]

DAY64_LESSONS = [
    ("day64-lifegoals-01", 1, "I'm going to start my own business in five years.", "నేను ఐదు సంవత్సరాలలో నా సొంత వ్యాపారం ప్రారంభించబోతున్నాను.",
     ["/z/ in 'business'", "/f/ in 'five'"], "own", "belonging to oneself, not shared or borrowed", "సొంతం",
     "'going to + base verb' expresses a firm future plan or intention decided in advance; Telugu speakers sometimes use simple future 'I will start' instead, which sounds more like a spontaneous decision than a long-term plan."),
    ("day64-lifegoals-02", 2, "By next year, I'll be working as a certified accountant.", "వచ్చే సంవత్సరానికల్లా, నేను ధృవీకరించబడిన అకౌంటెంట్‌గా పని చేస్తూ ఉంటాను.",
     ["/rt/ cluster in 'certified'", "/k/ in 'accountant'"], "certified", "officially recognized as having completed training in a skill", "ధృవీకరించబడిన",
     "Future continuous ('I'll be working') describes an action that will be in progress at a specific future point; Telugu speakers often use simple future ('I will work') here, losing the sense of an ongoing state at that future time."),
    ("day64-lifegoals-03", 3, "This time next year, we'll be living in our own house.", "వచ్చే సంవత్సరం ఈ సమయానికి, మేము మా సొంత ఇంట్లో ఉంటూ ఉంటాము.",
     ["/ð/ in 'this'", "/v/ vs /w/ in 'living'"], "own house", "a house that belongs to you, not rented", "సొంత ఇల్లు",
     "'This time next year, we'll be ___-ing' is a fixed pattern for picturing a future state in progress; Telugu has no direct grammatical equivalent to this continuous aspect, so learners often just say 'we will be in our own house' without the '-ing' verb form."),
    ("day64-lifegoals-04", 4, "I'm planning to learn a new skill every year for the next five years.", "వచ్చే ఐదు సంవత్సరాలు ప్రతి సంవత్సరం ఒక కొత్త నైపుణ్యం నేర్చుకోవాలని నేను ప్లాన్ చేస్తున్నాను.",
     ["/pl/ cluster in 'planning'", "/sk/ cluster in 'skill'"], "skill", "the ability to do something well, usually learned through practice", "నైపుణ్యం",
     "'I'm planning to + verb' expresses a deliberate long-term intention; 'planning' takes 'to + base verb', not 'planning of' or 'planning for + verb-ing', a preposition error Telugu speakers sometimes make by over-adding prepositions."),
    ("day64-lifegoals-05", 5, "In ten years, I hope to be running my own school.", "పది సంవత్సరాలలో, నేను నా సొంత పాఠశాలను నడుపుతూ ఉండాలని ఆశిస్తున్నాను.",
     ["/r/ in 'running'", "/sk/ cluster in 'school'"], "hope", "to want something to happen in the future and expect it's possible", "ఆశించడం",
     "'I hope to be running' combines 'hope to' with a continuous infinitive to express a wished-for ongoing future state; Telugu speakers often simplify this to 'I hope to run', which is grammatical but loses the emphasis on the activity being ongoing at that future time."),
]

DAY65_LESSONS = [
    ("day65-service-01", 1, "I'd like to speak to the manager, please.", "దయచేసి నేను మేనేజర్‌తో మాట్లాడాలనుకుంటున్నాను.",
     ["/sp/ cluster in 'speak'", "/m/ in 'manager'"], "manager", "the person in charge of a shop, restaurant, or business", "నిర్వాహకుడు/మేనేజర్",
     "'I'd like to + verb' (short for 'I would like to') is a polite, indirect way to make a request, softer than 'I want'; Telugu speakers often use 'I want to speak' directly, which is fine but sounds more demanding in a service complaint."),
    ("day65-service-02", 2, "This product is defective, and I'd like a full refund.", "ఈ వస్తువు లోపభూయిష్టంగా ఉంది, నాకు పూర్తి రీఫండ్ కావాలి.",
     ["/f/ in 'defective'", "/f/ in 'refund'"], "refund", "money given back when a product is returned", "వాపసు/రీఫండ్",
     "The connector 'and' joins the stated problem with the requested solution in one firm sentence; Telugu speakers often state only the problem and expect the solution to be inferred, whereas English service complaints typically state the desired outcome explicitly."),
    ("day65-service-03", 3, "I've already asked twice, so now I need to speak to someone senior.", "నేను ఇప్పటికే రెండుసార్లు అడిగాను, కాబట్టి ఇప్పుడు నేను సీనియర్ వ్యక్తితో మాట్లాడాలి.",
     ["/tw/ cluster in 'twice'", "/s/ vs /ʃ/ in 'senior'"], "senior", "higher in rank or position", "సీనియర్/పైస్థాయి వ్యక్తి",
     "Present perfect 'I've already asked' emphasizes that the action happened before now and is relevant to the current problem; Telugu speakers often use simple past 'I asked twice' here, losing the sense of continued relevance that justifies escalating the complaint."),
    ("day65-service-04", 4, "If this isn't resolved today, I'll have to file a formal complaint.", "ఇది ఈరోజు పరిష్కరించకపోతే, నేను అధికారికంగా ఫిర్యాదు చేయాల్సి వస్తుంది.",
     ["/r/ in 'resolved'", "/f/ in 'formal'"], "resolve", "to fix or settle a problem", "పరిష్కరించడం",
     "This conditional politely threatens a firm next step, using 'if...isn't...I'll have to...'; Telugu speakers sometimes drop the negative auxiliary and say 'If this not resolved', omitting 'is/isn't', because Telugu doesn't require a separate auxiliary verb in such clauses."),
    ("day65-service-05", 5, "Could you explain why I was charged twice for the same order?", "నేను ఒకే ఆర్డర్‌కి రెండుసార్లు ఎందుకు చార్జ్ చేయబడ్డానో మీరు వివరించగలరా?",
     ["/tʃ/ in 'charged'", "/ks/ cluster in 'explain'"], "charge", "to ask someone to pay an amount of money", "చార్జ్ చేయడం/వసూలు చేయడం",
     "'Could you explain why...' is a polite indirect question, where the embedded question keeps normal word order ('I was charged') instead of question word order ('was I charged'); Telugu speakers learning this structure often mistakenly invert the embedded clause as if it were a direct question."),
]

DAY66_LESSONS = [
    ("day66-news-01", 1, "I read that the government is planning to reduce fuel prices.", "ప్రభుత్వం ఇంధన ధరలు తగ్గించాలని ప్లాన్ చేస్తోందని నేను చదివాను.",
     ["/r/ in 'reduce'", "/v/ vs /w/ in 'government'"], "government", "the group of people who officially govern a country", "ప్రభుత్వం",
     "'I read that + clause' reports information from a written source; Telugu speakers often drop 'that' or restructure this as two separate sentences ('I read the news. Government will reduce prices.') instead of embedding it as one clause."),
    ("day66-news-02", 2, "They say that the new law will affect small businesses the most.", "కొత్త చట్టం చిన్న వ్యాపారాలను ఎక్కువగా ప్రభావితం చేస్తుందని చెప్తున్నారు.",
     ["/ð/ in 'they'", "/f/ in 'affect'"], "affect", "to have an influence on something or someone", "ప్రభావితం చేయడం",
     "'They say that...' reports a general, widely-held opinion without naming a specific source; Telugu speakers sometimes translate this too literally as 'people are saying', which shifts the tone from a neutral report to gossip."),
    ("day66-news-03", 3, "According to today's news, the match was cancelled due to rain.", "ఈ రోజు వార్తల ప్రకారం, వర్షం కారణంగా మ్యాచ్ రద్దు చేయబడింది.",
     ["/k/ in 'according'", "/dj/ in 'due'"], "cancel", "to officially stop an event from happening", "రద్దు చేయడం",
     "'According to + source' introduces reported information from a specific place, like news or a person; Telugu speakers often use 'news says' as a direct calque instead of the natural English pattern 'according to the news'."),
    ("day66-news-04", 4, "I heard that prices are going to rise again next month.", "వచ్చే నెల ధరలు మళ్ళీ పెరుగుతాయని నేను విన్నాను.",
     ["/h/ in 'heard'", "/r/ in 'rise'"], "rise", "to increase or go up", "పెరగడం",
     "'I heard that + clause' reports something learned orally, distinct from 'I read that' for written sources; both use 'that' to introduce the reported clause, a connector Telugu speakers frequently omit since Telugu doesn't require an equivalent linking word in reported speech."),
    ("day66-news-05", 5, "Many experts believe that the economy will improve next year.", "ఆర్థిక వ్యవస్థ వచ్చే సంవత్సరం మెరుగుపడుతుందని చాలామంది నిపుణులు నమ్ముతారు.",
     ["/eks/ cluster in 'experts'", "/v/ in 'improve'"], "expert", "a person with special knowledge or skill in a subject", "నిపుణుడు",
     "'Many experts believe that...' reports a collective professional opinion using the same 'believe/say/think + that' pattern; Telugu speakers sometimes place the reporting phrase at the end of the sentence by direct translation from Telugu word order, whereas English requires it at the front."),
]

DAY67_LESSONS = [
    ("day67-decision-01", 1, "I decided to take the job because it offered better opportunities.", "మంచి అవకాశాలు ఇచ్చిందని ఆ ఉద్యోగం తీసుకోవాలని నేను నిర్ణయించుకున్నాను.",
     ["/dʒ/ in 'job'", "/f/ in 'offered'"], "opportunity", "a chance to do something beneficial", "అవకాశం",
     "'because' introduces the reason for a decision with a full clause; Telugu speakers often drop the conjunction and just place two clauses side by side, so practice keeping 'because' explicit in English."),
    ("day67-decision-02", 2, "In the end, I chose to stay in my hometown instead of moving to the city.", "చివరికి, నేను నగరానికి వెళ్లే బదులు నా సొంత ఊర్లోనే ఉండిపోవాలని నిర్ణయించుకున్నాను.",
     ["/tʃ/ in 'chose'", "/v/ vs /w/ in 'moving'"], "instead of", "in place of; as an alternative to", "కి బదులుగా",
     "'instead of' is followed by a verb + '-ing' form (moving), not the base verb — Telugu speakers often say 'instead of move' by direct translation from the native structure."),
    ("day67-decision-03", 3, "I thought about it carefully before I made my final decision.", "నా చివరి నిర్ణయం తీసుకునే ముందు నేను దాని గురించి జాగ్రత్తగా ఆలోచించాను.",
     ["/θ/ in 'thought'", "/f/ in 'final'"], "carefully", "in a careful, cautious way", "జాగ్రత్తగా",
     "'before' + subject + past simple ('before I made') keeps both past events in simple past tense to show their order; Telugu speakers sometimes shift to a different tense in the second clause, breaking this parallel structure."),
    ("day67-decision-04", 4, "My main reason for choosing this college was its good reputation.", "నేను ఈ కళాశాలను ఎంచుకోవడానికి ప్రధాన కారణం దాని మంచి పేరు.",
     ["/r/ in 'reason'", "/dʒ/ in 'college'"], "reputation", "the general opinion people have about someone or something", "పేరు ప్రతిష్ట",
     "'reason for + verb-ing' (choosing) is the correct pattern; Telugu speakers often mix it with 'reason to' and produce 'reason for choose' or 'reason to choosing'."),
    ("day67-decision-05", 5, "Looking back, I believe I made the right decision.", "ఇప్పుడు వెనక్కి తిరిగి చూస్తే, నేను సరైన నిర్ణయమే తీసుకున్నానని నమ్ముతున్నాను.",
     ["/l/ in 'looking'", "/r/ in 'right'"], "looking back", "thinking about something after it has happened; in retrospect", "వెనక్కి తిరిగి చూస్తే",
     "'Looking back' is a fixed participle phrase used to open a sentence of reflection on the past; Telugu speakers often translate this literally as 'seeing back', so this English chunk needs direct memorization rather than word-for-word translation."),
]

DAY68_LESSONS = [
    ("day68-narrative-01", 1, "I was walking home when it suddenly started raining.", "నేను ఇంటికి నడుచుకుంటూ వెళ్తుండగా అకస్మాత్తుగా వర్షం మొదలైంది.",
     ["/w/ in 'was' and 'walking'", "/r/ in 'raining'"], "suddenly", "quickly and unexpectedly", "అకస్మాత్తుగా",
     "Past continuous ('was walking') sets the background scene, and past simple ('started') marks the interrupting action; Telugu speakers often use one continuous-style verb for both, so remember to switch tenses for the sudden event."),
    ("day68-narrative-02", 2, "While I was cooking dinner, the phone rang.", "నేను వంట చేస్తుండగా ఫోన్ మోగింది.",
     ["/f/ in 'phone'", "/ŋ/ in 'cooking' and 'rang'"], "while", "during the time that something else was happening", "అదే సమయంలో",
     "'While' + past continuous introduces the longer background action, and the short interrupting action takes past simple ('rang'); Telugu speakers sometimes pair 'while' with a simple past verb instead, losing the sense of an ongoing action."),
    ("day68-narrative-03", 3, "She was sleeping when the earthquake happened.", "భూకంపం వచ్చినప్పుడు ఆమె నిద్రపోతోంది.",
     ["/sl/ cluster in 'sleeping'", "/kw/ in 'earthquake'"], "happened", "took place; occurred", "జరిగింది",
     "'when' + past simple marks the sudden event that interrupts an ongoing past continuous action; Telugu speakers often drop the auxiliary 'was' and just say 'she sleeping', so the auxiliary must be practiced."),
    ("day68-narrative-04", 4, "We were watching the match when the power went out.", "మేము మ్యాచ్ చూస్తుండగా కరెంటు పోయింది.",
     ["/w/ in 'watching' and 'went'", "/tʃ/ in 'match'"], "went out", "stopped working suddenly, especially for electricity", "కరెంటు పోవడం",
     "'went out' is a fixed phrasal verb for a sudden electricity failure; Telugu speakers often say 'current went' or 'light went' as a direct calque instead of the correct 'the power went out'."),
    ("day68-narrative-05", 5, "In the end, everything turned out fine.", "చివరికి, అంతా బాగానే జరిగింది.",
     ["/f/ in 'fine'", "/nd/ cluster in 'end'"], "turned out", "ended up being a certain way, especially after uncertainty", "చివరికి అలా జరిగింది",
     "'In the end' and 'turned out' are narrative connectors that signal how a story concludes; Telugu speakers often substitute a generic 'at last' in every context, while 'in the end' fits best after a story with some tension or uncertainty."),
]

DAY69_LESSONS = [
    ("day69-presentation-01", 1, "Firstly, I'd like to talk about our sales results.", "మొదటిగా, మన అమ్మకాల ఫలితాల గురించి మాట్లాడాలనుకుంటున్నాను.",
     ["/f/ in 'firstly'", "/s/ in 'sales' and 'results'"], "firstly", "used to introduce the first point in a list or speech", "మొదటిగా",
     "Signposting words like 'firstly' sit at the very start of the sentence, followed by a comma, to organize a spoken presentation; Telugu speakers often skip these markers since the native speaking style relies more on context than explicit ordering words."),
    ("day69-presentation-02", 2, "Secondly, let's look at the challenges we faced.", "రెండవదిగా, మనం ఎదుర్కొన్న సవాళ్లను చూద్దాం.",
     ["/tʃ/ in 'challenges'", "/f/ in 'faced'"], "challenge", "a difficult task or problem", "సవాలు",
     "'let's + base verb' makes a suggestion to the audience ('let's look'); Telugu speakers sometimes add 'to' after 'let's' by analogy with other verb patterns, which is incorrect."),
    ("day69-presentation-03", 3, "Moving on, I'll explain our plan for next year.", "తర్వాత విషయానికి వస్తే, వచ్చే సంవత్సరానికి మా ప్రణాళికను వివరిస్తాను.",
     ["/v/ in 'moving'", "/pl/ cluster in 'plan'"], "moving on", "a phrase used to signal a shift to the next topic", "తర్వాత విషయానికి వస్తే",
     "'Moving on' is a present participle phrase acting as a transition signal, set off by a comma; this fixed spoken formula has no single-word Telugu equivalent, so it should be learned as one chunk."),
    ("day69-presentation-04", 4, "Finally, I'll take any questions you have.", "చివరగా, మీకున్న ప్రశ్నలు ఏమైనా ఉంటే తీసుకుంటాను.",
     ["/f/ in 'finally'", "/kw/ in 'questions'"], "finally", "used to introduce the last point", "చివరగా",
     "'any' modifies the plural countable noun 'questions' in this open, inviting offer; Telugu speakers sometimes use 'some' instead, which sounds less natural in this open-ended context."),
    ("day69-presentation-05", 5, "To sum up, this project has been a great success.", "సారాంశంగా చెప్పాలంటే, ఈ ప్రాజెక్టు గొప్ప విజయం సాధించింది.",
     ["/s/ in 'sum' and 'success'", "/dʒ/ in 'project'"], "to sum up", "used to give a brief summary before ending", "సారాంశంగా చెప్పాలంటే",
     "Present perfect ('has been') links a past project to its relevance right now, at the end of the presentation; Telugu speakers commonly use simple past ('was a success') here, losing the sense that the result still matters now."),
]

DAY70_LESSONS = [
    ("day70-hypothetical-01", 1, "If it rains tomorrow, I will cancel the trip.", "రేపు వర్షం పడితే, నేను ప్రయాణాన్ని రద్దు చేస్తాను.",
     ["/r/ in 'rains'", "/k/ in 'cancel'"], "cancel", "to decide that a planned event will not happen", "రద్దు చేయడం",
     "First conditional: 'If' + present simple, 'will' + base verb, for a real future possibility; Telugu speakers often use 'will' in both clauses ('if it will rain'), which is incorrect in English."),
    ("day70-hypothetical-02", 2, "If I had more time, I would learn to drive.", "నాకు ఇంకా సమయం ఉంటే, నేను డ్రైవింగ్ నేర్చుకుంటాను.",
     ["/dr/ cluster in 'drive'", "/l/ in 'learn'"], "would", "a modal verb used to imagine an unreal or unlikely present situation", "ఊహాజనిత పరిస్థితిని చూపే క్రియ",
     "Second conditional: 'If' + past simple, 'would' + base verb, imagines a present situation that isn't real; Telugu speakers sometimes keep 'will' instead of switching to 'would', which fails to signal that the situation is hypothetical."),
    ("day70-hypothetical-03", 3, "If I had known about the traffic, I would have left earlier.", "ట్రాఫిక్ గురించి నాకు ముందే తెలిస్తే, నేను ముందుగానే బయలుదేరేవాడిని.",
     ["/tr/ cluster in 'traffic'", "/l/ in 'left' and 'earlier'"], "traffic", "vehicles moving on a road, especially in large numbers", "ట్రాఫిక్ / రద్దీ",
     "Third conditional: 'If' + past perfect ('had known'), 'would have' + past participle ('left'), talks about an unreal past regret; Telugu speakers often use simple past in both clauses, which doesn't capture the sense of 'too late to change it'."),
    ("day70-hypothetical-04", 4, "If she studies hard, she will pass the exam.", "ఆమె బాగా చదివితే, పరీక్షలో పాస్ అవుతుంది.",
     ["/st/ cluster in 'studies'", "/z/ in 'exam'"], "pass", "to succeed in a test or exam", "ఉత్తీర్ణత సాధించడం",
     "In first conditional sentences, the 'if' clause never takes 'will', even though it refers to the future — only the main clause does; this is a common error for Telugu speakers translating a future idea into both halves of the sentence."),
    ("day70-hypothetical-05", 5, "If I were you, I would ask for help.", "నేను నీ స్థానంలో ఉంటే, సహాయం అడుగుతాను.",
     ["/w/ in 'were'", "/h/ in 'help'"], "were", "the subjunctive form of 'was', used in hypothetical statements regardless of subject", "ఊహాజనితంగా ఉంటే",
     "'If I were you' is a fixed advice-giving pattern that always uses 'were', not 'was', even with the subject 'I'; this exception to normal past-tense agreement often confuses Telugu learners who expect 'was' with a singular subject."),
]

DAY71_LESSONS = [
    ("day71-formal-01", 1, "I would be grateful if you could send me the report by Friday.", "మీరు శుక్రవారంలోగా నివేదికను పంపిస్తే నేను కృతజ్ఞతతో ఉంటాను.",
     ["/gr/ cluster in 'grateful'", "/r/ in 'report'"], "grateful", "feeling or showing thanks", "కృతజ్ఞత కలిగిన",
     "'I would be grateful if you could...' is a very formal, polite request pattern using two modal-style structures together; Telugu speakers often simplify this to a direct command ('please send'), which sounds less polite in formal English writing."),
    ("day71-formal-02", 2, "Could you possibly explain that point again?", "దయచేసి ఆ విషయాన్ని మళ్ళీ వివరించగలరా?",
     ["/p/ in 'possibly'", "/ks/ in 'explain'"], "possibly", "added to a request to make it sound softer and more polite", "వీలైతే",
     "Inserting 'possibly' after a modal ('Could you possibly') softens a request further than 'Could you' alone; Telugu speakers often omit softening words like this since politeness is expressed differently, through tone and honorifics, rather than extra words."),
    ("day71-formal-03", 3, "Would it be possible to reschedule our meeting?", "మన మీటింగ్‌ని వేరే సమయానికి మార్చడం సాధ్యమేనా?",
     ["/dʒ/ in 'reschedule'", "/m/ in 'meeting'"], "reschedule", "to change the planned time of an event", "సమయాన్ని మార్చడం",
     "'Would it be possible to + verb' is an indirect, formal way to make a request without addressing 'you' directly; this indirectness is a feature of polite English that Telugu speakers may skip in favor of more direct phrasing."),
    ("day71-formal-04", 4, "I was wondering if you could help me with this problem.", "మీరు ఈ సమస్యలో నాకు సహాయం చేయగలరేమో అని అనుకుంటున్నాను.",
     ["/w/ in 'wondering'", "/pr/ cluster in 'problem'"], "wondering", "thinking about something with mild uncertainty, often used to introduce a polite request", "ఏమో అని అనుకోవడం",
     "'I was wondering if...' uses past continuous to make a present request sound softer and less direct, a common politeness strategy in formal English; Telugu speakers often use straightforward present tense, missing this distancing effect."),
    ("day71-formal-05", 5, "Thank you for your time; I look forward to hearing from you.", "మీ సమయానికి ధన్యవాదాలు; మీ నుండి వినడానికి ఎదురుచూస్తుంటాను.",
     ["/θ/ in 'thank'", "/h/ in 'hearing'"], "look forward to", "to feel happy or excited about something that will happen", "ఎదురు చూడటం",
     "'look forward to' is followed by a verb + '-ing' (hearing), not the base verb 'to hear' — a frequent error since the 'to' here is a preposition, not part of an infinitive."),
]

DAY72_LESSONS = [
    ("day72-medical-01", 1, "I've had a headache for three days now.", "నాకు మూడు రోజులుగా తలనొప్పిగా ఉంది.",
     ["/h/ in 'headache'", "/θ/ in 'three'"], "headache", "a pain in the head", "తలనొప్పి",
     "Present perfect ('I've had') with 'for' + duration describes a symptom that started in the past and continues now; Telugu speakers often use simple present ('I have headache since three days'), missing both the auxiliary and the correct preposition 'for'."),
    ("day72-medical-02", 2, "It hurts whenever I bend down.", "నేను వంగిన ప్రతిసారి నొప్పిగా ఉంటుంది.",
     ["/h/ in 'hurts'", "/b/ in 'bend'"], "bend down", "to lower the top part of the body forward or downward", "వంగడం",
     "'whenever' + present simple describes a repeated, general condition — 'it hurts' takes the '-s' ending for the third person 'it', which Telugu speakers frequently drop since Telugu verbs don't mark agreement the same way."),
    ("day72-medical-03", 3, "I've been feeling dizzy since yesterday morning.", "నిన్న ఉదయం నుండి నాకు తలతిరుగుతున్నట్టుగా ఉంది.",
     ["/z/ in 'dizzy'", "/f/ in 'feeling'"], "dizzy", "feeling unsteady, as if everything is spinning", "తలతిరగడం",
     "Present perfect continuous ('I've been feeling') with 'since' + a starting point emphasizes a symptom continuing from a specific time until now; 'since' pairs with a point in time while 'for' pairs with a duration, and Telugu speakers often confuse the two."),
    ("day72-medical-04", 4, "The pain gets worse at night.", "రాత్రి పూట నొప్పి ఎక్కువగా ఉంటుంది.",
     ["/w/ in 'worse'", "/n/ in 'night'"], "worse", "more severe or bad; the comparative form of 'bad'", "మరింత తీవ్రంగా",
     "'worse' is the irregular comparative of 'bad' (not 'more bad'); Telugu speakers learning comparatives by the regular '-er'/'more' pattern sometimes wrongly produce 'more bad' instead of 'worse'."),
    ("day72-medical-05", 5, "I think I might have a fever.", "నాకు జ్వరం వచ్చినట్టుంది అనిపిస్తోంది.",
     ["/f/ in 'fever'", "/aɪ/ in 'might'"], "fever", "an abnormally high body temperature, usually caused by illness", "జ్వరం",
     "'might have' expresses uncertainty about a current condition, softer than the more sure 'have'; Telugu speakers often skip the modal entirely and state a fact directly, sounding more certain than intended when describing symptoms to a doctor."),
]

DAY73_LESSONS = [
    ("day73-clarifydeep-01", 1, "What I mean is, we need to finish this before the deadline, not after.", "నా ఉద్దేశం ఏంటంటే, మనం ఇది గడువుకు ముందే పూర్తి చేయాలి, తర్వాత కాదు.",
     ["/iː/ vs /ɪ/ in 'mean'", "/d/ final in 'deadline'"], "deadline", "the latest time or date by which something must be done", "గడువు",
     "'What I mean is...' is used to rephrase or clarify an earlier statement; Telugu speakers often skip this filler and simply repeat the same sentence louder, which can sound abrupt in English."),
    ("day73-clarifydeep-02", 2, "In other words, the project got delayed because we didn't have enough funding.", "మరో మాటలో చెప్పాలంటే, తగినంత నిధులు లేకపోవడం వల్ల ప్రాజెక్ట్ ఆలస్యమైంది.",
     ["/ð/ in 'other'", "/f/ vs /p/ in 'funding'"], "funding", "money provided for a project or activity", "నిధులు",
     "'In other words' signals a simpler restatement of a complex idea; note that 'got delayed' needs an auxiliary — Telugu learners often drop it and say 'the project delayed.'"),
    ("day73-clarifydeep-03", 3, "To put it simply, we're spending more than we're earning.", "సూటిగా చెప్పాలంటే, మనం సంపాదించే దాని కంటే ఎక్కువ ఖర్చు పెడుతున్నాం.",
     ["/s/ cluster in 'simply'", "/ɜː/ in 'earning'"], "earning", "money you receive from work", "సంపాదన",
     "'To put it simply' introduces a plain-language summary of something complicated; the comparative 'more than we're earning' keeps the second 'we're', which Telugu speakers often drop, saying 'more than earning.'"),
    ("day73-clarifydeep-04", 4, "Let me rephrase that — what I'm trying to say is, I need more time to decide.", "దాన్ని మళ్ళీ చెప్తాను — నేను చెప్పాలనుకుంటున్నది ఏంటంటే, నిర్ణయం తీసుకోవడానికి నాకు ఇంకొంచెం సమయం కావాలి.",
     ["/r/ in 'rephrase'", "/tr/ cluster in 'trying'"], "rephrase", "to say something again in different words", "మళ్ళీ చెప్పడం",
     "'Let me rephrase that' is a polite self-correction marker used mid-conversation; Telugu speakers often restart the whole sentence instead without signaling the correction, which can confuse listeners."),
    ("day73-clarifydeep-05", 5, "So basically, what I'm saying is, we should test the product before we launch it.", "కాబట్టి సూక్ష్మంగా చెప్పాలంటే, మనం ఉత్పత్తిని విడుదల చేయడానికి ముందు దాన్ని పరీక్షించాలి.",
     ["/b/ in 'basically'", "/tʃ/ in 'launch'"], "launch", "to introduce a new product to the public", "విడుదల చేయడం",
     "'So basically...' signals a distilled summary after a complex explanation; after the connector 'before', present tense is used even for a future action, not 'before we will launch.'"),
]

DAY74_LESSONS = [
    ("day74-lesson-01", 1, "Once, a farmer lost all his crops, but he never gave up hope.", "ఒకసారి, ఒక రైతు తన పంటలన్నీ కోల్పోయాడు, కానీ అతను ఆశ వదులుకోలేదు.",
     ["/f/ in 'farmer'", "/h/ in 'hope'"], "crops", "plants grown for food or other use, harvested from farmland", "పంటలు",
     "Simple past tense ('lost', 'never gave up') narrates a completed story; Telugu speakers sometimes slip into present tense mid-story ('he loses'), which breaks the narrative flow in English."),
    ("day74-lesson-02", 2, "If he had given up that day, he would never have succeeded.", "ఆ రోజు అతను వదులుకుంటే, అతను ఎప్పటికీ విజయం సాధించి ఉండేవాడు కాదు.",
     ["/ʃ/ in 'succeeded'", "/v/ in 'given'"], "succeed", "to achieve a desired goal or result", "విజయం సాధించడం",
     "This is a third conditional ('If he had given up... he would never have succeeded') used to reflect on a past event that didn't happen; Telugu learners often use simple past instead of past perfect in the 'if' clause."),
    ("day74-lesson-03", 3, "The moral of the story is that patience always pays off.", "ఈ కథలోని నీతి ఏంటంటే, ఓర్పు ఎప్పుడూ ఫలిస్తుంది.",
     ["/m/ in 'moral'", "/eɪ/ in 'always'"], "moral", "a lesson about right behavior taught by a story", "నీతి",
     "'The moral of the story is that...' is a formal, fixed way to state the lesson from a narrative; the following clause keeps normal subject-before-verb word order, unlike a question."),
    ("day74-lesson-04", 4, "I would like to share a story that taught me an important lesson.", "నాకు ఒక ముఖ్యమైన పాఠం నేర్పిన కథను నేను మీతో పంచుకోవాలనుకుంటున్నాను.",
     ["/ʃ/ in 'share'", "/tɔː/ in 'taught'"], "lesson", "something learned from experience", "పాఠం",
     "'I would like to...' is the formal, polite way to introduce a statement, softer than 'I want to'; it is followed directly by an infinitive ('to share'), not a gerund."),
    ("day74-lesson-05", 5, "In other words, if we stay determined like that farmer, we too can overcome hard times.", "మరో మాటలో చెప్పాలంటే, ఆ రైతులాగే మనం స్థిరంగా ఉంటే, మనం కూడా కష్ట సమయాలను అధిగమించగలం.",
     ["/d/ in 'determined'", "/k/ in 'overcome'"], "determined", "having a firm decision to achieve something despite difficulty", "దృఢ సంకల్పంతో ఉన్న",
     "This combines the rephrasing phrase 'in other words' with a first conditional ('if we stay... we can overcome') to draw a general lesson from the story, a natural way English speakers close a narrative with its takeaway."),
]

DAY75_LESSONS = [
    ("day75-culture-01", 1, "In my hometown, we usually celebrate festivals with the whole extended family.", "మా ఊరిలో, మేము సాధారణంగా పండుగలను మొత్తం బంధువులతో కలిసి జరుపుకుంటాం.",
     ["/h/ in 'hometown'", "/f/ in 'festivals'"], "extended family", "family including relatives beyond parents and siblings, such as grandparents, uncles, aunts", "ఉమ్మడి కుటుంబం",
     "'In my hometown, we usually...' sets up a habitual comparison; the frequency adverb 'usually' goes before the main verb, a placement Telugu speakers often get backwards by analogy with Telugu word order."),
    ("day75-culture-02", 2, "Compared to city life, village traditions are followed much more strictly.", "నగర జీవితంతో పోలిస్తే, గ్రామ సంప్రదాయాలను చాలా కచ్చితంగా పాటిస్తారు.",
     ["/str/ cluster in 'strictly'", "/tr/ in 'traditions'"], "strictly", "in a way that is done exactly and carefully, without exception", "కచ్చితంగా",
     "'Compared to X, Y...' is a formal comparative opener; the comparative adverb 'more strictly' needs the intensifier 'much' before it, which Telugu learners often omit."),
    ("day75-culture-03", 3, "Unlike in the West, most weddings here last for several days.", "పాశ్చాత్య దేశాల్లో లాగా కాకుండా, ఇక్కడ చాలా వరకు పెళ్ళిళ్ళు చాలా రోజులు జరుగుతాయి.",
     ["/w/ vs /v/ in 'weddings'/'West'"], "wedding", "a marriage ceremony", "పెళ్లి",
     "'Unlike in X, Y...' contrasts two cultural practices; the preposition 'in' is required before the place name ('unlike in the West'), which Telugu speakers often omit."),
    ("day75-culture-04", 4, "The older generation tends to follow customs more closely than the younger one does.", "పెద్ద తరం వారు యువ తరం కంటే ఆచారాలను ఎక్కువగా పాటిస్తారు.",
     ["/dʒ/ in 'generation'", "/k/ in 'closely'"], "customs", "traditional practices of a community", "ఆచారాలు",
     "'X tends to... more than Y does' is a comparative pattern for general tendencies; the auxiliary 'does' at the end avoids repeating the whole verb, a placeholder Telugu has no direct equivalent for."),
    ("day75-culture-05", 5, "Where I come from, guests are always offered food the moment they arrive.", "నేను వచ్చిన ప్రాంతంలో, అతిథులు రాగానే వెంటనే వారికి తినడానికి ఏదైనా ఇస్తారు.",
     ["/g/ in 'guests'", "/ð/ in 'the'"], "guests", "people invited to visit or stay", "అతిథులు",
     "'Where I come from...' introduces a description of one's own culture; 'the moment they arrive' means 'as soon as' and is followed by present tense even for habitual meaning."),
]

DAY76_LESSONS = [
    ("day76-regret-01", 1, "I should have studied harder before the exam.", "పరీక్షకు ముందు నేను మరింత కష్టపడి చదవాల్సింది.",
     ["/ʃ/ in 'should'", "/h/ in 'harder'"], "exam", "a formal test of knowledge or skill", "పరీక్ష",
     "'should have + past participle' expresses regret about a past action that didn't happen; Telugu speakers often say 'I should study' in present tense, losing the past-regret meaning entirely."),
    ("day76-regret-02", 2, "I wish I had told her the truth from the beginning.", "నేను మొదటి నుండే ఆమెకు నిజం చెప్పి ఉంటే బాగుండేది.",
     ["/w/ in 'wish'", "/tr/ in 'truth'"], "truth", "the actual facts of a situation", "నిజం",
     "'I wish I had + past participle' expresses regret about something in the past that cannot be changed; Telugu learners often say 'I wish I told her' in simple past, but past perfect is required for past wishes."),
    ("day76-regret-03", 3, "We shouldn't have left so late; now we're stuck in traffic.", "మేము అంత ఆలస్యంగా బయలుదేరకుండా ఉండాల్సింది; ఇప్పుడు ట్రాఫిక్‌లో ఇరుక్కుపోయాం.",
     ["/ʃ/ in 'shouldn't'", "/st/ cluster in 'stuck'"], "stuck", "unable to move or make progress", "ఇరుక్కుపోవడం",
     "'shouldn't have + past participle' criticizes a past decision that turned out badly; the following clause stays in present tense to describe the current result of that past mistake."),
    ("day76-regret-04", 4, "Looking back, I regret not spending more time with my grandparents.", "వెనక్కి తిరిగి చూస్తే, నా తాతయ్య నానమ్మలతో ఎక్కువ సమయం గడపకపోవడం నాకు బాధగా ఉంది.",
     ["/r/ in 'regret'", "/gr/ cluster in 'grandparents'"], "regret", "a feeling of sadness about something one did or failed to do", "పశ్చాత్తాపం",
     "'regret + not + verb-ing' expresses sorrow over something not done; Telugu speakers often add an infinitive ('regret to not spend') by analogy with other verbs, but 'regret' here takes a gerund."),
    ("day76-regret-05", 5, "If only I had asked for help sooner, things wouldn't have gotten so bad.", "నేను ముందుగానే సహాయం అడిగి ఉంటే, పరిస్థితులు ఇంత దారుణంగా మారేవి కావు.",
     ["/f/ in 'if'", "/h/ in 'help'"], "sooner", "earlier than a particular time", "ముందుగానే",
     "'If only I had...' is a strong, emotional way to express regret, more intense than 'I wish'; both clauses need past perfect / 'would have + past participle', a structure with no direct one-to-one match in Telugu conditionals."),
]

DAY77_LESSONS = [
    ("day77-feedback-01", 1, "One thing you could try is explaining your ideas a bit more slowly.", "మీరు చేయగలిగే ఒక పని ఏంటంటే, మీ ఆలోచనలను కొంచెం నెమ్మదిగా వివరించడం.",
     ["/θ/ in 'thing'", "/tr/ in 'try'"], "explaining", "making something clear by describing it in detail", "వివరించడం",
     "'One thing you could try is + verb-ing' softens a suggestion so it doesn't sound like direct criticism; Telugu speakers often give feedback as a blunt imperative ('explain slowly'), which can sound harsher in English."),
    ("day77-feedback-02", 2, "Thanks for pointing that out — I'll fix it right away.", "దాన్ని గుర్తు చేసినందుకు ధన్యవాదాలు — నేను వెంటనే సరిచేస్తాను.",
     ["/θ/ in 'thanks'", "/r/ in 'right'"], "pointing out", "drawing attention to a fact or mistake", "గుర్తు చేయడం",
     "'Thanks for + verb-ing' is used to graciously accept feedback rather than getting defensive; the preposition 'for' must be followed by a gerund, so 'thanks for point out' is incorrect."),
    ("day77-feedback-03", 3, "It might help if you double-checked the numbers before sending the report.", "రిపోర్ట్ పంపే ముందు మీరు నంబర్లను ఒకసారి మళ్ళీ చెక్ చేస్తే బాగుంటుంది.",
     ["/tʃ/ in 'checked'", "/r/ in 'report'"], "double-check", "to check something again to make sure it is correct", "మళ్ళీ సరిచూసుకోవడం",
     "'It might help if...' is an indirect, softened way of suggesting improvement; using 'might' instead of 'will' lowers the certainty and sounds less like a command, a nuance often lost when Telugu speakers translate advice directly."),
    ("day77-feedback-04", 4, "I really appreciate the effort, though I think the introduction could be a little clearer.", "మీ కృషిని నేను నిజంగా అభినందిస్తున్నాను, అయితే పరిచయం కొంచెం స్పష్టంగా ఉంటే బాగుంటుందని అనుకుంటున్నాను.",
     ["/θ/ in 'though'", "/kl/ cluster in 'clearer'"], "appreciate", "to recognize the value of something and be grateful for it", "అభినందించడం",
     "Praising first, then softening criticism with 'though I think...' is a common feedback structure in English; 'could be' (not 'should be' or 'must be') keeps the suggestion gentle rather than forceful."),
    ("day77-feedback-05", 5, "Would you mind if I gave you some feedback on your presentation?", "మీ ప్రజెంటేషన్ గురించి నేను కొంచెం ఫీడ్‌బ్యాక్ ఇస్తే పర్వాలేదా?",
     ["/w/ vs /v/ in 'Would'/'presentation'", "/d/ final in 'mind'"], "presentation", "a talk in which something is formally shown or explained to an audience", "ప్రజెంటేషన్",
     "'Would you mind if I + past tense verb...?' is a very polite way to ask permission before giving feedback; the past tense ('gave') is used here for politeness, not to refer to past time, a subtlety absent from Telugu tense marking."),
]

DAY78_LESSONS = [
    ("day78-smalltalk-01", 1, "By the way, did you hear about the new mall opening downtown?", "ఇంతకీ, డౌన్‌టౌన్‌లో కొత్త మాల్ తెరుస్తున్నారని మీకు తెలుసా?",
     ["/w/ in 'way'", "/h/ in 'hear'"], "downtown", "the central business area of a city", "నగర మధ్యభాగం",
     "'By the way' smoothly shifts the conversation to a new, often unrelated topic; it's typically followed directly by a question, unlike Telugu where a topic shift often needs an explicit phrase like 'సరే, ఇంకో విషయం.'"),
    ("day78-smalltalk-02", 2, "That reminds me — I still need to return your book.", "అది గుర్తుకొచ్చింది — నేను ఇంకా మీ పుస్తకం తిరిగివ్వాలి.",
     ["/r/ in 'reminds'", "/iː/ in 'reminds'"], "return", "to give something back to its owner", "తిరిగి ఇవ్వడం",
     "'That reminds me' links back to something just mentioned before pivoting to a related topic; 'remind' is used here as 'reminds me' with no extra preposition, not 'reminds to me.'"),
    ("day78-smalltalk-03", 3, "Speaking of food, have you tried that new restaurant near the office?", "ఆహారం గురించి చెప్పాలంటే, ఆఫీసు దగ్గర ఉన్న ఆ కొత్త రెస్టారెంట్ ప్రయత్నించారా?",
     ["/f/ in 'food'", "/r/ in 'restaurant'"], "restaurant", "a place where meals are served to paying customers", "రెస్టారెంట్",
     "'Speaking of X...' connects the new topic to a word or idea just mentioned, making the shift feel natural rather than abrupt; it is followed by a comma and then a full new sentence."),
    ("day78-smalltalk-04", 4, "Anyway, how's your sister doing these days?", "సరే, మీ చెల్లి ఈ మధ్య ఎలా ఉంది?",
     ["/eɪ/ in 'anyway'", "/d/ in 'days'"], "anyway", "used to change the subject or return to an earlier point", "సరే",
     "'Anyway' is used to close one topic and open another, often after a pause; 'these days' means 'currently' and pairs with present continuous ('is doing'), which Telugu speakers sometimes replace with simple present."),
    ("day78-smalltalk-05", 5, "Before I forget, can I ask you something unrelated?", "మర్చిపోకముందే, నేను మీకు వేరే విషయం గురించి అడగొచ్చా?",
     ["/f/ in 'forget'", "/r/ in 'unrelated'"], "unrelated", "not connected to the current topic", "సంబంధం లేని",
     "'Before I forget...' politely signals an abrupt topic change, often for something urgent; 'can I ask you something' uses the base verb after 'can', while Telugu speakers might mistakenly add 'to.'"),
]

DAY79_LESSONS = [
    ("day79-selfimprove-01", 1, "I've been trying to wake up earlier every day.", "నేను ప్రతిరోజూ ముందుగా లేవడానికి ప్రయత్నిస్తున్నాను.",
     ["/aɪ/ in 'trying'", "/w/ in 'wake'"], "trying to", "making an effort to do something", "ప్రయత్నించడం",
     "'I've been trying to' + base verb describes an ongoing effort that started in the past and continues now. Telugu speakers often drop the auxiliary 'have' and just say 'I trying', since Telugu marks continuity with a verb suffix (-తున్నాను) rather than a separate auxiliary."),
    ("day79-selfimprove-02", 2, "I've been working on my English pronunciation for a few months.", "నేను కొన్ని నెలలుగా నా ఇంగ్లీష్ ఉచ్చారణ మీద కృషి చేస్తున్నాను.",
     ["/ʃ/ in 'pronunciation'", "/w/ in 'work'"], "work on", "to make efforts to improve something", "మెరుగుపరచడానికి కృషి చేయడం",
     "Present perfect continuous with a duration phrase ('for a few months') emphasizes an effort that is still ongoing. Telugu learners often use simple present instead ('I work on'), losing the sense of continued duration up to now."),
    ("day79-selfimprove-03", 3, "My goal is to finish this course by December.", "నా లక్ష్యం డిసెంబర్ నాటికి ఈ కోర్సు పూర్తి చేయడం.",
     ["/g/ in 'goal'", "final /l/ in 'goal'"], "goal", "something you aim to achieve", "లక్ష్యం",
     "'My goal is to' + base verb states an intention or objective. 'By' + a deadline (not 'until') marks the point something must be completed — a distinction Telugu speakers often blur since Telugu doesn't separate these two prepositions as clearly."),
    ("day79-selfimprove-04", 4, "I haven't been sleeping well, so I'm trying to fix my routine.", "నేను సరిగ్గా నిద్రపోవడం లేదు, అందుకే నా దినచర్యను సరిదిద్దుకోవడానికి ప్రయత్నిస్తున్నాను.",
     ["/sl/ cluster in 'sleeping'", "/f/ in 'fix'"], "routine", "a fixed, regular way of doing things", "దినచర్య",
     "Negative present perfect continuous ('haven't been' + verb-ing) shows a problem that has continued up to now. Telugu speakers often say 'I am not sleeping well' instead, which loses the sense that this has been happening for a while."),
    ("day79-selfimprove-05", 5, "I've made a lot of progress since I started practicing every day.", "నేను ప్రతిరోజూ సాధన చేయడం మొదలుపెట్టినప్పటి నుండి చాలా పురోగతి సాధించాను.",
     ["/pr/ cluster in 'progress'", "/s/ in 'since'"], "progress", "forward movement toward a goal", "పురోగతి",
     "'Since' + a past starting point, combined with present perfect ('I've made'), links that past event to a present result. Telugu speakers often use simple past throughout ('I made progress when I started'), which loses the connection to now."),
]

DAY80_LESSONS = [
    ("day80-solution-01", 1, "The issue is that the app keeps crashing when I open it.", "సమస్య ఏమిటంటే, నేను యాప్ తెరిచినప్పుడు అది పదే పదే క్రాష్ అవుతోంది.",
     ["/ʃ/ in 'issue'", "/kr/ cluster in 'crashing'"], "issue", "a problem or difficulty", "సమస్య",
     "'The issue is that' + clause is a formal way to state a problem clearly before offering a solution. Telugu speakers often skip 'that' or state the problem directly without this framing phrase, which can sound abrupt in professional English."),
    ("day80-solution-02", 2, "I suggest we reschedule the meeting to next week.", "మనం సమావేశాన్ని వచ్చే వారానికి మార్చాలని నేను సూచిస్తున్నాను.",
     ["/dʒ/ in 'suggest'", "/ʒ/ in 'reschedule'"], "suggest", "to propose an idea or plan", "సూచించడం",
     "'suggest + subject + base verb' (no 'to') is the correct pattern. Telugu speakers commonly say 'I suggest to reschedule' by analogy with 'want to', which is a frequent English error."),
    ("day80-solution-03", 3, "One way to solve this is to double-check the numbers before sending.", "దీన్ని పరిష్కరించడానికి ఒక మార్గం ఏమిటంటే, పంపే ముందు అంకెలను మళ్ళీ సరిచూసుకోవడం.",
     ["/s/ in 'solve'", "/tʃ/ in 'double-check'"], "double-check", "to check something again to make sure it's correct", "మళ్ళీ సరిచూసుకోవడం",
     "'One way to solve this is to' + base verb structures a solution clearly, with 'to' required before both verbs. Telugu speakers often list solutions without this connector, jumping straight to advice, which sounds less organized in professional contexts."),
    ("day80-solution-04", 4, "If we fix the login page first, the rest should be easier.", "మనం ముందు లాగిన్ పేజీని సరిచేస్తే, మిగతాది సులభంగా ఉంటుంది.",
     ["/f/ in 'fix'", "/iː/ in 'easier'"], "login", "the process or page for entering an account", "లాగిన్ (ఖాతాలోకి ప్రవేశించడం)",
     "This is a real conditional ('If' + present simple, ... 'should' + base verb) used for practical predictions. Telugu speakers often use future tense in the if-clause ('If we will fix'), which is incorrect in English conditionals."),
    ("day80-solution-05", 5, "I recommend that we test it again before we launch.", "మనం లాంచ్ చేయడానికి ముందు దాన్ని మళ్ళీ పరీక్షించాలని నేను సిఫారసు చేస్తున్నాను.",
     ["/r/ in 'recommend'", "/l/ in 'launch'"], "recommend", "to formally suggest something as a good idea", "సిఫారసు చేయడం",
     "'recommend that + subject + base verb' uses this subjunctive-style base form in formal suggestions. Telugu speakers often add 'should' unnecessarily or use present tense with '-s' ('recommend that he tests'), missing this formal structure."),
]

DAY81_LESSONS = [
    ("day81-encouragement-01", 1, "Don't worry about the mistake — everyone messes up sometimes.", "ఆ తప్పు గురించి బాధపడకు — అందరూ ఒక్కోసారి పొరపాట్లు చేస్తారే.",
     ["/w/ in 'worry'", "/m/ in 'mistake'"], "mess up", "to make a mistake or do something badly", "పొరపాటు చేయడం",
     "'Don't worry about' + noun/-ing is used to comfort someone. Telugu speakers often translate literally as 'don't take tension about' — a calque — instead of using this natural English phrase."),
    ("day81-encouragement-02", 2, "You've been working really hard, and it shows.", "నువ్వు చాలా కష్టపడి పనిచేస్తున్నావు, అది కనిపిస్తూనే ఉంది.",
     ["/h/ in 'hard'", "/ʃ/ in 'shows'"], "it shows", "it is visible or noticeable", "అది స్పష్టంగా కనిపిస్తుంది",
     "This reuses the present perfect continuous ('You've been working') from self-improvement language, now directed at someone else to acknowledge their effort — a warm, encouraging use of the same structure."),
    ("day81-encouragement-03", 3, "I know you regret how the interview went, but you'll do better next time.", "ఇంటర్వ్యూ ఎలా జరిగిందో అనుకుని నువ్వు బాధపడుతున్నావని నాకు తెలుసు, కానీ వచ్చే సారి నువ్వు బాగా చేస్తావు.",
     ["/r/ in 'regret'", "/v/ in 'interview'"], "regret", "to feel sorry about something that happened", "పశ్చాత్తాపపడటం",
     "This recombines regret language ('regret how X went') with future encouragement ('you'll do better next time'). Telugu speakers often drop 'will' and say 'you do better next time', losing the future promise."),
    ("day81-encouragement-04", 4, "Thanks for the feedback — I'll try to fix that next time.", "ఫీడ్‌బ్యాక్ ఇచ్చినందుకు ధన్యవాదాలు — వచ్చే సారి దాన్ని సరిదిద్దుకోవడానికి ప్రయత్నిస్తాను.",
     ["/θ/ in 'thanks'", "/f/ in 'feedback'"], "feedback", "comments about how well something was done, used to improve it", "అభిప్రాయం / సూచనలు",
     "This reuses feedback-topic vocabulary in a response pattern ('Thanks for X — I'll try to Y'). Telugu speakers sometimes omit 'for' after 'thanks', saying 'thanks the feedback'."),
    ("day81-encouragement-05", 5, "You've already come a long way, so don't give up now.", "నువ్వు ఇప్పటికే చాలా దూరం వచ్చావు, కాబట్టి ఇప్పుడు వదిలేయకు.",
     ["/dʒ/ in 'give'", "/l/ in 'long'"], "give up", "to stop trying", "వదిలేయడం, ఆపేయడం",
     "'You've already' + past participle (present perfect with 'already') emphasizes achievement so far as encouragement. Telugu speakers often use simple past instead ('You came a long way already'), which loses the connection to the present moment."),
]

DAY82_LESSONS = [
    ("day82-videocalls-01", 1, "Can we reschedule the call to tomorrow afternoon?", "మనం కాల్‌ని రేపు మధ్యాహ్నానికి మార్చవచ్చా?",
     ["/ʃ/ in 'reschedule'", "/f/ in 'afternoon'"], "reschedule", "to change the planned time of something", "సమయాన్ని మార్చడం",
     "'Can we' + base verb + 'to' + time politely proposes a new time. Telugu speakers often say 'shift the call' or use 'at' instead of 'to' before the new time, mixing up prepositions of time."),
    ("day82-videocalls-02", 2, "I'm having connection issues — can you hear me now?", "నాకు కనెక్షన్ సమస్య వస్తోంది — ఇప్పుడు మీకు నా మాట వినిపిస్తోందా?",
     ["/kʃ/ in 'connection'", "/h/ in 'hear'"], "connection", "the link that lets devices communicate, e.g. the internet", "అనుసంధానం",
     "'I'm having' + noun issues (present continuous) describes a temporary technical problem happening right now. Telugu speakers often use simple present instead ('I have connection issue'), missing the sense that it's happening at this exact moment."),
    ("day82-videocalls-03", 3, "Let's mute ourselves when we're not speaking.", "మనం మాట్లాడనప్పుడు మైక్ మ్యూట్ చేసుకుందాం.",
     ["/m/ in 'mute'", "/spiː/ in 'speaking'"], "mute", "to turn off the microphone or sound", "మ్యూట్ చేయడం (శబ్దం ఆపడం)",
     "'Let's' + base verb makes a group suggestion. The reflexive 'ourselves' after 'mute' is often dropped by Telugu speakers, though English requires it here for the action to sound natural."),
    ("day82-videocalls-04", 4, "Could you share your screen so I can see the document?", "మీరు మీ స్క్రీన్‌ను షేర్ చేయగలరా, నేను డాక్యుమెంట్ చూడగలిగేలా?",
     ["/ʃ/ in 'share'", "/dʒ/ in 'document'"], "share screen", "to show your computer screen to others in a call", "స్క్రీన్ షేర్ చేయడం",
     "'Could you' + base verb, so (that) + subject + 'can' + base verb links a polite request with its purpose. Telugu speakers often drop 'so' and use two separate sentences, losing the cause-effect connection."),
    ("day82-videocalls-05", 5, "I'll send you the meeting link five minutes before we start.", "మనం మొదలుపెట్టడానికి ఐదు నిమిషాల ముందు నేను మీకు మీటింగ్ లింక్ పంపిస్తాను.",
     ["/f/ in 'five'", "/l/ in 'link'"], "link", "a clickable address that opens a webpage or call", "లింక్",
     "'I'll' + base verb ... 'before' + subject + present simple uses present tense in the time clause even though it refers to the future. Telugu speakers often break this rule by saying 'before we will start', a direct calque from Telugu future marking."),
]

DAY83_LESSONS = [
    ("day83-finance-01", 1, "If I save five thousand rupees every month, I'll be able to buy a bike by next year.", "నేను ప్రతి నెలా ఐదు వేల రూపాయలు దాచుకుంటే, వచ్చే సంవత్సరానికి బైక్ కొనగలుగుతాను.",
     ["/s/ in 'save'", "/b/ in 'buy'"], "be able to", "to have the ability or opportunity to do something", "చేయగలగడం",
     "First conditional ('If' + present simple, ... 'will' + base verb) is used for realistic future plans. Telugu speakers often use 'will' in both clauses ('If I will save'), which is incorrect in standard English conditionals."),
    ("day83-finance-02", 2, "I'm planning to set aside some money for emergencies.", "నేను అత్యవసర పరిస్థితుల కోసం కొంత డబ్బు దాచిపెట్టాలని అనుకుంటున్నాను.",
     ["/pl/ cluster in 'planning'", "/dʒ/ in 'emergencies'"], "set aside", "to save something for a specific future purpose", "ప్రత్యేకంగా దాచిపెట్టడం",
     "'be planning to' + base verb expresses a future intention already decided. Telugu speakers often say 'I plan that I will set aside', adding an unnecessary clause instead of this simpler infinitive structure."),
    ("day83-finance-03", 3, "If I invest this money wisely, it will grow over time.", "నేను ఈ డబ్బును తెలివిగా పెట్టుబడి పెడితే, అది కాలక్రమేణా పెరుగుతుంది.",
     ["/v/ in 'invest'", "/aɪ/ in 'wisely'"], "invest", "to put money into something expecting it to grow in value", "పెట్టుబడి పెట్టడం",
     "This reinforces the first conditional with 'wisely' as an adverb of manner placed after the object. Telugu speakers often place adverbs incorrectly, saying 'invest wisely this money' instead of after the object."),
    ("day83-finance-04", 4, "Once I pay off this loan, I'll have more savings every month.", "ఈ లోన్ తీర్చేసిన తర్వాత, నాకు ప్రతి నెలా ఎక్కువ మిగులు ఉంటుంది.",
     ["/l/ in 'loan'", "/v/ in 'savings'"], "pay off", "to completely repay a debt", "పూర్తిగా తీర్చేయడం",
     "'Once' + present simple, ... 'will' + base verb marks a future condition tied to completing an action first. Telugu speakers often use 'after' with future tense in both clauses, which sounds unnatural compared to this native pattern."),
    ("day83-finance-05", 5, "If we cut down on eating out, we'll save a lot by the end of the year.", "మనం బయట తినడం తగ్గిస్తే, సంవత్సరాంతానికి చాలా డబ్బు మిగులుతుంది.",
     ["/k/ in 'cut'", "/aʊ/ in 'out'"], "cut down on", "to reduce the amount of something", "తగ్గించుకోవడం",
     "The phrasal verb 'cut down on' + noun/-ing, combined with the first conditional, shows cause and result for financial planning. Telugu speakers often say 'cut the eating out', omitting 'down on', which changes the meaning."),
]

DAY84_LESSONS = [
    ("day84-unexpected-01", 1, "I'm sorry for the delay — my previous meeting ran longer than expected.", "ఆలస్యానికి క్షమించండి — నా మునుపటి మీటింగ్ అనుకున్న దానికంటే ఎక్కువసేపు జరిగింది.",
     ["/d/ in 'delay'", "/v/ in 'previous'"], "delay", "a period of time when something happens later than planned", "ఆలస్యం",
     "'I'm sorry for' + noun apologizes for a situation. Telugu speakers often say 'I'm sorry for late', using an adjective instead of a noun, which is grammatically incorrect after 'for'."),
    ("day84-unexpected-02", 2, "I should have told you earlier, and I apologize for the confusion.", "నేను ముందుగానే నీకు చెప్పి ఉండాల్సింది, గందరగోళానికి క్షమాపణ కోరుతున్నాను.",
     ["/ʃ/ in 'should'", "/kən/ in 'confusion'"], "confusion", "a state of not understanding what is happening", "గందరగోళం",
     "'should have' + past participle expresses regret about a past action that didn't happen. Telugu speakers often say 'I should told you', dropping 'have', which is a very common error with this structure."),
    ("day84-unexpected-03", 3, "Something came up suddenly, so I couldn't make it on time.", "అకస్మాత్తుగా ఏదో పని వచ్చిపడింది, అందుకే నేను సమయానికి రాలేకపోయాను.",
     ["/s/ in 'suddenly'", "/tʃ/ in 'couldn't'"], "come up", "to happen unexpectedly", "అనుకోకుండా జరగడం",
     "The phrasal verb 'something came up' is the natural way to explain an unexpected obstacle. Telugu speakers often over-explain literally ('suddenly one work happened') instead of using this idiomatic phrase."),
    ("day84-unexpected-04", 4, "It won't happen again — I'll double-check everything from now on.", "ఇలా మళ్ళీ జరగదు — ఇప్పటి నుండి నేను అన్నీ మళ్ళీ సరిచూసుకుంటాను.",
     ["/w/ in 'won't'", "/dʒ/ in 'again'"], "from now on", "starting from this moment onward", "ఇప్పటి నుండి",
     "'won't' (will not) + base verb promises future behavior change after a mistake. Telugu speakers sometimes confuse 'won't' with 'don't', saying 'It don't happen again', mixing present and future forms."),
    ("day84-unexpected-05", 5, "I made a mistake with the dates, and I want to correct it right away.", "నేను తేదీలలో పొరపాటు చేశాను, దాన్ని వెంటనే సరిదిద్దాలనుకుంటున్నాను.",
     ["/m/ in 'mistake'", "/r/ in 'right away'"], "right away", "immediately, without delay", "వెంటనే",
     "'made a mistake with' + noun is the natural collocation for admitting an error. Telugu speakers often say 'did a mistake' instead of 'made a mistake', a common verb-collocation error."),
]

DAY85_LESSONS = [
    ("day85-socialtopics-01", 1, "Some people think social media is harmful, but I feel it depends on how you use it.", "కొంతమంది సోషల్ మీడియా హానికరం అని అనుకుంటారు, కానీ అది మీరు ఎలా వాడతారు అనే దాని మీద ఆధారపడి ఉంటుందని నేను భావిస్తాను.",
     ["/θ/ in 'think'", "/z/ in 'use' (verb)"], "harmful", "causing damage or bad effects", "హానికరమైన",
     "'Some people think X, but I feel Y' is a hedging frame that presents an opinion politely without sounding like a blunt personal claim. Telugu speakers often translate opinions directly with 'నా అభిప్రాయం లో' without this softening contrast structure, which can sound too assertive in English."),
    ("day85-socialtopics-02", 2, "A lot of people believe joint families are better, though personally, I think it depends on the situation.", "చాలామంది ఉమ్మడి కుటుంబాలు మంచివని నమ్ముతారు, అయితే వ్యక్తిగతంగా, అది పరిస్థితిని బట్టి ఉంటుందని నేను అనుకుంటున్నాను.",
     ["/v/ vs /w/ in 'believe'", "/dʒ/ in 'joint'"], "personally", "speaking from one's own viewpoint", "వ్యక్తిగతంగా",
     "'though' can join two contrasting ideas in a single sentence (X, though Y), softer than 'but'. Telugu speakers often start a completely new sentence for the contrast instead of linking it with 'though', producing choppier speech than one flowing hedged opinion."),
    ("day85-socialtopics-03", 3, "I could be wrong, but I think students should learn practical skills, not just theory.", "నేను తప్పు కావచ్చు, కానీ విద్యార్థులు కేవలం సిద్ధాంతమే కాకుండా ఆచరణాత్మక నైపుణ్యాలు నేర్చుకోవాలని నేను అనుకుంటున్నాను.",
     ["/r/ in 'wrong'", "/θ/ in 'theory'"], "practical", "relating to actual doing or use rather than theory", "ఆచరణాత్మక",
     "'I could be wrong, but...' is a hedge that shows humility before stating an opinion — very common in polite spoken English. Telugu speakers, translating directly, tend to state 'నేను అనుకుంటున్నాను' (I think) without any softener first, which can sound overly confident."),
    ("day85-socialtopics-04", 4, "In my opinion, both parents can work and still raise their children well, though some people disagree.", "నా అభిప్రాయంలో, తల్లిదండ్రులిద్దరూ పని చేస్తూ కూడా పిల్లలను బాగా పెంచగలరు, అయితే కొంతమంది దీనితో ఏకీభవించరు.",
     ["/nj/ cluster in 'opinion'", "/r/ in 'raise'"], "disagree", "to have a different opinion", "ఏకీభవించకపోవడం",
     "Concluding a hedged opinion with 'though some people disagree' acknowledges the opposite view without conceding it — a hallmark of respectful debate. Telugu speakers often omit this closing acknowledgment, which can make an opinion sound like it dismisses other views entirely."),
    ("day85-socialtopics-05", 5, "Some say arranged marriages work better, but honestly, I feel it really depends on the couple.", "కొందరు పెద్దలు కుదిర్చిన పెళ్లిళ్లే మంచివని అంటారు, కానీ నిజం చెప్పాలంటే, అది ఆ జంటను బట్టి ఉంటుందని నేను అనుకుంటాను.",
     ["/ɑːr/ in 'arranged'", "/ʌ/ in 'couple'"], "honestly", "speaking truthfully, used to add sincerity", "నిజాయితీగా చెప్పాలంటే",
     "'Honestly' inserted mid-sentence signals sincerity before a personal opinion, a common spoken-English filler-hedge. Telugu speakers often place the equivalent 'నిజం చెప్పాలంటే' only at the very start of a sentence, so moving a similar hedge word mid-clause in English needs practice."),
]

DAY86_LESSONS = [
    ("day86-traveladvanced-01", 1, "I'd like to change my booking to a later flight, if that's possible.", "వీలైతే, నా బుకింగ్‌ను తర్వాతి విమానానికి మార్చాలనుకుంటున్నాను.",
     ["/tʃ/ in 'change'", "/f/ in 'flight'"], "booking", "a reservation made in advance", "బుకింగ్ / ముందస్తు రిజర్వేషన్",
     "'I'd like to...' is a polite way to state a request, softer than 'I want'; adding 'if that's possible' at the end further softens it. Telugu speakers often use direct imperative-style requests translated literally, which can sound blunt or demanding in English."),
    ("day86-traveladvanced-02", 2, "Could you tell me if there's a fee for cancelling this reservation?", "ఈ రిజర్వేషన్ రద్దు చేసుకుంటే ఏదైనా ఫీజు ఉంటుందా అని చెప్పగలరా?",
     ["/f/ in 'fee'", "/ʒ/ in 'reservation'"], "cancel", "to officially stop or call off a booking or plan", "రద్దు చేయడం",
     "'Could you tell me if...' embeds a yes/no question inside a polite request — the embedded clause keeps normal word order ('there's a fee'), not question order ('is there a fee'). Telugu speakers learning this pattern often mistakenly invert the embedded clause the way a direct question would be inverted."),
    ("day86-traveladvanced-03", 3, "I booked a room for two nights, but I need to extend it by one more night.", "నేను రెండు రాత్రులకు గది బుక్ చేశాను, కానీ దాన్ని ఒక రాత్రి పొడిగించాలి.",
     ["/nd/ cluster in 'extend'", "/ts/ cluster in 'nights'"], "extend", "to make something last longer", "పొడిగించడం",
     "Past simple ('I booked') combines with a present need ('I need to extend') to describe a completed action with an ongoing consequence — a common real-world pattern. Telugu speakers sometimes keep both verbs in the same tense, translating literally, instead of shifting tense to match the timeline."),
    ("day86-traveladvanced-04", 4, "Is it possible to get a refund since my flight got cancelled?", "నా విమానం రద్దు అయినందున, రీఫండ్ పొందడం సాధ్యమేనా?",
     ["/r/ in 'refund'", "/s/ vs /ʃ/ in 'possible'"], "refund", "money given back for a cancelled service or purchase", "వాపసు డబ్బు",
     "'since' here means 'because', linking a reason (flight cancelled) to a request (refund) inside one polite question. Telugu speakers often use 'because' only, or split this into two separate sentences, missing the smoother single-sentence connector spoken English favors."),
    ("day86-traveladvanced-05", 5, "I'd like to switch my seat to one near the window, if any are available.", "వీలైతే, నా సీటును కిటికీ దగ్గరిదానికి మార్చాలనుకుంటున్నాను.",
     ["/w/ in 'window'", "/v/ in 'available'"], "available", "able to be used or obtained", "అందుబాటులో ఉన్న",
     "The conditional tag 'if any are available' softens the request and shows flexibility — a polite structure Telugu speakers often skip, making requests sound like firm demands rather than open requests."),
]

DAY87_LESSONS = [
    ("day87-mentor-01", 1, "What I'd suggest is that you practice speaking a little every single day.", "నేను సూచించేదేమిటంటే, మీరు ప్రతిరోజూ కొంచెం మాట్లాడటం సాధన చేయాలి.",
     ["/dʒ/ in 'suggest'", "/v/ in 'every'"], "suggest", "to put forward an idea or recommendation", "సూచించడం",
     "'What I'd suggest is that...' is a cleft structure that puts emphasis on the advice being given, softer and more thoughtful-sounding than a direct command. Telugu speakers often give advice with a bare imperative ('Practice daily') translated straight from Telugu, missing this gentler framing."),
    ("day87-mentor-02", 2, "You might want to start with small goals before taking on bigger ones.", "పెద్ద లక్ష్యాలు తీసుకునే ముందు, చిన్న లక్ష్యాలతో మొదలుపెట్టడం మంచిది.",
     ["/aɪ/ in 'might'", "/g/ in 'goals'"], "goal", "something a person aims to achieve", "లక్ష్యం",
     "'You might want to...' is an indirect, gentle suggestion — much softer than 'you should', useful when giving advice to someone senior or unfamiliar. Telugu speakers tend to use 'should' for all advice, missing this softer register available in English."),
    ("day87-mentor-03", 3, "If I were mentoring you, I'd tell you to ask more questions in meetings.", "నేను నిన్ను మార్గనిర్దేశం చేస్తుంటే, మీటింగుల్లో ఎక్కువ ప్రశ్నలు అడగమని చెప్తాను.",
     ["/m/ vs /n/ clarity in 'mentoring'", "/ŋ/ in 'meetings'"], "mentor", "an experienced person who guides someone less experienced", "మార్గదర్శి / గురువు",
     "'If I were mentoring you, I'd tell you to...' uses a hypothetical conditional to give indirect advice gently, distancing it from a direct command. This 'If I were you' style conditional is often skipped by Telugu speakers, who give advice directly without the hypothetical softening."),
    ("day87-mentor-04", 4, "One thing that really helped me was writing down what I learned each week.", "నాకు నిజంగా ఉపయోగపడిన ఒక విషయం ఏమిటంటే, ప్రతివారం నేను నేర్చుకున్నది రాసుకోవడం.",
     ["/r/ in 'really'", "/w/ in 'writing'"], "helped", "past tense of help, gave assistance or benefit", "సహాయపడింది",
     "Sharing personal experience ('One thing that really helped me was...') before giving advice makes guidance feel earned rather than preachy — a natural mentoring technique. Telugu speakers often jump straight to instructions without this experience-based lead-in."),
    ("day87-mentor-05", 5, "You don't have to get everything right immediately — what matters is that you keep trying.", "మీరు అన్నీ వెంటనే సరిగ్గా చేయాల్సిన అవసరం లేదు — ముఖ్యమైనది మీరు ప్రయత్నిస్తూ ఉండటం.",
     ["/h/ in 'have'", "/tr/ cluster in 'trying'"], "immediately", "right away, without delay", "వెంటనే",
     "'don't have to' means something is not necessary (different from 'must not', which forbids it) — a distinction Telugu speakers frequently confuse, since Telugu modal expressions for obligation don't map cleanly onto this necessity/prohibition split."),
]

DAY88_LESSONS = [
    ("day88-friend-01", 1, "I know something unexpected happened, but I think you handled it really well.", "ఏదో ఊహించని విషయం జరిగిందని నాకు తెలుసు, కానీ నువ్వు దాన్ని చాలా బాగా డీల్ చేశావని నేను అనుకుంటున్నాను.",
     ["/ʌ/ in 'unexpected'", "/h/ in 'handled'"], "unexpected", "not expected or anticipated", "ఊహించని",
     "This revisits the hedged-opinion frame ('but I think...') from social-topics practice, now applied to comforting a friend after an unexpected event — the same softening structure works in personal, not just abstract, conversations."),
    ("day88-friend-02", 2, "What I'd suggest is that you talk to her honestly about how you feel.", "నేను సూచించేదేమిటంటే, నువ్వు నీ భావాలను గురించి ఆమెతో నిజాయితీగా మాట్లాడాలి.",
     ["/h/ in 'honestly'", "/f/ in 'feel'"], "honestly", "in a truthful, sincere way", "నిజాయితీగా",
     "Reusing the mentoring frame 'What I'd suggest is that...' shows this gentle-advice structure works equally well between close friends, not only in formal guidance settings."),
    ("day88-friend-03", 3, "You don't have to solve everything today — just take it one step at a time.", "నువ్వు అన్నీ ఈరోజే పరిష్కరించాల్సిన అవసరం లేదు — ఒక్కో అడుగు వేసుకుంటూ వెళ్ళు.",
     ["/v/ in 'solve'", "/st/ cluster in 'step'"], "solve", "to find an answer to a problem", "పరిష్కరించడం",
     "'don't have to' (absence of necessity) reappears here from mentoring practice, reassuring a friend rather than giving obligation-based advice — a useful review of necessity versus prohibition."),
    ("day88-friend-04", 4, "I was surprised too, but I feel things will get better soon.", "నేను కూడా ఆశ్చర్యపోయాను, కానీ విషయాలు త్వరలో మెరుగుపడతాయని నేను భావిస్తున్నాను.",
     ["/s/ in 'surprised'", "/b/ in 'better'"], "surprised", "feeling mild astonishment because of something unexpected", "ఆశ్చర్యపోయిన",
     "This combines an unexpected-situation reaction ('I was surprised too') with a hedged opinion ('but I feel...') in one sentence, echoing the pattern from social-topics practice but used to comfort rather than debate."),
    ("day88-friend-05", 5, "If I were you, I'd give it a little more time before deciding anything.", "నేను నీ స్థానంలో ఉంటే, ఏదైనా నిర్ణయం తీసుకునే ముందు కొంచెం సమయం ఇస్తాను.",
     ["/w/ in 'were'", "/d/ in 'deciding'"], "decide", "to make a choice after thinking", "నిర్ణయించుకోవడం",
     "The hypothetical mentoring conditional 'If I were you, I'd...' returns here from mentoring practice, showing it works naturally for advising friends through personal situations, not just professional guidance."),
]

DAY89_LESSONS = [
    ("day89-conversation-01", 1, "I've been meaning to ask you — did you end up changing your flight, or did you keep the original booking?", "నేను నిన్ను అడగాలని అనుకుంటున్నాను — నువ్వు చివరికి నీ విమాన బుకింగ్ మార్చావా, లేదా అసలైనదే ఉంచావా?",
     ["/m/ in 'meaning'", "/dʒ/ in 'changing'"], "end up", "to eventually reach a situation or decision", "చివరికి ... అవ్వడం",
     "'I've been meaning to ask' (present perfect continuous) shows an intention that's existed for a while, and 'end up' expresses an eventual outcome after some process — spoken-English connectors that Telugu speakers often replace with simpler, flatter past tense forms."),
    ("day89-conversation-02", 2, "She told me she'd call back later, but she still hasn't, so I'm a bit worried.", "ఆమె తర్వాత తిరిగి కాల్ చేస్తానని చెప్పింది, కానీ ఇంకా చేయలేదు, అందుకని నాకు కొంచెం ఆందోళనగా ఉంది.",
     ["/k/ in 'call'", "/w/ in 'worried'"], "worried", "feeling anxious or troubled", "ఆందోళనగా ఉన్న",
     "'she'd call' is reported speech ('would' replacing 'will' from the direct speech 'I will call'), and 'still hasn't' uses present perfect for an unfinished expectation. Telugu speakers often keep the original tense when reporting speech, saying 'she told me she will call', which breaks English backshifting rules."),
    ("day89-conversation-03", 3, "By the time we finished discussing it, we'd already agreed on a plan for next month.", "మేము దాని గురించి చర్చించడం ముగించే సరికి, వచ్చే నెలకు ఒక ప్రణాళికపై ఇప్పటికే అంగీకరించాము.",
     ["/dʒ/ in 'agreed'", "/pl/ cluster in 'plan'"], "agreed", "reached the same opinion or decision as someone else", "అంగీకరించాము",
     "'By the time X, we'd already Y' uses past perfect to show one past action completed before another past action — a sequencing structure Telugu speakers often flatten into two simple past sentences, losing the sense of which event happened first."),
    ("day89-conversation-04", 4, "Even though I don't fully agree, I can see why you'd feel that way about it.", "నేను పూర్తిగా ఏకీభవించకపోయినా, నువ్వు అలా ఎందుకు అనుకుంటున్నావో నాకు అర్థమవుతోంది.",
     ["/ð/ in 'though'", "/f/ in 'fully'"], "fully", "completely, entirely", "పూర్తిగా",
     "'Even though X, I can see why Y' respectfully acknowledges another person's viewpoint while still disagreeing — combining the concession connector from social-topics practice with the empathetic modal 'can see why'. Telugu speakers often use 'but' alone here, which can sound more dismissive than intended."),
    ("day89-conversation-05", 5, "If you hadn't mentioned it, I probably wouldn't have noticed the mistake at all.", "నువ్వు దాని గురించి చెప్పకపోతే, నేను బహుశా ఆ తప్పును అస్సలు గమనించి ఉండేవాడిని కాదు.",
     ["/h/ in 'hadn't'", "/n/ in 'noticed'"], "mention", "to refer to something briefly in speech", "ప్రస్తావించడం",
     "This is a third conditional ('If you hadn't..., I wouldn't have...') describing an unreal past situation and its unreal past result. Telugu speakers often mix tenses here, producing forms like 'if you didn't mention, I wouldn't notice', losing the past-in-the-past meaning."),
]

DAY90_LESSONS = [
    ("day90-capstone-01", 1, "If I hadn't started practicing English every day back then, I honestly don't think I'd be able to hold a conversation as confidently as I do now.", "అప్పట్లో నేను ప్రతిరోజూ ఇంగ్లీష్ ప్రాక్టీస్ చేయడం మొదలుపెట్టకపోయుంటే, ఇప్పుడు ఇంత నమ్మకంగా సంభాషణ కొనసాగించగలననని నేను నిజంగా అనుకోను.",
     ["/h/ in 'hadn't'", "/v/ in 'conversation'"], "confidently", "in a self-assured, sure manner", "నమ్మకంగా",
     "This mixes a third-conditional cause ('If I hadn't started... back then') with a present-tense result ('I'd be able to hold... now') — a natural 'mixed conditional' fluent speakers use to link a past unreal condition to a present unreal result, something Telugu speakers rarely attempt because Telugu conditionals don't split past cause from present result this way."),
    ("day90-capstone-02", 2, "Even though I used to get really nervous about speaking in front of people, I've learned that if you just keep practicing, you'll eventually get comfortable with it.", "నేను ప్రజల ముందు మాట్లాడాలంటే చాలా భయపడేవాడ్ని అయినప్పటికీ, నువ్వు ప్రాక్టీస్ చేస్తూ ఉంటే క్రమంగా దానితో సౌకర్యంగా మారతావని నేను నేర్చుకున్నాను.",
     ["/nɜːr/ in 'nervous'", "/f/ in 'front'"], "eventually", "in the end, after some time", "క్రమంగా / చివరికి",
     "This combines a past habit ('used to get nervous') with a concession ('even though'), a present perfect reflection ('I've learned'), and a first conditional ('if you keep practicing, you'll get comfortable') — four structures from across the program working together in one natural spoken sentence."),
    ("day90-capstone-03", 3, "She told me she'd been struggling with the interview, so I suggested that she prepare a few key points in advance, and it seems to have worked out well for her.", "ఆమె ఇంటర్వ్యూలో ఇబ్బంది పడుతున్నానని నాతో చెప్పింది, కాబట్టి కొన్ని ముఖ్యమైన పాయింట్లు ముందుగానే సిద్ధం చేసుకోమని నేను సూచించాను, అది ఆమెకు బాగా పని చేసినట్టు అనిపిస్తోంది.",
     ["/str/ cluster in 'struggling'", "/v/ in 'advance'"], "struggling", "having difficulty doing something", "ఇబ్బంది పడటం",
     "Reported speech backshifts 'has been struggling' to 'she'd been struggling' (past perfect continuous), advice is given with the suggestion structure 'I suggested that she prepare' (subjunctive, no '-s'), and 'seems to have worked out' uses a present perfect infinitive for a present guess about a past result — three advanced structures Telugu speakers often simplify or get wrong individually."),
    ("day90-capstone-04", 4, "Looking back, if someone had told me on day one that I'd be giving presentations in English and negotiating prices confidently, I probably wouldn't have believed them.", "వెనక్కి తిరిగి చూస్తే, మొదటి రోజునే నేను ఇంగ్లీష్‌లో ప్రెజెంటేషన్లు ఇస్తానని, ధరలను నమ్మకంగా బేరమాడతానని ఎవరైనా చెప్పి ఉంటే, నేను బహుశా వాళ్ళను నమ్మేవాడిని కాదు.",
     ["/dʒ/ in 'negotiating'", "/b/ in 'believed'"], "negotiate", "to discuss something to reach an agreement, e.g. on price", "బేరమాడటం / చర్చించడం",
     "This is a full third conditional ('if someone had told me... I wouldn't have believed') wrapped around a reported future-in-the-past clause ('that I'd be giving presentations'), reflecting back on the whole learning journey — the kind of layered, multi-clause sentence a confident B2 speaker produces naturally."),
    ("day90-capstone-05", 5, "What I'd suggest to anyone starting this journey is that you shouldn't be afraid of making mistakes, because that's exactly how I've improved the most, even though it wasn't always comfortable at the time.", "ఈ ప్రయాణాన్ని మొదలుపెట్టే ఎవరికైనా నేను సూచించేదేమిటంటే, తప్పులు చేయడానికి భయపడవద్దు, ఎందుకంటే నేను అలాగే ఎక్కువగా మెరుగుపడ్డాను, అది ఎప్పుడూ సౌకర్యంగా అనిపించకపోయినా.",
     ["/dʒ/ in 'journey'", "/k/ in 'comfortable'"], "improved", "became better at something", "మెరుగుపడ్డాను",
     "The mentoring frame 'What I'd suggest is that...' returns here combined with negative advice ('shouldn't be afraid'), present perfect achievement ('I've improved the most'), and a closing concession ('even though it wasn't always comfortable') — bringing together advice-giving, reflection, and concession in one closing, natural sentence."),
]

# ---------------------------------------------------------------------------
# Days list: (track, cefrLevel, unit, lessons)
# ---------------------------------------------------------------------------

DAYS = [
    ("day-61-debate", "B1/B2", "Expressing Opinions & Debating Respectfully", DAY61_LESSONS),
    ("day-62-negotiate", "B1/B2", "Negotiating Prices & Terms", DAY62_LESSONS),
    ("day-63-interview", "B1/B2", "Formal Job Interview Practice", DAY63_LESSONS),
    ("day-64-lifegoals", "B1/B2", "Long-Term Plans & Life Goals", DAY64_LESSONS),
    ("day-65-service", "B1/B2", "Handling Difficult Service Situations", DAY65_LESSONS),
    ("day-66-news", "B1/B2", "Talking About News & Current Events", DAY66_LESSONS),
    ("day-67-decision", "B1", "Talking About a Decision You Made (Week 11 review)", DAY67_LESSONS),
    ("day-68-narrative", "B1/B2", "Telling a Longer Story", DAY68_LESSONS),
    ("day-69-presentation", "B1/B2", "Giving a Short Presentation", DAY69_LESSONS),
    ("day-70-hypothetical", "B1/B2", "Talking About Hypotheticals", DAY70_LESSONS),
    ("day-71-formal", "B1/B2", "Formal Requests & Professional Language", DAY71_LESSONS),
    ("day-72-medical", "B1/B2", "Explaining Symptoms to a Doctor in Detail", DAY72_LESSONS),
    ("day-73-clarifydeep", "B1/B2", "Clarifying Complex Ideas", DAY73_LESSONS),
    ("day-74-lesson", "B1", "Telling a Story With a Lesson (Week 12 review)", DAY74_LESSONS),
    ("day-75-culture", "B1/B2", "Talking About Culture & Traditions", DAY75_LESSONS),
    ("day-76-regret", "B1/B2", "Expressing Regret & Reflecting", DAY76_LESSONS),
    ("day-77-feedback", "B1/B2", "Giving & Receiving Feedback", DAY77_LESSONS),
    ("day-78-smalltalk", "B1/B2", "Advanced Small Talk", DAY78_LESSONS),
    ("day-79-selfimprove", "B1/B2", "Talking About Self-Improvement", DAY79_LESSONS),
    ("day-80-solution", "B1/B2", "Explaining a Problem & Proposing a Solution", DAY80_LESSONS),
    ("day-81-encouragement", "B1", "Giving Someone Encouragement (Week 13 review)", DAY81_LESSONS),
    ("day-82-videocalls", "B1/B2", "Professional Phone & Video Call Etiquette", DAY82_LESSONS),
    ("day-83-finance", "B1/B2", "Money & Financial Planning", DAY83_LESSONS),
    ("day-84-unexpected", "B1/B2", "Handling Unexpected Situations Calmly", DAY84_LESSONS),
    ("day-85-socialtopics", "B1/B2", "Discussing Social Topics Respectfully", DAY85_LESSONS),
    ("day-86-traveladvanced", "B1/B2", "Advanced Travel & Booking", DAY86_LESSONS),
    ("day-87-mentor", "B1/B2", "Mentoring & Advising Someone", DAY87_LESSONS),
    ("day-88-friend", "B1", "Helping a Friend Through a Situation (Week 14 review)", DAY88_LESSONS),
    ("day-89-conversation", "B1/B2", "Extended Real Conversation Practice", DAY89_LESSONS),
    ("day-90-capstone", "B2", "Level 3 Capstone — Confident, Independent English Speaker", DAY90_LESSONS),
]


def seed_lessons() -> None:
    for track, cefr_level, unit, lessons in DAYS:
        for lesson_id, order, sentence, native_sentence, sounds, vocab_word, vocab_meaning, vocab_native, grammar_note in lessons:
            fields = {
                "id": lesson_id,
                "track": track,
                "cefrLevel": cefr_level,
                "unit": unit,
                "type": "speak_repeat",
                "order": order,
                "xpReward": 10,
                "prompt": {
                    "targetSentence": sentence,
                    "nativeTranslation": native_sentence,
                    "focusSounds": sounds,
                    "vocabIntroduced": [{"word": vocab_word, "meaning": vocab_meaning, "nativeMeaning": vocab_native}],
                    "grammarNote": grammar_note,
                },
            }
            upsert("lessons", lesson_id, fields)


QUIZZES = {
    "quiz-day-61": {
        "track": "day-61-debate", "title": "Day 61 Quiz — Expressing Opinions & Debating Respectfully", "xpReward": 30,
        "questions": [
            ("Which sentence correctly introduces a personal opinion?", ["In my opinion, exams should be shorter.", "In my opinion, exams should shorter.", "In my opinion, exams shorted be shorter.", "My in opinion, exams should be shorter."], 0,
             "'In my opinion' is followed by a complete clause with 'should be' (modal + be + adjective); the other options break word order or omit the verb 'be'."),
            ("Choose the correct polite disagreement:", ["I understand why you think that, but I don't fully agree.", "I understand why you thinking that, but I don't fully agree.", "I understand why you think that, but I no fully agree.", "I understanding why you think that, but I don't fully agree."], 0,
             "The base form 'think' follows 'why you', and 'don't' is the correct negative auxiliary; the other options use incorrect verb forms ('thinking' instead of 'think', 'understanding' instead of 'understand') or omit the auxiliary ('I no fully agree' instead of 'I don't')."),
            ("Select the grammatically correct sentence:", ["I see your point, but I think the evidence says something different.", "I see your point, but I think the evidences says something different.", "I see your point, but I think evidence say something different.", "I see you point, but I think the evidence says something different."], 0,
             "'Evidence' is an uncountable noun and never takes a plural '-s'; option 3 also drops the article 'the' and uses the wrong verb form 'say' instead of 'says', and option 4 wrongly drops the possessive 's' from 'your'."),
            ("Which sentence correctly presents two opposing opinions?", ["Some people believe exams are necessary, while others feel they cause too much stress.", "Some people believe exams are necessary, while others feels they cause too much stress.", "Some people believes exams are necessary, while others feel they cause too much stress.", "Some people believe exams is necessary, while others feel they cause too much stress."], 0,
             "Both 'people' and 'others' are plural subjects and need the plural verb forms 'believe' and 'feel', not the singular '-s' forms used in the other options."),
            ("Choose the correct polite way to strongly disagree:", ["With all due respect, I have to disagree with that argument.", "With all due respect, I have to disagree that argument.", "With all due respect, I have disagree with that argument.", "With all due respect, I has to disagree with that argument."], 0,
             "'Disagree with' requires the preposition 'with' before the object, and subject-verb agreement requires 'I have to', not 'I has to'; the other options drop the preposition 'with' or drop 'to' after 'have'."),
        ],
    },
    "quiz-day-62": {
        "track": "day-62-negotiate", "title": "Day 62 Quiz — Negotiating Prices & Terms", "xpReward": 30,
        "questions": [
            ("Complete the conditional offer correctly:", ["If you can give me a better price, I'll buy two of them.", "If you can give me a better price, I buy two of them.", "If you will can give me a better price, I'll buy two of them.", "If you can give me a better price, I'll bought two of them."], 0,
             "The first conditional uses present tense in the if-clause ('can give') and 'will'/'ll' + base verb in the result clause ('I'll buy'); the other options either drop 'will' from the result clause, wrongly double the modal 'will can', or use the wrong verb form 'bought' after ''ll'."),
            ("Choose the polite, firm refusal:", ["I'm sorry, but I can't go any lower than this.", "I'm sorry, but I can't go any low than this.", "I'm sorry, but I not can go any lower than this.", "I'm sorry, but I can't going any lower than this."], 0,
             "'Can't' is followed by the base verb 'go', and the comparative form 'lower' (not 'low') is needed before 'than'; the other options use the wrong adjective form, incorrect negative word order, or the wrong verb form 'going' after 'can't'."),
            ("Select the correct conditional deal sentence:", ["If you include free delivery, we have a deal.", "If you include free delivery, we having a deal.", "If you including free delivery, we have a deal.", "If you includes free delivery, we have a deal."], 0,
             "The if-clause uses simple present with the base form 'include' after 'you', and the result clause uses simple present 'we have'; the other options wrongly use '-ing' forms in place of the base verb or add an incorrect '-s' after 'you'."),
            ("Choose the correct polite negotiation question:", ["Would you be willing to accept payment in two installments?", "Would you be willing accept payment in two installments?", "Would you willing to accept payment in two installments?", "Would you be will to accept payment in two installments?"], 0,
             "'Be willing to + base verb' is the fixed structure; the other options drop 'to', drop the auxiliary 'be', or incorrectly replace 'willing' with 'will'."),
            ("Which sentence correctly forms a conditional negotiation question?", ["If we order in bulk, will you reduce the price per unit?", "If we will order in bulk, will you reduce the price per unit?", "If we order in bulk, you will reduce the price per unit?", "If we ordering in bulk, will you reduce the price per unit?"], 0,
             "The if-clause should use simple present ('we order'), not 'will' — 'will' belongs only in the result clause; the other options wrongly add 'will' to the if-clause, drop the auxiliary inversion needed for a question ('will you'), or use the wrong verb form 'ordering'."),
        ],
    },
    "quiz-day-63": {
        "track": "day-63-interview", "title": "Day 63 Quiz — Formal Job Interview Practice", "xpReward": 30,
        "questions": [
            ("Choose the correct way to ask someone to introduce themselves:", ["Tell me about yourself and your work experience.", "Tell me about you and your work experience.", "Tell me about yourself and you work experience.", "Tell me about youself and your work experience."], 0,
             "The reflexive pronoun 'yourself' (not the object pronoun 'you') is required after 'about' when referring back to the listener, and 'your' (the possessive form, not 'you') must come before 'work experience'."),
            ("Select the correct sentence describing a strength:", ["My greatest strength is that I stay calm under pressure.", "My greatest strength is I stay calm under pressure.", "My greatest strength is that I staying calm under pressure.", "My greatest strength are that I stay calm under pressure."], 0,
             "'That' is required to introduce the clause 'I stay calm under pressure' after the linking verb 'is'; the other options drop 'that', use the wrong verb form 'staying', or wrongly use the plural verb 'are' with the singular subject 'strength'."),
            ("Choose the correctly phrased weakness statement:", ["One area I'm working to improve is my time management.", "One area I'm working to improving is my time management.", "One area I working to improve is my time management.", "One area I'm working to improve are my time management."], 0,
             "'Working to improve' uses the base verb after 'to', and the singular subject 'One area' requires the singular verb 'is', not 'are'; the other options misuse '-ing' after 'to' or drop the auxiliary 'am' from 'I'm'."),
            ("Which sentence correctly describes a career goal?", ["I'm looking for a role where I can grow and take on more responsibility.", "I'm looking for a role where I can grow and taking on more responsibility.", "I'm looking a role where I can grow and take on more responsibility.", "I'm looking for a role where I can grows and take on more responsibility."], 0,
             "Both verbs joined by 'and' must stay in the same base form after the modal 'can' ('grow and take'), and 'looking for' requires the preposition 'for'; the other options break this parallel structure, drop 'for', or wrongly add '-s' to 'grow' after 'can'."),
            ("Choose the grammatically correct interview question:", ["Why should we hire you over other candidates?", "Why we should hire you over other candidates?", "Why should we hire you over other candidate?", "Why should we hiring you over other candidates?"], 0,
             "This is a direct question, so the auxiliary 'should' must come before the subject 'we' ('should we hire'); the other options reverse this word order, use the singular 'candidate' where the plural is needed, or use the wrong verb form 'hiring' after 'should'."),
        ],
    },
    "quiz-day-64": {
        "track": "day-64-lifegoals", "title": "Day 64 Quiz — Long-Term Plans & Life Goals", "xpReward": 30,
        "questions": [
            ("Choose the correct sentence for a long-term plan:", ["I'm going to start my own business in five years.", "I'm going to starting my own business in five years.", "I'm going start my own business in five years.", "I going to start my own business in five years."], 0,
             "'Going to' is followed by the base verb 'start', and the full auxiliary 'am' ('I'm') is required before 'going to'; the other options use the wrong verb form '-ing' or drop the auxiliary 'am'."),
            ("Select the correct future continuous sentence:", ["By next year, I'll be working as a certified accountant.", "By next year, I'll working as a certified accountant.", "By next year, I be working as a certified accountant.", "By next year, I'll be work as a certified accountant."], 0,
             "Future continuous requires 'will + be + verb-ing' ('I'll be working'); the other options drop 'be', drop 'will', or use the base verb 'work' instead of the '-ing' form."),
            ("Choose the sentence that correctly describes a future ongoing state:", ["This time next year, we'll be living in our own house.", "This time next year, we'll living in our own house.", "This time next year, we living in our own house.", "This time next year, we'll be live in our own house."], 0,
             "The future continuous structure 'will + be + verb-ing' requires all three parts together ('we'll be living'); the other options omit 'be', omit 'will', or use the base verb 'live' instead of '-ing'."),
            ("Which sentence correctly expresses a yearly plan?", ["I'm planning to learn a new skill every year for the next five years.", "I'm planning learn a new skill every year for the next five years.", "I'm planning to learning a new skill every year for the next five years.", "I'm plan to learn a new skill every year for the next five years."], 0,
             "'Planning to' must be followed by the base verb 'learn', not the '-ing' form, and 'to' must not be dropped; the last option also incorrectly drops the auxiliary 'am' before 'planning'."),
            ("Choose the correct sentence about a hoped-for future state:", ["In ten years, I hope to be running my own school.", "In ten years, I hope to running my own school.", "In ten years, I hoping to be running my own school.", "In ten years, I hope be running my own school."], 0,
             "'Hope to be running' correctly combines 'hope to' with the continuous infinitive 'be running'; the other options drop 'be' after 'to', use the wrong form 'hoping' without an auxiliary, or drop 'to' entirely."),
        ],
    },
    "quiz-day-65": {
        "track": "day-65-service", "title": "Day 65 Quiz — Handling Difficult Service Situations", "xpReward": 30,
        "questions": [
            ("Choose the correct polite request:", ["I'd like to speak to the manager, please.", "I'd like speak to the manager, please.", "I'd liking to speak to the manager, please.", "I like to speak to the manager, please."], 0,
             "'I'd like to' (short for 'I would like to') requires 'to' before the base verb 'speak'; the other options drop 'to', use the wrong form 'liking', or drop the 'would' contraction '-d', changing the polite meaning."),
            ("Select the correct complaint sentence:", ["This product is defective, and I'd like a full refund.", "This product is defective, and I'd like a full refunds.", "This product are defective, and I'd like a full refund.", "This product is defective, and I like a full refund."], 0,
             "'Refund' here is a single countable request and should not be pluralized as 'refunds', and the singular subject 'product' requires the singular verb 'is', not 'are'; the last option also drops the 'would' contraction, weakening the polite request form."),
            ("Choose the correct sentence for escalating a complaint:", ["I've already asked twice, so now I need to speak to someone senior.", "I've already asking twice, so now I need to speak to someone senior.", "I've already ask twice, so now I need to speak to someone senior.", "I've already asked twice, so now I needing to speak to someone senior."], 0,
             "Present perfect requires 'have'/'ve' + past participle ('asked'), so 'I've already asked' is correct; the other options wrongly use '-ing' or base verb forms after 'have'/'ve', or drop the correct verb form by using 'needing' instead of 'need'."),
            ("Choose the correct conditional warning sentence:", ["If this isn't resolved today, I'll have to file a formal complaint.", "If this isn't resolved today, I have to file a formal complaint.", "If this not resolved today, I'll have to file a formal complaint.", "If this isn't resolve today, I'll have to file a formal complaint."], 0,
             "The if-clause needs the auxiliary 'isn't' before the past participle 'resolved', and the result clause needs 'I'll have to' (will + have to) to express a future consequence; the other options drop 'will', drop the auxiliary 'isn't', or use the base verb 'resolve' instead of the past participle."),
            ("Select the correct polite question about a billing error:", ["Could you explain why I was charged twice for the same order?", "Could you explain why was I charged twice for the same order?", "Could you explain why I charged twice for the same order?", "Could you explain why I were charged twice for the same order?"], 0,
             "In an embedded question after 'explain why', normal statement word order is used ('I was charged'), not question word order ('was I charged'); the other options also wrongly invert the word order, drop the auxiliary 'was', or use 'were' instead of 'was' with the singular subject 'I'."),
        ],
    },
    "quiz-day-66": {
        "track": "day-66-news", "title": "Day 66 Quiz — Talking About News & Current Events", "xpReward": 30,
        "questions": [
            ("Choose the correct sentence reporting written news:", ["I read that the government is planning to reduce fuel prices.", "I read that the government planning to reduce fuel prices.", "I reading that the government is planning to reduce fuel prices.", "I read that the government is plan to reduce fuel prices."], 0,
             "The reported clause needs the auxiliary 'is' before 'planning' to form the present continuous; the other options drop 'is', use the wrong verb form 'reading' instead of 'read', or use 'plan' instead of 'planning' after 'is'."),
            ("Select the correct sentence reporting a general opinion:", ["They say that the new law will affect small businesses the most.", "They says that the new law will affect small businesses the most.", "They say that the new law affect small businesses the most.", "They say that the new law will affects small businesses the most."], 0,
             "The plural subject 'they' requires the plural verb 'say', not 'says'; the embedded clause also needs 'will affect' (future with base verb), not the bare present 'affect' or the incorrect 'will affects'."),
            ("Choose the correct sentence citing a news source:", ["According to today's news, the match was cancelled due to rain.", "According today's news, the match was cancelled due to rain.", "According to today's news, the match were cancelled due to rain.", "According to today's news, the match was cancel due to rain."], 0,
             "'According to' requires the preposition 'to', and the singular subject 'match' needs the singular past-tense passive 'was cancelled', not 'were cancelled' or the incorrect base form 'was cancel'."),
            ("Select the correct sentence reporting something heard:", ["I heard that prices are going to rise again next month.", "I heard that prices is going to rise again next month.", "I heard that prices are going to rising again next month.", "I hear that prices are going to rise again next month, yesterday."], 0,
             "The plural subject 'prices' needs the plural verb 'are', not 'is', and 'going to' must be followed by the base verb 'rise', not 'rising'; the last option also mixes present tense 'hear' with a past time marker 'yesterday', which is inconsistent."),
            ("Choose the correct sentence reporting expert opinion:", ["Many experts believe that the economy will improve next year.", "Many experts believes that the economy will improve next year.", "Many experts believe that the economy will improving next year.", "Many expert believe that the economy will improve next year."], 0,
             "The plural subject 'experts' requires the plural verb 'believe', not 'believes', and 'will' must be followed by the base verb 'improve', not 'improving'; the last option also incorrectly uses the singular 'expert' with a plural quantifier 'many'."),
        ],
    },
    "quiz-day-67": {
        "track": "day-67-decision", "title": "Day 67 Quiz — Explaining a Decision", "xpReward": 30,
        "questions": [
            ("I decided to take the job ___ it offered better opportunities.", ["because", "because of", "so", "although"], 0,
             "'because' introduces a full clause giving a reason; 'because of' needs a noun phrase (not a clause), 'so' shows a result, and 'although' shows contrast."),
            ("I chose to stay in my hometown instead of ___ to the city.", ["moving", "move", "moved", "to move"], 0,
             "'instead of' is a preposition and must be followed by a verb + '-ing' form, not the base form, past tense, or infinitive."),
            ("Which sentence is grammatically correct?", ["I thought about it carefully before I made my final decision.", "I thought about it careful before I made my final decision.", "I thinking about it carefully before I made my final decision.", "I thought about it carefully before I make my final decision."], 0,
             "The adverb 'carefully' (not 'careful') modifies 'thought', and both verbs stay in the simple past tense ('thought', 'made') since this describes a completed sequence of past actions."),
            ("My main reason ___ this college was its good reputation.", ["for choosing", "for choose", "for chose", "choosing"], 0,
             "'reason for' takes a gerund (verb + '-ing'); a bare verb ('choose'), past tense ('chose'), or a missing preposition entirely (just 'choosing') are all incorrect here."),
            ("___, I believe I made the right decision.", ["Looking back", "Look back", "Looked back", "Seeing back"], 0,
             "'Looking back' is a present participle phrase used to open a reflective statement about the past; a bare imperative ('Look back'), a past-tense form ('Looked back'), or a non-idiomatic literal phrase ('Seeing back') are not used this way in English."),
        ],
    },
    "quiz-day-68": {
        "track": "day-68-narrative", "title": "Day 68 Quiz — Telling a Story", "xpReward": 30,
        "questions": [
            ("I ___ home when it suddenly started raining.", ["was walking", "walked", "am walking", "walk"], 0,
             "Past continuous ('was walking') sets the background scene that was in progress when the sudden action interrupted it; simple past, present continuous, and present tense don't fit a past narrative interruption."),
            ("While I was cooking dinner, the phone ___.", ["rang", "rings", "ring", "has rang"], 0,
             "The short interrupting action takes simple past tense ('rang'); present tense forms don't fit a past narrative, and 'has rang' is also wrong since the correct past participle of 'ring' is 'rung', not 'rang'."),
            ("She ___ sleeping when the earthquake happened.", ["was", "is", "were", "did"], 0,
             "The past continuous auxiliary for 'she' (singular) is 'was', not 'is' (present tense), 'were' (wrong subject agreement), or 'did' (which doesn't combine with an '-ing' verb)."),
            ("Which sentence correctly describes a sudden electricity failure?", ["The power went out during the match.", "The power was gone out during the match.", "The power went off out during the match.", "The current has go out during the match."], 0,
             "'went out' is the correct simple past phrasal verb for a sudden electricity failure; the other options add an unnecessary 'was', duplicate the particle ('went off out'), or use an incorrect verb form ('has go out')."),
            ("___, everything turned out fine.", ["In the end", "In the last", "On the end", "At the last"], 0,
             "'In the end' is the fixed idiomatic phrase meaning 'eventually, after everything else'; 'in the last', 'on the end', and 'at the last' are not standard English phrases."),
        ],
    },
    "quiz-day-69": {
        "track": "day-69-presentation", "title": "Day 69 Quiz — Giving a Presentation", "xpReward": 30,
        "questions": [
            ("___, I'd like to talk about our sales results.", ["Firstly", "First of", "Firstly of", "The first"], 0,
             "'Firstly' is a complete signposting adverb used alone to introduce the first point; 'first of' and 'firstly of' are incomplete, nonstandard fragments, and 'the first' is a noun phrase, not an adverb, so it cannot stand alone this way."),
            ("Secondly, ___ look at the challenges we faced.", ["let's", "let's to", "lets to", "let us to"], 0,
             "'let's' (let us) is directly followed by the base verb 'look'; adding 'to' after 'let's' or 'let us' is a common error — English does not use 'to' here."),
            ("___, I'll explain our plan for next year.", ["Moving on", "Move on", "Moved on", "Moving onto"], 0,
             "'Moving on' (present participle) is the fixed transitional phrase for shifting to a new topic; 'move on' is a bare command, 'moved on' is past tense, and 'moving onto' incorrectly adds a preposition that doesn't belong in this fixed phrase."),
            ("Finally, I'll take ___ questions you have.", ["any", "much", "every", "no"], 0,
             "'any' correctly modifies the plural countable noun 'questions' in this open invitation; 'much' is used with uncountable nouns, and 'every' requires a singular noun ('every question'), making both grammatically wrong here; 'no' would reverse the meaning to refusing questions."),
            ("___, this project has been a great success.", ["To sum up", "To summary", "Summing", "For sum up"], 0,
             "'To sum up' is the correct fixed infinitive phrase for introducing a summary; 'to summary' misuses a noun as a verb, 'summing' is an incomplete fragment missing 'to' and 'up', and 'for sum up' uses the wrong preposition."),
        ],
    },
    "quiz-day-70": {
        "track": "day-70-hypothetical", "title": "Day 70 Quiz — Talking About Hypotheticals", "xpReward": 30,
        "questions": [
            ("If it rains tomorrow, I ___ the trip.", ["will cancel", "would cancel", "cancel", "am cancelling"], 0,
             "First conditional uses 'will' + base verb in the main clause for a real future possibility; 'would' is for hypothetical/unreal conditions, and the other options are missing the future modal entirely."),
            ("If I ___ more time, I would learn to drive.", ["had", "have", "will have", "would have"], 0,
             "Second conditional uses past simple ('had') in the if-clause to describe an unreal present situation, paired with 'would' in the main clause; present tense, future 'will have', and 'would have' (used for past hypotheticals) are all incorrect here."),
            ("If I had known about the traffic, I ___ left earlier.", ["would have", "would", "will have", "had"], 0,
             "Third conditional pairs past perfect ('had known') with 'would have' + past participle to talk about an unreal past regret; 'would' alone, 'will have', and repeating 'had' don't form the correct third conditional structure."),
            ("If she ___ hard, she will pass the exam.", ["studies", "will study", "studied", "is studying"], 0,
             "In first conditional sentences, the if-clause uses present simple even though it refers to the future ('studies'), never 'will'; past tense or present continuous also don't fit this structure."),
            ("If I ___ you, I would ask for help.", ["were", "was", "am", "would be"], 0,
             "'If I were you' is a fixed hypothetical expression that always uses 'were', regardless of the subject; 'was' breaks this fixed pattern, and 'am'/'would be' don't fit the second conditional if-clause."),
        ],
    },
    "quiz-day-71": {
        "track": "day-71-formal", "title": "Day 71 Quiz — Formal Requests", "xpReward": 30,
        "questions": [
            ("I would be grateful ___ you could send me the report by Friday.", ["if", "that", "when", "so"], 0,
             "'I would be grateful if...' is the fixed formal polite request pattern; 'that', 'when', and 'so' do not fit this conditional-style structure."),
            ("Could you ___ explain that point again?", ["possibly", "possible", "possibility", "possibly to"], 0,
             "'possibly' is an adverb placed after the modal 'could you' to soften the request; 'possible' and 'possibility' are the adjective and noun forms and cannot be used here, and 'possibly to' incorrectly adds 'to'."),
            ("Would it be possible ___ our meeting?", ["to reschedule", "rescheduling", "for reschedule", "we reschedule"], 0,
             "'Would it be possible to + base verb' is the correct formal request pattern; a gerund, a bare verb after 'for', or a plain clause without 'to' don't fit this structure."),
            ("I was wondering if you ___ help me with this problem.", ["could", "could to", "would to", "will can"], 0,
             "'I was wondering if you could + base verb' is the correct polite pattern; adding 'to' after a modal ('could to', 'would to') is ungrammatical, and 'will can' incorrectly stacks two modals together, which English does not allow."),
            ("Thank you for your time; I look forward ___ hearing from you.", ["to", "for", "on", "in"], 0,
             "'look forward to' always takes the preposition 'to' (followed by a gerund); 'for', 'on', and 'in' are not used with this fixed phrasal verb."),
        ],
    },
    "quiz-day-72": {
        "track": "day-72-medical", "title": "Day 72 Quiz — Explaining Symptoms to a Doctor", "xpReward": 30,
        "questions": [
            ("I've had a headache ___ three days now.", ["for", "since", "from", "during"], 0,
             "'for' is used with a duration or length of time ('for three days'); 'since' is used with a starting point in time, and 'from'/'during' don't fit this present perfect duration pattern."),
            ("It ___ whenever I bend down.", ["hurts", "hurt", "is hurt", "hurting"], 0,
             "Present simple with the third-person '-s' ending ('hurts') describes a repeated, general condition; the base form, the passive 'is hurt', and the bare '-ing' form without an auxiliary are all incorrect here."),
            ("I've been feeling dizzy ___ yesterday morning.", ["since", "for", "from", "in"], 0,
             "'since' is used with a specific starting point in time ('yesterday morning'); 'for' would need a duration instead of a point in time, and 'from'/'in' don't fit this present perfect continuous pattern."),
            ("The pain gets ___ at night.", ["worse", "more bad", "badder", "more worse"], 0,
             "'worse' is the correct irregular comparative form of 'bad'; 'more bad', 'badder', and 'more worse' are all incorrect ways of forming this comparative."),
            ("I think I ___ have a fever.", ["might", "would", "must to", "can to"], 0,
             "'might have' expresses uncertainty about a current condition; 'would' doesn't fit this context of present possibility, and 'must to'/'can to' are ungrammatical since modal verbs are never followed by 'to' + base verb."),
        ],
    },
    "quiz-day-73": {
        "track": "day-73-clarifydeep", "title": "Day 73 Quiz — Clarifying Complex Ideas", "xpReward": 30,
        "questions": [
            ("Choose the correct rephrasing opener:", ["What I mean is, we need to finish before the deadline.", "What I mean, we need to finish before the deadline.", "What do I mean is, we need to finish before the deadline.", "What I am meaning is, we need to finish before the deadline."], 0,
             "'What I mean is...' requires 'is' after the noun clause, and 'mean' is a stative verb that is not normally used in the continuous form."),
            ("Which sentence correctly uses 'In other words' to restate an idea?", ["In other words, the project got delayed because we didn't have enough funding.", "In other words, the project delayed because we didn't have enough funding.", "In other word, the project got delayed because we didn't have enough funding.", "In other words, the project got delay because we didn't have enough funding."], 0,
             "'Delayed' needs an auxiliary here ('got delayed'); 'other words' is always plural in this fixed phrase, and 'got delay' is not a valid verb form."),
            ("Pick the correct use of 'To put it simply':", ["To put it simply, we're spending more than we're earning.", "To put simply it, we're spending more than we're earning.", "To put it simple, we're spending more than we're earning.", "To putting it simply, we're spending more than we're earning."], 0,
             "The fixed phrase is 'to put it simply' — the object pronoun 'it' comes right after 'put', the adverb 'simply' (not the adjective 'simple') describes how it's put, and the base verb follows 'to', not the gerund."),
            ("Which sentence correctly signals a self-correction/rephrase?", ["Let me rephrase that — what I'm trying to say is, I need more time to decide.", "Let me rephrase that — what I try to say is, I need more time to decide.", "Let me rephrasing that — what I'm trying to say is, I need more time to decide.", "Let me rephrase it that — what I'm trying to say is, I need more time to decide."], 0,
             "'Let me' is followed by the base verb 'rephrase', not the gerund; the ongoing attempt to explain is expressed with present continuous 'I'm trying to say', not simple present."),
            ("Choose the correct summarizing sentence:", ["So basically, what I'm saying is, we should test the product before we launch it.", "So basically, what I'm saying is, we should test the product before we will launch it.", "So basically, what I saying is, we should test the product before we launch it.", "So basically, what I'm say is, we should test the product before we launch it."], 0,
             "After the time connector 'before', present tense is used even for a future action ('before we launch it'), not 'will launch'; also, the continuous form requires 'I'm saying', not 'I saying' or 'I'm say'."),
        ],
    },
    "quiz-day-74": {
        "track": "day-74-lesson", "title": "Day 74 Quiz — Telling a Story With a Lesson", "xpReward": 30,
        "questions": [
            ("Which sentence correctly narrates a past story?", ["Once, a farmer lost all his crops, but he never gave up hope.", "Once, a farmer loses all his crops, but he never gave up hope.", "Once, a farmer has lost all his crops, but he never gave up hope.", "Once, a farmer lost all his crops, but he never give up hope."], 0,
             "A story set in the past uses simple past tense consistently throughout; mixing in present tense ('loses'), present perfect ('has lost'), or an unmarked base verb ('give') breaks the narrative tense."),
            ("Which is the correct third conditional (reflecting on an unreal past)?", ["If he had given up that day, he would never have succeeded.", "If he gave up that day, he would never have succeeded.", "If he had given up that day, he would never succeed.", "If he has given up that day, he would never have succeeded."], 0,
             "The third conditional needs past perfect in the 'if' clause ('had given up') and 'would have + past participle' in the main clause ('would never have succeeded') to talk about an unreal past event."),
            ("Choose the correctly formed 'moral of the story' statement:", ["The moral of the story is that patience always pays off.", "The moral of the story that patience always pays off.", "The moral of the story is that patience always pay off.", "The moral of story is that patience always pays off."], 0,
             "The fixed phrase needs 'is' before the 'that' clause, the article 'the' before 'story', and subject-verb agreement in the clause ('patience... pays', not 'pay')."),
            ("Which sentence correctly uses the formal 'I would like to' structure?", ["I would like to share a story that taught me an important lesson.", "I would like sharing a story that taught me an important lesson.", "I would to like share a story that taught me an important lesson.", "I would like share a story that taught me an important lesson."], 0,
             "'I would like to' is always followed by the infinitive ('to share'), never a gerund, and 'to' must come directly before the base verb, not before 'like'."),
            ("Which sentence correctly combines rephrasing with a first conditional lesson?", ["In other words, if we stay determined like that farmer, we too can overcome hard times.", "In other words, if we stayed determined like that farmer, we too can overcome hard times.", "In other words, if we stay determined like that farmer, we too could overcame hard times.", "In other words, if we stay determine like that farmer, we too can overcome hard times."], 0,
             "A first conditional uses present tense in the 'if' clause ('if we stay') with 'can/will' in the main clause; 'determined' here is the adjective form, and 'overcame' cannot follow the modal 'could', which needs the base form 'overcome'."),
        ],
    },
    "quiz-day-75": {
        "track": "day-75-culture", "title": "Day 75 Quiz — Talking About Culture & Traditions", "xpReward": 30,
        "questions": [
            ("Which sentence correctly describes a habitual cultural practice?", ["In my hometown, we usually celebrate festivals with the whole extended family.", "In my hometown, we usually celebrating festivals with the whole extended family.", "In my hometown, we celebrate usually festivals with the whole extended family.", "In my hometown, we usually celebrated festivals with the whole extended family."], 0,
             "Habitual actions use present simple ('celebrate'), with the frequency adverb 'usually' placed before the main verb — not after it, and not with the past tense form 'celebrated'."),
            ("Choose the correct comparative sentence:", ["Compared to city life, village traditions are followed much more strictly.", "Compared to city life, village traditions are followed much strictly.", "Compared with city life, village tradition are followed much more strictly.", "Compare to city life, village traditions are followed much more strictly."], 0,
             "The comparative adverb 'more strictly' needs the intensifier 'much' before it; the introductory phrase must be the past participle 'compared', not the base verb 'compare', and 'traditions' stays plural to agree with 'are'."),
            ("Which sentence correctly uses 'Unlike':", ["Unlike in the West, most weddings here last for several days.", "Unlike in the West, most weddings here lasts for several days.", "Unlike in West, most weddings here last for several days.", "Unlike in the West, most wedding here last for several days."], 0,
             "The plural subject 'weddings' requires the plural verb form 'last', not 'lasts'; the place name 'the West' needs its article, and 'wedding' must be plural to match 'weddings'."),
            ("Choose the correct comparative tendency sentence:", ["The older generation tends to follow customs more closely than the younger one does.", "The older generation tend to follow customs more closely than the younger one does.", "The older generation tends to following customs more closely than the younger one does.", "The older generation tends to follow customs more close than the younger one does."], 0,
             "The singular subject 'generation' takes 'tends' (not 'tend'); 'tends to' is followed by the base verb 'follow' (not a gerund), and the comparative needs the adverb 'closely' (not the adjective 'close')."),
            ("Which sentence correctly describes a cultural custom with a time expression?", ["Where I come from, guests are always offered food the moment they arrive.", "Where I come from, guests are always offer food the moment they arrive.", "Where I come from, guests are always offered food the moment they arrived.", "Where I come from, guest are always offered food the moment they arrive."], 0,
             "The passive needs the past participle 'offered' (not 'offer'); the time clause 'the moment they arrive' takes present tense for habitual meaning (not 'arrived'), and 'guests' must stay plural."),
        ],
    },
    "quiz-day-76": {
        "track": "day-76-regret", "title": "Day 76 Quiz — Expressing Regret & Reflecting", "xpReward": 30,
        "questions": [
            ("Which sentence correctly expresses regret about the past?", ["I should have studied harder before the exam.", "I should have study harder before the exam.", "I should has studied harder before the exam.", "I should studied harder before the exam."], 0,
             "'should have + past participle' requires 'have' (not 'has') followed by the past participle 'studied' (not the base verb 'study'); 'have' cannot be dropped."),
            ("Choose the correct 'I wish' sentence for past regret:", ["I wish I had told her the truth from the beginning.", "I wish I told her the truth from the beginning.", "I wish I have told her the truth from the beginning.", "I wish I had tell her the truth from the beginning."], 0,
             "A wish about the past needs past perfect: 'I wish I had + past participle'. Simple past ('told') and present perfect ('have told') are both incorrect here, and 'had' must be followed by the past participle 'told', not the base verb 'tell'."),
            ("Which sentence correctly criticizes a past decision?", ["We shouldn't have left so late; now we're stuck in traffic.", "We shouldn't have leave so late; now we're stuck in traffic.", "We didn't should have left so late; now we're stuck in traffic.", "We shouldn't left so late; now we're stuck in traffic."], 0,
             "'shouldn't have + past participle' requires the past participle 'left' (not the base verb 'leave'); modals are negated by adding 'not' directly ('shouldn't'), not with 'didn't should', and 'have' cannot be dropped."),
            ("Choose the correct sentence expressing regret about something not done:", ["Looking back, I regret not spending more time with my grandparents.", "Looking back, I regret to not spend more time with my grandparents.", "Looking back, I regret not spent more time with my grandparents.", "Looking back, I regret not to spending more time with my grandparents."], 0,
             "'Regret' expressing sorrow over a past omission takes a gerund: 'regret not spending'. An infinitive ('regret to not spend') or a mixed/incorrect form is not valid here."),
            ("Which sentence correctly uses 'If only' for strong regret?", ["If only I had asked for help sooner, things wouldn't have gotten so bad.", "If only I asked for help sooner, things wouldn't have gotten so bad.", "If only I had asked for help sooner, things wouldn't get so bad.", "If only I had ask for help sooner, things wouldn't have gotten so bad."], 0,
             "'If only' for past regret needs past perfect in the 'if' clause ('had asked') and 'wouldn't have + past participle' in the result clause ('wouldn't have gotten'); 'had' must be followed by the past participle 'asked', not the base verb 'ask'."),
        ],
    },
    "quiz-day-77": {
        "track": "day-77-feedback", "title": "Day 77 Quiz — Giving & Receiving Feedback", "xpReward": 30,
        "questions": [
            ("Which sentence correctly softens a suggestion?", ["One thing you could try is explaining your ideas a bit more slowly.", "One thing you could try is explain your ideas a bit more slowly.", "One thing you could tried is explaining your ideas a bit more slowly.", "One thing you could try is to explaining your ideas a bit more slowly."], 0,
             "After 'is', the gerund 'explaining' is needed, not the base verb; the modal 'could' must be followed by the base verb 'try', not the past tense 'tried', and 'to' should not appear before a gerund."),
            ("Choose the correct way to graciously accept feedback:", ["Thanks for pointing that out — I'll fix it right away.", "Thanks for point that out — I'll fix it right away.", "Thanks to pointing that out — I'll fix it right away.", "Thanks for pointed that out — I'll fix it right away."], 0,
             "'Thanks for' is always followed by a gerund ('pointing'), never the base verb ('point') or the past tense ('pointed'); the preposition here must be 'for', not 'to'."),
            ("Which sentence correctly gives indirect advice?", ["It might help if you double-checked the numbers before sending the report.", "It might helps if you double-checked the numbers before sending the report.", "It might help if you double-checking the numbers before sending the report.", "It might help you double-checked the numbers before sending the report."], 0,
             "After the modal 'might', the base verb 'help' is required, not 'helps'; the 'if' clause needs a finite verb ('double-checked'), not a gerund, and the conjunction 'if' cannot be omitted."),
            ("Choose the sentence that correctly balances praise with softened criticism:", ["I really appreciate the effort, though I think the introduction could be a little clearer.", "I really appreciate the effort, though I think the introduction could being a little clearer.", "I really appreciate the effort, though I think the introduction could clearer.", "I really appreciate effort, though I think the introduction could be a little clearer."], 0,
             "The modal 'could' must be followed by the base verb 'be' (not 'being' or omitted entirely), and the noun 'effort' needs the article 'the' when referring to a specific effort just discussed."),
            ("Which sentence correctly asks polite permission to give feedback?", ["Would you mind if I gave you some feedback on your presentation?", "Would you mind I gave you some feedback on your presentation?", "Would you mind if I gives you some feedback on your presentation?", "Would you mind if I giving you some feedback on your presentation?"], 0,
             "'Would you mind if...' requires the conjunction 'if' after 'mind', and the clause needs a finite past-tense verb for politeness ('gave'), not the third-person form 'gives' or the gerund 'giving'."),
        ],
    },
    "quiz-day-78": {
        "track": "day-78-smalltalk", "title": "Day 78 Quiz — Advanced Small Talk", "xpReward": 30,
        "questions": [
            ("Which sentence correctly uses 'By the way' to change topics?", ["By the way, did you hear about the new mall opening downtown?", "By the way, did you heard about the new mall opening downtown?", "By way, did you hear about the new mall opening downtown?", "By the way, you did hear about the new mall opening downtown?"], 0,
             "After the auxiliary 'did', the base verb 'hear' is required, not the past participle 'heard'; the fixed phrase is 'by the way' with the article 'the', and a question needs auxiliary-subject inversion ('did you hear')."),
            ("Choose the correct use of 'That reminds me':", ["That reminds me — I still need to return your book.", "That reminds me — I still need return your book.", "That remind me — I still need to return your book.", "That reminds to me — I still need to return your book."], 0,
             "The singular subject 'that' requires 'reminds' (not 'remind'); 'reminds me' takes no extra preposition ('reminds to me' is wrong), and 'need' is followed by the infinitive 'to return'."),
            ("Which sentence correctly uses 'Speaking of' to shift topics?", ["Speaking of food, have you tried that new restaurant near the office?", "Speak of food, have you tried that new restaurant near the office?", "Speaking of food, have you try that new restaurant near the office?", "Speaking food, have you tried that new restaurant near the office?"], 0,
             "The fixed phrase is the gerund form 'speaking of' (not the base verb 'speak'), and it requires the preposition 'of'; after 'have', the past participle 'tried' is needed, not the base verb 'try'."),
            ("Choose the correct sentence using 'Anyway' with a present habitual question:", ["Anyway, how's your sister doing these days?", "Anyway, how's your sister does these days?", "Anyway, how does your sister doing these days?", "Anyway, how's your sister do these days?"], 0,
             "'How's your sister doing' uses 'is' (contracted to 's) plus the '-ing' form 'doing'; mixing in 'does' with 's or using the base verb 'do' after 's are both incorrect combinations."),
            ("Which sentence correctly uses 'Before I forget' to introduce a new topic?", ["Before I forget, can I ask you something unrelated?", "Before I forget, can I ask you something unrelate?", "Before I forget, can I to ask you something unrelated?", "Before I forgetting, can I ask you something unrelated?"], 0,
             "'Unrelate' is not a word — the correct adjective is 'unrelated'; after the modal 'can', the base verb 'ask' follows directly with no 'to', and 'before I forget' uses the base verb 'forget', not 'forgetting'."),
        ],
    },
    "quiz-day-79": {
        "track": "day-79-selfimprove", "title": "Day 79 Quiz — Self-Improvement", "xpReward": 30,
        "questions": [
            ("Choose the correct sentence:", ["I've been trying to wake up earlier every day.", "I've been try to wake up earlier every day.", "I trying to wake up earlier every day.", "I've been trying wake up earlier every day."], 0,
             "'have been' + verb-ing + 'to' + base verb is the correct present perfect continuous pattern with 'try to'."),
            ("I've been working ___ my English pronunciation for a few months.", ["on", "in", "at", "for"], 0,
             "'work on something' is the correct phrasal verb combination meaning to make efforts to improve it."),
            ("Choose the correct sentence about a goal:", ["My goal is to finish this course by December.", "My goal is finish this course by December.", "My goal is to finishing this course by December.", "My goal to finish this course by December."], 0,
             "'My goal is to' + base verb requires 'to' plus the base form of the verb, and the linking verb 'is' must be present."),
            ("Which sentence correctly shows an ongoing problem?", ["I haven't been sleeping well, so I'm trying to fix my routine.", "I haven't sleep well, so I'm trying to fix my routine.", "I not been sleeping well, so I'm trying to fix my routine.", "I haven't being sleeping well, so I'm trying to fix my routine."], 0,
             "Negative present perfect continuous is formed with 'haven't been' + verb-ing; the other options use incorrect or missing auxiliary forms."),
            ("Choose the correct sentence:", ["I've made a lot of progress since I started practicing every day.", "I made a lot of progress since I am starting practicing every day.", "I've make a lot of progress since I started practicing every day.", "I've made a lot of progress since I start practicing every day."], 0,
             "Present perfect ('I've made') pairs with simple past ('I started') after 'since' to link a past starting point to a present result."),
        ],
    },
    "quiz-day-80": {
        "track": "day-80-solution", "title": "Day 80 Quiz — Explaining a Problem & Proposing a Solution", "xpReward": 30,
        "questions": [
            ("Choose the correct way to state a problem formally:", ["The issue is that the app keeps crashing when I open it.", "The issue that the app keeps crashing when I open it.", "The issue is the app keep crashing when I open it.", "Issue is that the app keeps crashing when I open it."], 0,
             "'The issue is that' + clause requires both the linking verb 'is' and the connector 'that' to introduce the problem clause correctly."),
            ("Choose the correct sentence:", ["I suggest we reschedule the meeting to next week.", "I suggest to reschedule the meeting to next week.", "I suggest we rescheduling the meeting to next week.", "I suggest we rescheduled the meeting to next week."], 0,
             "'suggest + subject + base verb' (no 'to') is correct; adding 'to', using a gerund, or using the past tense are all incorrect after 'suggest' here."),
            ("Choose the correct sentence describing a solution:", ["One way to solve this is to double-check the numbers before sending.", "One way to solve this is double-check the numbers before sending.", "One way for solve this is to double-check the numbers before sending.", "One way to solving this is to double-check the numbers before sending."], 0,
             "'One way to solve this is to' + base verb needs 'to' before both 'solve' and the following verb; using 'for' or a gerund breaks this pattern."),
            ("Choose the correct conditional sentence:", ["If we fix the login page first, the rest should be easier.", "If we will fix the login page first, the rest should be easier.", "If we fixed the login page first, the rest should be easier.", "If we fixing the login page first, the rest should be easier."], 0,
             "In a real (first) conditional, the if-clause uses present simple ('fix'), not 'will fix', past tense 'fixed', or an -ing form."),
            ("Choose the correct sentence:", ["I recommend that we test it again before we launch.", "I recommend we to test it again before we launch.", "I recommend that we tests it again before we launch.", "I recommend that we testing it again before we launch."], 0,
             "'recommend that + subject + base verb' uses the subjunctive base form ('test'), without 's' or '-ing', and without 'to'."),
        ],
    },
    "quiz-day-81": {
        "track": "day-81-encouragement", "title": "Day 81 Quiz — Giving Someone Encouragement", "xpReward": 30,
        "questions": [
            ("Choose the correct way to comfort someone about a mistake:", ["Don't worry about the mistake — everyone messes up sometimes.", "Don't worry the mistake — everyone messes up sometimes.", "Don't worry about the mistake — everyone messing up sometimes.", "Don't worried about the mistake — everyone messes up sometimes."], 0,
             "'worry about' needs the preposition 'about', and the imperative 'Don't worry' uses the base form, not 'worried'."),
            ("Choose the correct sentence acknowledging effort:", ["You've been working really hard, and it shows.", "You've been work really hard, and it shows.", "You been working really hard, and it shows.", "You've being working really hard, and it shows."], 0,
             "Present perfect continuous requires 'have/'ve' + 'been' + verb-ing; the other options are missing or misuse an auxiliary."),
            ("Choose the correct sentence:", ["I know you regret how the interview went, but you'll do better next time.", "I know you regret how the interview went, but you do better next time.", "I know you regret how the interview go, but you'll do better next time.", "I know you regret how the interview went, but you will better next time."], 0,
             "'you'll do better' correctly uses 'will' with the base verb 'do'; omitting 'will' or the verb 'do' breaks the future prediction."),
            ("Choose the correct way to respond to feedback:", ["Thanks for the feedback — I'll try to fix that next time.", "Thanks the feedback — I'll try to fix that next time.", "Thanks for the feedback — I'll try fix that next time.", "Thanks for the feedback — I try to fix that next time."], 0,
             "'Thanks for' requires the preposition 'for', and 'try to fix' requires 'to' before the base verb; 'I'll' is needed to show future intention."),
            ("Choose the correct sentence:", ["You've already come a long way, so don't give up now.", "You already come a long way, so don't give up now.", "You've already came a long way, so don't give up now.", "You've already come a long way, so don't given up now."], 0,
             "Present perfect with 'already' needs 'have/'ve' + past participle ('come'), not simple present, simple past ('came'), or a bare past participle after 'don't' ('given')."),
        ],
    },
    "quiz-day-82": {
        "track": "day-82-videocalls", "title": "Day 82 Quiz — Professional Phone & Video Call Etiquette", "xpReward": 30,
        "questions": [
            ("Choose the correct way to propose a new time:", ["Can we reschedule the call to tomorrow afternoon?", "Can we reschedule the call at tomorrow afternoon?", "Can we reschedule the call to tomorrow's afternoon?", "Can we rescheduled the call to tomorrow afternoon?"], 0,
             "'reschedule...to' + time is correct; 'at' is the wrong preposition here, 'tomorrow's afternoon' is not a natural time phrase, and the base verb 'reschedule' (not the past tense) must follow the modal 'can'."),
            ("Choose the correct sentence about a technical problem happening now:", ["I'm having connection issues — can you hear me now?", "I have connection issues since now — can you hear me now?", "I having connection issues — can you hear me now?", "I'm have connection issues — can you hear me now?"], 0,
             "Present continuous 'I'm having' correctly shows a problem happening right now; the other options misuse or drop the auxiliary 'am'."),
            ("Choose the correct group suggestion for a call:", ["Let's mute ourselves when we're not speaking.", "Let's mute ourself when we're not speaking.", "Let's muting ourselves when we're not speaking.", "Let's mute ourselves when we not speaking."], 0,
             "'ourselves' (plural reflexive) is correct after 'let's'; 'ourself' is not standard English, and 'we're' (we are) cannot be shortened to just 'we' before 'not speaking'."),
            ("Choose the correct polite request:", ["Could you share your screen so I can see the document?", "Could you share your screen so I can seeing the document?", "Could you shared your screen so I can see the document?", "Could you share you screen so I can see the document?"], 0,
             "The base verb 'see' follows the modal 'can', and 'share' (base form) follows 'could you'; 'you screen' incorrectly uses the subject pronoun instead of the possessive 'your'."),
            ("Choose the correct sentence:", ["I'll send you the meeting link five minutes before we start.", "I'll send you the meeting link five minutes before we will start.", "I send you the meeting link five minutes before we start.", "I'll sending you the meeting link five minutes before we start."], 0,
             "Time clauses with 'before' use present simple ('we start') even when referring to the future, not 'will start'; the main clause needs 'I'll send', not 'I send' or 'I'll sending'."),
        ],
    },
    "quiz-day-83": {
        "track": "day-83-finance", "title": "Day 83 Quiz — Money & Financial Planning", "xpReward": 30,
        "questions": [
            ("Choose the correct conditional sentence about saving money:", ["If I save five thousand rupees every month, I'll be able to buy a bike by next year.", "If I will save five thousand rupees every month, I'll be able to buy a bike by next year.", "If I save five thousand rupees every month, I be able to buy a bike by next year.", "If I saved five thousand rupees every month, I'll be able to buy a bike by next year."], 0,
             "In a first conditional, the if-clause uses present simple ('save') and the result clause needs 'will' ('I'll be able to'); using 'will' in the if-clause, dropping 'will' from the result clause, or using past tense 'saved' with 'I'll' are all incorrect."),
            ("Choose the correct sentence about future plans:", ["I'm planning to set aside some money for emergencies.", "I'm planning set aside some money for emergencies.", "I plan to setting aside some money for emergencies.", "I'm planning to set aside some money for emergencies since long."], 0,
             "'be planning to' + base verb requires 'to' before the base verb 'set'; dropping 'to' or using 'setting' after 'plan to' is incorrect."),
            ("Choose the correct sentence:", ["If I invest this money wisely, it will grow over time.", "If I invest wisely this money, it will grow over time.", "If I invest this money wisely, it grow over time.", "If I invested this money wisely, it will grow over time."], 0,
             "The adverb 'wisely' correctly comes after the object ('this money wisely'); the result clause needs 'will grow', and the if-clause needs present simple 'invest' (not past tense 'invested') to match the 'will' result clause."),
            ("Choose the correct sentence about paying off debt:", ["Once I pay off this loan, I'll have more savings every month.", "Once I will pay off this loan, I'll have more savings every month.", "Once I pay off this loan, I have more savings every month.", "Once I paid off this loan, I'll have more savings every month."], 0,
             "'Once' introduces a future time clause using present simple ('pay off'), not 'will pay' or past tense 'paid'; the main clause correctly uses 'I'll have' to show the future result."),
            ("Choose the correct sentence about reducing expenses:", ["If we cut down on eating out, we'll save a lot by the end of the year.", "If we cut down eating out, we'll save a lot by the end of the year.", "If we cut down on eating out, we save a lot by the end of the year.", "If we cut down on eat out, we'll save a lot by the end of the year."], 0,
             "The phrasal verb 'cut down on' requires the preposition 'on' before the gerund 'eating'; the result clause needs 'we'll save' to show the future outcome."),
        ],
    },
    "quiz-day-84": {
        "track": "day-84-unexpected", "title": "Day 84 Quiz — Handling Unexpected Situations Calmly", "xpReward": 30,
        "questions": [
            ("Choose the correct apology:", ["I'm sorry for the delay — my previous meeting ran longer than expected.", "I'm sorry for delay — my previous meeting ran longer than expected.", "I'm sorry for late — my previous meeting ran longer than expected.", "I'm sorry about for the delay — my previous meeting ran longer than expected."], 0,
             "'sorry for' is followed by a noun with an article ('the delay'); 'late' is an adjective and cannot follow 'sorry for', and using both 'about' and 'for' together is incorrect."),
            ("Choose the correct sentence expressing regret about a past action:", ["I should have told you earlier, and I apologize for the confusion.", "I should told you earlier, and I apologize for the confusion.", "I should have tell you earlier, and I apologize for the confusion.", "I should have telling you earlier, and I apologize for the confusion."], 0,
             "'should have' + past participle ('told') correctly expresses regret about the past; omitting 'have' or using the base form/gerund instead of the past participle is incorrect."),
            ("Choose the correct way to explain an unexpected delay:", ["Something came up suddenly, so I couldn't make it on time.", "Something come up suddenly, so I couldn't make it on time.", "Something came up suddenly, so I can't make it on time.", "Something was come up suddenly, so I couldn't make it on time."], 0,
             "'came up' (simple past) correctly matches 'couldn't' (past ability); using present tense forms like 'come' or 'can't' breaks the past-tense consistency of the story."),
            ("Choose the correct promise after a mistake:", ["It won't happen again — I'll double-check everything from now on.", "It don't happen again — I'll double-check everything from now on.", "It won't happened again — I'll double-check everything from now on.", "It won't happen again — I double-check everything from now on."], 0,
             "'won't' (will not) + base verb ('happen') correctly forms the future negative promise; 'don't' is present tense and doesn't match the future meaning, and the base form 'happen' (not 'happened') must follow 'won't'."),
            ("Choose the correct sentence about admitting an error:", ["I made a mistake with the dates, and I want to correct it right away.", "I did a mistake with the dates, and I want to correct it right away.", "I made a mistake with the dates, and I want correct it right away.", "I made mistake with the dates, and I want to correct it right away."], 0,
             "The correct collocation is 'made a mistake', not 'did a mistake'; the article 'a' is required before 'mistake', and 'want to correct' needs 'to' before the base verb."),
        ],
    },
    "quiz-day-85": {
        "track": "day-85-socialtopics", "title": "Day 85 Quiz — Discussing Social Topics Respectfully", "xpReward": 30,
        "questions": [
            ("Choose the correctly hedged opinion:", ["Some people think remote work is better, but I feel it depends on the job.", "Some people thinks remote work is better, but I feel it depends on the job.", "Some people think remote work is better, but I am feeling it depends on the job.", "Some people think remote work is better, but I feel it depend on the job."], 0,
             "'people' is a plural noun taking 'think' (not 'thinks'); 'feel' is a stative verb here and isn't normally used in continuous form; and 'it depends' needs the third-person '-s'. Only the first option has correct agreement and verb form throughout."),
            ("'I ___ be wrong, but I think students should learn practical skills.'", ["could", "could to", "am could", "could being"], 0,
             "After the modal 'could', a base verb form follows directly ('could be'), with no 'to', no auxiliary 'am', and no '-ing' form."),
            ("'A lot of people believe joint families are better, ___ personally, I think it depends on the situation.'", ["though", "despite", "because", "although despite"], 0,
             "'though' correctly links two contrasting ideas in one sentence; 'despite' needs a noun phrase (e.g., 'despite this') not a full clause, 'because' reverses the logical relationship, and stacking two connectors together is ungrammatical."),
            ("'In my opinion, both parents can work and still raise their children well, ___ some people disagree.'", ["though", "so", "because of", "unless"], 0,
             "'though' introduces a concession or contrast between the speaker's opinion and others' disagreement; 'so' wrongly signals a cause-effect relation, 'because of' cannot be followed by a full clause, and 'unless' would mean the opposite (a condition), not a simple contrast."),
            ("'Some say arranged marriages work better, but ___, I feel it really depends on the couple.'", ["honestly", "honest", "honestly speak", "to honest"], 0,
             "'Honestly' is the adverb form used to add sincerity to a statement; 'honest' is an adjective and cannot stand alone this way, and the fixed phrase is either 'honestly' or 'to be honest' — not 'honestly speak' or 'to honest'."),
        ],
    },
    "quiz-day-86": {
        "track": "day-86-traveladvanced", "title": "Day 86 Quiz — Advanced Travel & Booking", "xpReward": 30,
        "questions": [
            ("'I'd like ___ my booking to a later flight, if that's possible.'", ["to change", "change", "changing", "changed"], 0,
             "'I'd like to + base verb' is the standard polite request structure; the base verb must be preceded by 'to', not left bare, in gerund form, or in past participle form."),
            ("Choose the correct embedded question:", ["Could you tell me if there is a fee for cancelling this reservation?", "Could you tell me if is there a fee for cancelling this reservation?", "Could you tell me if there a fee is for cancelling this reservation?", "Could you tell me is there a fee for cancelling this reservation?"], 0,
             "In an embedded question after 'if', normal statement word order is used ('there is a fee'), not question word order ('is there'); the sentence also needs 'if' to properly embed the question."),
            ("'I booked a room for two nights, but I ___ to extend it by one more night.'", ["need", "needed", "needing", "am needed"], 0,
             "The sentence describes a current, present need following a past action, so present simple 'need' is correct; 'needed' wrongly shifts to past, 'needing' lacks an auxiliary verb, and 'am needed' incorrectly uses passive voice."),
            ("'Is it possible to get a refund ___ my flight got cancelled?'", ["since", "since that", "because of", "despite"], 0,
             "'since' here means 'because' and can directly introduce a reason clause; 'because of' must be followed by a noun phrase not a clause, 'despite' signals the wrong logical relationship (contrast, not cause), and 'since that' is not a standard connector."),
            ("'I'd like to switch my seat to one near the window, if any ___ available.'", ["are", "is", "be", "will"], 0,
             "'any' refers back to plural 'seats', so the plural verb 'are' is required; 'is' breaks agreement, 'be' can't function as a finite main verb here, and 'will' cannot be followed directly by the adjective 'available' without 'be'."),
        ],
    },
    "quiz-day-87": {
        "track": "day-87-mentor", "title": "Day 87 Quiz — Mentoring & Advising Someone", "xpReward": 30,
        "questions": [
            ("Choose the correct sentence:", ["What I'd suggest is that you practice speaking a little every single day.", "What I'd suggest is that you practicing speaking a little every single day.", "What I'd suggest that you practice speaking a little every single day.", "What I'd suggest is you to practice speaking a little every single day."], 0,
             "The cleft structure 'What I'd suggest is that + subject + base verb' requires 'is' before 'that' and a base verb form ('practice'), not a gerund or an infinitive with 'to'."),
            ("'You ___ want to start with small goals before taking on bigger ones.'", ["might", "might to", "are might", "musting"], 0,
             "'might want to' is a fixed gentle-suggestion structure using the modal 'might' directly followed by 'want to'; modals are never followed by 'to' directly, doubled with 'are', or turned into an '-ing' form."),
            ("'If I ___ mentoring you, I'd tell you to ask more questions in meetings.'", ["were", "was", "am", "will be"], 0,
             "In this hypothetical conditional ('If I were mentoring you, I'd tell you...'), the subjunctive 'were' is used for all subjects including 'I', not 'was', 'am', or a future form."),
            ("'One thing that really ___ me was writing down what I learned each week.'", ["helped", "helps", "helping", "was help"], 0,
             "The sentence recounts a past experience, so the simple past 'helped' is required; present tense, a bare '-ing' form, and 'was help' are all grammatically incorrect here."),
            ("Which sentence correctly expresses that something is NOT necessary?", ["You don't have to get everything right immediately.", "You mustn't get everything right immediately.", "You don't must get everything right immediately.", "You haven't to get everything right immediately."], 0,
             "'don't have to' correctly expresses that something is not necessary; 'mustn't' wrongly expresses prohibition, 'don't must' is ungrammatical since 'must' can't follow 'don't', and 'haven't to' is not a correct negation of 'have to' in modern English."),
        ],
    },
    "quiz-day-88": {
        "track": "day-88-friend", "title": "Day 88 Quiz — Helping a Friend Through a Situation", "xpReward": 30,
        "questions": [
            ("'I know something unexpected happened, but I ___ you handled it really well.'", ["think", "thinks", "thinking", "am think"], 0,
             "With the subject 'I', the base present-tense form 'think' is correct; 'thinks' is for third-person singular, and 'thinking'/'am think' are not grammatical as the main verb here."),
            ("'What I'd suggest is that you ___ to her honestly about how you feel.'", ["talk", "talks", "talked", "to talk"], 0,
             "After 'What I'd suggest is that you...', the base verb form is required ('talk'), without '-s', without changing to past tense, and without an extra 'to'."),
            ("'Solve' most closely means:", ["to find an answer to a problem", "to create a new problem", "to ignore something completely", "to make a problem worse"], 0,
             "'Solve' means to find an answer to or fix a problem — the opposite of creating, ignoring, or worsening one."),
            ("'I was surprised too, but I feel things ___ better soon.'", ["will get", "get", "would got", "getting"], 0,
             "A future prediction here requires 'will + base verb' ('will get'); plain present tense, 'would got' (which wrongly combines a modal with a past-tense verb), and a bare '-ing' form are all incorrect."),
            ("Which sentence uses the hypothetical advice structure correctly?", ["If I were you, I'd wait a bit longer before making a decision.", "If I was you, I'd wait a bit longer before making a decision.", "If I were you, I will wait a bit longer before making a decision.", "If I am you, I'd wait a bit longer before making a decision."], 0,
             "The hypothetical advice structure requires subjunctive 'were' in the if-clause and 'would' ('I'd') in the result clause; using 'was', 'will', or 'am' breaks this pattern."),
        ],
    },
    "quiz-day-89": {
        "track": "day-89-conversation", "title": "Day 89 Quiz — Extended Real Conversation Practice", "xpReward": 30,
        "questions": [
            ("'I've been meaning to ask you — did you end up changing your flight?' What does 'end up' mean here?", ["eventually reach a particular result or decision", "start something from the very beginning", "completely cancel a plan", "immediately decide without thinking"], 0,
             "'End up' describes eventually reaching a result or decision after a process — not starting, cancelling, or deciding immediately."),
            ("'She told me she ___ call back later, but she still hasn't.'", ["'d", "will", "shall", "does"], 0,
             "In reported speech, 'will' from the original statement backshifts to 'would' ('she'd call') when the reporting verb is in the past tense; 'will', 'shall', and 'does' do not correctly reflect this backshifting."),
            ("'By the time we finished discussing it, we ___ already agreed on a plan for next month.'", ["'d", "have", "did", "was"], 0,
             "'By the time X (past), we'd already Y' requires the past perfect ('had already agreed') to show one past action completed before another past action; present perfect, simple past 'did', and 'was' don't correctly express this past-before-past sequencing."),
            ("'Even though I don't fully agree, I can see why you'd feel that way about it.' What does 'even though' signal here?", ["a contrast or concession between two ideas", "a reason or cause", "a condition", "a result"], 0,
             "'Even though' introduces a concession or contrast between two ideas, unlike 'because' (reason), 'if' (condition), or 'so' (result)."),
            ("'If you ___ mentioned it, I probably wouldn't have noticed the mistake at all.'", ["hadn't", "didn't", "haven't", "don't"], 0,
             "This third conditional describes an unreal past situation, requiring past perfect 'hadn't mentioned' in the if-clause paired with 'wouldn't have noticed' in the result clause; 'didn't', 'haven't', and 'don't' all use the wrong tense for this structure."),
        ],
    },
    "quiz-day-90": {
        "track": "day-90-capstone", "title": "Day 90 Quiz — Level 3 Capstone: Confident, Independent English Speaker", "xpReward": 30,
        "questions": [
            ("'If I hadn't started practicing English every day back then, I honestly don't think I'd ___ hold a conversation as confidently as I do now.'", ["be able to", "been able to", "being able to", "was able to"], 0,
             "After 'I'd' (I would), the base verb form follows ('be able to'); a past participle, an '-ing' form, or a finite past tense verb cannot directly follow a modal like 'would'."),
            ("'Even though I used to get really nervous about speaking in front of people, I've learned that if you just keep practicing, you'll eventually ___ comfortable with it.'", ["get", "getting", "got", "to get"], 0,
             "After 'will' ('you'll'), the base verb form is required directly, without '-ing', past tense, or 'to'."),
            ("'She told me she'd been struggling with the interview, so I suggested that she ___ a few key points in advance.'", ["prepare", "prepares", "prepared", "to prepare"], 0,
             "After 'suggested that + subject', English uses the subjunctive base verb form ('prepare'), not a form with '-s', past tense, or 'to'."),
            ("'Looking back, if someone ___ me on day one that I'd be giving presentations in English, I probably wouldn't have believed them.'", ["had told", "told", "has told", "would tell"], 0,
             "This third conditional requires past perfect in the if-clause ('had told'), paired with 'wouldn't have believed' in the result clause; simple past, present perfect, and 'would' are all incorrect here."),
            ("'What I'd suggest to anyone starting this journey is that you ___ be afraid of making mistakes, because that's exactly how I've improved the most.'", ["shouldn't", "don't should", "not should", "aren't should"], 0,
             "The modal 'should' is negated directly as 'shouldn't' (should not); it cannot be negated with 'don't', reordered as 'not should', or combined with 'aren't'."),
        ],
    },
}


def seed_quizzes() -> None:
    for quiz_id, quiz in QUIZZES.items():
        questions = [
            {
                "question": question_text,
                "options": [{"text": text, "isCorrect": i == correct_index} for i, text in enumerate(options)],
                "explanation": explanation,
            }
            for question_text, options, correct_index, explanation in quiz["questions"]
        ]
        fields = {
            "id": quiz_id,
            "track": quiz["track"],
            "title": quiz["title"],
            "xpReward": quiz["xpReward"],
            "questions": questions,
        }
        upsert("quizzes", quiz_id, fields)


if __name__ == "__main__":
    seed_lessons()
    seed_quizzes()
