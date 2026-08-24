"""Seeds Week 1 (Days 1-7) of the 30-day roadmap into Firestore: lessons for
each day plus one multiple-choice quiz per day.

Content design is grounded in real research, not guesswork — see
CURRICULUM.md §8 for citations. In short:
  - Topic order (greetings -> personal info -> numbers/time -> shopping ->
    food -> directions -> health) matches standard adult-ESL "survival
    English" sequencing.
  - Every target sentence is a genuine CEFR A1 high-frequency phrase.
  - Grammar notes target real, published L1-interference patterns for
    Telugu speakers (dropped articles, dropped linking words like "of" and
    "as a", literal-translation calques like "myself Ravi" / "head is
    paining", unfamiliarity with English tag questions).
  - Every target sentence and vocab word carries a Telugu translation
    (`nativeTranslation` / `nativeMeaning`), shown to the learner BEFORE
    they attempt the sentence — research on L1 vs L2 glossing shows L1
    translations help most at exactly the beginner stage this content is
    for, which is the concrete "start fast" ask this content responds to.

Telugu text here was written by Claude (not a certified native reviewer) —
correct standard Telugu to the best of that ability, but worth a native
speaker's read-through before this is the only Telugu a learner sees.

This upserts (PATCH-with-full-fields, not skip-on-exists) so re-running is
safe and also fixes up the 10 original Day 1 lessons, which were seeded
before nativeTranslation/nativeMeaning existed in the schema.

Usage:
    python3 backend/scripts/seed_week1_content.py
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

DAY1_LESSONS = [
    ("found-a1-greet-01", 1, "Hello, how are you?", "హలో, మీరు ఎలా ఉన్నారు?",
     ["/h/ in 'hello'"], "hello", "a greeting", "పలకరింపు మాట",
     "A fixed greeting phrase — used the same way every time."),
    ("found-a1-greet-02", 2, "I am fine, thank you.", "నేను బాగానే ఉన్నాను, ధన్యవాదాలు.",
     ["/θ/ in 'thank'"], "fine", "okay, well", "బాగా",
     "'I am' is often the response to 'how are you?'"),
    ("found-a1-greet-03", 3, "Nice to meet you.", "మిమ్మల్ని కలవడం సంతోషంగా ఉంది.",
     ["/iː/ in 'meet'", "linking 'nice to' -> 'nice-tuh'"], "nice", "pleasant, kind", "మంచిది",
     "A fixed phrase said when meeting someone for the first time."),
    ("found-a1-greet-04", 4, "My name is Alex.", "నా పేరు అలెక్స్.",
     ["/æ/ in 'Alex'"], "name", "what you are called", "పేరు",
     "'My name is ___' — the standard way to introduce yourself. Avoid the direct translation 'Myself Alex' — it's understood, but not correct English."),
    ("found-a1-greet-05", 5, "Where are you from?", "మీరు ఎక్కడ నుండి వచ్చారు?",
     ["/w/ in 'where'"], "from", "indicates origin", "నుండి",
     "A common question when meeting someone new. The question word 'where' always comes first."),
    ("found-a1-greet-06", 6, "I am from India.", "నేను భారతదేశం నుండి వచ్చాను.",
     ["/ɪ/ in 'India'"], "India", "a country", "భారతదేశం",
     "'I am from ___' states your country of origin."),
    ("found-a1-greet-07", 7, "See you later.", "తర్వాత కలుద్దాం.",
     ["/l/ in 'later'"], "later", "at a future time", "తర్వాత",
     "A casual way to say goodbye."),
    ("found-a1-greet-08", 8, "Have a good day.", "మీ రోజు బాగుండాలి.",
     ["/g/ in 'good'"], "good", "pleasant, nice", "మంచి",
     "A polite phrase used when parting."),
    ("found-a1-greet-09", 9, "What is your name?", "మీ పేరు ఏమిటి?",
     ["/w/ in 'what'"], "your", "belonging to you", "మీ",
     "A direct question to learn someone's name."),
    ("found-a1-greet-10", 10, "It was nice talking to you.", "మీతో మాట్లాడటం సంతోషంగా ఉంది.",
     ["/t/ in 'talking'"], "talking", "speaking with someone", "మాట్లాడటం",
     "Past tense — said at the end of a conversation."),
]

DAY2_LESSONS = [
    ("day2-family-01", 1, "This is my husband.", "ఇతను నా భర్త.",
     ["/h/ in 'husband'"], "husband", "a woman's male marriage partner", "భర్త",
     "'This is my ___' introduces a person who is present."),
    ("day2-family-02", 2, "I have two children.", "నాకు ఇద్దరు పిల్లలు ఉన్నారు.",
     ["/tʃ/ in 'children'"], "children", "sons and/or daughters (irregular plural of 'child')", "పిల్లలు",
     "'Children' is irregular — never say 'childs'."),
    ("day2-family-03", 3, "She is my daughter.", "ఆమె నా కూతురు.",
     ["/ɔː/ in 'daughter'"], "daughter", "a person's female child", "కూతురు",
     "'She is my ___' works the same way as 'This is my ___' once the person is known."),
    ("day2-family-04", 4, "He works as a teacher.", "అతను ఉపాధ్యాయుడిగా పని చేస్తాడు.",
     ["/w/ in 'works'"], "teacher", "someone who helps others learn", "ఉపాధ్యాయుడు",
     "'works as a ___' states a person's job or role — a common mistake is dropping 'as a' entirely."),
    ("day2-family-05", 5, "My family lives in Vijayawada.", "మా కుటుంబం విజయవాడలో నివసిస్తుంది.",
     ["/v/ in 'Vijayawada'"], "family", "a group of related people, e.g. parents and children", "కుటుంబం",
     "'Family' takes a singular verb ('lives'), treated as one unit, even though it means many people."),
    # Added alongside "This is my husband." so the lesson introduces a spouse
    # of either gender, not just one — same "This is my ___" pattern, no new
    # grammar to learn, purely additive.
    ("day2-family-06", 6, "This is my wife.", "ఈమె నా భార్య.",
     ["/w/ in 'wife'"], "wife", "a man's female marriage partner", "భార్య",
     "Same pattern as 'This is my husband' — 'This is my ___' introduces any family member who is present."),
]

DAY3_LESSONS = [
    ("day3-routine-01", 1, "I wake up at six o'clock.", "నేను ఆరు గంటలకు నిద్ర లేస్తాను.",
     ["/w/ in 'wake'"], "wake up", "to stop sleeping", "నిద్ర లేవడం",
     "Use 'at' with exact clock times: 'at six o'clock'."),
    ("day3-routine-02", 2, "I drink tea every morning.", "నేను ప్రతి ఉదయం టీ తాగుతాను.",
     ["/iː/ in 'tea'"], "every", "each one, without exception", "ప్రతి",
     "'Every' already means 'each' — don't add 'the' before it ('the every morning' is wrong)."),
    ("day3-routine-03", 3, "I go to the market in the evening.", "నేను సాయంత్రం మార్కెట్‌కి వెళ్తాను.",
     ["/ɑː/ in 'market'"], "market", "a place to buy food and goods", "మార్కెట్ / సంత",
     "'the market' — use 'the' for a specific, known place, unlike the article-free 'every morning'."),
    ("day3-routine-04", 4, "I watch television after dinner.", "నేను రాత్రి భోజనం తర్వాత టీవీ చూస్తాను.",
     ["/tʃ/ in 'watch'"], "television", "a device for watching shows", "టీవీ",
     "'watch television', not 'see television' — 'watch' is the natural verb for TV."),
    ("day3-routine-05", 5, "What time do you wake up?", "మీరు ఎన్ని గంటలకు నిద్ర లేస్తారు?",
     ["/w/ in 'what'"], "time", "the point on the clock", "సమయం",
     "Question word first: 'What time do you ___?' — this order is fixed in English."),
]

DAY4_LESSONS = [
    ("day4-shopping-01", 1, "How much does this cost?", "ఇది ఎంత ఖరీదు?",
     ["/k/ in 'cost'"], "cost", "the price of something", "ఖరీదు / ధర",
     "'How much does this cost?' is the standard, polite way to ask a price."),
    ("day4-shopping-02", 2, "This costs two hundred rupees.", "దీని ధర రెండు వందల రూపాయలు.",
     ["/r/ in 'rupees'"], "rupees", "Indian currency", "రూపాయలు",
     "No 'a' or 'the' before a specific number like 'two hundred' — the number is enough on its own."),
    ("day4-shopping-03", 3, "Can you give me a discount?", "మీరు నాకు కొంచెం తగ్గించి ఇవ్వగలరా?",
     ["/d/ in 'discount'"], "discount", "a reduction in price", "తగ్గింపు",
     "'Can you ___?' is a polite way to ask someone for something."),
    ("day4-shopping-04", 4, "I need one kilogram of rice.", "నాకు ఒక కిలో బియ్యం కావాలి.",
     ["/k/ in 'kilogram'"], "kilogram", "a unit of weight", "కిలో",
     "Use 'of' to link a quantity and an item: 'one kilogram OF rice' — dropping 'of' is a very common mistake."),
    ("day4-shopping-05", 5, "The shop closes at nine.", "ఈ దుకాణం తొమ్మిది గంటలకు మూసేస్తారు.",
     ["/ʃ/ in 'shop'"], "closes", "stops being open", "మూసివేయడం",
     "Use 'at' with exact times, same pattern as Day 3's 'wake up at six o'clock'."),
]

DAY5_LESSONS = [
    ("day5-food-01", 1, "I would like a cup of coffee.", "నాకు ఒక కప్పు కాఫీ కావాలి.",
     ["/w/ in 'would'"], "would like", "a polite way to say 'want'", "మర్యాదపూర్వకంగా కావాలి అనడం",
     "'I would like ___' sounds more polite than 'I want ___', especially with strangers."),
    ("day5-food-02", 2, "Can I have the menu, please?", "దయచేసి మెనూ ఇవ్వగలరా?",
     ["/m/ in 'menu'"], "menu", "the list of food available", "మెనూ",
     "'Can I have ___, please?' is a polite request pattern useful far beyond restaurants."),
    ("day5-food-03", 3, "This food is very spicy.", "ఈ ఆహారం చాలా కారంగా ఉంది.",
     ["/s/ in 'spicy'"], "spicy", "having a hot, strong chili taste", "కారం",
     "'very' makes an adjective stronger: 'very spicy'."),
    ("day5-food-04", 4, "I am allergic to peanuts.", "నాకు వేరుశెనగలు పడవు (అలర్జీ).",
     ["/dʒ/ in 'allergic'"], "allergic", "having a bad reaction to something", "పడకపోవడం",
     "'allergic TO ___' — always followed by 'to'. A genuinely useful phrase to have ready."),
    ("day5-food-05", 5, "The bill, please.", "బిల్లు ఇవ్వండి, దయచేసి.",
     ["/b/ in 'bill'"], "bill", "the paper showing what you owe", "బిల్లు",
     "A short, polite way to ask to pay — no full sentence needed."),
]

DAY6_LESSONS = [
    ("day6-directions-01", 1, "Where is the bus stop?", "బస్ స్టాప్ ఎక్కడ ఉంది?",
     ["/w/ in 'where'"], "bus stop", "the place a bus picks up passengers", "బస్ స్టాప్",
     "'Where is ___?' asks for the location of something specific."),
    ("day6-directions-02", 2, "Turn left at the next signal.", "తర్వాతి సిగ్నల్ దగ్గర ఎడమవైపు తిరగండి.",
     ["/l/ in 'left'"], "signal", "a traffic light", "సిగ్నల్",
     "Direction instructions often start with the action verb: 'Turn left...', 'Go straight...'."),
    ("day6-directions-03", 3, "How far is the railway station?", "రైల్వే స్టేషన్ ఎంత దూరంలో ఉంది?",
     ["/f/ in 'far'"], "far", "a long distance away", "దూరం",
     "'How far is ___?' asks about distance, not price or time."),
    ("day6-directions-04", 4, "I want to go to the airport.", "నేను విమానాశ్రయానికి వెళ్ళాలి.",
     ["/eə/ in 'airport'"], "airport", "where airplanes take off and land", "విమానాశ్రయం",
     "'want to go to ___' — both 'to's are needed: one for 'go to', one before the destination."),
    ("day6-directions-05", 5, "Please stop here.", "దయచేసి ఇక్కడ ఆపండి.",
     ["/h/ in 'here'"], "stop", "to come to a halt", "ఆపడం",
     "'Please ___' softens a direct instruction — useful when speaking to a driver."),
]

DAY7_LESSONS = [
    ("day7-health-01", 1, "I have a headache.", "నాకు తలనొప్పిగా ఉంది.",
     ["/h/ in 'headache'"], "headache", "pain in the head", "తలనొప్పి",
     "English says 'have a headache', not the direct translation 'my head is paining'."),
    ("day7-health-02", 2, "I am not feeling well today.", "ఈ రోజు నాకు ఒంట్లో బాగాలేదు.",
     ["/f/ in 'feeling'"], "feeling", "the state of your body or mood", "అనుభూతి",
     "'not feeling well' is the natural way to say you're a bit sick, without naming the illness."),
    ("day7-health-03", 3, "Please call a doctor.", "దయచేసి డాక్టర్‌ని పిలవండి.",
     ["/k/ in 'call'"], "doctor", "a medical professional", "డాక్టర్",
     "'Please call a ___' is a clear, polite request in an urgent situation."),
    ("day7-health-04", 4, "It's a beautiful day, isn't it?", "ఈ రోజు చాలా బాగుంది, కదా?",
     ["/juː/ in 'beautiful'"], "beautiful", "very pleasant to look at or experience", "అందమైన",
     "'..., isn't it?' is a 'tag question' — a short question added to invite agreement. Telugu doesn't have a direct equivalent, so this often feels unfamiliar at first."),
    ("day7-health-05", 5, "Take care of yourself.", "మిమ్మల్ని మీరు జాగ్రత్తగా చూసుకోండి.",
     ["/j/ in 'yourself'"], "take care", "stay safe and well", "జాగ్రత్త",
     "A warm way to say goodbye to someone you care about — a nice bookend to Day 1's 'See you later.'"),
]

DAYS = [
    ("foundations", "A1", "Greetings & Introductions", DAY1_LESSONS),
    ("day-2-family", "A1", "Family & People", DAY2_LESSONS),
    ("day-3-routine", "A1", "Daily Routine", DAY3_LESSONS),
    ("day-4-shopping", "A1", "Numbers, Time & Shopping", DAY4_LESSONS),
    ("day-5-food", "A1", "Food & Ordering", DAY5_LESSONS),
    ("day-6-directions", "A1", "Directions & Travel", DAY6_LESSONS),
    ("day-7-health", "A1/A2", "Health & Small Talk (Week 1 review)", DAY7_LESSONS),
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


# ---------------------------------------------------------------------------
# Quizzes — one per day, 5 multiple-choice questions each. Explanations are
# bilingual: a short Telugu clause reinforces the point right after the
# English one, same "native, to help them start fast" principle as lessons.
# ---------------------------------------------------------------------------

QUIZZES = {
    "quiz-day-1": {
        "track": "foundations",
        "title": "Day 1 Quiz — Greetings & Introductions",
        "xpReward": 30,
        "questions": [
            (
                "Someone says \"How are you?\" What is the best reply?",
                ["I am fine, thank you.", "Yes, I am.", "Hello, hello.", "No problem."],
                0,
                "‘I am fine, thank you’ directly answers how you feel — the standard polite reply. (ఇది సాధారణ సమాధానం.)",
            ),
            (
                "How do you introduce yourself in English?",
                ["My name is Ravi.", "Myself Ravi.", "I name Ravi.", "Ravi I am."],
                0,
                "‘My name is ___’ is correct. ‘Myself Ravi’ is a very common direct translation, but it isn't standard English. (నేరుగగా తెలుగులోనుంచి అనువదించథే ఇలా వస్తుంది.)",
            ),
            (
                "Which question asks about someone's native country?",
                ["Where are you from?", "What is your from?", "You are from where?", "From you are?"],
                0,
                "'Where' comes first, then 'are you'. English keeps this word order fixed. (ప్రశ్న పదం మొదట వస్తుంది.)",
            ),
            (
                "What does \"Nice to meet you\" mean?",
                [
                    "A polite phrase said when meeting someone for the first time",
                    "A way to say goodbye",
                    "A question about someone's health",
                    "A way to introduce your name",
                ],
                0,
                "Said right after being introduced — not at any other point. (మొదటిసారి కలిసినప్పుడే అంటారు.)",
            ),
            (
                "Which is the most natural way to end a casual conversation?",
                ["See you later.", "I am going now finish.", "Bye stop.", "Finish talking."],
                0,
                "A simple, standard goodbye phrase. (సాధారణంగా వినిపించే విద్ద చెప్పే మాట.)",
            ),
        ],
    },
    "quiz-day-2": {
        "track": "day-2-family",
        "title": "Day 2 Quiz — Family & People",
        "xpReward": 30,
        "questions": [
            (
                "Fill in the blank: \"This ___ my husband.\"",
                ["is", "are", "am", "be"],
                0,
                "'This is' — singular subject, singular verb.",
            ),
            (
                "How do you say you have two kids in English?",
                ["I have two children.", "I have two childs.", "I am having two children.", "Two children I have."],
                0,
                "‘Children’ is the irregular plural of ‘child’ — not ‘childs’. (పిల్లలు అనేది స్పెషల్ ప్లురల్.)",
            ),
            (
                "\"He works ___ a teacher.\" Which word completes this sentence?",
                ["as", "for", "in", "like"],
                0,
                "'works as a ___' states a job or role. (ఉద్యోగం చెప్పడానికి ఉపయోగపడుతుంది.)",
            ),
            (
                "Which sentence correctly describes a family member's job?",
                ["She works as a doctor.", "She work doctor.", "She is working doctor.", "Doctor she works."],
                0,
                "Subject 'She' needs 'works' (with -s), plus 'as a' before the job title.",
            ),
            (
                "\"My family ___ in Vijayawada.\" Which verb is correct?",
                ["lives", "live", "living", "lived"],
                0,
                "'Family' is treated as one unit in English, so it takes the singular verb 'lives'. (కుటుంబం ఒక గుంపుగా భావిస్తారు.)",
            ),
        ],
    },
    "quiz-day-3": {
        "track": "day-3-routine",
        "title": "Day 3 Quiz — Daily Routine",
        "xpReward": 30,
        "questions": [
            (
                "\"I wake up ___ six o'clock.\" Which word is correct?",
                ["at", "on", "in", "to"],
                0,
                "Use 'at' with exact clock times.",
            ),
            (
                "Which sentence is correct?",
                [
                    "I drink tea every morning.",
                    "I drink tea the every morning.",
                    "I drink every morning tea.",
                    "Every morning I am drinking tea always.",
                ],
                0,
                "'Every' already means 'each one' — no 'the' is needed before it. (‘every’ అనగా ‘ప్రతి’ అని అర్థం; ముందు ‘the’ అవసరం లేదు.)",
            ),
            (
                "\"I go to ___ market in the evening.\" Which word completes this correctly?",
                ["the", "a", "(no word needed)", "an"],
                0,
                "'the market' refers to a specific, known place both speakers have in mind.",
            ),
            (
                "Which is the correct question to ask about someone's wake-up time?",
                ["What time do you wake up?", "You wake up what time?", "What time you wake up?", "Wake up what time do you?"],
                0,
                "Question word first, then 'do you' — this order is fixed in English.",
            ),
            (
                "\"I ___ television after dinner.\" Which verb fits?",
                ["watch", "see", "look", "view"],
                0,
                "'watch television' is the natural pairing — not 'see' or 'look'.",
            ),
        ],
    },
    "quiz-day-4": {
        "track": "day-4-shopping",
        "title": "Day 4 Quiz — Numbers, Time & Shopping",
        "xpReward": 30,
        "questions": [
            (
                "How do you ask the price of something politely?",
                ["How much does this cost?", "This cost how much?", "How much this?", "What cost this is?"],
                0,
                "The standard polite way to ask a price. (ధర అడగడానికి సరైన మార్గం.)",
            ),
            (
                "\"This costs two hundred ___.\" Which word completes the sentence about Indian currency?",
                ["rupees", "a rupees", "the rupees", "rupee's"],
                0,
                "No article before a specific number — the number already says how many.",
            ),
            (
                "\"I need one kilogram ___ rice.\" Which word is missing?",
                ["of", "for", "to", "(no word needed)"],
                0,
                "'kilogram OF rice' links quantity to item — dropping 'of' is a very common mistake. (‘of’ తెలుగులో అవసరం లేకపోయినా ఇంగ్లీష్లో అవసరం.)",
            ),
            (
                "Which sentence politely asks for a lower price?",
                ["Can you give me a discount?", "Give me less price.", "Reduce the cost now.", "Discount you give?"],
                0,
                "'Can you ___?' softens the request — much more polite than a direct command.",
            ),
            (
                "\"It is half past four\" means the time is:",
                ["4:30", "4:15", "3:30", "4:45"],
                0,
                "'half past ___' means 30 minutes after that hour.",
            ),
        ],
    },
    "quiz-day-5": {
        "track": "day-5-food",
        "title": "Day 5 Quiz — Food & Ordering",
        "xpReward": 30,
        "questions": [
            (
                "Which is the most polite way to order something?",
                ["I would like a cup of coffee.", "Give me coffee.", "I want coffee now.", "Coffee bring."],
                0,
                "'I would like ___' is softer and more polite than 'I want', especially with strangers.",
            ),
            (
                "How do you ask to see the food options?",
                ["Can I have the menu, please?", "Show me food list.", "Menu give me.", "What food is there?"],
                0,
                "A polite, standard restaurant phrase. (మెనూ అడగడానికి సరైన మార్గం.)",
            ),
            (
                "\"I am ___ to peanuts\" means you cannot safely eat them.",
                ["allergic", "allergy", "allergical", "allergen"],
                0,
                "'allergic TO ___' is the correct form — 'allergy' is the noun, not the adjective used here.",
            ),
            (
                "Which sentence politely asks for the check at a restaurant?",
                ["The bill, please.", "Give bill.", "Money how much?", "Bill now."],
                0,
                "A short, polite way to ask to pay.",
            ),
            (
                "\"This food is very ___\" — which word describes a strong chili taste?",
                ["spicy", "spice", "spiced-full", "spicing"],
                0,
                "'spicy' is the adjective form — 'spice' is the noun (the ingredient itself).",
            ),
        ],
    },
    "quiz-day-6": {
        "track": "day-6-directions",
        "title": "Day 6 Quiz — Directions & Travel",
        "xpReward": 30,
        "questions": [
            (
                "How do you ask where a bus stop is?",
                ["Where is the bus stop?", "Bus stop where?", "Where bus stop is?", "Is where the bus stop?"],
                0,
                "'Where is ___?' is the fixed pattern for asking a location.",
            ),
            (
                "Which sentence gives a direction instruction?",
                ["Turn left at the next signal.", "Left turn you at signal.", "At signal left turning.", "Signal, left, turn."],
                0,
                "Direction instructions start with the action verb: 'Turn left...'",
            ),
            (
                "\"How far is the railway station?\" is asking about:",
                ["distance", "price", "time of day", "direction only"],
                0,
                "'How far' always asks about distance. (దూరం గురించి అడిగే ప్రశ్న.)",
            ),
            (
                "Which is correct when telling a driver your destination?",
                ["I want to go to the airport.", "Airport I want go.", "I want go airport.", "Go airport I want."],
                0,
                "Both 'to's are needed — 'want to go' and 'to the airport'.",
            ),
            (
                "Which phrase politely asks a driver to stop?",
                ["Please stop here.", "Stop now here.", "Here stop please now.", "Stopping here please."],
                0,
                "'Please ___' softens a direct instruction.",
            ),
        ],
    },
    "quiz-day-7": {
        "track": "day-7-health",
        "title": "Day 7 Quiz — Health & Small Talk (Week 1 Review)",
        "xpReward": 30,
        "questions": [
            (
                "How do you tell someone you have a headache?",
                ["I have a headache.", "My head is paining.", "Head pain I have.", "I am headache."],
                0,
                "'My head is paining' is a very common direct translation, but 'I have a headache' is the natural English phrase. (సహజంగా ఇలా అంటారు.)",
            ),
            (
                "Which sentence says you're unwell today?",
                ["I am not feeling well today.", "Today I am not well feeling.", "I not feel well.", "Not well I feeling today."],
                0,
                "'not feeling well' is the natural phrase for being a bit sick.",
            ),
            (
                "\"It's a beautiful day, isn't it?\" — this kind of short question at the end is called a:",
                ["tag question", "command", "request", "exclamation"],
                0,
                "Tag questions like 'isn't it?' invite agreement — common in friendly small talk, and unfamiliar to many Telugu speakers since Telugu has no direct equivalent.",
            ),
            (
                "Which phrase is a warm way to say goodbye to someone you care about?",
                ["Take care of yourself.", "Go now.", "Finish talking, bye.", "Care you take."],
                0,
                "A caring, natural way to end a conversation. (ఆత్మీయులకు చెప్పే విద్ద మాట.)",
            ),
            (
                "This week you practiced greetings, family, routines, shopping, food, and directions. Which sentence uses \"would like\" correctly?",
                [
                    "I would like some water, please.",
                    "I would like water bring.",
                    "Water I would like bring.",
                    "Bring I would like water.",
                ],
                0,
                "'I would like ___, please' — polite request pattern practiced all week.",
            ),
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
