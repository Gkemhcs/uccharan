package com.uccharan.app.ui.tutor

/**
 * The learner's chosen tutor persona — asked once at onboarding (changeable
 * later from Profile), so the same character shows up consistently across
 * lessons, quizzes, and practice conversations instead of feeling anonymous.
 * Purely a client-side visual/identity choice — the backend tutor persona
 * prompt (`GeminiService.PRACTICE_PROMPT_TEMPLATE`) is deliberately left
 * unchanged so this can't destabilize the actual conversation behavior.
 */
enum class TutorGender(val emoji: String, val label: String) {
    FEMALE("👩‍🏫", "Female Tutor"),
    MALE("👨‍🏫", "Male Tutor"),
}

/** `null`/unrecognized stored values fall back to [TutorGender.FEMALE] — never a crash, always a sensible default. */
fun tutorGenderFromStorage(value: String?): TutorGender = when (value) {
    "male" -> TutorGender.MALE
    "female" -> TutorGender.FEMALE
    else -> TutorGender.FEMALE
}

fun TutorGender.toStorageValue(): String = when (this) {
    TutorGender.MALE -> "male"
    TutorGender.FEMALE -> "female"
}
