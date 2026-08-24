package com.uccharan.app.data.repository

import com.google.firebase.firestore.FieldValue
import com.google.firebase.firestore.FirebaseFirestore
import com.uccharan.app.data.model.Quiz
import kotlinx.coroutines.tasks.await

/** A quiz attempt counts as a pass at 70% or better — matches SUCCESS_CRITERIA framing in CURRICULUM.md §2. */
const val QUIZ_PASS_THRESHOLD = 0.7

/**
 * A stored quiz result — one per quiz per user (retaking a quiz overwrites
 * the previous record for that quiz, so this is "your latest attempt at
 * each quiz", which is what the Profile progress view needs, not a full
 * audit trail of every retake).
 */
data class QuizAttemptRecord(
    val quizId: String = "",
    val title: String = "",
    val correctCount: Int = 0,
    val totalCount: Int = 0,
    val xpEarned: Int = 0,
    val passed: Boolean = false,
)

class QuizRepository(
    private val firestore: FirebaseFirestore = FirebaseFirestore.getInstance(),
) {
    suspend fun getQuiz(quizId: String): Result<Quiz?> = runCatching {
        firestore.collection("quizzes").document(quizId).get().await().toObject(Quiz::class.java)
    }

    /** Records a finished attempt; only a pass unlocks the next day, but every attempt is logged. */
    suspend fun recordAttempt(
        uid: String,
        quizId: String,
        title: String,
        correctCount: Int,
        totalCount: Int,
        xpEarned: Int,
    ): Result<Unit> = runCatching {
        val passed = totalCount > 0 && correctCount.toDouble() / totalCount >= QUIZ_PASS_THRESHOLD
        firestore.collection("users").document(uid)
            .collection("quizAttempts").document(quizId)
            .set(
                mapOf(
                    "title" to title,
                    "correctCount" to correctCount,
                    "totalCount" to totalCount,
                    "xpEarned" to xpEarned,
                    "passed" to passed,
                    "attemptedAt" to FieldValue.serverTimestamp(),
                ),
            )
            .await()
        Unit
    }

    suspend fun getPassedQuizIds(uid: String): Result<Set<String>> = runCatching {
        firestore.collection("users").document(uid)
            .collection("quizAttempts")
            .whereEqualTo("passed", true)
            .get()
            .await()
            .documents
            .map { it.id }
            .toSet()
    }

    /** Every quiz the learner has attempted at least once, most recently authored day first (quiz ids sort as "quiz-day-N"). */
    suspend fun getAttemptHistory(uid: String): Result<List<QuizAttemptRecord>> = runCatching {
        firestore.collection("users").document(uid)
            .collection("quizAttempts")
            .get()
            .await()
            .documents
            .mapNotNull { doc -> doc.toObject(QuizAttemptRecord::class.java)?.copy(quizId = doc.id) }
            .sortedByDescending { it.quizId }
    }
}
