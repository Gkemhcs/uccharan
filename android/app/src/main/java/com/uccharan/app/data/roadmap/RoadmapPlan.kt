package com.uccharan.app.data.roadmap

/**
 * The 90-day structure described in CURRICULUM.md §8. This is navigational
 * shell, not content — it says "Day 4 is themed Numbers, Time & Shopping and
 * its lessons live under the `day-4-shopping` Firestore track"; the actual
 * sentences/quiz questions live in Firestore, same as any other lesson
 * content, so they can be updated without an app release.
 *
 * The program is a deliberately BOUNDED, structured sequence, not an
 * indefinite drip: three 30-day Levels (see [ROADMAP_LEVELS]), each with a
 * defined CEFR target and a capstone day at its end (30/60/90). This
 * mirrors how real CEFR-aligned courses are structured — a defined
 * "Beginner course," then a separately-entered "Intermediate course" — not
 * an unbounded stream of content or an open-ended "explore on your own"
 * mode. "Practice with your Tutor" is likewise tied to the learner's
 * current day's content, not a free topic picker — see
 * `PracticeApi`/`practice_scenarios.py`.
 *
 * `track`/`quizId` stay nullable so a future day added to this list before
 * its content is seeded still shows as "coming soon" ([HomeViewModel])
 * rather than broken. All 90 days now have real, seeded content:
 *   - Days 1-7:   seed_week1_content.py         (Level 1, Week 1)
 *   - Days 8-30:  seed_weeks_2_to_5_content.py   (Level 1, Weeks 2-5)
 *   - Days 31-60: seed_days_31_to_60_content.py  (Level 2)
 *   - Days 61-90: seed_days_61_to_90_content.py  (Level 3)
 *
 * `practiceScenario` is a concrete, real-world situation for that day's
 * "Practice with your Tutor" session (e.g. Day 6 → asking a stranger for
 * directions; Day 43 → haggling with an auto-rickshaw driver over a fare) —
 * richer and more immersive than just handing the bare theme text to the
 * tutor persona prompt. Left null on days that are more grammar-abstract
 * than situational (e.g. capstones, hypotheticals); those fall back to the
 * theme text, unchanged from before. See also `PracticeTabScreen`'s curated
 * situations list and custom-topic field, which this complements, not replaces.
 */
data class RoadmapDay(
    val day: Int,
    val theme: String,
    val track: String?,
    val quizId: String?,
    val practiceScenario: String? = null,
)

