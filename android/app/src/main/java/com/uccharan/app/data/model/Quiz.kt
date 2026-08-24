package com.uccharan.app.data.model

import com.google.firebase.firestore.PropertyName

/**
 * A multiple-choice quiz closing out a roadmap day (CURRICULUM.md §8).
 * Scored entirely on-device — no AI call needed for multiple-choice — so
 * this feature needed no backend changes, just Firestore content.
 *
 * All properties default for the same reason as [Lesson]: Firestore's Kotlin
 * POJO mapping needs a no-arg constructor.
 */
data class QuizOption(
    val text: String = "",
    // Kotlin compiles a `val isCorrect: Boolean` property to a getter named
    // isCorrect() — Firestore's mapper strips the "is" prefix from that
    // getter to derive the property name it looks for, i.e. "correct", not
    // "isCorrect". Without this annotation it silently deserializes every
    // option as isCorrect=false (confirmed live: every quiz answer scored
    // as wrong regardless of what was tapped). @get:PropertyName pins the
    // Firestore field name explicitly so the getter-name quirk doesn't matter.
    @get:PropertyName("isCorrect")
    val isCorrect: Boolean = false,
)

data class QuizQuestion(
    val question: String = "",
    val options: List<QuizOption> = emptyList(),
    val explanation: String = "",
)

data class Quiz(
    val id: String = "",
    val track: String = "",
    val title: String = "",
    val questions: List<QuizQuestion> = emptyList(),
    val xpReward: Int = 30,
)
