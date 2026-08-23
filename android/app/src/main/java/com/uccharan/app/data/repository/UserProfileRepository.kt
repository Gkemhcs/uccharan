package com.uccharan.app.data.repository

import com.google.firebase.firestore.FirebaseFirestore
import com.uccharan.app.data.model.UserProfile
import kotlinx.coroutines.tasks.await

class UserProfileRepository(
    private val firestore: FirebaseFirestore = FirebaseFirestore.getInstance(),
) {
    private fun userDoc(uid: String) = firestore.collection("users").document(uid)

    suspend fun getProfile(uid: String): Result<UserProfile?> = runCatching {
        userDoc(uid).get().await().toObject(UserProfile::class.java)
    }

    /** Creates a minimal profile on first sign-in if one doesn't already exist. */
    suspend fun ensureProfileExists(uid: String, displayName: String, email: String): Result<Unit> = runCatching {
        val existing = userDoc(uid).get().await()
        if (!existing.exists()) {
            val profile = UserProfile(uid = uid, displayName = displayName, email = email)
            userDoc(uid).set(profile).await()
        }
    }

    suspend fun completeOnboarding(
        uid: String,
        nativeLanguage: String?,
        preferredAddressTerm: String?,
    ): Result<Unit> = runCatching {
        userDoc(uid).update(
            mapOf(
                "nativeLanguage" to nativeLanguage,
                "preferredAddressTerm" to preferredAddressTerm,
                "onboardingComplete" to true,
            ),
        ).await()
    }

    suspend fun addXp(uid: String, amount: Int): Result<Unit> = runCatching {
        firestore.runTransaction { transaction ->
            val snapshot = transaction.get(userDoc(uid))
            val currentXp = snapshot.getLong("xp") ?: 0L
            transaction.update(userDoc(uid), "xp", currentXp + amount)
        }.await()
    }
}
