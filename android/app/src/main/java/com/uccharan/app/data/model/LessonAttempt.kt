package com.uccharan.app.data.model

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
    val isCorrect: Boolean = false,
    val feedback: String = "",
    val nativeExplanation: String? = null,
    @ServerTimestamp val timestamp: Date? = null,
)
