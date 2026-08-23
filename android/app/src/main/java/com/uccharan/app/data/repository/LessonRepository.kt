package com.uccharan.app.data.repository

import com.google.firebase.firestore.FirebaseFirestore
import com.uccharan.app.data.model.Lesson
import com.uccharan.app.data.model.LessonAttempt
import kotlinx.coroutines.tasks.await

class LessonRepository(
    private val firestore: FirebaseFirestore = FirebaseFirestore.getInstance(),
) {
    /** Lessons for a track, in curriculum order. Cached by Firestore's default offline persistence. */
    suspend fun getLessonsForTrack(track: String): Result<List<Lesson>> = runCatching {
        firestore.collection("lessons")
            .whereEqualTo("track", track)
            .orderBy("order")
            .get()
            .await()
            .toObjects(Lesson::class.java)
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
