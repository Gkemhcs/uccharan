"""Seeds Level 2 ("Consolidation", Days 31-60) of the 90-day roadmap into
Firestore: lessons for each day plus one multiple-choice quiz per day.

Level 2 picks up where Level 1 (seed_week1_content.py / seed_weeks_2_to_5_content.py)
left off — B1 solidification. Same design principles as Level 1:
  - Every target sentence is a genuine, high-frequency spoken-English phrase,
    not textbook-stiff filler.
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
    python3 backend/scripts/seed_days_31_to_60_content.py
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

DAY31_LESSONS = [
    ("day31-habits-01", 1, "I used to play cricket every evening.", "నేను ప్రతి సాయంత్రం క్రికెట్ ఆడేవాడిని.",
     ["/juːstə/ in 'used to' (silent d)", "/v/ in 'evening'"], "used to", "a phrase for past habits that no longer happen", "గత అలవాట్లను సూచించే పదబంధం",
     "'used to + base verb' describes a past habit or state that has now stopped. Telugu speakers often say 'I play cricket before' instead — English needs 'used to', not just a time word."),
    ("day31-habits-02", 2, "I usually wake up at six.", "నేను సాధారణంగా ఆరు గంటలకు లేస్తాను.",
     ["/juː/ in 'usually'", "/w/ vs /v/ in 'wake'"], "usually", "most of the time; as a regular habit", "సాధారణంగా",
     "Frequency adverbs like 'usually' go before the main verb in simple present tense to describe a routine that still continues."),
    ("day31-habits-03", 3, "She used to live in a village.", "ఆమె ఒక గ్రామంలో నివసించేది.",
     ["/v/ in 'village'", "/l/ in 'live'"], "village", "a small settlement, smaller than a town", "గ్రామం",
     "'used to' + base verb marks a discontinued past habit. Many Telugu speakers drop it and just say 'she lived', which loses the meaning that it has now changed."),
    ("day31-habits-04", 4, "We don't watch TV much these days.", "మేము ఈ రోజుల్లో ఎక్కువగా టీవీ చూడము.",
     ["/w/ vs /v/ in 'watch'", "/ð/ in 'these'"], "these days", "nowadays; in the present period, as a contrast to the past", "ఈ రోజుల్లో",
     "Negative present habits use 'don't/doesn't + base verb'; 'these days' signals the habit has changed from before."),
    ("day31-habits-05", 5, "He used to smoke, but he quit.", "అతను ధూమపానం చేసేవాడు, కానీ మానేశాడు.",
     ["/sm/ cluster in 'smoke'", "/kw/ in 'quit'"], "quit", "to stop doing something completely", "మానేయడం",
     "'used to' for the old habit, then simple past ('quit') for the change. Avoid the calque 'he is not doing smoking now' — it isn't natural English."),
]

DAY32_LESSONS = [
    ("day32-neighborhood-01", 1, "There is a small market near my house.", "నా ఇంటికి దగ్గర్లో ఒక చిన్న మార్కెట్ ఉంది.",
     ["/ð/ in 'there'", "/m/ cluster in 'market'"], "market", "a place where goods are bought and sold", "మార్కెట్",
     "'There is a ___' introduces something that exists, with the article 'a' before a singular noun. Telugu speakers often skip this structure and just say 'Near house small market.'"),
    ("day32-neighborhood-02", 2, "There are many trees on our street.", "మా వీధిలో చాలా చెట్లు ఉన్నాయి.",
     ["/tr/ cluster in 'trees'", "/str/ cluster in 'street'"], "street", "a public road in a town or city", "వీధి",
     "'There are' is used with plural nouns — 'is/are' must agree in number with the noun that follows."),
    ("day32-neighborhood-03", 3, "It's a quiet area with friendly neighbors.", "ఇది స్నేహపూర్వక పొరుగువారితో ప్రశాంతమైన ప్రాంతం.",
     ["/kw/ in 'quiet'", "/f/ in 'friendly'"], "neighbor", "a person who lives near you", "పొరుగువాడు",
     "'It's a ___ area with ___' is a fixed pattern for describing a place: adjective + noun, followed by a detail introduced by 'with'."),
    ("day32-neighborhood-04", 4, "The bus stop is very close to my home.", "బస్ స్టాప్ నా ఇంటికి చాలా దగ్గరగా ఉంది.",
     ["/st/ cluster in 'stop'", "/kl/ cluster in 'close'"], "close to", "near in distance", "దగ్గరగా",
     "'close to' is a fixed preposition phrase for nearness — the 'to' cannot be dropped, unlike a literal Telugu translation might suggest."),
    ("day32-neighborhood-05", 5, "There isn't a hospital in our neighborhood.", "మా పరిసర ప్రాంతంలో ఆసుపత్రి లేదు.",
     ["/h/ in 'hospital'", "/z/ in 'isn't'"], "neighborhood", "the area around where you live", "పరిసర ప్రాంతం",
     "'There isn't a ___' is the negative form for a singular noun; plural negatives use 'There aren't any ___' instead."),
]

DAY33_LESSONS = [
    ("day33-complaints-01", 1, "I'm afraid there's a problem with my order.", "క్షమించండి, నా ఆర్డర్‌లో ఒక సమస్య ఉంది.",
     ["/f/ in 'afraid'", "/ð/ in \"there's\""], "problem", "an issue or difficulty", "సమస్య",
     "'I'm afraid there's a problem with ___' softens a complaint. Stating it too directly, as in a literal Telugu translation, can sound rude in English."),
    ("day33-complaints-02", 2, "Could you please fix this as soon as possible?", "దయచేసి దీన్ని వీలైనంత త్వరగా సరిచేయగలరా?",
     ["/pl/ cluster in 'please'", "/f/ in 'fix'"], "as soon as possible", "very quickly, without any delay", "వీలైనంత త్వరగా",
     "'Could you please ___?' is a polite request form, softer and more indirect than a plain command like 'Fix this now.'"),
    ("day33-complaints-03", 3, "Excuse me, I think there's a mistake in the bill.", "క్షమించండి, బిల్లులో పొరపాటు ఉందని అనుకుంటున్నాను.",
     ["/ɪ/ in 'excuse'", "/b/ in 'bill'"], "mistake", "an error", "పొరపాటు",
     "'I think there's a mistake' softens the claim, rather than directly accusing someone with 'You are wrong.'"),
    ("day33-complaints-04", 4, "This isn't what I ordered, could you check again?", "ఇది నేను ఆర్డర్ చేసినది కాదు, మీరు మళ్ళీ చెక్ చేస్తారా?",
     ["/tʃ/ in 'check'", "final cluster /rd/ in 'ordered'"], "check again", "to look or verify once more", "మళ్ళీ చెక్ చేయడం",
     "State the problem factually first ('This isn't what I ordered'), then follow with a polite question rather than a blunt demand."),
    ("day33-complaints-05", 5, "I'm sorry to bother you, but the room is too noisy.", "ఇబ్బంది పెడుతున్నందుకు క్షమించండి, కానీ గది చాలా శబ్దంగా ఉంది.",
     ["/ð/ in 'bother'", "/z/ in 'noisy'"], "bother", "to disturb or trouble someone", "ఇబ్బంది పెట్టడం",
     "'I'm sorry to bother you, but ___' is a common softening opener used before raising a complaint in spoken English."),
]

DAY34_LESSONS = [
    ("day34-advice-01", 1, "You should drink more water every day.", "మీరు ప్రతిరోజూ ఎక్కువ నీరు తాగాలి.",
     ["/ʃ/ in 'should'", "/w/ in 'water'"], "should", "a modal verb used to give advice or a recommendation", "సలహా ఇచ్చే క్రియ",
     "'should + base verb' gives advice, with no 'to' after it — a common error when Telugu speakers add 'to' by analogy."),
    ("day34-advice-02", 2, "Why don't you try a new job?", "మీరు కొత్త ఉద్యోగం ఎందుకు ప్రయత్నించకూడదు?",
     ["/w/ in 'why'", "/tr/ cluster in 'try'"], "try", "to attempt something", "ప్రయత్నించడం",
     "'Why don't you + base verb?' is a fixed suggestion form — it's an idea, not a real question about reasons."),
    ("day34-advice-03", 3, "You could ask your doctor for advice.", "మీరు మీ డాక్టర్‌ని సలహా అడగవచ్చు.",
     ["/k/ in 'could'", "/d/ in 'doctor'"], "advice", "a recommendation or suggestion (uncountable)", "సలహా",
     "'could' softens a suggestion, making it gentler than 'should'. 'Advice' is uncountable — there's no plural 'advices'."),
    ("day34-advice-04", 4, "You shouldn't skip breakfast every morning.", "మీరు ప్రతిరోజూ అల్పాహారం మానేయకూడదు.",
     ["/ʃ/ in \"shouldn't\"", "/br/ cluster in 'breakfast'"], "skip", "to miss or not do something", "వదిలేయడం",
     "'shouldn't + base verb' is the negative advice form, the contraction of 'should not'."),
    ("day34-advice-05", 5, "If I were you, I would save some money every month.", "నేను నీ స్థానంలో ఉంటే, ప్రతి నెలా కొంత డబ్బు దాచుకుంటాను.",
     ["/w/ in 'were'", "/m/ in 'money'"], "save", "to keep money instead of spending it", "దాచుకోవడం",
     "'If I were you, I would ___' is a fixed pattern for giving advice; 'were' is used for all subjects here, not 'was'."),
]

DAY35_LESSONS = [
    ("day35-wellbeing-01", 1, "I try to exercise three times a week.", "నేను వారానికి మూడుసార్లు వ్యాయామం చేయడానికి ప్రయత్నిస్తాను.",
     ["/tr/ cluster in 'try'", "/ks/ cluster in 'exercise'"], "exercise", "physical activity done to stay healthy", "వ్యాయామం",
     "'try to + base verb' expresses effort toward a habit or goal. Telugu speakers sometimes drop 'to' and say 'I try exercise', which is incorrect."),
    ("day35-wellbeing-02", 2, "I rarely eat junk food.", "నేను చాలా అరుదుగా జంక్ ఫుడ్ తింటాను.",
     ["/r/ in 'rarely'", "/dʒ/ in 'junk'"], "rarely", "almost never", "అరుదుగా",
     "Frequency adverbs like 'rarely' go before the main verb in simple present. Note 'rarely' already has a near-negative meaning."),
    ("day35-wellbeing-03", 3, "I always drink water before breakfast.", "నేను అల్పాహారానికి ముందు ఎల్లప్పుడూ నీళ్ళు తాగుతాను.",
     ["/w/ vs /v/ in 'water'", "/br/ cluster in 'breakfast'"], "before", "earlier than something", "ముందు",
     "The frequency adverb 'always' is placed before the main verb — not 'I drink always water', a common word-order error."),
    ("day35-wellbeing-04", 4, "I sometimes go for a walk in the evening.", "నేను కొన్నిసార్లు సాయంత్రం వాకింగ్‌కి వెళ్తాను.",
     ["/s/ in 'sometimes'", "/w/ in 'walk'"], "go for a walk", "to walk for exercise or leisure", "వాకింగ్‌కి వెళ్ళడం",
     "'go for a walk' is a fixed collocation for this kind of exercise; learn it as a whole phrase rather than translating word by word."),
    ("day35-wellbeing-05", 5, "I never skip my medicine.", "నేను నా మందు ఎప్పుడూ మానేయను.",
     ["/n/ in 'never'", "/sk/ cluster in 'skip'"], "medicine", "a substance used to treat illness", "మందు",
     "'never' already carries negative meaning, so avoid adding 'don't' as well — 'I don't never skip' is an incorrect double negative."),
]

DAY36_LESSONS = [
    ("day36-jobinterview-01", 1, "I have worked as a teacher for five years.", "నేను ఐదు సంవత్సరాలుగా ఉపాధ్యాయుడిగా పని చేశాను.",
     ["/w/ in 'worked'", "/f/ in 'five'"], "teacher", "a person whose job is to teach", "ఉపాధ్యాయుడు",
     "Present perfect ('have/has + past participle') links past experience to now; use 'for' with a duration like 'five years', and 'since' with a starting point."),
    ("day36-jobinterview-02", 2, "I have never worked in sales before.", "నేను ఇంతకు ముందు సేల్స్‌లో ఎప్పుడూ పని చేయలేదు.",
     ["/s/ in 'sales'", "/v/ in 'never'"], "sales", "the work of selling products", "విక్రయాలు",
     "Present perfect with 'never' describes an experience one has not had up to now; 'before' often reinforces this meaning."),
    ("day36-jobinterview-03", 3, "Have you ever managed a team?", "మీరు ఎప్పుడైనా ఒక బృందాన్ని నిర్వహించారా?",
     ["/h/ in 'have'", "/dʒ/ in 'managed'"], "manage", "to be in charge of or lead something", "నిర్వహించడం",
     "'Have you ever + past participle?' asks about life experience up to now, and is answered with 'Yes, I have' / 'No, I haven't', not simple past."),
    ("day36-jobinterview-04", 4, "She has recently completed a computer course.", "ఆమె ఇటీవల ఒక కంప్యూటర్ కోర్సు పూర్తి చేసింది.",
     ["/r/ in 'recently'", "/kəm/ in 'computer'"], "recently", "not long ago", "ఇటీవల",
     "Present perfect with 'recently' describes something finished a short time ago that is still relevant now; the subject 'she' requires 'has', not 'have'."),
    ("day36-jobinterview-05", 5, "I haven't received any response from them yet.", "నాకు ఇంకా వారి నుండి ఎలాంటి స్పందన రాలేదు.",
     ["/h/ in \"haven't\"", "/r/ in 'received'"], "response", "a reply or answer", "స్పందన",
     "Present perfect negative with 'yet' at the end shows something expected hasn't happened up to now."),
]

DAY37_LESSONS = [
    ("day37-recap-01", 1, "Last week, I visited my parents in the village.", "గత వారం, నేను నా తల్లిదండ్రులను గ్రామంలో సందర్శించాను.",
     ["/v/ in 'visited'", "/p/ in 'parents'"], "last week", "the week before this one", "గత వారం",
     "A finished past time expression like 'last week' requires simple past tense, not present perfect."),
    ("day37-recap-02", 2, "On Monday, I had a problem with my landlord.", "సోమవారం, నాకు నా ఇంటి యజమానితో ఒక సమస్య వచ్చింది.",
     ["/l/ in 'landlord'", "/d/ in 'had'"], "landlord", "a person who rents out property", "ఇంటి యజమాని",
     "'had' is the irregular past form of 'have'; a day name followed by a comma introduces a specific past time."),
    ("day37-recap-03", 3, "Then I asked him for advice about it.", "తర్వాత నేను దాని గురించి అతన్ని సలహా అడిగాను.",
     ["/ð/ in 'then'", "/sk/ cluster in 'asked'"], "then", "next; after that, used to sequence events", "తర్వాత",
     "The sequencing word 'then' links two past events in order; 'advice' stays uncountable, with no plural form."),
    ("day37-recap-04", 4, "After that, I felt much better about the situation.", "దాని తర్వాత, పరిస్థితి గురించి నాకు చాలా బాగా అనిపించింది.",
     ["/f/ in 'felt'", "/b/ in 'better'"], "situation", "a set of circumstances", "పరిస్థితి",
     "'After that' continues a past narrative to the next step; 'felt' is the irregular past form of 'feel'."),
    ("day37-recap-05", 5, "By the end of the week, everything was fine again.", "వారం చివరికి, ప్రతిదీ మళ్ళీ బాగానే అయ్యింది.",
     ["/f/ in 'fine'", "/w/ in 'week'"], "by the end of", "before or at the completion of a time period", "చివరికి",
     "'by the end of ___' marks a deadline point in a past narrative; 'everything' is singular, so it takes 'was', not 'were'."),
]

DAY38_LESSONS = [
    ("day38-preferences-01", 1, "I'd rather stay home tonight.", "నేను ఈ రాత్రి ఇంట్లోనే ఉండటానికి ఇష్టపడతాను.",
     ["/aɪd/ in \"I'd\"", "/r/ in 'rather'"], "would rather", "to prefer to do one thing over another", "ఇష్టపడటం",
     "'I'd rather + base verb' expresses a preference, with no 'to' after it — unlike 'I'd like to'."),
    ("day38-preferences-02", 2, "I prefer tea to coffee.", "నాకు కాఫీ కంటే టీ ఇష్టం.",
     ["/f/ in 'prefer'", "/k/ in 'coffee'"], "prefer", "to like one thing more than another", "ఇష్టపడటం",
     "'prefer X to Y' compares two things — the comparison word after 'prefer' is 'to', not 'than'."),
    ("day38-preferences-03", 3, "I prefer reading books to watching movies.", "నాకు సినిమాలు చూడటం కంటే పుస్తకాలు చదవడం ఇష్టం.",
     ["/r/ in 'reading'", "/tʃ/ in 'watching'"], "reading", "the act of reading (gerund form)", "చదవడం",
     "After 'prefer', use the -ing (gerund) form of the verb when comparing two activities: 'prefer doing X to doing Y'."),
    ("day38-preferences-04", 4, "Would you rather have tea or coffee?", "మీకు టీ ఇష్టమా లేదా కాఫీ ఇష్టమా?",
     ["/w/ in 'would'", "/r/ in 'rather'"], "or", "used to offer a choice between options", "లేదా",
     "'Would you rather X or Y?' is the question form for asking about someone's preference between two options."),
    ("day38-preferences-05", 5, "I don't like spicy food very much.", "నాకు కారంగా ఉండే ఆహారం పెద్దగా ఇష్టం లేదు.",
     ["/sp/ cluster in 'spicy'", "/f/ in 'food'"], "spicy", "having a strong, hot taste", "కారంగా ఉండే",
     "'don't like ___ very much' softens a dislike, making it less blunt than a strong word like 'hate'."),
]

DAY39_LESSONS = [
    ("day39-pastdetail-01", 1, "First, I woke up and made breakfast.", "మొదట, నేను నిద్రలేచి అల్పాహారం తయారు చేశాను.",
     ["/w/ in 'woke'", "/f/ in 'first'"], "first", "the initial step in a sequence", "మొదట",
     "'First' opens a sequence of past actions; 'woke' is the irregular past of 'wake', matching the past tense 'made'."),
    ("day39-pastdetail-02", 2, "Then, I went to the market to buy vegetables.", "తర్వాత, నేను కూరగాయలు కొనడానికి మార్కెట్‌కి వెళ్ళాను.",
     ["/ð/ in 'then'", "/v/ in 'vegetables'"], "vegetables", "plant-based food items", "కూరగాయలు",
     "'Then' links the next action in a past sequence; 'went' is the irregular past of 'go'."),
    ("day39-pastdetail-03", 3, "After that, I cooked lunch for my family.", "దాని తర్వాత, నేను నా కుటుంబం కోసం భోజనం వండాను.",
     ["/k/ in 'cooked'", "/f/ in 'family'"], "cook", "to prepare food", "వండటం",
     "'After that' moves the narrative to the next step; 'cooked' is a regular past tense verb ending in -ed."),
    ("day39-pastdetail-04", 4, "Later, I met my friend at the tea stall.", "తర్వాత, నేను నా స్నేహితుడిని టీ కొట్టు దగ్గర కలిశాను.",
     ["/l/ in 'later'", "/m/ in 'met'"], "later", "at a subsequent point in time", "తర్వాత",
     "'Later' also sequences events, but more loosely than 'then'/'after that'; 'met' is the irregular past of 'meet'."),
    ("day39-pastdetail-05", 5, "Finally, I came back home in the evening.", "చివరగా, నేను సాయంత్రం ఇంటికి తిరిగి వచ్చాను.",
     ["/f/ in 'finally'", "/k/ in 'came'"], "finally", "at the end of a sequence", "చివరగా",
     "'Finally' signals the last step in a sequence of past events; 'came' is the irregular past of 'come'."),
]

DAY40_LESSONS = [
    ("day40-invitations-01", 1, "Would you like to join us for dinner?", "మీరు మాతో డిన్నర్‌కి రావాలనుకుంటున్నారా?",
     ["/w/ in 'would'", "/dʒ/ in 'join'"], "join", "to take part with others", "చేరడం",
     "'Would you like to + base verb?' is the polite way to invite someone; note 'to' is needed here, unlike in 'I'd rather'."),
    ("day40-invitations-02", 2, "I'd love to, thank you.", "తప్పకుండా వస్తాను, ధన్యవాదాలు.",
     ["/l/ in 'love'", "/θ/ in 'thank'"], "I'd love to", "a warm, enthusiastic way to accept an invitation", "సంతోషంగా అంగీకరించడం",
     "'I'd love to' (short for 'I would love to') is a common, enthusiastic way to accept an invitation."),
    ("day40-invitations-03", 3, "I'm sorry, I can't make it this time.", "క్షమించండి, ఈసారి నేను రాలేను.",
     ["/k/ in \"can't\"", "/m/ in 'make'"], "make it", "to be able to attend or come", "రాగలగడం",
     "'I can't make it' is a polite fixed phrase for declining an invitation, softer than a plain 'No'."),
    ("day40-invitations-04", 4, "Shall we meet at seven o'clock?", "మనం ఏడు గంటలకు కలుద్దామా?",
     ["/ʃ/ in 'shall'", "/iː/ in 'meet'"], "shall", "used to suggest a plan together", "కలిసి చేద్దామా అని సూచించడానికి",
     "'Shall we + base verb?' suggests a plan and invites agreement, common in polite spoken English."),
    ("day40-invitations-05", 5, "Thanks for inviting me, but I already have plans.", "నన్ను ఆహ్వానించినందుకు ధన్యవాదాలు, కానీ నాకు ఇప్పటికే ప్లాన్స్ ఉన్నాయి.",
     ["/θ/ in 'thanks'", "/v/ in 'inviting'"], "have plans", "to already have something arranged", "ప్లాన్స్ ఉండటం",
     "'Thanks for ___, but ___' politely declines while acknowledging the invitation; the gerund 'inviting' follows the preposition 'for'."),
]

# ---------------------------------------------------------------------------
# Days list: (track, cefrLevel, unit, lessons)
# ---------------------------------------------------------------------------

DAY41_LESSONS = [
    ("day41-process-01", 1, "First, boil the water.", "మొదట, నీళ్లు మరగబెట్టండి.",
     ["/b/ in 'boil'", "/w/ vs /v/ in 'water'"], "boil", "to heat a liquid until it bubbles", "మరిగించడం",
     "Instructions use the bare imperative verb with no subject — 'First' marks it as step one of a sequence."),
    ("day41-process-02", 2, "Next, add the tea leaves.", "తర్వాత, తేయాకు వేయండి.",
     ["/ð/ in 'the'", "/ks/ cluster in 'next'"], "add", "to put something into a mixture", "కలపడం",
     "'Next' signals the second step; the imperative verb 'add' still needs no subject."),
    ("day41-process-03", 3, "Then, let it simmer for two minutes.", "ఆ తర్వాత, దాన్ని రెండు నిమిషాలు మెల్లగా మరగనివ్వండి.",
     ["final cluster in 'minutes'"], "simmer", "to boil gently at a low heat", "మెల్లగా మరగడం",
     "'Then' links steps just like 'next'. 'Let it + base verb' means allow something to happen on its own."),
    ("day41-process-04", 4, "After that, add some milk.", "దాని తర్వాత, కొంచెం పాలు వేయండి.",
     ["/f/ in 'after'"], "pour", "to make a liquid flow from a container", "పోయడం",
     "'After that' introduces a later step and sounds more natural in speech than repeating 'then' every time."),
    ("day41-process-05", 5, "Finally, strain it into a cup.", "చివరగా, దాన్ని కప్పులోకి వడకట్టండి.",
     ["/f/ in 'finally'", "/tr/ cluster in 'strain'"], "strain", "to separate liquid from solid using a sieve", "వడకట్టడం",
     "'Finally' marks the last step in a process — don't drop the sequencing word, as it signals the instructions are complete."),
]

DAY42_LESSONS = [
    ("day42-phonecalls-01", 1, "Could I leave a message, please?", "దయచేసి, నేను ఒక సందేశం ఇవ్వొచ్చా?",
     ["/l/ in 'leave'", "/dʒ/ in 'message'"], "message", "information left for someone", "సందేశం",
     "'Could I ___?' is a polite way to ask permission, softer than 'Can I'. Telugu speakers often skip this politeness marker and sound too direct in English."),
    ("day42-phonecalls-02", 2, "He's not available right now.", "ఆయన ఇప్పుడు అందుబాటులో లేరు.",
     ["/v/ vs /w/ in 'available'"], "available", "free to talk or meet", "అందుబాటులో",
     "'Available' describes whether a person is free to talk — a key phone word that doesn't translate word-for-word."),
    ("day42-phonecalls-03", 3, "I'll call you back later.", "నేను తర్వాత మీకు తిరిగి కాల్ చేస్తాను.",
     ["/ɔː/ in 'call'"], "call back", "to phone someone again", "తిరిగి కాల్ చేయడం",
     "'Will' is used for a decision made at the moment of speaking, like promising to call back."),
    ("day42-phonecalls-04", 4, "Please hold the line for a moment.", "దయచేసి కొద్దిసేపు లైన్‌లో ఉండండి.",
     ["/h/ in 'hold'", "final /d/ in 'hold'"], "hold", "to wait on the phone line", "లైన్‌లో వేచి ఉండటం",
     "Imperative 'Please hold' is a fixed phone phrase — 'hold' here means to wait on the line, not to physically hold something."),
    ("day42-phonecalls-05", 5, "I think you have the wrong number.", "క్షమించండి, మీరు తప్పు నంబర్‌కు కాల్ చేశారనుకుంటాను.",
     ["/r/ in 'wrong'", "/ʌ/ in 'number'"], "wrong number", "a phone number that is not the one intended", "తప్పు నంబర్",
     "'I think' softens a correction, making 'you have the wrong number' sound polite rather than blunt."),
]

DAY43_LESSONS = [
    ("day43-bargaining-01", 1, "This is too expensive.", "ఇది చాలా ఖరీదైనది.",
     ["/ks/ cluster in 'expensive'"], "expensive", "costing a lot of money", "ఖరీదైన",
     "'Too' + adjective means more than acceptable — different from 'very', which just states a high degree."),
    ("day43-bargaining-02", 2, "Could you lower the price a little?", "ధర కొంచెం తగ్గించగలరా?",
     ["/l/ in 'lower'", "/aɪ/ in 'price'"], "lower", "to reduce", "తగ్గించడం",
     "'Could you ___?' softens a request, making it sound polite rather than a demand — important when bargaining."),
    ("day43-bargaining-03", 3, "This one is cheaper than that one.", "ఇది దాని కంటే చౌక.",
     ["/tʃ/ in 'cheaper'"], "cheaper", "costing less money", "చౌక అయిన",
     "Comparatives add '-er' to short adjectives (cheap → cheaper) and are followed by 'than' when comparing two things."),
    ("day43-bargaining-04", 4, "Can you give me a discount?", "నాకు డిస్కౌంట్ ఇవ్వగలరా?",
     ["/s/ vs /ʃ/ in 'discount'"], "discount", "a reduction in price", "తగ్గింపు",
     "'Give me a discount' is the fixed way to ask for a lower price; the object order 'give me + noun' is essential."),
    ("day43-bargaining-05", 5, "That's my final offer.", "ఇదే నా చివరి ఆఫర్.",
     ["/f/ in 'final' and 'offer'"], "final offer", "the last price you will offer", "చివరి ఆఫర్",
     "'That's my final offer' is a fixed negotiating phrase signalling no more bargaining is possible."),
]

DAY44_LESSONS = [
    ("day44-weekend-01", 1, "We're going to visit my uncle's village this weekend.", "ఈ వారాంతంలో మేము మా బాబాయి గ్రామానికి వెళ్లబోతున్నాం.",
     ["/v/ vs /w/ in 'village'"], "village", "a small settlement in a rural area", "గ్రామం",
     "'Going to' + base verb describes a plan already decided before the moment of speaking — the standard way to talk about weekend plans."),
    ("day44-weekend-02", 2, "I'll book the bus tickets tonight.", "నేను ఈ రాత్రి బస్ టికెట్లు బుక్ చేస్తాను.",
     ["/k/ in 'book'", "final /ts/ cluster in 'tickets'"], "book (tickets)", "to reserve in advance", "బుక్ చేయడం",
     "'Will' (I'll) is used for a decision made right now, unlike 'going to' for pre-planned intentions."),
    ("day44-weekend-03", 3, "The bus leaves at six in the morning.", "బస్సు ఉదయం ఆరు గంటలకు బయలుదేరుతుంది.",
     ["/iː/ vs /ɪ/ in 'leaves'"], "leaves (departs)", "to depart from a place", "బయలుదేరడం",
     "Present simple is used for fixed timetables and schedules, even though the action is in the future."),
    ("day44-weekend-04", 4, "First, we'll pack our bags, then we'll leave.", "మొదట మేము మా బ్యాగులు సర్దుకుంటాం, తర్వాత బయలుదేరతాం.",
     ["/æ/ in 'pack'"], "pack", "to put things into a bag for travel", "సర్దుకోవడం",
     "Review: sequencing words ('first...then') link steps in a plan, reused from Day 41's instruction pattern."),
    ("day44-weekend-05", 5, "Could you save two seats for us, please?", "దయచేసి మాకు రెండు సీట్లు రిజర్వ్ చేసి ఉంచగలరా?",
     ["/s/ in 'save'", "/iː/ in 'seats'"], "save (seats)", "to reserve something for later use", "రిజర్వ్ చేయడం",
     "Review: 'Could you ___?' politely asks a favor, reused from Day 43's bargaining pattern."),
]

DAY45_LESSONS = [
    ("day45-hopes-01", 1, "I hope to get a better job soon.", "నేను త్వరలో మంచి ఉద్యోగం పొందాలని ఆశిస్తున్నాను.",
     ["/h/ in 'hope'", "/dʒ/ in 'job'"], "hope", "to want something to happen", "ఆశించడం",
     "'Hope to' + base verb expresses a realistic wish for the future — different from 'wish', used for things that feel unlikely."),
    ("day45-hopes-02", 2, "I'm planning to learn English this year.", "నేను ఈ సంవత్సరం ఇంగ్లీష్ నేర్చుకోవాలని ప్లాన్ చేస్తున్నాను.",
     ["/pl/ cluster in 'planning'"], "planning", "arranging to do something in the future", "ప్రణాళిక వేయడం",
     "'Planning to' + verb shows an intention already being arranged, stronger than just a hope."),
    ("day45-hopes-03", 3, "I wish I could travel more.", "నేను ఇంకా ఎక్కువ ప్రయాణం చేయగలిగితే బాగుండు.",
     ["/w/ vs /v/ in 'wish'"], "wish", "to want something not currently true or possible", "కోరుకోవడం",
     "'Wish I could' + base verb expresses a desire for something currently impossible, using past form 'could', not 'can'."),
    ("day45-hopes-04", 4, "I'm hoping to buy a house one day.", "నేను ఏదో ఒక రోజు ఇల్లు కొనాలని ఆశపడుతున్నాను.",
     ["/h/ in 'hoping'"], "one day", "at some unspecified time in the future", "ఏదో ఒక రోజు",
     "'Hoping to' (continuous) sounds slightly softer and more ongoing than 'hope to' — both are correct."),
    ("day45-hopes-05", 5, "I really want to improve my English.", "నేను నిజంగా నా ఇంగ్లీష్‌ను మెరుగుపరచుకోవాలని అనుకుంటున్నాను.",
     ["/v/ in 'improve'"], "improve", "to make better", "మెరుగుపరచడం",
     "'Want to' + verb is the most direct, common way to state a desire — simpler than 'wish' or 'hope' for everyday goals."),
]

DAY46_LESSONS = [
    ("day46-obligations-01", 1, "You must wear a helmet on a bike.", "మీరు తప్పనిసరిగా బైక్‌పై హెల్మెట్ ధరించాలి.",
     ["/h/ in 'helmet'"], "must", "expresses strong obligation or a rule", "తప్పనిసరిగా చేయాలి",
     "'Must' expresses a strong rule or obligation — used for laws and strict rules, followed directly by the base verb."),
    ("day46-obligations-02", 2, "I have to finish this work by tomorrow.", "నేను ఈ పనిని రేపటిలోగా పూర్తి చేయాలి.",
     ["/f/ in 'finish'"], "have to", "expresses necessity, often from outside circumstances", "చేయవలసి ఉంది",
     "'Have to' expresses necessity from outside circumstances (a deadline, a rule), and changes to 'has to' for he/she/it."),
    ("day46-obligations-03", 3, "You should drink more water every day.", "మీరు ప్రతిరోజూ ఎక్కువ నీళ్లు తాగాలి.",
     ["/ʃ/ in 'should'"], "should", "expresses advice or recommendation", "సలహా ఇవ్వడం",
     "'Should' gives advice or a recommendation, weaker than 'must' — it's a suggestion, not a strict rule."),
    ("day46-obligations-04", 4, "May I come in?", "నేను లోపలికి రావచ్చా?",
     ["/meɪ/ diphthong in 'may'"], "may", "polite way to ask permission", "అనుమతి అడగడం",
     "'May I ___?' is the most formal, polite way to ask permission, more formal than 'Can I ___?'."),
    ("day46-obligations-05", 5, "You can park your car here.", "మీరు మీ కారును ఇక్కడ పార్క్ చేయవచ్చు.",
     ["/k/ in 'park'", "/r/ in 'car'"], "can (permission)", "used to give permission informally", "అనుమతి ఇవ్వడం",
     "'Can' is used informally to give or ask permission, more casual than the formal 'may'."),
]

DAY47_LESSONS = [
    ("day47-causeeffect-01", 1, "I was late because the bus didn't come on time.", "బస్సు సమయానికి రాకపోవడం వల్ల నేను ఆలస్యంగా వచ్చాను.",
     ["/b/ in 'because'"], "because", "conjunction introducing a reason", "ఎందుకంటే",
     "'Because' introduces the reason for something and is directly followed by a full clause (subject + verb)."),
    ("day47-causeeffect-02", 2, "It was raining heavily, so we stayed at home.", "వర్షం చాలా పడుతోంది, కాబట్టి మేము ఇంట్లోనే ఉండిపోయాం.",
     ["/h/ in 'heavily'"], "so", "conjunction introducing a result", "కాబట్టి",
     "'So' introduces the result or effect, placed after the cause — the opposite direction from 'because'."),
    ("day47-causeeffect-03", 3, "He didn't study, so he failed the exam.", "అతను చదవలేదు, కాబట్టి పరీక్షలో ఫెయిల్ అయ్యాడు.",
     ["/f/ in 'failed'"], "failed", "did not pass", "ఫెయిల్ అవ్వడం",
     "Review of 'so' with a clear cause-effect pair: not studying (cause) and failing (effect)."),
    ("day47-causeeffect-04", 4, "There was heavy traffic. As a result, I missed my train.", "విపరీతమైన ట్రాఫిక్ ఉంది. దాని ఫలితంగా, నేను రైలు మిస్ అయ్యాను.",
     ["/r/ in 'result'", "/z/ in 'as'"], "as a result", "phrase meaning 'because of this'", "దాని ఫలితంగా",
     "'As a result' is a more formal way to connect two separate sentences showing cause and effect."),
    ("day47-causeeffect-05", 5, "I saved money every month, so I could buy a new phone.", "నేను ప్రతి నెలా డబ్బు పొదుపు చేశాను, కాబట్టి కొత్త ఫోన్ కొనగలిగాను.",
     ["/s/ in 'saved'"], "saved (money)", "kept money instead of spending it", "పొదుపు చేయడం",
     "'So' can also connect an action to an ability gained because of it — the cause enables a later result."),
]

DAY48_LESSONS = [
    ("day48-disagree-01", 1, "I see your point, but I think differently.", "మీ అభిప్రాయం అర్థమైంది, కానీ నేను వేరేలా అనుకుంటున్నాను.",
     ["/p/ in 'point'"], "point", "an opinion or idea someone makes", "అభిప్రాయం",
     "'I see your point, but...' politely acknowledges someone's opinion before disagreeing — softer than a direct 'You're wrong'."),
    ("day48-disagree-02", 2, "I'm not sure I agree with that.", "దానితో నేను ఏకీభవిస్తానో లేదో నాకు తెలియదు.",
     ["/ə/ schwa in 'agree'"], "agree", "to have the same opinion", "ఏకీభవించడం",
     "'I'm not sure I agree' is a hedging phrase that disagrees indirectly and politely, common in respectful discussion."),
    ("day48-disagree-03", 3, "Have you considered the cost?", "ఖర్చు గురించి మీరు ఆలోచించారా?",
     ["/k/ vs /s/ in 'considered'"], "considered", "thought carefully about", "పరిగణించడం",
     "'Have you considered ___?' turns a disagreement into a question, making it sound like a suggestion rather than a criticism."),
    ("day48-disagree-04", 4, "I understand, but I see it differently.", "నాకు అర్థమైంది, కానీ నేను దాన్ని వేరేలా చూస్తున్నాను.",
     ["/f/ in 'differently'"], "differently", "in another way", "వేరేలా",
     "'I understand, but...' validates the other person's view first — a common respectful disagreement pattern in English."),
    ("day48-disagree-05", 5, "Let's agree to disagree.", "మన అభిప్రాయాలు వేరుగా ఉన్నాయని ఒప్పుకుందాం.",
     ["/z/ in 'disagree'"], "agree to disagree", "phrase for accepting two people won't share the same opinion", "అభిప్రాయభేదాన్ని అంగీకరించడం",
     "'Let's agree to disagree' is a fixed idiom used to politely end a disagreement without either side losing."),
]

DAY49_LESSONS = [
    ("day49-technology-01", 1, "I'm using my phone to learn English these days.", "ఈ మధ్య నేను ఇంగ్లీష్ నేర్చుకోవడానికి నా ఫోన్‌ను వాడుతున్నాను.",
     ["/z/ in 'using'"], "these days", "phrase meaning 'currently, in the present time period'", "ఈ మధ్య",
     "Present continuous ('I'm using') describes a habit or trend happening around now, common for talking about current tech habits."),
    ("day49-technology-02", 2, "She's video calling her family every weekend.", "ఆమె ప్రతి వారాంతం తన కుటుంబంతో వీడియో కాల్ చేస్తోంది.",
     ["/v/ in 'video'"], "video calling", "making a call with video", "వీడియో కాల్ చేయడం",
     "Present continuous with -ing describes an ongoing repeated action in this period of time, even without 'now' in the sentence."),
    ("day49-technology-03", 3, "We're chatting on WhatsApp right now.", "మేము ఇప్పుడు వాట్సాప్‌లో చాట్ చేస్తున్నాము.",
     ["/tʃ/ in 'chatting'"], "chatting", "having an informal text conversation", "చాట్ చేయడం",
     "'Right now' emphasizes the action is happening at this exact moment, the clearest use of present continuous."),
    ("day49-technology-04", 4, "He's downloading a new app.", "అతను కొత్త యాప్‌ను డౌన్‌లోడ్ చేస్తున్నాడు.",
     ["/d/ in 'downloading'"], "downloading", "getting a file or app from the internet", "డౌన్‌లోడ్ చేయడం",
     "Present continuous describes an action in progress; Telugu speakers often default to present simple even when describing something happening right now."),
    ("day49-technology-05", 5, "I'm not getting good internet signal here.", "నాకు ఇక్కడ మంచి ఇంటర్నెట్ సిగ్నల్ రావడం లేదు.",
     ["/s/ vs /ʃ/ in 'signal'"], "signal", "the strength of a network connection", "సిగ్నల్",
     "Negative present continuous ('I'm not getting') describes a problem currently occurring, not a general fact."),
]

DAY50_LESSONS = [
    ("day50-transport-01", 1, "The bus is running late today.", "బస్సు ఈ రోజు ఆలస్యంగా నడుస్తోంది.",
     ["/r/ in 'running'", "final /t/ cluster in 'late'"], "running late", "behind the expected schedule", "ఆలస్యంగా నడుస్తున్న",
     "'Running late' is a fixed phrase meaning something is behind schedule — don't translate 'running' as physical running."),
    ("day50-transport-02", 2, "The train has been delayed by twenty minutes.", "రైలు ఇరవై నిమిషాలు ఆలస్యమైంది.",
     ["/d/ in 'delayed'"], "delayed", "made to happen later than planned", "ఆలస్యమైన",
     "Present perfect passive ('has been delayed') describes a recent change of state that is still relevant now."),
    ("day50-transport-03", 3, "You need to change buses at the next stop.", "మీరు తర్వాత స్టాప్‌లో బస్సు మార్చుకోవాలి.",
     ["/tʃ/ in 'change'"], "change (buses)", "to switch from one vehicle to another", "బస్సు మార్చుకోవడం",
     "'Need to' + verb expresses necessity, similar to 'have to', commonly used for giving travel instructions."),
    ("day50-transport-04", 4, "We just missed the last bus.", "మేము ఇప్పుడే చివరి బస్సును మిస్ అయ్యాము.",
     ["/s/ in 'missed'"], "missed", "failed to catch something in time", "మిస్ అవ్వడం",
     "'Just' + past tense emphasizes something happened a very short time ago."),
    ("day50-transport-05", 5, "The next bus arrives in ten minutes.", "తర్వాతి బస్సు పది నిమిషాల్లో వస్తుంది.",
     ["/r/ in 'arrives'"], "arrives", "reaches a place, comes", "వస్తుంది",
     "Present simple ('arrives') is used for scheduled future events, just like fixed timetables, even though it refers to the future."),
]

DAY51_LESSONS = [
    ("day51-problems-01", 1, "I have to fix this problem today.", "నేను ఈ సమస్యను ఈ రోజు పరిష్కరించాలి.",
     ["/f/ in 'fix'"], "fix", "to repair or solve something", "పరిష్కరించడం",
     "'have to' expresses obligation — Telugu speakers often drop it and use just the base verb, but English needs 'have to' to show necessity."),
    ("day51-problems-02", 2, "There was a power cut, so I couldn't finish the work.", "కరెంట్ పోయింది, అందుకే నేను పని పూర్తి చేయలేకపోయాను.",
     ["/f/ in 'finish'", "final cluster in \"couldn't\""], "power cut", "a sudden stop in the electricity supply", "కరెంటు పోవడం",
     "'so' links a stated cause to its result — the cause comes first, then 'so' introduces the effect, unlike 'because' which would reverse the order."),
    ("day51-problems-03", 3, "I don't think that's a good idea.", "నాకు అది మంచి ఆలోచనలా అనిపించడం లేదు.",
     ["/ð/ in \"that's\""], "idea", "a plan or suggestion", "ఆలోచన",
     "'I don't think...' softens disagreement — English negates the main verb 'think', not the clause that follows it, unlike a literal word-for-word translation."),
    ("day51-problems-04", 4, "You must call the plumber because the pipe is leaking.", "పైపు లీక్ అవుతోంది కాబట్టి మీరు ప్లంబర్‌కి కాల్ చేయాలి.",
     ["/pl/ cluster in 'plumber'", "/iː/ in 'leaking'"], "leaking", "water escaping through a crack or hole", "లీక్ అవడం/కారడం",
     "'must' shows strong obligation and is followed directly by the base verb with no 'to'; 'because' introduces the reason after the main clause, not before it."),
    ("day51-problems-05", 5, "Let's try a different solution instead.", "మనం వేరే పరిష్కారం ప్రయత్నిద్దాం.",
     ["/s/ cluster in 'solution'", "/ɪ/ in 'different'"], "solution", "a way of solving a problem", "పరిష్కారం",
     "'Let's + base verb' is a fixed pattern for suggesting an action together — never 'let's to try'."),
]

DAY52_LESSONS = [
    ("day52-feelingsdetail-01", 1, "I feel frustrated because the internet is so slow.", "ఇంటర్నెట్ చాలా స్లోగా ఉండటం వల్ల నాకు చిరాకుగా అనిపిస్తోంది.",
     ["/fr/ cluster in 'frustrated'", "/s/ cluster in 'slow'"], "frustrated", "annoyed because you can't do something", "చిరాకు/విసుగు కలిగిన",
     "'I feel + adjective + because + reason' is the standard pattern for explaining an emotion — don't drop 'because' and just place two sentences side by side."),
    ("day52-feelingsdetail-02", 2, "I feel relieved that the exam is finally over.", "పరీక్ష చివరకు అయిపోయినందుకు నాకు ఊరటగా అనిపిస్తోంది.",
     ["/r/ in 'relieved'", "/v/ in 'relieved'"], "relieved", "no longer worried, because a problem has ended", "ఊరట చెందిన",
     "'relieved' describes how you feel about a finished problem — it takes 'that' or 'because' to introduce the reason, unlike an action verb."),
    ("day52-feelingsdetail-03", 3, "She is proud of her son's achievement.", "ఆమె తన కొడుకు సాధించిన విజయం గురించి గర్వపడుతోంది.",
     ["/pr/ cluster in 'proud'", "/aʊ/ in 'proud'"], "proud", "feeling pleased about someone's success", "గర్వం/అభిమానం",
     "'proud' always takes the preposition 'of' — Telugu speakers often drop the preposition entirely."),
    ("day52-feelingsdetail-04", 4, "I was disappointed when the trip got cancelled.", "ట్రిప్ క్యాన్సిల్ అయినప్పుడు నాకు నిరాశ కలిగింది.",
     ["/p/ cluster in 'disappointed'", "/æ/ in 'cancelled'"], "disappointed", "sad because something didn't happen as hoped", "నిరాశ చెందిన",
     "Both verbs stay in the past tense when describing a past feeling and its cause — 'was disappointed when...got cancelled', not a mixed tense."),
    ("day52-feelingsdetail-05", 5, "I feel nervous because I have an interview tomorrow.", "రేపు నాకు ఇంటర్వ్యూ ఉన్నందువల్ల నాకు కంగారుగా ఉంది.",
     ["/v/ in 'nervous'", "/ɜː/ in 'nervous'"], "nervous", "worried or anxious about something coming up", "కంగారు/ఆందోళన",
     "The 'because' clause needs its own subject and verb — don't drop 'I have' and just say 'because interview tomorrow'."),
]

DAY53_LESSONS = [
    ("day53-experience-01", 1, "I have done my homework already.", "నేను నా హోంవర్క్ ఇప్పటికే చేసేశాను.",
     ["/ɔːl/ in 'already'", "/d/ final in 'done'"], "already", "before now, by this time", "ఇప్పటికే",
     "Present perfect ('have done') connects a finished action to now — use it for completed actions with present relevance, not simple past."),
    ("day53-experience-02", 2, "I have been to Hyderabad twice.", "నేను హైదరాబాద్‌కి రెండుసార్లు వెళ్ళాను.",
     ["/tw/ cluster in 'twice'", "/iː/ in 'been'"], "twice", "two times", "రెండుసార్లు",
     "'have been to' is the standard present perfect form for describing a life experience of visiting a place, different from 'have gone to'."),
    ("day53-experience-03", 3, "Have you ever eaten Chinese food?", "మీరు ఎప్పుడైనా చైనీస్ ఫుడ్ తిన్నారా?",
     ["/ev/ in 'ever'", "/tʃ/ in 'Chinese'"], "ever", "at any time (used in questions)", "ఎప్పుడైనా",
     "'ever' is used in present perfect questions to ask about life experience; 'Have' comes before the subject, followed by the past participle."),
    ("day53-experience-04", 4, "I have never seen snow in my life.", "నేను నా జీవితంలో ఎప్పుడూ మంచు చూడలేదు.",
     ["/n/ nasal cluster in 'never'", "/s/ in 'snow'"], "never", "not at any time", "ఎప్పుడూ (లేదు)",
     "'have never + past participle' already carries the negative meaning, so adding 'not' as well creates a double negative error."),
    ("day53-experience-05", 5, "She has just finished her project.", "ఆమె ఇప్పుడే తన ప్రాజెక్ట్ పూర్తి చేసింది.",
     ["/dʒ/ in 'just'", "/ʃ/ in 'finished'"], "just", "a very short time ago", "ఇప్పుడే",
     "'just' goes between 'has/have' and the past participle to show something happened very recently."),
]

DAY54_LESSONS = [
    ("day54-directionsdetail-01", 1, "Turn left at the second signal.", "రెండో సిగ్నల్ దగ్గర ఎడమవైపు తిరగండి.",
     ["/s/ cluster in 'signal'", "/ɜː/ in 'turn'"], "signal", "a traffic light at a road junction", "సిగ్నల్/ట్రాఫిక్ లైట్",
     "Ordinal numbers ('second', 'third') describe the order of turns or landmarks and go directly before the noun, as in 'the second signal'."),
    ("day54-directionsdetail-02", 2, "Go straight until you see the bus stop.", "బస్ స్టాప్ కనిపించే వరకు స్ట్రెయిట్‌గా వెళ్ళండి.",
     ["/str/ cluster in 'straight'", "/s/ in 'stop'"], "bus stop", "a place where buses stop for passengers", "బస్ స్టాప్",
     "'until' marks the point where you should stop the action — use the simple present after it, not 'will' or the past tense."),
    ("day54-directionsdetail-03", 3, "The bank is on your right, next to the pharmacy.", "బ్యాంక్ మీ కుడివైపు, ఫార్మసీ పక్కన ఉంది.",
     ["/f/ in 'pharmacy'", "/r/ in 'right'"], "pharmacy", "a shop that sells medicine", "ఫార్మసీ/మందుల దుకాణం",
     "'next to' is a fixed two-word preposition showing position beside something — both words are required, unlike a dropped 'to'."),
    ("day54-directionsdetail-04", 4, "Take the third left after the temple.", "గుడి దాటిన తర్వాత మూడో ఎడమ మలుపు తీసుకోండి.",
     ["/θ/ in 'third'", "aspirated /t/ in 'temple'"], "temple", "a place of worship", "గుడి/దేవాలయం",
     "'the third left' means the third turning on the left side — ordinal number plus direction word is a fixed pattern for giving directions."),
    ("day54-directionsdetail-05", 5, "You can't miss it — it's the big building on the corner.", "మీరు మిస్ కాలేరు — అది మూలలో ఉన్న పెద్ద భవనం.",
     ["/k/ in 'corner'", "final cluster in \"can't\""], "corner", "the point where two streets meet", "మూల/కూడలి",
     "'You can't miss it' is a fixed idiom meaning something is very easy to find — don't translate it word for word."),
]

DAY55_LESSONS = [
    ("day55-emergencies-01", 1, "Please help, there's been an accident!", "దయచేసి సహాయం చేయండి, ఒక ప్రమాదం జరిగింది!",
     ["/æ/ in 'accident'", "/h/ in 'help'"], "accident", "an unexpected event that causes harm or damage", "ప్రమాదం",
     "'There's been a/an + noun' (present perfect of 'there is') is the standard way to announce that an emergency has just happened."),
    ("day55-emergencies-02", 2, "Call an ambulance right now!", "వెంటనే అంబులెన్స్‌కి కాల్ చేయండి!",
     ["/æ/ in 'ambulance'", "/r/ in 'right'"], "ambulance", "a vehicle that takes sick or injured people to hospital", "అంబులెన్స్",
     "Imperative sentences drop the subject 'you' and start directly with the base verb, giving an urgent command."),
    ("day55-emergencies-03", 3, "Someone fainted, please bring water quickly.", "ఎవరో మూర్ఛపోయారు, దయచేసి త్వరగా నీళ్ళు తీసుకురండి.",
     ["/f/ in 'fainted'", "final cluster in 'fainted'"], "fainted", "suddenly lost consciousness", "మూర్ఛపోవడం/స్పృహ కోల్పోవడం",
     "'Someone + past tense verb' reports a sudden event quickly and directly — extra words slow down an emergency message."),
    ("day55-emergencies-04", 4, "Watch out, the floor is wet!", "జాగ్రత్త, నేల తడిగా ఉంది!",
     ["/w/ vs /v/ in 'watch' and 'wet'"], "watch out", "a warning to be careful of danger", "జాగ్రత్త",
     "'Watch out' is a fixed warning phrase, more urgent and immediate than simply saying 'be careful'."),
    ("day55-emergencies-05", 5, "I need help immediately, it's an emergency!", "నాకు వెంటనే సహాయం కావాలి, ఇది ఒక అత్యవసర పరిస్థితి!",
     ["/ɪ/ in 'immediately'", "/dʒ/ in 'emergency'"], "emergency", "a serious situation needing immediate action", "అత్యవసర పరిస్థితి",
     "The adverb 'immediately' follows the main clause 'I need help' for natural emphasis — the adjective form 'immediate' cannot modify a verb this way."),
]

DAY56_LESSONS = [
    ("day56-weatherdetail-01", 1, "Summer is hotter than winter here.", "ఇక్కడ చలికాలం కంటే వేసవి ఎక్కువ వేడిగా ఉంటుంది.",
     ["/h/ in 'hotter'", "/θ/ in 'than'"], "hotter", "having a higher temperature (comparative of hot)", "ఎక్కువ వేడి",
     "Short adjectives form comparatives with '-er' + 'than' — never 'more hot than'."),
    ("day56-weatherdetail-02", 2, "It's supposed to rain this evening.", "ఈ సాయంత్రం వర్షం పడే అవకాశం ఉంది.",
     ["/s/ cluster in 'supposed'", "/r/ in 'rain'"], "supposed to", "expected to happen, according to a forecast or plan", "అయ్యే అవకాశం ఉంది",
     "'It's supposed to + verb' reports an expectation, not a certainty — it's the natural way to talk about weather forecasts."),
    ("day56-weatherdetail-03", 3, "This monsoon is wetter than last year's.", "ఈ వర్షాకాలం గత సంవత్సరం కంటే ఎక్కువ వర్షంగా ఉంది.",
     ["/w/ vs /v/ in 'wetter'", "/uː/ in 'monsoon'"], "monsoon", "the rainy season", "వర్షాకాలం/రుతుపవనాలు",
     "Comparatives need 'than' after the adjective — it's often dropped in a direct word-for-word translation."),
    ("day56-weatherdetail-04", 4, "Winter mornings are colder than winter evenings.", "చలికాలంలో సాయంత్రాల కంటే ఉదయాలు ఎక్కువ చల్లగా ఉంటాయి.",
     ["final cluster in 'colder'", "/ɔː/ in 'mornings'"], "colder", "having a lower temperature (comparative of cold)", "ఎక్కువ చల్లని",
     "The comparative pattern 'A is colder than B' needs both sides of the comparison clearly stated."),
    ("day56-weatherdetail-05", 5, "The weather forecast says it will be sunny tomorrow.", "వాతావరణ సూచన ప్రకారం రేపు ఎండగా ఉంటుంది.",
     ["/f/ in 'forecast'", "/s/ in 'sunny'"], "forecast", "a prediction of future weather", "వాతావరణ సూచన",
     "Weather predictions use 'will be' + adjective — 'will' must be followed by 'be' before an adjective like 'sunny'."),
]

DAY57_LESSONS = [
    ("day57-etiquette-01", 1, "Could you please pass the salt?", "దయచేసి ఉప్పు అందించగలరా?",
     ["/k/ in 'could'", "/s/ cluster in 'salt'"], "could you please", "a polite way to make a request", "దయచేసి ...గలరా",
     "'Could you please + verb?' is more polite and formal than 'Can you' — the natural choice with elders or in formal settings."),
    ("day57-etiquette-02", 2, "Would you mind if I sat here?", "నేను ఇక్కడ కూర్చుంటే మీకు అభ్యంతరం లేదు కదా?",
     ["/w/ in 'would'", "final cluster in 'mind'"], "would you mind", "a very polite way to ask permission", "మీకు అభ్యంతరం లేదు కదా",
     "'Would you mind if I + past tense verb?' is an extra-polite request form — the verb after 'if I' stays in past tense even though it refers to the present."),
    ("day57-etiquette-03", 3, "Please call me 'uncle' — no need for formalities.", "దయచేసి నన్ను 'అంకుల్' అని పిలవండి — ఫార్మాలిటీలు అవసరం లేదు.",
     ["/f/ in 'formalities'", "/l/ in 'call'"], "formalities", "polite but unnecessary formal behavior", "లాంఛనాలు/ఫార్మాలిటీలు",
     "'No need for + noun' is a short, polite way to tell someone to relax formal manners."),
    ("day57-etiquette-04", 4, "Excuse me, sir, may I ask you something?", "క్షమించండి సార్, నేను మిమ్మల్ని ఏదైనా అడగవచ్చా?",
     ["/s/ in 'sir'", "/ks/ cluster in 'excuse'"], "sir", "a respectful, formal way to address a man", "సార్ (గౌరవంగా పిలిచే మాట)",
     "'May I + verb?' is the most formal way to ask permission — preferred over 'Can I' when addressing elders or strangers respectfully."),
    ("day57-etiquette-05", 5, "Thank you for your time, I really appreciate it.", "మీ సమయానికి ధన్యవాదాలు, నేను దీన్ని నిజంగా మెచ్చుకుంటున్నాను.",
     ["/θ/ in 'thank'", "/ʃ/ in 'appreciate'"], "appreciate", "to be grateful for something", "కృతజ్ఞత తెలుపడం/మెచ్చుకోవడం",
     "'I really appreciate it' is a fixed polite closing phrase — 'it' refers back to the favor already mentioned, so don't drop it."),
]

DAY58_LESSONS = [
    ("day58-gathering-01", 1, "I felt so proud when my niece got her first job.", "నా మేనకోడలు మొదటి ఉద్యోగం సంపాదించినప్పుడు నాకు చాలా గర్వంగా అనిపించింది.",
     ["/pr/ cluster in 'proud'", "/dʒ/ in 'job'"], "niece", "the daughter of your brother or sister", "మేనకోడలు",
     "'felt + adjective + when...' reports a past feeling connected to a past event — both verbs stay in past tense to describe a memory."),
    ("day58-gathering-02", 2, "Could you please pass the sweets to grandmother first?", "దయచేసి తీపి పదార్థాలను ముందు నానమ్మకు అందించగలరా?",
     ["/s/ cluster in 'sweets'", "final cluster in 'first'"], "sweets", "sugary food items served on special occasions", "తీపి పదార్థాలు",
     "This reuses the polite 'Could you please...' request form from etiquette, with 'first' politely signalling who should be served before others."),
    ("day58-gathering-03", 3, "Someone spilled juice on the carpet — please bring a cloth quickly.", "ఎవరో కార్పెట్ మీద జ్యూస్ చిందించారు — దయచేసి త్వరగా ఒక గుడ్డ తీసుకురండి.",
     ["/s/ cluster in 'spilled'", "final cluster in 'spilled'"], "spilled", "accidentally poured out (a liquid)", "చిందించడం",
     "'Someone + past tense verb' quickly reports what happened — the same urgent-report pattern reused from emergencies, scaled down to a small household mishap."),
    ("day58-gathering-04", 4, "We were all relieved when the power came back during the party.", "పార్టీలో కరెంటు తిరిగి వచ్చినప్పుడు మేమందరం ఊరటగా భావించాము.",
     ["/r/ in 'relieved'", "/p/ in 'power'"], "came back", "returned after being away or stopped", "తిరిగి వచ్చింది",
     "'were relieved when...' reuses the 'feel + adjective' feelings pattern from Day 52, shifted fully into the past for storytelling."),
    ("day58-gathering-05", 5, "Excuse me, uncle, would you like some more rice?", "క్షమించండి అంకుల్, మీకు ఇంకొంచెం అన్నం కావాలా?",
     ["/w/ in 'would'", "/aɪ/ in 'like'"], "would you like", "a polite way to offer something", "మీకు కావాలా (మర్యాదపూర్వకంగా అడగడం)",
     "'Would you like + noun?' is the polite way to offer food, reused from etiquette — more formal than 'Do you want'."),
]

DAY59_LESSONS = [
    ("day59-goals-01", 1, "I'm planning to learn English fluently this year.", "ఈ సంవత్సరం నేను ఇంగ్లీష్ ఫ్లుయెంట్‌గా నేర్చుకోవాలని అనుకుంటున్నాను.",
     ["/fl/ cluster in 'fluently'", "/pl/ cluster in 'planning'"], "fluently", "speaking smoothly and easily", "అనర్గళంగా/ఫ్లుయెంట్‌గా",
     "'I'm planning to + verb' expresses a definite future intention and is always followed by the base verb with 'to'."),
    ("day59-goals-02", 2, "I hope to get a better job next year.", "వచ్చే సంవత్సరం మంచి ఉద్యోగం వస్తుందని ఆశిస్తున్నాను.",
     ["/h/ in 'hope'", "/dʒ/ in 'job'"], "hope", "to want something to happen in the future", "ఆశించడం",
     "'I hope to + verb' expresses a wish about the future, softer than 'planning to' — always followed by 'to' plus the base verb, not '-ing'."),
    ("day59-goals-03", 3, "My goal is to save money for a new house.", "నా లక్ష్యం కొత్త ఇంటి కోసం డబ్బు దాచుకోవడం.",
     ["/s/ cluster in 'save'", "/g/ in 'goal'"], "save", "to keep money instead of spending it", "దాచుకోవడం/పొదుపు చేయడం",
     "'My goal is to + verb' states a clear objective — the verb after 'is to' stays in its base form."),
    ("day59-goals-04", 4, "I'm determined to improve my pronunciation.", "నా ఉచ్చారణను మెరుగుపరచాలని నేను గట్టిగా నిర్ణయించుకున్నాను.",
     ["/d/ in 'determined'", "final cluster in 'improved'"], "determined", "having a strong intention to succeed at something", "దృఢ నిశ్చయం కలిగిన",
     "'I'm determined to + verb' shows strong personal commitment, stronger than 'planning to'."),
    ("day59-goals-05", 5, "By next year, I will have finished this course.", "వచ్చే సంవత్సరం నాటికి, నేను ఈ కోర్సును పూర్తి చేసి ఉంటాను.",
     ["/f/ in 'finished'", "/k/ in 'course'"], "by next year", "before or at the point of next year", "వచ్చే సంవత్సరం నాటికి",
     "'will have + past participle' (future perfect) shows an action completed before a specific future point in time."),
]

DAY60_LESSONS = [
    ("day60-capstone-01", 1, "I usually go for a walk every morning, but I haven't had time this week because I've been so busy.", "నేను సాధారణంగా ప్రతి ఉదయం వాకింగ్‌కి వెళ్తాను, కానీ ఈ వారం చాలా బిజీగా ఉన్నందువల్ల నాకు సమయం దొరకలేదు.",
     ["/w/ in 'walk'", "/z/ in 'busy'"], "haven't had", "have not experienced or found (present perfect negative)", "దొరకలేదు (ఇప్పటివరకు)",
     "This mixes a habitual present ('I usually go') with present perfect ('haven't had... because I've been') to contrast a regular routine with a recent change — a common pattern in natural, connected speech."),
    ("day60-capstone-02", 2, "You should see a doctor because you've had a cough for three days now.", "మీకు మూడు రోజులుగా దగ్గు ఉన్నందున మీరు డాక్టర్‌ని చూడాలి.",
     ["/ʃ/ in 'should'", "/f/ in 'cough'"], "for three days", "a duration continuing up to now", "మూడు రోజులుగా",
     "'have had + for + duration' shows something started in the past and continues now, combined here with 'should' for advice — a very natural spoken pattern."),
    ("day60-capstone-03", 3, "I have to finish this report today, even though I'm exhausted and I'd rather rest.", "నేను చాలా అలసిపోయినా, విశ్రాంతి తీసుకోవాలనిపించినా, ఈ రిపోర్ట్‌ను ఈ రోజే పూర్తి చేయాలి.",
     ["/ɪɡˈzɔːstɪd/ in 'exhausted'", "/r/ in 'rather'"], "exhausted", "extremely tired", "బాగా అలసిపోయిన",
     "'even though' introduces a contrast within one sentence, linking obligation ('have to') with a feeling ('exhausted') — it joins two true but conflicting ideas."),
    ("day60-capstone-04", 4, "If I were you, I'd apologize, because you've hurt her feelings and she's been upset since yesterday.", "నేను నీ స్థానంలో ఉంటే, క్షమాపణ చెప్తాను, ఎందుకంటే నువ్వు ఆమె మనసు నొప్పించావు, నిన్నటి నుండి ఆమె బాధగా ఉంది.",
     ["/w/ in 'were'", "/dʒ/ in 'apologize'"], "apologize", "to say sorry for something", "క్షమాపణ చెప్పడం",
     "'If I were you, I'd...' gives hypothetical advice, combined here with present perfect ('have hurt') and 'since' for an ongoing feeling — the kind of longer, connected sentence fluent speakers naturally produce."),
    ("day60-capstone-05", 5, "I've never felt so proud, because after months of practice, I can finally speak English confidently.", "నెలల తరబడి ప్రాక్టీస్ చేసిన తర్వాత, నేను ఇప్పుడు ఇంగ్లీష్ నమ్మకంగా మాట్లాడగలుగుతున్నాను, అందుకే నాకు ఇంత గర్వంగా ఎప్పుడూ అనిపించలేదు.",
     ["/pr/ cluster in 'proud' and 'practice'", "/f/ in 'confidently'"], "confidently", "in a way that shows self-assurance", "నమ్మకంగా/ధైర్యంగా",
     "This links present perfect ('I've never felt'), a time phrase ('after months of practice'), and a result clause ('I can finally speak') — the kind of longer, multi-clause sentence fluent speakers naturally produce."),
]

DAYS = [
    ("day-31-habits", "B1", "Talking About Habits & Routines", DAY31_LESSONS),
    ("day-32-neighborhood", "B1", "Describing Your Neighborhood", DAY32_LESSONS),
    ("day-33-complaints", "B1", "Making Complaints Politely", DAY33_LESSONS),
    ("day-34-advice", "B1", "Giving Advice & Suggestions", DAY34_LESSONS),
    ("day-35-wellbeing", "B1", "Health & Wellbeing Habits", DAY35_LESSONS),
    ("day-36-jobinterview", "B1", "Talking About Your Job & Experience", DAY36_LESSONS),
    ("day-37-recap", "A2/B1", "Talking About Your Week (Week 6 review)", DAY37_LESSONS),
    ("day-38-preferences", "B1", "Likes, Dislikes & Preferences", DAY38_LESSONS),
    ("day-39-pastdetail", "B1", "Talking About the Past in Detail", DAY39_LESSONS),
    ("day-40-invitations", "B1", "Making & Responding to Invitations", DAY40_LESSONS),
    ("day-41-process", "B1", "Explaining How to Do Something", DAY41_LESSONS),
    ("day-42-phonecalls", "B1", "Phone Calls — Leaving a Message", DAY42_LESSONS),
    ("day-43-bargaining", "B1", "Bargaining & Talking About Prices", DAY43_LESSONS),
    ("day-44-weekend", "A2/B1", "Planning a Weekend Trip (Week 7 review)", DAY44_LESSONS),
    ("day-45-hopes", "B1", "Hopes, Wishes & Plans", DAY45_LESSONS),
    ("day-46-obligations", "B1", "Rules & Obligations", DAY46_LESSONS),
    ("day-47-causeeffect", "B1", "Explaining Reasons — Cause & Effect", DAY47_LESSONS),
    ("day-48-disagree", "B1", "Handling Disagreements Respectfully", DAY48_LESSONS),
    ("day-49-technology", "B1", "Technology & the Internet", DAY49_LESSONS),
    ("day-50-transport", "B1", "Public Transport & Travel Logistics", DAY50_LESSONS),
    ("day-51-problems", "A2/B1", "Everyday Problems & Solutions (Week 8 review)", DAY51_LESSONS),
    ("day-52-feelingsdetail", "B1", "Describing Feelings in Detail", DAY52_LESSONS),
    ("day-53-experience", "B1", "Talking About Achievements", DAY53_LESSONS),
    ("day-54-directionsdetail", "B1", "Giving Detailed Directions", DAY54_LESSONS),
    ("day-55-emergencies", "B1", "Handling Emergencies", DAY55_LESSONS),
    ("day-56-weatherdetail", "B1", "Weather & Seasons in Depth", DAY56_LESSONS),
    ("day-57-etiquette", "B1", "Social Etiquette & Manners", DAY57_LESSONS),
    ("day-58-gathering", "A2/B1", "A Family Gathering (Week 9 review)", DAY58_LESSONS),
    ("day-59-goals", "B1", "Future Goals & Ambitions", DAY59_LESSONS),
    ("day-60-capstone", "B1/B2", "Level 2 Capstone — Confident Everyday Conversations", DAY60_LESSONS),
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
    "quiz-day-31": {
        "track": "day-31-habits", "title": "Day 31 Quiz — Habits & Routines", "xpReward": 30,
        "questions": [
            ("Which sentence is correct?", ["I used to play cricket every evening.", "I use to play cricket every evening.", "I used to played cricket every evening.", "I am used to play cricket every evening."], 0,
             "'used to + base verb' is the correct structure for a past habit that has stopped."),
            ("Correct way to complete: 'I ___ wake up at six.'", ["usually", "usual", "use to", "using"], 0,
             "'usually' is the frequency adverb used to describe a regular routine in simple present."),
            ("Correct way to say she doesn't live there anymore:", ["She used to live in a village.", "She uses to live in a village.", "She used to living in a village.", "She living in a village before."], 0,
             "'used to' takes the base form of the verb ('live'), not '-ing' or 's'."),
            ("Which sentence is correct?", ["We don't watch TV much these days.", "We not watch TV much these days.", "We didn't watch TV much these days now.", "We don't watching TV much these days."], 0,
             "Negative present habits use 'don't/doesn't + base verb'."),
            ("Correct way to say a habit he stopped:", ["He used to smoke, but he quit.", "He use to smoke, but he quit.", "He was smoking, but he quit.", "He smokes before, but he quit."], 0,
             "'used to' correctly marks the discontinued past habit before the change described by 'quit'."),
        ],
    },
    "quiz-day-32": {
        "track": "day-32-neighborhood", "title": "Day 32 Quiz — Describing Your Neighborhood", "xpReward": 30,
        "questions": [
            ("Correct way to describe a market near your house:", ["There is a small market near my house.", "There is small market near my house.", "Near my house there small market.", "A small market there is near my house."], 0,
             "Singular 'There is' requires the article 'a' before a singular countable noun."),
            ("Correct way to complete: '___ many trees on our street.'", ["There are", "There is", "It has", "There has"], 0,
             "The plural noun 'trees' requires 'There are', not the singular 'There is'."),
            ("Which sentence correctly describes a place?", ["It's a quiet area with friendly neighbors.", "It's quiet area with friendly neighbors.", "It is a quiet area with friendly neighbors have.", "Is a quiet area with friendly neighbors."], 0,
             "The singular noun 'area' needs the article 'a' after 'It's'."),
            ("Correct way to say something is nearby:", ["The bus stop is very close to my home.", "The bus stop is very close my home.", "The bus stop is very close for my home.", "The bus stop is very closes to my home."], 0,
             "'close to' is the fixed preposition phrase for proximity — 'to' cannot be dropped."),
            ("Correct negative sentence:", ["There isn't a hospital in our neighborhood.", "There isn't hospital in our neighborhood.", "There not a hospital in our neighborhood.", "There aren't a hospital in our neighborhood."], 0,
             "The singular negative form is 'There isn't a ___', with the article 'a' before the noun."),
        ],
    },
    "quiz-day-33": {
        "track": "day-33-complaints", "title": "Day 33 Quiz — Polite Complaints", "xpReward": 30,
        "questions": [
            ("Polite way to point out a problem:", ["I'm afraid there's a problem with my order.", "There is problem with my order.", "My order has problem, fix it.", "Problem is there in my order."], 0,
             "'I'm afraid there's a problem with ___' is the natural, softened way to raise an issue."),
            ("Polite request to fix something quickly:", ["Could you please fix this as soon as possible?", "You fix this as soon as possible?", "Could you fix this fast, please now?", "Please you fix this as soon as possible."], 0,
             "'Could you please ___?' is the standard polite request structure."),
            ("Polite way to point out a billing error:", ["Excuse me, I think there's a mistake in the bill.", "Excuse me, bill has mistake.", "You made mistake in bill, excuse me.", "Excuse me, in bill mistake is there."], 0,
             "'I think there's a mistake in ___' softens the claim rather than directly accusing someone."),
            ("Which sentence correctly points out a wrong order politely?", ["This isn't what I ordered, could you check again?", "This is not what I order, check again you?", "I ordered not this, check again could you?", "This isn't what I order, could you checked again?"], 0,
             "The correct past tense 'ordered' and the polite question form 'could you check' make this the natural sentence."),
            ("Polite opener before a complaint about noise:", ["I'm sorry to bother you, but the room is too noisy.", "Sorry bothering you, room too noisy.", "I sorry to bother you, but room is noisy too.", "I'm sorry bother you, but the room too noisy is."], 0,
             "'I'm sorry to bother you, but ___' is the correct, complete softening phrase before a complaint."),
        ],
    },
    "quiz-day-34": {
        "track": "day-34-advice", "title": "Day 34 Quiz — Giving Advice", "xpReward": 30,
        "questions": [
            ("Correct way to give advice:", ["You should drink more water every day.", "You should to drink more water every day.", "You should drinking more water every day.", "You should drinks more water every day."], 0,
             "'should' is followed directly by the base verb, with no 'to' and no '-s' or '-ing'."),
            ("Correct suggestion:", ["Why don't you try a new job?", "Why you don't try a new job?", "Why don't you to try a new job?", "Why not you try a new job?"], 0,
             "'Why don't you + base verb?' is the correct fixed suggestion form."),
            ("Which sentence uses 'could' correctly for a suggestion?", ["You could ask your doctor for advice.", "You could to ask your doctor for advice.", "You could asking your doctor for advice.", "You could asked your doctor for advice."], 0,
             "The modal 'could' is followed directly by the base verb, with no 'to'."),
            ("Correct negative advice:", ["You shouldn't skip breakfast every morning.", "You don't should skip breakfast every morning.", "You shouldn't to skip breakfast every morning.", "You not should skip breakfast every morning."], 0,
             "'shouldn't + base verb' is the correct negative advice form."),
            ("Correct conditional advice sentence:", ["If I were you, I would save some money every month.", "If I was you, I would save some money every month.", "If I were you, I will save some money every month.", "If I am you, I would save some money every month."], 0,
             "This hypothetical advice pattern uses 'were' for all subjects, paired with 'would' in the result clause."),
        ],
    },
    "quiz-day-35": {
        "track": "day-35-wellbeing", "title": "Day 35 Quiz — Health & Wellbeing", "xpReward": 30,
        "questions": [
            ("Correct way to say a wellness goal:", ["I try to exercise three times a week.", "I try exercise three times a week.", "I trying to exercise three times a week.", "I try to exercising three times a week."], 0,
             "'try to + base verb' is the correct structure — 'to' cannot be dropped."),
            ("Correct placement of the frequency adverb:", ["I rarely eat junk food.", "I eat rarely junk food.", "Rarely I eat junk food always.", "I eat junk food rarely never."], 0,
             "Frequency adverbs like 'rarely' are placed before the main verb in simple present."),
            ("Which sentence is correct?", ["I always drink water before breakfast.", "I drink always water before breakfast.", "Always I drink water before breakfast time.", "I always drinking water before breakfast."], 0,
             "'always' goes before the main verb 'drink', not between the verb and its object."),
            ("Correct fixed phrase for evening exercise:", ["I sometimes go for a walk in the evening.", "I sometimes go for walking in the evening.", "I sometimes go to walk in the evening.", "I sometimes going for a walk in the evening."], 0,
             "'go for a walk' is the correct fixed collocation for this activity."),
            ("Correct way to avoid a double negative:", ["I never skip my medicine.", "I don't never skip my medicine.", "I never don't skip my medicine.", "I no never skip my medicine."], 0,
             "'never' is already negative, so adding 'don't' creates an incorrect double negative."),
        ],
    },
    "quiz-day-36": {
        "track": "day-36-jobinterview", "title": "Day 36 Quiz — Job & Experience", "xpReward": 30,
        "questions": [
            ("Correct way to describe work experience:", ["I have worked as a teacher for five years.", "I worked as a teacher since five years.", "I have work as a teacher for five years.", "I am working as a teacher for five years before."], 0,
             "Present perfect 'have worked ... for' correctly links past duration to now; 'since' pairs with a starting point, not a duration."),
            ("Correct way to say no past experience:", ["I have never worked in sales before.", "I never have worked in sales before.", "I have never work in sales before.", "I didn't never worked in sales before."], 0,
             "Present perfect negative experience uses 'have never + past participle'."),
            ("Correct question about experience:", ["Have you ever managed a team?", "Did you ever managed a team?", "You have ever managed a team?", "Have you ever manage a team?"], 0,
             "'Have you ever + past participle?' is the correct present perfect question form."),
            ("Correct way to mention a recent achievement:", ["She has recently completed a computer course.", "She has recently complete a computer course.", "She recently completing a computer course.", "She have recently completed a computer course."], 0,
             "The subject 'She' requires 'has' (not 'have'), followed by the past participle 'completed'."),
            ("Correct negative sentence with 'yet':", ["I haven't received any response from them yet.", "I haven't receive any response from them yet.", "I don't received any response from them yet.", "I haven't received any response from them already."], 0,
             "Present perfect negative uses 'haven't + past participle', with 'yet' at the end for something still expected."),
        ],
    },
    "quiz-day-37": {
        "track": "day-37-recap", "title": "Day 37 Quiz — Talking About Your Week", "xpReward": 30,
        "questions": [
            ("Correct way to talk about a finished past action:", ["Last week, I visited my parents in the village.", "Last week, I visit my parents in the village.", "Last week, I have visited my parents in the village.", "Last week, I visiting my parents in the village."], 0,
             "'Last week' signals a finished time, which requires simple past tense, not present perfect."),
            ("Correct sentence using irregular past tense:", ["On Monday, I had a problem with my landlord.", "On Monday, I have a problem with my landlord.", "On Monday, I haved a problem with my landlord.", "On Monday, I having a problem with my landlord."], 0,
             "'had' is the correct irregular past tense form of 'have'."),
            ("Correct way to sequence past events:", ["Then I asked him for advice about it.", "Then I ask him for advice about it.", "I then asking him for advice about it.", "Then I asked he for advice about it."], 0,
             "'Then' introduces the next past action, and 'him' (object pronoun) correctly follows the verb 'asked'."),
            ("Correct sequencing phrase for a narrative:", ["After that, I felt much better about the situation.", "After that, I feel much better about the situation.", "After that, I felted much better about the situation.", "That after, I felt much better about the situation."], 0,
             "'felt' is the correct irregular past tense form of 'feel', following the sequencing phrase 'After that'."),
            ("Correct way to conclude a past narrative:", ["By the end of the week, everything was fine again.", "By the end of the week, everything were fine again.", "By the end of the week, everything is fine again.", "By end of the week, everything was fine again."], 0,
             "'everything' is singular and takes 'was' in past tense."),
        ],
    },
    "quiz-day-38": {
        "track": "day-38-preferences", "title": "Day 38 Quiz — Likes & Preferences", "xpReward": 30,
        "questions": [
            ("Correct way to express a preference:", ["I'd rather stay home tonight.", "I'd rather to stay home tonight.", "I'd rather staying home tonight.", "I rather stay home tonight."], 0,
             "'would rather' is followed directly by the base verb, with no 'to'."),
            ("Correct comparison structure:", ["I prefer tea to coffee.", "I prefer tea than coffee.", "I prefer tea more coffee.", "I prefer tea from coffee."], 0,
             "'prefer' pairs with 'to' for comparisons, not 'than'."),
            ("Correct way to compare two activities:", ["I prefer reading books to watching movies.", "I prefer read books to watch movies.", "I prefer reading books than watching movies.", "I prefer to reading books to watching movies."], 0,
             "After 'prefer', both activities take the gerund (-ing) form, compared using 'to'."),
            ("Correct question form for preference:", ["Would you rather have tea or coffee?", "Would you rather to have tea or coffee?", "Do you rather have tea or coffee?", "Would you rather having tea or coffee?"], 0,
             "'Would you rather + base verb ... or ...?' is the correct question form for preference."),
            ("Polite way to express dislike:", ["I don't like spicy food very much.", "I no like spicy food very much.", "I don't liking spicy food very much.", "I am not liking spicy food very much."], 0,
             "'don't like ___ very much' correctly softens the dislike using simple present negative."),
        ],
    },
    "quiz-day-39": {
        "track": "day-39-pastdetail", "title": "Day 39 Quiz — Past in Detail", "xpReward": 30,
        "questions": [
            ("Correct way to start a sequence of past actions:", ["First, I woke up and made breakfast.", "First, I wake up and made breakfast.", "First, I woke up and make breakfast.", "First, I waked up and made breakfast."], 0,
             "'woke' is the correct irregular past of 'wake', matching the past tense 'made'."),
            ("Correct sequencing sentence:", ["Then, I went to the market to buy vegetables.", "Then, I go to the market to buy vegetables.", "Then, I goed to the market to buy vegetables.", "Then, I went to the market for buy vegetables."], 0,
             "'went' is the correct irregular past of 'go', followed by 'to buy' to express purpose."),
            ("Correct way to continue a past narrative:", ["After that, I cooked lunch for my family.", "After that, I cook lunch for my family.", "That after, I cooked lunch for my family.", "After that, I cooking lunch for my family."], 0,
             "'After that' is the correct sequencing phrase, followed by the regular past tense verb 'cooked'."),
            ("Correct sentence with irregular past tense:", ["Later, I met my friend at the tea stall.", "Later, I meet my friend at the tea stall.", "Later, I meeted my friend at the tea stall.", "Later, I was meet my friend at the tea stall."], 0,
             "'met' is the correct irregular past tense form of 'meet'."),
            ("Correct way to end a past narrative:", ["Finally, I came back home in the evening.", "Finally, I come back home in the evening.", "Finally, I comed back home in the evening.", "Final, I came back home in the evening."], 0,
             "'came' is the correct irregular past tense form of 'come', following the sequencing word 'Finally'."),
        ],
    },
    "quiz-day-40": {
        "track": "day-40-invitations", "title": "Day 40 Quiz — Invitations", "xpReward": 30,
        "questions": [
            ("Polite way to invite someone:", ["Would you like to join us for dinner?", "Would you like join us for dinner?", "Do you like to join us for dinner?", "Would you like to joining us for dinner?"], 0,
             "'Would you like to + base verb?' is the correct polite invitation form."),
            ("Enthusiastic way to accept an invitation:", ["I'd love to, thank you.", "I love to, thank you.", "I'd loving to, thank you.", "I'd love, thank you."], 0,
             "'I'd love to' (short for 'I would love to') is the correct, complete way to accept enthusiastically."),
            ("Polite way to decline an invitation:", ["I'm sorry, I can't make it this time.", "I'm sorry, I can't do it this time.", "I'm sorry, I no can make it this time.", "I'm sorry, I can't made it this time."], 0,
             "'can't make it' is the fixed idiom meaning unable to attend."),
            ("Correct way to suggest a meeting time:", ["Shall we meet at seven o'clock?", "Shall we meeting at seven o'clock?", "We shall meet at seven o'clock?", "Shall we to meet at seven o'clock?"], 0,
             "'Shall we + base verb?' is the correct form for suggesting a plan together."),
            ("Polite way to decline while thanking someone:", ["Thanks for inviting me, but I already have plans.", "Thanks for invite me, but I already have plans.", "Thanks to invite me, but I already have plans.", "Thanks for inviting me, but I already had plans."], 0,
             "The preposition 'for' must be followed by the gerund 'inviting', and 'have plans' correctly describes a current commitment."),
        ],
    },
    "quiz-day-41": {
        "track": "day-41-process", "title": "Day 41 Quiz — Explaining a Process", "xpReward": 30,
        "questions": [
            ("Which sentence gives instructions correctly?", ["First, boil the water.", "First, you are boiling the water.", "First boiling the water.", "First, water boil."], 0,
             "Instructions use the bare imperative verb form, without a subject or -ing."),
            ("Correct way to sequence steps:", ["First, wash the vegetables. Next, you cut them.", "First wash the vegetables next cut them and", "First, wash the vegetables. Next, cut them.", "Washing vegetables first, cutting next."], 2,
             "Sequencing words like 'first' and 'next' introduce each imperative step without a subject."),
            ("___, add the tea leaves to the boiling water.", ["Nexting", "Next", "The next", "Is next"], 1,
             "'Next' is the correct sequencing adverb; it doesn't take an article or -ing form."),
            ("Which is the correct final step in a recipe?", ["Finally, strain it into a cup.", "Final, strain it into a cup.", "At final, strain it into a cup.", "Finally strain into a cup it."], 0,
             "'Finally' (adverb) correctly introduces the last step, followed by normal verb-object word order."),
            ("Which sentence is correct?", ["Let it boiling for two minutes.", "Let it to boil for two minutes.", "Let boil it for two minutes.", "Let it boil for two minutes."], 3,
             "'Let it + base verb' is the correct structure — no 'to' and no -ing after 'let'."),
        ],
    },
    "quiz-day-42": {
        "track": "day-42-phonecalls", "title": "Day 42 Quiz — Phone Messages", "xpReward": 30,
        "questions": [
            ("Polite way to ask to leave a message:", ["I leave a message can?", "Could I leave a message, please?", "Could I left a message?", "Leaving a message I could?"], 1,
             "'Could I ___?' followed by the base verb is the polite question form."),
            ("Which sentence is correct?", ["He's not available right now.", "He's not availability right now.", "He not available right now.", "He isn't available now not."], 0,
             "'Available' is the correct adjective form, used with the contracted auxiliary 'He's not'."),
            ("Correct way to promise a return call:", ["I call you back will later.", "I will calling you back later.", "I'll call you back later.", "I back call you will later."], 2,
             "'Will' + base verb ('call') is the correct future form for a spontaneous promise."),
            ("Please ___ the line for a moment.", ["hold", "holding", "to hold", "holds"], 0,
             "Imperative instructions use the base verb form, so 'hold' is correct."),
            ("Polite way to point out a mistaken number:", ["You have wrong number, I think.", "I think you have the wrong number.", "Wrong number you have, I think.", "I think you have wrong the number."], 1,
             "'I think you have the wrong number' uses correct word order with the article 'the' before 'wrong number'."),
        ],
    },
    "quiz-day-43": {
        "track": "day-43-bargaining", "title": "Day 43 Quiz — Bargaining & Prices", "xpReward": 30,
        "questions": [
            ("Polite way to ask for a lower price:", ["Could you lower the price a little?", "Could you low the price a little?", "Could you lowering the price?", "You could lower the price a little?"], 0,
             "'Lower' is the correct verb form after 'could you', and question word order places 'could' before the subject."),
            ("Which sentence is correct?", ["This one is more cheap than that one.", "This one is cheaper that that one.", "This one cheaper is than that one.", "This one is cheaper than that one."], 3,
             "'Cheaper' is the correct one-word comparative for the short adjective 'cheap', followed by 'than'."),
            ("This shirt is ___ expensive for me.", ["so much", "too", "very much", "much too much"], 1,
             "'Too' + adjective means more than acceptable, the natural way to say something is beyond a limit."),
            ("Correct way to ask for a discount:", ["Can you give a discount me?", "Can you give me discount a?", "Can you give me a discount?", "Can you giving me a discount?"], 2,
             "'Give me a discount' follows correct object order, with the article 'a' before 'discount'."),
            ("Which phrase signals bargaining is over?", ["That's my final offer.", "That's my finally offer.", "That's my offer final.", "That my final is offer."], 0,
             "'Final' is the correct adjective form placed directly before the noun 'offer'."),
        ],
    },
    "quiz-day-44": {
        "track": "day-44-weekend", "title": "Day 44 Quiz — Planning a Weekend Trip", "xpReward": 30,
        "questions": [
            ("Which sentence correctly describes a pre-decided plan?", ["We go to visit my uncle's village this weekend.", "We will going to visit my uncle's village.", "We're going to visit my uncle's village this weekend.", "We going to visit my uncle's village."], 2,
             "'Going to' + base verb is the correct structure for a plan decided before speaking."),
            ("Correct way to state a spontaneous decision:", ["I'll book the bus tickets tonight.", "I book will the bus tickets tonight.", "I'll booking the bus tickets tonight.", "I will to book the bus tickets tonight."], 0,
             "'Will' + base verb ('book') correctly expresses a decision made at the moment of speaking."),
            ("Which sentence correctly states a fixed schedule?", ["The bus is leave at six in the morning.", "The bus leaves at six in the morning.", "The bus leaving at six in the morning.", "The bus leaves is at six in the morning."], 1,
             "Present simple is used for fixed timetables, even when talking about the future."),
            ("Which correctly sequences two travel steps?", ["First we'll pack our bags then leave we'll.", "We'll pack first bags our, then leave.", "First pack we'll bags our, then we'll leave.", "First, we'll pack our bags, then we'll leave."], 3,
             "'First...then' keeps standard subject-verb order in each clause while sequencing the actions."),
            ("Polite request to reserve seats:", ["Could you save two seats for us, please?", "Could you saving two seats for us?", "Could you save for us two seats please you?", "You could save two seats for us please?"], 0,
             "'Could you ___?' followed by the base verb 'save' is the correct polite question form."),
        ],
    },
    "quiz-day-45": {
        "track": "day-45-hopes", "title": "Day 45 Quiz — Hopes & Wishes", "xpReward": 30,
        "questions": [
            ("Which sentence correctly expresses a realistic hope?", ["I hope to get a better job soon.", "I hope get a better job soon.", "I hope to getting a better job soon.", "I hoping to get a better job soon."], 0,
             "'Hope to' is followed by the base verb form ('get'), not the -ing form or the bare form without 'to'."),
            ("Correct way to state an intention:", ["I'm planning learn English this year.", "I'm planning to learn English this year.", "I plan to learning English this year.", "I'm plan to learn English this year."], 1,
             "'Planning to' must be followed by the base verb ('learn'), and needs the auxiliary 'am' (I'm)."),
            ("Which sentence correctly expresses a wish for something currently impossible?", ["I wish I can travel more.", "I wish I will travel more.", "I wish I traveling more.", "I wish I could travel more."], 3,
             "'Wish I could' uses the past form 'could' to express a present desire for something unlikely, not 'can'."),
            ("Which sentence is correct?", ["I'm hope to buy a house one day.", "I'm hoping buy a house one day.", "I'm hoping to buy a house one day.", "I hoping to buy a house one day."], 2,
             "The continuous form needs the auxiliary 'am' (I'm) plus 'hoping to' followed by the base verb."),
            ("Correct way to state a direct desire:", ["I really want to improve my English.", "I really want improve my English.", "I really wants to improve my English.", "I really want to improving my English."], 0,
             "'Want to' is followed by the base verb ('improve'), and 'want' doesn't take an 's' with the subject 'I'."),
        ],
    },
    "quiz-day-46": {
        "track": "day-46-obligations", "title": "Day 46 Quiz — Rules & Obligations", "xpReward": 30,
        "questions": [
            ("Which sentence correctly states a strict rule?", ["You must to wear a helmet on a bike.", "You must wear a helmet on a bike.", "You must wearing a helmet on a bike.", "You must wears a helmet on a bike."], 1,
             "'Must' is a modal verb followed directly by the base verb, with no 'to' and no change for the subject."),
            ("Which sentence correctly expresses necessity?", ["I have to finish this work by tomorrow.", "I have finish this work by tomorrow.", "I has to finish this work by tomorrow.", "I have to finishing this work by tomorrow."], 0,
             "'Have to' needs 'to' before the base verb, and stays as 'have' (not 'has') with the subject 'I'."),
            ("Which sentence gives advice correctly?", ["You should to drink more water every day.", "You should drinking more water every day.", "You should drink more water every day.", "You shoulds drink more water every day."], 2,
             "'Should' is a modal verb followed directly by the base verb, with no 'to' and no 's' added."),
            ("Most formal way to ask permission to enter:", ["May I come in?", "May I to come in?", "I may come in?", "May come I in?"], 0,
             "'May I ___?' followed by the base verb is the standard formal question form for permission."),
            ("Which sentence correctly gives permission?", ["You can to park your car here.", "You can parking your car here.", "You cans park your car here.", "You can park your car here."], 3,
             "'Can' is a modal verb followed directly by the base verb, with no 'to' and no 's' added."),
        ],
    },
    "quiz-day-47": {
        "track": "day-47-causeeffect", "title": "Day 47 Quiz — Cause & Effect", "xpReward": 30,
        "questions": [
            ("Which sentence correctly gives a reason?", ["I was late because the bus didn't come on time.", "I was late because of the bus didn't come on time.", "I was late the bus didn't come on time because.", "I was late, because the bus not came on time."], 0,
             "'Because' is directly followed by a full clause (subject + verb) to explain the reason."),
            ("Which sentence correctly shows a result?", ["It was raining heavily, because we stayed at home.", "It was raining heavily, we stayed so at home.", "It was raining heavily, so we stayed at home.", "So it was raining heavily, we stayed at home."], 2,
             "'So' introduces the result that follows from the cause stated first — the opposite direction from 'because'."),
            ("Which sentence correctly connects the cause and effect?", ["He didn't study, so he failed the exam.", "He didn't study, because he failed the exam.", "He failed the exam, so he didn't study.", "He didn't study so failed he the exam."], 0,
             "The cause ('didn't study') comes first, followed by 'so' and the result ('failed the exam')."),
            ("Which is the correct formal connector?", ["There was heavy traffic. As result, I missed my train.", "There was heavy traffic. As a result, I missed my train.", "There was heavy traffic. As a result I missing my train.", "As a result there was heavy traffic, I missed my train."], 1,
             "'As a result' needs the article 'a' and correctly starts a new sentence stating the effect."),
            ("Which sentence is correct?", ["I saved money every month, so I can buy a new phone.", "I saved money every month, because I could buy a new phone.", "So I saved money every month, I could buy a new phone.", "I saved money every month, so I could buy a new phone."], 3,
             "'So' correctly links the past cause to the past result 'could buy', keeping consistent past tense."),
        ],
    },
    "quiz-day-48": {
        "track": "day-48-disagree", "title": "Day 48 Quiz — Handling Disagreements", "xpReward": 30,
        "questions": [
            ("Polite way to disagree after acknowledging someone's opinion:", ["I see your point, but I am thinking different.", "I see you point, but I think differently.", "Your point I see, but I think differently.", "I see your point, but I think differently."], 3,
             "'I see your point' correctly uses the possessive 'your' before 'point', followed by 'but' to introduce the disagreement."),
            ("Which sentence politely expresses uncertainty about agreeing?", ["I'm not sure I agree with that.", "I'm not sure I agree that with.", "I not sure am I agree with that.", "I'm not sure agree I with that."], 0,
             "'I'm not sure I agree with that' has correct subject-verb order in both clauses."),
            ("Which sentence turns a disagreement into a soft question?", ["Have you consider the cost?", "Have you considered the cost?", "You have considered the cost?", "Considered you have the cost?"], 1,
             "Present perfect questions use 'Have you' followed by the past participle 'considered'."),
            ("Which sentence correctly validates before disagreeing?", ["I understand, but I see it differently.", "I understand, but I see it different.", "I understand, but I seeing it differently.", "But I see it differently, I understand."], 0,
             "'Differently' (adverb) correctly modifies the verb 'see', not the adjective form 'different'."),
            ("Fixed idiom for ending a disagreement politely:", ["Let's agree for disagree.", "Let's agreeing to disagree.", "Let's agree to disagree.", "Let's agree to disagreeing."], 2,
             "'Agree to disagree' is a fixed idiom using the base verb form after 'to'."),
        ],
    },
    "quiz-day-49": {
        "track": "day-49-technology", "title": "Day 49 Quiz — Technology & the Internet", "xpReward": 30,
        "questions": [
            ("Which sentence correctly describes a current habit?", ["I'm using my phone to learn English these days.", "I use my phone to learn English these days.", "I'm use my phone to learn English these days.", "I using my phone to learn English these days."], 0,
             "Present continuous ('I'm using') with the auxiliary 'am' correctly describes a current ongoing habit."),
            ("Which sentence is correct?", ["She's video call her family every weekend.", "She's video calling her family every weekend.", "She video calling her family every weekend.", "She's videos calling her family every weekend."], 1,
             "Present continuous needs the auxiliary 'is' (She's) plus the -ing form 'calling'."),
            ("Which sentence correctly emphasizes something happening right now?", ["We're chatting on WhatsApp right now.", "We chat on WhatsApp right now.", "We're chat on WhatsApp right now.", "We chatting on WhatsApp right now."], 0,
             "'Right now' pairs with present continuous, which needs the auxiliary 'are' (We're) plus 'chatting'."),
            ("Which sentence is correct?", ["He downloading a new app.", "He's download a new app.", "He download a new app.", "He's downloading a new app."], 3,
             "Present continuous requires the auxiliary 'is' (He's) plus the -ing form 'downloading'."),
            ("Which sentence correctly describes a current problem?", ["I don't getting good internet signal here.", "I'm not get good internet signal here.", "I'm not getting good internet signal here.", "I not getting good internet signal here."], 2,
             "Negative present continuous uses 'am not' (I'm not) plus the -ing form 'getting'."),
        ],
    },
    "quiz-day-50": {
        "track": "day-50-transport", "title": "Day 50 Quiz — Public Transport", "xpReward": 30,
        "questions": [
            ("Which sentence correctly describes a bus behind schedule?", ["The bus is run late today.", "The bus running late today.", "The bus is running late today.", "The bus is run lately today."], 2,
             "'Running late' is a fixed phrase using 'is' plus the -ing form 'running'."),
            ("Which sentence correctly reports a recent delay?", ["The train has been delayed by twenty minutes.", "The train has delayed by twenty minutes.", "The train has been delay by twenty minutes.", "The train had been delayed twenty minutes by."], 0,
             "Present perfect passive needs 'has been' plus the past participle 'delayed'."),
            ("Which sentence correctly gives travel instructions?", ["You need change buses at the next stop.", "You need to changing buses at the next stop.", "You needs to change buses at the next stop.", "You need to change buses at the next stop."], 3,
             "'Need to' is followed by the base verb ('change'), and 'need' doesn't take an 's' with the subject 'you'."),
            ("Which sentence correctly says something happened moments ago?", ["We missed just the last bus.", "We just missed the last bus.", "We just miss the last bus.", "We have just miss the last bus."], 1,
             "'Just' placed before the past tense verb 'missed' shows the action happened a very short time ago."),
            ("Which sentence correctly describes a scheduled arrival?", ["The next bus arrives in ten minutes.", "The next bus is arrive in ten minutes.", "The next bus arriving in ten minutes.", "The next bus arrive in ten minutes."], 0,
             "Present simple ('arrives') with the 's' for third person singular correctly describes a scheduled future event."),
        ],
    },
    "quiz-day-51": {
        "track": "day-51-problems", "title": "Day 51 Quiz — Everyday Problems & Solutions", "xpReward": 30,
        "questions": [
            ("Which sentence is correct?", ["I having fix this today.", "I have to fix this today.", "I have fix this today.", "I to fix this today."], 1,
             "'have to' + base verb expresses obligation, with no 'to' needed before the main verb after 'have'."),
            ("Fill in the blank: 'There was a power cut, ___ I couldn't finish the work.'", ["because", "but", "although", "so"], 3,
             "'so' introduces the result of the cause already stated."),
            ("Correct way to disagree politely:", ["I don't think that's a good idea.", "I not think that's a good idea.", "I think that's not good idea, no.", "Not I think that's good idea."], 0,
             "'I don't think...' negates the main verb 'think', softening the disagreement."),
            ("Which sentence is correct?", ["You must call the plumber the pipe is leaking because.", "You must call the plumber because the pipe is leaking.", "Because the pipe is leaking must you call the plumber.", "You must to call the plumber because the pipe is leaking."], 1,
             "'must' is followed directly by the base verb without 'to', and 'because' introduces the reason after the main clause."),
            ("Fill in the blank: '___ try a different solution instead.'", ["Let we", "Let's", "Lets to", "We let's"], 1,
             "'Let's' (let us) + base verb is the fixed pattern for suggesting an action together."),
        ],
    },
    "quiz-day-52": {
        "track": "day-52-feelingsdetail", "title": "Day 52 Quiz — Describing Feelings in Detail", "xpReward": 30,
        "questions": [
            ("Fill in the blank: 'I feel ___ because the internet is so slow.'", ["frustrating", "frustration", "frustrated", "frustrate"], 2,
             "'frustrated' is the adjective form describing how a person feels."),
            ("Which sentence correctly uses 'proud of'?", ["She is proud of her son's achievement.", "She is proud her son's achievement.", "She is proud about her son's achievement's.", "She is proud on her son's achievement."], 0,
             "'proud' is always followed by the preposition 'of'."),
            ("Correct way to say you're happy a problem ended:", ["I feel relieved the exam over is that.", "I feel relieved that the exam is over.", "I feel relieved that the exam over.", "I feeling relieved that the exam is over."], 1,
             "'feel relieved that + clause' needs a full clause with a verb — dropping 'is' breaks the sentence."),
            ("Which sentence is correct?", ["I am disappointed when the trip got cancelled.", "I was disappointed when the trip gets cancelled.", "I was disappoint when the trip got cancelled.", "I was disappointed when the trip got cancelled."], 3,
             "Both the feeling and the event happened in the past, so both verbs use past tense."),
            ("Fill in the blank: 'I feel nervous ___ I have an interview tomorrow.'", ["but", "although", "because", "so"], 2,
             "'because' introduces the reason for the feeling."),
        ],
    },
    "quiz-day-53": {
        "track": "day-53-experience", "title": "Day 53 Quiz — Talking About Achievements", "xpReward": 30,
        "questions": [
            ("Fill in the blank: 'I have ___ my homework already.'", ["do", "did", "doing", "done"], 3,
             "Present perfect uses 'have/has' + past participle, and 'done' is the past participle of 'do'."),
            ("Which sentence correctly describes a travel experience?", ["I has been to Hyderabad twice.", "I have been to Hyderabad twice.", "I have go to Hyderabad twice.", "I have went to Hyderabad twice."], 1,
             "'have been to' is the correct present perfect form for describing places visited."),
            ("Correct question form to ask about life experience:", ["You have ever eaten Chinese food?", "Have you ever ate Chinese food?", "Have you ever eaten Chinese food?", "Did you ever eaten Chinese food?"], 2,
             "Present perfect questions place 'Have/Has' before the subject, followed by the past participle."),
            ("Which sentence is correct?", ["I have never seen snow in my life.", "I have not never seen snow in my life.", "I never have not seen snow in my life.", "I have never not seen snow in my life."], 0,
             "'never' alone makes the sentence negative, so adding 'not' creates a double negative error."),
            ("Fill in the blank: 'She has ___ finished her project.'", ["yet", "already before", "since", "just"], 3,
             "'just' goes between 'has' and the past participle to show something happened very recently."),
        ],
    },
    "quiz-day-54": {
        "track": "day-54-directionsdetail", "title": "Day 54 Quiz — Giving Detailed Directions", "xpReward": 30,
        "questions": [
            ("Fill in the blank: 'Turn left at the ___ signal.'", ["second", "two", "2th", "twice"], 0,
             "'second' is the correct ordinal number form for describing order."),
            ("Which sentence is correct?", ["Go straight until you saw the bus stop.", "Go straight until seeing you the bus stop.", "Go straight until you see the bus stop.", "Go straight until you will see the bus stop."], 2,
             "After 'until', use the simple present tense to describe a future point of reference, not 'will' or the past tense."),
            ("Correct way to describe position next to something:", ["The bank is next the pharmacy.", "The bank is nexting to the pharmacy.", "The bank is at next to the pharmacy.", "The bank is next to the pharmacy."], 3,
             "'next to' is a fixed two-word preposition and both words are required."),
            ("Fill in the blank: 'Take the ___ left after the temple.'", ["thirdly", "third", "three", "threeth"], 1,
             "'third' is the correct ordinal adjective to use directly before a noun like 'left'."),
            ("Which sentence correctly uses the idiom for 'easy to find'?", ["You can't miss it.", "You cannot lose it.", "You can't fail it.", "You won't lost it."], 0,
             "'You can't miss it' is the fixed idiom meaning something is very easy to find."),
        ],
    },
    "quiz-day-55": {
        "track": "day-55-emergencies", "title": "Day 55 Quiz — Handling Emergencies", "xpReward": 30,
        "questions": [
            ("Correct way to report an emergency:", ["Please help, there has an accident been!", "Please help, there's been an accident!", "Please help, there is an accident happened!", "Please help, an accident there has been!"], 1,
             "'There's been a/an + noun' is the correct present perfect form for reporting that something has just happened."),
            ("Which is the correct urgent command?", ["You call an ambulance right now!", "Calling an ambulance right now!", "To call an ambulance right now!", "Call an ambulance right now!"], 3,
             "Imperative sentences start directly with the base verb, without a subject like 'you'."),
            ("Fill in the blank: 'Someone ___, please bring water quickly.'", ["fainted", "faint", "fainting", "faints"], 0,
             "The simple past 'fainted' reports a completed sudden event."),
            ("Correct warning to say when the floor is wet:", ["Out watch, the floor is wet!", "Watching out, the floor wet is!", "Watch out, the floor is wet!", "Watch the floor out, is wet!"], 2,
             "'Watch out' is a fixed phrasal warning that must stay together at the start of the sentence."),
            ("Which sentence correctly expresses urgency?", ["I need help immediate, it's an emergency!", "I need help immediately, it's an emergency!", "I need immediately help, it's an emergency!", "I immediately need help, an emergency it's!"], 1,
             "'immediately' is an adverb and naturally follows the verb phrase 'need help', while 'immediate' is an adjective and cannot modify a verb this way."),
        ],
    },
    "quiz-day-56": {
        "track": "day-56-weatherdetail", "title": "Day 56 Quiz — Weather & Seasons in Depth", "xpReward": 30,
        "questions": [
            ("Fill in the blank: 'Summer is ___ than winter here.'", ["more hotter", "hottest", "hotter", "hot"], 2,
             "Short adjectives like 'hot' form comparatives by adding '-er', and 'more hotter' is a double comparative error."),
            ("Correct way to talk about a weather forecast:", ["It's supposed to rain this evening.", "It's suppose to rain this evening.", "It's supposed rain this evening.", "It's supposing to rain this evening."], 0,
             "'be supposed to' is the fixed structure used to report an expectation, and 'supposed' must be followed by 'to'."),
            ("Which sentence correctly compares this year's monsoon to last year's?", ["This monsoon is wet than last year's.", "This monsoon is wetter than last year's.", "This monsoon is more wetter last year's.", "This monsoon is wetter as last year's."], 1,
             "Comparative adjectives require 'than', and short adjectives like 'wet' don't take 'more' as well as '-er'."),
            ("Fill in the blank: 'Winter mornings are colder ___ winter evenings.'", ["then", "that", "as", "than"], 3,
             "'than' is the correct word used after a comparative adjective to introduce the second thing being compared."),
            ("Correct way to report a weather forecast prediction:", ["The weather forecast said it will sunny tomorrow.", "The weather forecast says it will sunny tomorrow.", "The weather forecast says it will be sunny tomorrow.", "The weather forecast says it is sunny tomorrow."], 2,
             "Future predictions use 'will be' + adjective, and 'will' must be followed by 'be' before an adjective like 'sunny'."),
        ],
    },
    "quiz-day-57": {
        "track": "day-57-etiquette", "title": "Day 57 Quiz — Social Etiquette & Manners", "xpReward": 30,
        "questions": [
            ("Most polite way to ask someone to pass the salt:", ["You pass the salt please?", "Pass me salt, could you?", "Please salt pass you could?", "Could you please pass the salt?"], 3,
             "'Could you please + base verb?' is the standard polite request structure."),
            ("Which sentence correctly asks permission very politely?", ["Would you minding if I sat here?", "Would you mind if I sat here?", "Would you mind if I sit here?", "Would you mind I sat here?"], 1,
             "'Would you mind if I + past tense verb?' is the fixed polite permission structure, even though it refers to the present."),
            ("Fill in the blank: 'Please call me uncle — no need ___ formalities.'", ["of", "with", "for", "to"], 2,
             "'no need for + noun' is the correct fixed preposition pattern."),
            ("Most formal way to ask permission to speak to someone:", ["Excuse me, sir, may I ask you something?", "Excuse me, sir, can I ask you something?", "Hey sir, I ask you something?", "Sir excuse me, asking you something?"], 0,
             "'May I' is the most formal and respectful way to ask permission, appropriate for addressing elders or strangers."),
            ("Correct polite closing phrase after someone helps you:", ["Thank you for your time, I really appreciate.", "Thank for your time, I really appreciate it.", "Thank you your time, I really appreciate it.", "Thank you for your time, I really appreciate it."], 3,
             "'appreciate' needs an object like 'it' to complete the sentence, and 'thank you for' requires both words."),
        ],
    },
    "quiz-day-58": {
        "track": "day-58-gathering", "title": "Day 58 Quiz — A Family Gathering", "xpReward": 30,
        "questions": [
            ("Which sentence correctly reports a past feeling during an event?", ["I felt so proud when my niece got her first job.", "I feel so proud when my niece got her first job.", "I felt so proud when my niece gets her first job.", "I felt so proud my niece got her first job when."], 0,
             "Describing a past memory requires both verbs, 'felt' and 'got', to be in the past tense."),
            ("Most polite way to ask someone to serve grandmother first:", ["You could please pass grandmother sweets first?", "Please could sweets pass grandmother first?", "Could you please pass the sweets to grandmother first?", "Pass grandmother the sweets first, could you?"], 2,
             "'Could you please + verb + object?' is the correct polite request word order."),
            ("Correct way to quickly report a small accident at home:", ["Someone spill juice on the carpet.", "Someone has spilling juice on the carpet.", "Someone spilled on juice the carpet.", "Someone spilled juice on the carpet."], 3,
             "Simple past tense 'spilled' correctly reports a completed sudden action."),
            ("Fill in the blank: 'We were all relieved ___ the power came back.'", ["during", "when", "because of", "for"], 1,
             "'when' introduces the specific time clause describing the moment the relief occurred."),
            ("Most polite way to offer more food to an elder:", ["Would you like some more rice?", "You like some more rice?", "Do you want more rice, uncle, now?", "Like you more rice would?"], 0,
             "'Would you like + noun?' is the standard polite way to offer something to someone, especially an elder."),
        ],
    },
    "quiz-day-59": {
        "track": "day-59-goals", "title": "Day 59 Quiz — Future Goals & Ambitions", "xpReward": 30,
        "questions": [
            ("Which sentence correctly expresses a future plan?", ["I'm planning to learning English fluently this year.", "I'm planning to learn English fluently this year.", "I'm planning learn English fluently this year.", "I'm plan to learn English fluently this year."], 1,
             "'planning to' is followed by the base verb, not the '-ing' form or a bare verb without 'to'."),
            ("Fill in the blank: 'I hope ___ get a better job next year.'", ["for", "for to", "of", "to"], 3,
             "'hope to + base verb' is the correct fixed structure for expressing a future wish."),
            ("Correct way to state a personal goal:", ["My goal is to save money for a new house.", "My goal is save money for a new house.", "My goal to save money for a new house.", "My goal is saving to money for a new house."], 0,
             "'My goal is to + base verb' requires both 'is' and 'to' before the verb."),
            ("Which sentence correctly shows strong commitment?", ["I'm determine to improve my pronunciation.", "I'm determined to improving my pronunciation.", "I'm determined to improve my pronunciation.", "I'm determined improve my pronunciation."], 2,
             "'determined to' is followed by 'to' plus the base verb, and 'determine' must be in its adjective form 'determined' after 'am'."),
            ("Correct way to describe an action completed before a future point:", ["By next year, I will finish already this course.", "By next year, I will have finished this course.", "By next year, I will finished this course.", "By next year, I have finished this course."], 1,
             "Future perfect ('will have + past participle') is used to show an action completed before a specific future time."),
        ],
    },
    "quiz-day-60": {
        "track": "day-60-capstone", "title": "Day 60 Quiz — Level 2 Capstone: Confident Everyday Conversations", "xpReward": 30,
        "questions": [
            ("Which sentence correctly mixes habit and present perfect to contrast routine with a recent change?", ["I usually go for a walk every morning, but I hadn't had time this week.", "I usually go for a walk every morning, but I don't had time this week.", "I usually go for a walk every morning, but I haven't had time this week.", "I usually going for a walk every morning, but I haven't had time this week."], 2,
             "'usually go' (simple present habit) contrasts correctly with 'haven't had' (present perfect for a recent, ongoing situation)."),
            ("Correct way to combine advice with a duration using present perfect:", ["You should see a doctor because you've had a cough for three days.", "You should see a doctor because you had a cough since three days.", "You should see a doctor because you've had a cough since three days.", "You should to see a doctor because you've had a cough for three days."], 0,
             "'for' is used with a length of time like 'three days', while 'since' is used with a starting point, so 'for three days' is correct here."),
            ("Which sentence correctly links obligation with a contrasting feeling?", ["I have finish this report today, even though I'm exhausted.", "I have to finish this report today, even though I'm exhausted.", "I have to finish this report today, even though I'm exhaust.", "I had to finish this report today, even though I'm exhausted."], 1,
             "'have to' + base verb states the obligation, and 'even though' correctly introduces the contrasting feeling 'exhausted' in the present."),
            ("Correct hypothetical advice combined with present perfect and 'since':", ["If I was you, I'd apologize, because you've hurt her feelings and she's been upset since yesterday.", "If I were you, I'd apologize, because you've hurt her feelings and she's been upset for yesterday.", "If I were you, I apologize, because you've hurt her feelings and she's been upset since yesterday.", "If I were you, I'd apologize, because you've hurt her feelings and she's been upset since yesterday."], 3,
             "Hypothetical advice uses 'If I were you' (not 'was'), 'I'd' for the result, and 'since yesterday' correctly marks the starting point of the ongoing feeling."),
            ("Which sentence correctly connects present perfect, a time phrase, and a result clause?", ["I've never felt so proud, because after months of practice, I could finally speak English confidently.", "I've never feel so proud, because after months of practice, I can finally speak English confidently.", "I've never felt so proud, because after months of practice, I can finally speak English confidently.", "I never felt so proud, because after months of practice, I can finally speak English confidently."], 2,
             "'I've never felt' (present perfect) correctly links a life experience up to now with the present ability 'I can finally speak', shown by 'can' not 'could'."),
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
