package com.uccharan.app.data.model

/**
 * Mirrors the lesson schema in CURRICULUM.md §2. Only `speak_repeat` ships
 * in Phase 1, but every field here is designed to carry the other exercise
 * types later without a data-model rewrite.
 *
 * All properties have defaults because Firestore's Kotlin POJO mapping
 * requires a no-arg constructor, which a Kotlin data class only gets when
 * every property has a default value.
 */
data class VocabWord(
    val word: String = "",
    val meaning: String = "",
)

data class LessonPrompt(
    val targetSentence: String = "",
    val focusSounds: List<String> = emptyList(),
    val vocabIntroduced: List<VocabWord> = emptyList(),
    val grammarNote: String = "",
)

data class Lesson(
    val id: String = "",
    val track: String = "",
    val cefrLevel: String = "",
    val unit: String = "",
    val type: String = "speak_repeat",
    val order: Int = 0,
    val prompt: LessonPrompt = LessonPrompt(),
    val xpReward: Int = 10,
)
