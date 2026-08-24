package com.uccharan.app.data.repository

import com.google.firebase.firestore.FirebaseFirestore
import com.uccharan.app.data.model.Lesson
import com.uccharan.app.data.model.LessonAttempt
import kotlinx.coroutines.tasks.await

class LessonRepository(
    private val firestore: FirebaseFirestore = FirebaseFirestore.getInstance(),
) {
    /**
     * Lessons for a track, in curriculum order. Sorted client-side rather than
     * via Firestore's `orderBy` — combining an equality filter with orderBy on
     * a different field needs a composite index; sorting ~10-15 lessons in
     * memory is simpler than managing that index for a list this small.
     */
    suspend fun getLessonsForTrack(track: String): Result<List<Lesson>> = runCatching {
        firestore.collection("lessons")
            .whereEqualTo("track", track)
            .get()
            .await()
            .toObjects(Lesson::class.java)
            .sortedBy { it.order }
    }

    suspend fun getLesson(lessonId: String): Result<Lesson?> = runCatching {
        firestore.collection("lessons").document(lessonId).get().await().toObject(Lesson::class.java)
    }

    /** Logs an attempt — see CURRICULUM.md §7: this is the whole data source for future weak-point analytics. */
    suspend fun logAttempt(uid: String, attempt: LessonAttempt): Result<Unit> = runCatching {
        firestore.collection("users").document(uid).collection("attempts").add(attempt).await()
        Unit
    }

    suspend fun markLessonComplete(uid: String, lessonId: String): Result<Unit> = runCatching {
        firestore.collection("users").document(uid)
            .collection("completedLessons").document(lessonId)
            .set(mapOf("completedAt" to com.google.firebase.firestore.FieldValue.serverTimestamp()))
            .await()
    }

    /**
     * Marks several lessons complete in one batch — used by "skip this section"
     * so a learner who already knows the basics can bypass a whole track
     * without stepping through each lesson individually. No XP is awarded,
     * since nothing was actually demonstrated.
     */
    suspend fun markLessonsComplete(uid: String, lessonIds: List<String>): Result<Unit> = runCatching {
        if (lessonIds.isEmpty()) return@runCatching
        val batch = firestore.batch()
        val completedLessons = firestore.collection("users").document(uid).collection("completedLessons")
        lessonIds.forEach { lessonId ->
            batch.set(completedLessons.document(lessonId), mapOf("completedAt" to com.google.firebase.firestore.FieldValue.serverTimestamp()))
        }
        batch.commit().await()
        Unit
    }

    suspend fun getCompletedLessonIds(uid: String): Result<Set<String>> = runCatching {
        firestore.collection("users").document(uid)
            .collection("completedLessons")
            .get()
            .await()
            .documents
            .map { it.id }
            .toSet()
    }
}