val ROADMAP_DAYS: List<RoadmapDay> = listOf(
    // ---- Level 1: Foundations (Days 1-30) ----
    // Week 1
    RoadmapDay(1, "Greetings & Introductions", "foundations", "quiz-day-1", practiceScenario = "You've just met the learner for the first time at a social gathering — introduce yourself and get to know them."),
    RoadmapDay(2, "Family & People", "day-2-family", "quiz-day-2", practiceScenario = "You are a curious new neighbor asking the learner about their family."),
    RoadmapDay(3, "Daily Routine", "day-3-routine", "quiz-day-3", practiceScenario = "You are a friend asking the learner to describe what a normal day looks like for them."),
    RoadmapDay(4, "Numbers, Time & Shopping", "day-4-shopping", "quiz-day-4", practiceScenario = "You are a shopkeeper helping the learner buy groceries — agree on quantities and prices."),
    RoadmapDay(5, "Food & Ordering", "day-5-food", "quiz-day-5", practiceScenario = "You are a waiter taking the learner's order at a small restaurant."),
    RoadmapDay(6, "Directions & Travel", "day-6-directions", "quiz-day-6", practiceScenario = "You are a stranger on the street the learner has stopped to ask for directions to the railway station."),
    RoadmapDay(7, "Health & Small Talk (Week 1 review)", "day-7-health", "quiz-day-7", practiceScenario = "You are a friend checking in on how the learner is feeling, with some light small talk."),

    // Week 2
    RoadmapDay(8, "Weather & Feelings", "day-8-weather", "quiz-day-8", practiceScenario = "You are a friend chatting casually about today's weather and how it's affecting your mood."),
    RoadmapDay(9, "Home & Household", "day-9-home", "quiz-day-9", practiceScenario = "You are a neighbor visiting the learner's home for the first time, asking about it."),
    RoadmapDay(10, "Phone Calls & Messages", "day-10-phone", "quiz-day-10", practiceScenario = "You've answered a phone call from the learner, who needs to leave a message for someone who's out."),
    RoadmapDay(11, "Work & Occupations", "day-11-work", "quiz-day-11", practiceScenario = "You are a new acquaintance asking the learner about their job."),
    RoadmapDay(12, "Money & Banking", "day-12-money", "quiz-day-12", practiceScenario = "You are a bank teller helping the learner with a simple banking task."),
    RoadmapDay(13, "Hobbies & Free Time", "day-13-hobbies", "quiz-day-13", practiceScenario = "You are a friend asking what the learner likes to do in their free time."),
    RoadmapDay(14, "Making Plans (Week 2 review)", "day-14-plans", "quiz-day-14", practiceScenario = "You are a friend trying to make weekend plans together with the learner."),

    // Week 3
    RoadmapDay(15, "Describing People & Things", "day-15-describing", "quiz-day-15", practiceScenario = "You are a friend asking the learner to describe someone or something they saw recently."),
    RoadmapDay(16, "Past Events — Talking About Yesterday", "day-16-past", "quiz-day-16", practiceScenario = "You are a friend asking the learner what they did yesterday."),
    RoadmapDay(17, "Future Plans — Talking About Tomorrow", "day-17-future", "quiz-day-17", practiceScenario = "You are a friend asking about the learner's plans for tomorrow."),
    RoadmapDay(18, "Giving Opinions & Agreeing/Disagreeing Politely", "day-18-opinions", "quiz-day-18", practiceScenario = "You are a friend discussing an everyday topic and politely disagreeing with the learner at one point."),
    RoadmapDay(19, "At the Doctor & Pharmacy", "day-19-doctor", "quiz-day-19", practiceScenario = "You are a doctor asking the learner about their symptoms."),
    RoadmapDay(20, "Festivals & Celebrations", "day-20-festivals", "quiz-day-20", practiceScenario = "You are a friend asking the learner how they celebrate festivals with their family."),
    RoadmapDay(21, "Neighbors & Community (Week 3 review)", "day-21-neighbors", "quiz-day-21", practiceScenario = "You are a neighbor asking the learner for a small favor."),

    // Week 4
    RoadmapDay(22, "Asking for Help & Giving Instructions", "day-22-help", "quiz-day-22", practiceScenario = "The learner has asked you for help — give them simple, clear instructions."),
    RoadmapDay(23, "Comparing Things (bigger, cheaper, better)", "day-23-comparing", "quiz-day-23", practiceScenario = "You are a shopkeeper helping the learner compare two products before they decide what to buy."),
    RoadmapDay(24, "Emotions & Comfort — Talking About Feelings", "day-24-emotions", "quiz-day-24", practiceScenario = "You are a caring friend comforting the learner after they've had a bad day."),
    RoadmapDay(25, "Technology & Everyday Devices", "day-25-technology", "quiz-day-25", practiceScenario = "You are a friend helping the learner troubleshoot a problem with their phone."),
    RoadmapDay(26, "Travel & Booking Tickets", "day-26-travel", "quiz-day-26", practiceScenario = "You are a ticket counter clerk helping the learner book a bus or train ticket."),
    RoadmapDay(27, "Small Talk With Strangers", "day-27-strangers", "quiz-day-27", practiceScenario = "You are a stranger sitting next to the learner, making light small talk while waiting."),
    RoadmapDay(28, "Telling a Short Story", "day-28-story", "quiz-day-28", practiceScenario = "You are a friend who has just asked the learner to tell you about something interesting that happened to them."),

    // Week 5 (partial)
    RoadmapDay(29, "Handling Misunderstandings ('Could you repeat that?')", "day-29-clarify", "quiz-day-29", practiceScenario = "You are a friend who just said something the learner didn't quite catch — help them ask you to repeat or clarify it."),
    RoadmapDay(30, "Putting It All Together — Confident Conversations (Level 1 Capstone)", "day-30-final", "quiz-day-30"),

    // ---- Level 2: Consolidation (Days 31-60) ----
    // Week 6
    RoadmapDay(31, "Talking About Habits & Routines", "day-31-habits", "quiz-day-31", practiceScenario = "You are a friend asking about habits the learner used to have and has since changed."),
    RoadmapDay(32, "Describing Your Neighborhood", "day-32-neighborhood", "quiz-day-32", practiceScenario = "You are a visitor asking the learner to describe their neighborhood."),
    RoadmapDay(33, "Making Complaints Politely", "day-33-complaints", "quiz-day-33", practiceScenario = "You are a shopkeeper or waiter the learner needs to politely complain to about something wrong with their order."),
    RoadmapDay(34, "Giving Advice & Suggestions", "day-34-advice", "quiz-day-34", practiceScenario = "You are a friend asking the learner for advice about a small problem you're having."),
    RoadmapDay(35, "Health & Wellbeing Habits", "day-35-wellbeing", "quiz-day-35", practiceScenario = "You are a friend comparing healthy habits with the learner."),
    RoadmapDay(36, "Talking About Your Job & Experience", "day-36-jobinterview", "quiz-day-36", practiceScenario = "You are an interviewer asking the learner about their work experience."),
    RoadmapDay(37, "Talking About Your Week (Week 6 review)", "day-37-recap", "quiz-day-37", practiceScenario = "You are a friend catching up, asking the learner how their week went."),

    // Week 7
    RoadmapDay(38, "Likes, Dislikes & Preferences", "day-38-preferences", "quiz-day-38", practiceScenario = "You are a friend asking the learner about their likes and dislikes."),
    RoadmapDay(39, "Talking About the Past in Detail", "day-39-pastdetail", "quiz-day-39", practiceScenario = "You are a friend asking the learner to walk you through their morning, step by step."),
    RoadmapDay(40, "Making & Responding to Invitations", "day-40-invitations", "quiz-day-40", practiceScenario = "You are a friend inviting the learner to an event and responding to whatever they say."),
    RoadmapDay(41, "Explaining How to Do Something", "day-41-process", "quiz-day-41", practiceScenario = "You are a friend asking the learner to explain how to make or do something they know well."),
    RoadmapDay(42, "Phone Calls — Leaving a Message", "day-42-phonecalls", "quiz-day-42", practiceScenario = "You've called and the person the learner wants isn't available — take a message from the learner."),
    RoadmapDay(43, "Bargaining & Talking About Prices", "day-43-bargaining", "quiz-day-43", practiceScenario = "You are an auto-rickshaw driver — the learner is negotiating the fare for a ride with you."),
    RoadmapDay(44, "Planning a Weekend Trip (Week 7 review)", "day-44-weekend", "quiz-day-44", practiceScenario = "You are a friend planning a weekend trip together with the learner."),

    // Week 8
    RoadmapDay(45, "Hopes, Wishes & Plans", "day-45-hopes", "quiz-day-45", practiceScenario = "You are a friend asking about the learner's hopes for the future."),
    RoadmapDay(46, "Rules & Obligations", "day-46-obligations", "quiz-day-46", practiceScenario = "You are a security guard or official explaining the rules of a place to the learner."),
    RoadmapDay(47, "Explaining Reasons — Cause & Effect", "day-47-causeeffect", "quiz-day-47", practiceScenario = "You are a friend asking the learner to explain why something happened."),
    RoadmapDay(48, "Handling Disagreements Respectfully", "day-48-disagree", "quiz-day-48", practiceScenario = "You are a friend who disagrees with the learner about something small — work it out respectfully."),
    RoadmapDay(49, "Technology & the Internet", "day-49-technology", "quiz-day-49", practiceScenario = "You are a friend comparing how you both use your phones and the internet day to day."),
    RoadmapDay(50, "Public Transport & Travel Logistics", "day-50-transport", "quiz-day-50", practiceScenario = "You are a fellow passenger or bus conductor discussing a delay with the learner."),
    RoadmapDay(51, "Everyday Problems & Solutions (Week 8 review)", "day-51-problems", "quiz-day-51", practiceScenario = "You are a friend helping the learner think through an everyday problem."),

    // Week 9
    RoadmapDay(52, "Describing Feelings in Detail", "day-52-feelingsdetail", "quiz-day-52", practiceScenario = "You are a close friend the learner is opening up to about how they're feeling."),
    RoadmapDay(53, "Talking About Achievements", "day-53-experience", "quiz-day-53", practiceScenario = "You are a friend catching up and asking about the learner's recent achievements."),
    RoadmapDay(54, "Giving Detailed Directions", "day-54-directionsdetail", "quiz-day-54", practiceScenario = "You are a local giving the learner detailed directions to a specific place."),
    RoadmapDay(55, "Handling Emergencies", "day-55-emergencies", "quiz-day-55", practiceScenario = "You are responding to the learner, who has just called you for urgent help."),
    RoadmapDay(56, "Weather & Seasons in Depth", "day-56-weatherdetail", "quiz-day-56", practiceScenario = "You are a friend comparing the weather across different seasons with the learner."),
    RoadmapDay(57, "Social Etiquette & Manners", "day-57-etiquette", "quiz-day-57", practiceScenario = "You are an elder or host the learner needs to speak with politely and formally."),
    RoadmapDay(58, "A Family Gathering (Week 9 review)", "day-58-gathering", "quiz-day-58", practiceScenario = "You are a family member at a gathering, chatting with the learner."),

    // Week 10 (partial)
    RoadmapDay(59, "Future Goals & Ambitions", "day-59-goals", "quiz-day-59", practiceScenario = "You are a friend asking about the learner's goals for the future."),
    RoadmapDay(60, "Level 2 Capstone — Confident Everyday Conversations", "day-60-capstone", "quiz-day-60"),

    // ---- Level 3: Real-World Fluency (Days 61-90) ----
    // Week 11
    RoadmapDay(61, "Expressing Opinions & Debating Respectfully", "day-61-debate", "quiz-day-61", practiceScenario = "You are a friend having a respectful debate with the learner about an everyday topic you disagree on."),
    RoadmapDay(62, "Negotiating Prices & Terms", "day-62-negotiate", "quiz-day-62", practiceScenario = "You are a shopkeeper or landlord negotiating a price or deal with the learner."),
    RoadmapDay(63, "Formal Job Interview Practice", "day-63-interview", "quiz-day-63", practiceScenario = "You are an interviewer conducting a formal job interview with the learner."),
    RoadmapDay(64, "Long-Term Plans & Life Goals", "day-64-lifegoals", "quiz-day-64", practiceScenario = "You are a friend discussing long-term life plans with the learner."),
    RoadmapDay(65, "Handling Difficult Service Situations", "day-65-service", "quiz-day-65", practiceScenario = "You are customer service staff the learner needs to escalate a complaint to."),
    RoadmapDay(66, "Talking About News & Current Events", "day-66-news", "quiz-day-66", practiceScenario = "You are a friend discussing a piece of recent news with the learner."),
    RoadmapDay(67, "Talking About a Decision You Made (Week 11 review)", "day-67-decision", "quiz-day-67", practiceScenario = "You are a friend the learner is explaining a recent decision to."),

    // Week 12
    RoadmapDay(68, "Telling a Longer Story", "day-68-narrative", "quiz-day-68", practiceScenario = "You are a friend who has asked the learner to tell a longer story about something that happened to them."),
    RoadmapDay(69, "Giving a Short Presentation", "day-69-presentation", "quiz-day-69", practiceScenario = "You are an audience member listening to the learner give a short presentation, and may ask a question."),
    RoadmapDay(70, "Talking About Hypotheticals", "day-70-hypothetical", "quiz-day-70"),
    RoadmapDay(71, "Formal Requests & Professional Language", "day-71-formal", "quiz-day-71", practiceScenario = "You are a colleague the learner needs to make a formal, polite request to."),
    RoadmapDay(72, "Explaining Symptoms to a Doctor in Detail", "day-72-medical", "quiz-day-72", practiceScenario = "You are a doctor asking the learner detailed questions about their symptoms."),
    RoadmapDay(73, "Clarifying Complex Ideas", "day-73-clarifydeep", "quiz-day-73", practiceScenario = "You are a friend who's confused by something the learner said — help them clarify it."),
    RoadmapDay(74, "Telling a Story With a Lesson (Week 12 review)", "day-74-lesson", "quiz-day-74", practiceScenario = "You are a friend the learner is telling a story with a lesson or moral to."),

    // Week 13
    RoadmapDay(75, "Talking About Culture & Traditions", "day-75-culture", "quiz-day-75", practiceScenario = "You are someone from a different place, curious about the learner's culture and traditions."),
    RoadmapDay(76, "Expressing Regret & Reflecting", "day-76-regret", "quiz-day-76", practiceScenario = "You are a close friend the learner is reflecting on a past regret with."),
    RoadmapDay(77, "Giving & Receiving Feedback", "day-77-feedback", "quiz-day-77", practiceScenario = "You are a colleague exchanging feedback on a piece of work with the learner."),
    RoadmapDay(78, "Advanced Small Talk", "day-78-smalltalk", "quiz-day-78", practiceScenario = "You are an acquaintance having natural small talk with the learner, moving smoothly between topics."),
    RoadmapDay(79, "Talking About Self-Improvement", "day-79-selfimprove", "quiz-day-79", practiceScenario = "You are a friend discussing self-improvement goals with the learner."),
    RoadmapDay(80, "Explaining a Problem & Proposing a Solution", "day-80-solution", "quiz-day-80", practiceScenario = "You are a colleague the learner is explaining a problem and a proposed solution to."),
    RoadmapDay(81, "Giving Someone Encouragement (Week 13 review)", "day-81-encouragement", "quiz-day-81", practiceScenario = "You are a friend the learner is encouraging after a setback."),

    // Week 14
    RoadmapDay(82, "Professional Phone & Video Call Etiquette", "day-82-videocalls", "quiz-day-82", practiceScenario = "You are a colleague on a video call with the learner, working out a scheduling change."),
    RoadmapDay(83, "Money & Financial Planning", "day-83-finance", "quiz-day-83", practiceScenario = "You are a friend or bank advisor discussing financial planning with the learner."),
    RoadmapDay(84, "Handling Unexpected Situations Calmly", "day-84-unexpected", "quiz-day-84", practiceScenario = "The learner needs to calmly explain an unexpected delay or mistake to you."),
    RoadmapDay(85, "Discussing Social Topics Respectfully", "day-85-socialtopics", "quiz-day-85", practiceScenario = "You are a friend discussing a social topic respectfully, with a somewhat different view from the learner's."),
    RoadmapDay(86, "Advanced Travel & Booking", "day-86-traveladvanced", "quiz-day-86", practiceScenario = "You are a travel agent helping the learner change or book a trip."),
    RoadmapDay(87, "Mentoring & Advising Someone", "day-87-mentor", "quiz-day-87", practiceScenario = "You are someone the learner is mentoring — you've come to them for advice."),
    RoadmapDay(88, "Helping a Friend Through a Situation (Week 14 review)", "day-88-friend", "quiz-day-88", practiceScenario = "You are a friend the learner is helping through a tough situation."),

    // Week 15 (partial)
    RoadmapDay(89, "Extended Real Conversation Practice", "day-89-conversation", "quiz-day-89", practiceScenario = "You are a close friend having an extended, natural conversation with the learner about whatever comes up."),
    RoadmapDay(90, "Level 3 Capstone — Confident, Independent English Speaker", "day-90-capstone", "quiz-day-90"),
)

