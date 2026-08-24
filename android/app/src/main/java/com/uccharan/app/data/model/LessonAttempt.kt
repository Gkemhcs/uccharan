package com.uccharan.app.data.model

import com.google.firebase.firestore.PropertyName
import com.google.firebase.firestore.ServerTimestamp
import java.util.Date

/**
 * One logged attempt at a lesson, written to Firestore under
 * `users/{uid}/attempts`. Costs nothing extra to store now and is the
 * entire data source for Phase 3's weak-point analytics later
 * (see CURRICULUM.md §7).
 */
data class LessonAttempt(
    val lessonId: String = "",
    val targetSentence: String = "",
    val spokenText: String = "",
    // See the identical annotation on QuizOption.isCorrect — same Kotlin/Firestore
    // "is"-prefixed boolean getter quirk. Currently write-only (never read back
    // into this class yet), but pinned now so it doesn't silently break whenever
    // weak-point analytics starts reading these back.
    @get:PropertyName("isCorrect")
    val isCorrect: Boolean = false,
    val feedback: String = "",
    val nativeExplanation: String? = null,
    /** This lesson's curriculum-authored target pronunciation sound(s) (may be empty) — the weak-point analytics aggregate accuracy per sound across attempts using this. */
    val focusSounds: List<String> = emptyList(),
    @ServerTimestamp val timestamp: Date? = null,
)
