package com.uccharan.app.data.repository

import com.google.firebase.firestore.FieldValue
import com.google.firebase.firestore.FirebaseFirestore
import com.uccharan.app.data.model.Quiz
import kotlinx.coroutines.tasks.await

/** A quiz attempt counts as a pass at 70% or better — matches SUCCESS_CRITERIA framing in CURRICULUM.md §2. */
const val QUIZ_PASS_THRESHOLD = 0.7

/**
 * A stored quiz result — one per quiz per user. Retaking a quiz updates this
 * record with the LATEST attempt's score, but `passed` is sticky: once a
 * learner has passed a quiz, a later lower-scoring review attempt (retaking
 * it on purpose to revise) can never flip it back to failed — see
 * [QuizRepository.recordAttempt]. `correctCount`/`totalCount`/`xpEarned`
 * still reflect the most recent attempt, since that's what the Profile
 * screen's quiz-history list is showing "your latest attempt", not `passed`.
 */
data class QuizAttemptRecord(
    val quizId: String = "",
    val title: String = "",
    val correctCount: Int = 0,
    val totalCount: Int = 0,
    val xpEarned: Int = 0,
    val passed: Boolean = false,
)

/** [passed] is the record's sticky "ever passed" state (see [QuizRepository.recordAttempt]); [isFirstPass] is true only the one time it flips false→true, which is when XP/advancement should happen — never on a later re-pass of a review attempt. */
data class QuizAttemptOutcome(val passed: Boolean, val isFirstPass: Boolean)

class QuizRepository(
    private val firestore: FirebaseFirestore = FirebaseFirestore.getInstance(),
) {
    suspend fun getQuiz(quizId: String): Result<Quiz?> = runCatching {
        firestore.collection("quizzes").document(quizId).get().await().toObject(Quiz::class.java)
    }

    /**
     * Records a finished attempt. `passed` is a transactional read-then-write
     * (not a blind overwrite) specifically so that reviewing an already-passed
     * quiz and scoring below 70% this time can't erase the earlier pass —
     * confirmed live as a real bug: a learner revisiting Day 1 to revise lost
     * their Day 1 completion because a review attempt scored lower than their
     * original pass. `xpEarned`/next-day unlock should only ever happen once
     * per quiz — see [QuizAttemptOutcome.isFirstPass].
     */
    suspend fun recordAttempt(
        uid: String,
        quizId: String,
        title: String,
        correctCount: Int,
        totalCount: Int,
        xpEarned: Int,
    ): Result<QuizAttemptOutcome> = runCatching {
        val passedThisAttempt = totalCount > 0 && correctCount.toDouble() / totalCount >= QUIZ_PASS_THRESHOLD
        val docRef = firestore.collection("users").document(uid).collection("quizAttempts").document(quizId)
        firestore.runTransaction { transaction ->
            val existing = transaction.get(docRef)
            val wasAlreadyPassed = existing.getBoolean("passed") == true
            val stickyPassed = passedThisAttempt || wasAlreadyPassed
            transaction.set(
                docRef,
                mapOf(
                    "title" to title,
                    "correctCount" to correctCount,
                    "totalCount" to totalCount,
                    "xpEarned" to xpEarned,
                    "passed" to stickyPassed,
                    "attemptedAt" to FieldValue.serverTimestamp(),
                ),
            )
            QuizAttemptOutcome(passed = stickyPassed, isFirstPass = passedThisAttempt && !wasAlreadyPassed)
        }.await()
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
