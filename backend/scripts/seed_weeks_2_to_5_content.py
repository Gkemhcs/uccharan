"""Seeds Weeks 2-5 (Days 8-30) of the 30-day roadmap into Firestore: lessons
for each day plus one multiple-choice quiz per day.

Companion to seed_week1_content.py (Days 1-7) — see that script's docstring
for the full grounding rationale (CURRICULUM.md §8), which applies equally
here: CEFR-appropriate progression, real Telugu-L1-interference-targeted
grammar notes, and bilingual (English + Telugu) content shown to the learner
BEFORE they attempt a sentence, not just as post-mistake correction.

CEFR progression across these weeks (deliberately not flat difficulty):
  - Days 8-14 (Week 2): still mostly A1/A2 — weather, home, phone calls,
    work, money, hobbies — expanding vocabulary breadth at the same
    grammatical simplicity as Week 1.
  - Days 15-21 (Week 3): A2/B1 — introduces past tense ("Did you sleep
    well?"), future tense ("going to" vs "will"), and opinion/agreement
    language, all genuine step-ups in grammatical complexity.
  - Days 22-28 (Week 4): B1 — comparatives/superlatives, instructions,
    small talk with strangers, storytelling (past continuous).
  - Days 29-30 (Week 5, partial): B1/B2 capstone — clarification phrases
    ("Could you repeat that?") and a final review day that explicitly ties
    back to Day 1's "See you later" with "Take care of yourself", and
    points the learner at "Practice with your Tutor" for open conversation.

Telugu text here was written by Claude (not a certified native reviewer) —
correct standard, respectful (మీరు-register) Telugu to the best of that
ability, but worth a native speaker's read-through, same honesty note as
seed_week1_content.py.

Usage:
    python3 backend/scripts/seed_weeks_2_to_5_content.py
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
# Lessons — same tuple shape as seed_week1_content.py:
# (id, order, targetSentence, nativeTranslation, focusSounds, vocabWord,
#  vocabMeaning, vocabNativeMeaning, grammarNote)
# ---------------------------------------------------------------------------

DAY8_LESSONS = [
    ("day8-weather-01", 1, "It is very hot today.", "ఈ రోజు చాలా వేడిగా ఉంది.",
     ["/h/ in 'hot'"], "hot", "having a high temperature", "వేడి",
     "'It is ___' describes weather — English always needs the dummy subject 'it', even though Telugu can drop the subject entirely for weather."),
    ("day8-weather-02", 2, "I feel tired.", "నాకు అలసటగా ఉంది.",
     ["/t/ in 'tired'"], "tired", "needing rest", "అలసట",
     "'I feel ___' + adjective describes how you feel. Telugu expresses this more like 'to me, tiredness is happening' (నాకు...ఉంది) — a different sentence pattern."),
    ("day8-weather-03", 3, "It might rain tomorrow.", "రేపు వర్షం పడొచ్చు.",
     ["/m/ in 'might'"], "might", "shows something is possible, not certain", "కావచ్చు",
     "'might' is softer than 'will' — use it when you're not sure."),
    ("day8-weather-04", 4, "I am happy to see you.", "మిమ్మల్ని చూసి నాకు సంతోషంగా ఉంది.",
     ["/h/ in 'happy'"], "happy", "feeling pleased", "సంతోషం",
     "'happy to ___' is followed by the base verb form ('to see'), not '-ing'."),
    ("day8-weather-05", 5, "Don't worry, everything will be fine.", "చింతించకండి, అంతా బాగానే జరుగుతుంది.",
     ["/w/ in 'worry'"], "worry", "to feel anxious", "చింత",
     "'Don't ___' is the negative imperative — used here to comfort someone."),
]

DAY9_LESSONS = [
    ("day9-home-01", 1, "Please turn off the lights.", "దయచేసి లైట్లు ఆపండి.",
     ["/l/ in 'lights'"], "turn off", "to switch something off", "ఆపడం",
     "'turn off' is a phrasal verb — the two words work together as one meaning."),
    ("day9-home-02", 2, "The kitchen is next to the hall.", "వంటగది హాల్ పక్కన ఉంది.",
     ["/n/ in 'next'"], "next to", "beside, close to", "పక్కన",
     "'next to' is a preposition of place, showing position beside something."),
    ("day9-home-03", 3, "I need to clean the house today.", "ఈ రోజు నేను ఇల్లు శుభ్రం చేయాలి.",
     ["/k/ in 'clean'"], "clean", "to remove dirt", "శుభ్రం చేయడం",
     "'need to ___' + base verb expresses a necessity."),
    ("day9-home-04", 4, "The water is not working.", "నీళ్లు రావట్లేదు.",
     ["/w/ in 'water'"], "working", "functioning correctly", "పనిచేయడం",
     "'not working' describes something broken — used for appliances, water, electricity."),
    ("day9-home-05", 5, "Can you help me fix this?", "మీరు దీన్ని బాగు చేయడంలో సహాయం చేయగలరా?",
     ["/f/ in 'fix'"], "fix", "to repair", "బాగు చేయడం",
     "'Can you help me ___?' + base verb is a polite way to ask for help with a task."),
]

DAY10_LESSONS = [
    ("day10-phone-01", 1, "Hello, may I speak to Ravi?", "హలో, నేను రవితో మాట్లాడవచ్చా?",
     ["/m/ in 'may'"], "speak to", "to talk with someone", "మాట్లాడటం",
     "'May I ___?' politely asks permission — a common way to start a phone call."),
    ("day10-phone-02", 2, "Sorry, wrong number.", "క్షమించండి, తప్పు నంబర్.",
     ["/r/ in 'wrong'"], "wrong number", "a mistakenly dialed number", "తప్పు నంబర్",
     "A short, standard phrase for a misdialed call."),
    ("day10-phone-03", 3, "Please call me back later.", "దయచేసి తర్వాత నాకు తిరిగి కాల్ చేయండి.",
     ["/b/ in 'back'"], "call back", "to return a phone call", "తిరిగి కాల్ చేయడం",
     "'call back' — another phrasal verb, common in phone conversations."),
    ("day10-phone-04", 4, "I will send you a message.", "నేను మీకు మెసేజ్ పంపిస్తాను.",
     ["/m/ in 'message'"], "message", "a short written note", "సందేశం",
     "'will' is used for a decision made right at the moment of speaking."),
    ("day10-phone-05", 5, "My phone battery is low.", "నా ఫోన్ బ్యాటరీ తక్కువగా ఉంది.",
     ["/b/ in 'battery'"], "battery", "the power source of a device", "బ్యాటరీ",
     "'is low' describes a battery close to running out."),
]

DAY11_LESSONS = [
    ("day11-work-01", 1, "What do you do for work?", "మీరు ఏం పని చేస్తారు?",
     ["/w/ in 'work'"], "work", "a job or occupation", "పని",
     "'What do you do?' asks about someone's job/profession, not a one-time action."),
    ("day11-work-02", 2, "I work in a bank.", "నేను బ్యాంకులో పని చేస్తాను.",
     ["/b/ in 'bank'"], "bank", "a place that handles money", "బ్యాంకు",
     "'work in a ___' names your workplace."),
    ("day11-work-03", 3, "I start work at nine every day.", "నేను ప్రతిరోజు తొమ్మిది గంటలకు పని మొదలుపెడతాను.",
     ["/s/ in 'start'"], "start", "to begin", "మొదలుపెట్టడం",
     "'start work at ___' + time states a daily routine — like Day 3's 'wake up at six'."),
    ("day11-work-04", 4, "My colleague is very helpful.", "నా సహోద్యోగి చాలా సహాయకారి.",
     ["/k/ in 'colleague'"], "colleague", "someone you work with", "సహోద్యోగి",
     "'colleague' — a workplace-specific word for 'someone I work with'."),
    ("day11-work-05", 5, "I am looking for a new job.", "నేను కొత్త ఉద్యోగం కోసం చూస్తున్నాను.",
     ["/dʒ/ in 'job'"], "job", "paid work", "ఉద్యోగం",
     "'am looking for' — present continuous, shows an ongoing search."),
]

DAY12_LESSONS = [
    ("day12-money-01", 1, "I would like to open a bank account.", "నేను బ్యాంక్ ఖాతా తెరవాలనుకుంటున్నాను.",
     ["/b/ in 'bank'"], "bank account", "an account for keeping money", "బ్యాంక్ ఖాతా",
     "'would like to ___' — the polite request pattern from Day 5, reused here."),
    ("day12-money-02", 2, "Where is the nearest ATM?", "దగ్గరలో ATM ఎక్కడ ఉంది?",
     ["/n/ in 'nearest'"], "nearest", "closest in distance", "దగ్గరలో ఉన్న",
     "'the nearest ___' asks for the closest option — very useful when traveling."),
    ("day12-money-03", 3, "I need to withdraw some money.", "నాకు కొంత డబ్బు తీసుకోవాలి.",
     ["/w/ in 'withdraw'"], "withdraw", "to take money out of an account", "డబ్బు తీసుకోవడం",
     "'need to ___' — same necessity pattern as Day 9's 'need to clean'."),
    ("day12-money-04", 4, "Can I pay by card?", "నేను కార్డ్‌తో చెల్లించవచ్చా?",
     ["/p/ in 'pay'"], "pay", "to give money for something", "చెల్లించడం",
     "'pay by ___' names the payment method."),
    ("day12-money-05", 5, "Please keep the change.", "మిగిలిన డబ్బు మీరే ఉంచుకోండి.",
     ["/tʃ/ in 'change'"], "change", "money returned after a payment", "చిల్లర",
     "A polite phrase telling someone they can keep the extra money."),
]

DAY13_LESSONS = [
    ("day13-hobbies-01", 1, "What do you like to do in your free time?", "మీ ఖాళీ సమయంలో మీకు ఏమి చేయడం ఇష్టం?",
     ["/f/ in 'free'"], "free time", "time with no work or obligations", "ఖాళీ సమయం",
     "A friendly, common small-talk question."),
    ("day13-hobbies-02", 2, "I enjoy gardening on weekends.", "నాకు వారాంతాల్లో తోటపని చేయడం ఇష్టం.",
     ["/g/ in 'gardening'"], "gardening", "growing and caring for plants", "తోటపని",
     "'enjoy' is followed by '-ing', not 'to' — 'enjoy gardening', not 'enjoy to garden'."),
    ("day13-hobbies-03", 3, "I like listening to music.", "నాకు పాటలు వినడం ఇష్టం.",
     ["/m/ in 'music'"], "listening", "paying attention to sound", "వినడం",
     "'listen to ___' — 'to' is needed after 'listen', unlike 'watch' (no 'to')."),
    ("day13-hobbies-04", 4, "Do you play any sports?", "మీరు ఏదైనా ఆటలు ఆడతారా?",
     ["/s/ in 'sports'"], "sports", "physical games and activities", "ఆటలు",
     "'Do you ___?' — the standard yes/no question form."),
    ("day13-hobbies-05", 5, "I have been learning English for two months.", "నేను రెండు నెలలుగా ఇంగ్లీష్ నేర్చుకుంటున్నాను.",
     ["/l/ in 'learning'"], "learning", "gaining knowledge or skill", "నేర్చుకోవడం",
     "'have been ___ing' shows an action that started in the past and is still continuing — a new, useful pattern to notice."),
]

DAY14_LESSONS = [
    ("day14-plans-01", 1, "Are you free this weekend?", "ఈ వారాంతంలో మీరు ఖాళీగా ఉన్నారా?",
     ["/w/ in 'weekend'"], "free", "not busy, available", "ఖాళీ",
     "'Are you free ___?' is how you check someone's availability before making plans."),
    ("day14-plans-02", 2, "Let's meet at the park at five.", "పార్క్ దగ్గర ఐదు గంటలకు కలుద్దాం.",
     ["/p/ in 'park'"], "meet", "to come together with someone", "కలవడం",
     "'Let's ___' suggests doing something together."),
    ("day14-plans-03", 3, "I am going to visit my parents next week.", "వచ్చే వారం నేను నా తల్లిదండ్రులను చూడటానికి వెళ్తున్నాను.",
     ["/v/ in 'visit'"], "visit", "to go see someone or somewhere", "చూడటానికి వెళ్లడం",
     "'going to' expresses a plan already decided — different from 'will' (a decision made right now)."),
    ("day14-plans-04", 4, "Can we reschedule to another day?", "మనం వేరే రోజుకు మార్చుకోవచ్చా?",
     ["/r/ in 'reschedule'"], "reschedule", "to change a planned time", "మార్చుకోవడం",
     "A polite way to ask to change a plan."),
    ("day14-plans-05", 5, "See you then!", "అప్పుడు కలుద్దాం!",
     ["/ð/ in 'then'"], "then", "at that time", "అప్పుడు",
     "A casual closing once a plan is set — a nice bookend for this week's theme of making plans."),
]

DAY15_LESSONS = [
    ("day15-describe-01", 1, "She is tall and friendly.", "ఆమె పొడుగ్గా మరియు స్నేహపూర్వకంగా ఉంటుంది.",
     ["/f/ in 'friendly'"], "friendly", "kind and pleasant", "స్నేహపూర్వక",
     "Two adjectives joined with 'and' describe a person."),
    ("day15-describe-02", 2, "This bag is bigger than that one.", "ఈ బ్యాగ్ ఆ దానికంటే పెద్దది.",
     ["/b/ in 'bigger'"], "bigger", "larger in size", "పెద్దది",
     "'bigger than' — comparative form ('-er') plus 'than', used to compare two things."),
    ("day15-describe-03", 3, "He has short black hair.", "అతనికి పొట్టి నల్లని జుట్టు ఉంది.",
     ["/h/ in 'hair'"], "hair", "the growth on a person's head", "జుట్టు",
     "'has ___ hair' — two adjectives before 'hair' describe length and color."),
    ("day15-describe-04", 4, "This is a very useful tool.", "ఇది చాలా ఉపయోగకరమైన పరికరం.",
     ["/juː/ in 'useful'"], "useful", "helpful, practical", "ఉపయోగకరమైన",
     "'very' + adjective intensifies a description."),
    ("day15-describe-05", 5, "She looks happy today.", "ఈ రోజు ఆమె సంతోషంగా కనిపిస్తోంది.",
     ["/l/ in 'looks'"], "looks", "appears to be", "కనిపించడం",
     "'looks + adjective' describes appearance — 'looks happy', not 'looks like happy'."),
]

DAY16_LESSONS = [
    ("day16-past-01", 1, "I went to the market yesterday.", "నేను నిన్న మార్కెట్‌కి వెళ్ళాను.",
     ["/w/ in 'went'"], "went", "past tense of 'go'", "వెళ్ళాను",
     "'went' is the irregular past tense of 'go' — English past tense often changes the word itself, not just adds an ending."),
    ("day16-past-02", 2, "Did you sleep well last night?", "మీరు నిన్న రాత్రి బాగా నిద్రపోయారా?",
     ["/d/ in 'did'"], "last night", "the night before today", "నిన్న రాత్రి",
     "Past-tense questions use 'Did you ___?' plus the BASE verb ('sleep'), not the past form — 'Did you slept?' is a common mistake to avoid."),
    ("day16-past-03", 3, "I did not finish my work yesterday.", "నేను నిన్న నా పని పూర్తి చేయలేదు.",
     ["/f/ in 'finish'"], "finish", "to complete something", "పూర్తి చేయడం",
     "'did not' + base verb forms the negative past — 'did not finish', not 'did not finished'."),
    ("day16-past-04", 4, "We had a great time at the wedding.", "మేము పెళ్ళిలో చాలా బాగా గడిపాము.",
     ["/w/ in 'wedding'"], "wedding", "a marriage ceremony", "పెళ్ళి",
     "'had a great time' — a fixed phrase for enjoying an event."),
    ("day16-past-05", 5, "I was very busy last week.", "నేను గత వారం చాలా బిజీగా ఉన్నాను.",
     ["/b/ in 'busy'"], "busy", "having a lot to do", "బిజీ",
     "'was' is the past tense of 'am/is' — used with 'I', 'he', 'she', 'it'."),
]

DAY17_LESSONS = [
    ("day17-future-01", 1, "I will call you tomorrow.", "నేను రేపు మీకు కాల్ చేస్తాను.",
     ["/t/ in 'tomorrow'"], "tomorrow", "the day after today", "రేపు",
     "'will' + base verb — a simple future decision or promise."),
    ("day17-future-02", 2, "We are going to travel next month.", "మేము వచ్చే నెల ప్రయాణం చేయబోతున్నాము.",
     ["/tr/ in 'travel'"], "travel", "to go from one place to another", "ప్రయాణం",
     "'going to' — for a plan already decided, unlike spontaneous 'will'."),
    ("day17-future-03", 3, "I hope to finish this by Friday.", "శుక్రవారం లోపు దీన్ని పూర్తి చేయాలని ఆశిస్తున్నాను.",
     ["/h/ in 'hope'"], "hope", "to wish for something to happen", "ఆశించడం",
     "'hope to ___' expresses a wish about the future."),
    ("day17-future-04", 4, "The train leaves at 6 PM.", "రైలు సాయంత్రం 6 గంటలకు బయలుదేరుతుంది.",
     ["/tr/ in 'train'"], "leaves", "departs", "బయలుదేరడం",
     "Present tense ('leaves') is used for fixed schedules/timetables, even though it's about the future."),
    ("day17-future-05", 5, "I am sure everything will go well.", "అంతా బాగా జరుగుతుందని నాకు నమ్మకం ఉంది.",
     ["/ʃ/ in 'sure'"], "sure", "certain, confident", "నమ్మకం",
     "'I am sure ___' expresses confidence about a future outcome."),
]

DAY18_LESSONS = [
    ("day18-opinions-01", 1, "I think this is a good idea.", "ఇది మంచి ఆలోచన అని నేను అనుకుంటున్నాను.",
     ["/aɪ/ in 'idea'"], "idea", "a thought or plan", "ఆలోచన",
     "'I think ___' introduces an opinion — a softer way to state a view than a flat statement."),
    ("day18-opinions-02", 2, "I agree with you.", "నేను మీతో ఏకీభవిస్తున్నాను.",
     ["/g/ in 'agree'"], "agree", "to share the same opinion", "ఏకీభవించడం",
     "'agree with ___' names who you agree with."),
    ("day18-opinions-03", 3, "I am not sure about that.", "దాని గురించి నాకు ఖచ్చితంగా తెలియదు.",
     ["/ʃ/ in 'sure'"], "not sure", "uncertain, doubtful", "ఖచ్చితంగా తెలియదు",
     "A gentle way to disagree or express doubt without sounding rude."),
    ("day18-opinions-04", 4, "In my opinion, it is better to wait.", "నా అభిప్రాయం ప్రకారం, వేచి ఉండటం మంచిది.",
     ["/ə/ in 'opinion'"], "opinion", "a personal view or belief", "అభిప్రాయం",
     "'In my opinion, ___' is a formal way to introduce a personal view."),
    ("day18-opinions-05", 5, "That's a fair point, but I see it differently.", "అది సరైన విషయమే, కానీ నేను దీన్ని వేరేలా చూస్తున్నాను.",
     ["/f/ in 'fair'"], "differently", "in another way", "వేరేలా",
     "A polite way to disagree — acknowledge the other person's point first, then share your own view."),
]

DAY19_LESSONS = [
    ("day19-doctor-01", 1, "I have a fever since yesterday.", "నిన్నటి నుండి నాకు జ్వరం వస్తోంది.",
     ["/f/ in 'fever'"], "fever", "a higher than normal body temperature", "జ్వరం",
     "'since yesterday' — 'since' plus a starting point in time, showing something continuing from then until now."),
    ("day19-doctor-02", 2, "Do I need a prescription for this?", "దీనికి ప్రిస్క్రిప్షన్ కావాలా?",
     ["/p/ in 'prescription'"], "prescription", "a doctor's written medicine order", "మందుల చీటీ",
     "'Do I need ___?' checks a requirement before buying medicine."),
    ("day19-doctor-03", 3, "How many times a day should I take this?", "దీన్ని రోజుకి ఎన్నిసార్లు తీసుకోవాలి?",
     ["/t/ in 'take'"], "take", "to consume (medicine)", "తీసుకోవడం",
     "'How many times a day' asks about dosage frequency — an important phrase to know."),
    ("day19-doctor-04", 4, "I am allergic to this medicine.", "నాకు ఈ మందు పడదు.",
     ["/dʒ/ in 'allergic'"], "medicine", "a substance used for treatment", "మందు",
     "'allergic to ___' — reused from Day 5's peanut allergy example, now for medicine, a genuinely important safety phrase."),
    ("day19-doctor-05", 5, "Please take rest and drink plenty of water.", "దయచేసి విశ్రాంతి తీసుకోండి మరియు ఎక్కువ నీళ్లు తాగండి.",
     ["/r/ in 'rest'"], "rest", "relaxation, sleep", "విశ్రాంతి",
     "Common advice a doctor gives — two instructions joined with 'and'."),
]

DAY20_LESSONS = [
    ("day20-festivals-01", 1, "We celebrate Sankranti with our family.", "మేము మా కుటుంబంతో సంక్రాంతి జరుపుకుంటాము.",
     ["/s/ in 'celebrate'"], "celebrate", "to mark a special occasion", "జరుపుకోవడం",
     "'celebrate ___ with ___' names the festival and who you share it with."),
    ("day20-festivals-02", 2, "Happy Ugadi! Wish you a wonderful year.", "ఉగాది శుభాకాంక్షలు! మీకు అద్భుతమైన సంవత్సరం రావాలని కోరుకుంటున్నాను.",
     ["/w/ in 'wish'"], "wish", "to hope for someone's happiness or success", "కోరుకోవడం",
     "'Happy ___!' is the standard festival greeting pattern in English."),
    ("day20-festivals-03", 3, "The whole street is decorated with lights.", "వీధి మొత్తం లైట్లతో అలంకరించబడింది.",
     ["/d/ in 'decorated'"], "decorated", "made to look attractive for an occasion", "అలంకరించబడింది",
     "'is decorated with ___' — passive voice, describing something done to the street."),
    ("day20-festivals-04", 4, "We usually visit the temple during festivals.", "పండుగల సమయంలో మేము సాధారణంగా గుడికి వెళ్తాము.",
     ["/t/ in 'temple'"], "temple", "a place of worship", "గుడి",
     "'usually' shows a habitual action — placed before the main verb."),
    ("day20-festivals-05", 5, "Thank you for inviting us to the celebration.", "వేడుకకు మమ్మల్ని ఆహ్వానించినందుకు ధన్యవాదాలు.",
     ["/v/ in 'inviting'"], "inviting", "asking someone to attend", "ఆహ్వానించడం",
     "'Thank you for ___ing' — gerund after 'for', not 'Thank you to invite'."),
]

DAY21_LESSONS = [
    ("day21-neighbors-01", 1, "My neighbor is very friendly and helpful.", "నా పొరుగువాడు చాలా స్నేహపూర్వకంగా మరియు సహాయకారిగా ఉంటాడు.",
     ["/n/ in 'neighbor'"], "neighbor", "someone who lives nearby", "పొరుగువాడు",
     "Review: two adjectives joined with 'and', same pattern as Day 15."),
    ("day21-neighbors-02", 2, "We take turns cleaning the street.", "మేము వంతుల వారీగా వీధిని శుభ్రం చేస్తాము.",
     ["/t/ in 'turns'"], "take turns", "to do something one after another", "వంతుల వారీగా చేయడం",
     "'take turns ___ing' describes sharing a task by rotation."),
    ("day21-neighbors-03", 3, "There was a small function in our community hall.", "మా కమ్యూనిటీ హాల్‌లో చిన్న ఫంక్షన్ జరిగింది.",
     ["/k/ in 'community'"], "community", "a group of people living in one area", "సంఘం",
     "Review: past tense 'was' — a short event description, like Day 16's wedding sentence."),
    ("day21-neighbors-04", 4, "Could you keep an eye on my house while I'm away?", "నేను లేనప్పుడు మా ఇంటిని కొంచెం చూస్తారా?",
     ["/aɪ/ in 'eye'"], "keep an eye on", "to watch over something", "చూసుకోవడం",
     "'keep an eye on' is an idiom meaning 'watch over' — not literal."),
    ("day21-neighbors-05", 5, "We look out for each other in this neighborhood.", "మా ఈ ప్రాంతంలో మేము ఒకరికొకరు సహాయంగా ఉంటాము.",
     ["/l/ in 'look'"], "look out for", "to take care of, watch over", "సహాయంగా ఉండటం",
     "Another idiom — 'look out for each other' means to support and protect one another."),
]

DAY22_LESSONS = [
    ("day22-help-01", 1, "Could you please help me carry this?", "దయచేసి దీన్ని మోయడంలో సహాయం చేస్తారా?",
     ["/k/ in 'carry'"], "carry", "to hold and move something", "మోయడం",
     "'Could you please ___?' is an even more polite request form than 'Can you ___?'."),
    ("day22-help-02", 2, "First, switch on the machine, then press this button.", "మొదట మెషిన్ ఆన్ చేయండి, తర్వాత ఈ బటన్ నొక్కండి.",
     ["/tʃ/ in 'switch'"], "switch on", "to turn on", "ఆన్ చేయడం",
     "'First..., then...' sequences instructions clearly — a very useful pattern for giving directions or steps."),
    ("day22-help-03", 3, "I don't know how to use this app.", "ఈ యాప్‌ని ఎలా ఉపయోగించాలో నాకు తెలియదు.",
     ["/juː/ in 'use'"], "use", "to operate or make use of", "ఉపయోగించడం",
     "'don't know how to ___' expresses a lack of skill or knowledge."),
    ("day22-help-04", 4, "Can you show me how to do this?", "దీన్ని ఎలా చేయాలో మీరు నాకు చూపిస్తారా?",
     ["/ʃ/ in 'show'"], "show", "to demonstrate", "చూపించడం",
     "'show me how to ___' asks for a demonstration, not just an explanation."),
    ("day22-help-05", 5, "Thanks a lot, that was really helpful.", "చాలా ధన్యవాదాలు, అది నిజంగా సహాయకారిగా ఉంది.",
     ["/h/ in 'helpful'"], "helpful", "giving useful assistance", "సహాయకారి",
     "A warm way to close a request for help."),
]

DAY23_LESSONS = [
    ("day23-compare-01", 1, "This phone is cheaper than that one.", "ఈ ఫోన్ ఆ దానికంటే చౌక.",
     ["/tʃ/ in 'cheaper'"], "cheaper", "lower in price", "చౌక",
     "Review: comparative + 'than', same pattern as Day 15's 'bigger than'."),
    ("day23-compare-02", 2, "This is the best restaurant in town.", "ఇది ఊర్లోనే బెస్ట్ రెస్టారెంట్.",
     ["/b/ in 'best'"], "best", "the highest quality", "అత్యుత్తమ",
     "'the best' is the superlative form — used when comparing three or more things, not just two."),
    ("day23-compare-03", 3, "My new job is more interesting than my old one.", "నా కొత్త ఉద్యోగం పాత దాని కంటే ఆసక్తికరంగా ఉంది.",
     ["/ɪ/ in 'interesting'"], "interesting", "holding your attention", "ఆసక్తికరం",
     "Longer adjectives use 'more ___ than' instead of adding '-er' — 'more interesting', not 'interestinger'."),
    ("day23-compare-04", 4, "This one is as good as that one.", "ఇది ఆ దానితో సమానంగా బాగుంది.",
     ["/ɡ/ in 'good'"], "as good as", "equal in quality to", "సమానంగా బాగుండటం",
     "'as ___ as' compares two things as equal, a third comparison pattern alongside comparatives and superlatives."),
    ("day23-compare-05", 5, "Which one is faster, the bus or the train?", "బస్సు, రైలు రెండింటిలో ఏది వేగంగా ఉంటుంది?",
     ["/f/ in 'faster'"], "faster", "moving at greater speed", "వేగంగా",
     "'Which one is ___?' asks someone to choose between two named options."),
]

DAY24_LESSONS = [
    ("day24-emotions-01", 1, "I am a little nervous about the interview.", "ఇంటర్వ్యూ గురించి నాకు కొంచెం ఆందోళనగా ఉంది.",
     ["/n/ in 'nervous'"], "nervous", "anxious, worried", "ఆందోళన",
     "'a little ___' softens an adjective — less intense than just 'nervous'."),
    ("day24-emotions-02", 2, "Don't be afraid, I am here with you.", "భయపడకు, నేను నీతోనే ఉన్నాను.",
     ["/f/ in 'afraid'"], "afraid", "feeling fear", "భయం",
     "A comforting phrase — 'Don't be ___' plus reassurance."),
    ("day24-emotions-03", 3, "It's okay to make mistakes while learning.", "నేర్చుకునేటప్పుడు తప్పులు చేయడం పర్వాలేదు.",
     ["/m/ in 'mistakes'"], "mistakes", "errors", "తప్పులు",
     "A gentle, encouraging sentence — genuinely useful for a learner to hear and to say to themselves."),
    ("day24-emotions-04", 4, "I feel much better now, thank you.", "ఇప్పుడు నాకు చాలా బాగుంది, ధన్యవాదాలు.",
     ["/b/ in 'better'"], "better", "improved, in a more positive state", "మెరుగు",
     "'much better' — 'much' intensifies a comparative like 'better'."),
    ("day24-emotions-05", 5, "Take a deep breath, you are doing great.", "గట్టిగా ఊపిరి పీల్చుకో, నువ్వు చాలా బాగా చేస్తున్నావు.",
     ["/b/ in 'breath'"], "deep breath", "a long, calming inhale", "గట్టి ఊపిరి",
     "An encouraging phrase, useful in both calming and cheering someone on."),
]

DAY25_LESSONS = [
    ("day25-tech-01", 1, "My laptop is not turning on.", "నా ల్యాప్‌టాప్ ఆన్ కావట్లేదు.",
     ["/l/ in 'laptop'"], "laptop", "a portable computer", "ల్యాప్‌టాప్",
     "Review: 'not ___ing' describes something not functioning, same pattern as Day 9's 'not working'."),
    ("day25-tech-02", 2, "Can you connect to the WiFi?", "మీరు వైఫైకి కనెక్ట్ అవ్వగలరా?",
     ["/k/ in 'connect'"], "connect", "to join or link to a network", "కనెక్ట్ అవ్వడం",
     "'connect to ___' names what you're joining."),
    ("day25-tech-03", 3, "Please charge your phone before we leave.", "మనం బయలుదేరే ముందు మీ ఫోన్ ఛార్జ్ చేసుకోండి.",
     ["/tʃ/ in 'charge'"], "charge", "to add power to a battery", "ఛార్జ్ చేయడం",
     "'before we leave' — 'before' + a future event, giving a deadline."),
    ("day25-tech-04", 4, "I forgot my password again.", "నేను మళ్ళీ నా పాస్‌వర్డ్ మర్చిపోయాను.",
     ["/p/ in 'password'"], "password", "a secret code for access", "పాస్‌వర్డ్",
     "'forgot' — irregular past tense of 'forget'."),
    ("day25-tech-05", 5, "This app is very easy to use.", "ఈ యాప్ ఉపయోగించడం చాలా సులభం.",
     ["/iː/ in 'easy'"], "easy", "not difficult", "సులభం",
     "'easy to ___' + base verb describes how simple an action is."),
]

DAY26_LESSONS = [
    ("day26-travel-01", 1, "I would like to book two tickets to Hyderabad.", "నేను హైదరాబాద్‌కు రెండు టిక్కెట్లు బుక్ చేసుకోవాలనుకుంటున్నాను.",
     ["/b/ in 'book'"], "book", "to reserve", "బుక్ చేసుకోవడం",
     "Review: 'would like to ___', the polite request pattern used all through this roadmap."),
    ("day26-travel-02", 2, "What time does the bus depart?", "బస్సు ఎన్ని గంటలకు బయలుదేరుతుంది?",
     ["/d/ in 'depart'"], "depart", "to leave, set off", "బయలుదేరడం",
     "'depart' is a slightly more formal word for 'leave', common at stations/airports."),
    ("day26-travel-03", 3, "Is there a direct train to Vijayawada?", "విజయవాడకు డైరెక్ట్ రైలు ఉందా?",
     ["/d/ in 'direct'"], "direct", "going straight to a destination, no changes", "నేరుగా",
     "'Is there a ___?' checks if something exists/is available."),
    ("day26-travel-04", 4, "How long does the journey take?", "ప్రయాణం ఎంత సమయం పడుతుంది?",
     ["/dʒ/ in 'journey'"], "journey", "a trip from one place to another", "ప్రయాణం",
     "'How long does ___ take?' asks about duration."),
    ("day26-travel-05", 5, "Please confirm my seat number.", "దయచేసి నా సీట్ నంబర్ కన్ఫర్మ్ చేయండి.",
     ["/k/ in 'confirm'"], "confirm", "to verify or make certain", "కన్ఫర్మ్ చేయడం",
     "A short, practical request common at ticket counters."),
]

DAY27_LESSONS = [
    ("day27-smalltalk-01", 1, "Excuse me, is this seat taken?", "క్షమించండి, ఈ సీటు ఎవరైనా తీసుకున్నారా?",
     ["/s/ in 'seat'"], "taken", "already in use/occupied", "తీసుకున్న",
     "'Excuse me, ___?' politely opens a conversation with a stranger."),
    ("day27-smalltalk-02", 2, "Lovely weather today, isn't it?", "ఈ రోజు వాతావరణం చాలా బాగుంది, కదా?",
     ["/w/ in 'weather'"], "weather", "the day's atmospheric conditions", "వాతావరణం",
     "Review: the tag question pattern from Day 7 ('isn't it?') — very common in small talk with strangers."),
    ("day27-smalltalk-03", 3, "Do you come here often?", "మీరు ఇక్కడికి తరచుగా వస్తుంటారా?",
     ["/ɒ/ in 'often'"], "often", "many times, frequently", "తరచుగా",
     "A common, friendly small-talk question."),
    ("day27-smalltalk-04", 4, "It was nice chatting with you.", "మీతో మాట్లాడటం బాగుంది.",
     ["/tʃ/ in 'chatting'"], "chatting", "having an informal conversation", "మాట్లాడటం",
     "Review: past tense closing phrase, echoing Day 1's 'It was nice talking to you.'"),
    ("day27-smalltalk-05", 5, "Have a safe journey!", "సురక్షితమైన ప్రయాణం జరగాలి!",
     ["/s/ in 'safe'"], "safe", "free from danger", "సురక్షితం",
     "A warm parting phrase for someone about to travel."),
]

DAY28_LESSONS = [
    ("day28-story-01", 1, "Once, I got lost in a new city.", "ఒకసారి, నేను కొత్త నగరంలో దారి తప్పిపోయాను.",
     ["/w/ in 'once'"], "got lost", "became unable to find your way", "దారి తప్పిపోవడం",
     "'Once, ___' is a classic way to open a short personal story."),
    ("day28-story-02", 2, "It was raining heavily that day.", "ఆ రోజు గట్టిగా వర్షం పడుతోంది.",
     ["/r/ in 'raining'"], "heavily", "with great intensity", "గట్టిగా",
     "'was raining' — past continuous, describes an action in progress at a specific past moment, useful for setting a story's scene."),
    ("day28-story-03", 3, "Suddenly, someone offered to help me.", "అకస్మాత్తుగా, ఎవరో నాకు సహాయం చేస్తానని అన్నారు.",
     ["/s/ in 'suddenly'"], "suddenly", "quickly and unexpectedly", "అకస్మాత్తుగా",
     "'Suddenly, ___' signals a turning point in a story."),
    ("day28-story-04", 4, "In the end, everything turned out fine.", "చివరికి, అంతా బాగానే జరిగింది.",
     ["/ɛ/ in 'end'"], "turned out", "ended up being (a certain way)", "ఫలితం అయ్యింది",
     "'In the end, ___' introduces how a story concludes."),
    ("day28-story-05", 5, "That experience taught me to stay calm.", "ఆ అనుభవం నాకు ప్రశాంతంగా ఉండటం నేర్పింది.",
     ["/ɪ/ in 'experience'"], "experience", "something that happened to you", "అనుభవం",
     "A reflective closing line — what a story taught you."),
]

DAY29_LESSONS = [
    ("day29-clarify-01", 1, "Sorry, could you repeat that, please?", "క్షమించండి, దయచేసి మళ్ళీ చెప్తారా?",
     ["/r/ in 'repeat'"], "repeat", "to say again", "మళ్ళీ చెప్పడం",
     "A polite, essential phrase for when you miss something."),
    ("day29-clarify-02", 2, "I didn't quite catch that.", "నాకు అది సరిగ్గా అర్థం కాలేదు.",
     ["/k/ in 'catch'"], "catch", "to understand, in this informal sense", "అర్థం చేసుకోవడం",
     "'catch' here means 'understand', not 'grab' — a common informal usage."),
    ("day29-clarify-03", 3, "Could you speak a little slower, please?", "దయచేసి కొంచెం నెమ్మదిగా మాట్లాడతారా?",
     ["/s/ in 'slower'"], "slower", "at a reduced speed", "నెమ్మదిగా",
     "A calm, polite request that helps a lot when listening is hard."),
    ("day29-clarify-04", 4, "What I meant was this.", "నేను చెప్పదలచుకున్నది ఇది.",
     ["/m/ in 'meant'"], "meant", "past tense of 'mean' — intended to say", "చెప్పదలచుకున్నది",
     "'What I meant was ___' clarifies your own earlier statement."),
    ("day29-clarify-05", 5, "Sorry for the confusion, let me explain again.", "గందరగోళానికి క్షమించండి, నేను మళ్ళీ వివరిస్తాను.",
     ["/k/ in 'confusion'"], "explain", "to make something clear", "వివరించడం",
     "A graceful way to acknowledge a misunderstanding and try again."),
]

DAY30_LESSONS = [
    ("day30-final-01", 1, "I have learned so much this month.", "ఈ నెలలో నేను చాలా నేర్చుకున్నాను.",
     ["/l/ in 'learned'"], "learned", "gained knowledge or skill", "నేర్చుకున్నాను",
     "'have learned' — present perfect, connects a past month of practice to how you feel right now."),
    ("day30-final-02", 2, "I feel more confident speaking English now.", "ఇప్పుడు ఇంగ్లీష్ మాట్లాడటంలో నాకు ఎక్కువ నమ్మకం వచ్చింది.",
     ["/k/ in 'confident'"], "confident", "self-assured, sure of yourself", "నమ్మకం",
     "The whole point of this month — this sentence names it directly."),
    ("day30-final-03", 3, "Practice makes a person perfect.", "అభ్యాసం మనిషిని పరిపూర్ణుడిని చేస్తుంది.",
     ["/p/ in 'practice'"], "practice", "repeated exercise to improve a skill", "అభ్యాసం",
     "A well-known encouraging saying — good to end the roadmap on."),
    ("day30-final-04", 4, "I will keep practicing every day.", "నేను ప్రతిరోజు అభ్యాసం చేస్తూనే ఉంటాను.",
     ["/k/ in 'keep'"], "keep practicing", "to continue practicing", "అభ్యాసం చేస్తూ ఉండటం",
     "'keep ___ing' expresses continuing an action — a commitment to keep going."),
    ("day30-final-05", 5, "Thank you for helping me learn.", "నన్ను నేర్చుకోవడంలో సహాయం చేసినందుకు ధన్యవాదాలు.",
     ["/h/ in 'helping'"], "helping", "assisting", "సహాయం చేయడం",
     "'Thank you for ___ing' — gerund after 'for', review from Day 20. A warm closing line for the whole roadmap — and a natural moment to try 'Practice with your Tutor' for open conversation."),
]

DAYS = [
    ("day-8-weather", "A1/A2", "Weather & Feelings", DAY8_LESSONS),
    ("day-9-home", "A1/A2", "Home & Household", DAY9_LESSONS),
    ("day-10-phone", "A1/A2", "Phone Calls & Messages", DAY10_LESSONS),
    ("day-11-work", "A2", "Work & Occupations", DAY11_LESSONS),
    ("day-12-money", "A2", "Money & Banking", DAY12_LESSONS),
    ("day-13-hobbies", "A2", "Hobbies & Free Time", DAY13_LESSONS),
    ("day-14-plans", "A2", "Making Plans (Week 2 review)", DAY14_LESSONS),
    ("day-15-describing", "A2", "Describing People & Things", DAY15_LESSONS),
    ("day-16-past", "A2/B1", "Past Events — Talking About Yesterday", DAY16_LESSONS),
    ("day-17-future", "A2/B1", "Future Plans — Talking About Tomorrow", DAY17_LESSONS),
    ("day-18-opinions", "B1", "Giving Opinions & Agreeing/Disagreeing Politely", DAY18_LESSONS),
    ("day-19-doctor", "A2/B1", "At the Doctor & Pharmacy", DAY19_LESSONS),
    ("day-20-festivals", "A2/B1", "Festivals & Celebrations", DAY20_LESSONS),
    ("day-21-neighbors", "B1", "Neighbors & Community (Week 3 review)", DAY21_LESSONS),
    ("day-22-help", "B1", "Asking for Help & Giving Instructions", DAY22_LESSONS),
    ("day-23-comparing", "B1", "Comparing Things (bigger, cheaper, better)", DAY23_LESSONS),
    ("day-24-emotions", "B1", "Emotions & Comfort — Talking About Feelings", DAY24_LESSONS),
    ("day-25-technology", "B1", "Technology & Everyday Devices", DAY25_LESSONS),
    ("day-26-travel", "B1", "Travel & Booking Tickets", DAY26_LESSONS),
    ("day-27-strangers", "B1", "Small Talk With Strangers", DAY27_LESSONS),
    ("day-28-story", "B1/B2", "Telling a Short Story", DAY28_LESSONS),
    ("day-29-clarify", "B1/B2", "Handling Misunderstandings", DAY29_LESSONS),
    ("day-30-final", "B1/B2", "Putting It All Together — Free Conversation (Final review)", DAY30_LESSONS),
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
# Quizzes — one per day, 5 multiple-choice questions each. Same bilingual-
# explanation principle as seed_week1_content.py.
# ---------------------------------------------------------------------------

QUIZZES = {
    "quiz-day-8": {
        "track": "day-8-weather", "title": "Day 8 Quiz — Weather & Feelings", "xpReward": 30,
        "questions": [
            ("\"It ___ very hot today.\" Which word is correct?", ["is", "has", "does", "are"], 0,
             "Weather sentences always use the dummy subject 'it' + 'is'."),
            ("Which word best fits: \"I feel ___\" (exhausted)?", ["tired", "tire", "tiring", "tiredly"], 0,
             "'tired' is the adjective form used after 'feel'."),
            ("\"It ___ rain tomorrow\" (possible, not certain).", ["might", "is", "does", "was"], 0,
             "'might' shows possibility, softer than 'will'."),
            ("Which sentence is correct?", ["I am happy to see you.", "I am happy for seeing you.", "I happy to see you.", "Happy I am to see you."], 0,
             "'happy to ___' takes the base verb form."),
            ("\"Don't worry, everything will be ___.\"", ["fine", "fined", "finely", "fining"], 0,
             "'fine' is the simple adjective used in this comforting phrase."),
        ],
    },
    "quiz-day-9": {
        "track": "day-9-home", "title": "Day 9 Quiz — Home & Household", "xpReward": 30,
        "questions": [
            ("Which is the correct polite instruction?", ["Please turn off the lights.", "Please light off turn.", "Please off turn lights.", "Turn please off lights."], 0,
             "'turn off' stays together as a phrasal verb."),
            ("\"The kitchen is ___ the hall.\"", ["next to", "next at", "near at", "close from"], 0,
             "'next to' is the correct preposition phrase for 'beside'."),
            ("Which sentence is correct?", ["I need to clean the house today.", "I need clean house today.", "I needing to clean house.", "I need cleaning the house."], 0,
             "'need to' + base verb — don't drop 'to'."),
            ("\"The water is not ___.\"", ["working", "work", "works", "worked"], 0,
             "'not working' describes something broken — present continuous form."),
            ("Which politely asks for help?", ["Can you help me fix this?", "You fix this help me.", "Help fix this me.", "Fix this can you help?"], 0,
             "'Can you help me ___?' + base verb is the standard polite request."),
        ],
    },
    "quiz-day-10": {
        "track": "day-10-phone", "title": "Day 10 Quiz — Phone Calls & Messages", "xpReward": 30,
        "questions": [
            ("\"___ I speak to Ravi?\"", ["May", "Do", "Am", "Will"], 0,
             "'May I ___?' politely asks permission."),
            ("Correct response to a misdialed call:", ["Sorry, wrong number.", "Sorry, number wrong.", "Number is not correct sorry.", "Wrong you called."], 0,
             "The fixed, standard phrase for a misdialed call."),
            ("\"Please call me ___ later.\"", ["back", "backing", "backs", "backed"], 0,
             "'call back' — a phrasal verb, stays as 'back' regardless of tense elsewhere in the sentence."),
            ("Which shows a spontaneous decision made right now?", ["I will send you a message.", "I am going to send you a message.", "I sending you a message.", "I sent you message will."], 0,
             "'will' is for decisions made at the moment of speaking, unlike pre-planned 'going to'."),
            ("\"My phone battery is ___.\"", ["low", "less", "little", "few"], 0,
             "'low' is the correct adjective for battery level."),
        ],
    },
    "quiz-day-11": {
        "track": "day-11-work", "title": "Day 11 Quiz — Work & Occupations", "xpReward": 30,
        "questions": [
            ("\"What do you ___ for work?\"", ["do", "does", "doing", "did"], 0,
             "'What do you do?' asks about someone's job — base verb after 'do you'."),
            ("Which sentence is correct?", ["I work in a bank.", "I work at in bank.", "I working bank.", "I am work in a bank."], 0,
             "'work in a ___' — simple present tense, no extra words needed."),
            ("\"I ___ work at nine every day.\"", ["start", "starting", "starts", "started"], 0,
             "Base verb form with 'I' in simple present tense."),
            ("\"My colleague is very ___.\"", ["helpful", "help", "helping", "helps"], 0,
             "'helpful' is the adjective form needed after 'is very'."),
            ("Which shows an ongoing search for a job?", ["I am looking for a new job.", "I look for new job.", "I looked for new job now.", "I am look for a new job."], 0,
             "Present continuous 'am looking for' shows an action happening now."),
        ],
    },
    "quiz-day-12": {
        "track": "day-12-money", "title": "Day 12 Quiz — Money & Banking", "xpReward": 30,
        "questions": [
            ("\"I would like to ___ a bank account.\"", ["open", "opening", "opened", "opens"], 0,
             "'would like to' + base verb."),
            ("\"Where is the nearest ___?\"", ["ATM", "a ATM", "the ATMs", "ATMs a"], 0,
             "No extra article needed before a specific single place name like 'ATM' in this question form."),
            ("Which sentence is correct?", ["I need to withdraw some money.", "I need withdraw some money.", "I needing withdraw money.", "I need to withdrawing money."], 0,
             "'need to' + base verb, same pattern as Day 9."),
            ("Which politely asks about payment method?", ["Can I pay by card?", "I pay by card can?", "By card I pay can?", "Card pay I can?"], 0,
             "Standard question word order: 'Can I ___?'"),
            ("\"Please keep the ___.\"", ["change", "changing", "changed", "changes"], 0,
             "'change' (noun) here means the extra money returned."),
        ],
    },
    "quiz-day-13": {
        "track": "day-13-hobbies", "title": "Day 13 Quiz — Hobbies & Free Time", "xpReward": 30,
        "questions": [
            ("Which sentence is correct?", ["What do you like to do in your free time?", "What you like to do free time?", "What do you liking to do?", "What like you to do?"], 0,
             "Standard question form: 'What do you like to ___?'"),
            ("\"I enjoy ___ on weekends.\" (garden)", ["gardening", "to garden", "garden", "gardened"], 0,
             "'enjoy' is followed by '-ing', not 'to' — 'enjoy gardening', not 'enjoy to garden'."),
            ("Which sentence is correct?", ["I like listening to music.", "I like listen music.", "I like to listening music.", "I liking listen to music."], 0,
             "'listen to ___' needs 'to' after 'listen', and 'like listening' uses '-ing' after 'like'."),
            ("\"Do you play any ___?\"", ["sports", "sport's", "sporting", "a sports"], 0,
             "'sports' — plural noun, no article needed."),
            ("Which shows an action that started in the past and is still continuing?", ["I have been learning English for two months.", "I learned English two months.", "I am learn English two months.", "I learning English since two months ago now."], 0,
             "'have been ___ing' shows a continuing action started in the past."),
        ],
    },
    "quiz-day-14": {
        "track": "day-14-plans", "title": "Day 14 Quiz — Making Plans (Week 2 Review)", "xpReward": 30,
        "questions": [
            ("\"Are you ___ this weekend?\"", ["free", "freely", "freedom", "freeing"], 0,
             "'free' (adjective) means 'available'."),
            ("Which sentence is correct?", ["Let's meet at the park at five.", "Let's meeting at park five.", "Let we meet park at five.", "Let's meet the park at five."], 0,
             "'Let's meet at ___' — needs 'at' before both the place and the time."),
            ("Which shows a plan already decided?", ["I am going to visit my parents next week.", "I will visit my parents next week decided already.", "I visiting my parents next week.", "I visit my parents will next week."], 0,
             "'going to' expresses a pre-decided plan, unlike spontaneous 'will'."),
            ("\"Can we ___ to another day?\"", ["reschedule", "reschedules", "rescheduling", "rescheduled"], 0,
             "Base verb form after 'we' in a question."),
            ("Correct casual closing once plans are set:", ["See you then!", "See then you!", "You see then!", "Then see you will!"], 0,
             "A simple, standard casual goodbye once plans are confirmed."),
        ],
    },
    "quiz-day-15": {
        "track": "day-15-describing", "title": "Day 15 Quiz — Describing People & Things", "xpReward": 30,
        "questions": [
            ("Which sentence is correct?", ["She is tall and friendly.", "She tall and friendly is.", "She is tall friendly.", "She is tall, and, friendly."], 0,
             "Two adjectives joined naturally with 'and'."),
            ("\"This bag is bigger ___ that one.\"", ["than", "that", "then", "from"], 0,
             "'bigger than' — comparative + 'than', not 'then' (a common spelling confusion)."),
            ("\"He has short black ___.\"", ["hair", "hairs", "haired", "hairy"], 0,
             "'hair' is uncountable in this everyday sense — no plural 's'."),
            ("Which sentence is correct?", ["This is a very useful tool.", "This is a tool very useful.", "This is very a useful tool.", "This a very useful tool is."], 0,
             "'very' comes directly before the adjective it intensifies."),
            ("\"She ___ happy today.\"", ["looks", "looking", "look", "looked"], 0,
             "'looks + adjective' — present tense, third person singular."),
        ],
    },
    "quiz-day-16": {
        "track": "day-16-past", "title": "Day 16 Quiz — Past Events", "xpReward": 30,
        "questions": [
            ("Correct past tense of 'go':", ["I went to the market yesterday.", "I goed to the market yesterday.", "I go to the market yesterday.", "I have go to the market yesterday."], 0,
             "'went' is the irregular past tense of 'go' — not 'goed'."),
            ("Correct past-tense question form:", ["Did you sleep well last night?", "Did you slept well last night?", "You did sleep well last night?", "Did you sleeping well last night?"], 0,
             "'Did you ___?' uses the BASE verb form, not the past form — 'Did you slept?' is a common mistake."),
            ("Correct negative past tense:", ["I did not finish my work yesterday.", "I did not finished my work yesterday.", "I not did finish my work.", "I did finish not my work."], 0,
             "'did not' + base verb — 'did not finish', not 'did not finished'."),
            ("\"We had a great time at the ___.\"", ["wedding", "wed", "wedded", "weds"], 0,
             "'wedding' is the noun for a marriage ceremony."),
            ("\"I ___ very busy last week.\"", ["was", "am", "is", "were"], 0,
             "'was' is the correct past tense of 'am' with the subject 'I'."),
        ],
    },
    "quiz-day-17": {
        "track": "day-17-future", "title": "Day 17 Quiz — Future Plans", "xpReward": 30,
        "questions": [
            ("Which shows a spontaneous decision?", ["I will call you tomorrow.", "I am calling you tomorrow decided now.", "I call you will tomorrow.", "I going to call you tomorrow."], 0,
             "'will' is for decisions made right at the moment of speaking."),
            ("Which shows a plan already made?", ["We are going to travel next month.", "We travel next month will.", "We will travelling next month.", "We going travel next month."], 0,
             "'going to' — for plans already decided."),
            ("\"I ___ to finish this by Friday.\"", ["hope", "hoping", "hopes", "hoped"], 0,
             "Base verb form after 'I' in simple present tense."),
            ("Correct use of present tense for a fixed schedule:", ["The train leaves at 6 PM.", "The train will leaving at 6 PM.", "The train is leave at 6 PM.", "The train leaved at 6 PM."], 0,
             "Present tense ('leaves') is standard for timetables, even about the future."),
            ("\"I am ___ everything will go well.\"", ["sure", "surely", "assurance", "suring"], 0,
             "'sure' is the adjective form used after 'am'."),
        ],
    },
    "quiz-day-18": {
        "track": "day-18-opinions", "title": "Day 18 Quiz — Giving Opinions", "xpReward": 30,
        "questions": [
            ("Which sentence is correct?", ["I think this is a good idea.", "I am thinking this good idea.", "I think this good idea is.", "This is I think a good idea."], 0,
             "'I think ___' is the standard way to introduce an opinion."),
            ("Correct way to agree:", ["I agree with you.", "I agree you.", "I am agree with you.", "I agree to you."], 0,
             "'agree with ___' — no 'am' needed, and the preposition is 'with', not 'to'."),
            ("Gentle way to express doubt:", ["I am not sure about that.", "I don't know nothing about that.", "I know not about that.", "Not sure I about that."], 0,
             "A polite hedge, avoiding a double negative like 'don't know nothing'."),
            ("\"In my ___, it is better to wait.\"", ["opinion", "opinions", "opinionated", "opining"], 0,
             "'In my opinion, ___' — singular noun form."),
            ("Polite disagreement pattern:", ["That's a fair point, but I see it differently.", "You are wrong.", "That is not correct at all.", "No, that's wrong opinion."], 0,
             "Acknowledge the other person's point first, then share your own view."),
        ],
    },
    "quiz-day-19": {
        "track": "day-19-doctor", "title": "Day 19 Quiz — At the Doctor & Pharmacy", "xpReward": 30,
        "questions": [
            ("\"I have a fever ___ yesterday.\"", ["since", "from", "for", "at"], 0,
             "'since' + a starting point in time shows something continuing from then until now."),
            ("Which sentence is correct?", ["Do I need a prescription for this?", "I need do a prescription?", "Do I a prescription need?", "Need I a prescription do?"], 0,
             "Standard yes/no question word order: 'Do I need ___?'"),
            ("\"How many times a day should I ___ this?\"", ["take", "taking", "takes", "took"], 0,
             "Base verb form after 'should I'."),
            ("Which sentence is correct?", ["I am allergic to this medicine.", "I am allergic from this medicine.", "I am allergic with this medicine.", "I allergic this medicine."], 0,
             "'allergic to ___' — always 'to', not 'from' or 'with'."),
            ("\"Please take rest and drink plenty of ___.\"", ["water", "waters", "watering", "watered"], 0,
             "'water' is uncountable — no plural form here."),
        ],
    },
    "quiz-day-20": {
        "track": "day-20-festivals", "title": "Day 20 Quiz — Festivals & Celebrations", "xpReward": 30,
        "questions": [
            ("Which sentence is correct?", ["We celebrate Sankranti with our family.", "We celebrate with Sankranti our family.", "We celebrating Sankranti family.", "Sankranti we celebrate family with."], 0,
             "'celebrate ___ with ___' — festival first, then who you share it with."),
            ("Correct festive greeting pattern:", ["Happy Ugadi!", "Ugadi Happy!", "Very Happy of Ugadi!", "Happy for Ugadi!"], 0,
             "'Happy ___!' is the standard English festival greeting."),
            ("\"The whole street is ___ with lights.\"", ["decorated", "decorate", "decorating", "decoration"], 0,
             "Passive voice: 'is decorated with ___'."),
            ("\"We usually visit the ___ during festivals.\"", ["temple", "temples", "templed", "temple's"], 0,
             "Singular 'temple' fits this general statement."),
            ("Which sentence is correct?", ["Thank you for inviting us to the celebration.", "Thank you to invite us to the celebration.", "Thank you for invite us.", "Thank you invited us."], 0,
             "'Thank you for ___ing' — gerund after 'for', not 'to invite'."),
        ],
    },
    "quiz-day-21": {
        "track": "day-21-neighbors", "title": "Day 21 Quiz — Neighbors & Community (Week 3 Review)", "xpReward": 30,
        "questions": [
            ("Which sentence is correct?", ["My neighbor is very friendly and helpful.", "My neighbor very friendly and helpful is.", "My neighbor is friendly very and helpful.", "Friendly and helpful my neighbor is very."], 0,
             "Review: two adjectives joined with 'and', same pattern as Day 15."),
            ("\"We ___ turns cleaning the street.\"", ["take", "taking", "took", "takes"], 0,
             "'take turns ___ing' — base verb form with 'we'."),
            ("Which sentence correctly uses past tense?", ["There was a small function in our community hall.", "There is a small function was in our hall.", "There were a small function.", "A small function there was."], 0,
             "Review: 'was' for a singular past event, same as Day 16."),
            ("Idiom meaning 'watch over':", ["keep an eye on", "keep an ear on", "keep a hand on", "keep a foot on"], 0,
             "'keep an eye on' is the correct idiom for watching over something."),
            ("Which sentence is correct?", ["We look out for each other in this neighborhood.", "We look out each other for.", "We looking out for each other.", "Each other we look out for."], 0,
             "'look out for each other' — a fixed idiomatic phrase."),
        ],
    },
    "quiz-day-22": {
        "track": "day-22-help", "title": "Day 22 Quiz — Asking for Help & Instructions", "xpReward": 30,
        "questions": [
            ("Most polite help request:", ["Could you please help me carry this?", "Help me carry this you could?", "You help carry this please could?", "Carry this help me could you please?"], 0,
             "'Could you please ___?' is a very polite request form."),
            ("Correct sequencing of instructions:", ["First, switch on the machine, then press this button.", "Switch first on machine, press then button.", "First switch machine on, this button then press.", "Press this button, first switch on the machine."], 0,
             "'First..., then...' clearly sequences steps in order."),
            ("Which sentence is correct?", ["I don't know how to use this app.", "I don't know how use this app.", "I not know how to use this app.", "I don't knowing how to use this app."], 0,
             "'know how to ___' needs 'to' before the base verb."),
            ("Which sentence is correct?", ["Can you show me how to do this?", "Can you show me how do this?", "Can you show how to do me this?", "Show can you me how to do this?"], 0,
             "'show me how to ___' needs 'to' before the base verb."),
            ("Correct closing thanks:", ["Thanks a lot, that was really helpful.", "Thanks a lot, that helpful was really.", "That was helpful thanks a lot really.", "Really helpful that was, thanks lot a."], 0,
             "A natural, warm closing phrase."),
        ],
    },
    "quiz-day-23": {
        "track": "day-23-comparing", "title": "Day 23 Quiz — Comparing Things", "xpReward": 30,
        "questions": [
            ("Correct comparative:", ["This phone is cheaper than that one.", "This phone is more cheap than that one.", "This phone is cheaper that one.", "This phone cheaper than that one is."], 0,
             "Short adjectives add '-er' + 'than' for comparisons."),
            ("Correct superlative:", ["This is the best restaurant in town.", "This is the bestest restaurant in town.", "This is best restaurant in town.", "This is the more best restaurant in town."], 0,
             "'the best' is the correct superlative form — no 'the' dropped, no double superlative."),
            ("Correct long-adjective comparative:", ["My new job is more interesting than my old one.", "My new job is interestinger than my old one.", "My new job is more interesting that my old one.", "My new job interesting more than old one."], 0,
             "Longer adjectives use 'more ___ than', not '-er'."),
            ("Correct equal comparison:", ["This one is as good as that one.", "This one is good as that one.", "This one is as good than that one.", "This one as good as that is."], 0,
             "'as ___ as' — the full pattern, not dropping the first 'as'."),
            ("Correct comparative question:", ["Which one is faster, the bus or the train?", "Which faster one is, bus or train?", "Faster which one is, the bus the train?", "Which one faster is, the bus or the train?"], 0,
             "Standard word order: 'Which one is ___, X or Y?'"),
        ],
    },
    "quiz-day-24": {
        "track": "day-24-emotions", "title": "Day 24 Quiz — Emotions & Comfort", "xpReward": 30,
        "questions": [
            ("Which sentence is correct?", ["I am a little nervous about the interview.", "I am little nervous the interview.", "I a little am nervous about interview.", "Nervous a little I am about the interview."], 0,
             "'a little' softens the adjective 'nervous', placed before it."),
            ("Correct comfort phrase:", ["Don't be afraid, I am here with you.", "Don't afraid be, I here with you am.", "Not be afraid, I am here you with.", "Be not afraid, here I am with you."], 0,
             "'Don't be ___' is the standard negative imperative for comfort."),
            ("Correct encouraging phrase:", ["It's okay to make mistakes while learning.", "It's okay make mistakes while learning.", "Its okay to mistakes make while learning.", "It okay's to make mistakes learning while."], 0,
             "'It's okay to ___' + base verb."),
            ("Which sentence is correct?", ["I feel much better now, thank you.", "I feel more better now, thank you.", "I feeling much better now.", "Much better I feel now, thank you."], 0,
             "'much better' — don't add 'more' before an already-comparative word."),
            ("Correct encouragement:", ["Take a deep breath, you are doing great.", "Take deep a breath, doing great you are.", "Take a breath deep, you great doing are.", "A deep breath take, great you are doing."], 0,
             "Standard word order for this encouraging phrase."),
        ],
    },
    "quiz-day-25": {
        "track": "day-25-technology", "title": "Day 25 Quiz — Technology & Everyday Devices", "xpReward": 30,
        "questions": [
            ("Which sentence is correct?", ["My laptop is not turning on.", "My laptop not turning on is.", "My laptop is not turn on.", "Not my laptop is turning on."], 0,
             "'is not turning on' — present continuous negative."),
            ("Which sentence is correct?", ["Can you connect to the WiFi?", "Can you connect the WiFi to?", "Can connect you to the WiFi?", "You can connect to WiFi?"], 0,
             "'connect to ___' names what you're joining."),
            ("Which sentence is correct?", ["Please charge your phone before we leave.", "Please charge your phone we leave before.", "Please your phone charge before we leave.", "Before we leave please charge phone your."], 0,
             "'before we leave' comes after the main instruction here, both orders work but this is the natural default."),
            ("\"I ___ my password again.\"", ["forgot", "forgetted", "forget", "forgetting"], 0,
             "'forgot' is the irregular past tense of 'forget'."),
            ("Which sentence is correct?", ["This app is very easy to use.", "This app is very easy for use.", "This app is very easy using.", "This app very easy is to use."], 0,
             "'easy to ___' + base verb — not 'easy for use'."),
        ],
    },
    "quiz-day-26": {
        "track": "day-26-travel", "title": "Day 26 Quiz — Travel & Booking Tickets", "xpReward": 30,
        "questions": [
            ("Which sentence is correct?", ["I would like to book two tickets to Hyderabad.", "I would to like book two tickets.", "I like would to book two tickets.", "Book I would like two tickets."], 0,
             "'would like to' + base verb — the standard polite request pattern."),
            ("Which sentence is correct?", ["What time does the bus depart?", "What time do the bus depart?", "What time the bus departs?", "Bus depart what time does?"], 0,
             "'does' is used with singular subjects like 'the bus' in questions."),
            ("Which sentence is correct?", ["Is there a direct train to Vijayawada?", "Is there direct a train to Vijayawada?", "There is a direct train to Vijayawada is?", "Direct is there a train to Vijayawada?"], 0,
             "'Is there a ___?' checks if something exists/is available."),
            ("Which sentence is correct?", ["How long does the journey take?", "How long the journey does take?", "How long take does the journey?", "Journey how long does take?"], 0,
             "'How long does ___ take?' asks about duration."),
            ("Which sentence is correct?", ["Please confirm my seat number.", "Please my seat number confirm.", "Confirm please my seat number.", "My seat number please confirm."], 0,
             "Standard imperative word order: verb, then object."),
        ],
    },
    "quiz-day-27": {
        "track": "day-27-strangers", "title": "Day 27 Quiz — Small Talk With Strangers", "xpReward": 30,
        "questions": [
            ("Polite way to ask about an empty seat:", ["Excuse me, is this seat taken?", "Excuse me, this seat is taken?", "This seat taken is, excuse me?", "Is taken this seat, excuse me?"], 0,
             "'Excuse me, is this seat taken?' is the natural, polite phrasing."),
            ("Correct tag question:", ["Lovely weather today, isn't it?", "Lovely weather today, is it not?", "Lovely weather today, isn't?", "Lovely weather today, not it is?"], 0,
             "Review: tag questions from Day 7 — 'isn't it?' is the standard short form."),
            ("Which sentence is correct?", ["Do you come here often?", "You do come here often?", "Do you come often here?", "You come here often do?"], 0,
             "'Do you ___?' is the standard yes/no question form — the auxiliary 'do' comes first, before the subject."),
            ("Correct closing phrase:", ["It was nice chatting with you.", "It was nice chat with you.", "It nice was chatting with you.", "Chatting with you was it nice."], 0,
             "Review: past tense closing, echoing Day 1's 'It was nice talking to you.'"),
            ("Warm phrase for someone about to travel:", ["Have a safe journey!", "Have safe a journey!", "A safe journey have!", "Journey safe have a!"], 0,
             "Standard word order for this parting phrase."),
        ],
    },
    "quiz-day-28": {
        "track": "day-28-story", "title": "Day 28 Quiz — Telling a Short Story", "xpReward": 30,
        "questions": [
            ("Classic story opener:", ["Once, I got lost in a new city.", "I once got in a new city lost.", "Lost once I got in a new city.", "In a new city, once lost I got."], 0,
             "'Once, ___' is a natural way to begin a short personal story."),
            ("Correct past continuous, for scene-setting:", ["It was raining heavily that day.", "It rained heavily was that day.", "It is raining heavily that day.", "It raining was heavily that day."], 0,
             "'was raining' — past continuous, sets the scene of an in-progress action."),
            ("Which sentence is correct?", ["Suddenly, someone offered to help me.", "Suddenly someone offering help me.", "Someone suddenly offered help to me me.", "Suddenly, someone offered helping me."], 0,
             "'offered to ___' + base verb."),
            ("\"In the ___, everything turned out fine.\"", ["end", "ending", "ended", "ends"], 0,
             "'In the end, ___' — fixed phrase introducing a conclusion."),
            ("Which sentence is correct?", ["That experience taught me to stay calm.", "That experience teached me to stay calm.", "That experience taught me stay calm.", "Taught me that experience to stay calm."], 0,
             "'taught' is the irregular past tense of 'teach' — and 'taught me to ___' needs 'to'."),
        ],
    },
    "quiz-day-29": {
        "track": "day-29-clarify", "title": "Day 29 Quiz — Handling Misunderstandings", "xpReward": 30,
        "questions": [
            ("Polite clarification request:", ["Sorry, could you repeat that, please?", "Sorry, you could repeat that please?", "Repeat that please, sorry could you?", "Could repeat you that, sorry please?"], 0,
             "'could you ___, please?' is the standard polite request form."),
            ("Which sentence is correct?", ["I didn't quite catch that.", "I not quite catch that.", "I didn't quite caught that.", "Quite I didn't catch that."], 0,
             "'didn't' + base verb ('catch'), not the past form."),
            ("Which sentence is correct?", ["Could you speak a little slower, please?", "Could you speak little a slower please?", "Could you a little speak slower please?", "Speak could you a little slower please?"], 0,
             "'a little slower' modifies 'speak' — standard word order."),
            ("Which sentence is correct?", ["What I meant was this.", "What I mean was this.", "What did I meant was this.", "This was what I meant it."], 0,
             "'meant' is the past tense of 'mean', matching 'was' for consistency."),
            ("Graceful way to acknowledge confusion:", ["Sorry for the confusion, let me explain again.", "Sorry the confusion, explain me again let.", "For the confusion sorry, let explain me again.", "Let me again explain, sorry for confusion."], 0,
             "Natural word order: apologize first, then offer to fix it."),
        ],
    },
    "quiz-day-30": {
        "track": "day-30-final", "title": "Day 30 Quiz — Final Review", "xpReward": 30,
        "questions": [
            ("Which sentence correctly uses present perfect?", ["I have learned so much this month.", "I have learn so much this month.", "I has learned so much this month.", "I learned have so much this month."], 0,
             "'have learned' — present perfect, connects the past month to now."),
            ("Which sentence is correct?", ["I feel more confident speaking English now.", "I feel more confident to speak English now.", "I feeling more confident speaking English.", "More confident I feel speaking English now."], 0,
             "'confident speaking ___' — 'confident' followed directly by the '-ing' form here."),
            ("Well-known encouraging saying:", ["Practice makes a person perfect.", "Practice make a person perfect.", "Practicing makes person a perfect.", "Perfect makes a person practice."], 0,
             "A fixed, well-known saying — 'Practice makes...' is the correct subject-verb agreement."),
            ("Correct future habitual form:", ["I will keep practicing every day.", "I will keep practice every day.", "I keep will practicing every day.", "I will keeping practice every day."], 0,
             "'keep ___ing' expresses continuing an action."),
            ("Correct gerund-after-preposition form:", ["Thank you for helping me learn.", "Thank you to help me learn.", "Thank you for help me learn.", "Thank you helping for me learn."], 0,
             "'Thank you for ___ing' — gerund after 'for', a pattern reviewed all through this roadmap."),
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