/**
 * The program's three bounded stages. Each is exactly 30 days with its own
 * CEFR target and capstone day — a learner deliberately advances from one
 * to the next, the same way a real course catalog separates "Beginner" from
 * "Intermediate" rather than running one endless unit list.
 */
data class RoadmapLevel(val level: Int, val name: String, val cefrTarget: String, val days: List<RoadmapDay>)

val ROADMAP_LEVELS: List<RoadmapLevel> = listOf(
    RoadmapLevel(1, "Foundations", "A1 → B1", ROADMAP_DAYS.filter { it.day in 1..30 }),
    RoadmapLevel(2, "Consolidation", "B1", ROADMAP_DAYS.filter { it.day in 31..60 }),
    RoadmapLevel(3, "Real-World Fluency", "B1 → B2", ROADMAP_DAYS.filter { it.day in 61..90 }),
)

/** Week groupings for progress display (Profile screen). Week numbering restarts at 1 within each Level (e.g. Level 2's first week is "Week 1", not "Week 6") — Days 1-7 -> Level 1 Week 1, Days 31-37 -> Level 2 Week 1, etc. */
data class RoadmapWeek(val level: Int, val weekNumber: Int, val days: List<RoadmapDay>)

val ROADMAP_WEEKS: List<RoadmapWeek> = ROADMAP_LEVELS.flatMap { level ->
    level.days.chunked(7).mapIndexed { index, days -> RoadmapWeek(level.level, index + 1, days) }
}

fun roadmapDayForTrack(track: String): RoadmapDay? = ROADMAP_DAYS.firstOrNull { it.track == track }

/** The Level (1-indexed) that contains a given day number, e.g. day 45 -> Level 2. */
fun levelContaining(dayNumber: Int): RoadmapLevel? = ROADMAP_LEVELS.firstOrNull { level -> level.days.any { it.day == dayNumber } }

/** The week (within its Level) that contains a given day number, e.g. day 45 -> Level 2, Week 3. */
fun weekContaining(dayNumber: Int): RoadmapWeek? = ROADMAP_WEEKS.firstOrNull { week -> week.days.any { it.day == dayNumber } }

fun nextRoadmapDay(currentTrack: String): RoadmapDay? {
    val currentIndex = ROADMAP_DAYS.indexOfFirst { it.track == currentTrack }
    if (currentIndex == -1) return null
    return ROADMAP_DAYS.drop(currentIndex + 1).firstOrNull()
}
