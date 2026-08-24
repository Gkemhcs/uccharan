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

    /**
     * Creates a minimal profile on first sign-in if one doesn't already
     * exist. Also patches in [displayName] if the stored profile's is blank
     * and this call has a real one to offer — see
     * [com.uccharan.app.data.repository.AuthRepository.signUpWithEmail]'s
     * doc: email sign-up sets the Firebase Auth display name via a second,
     * separate call, which can race behind RootViewModel's reactive call to
     * this same method (triggered by account creation itself) and lose,
     * leaving the profile doc created with a blank name. Without this
     * patch-on-mismatch step, that blank name would be permanent — this
     * method is otherwise never called again for that user afterward.
     */
    suspend fun ensureProfileExists(uid: String, displayName: String, email: String): Result<Unit> = runCatching {
        val existing = userDoc(uid).get().await()
        if (!existing.exists()) {
            val profile = UserProfile(uid = uid, displayName = displayName, email = email)
            userDoc(uid).set(profile).await()
        } else if (displayName.isNotBlank() && existing.getString("displayName").isNullOrBlank()) {
            userDoc(uid).update("displayName", displayName).await()
        }
    }

    suspend fun completeOnboarding(
        uid: String,
        nativeLanguage: String?,
        preferredAddressTerm: String?,
        tutorGender: String?,
    ): Result<Unit> = runCatching {
        userDoc(uid).update(
            mapOf(
                "nativeLanguage" to nativeLanguage,
                "preferredAddressTerm" to preferredAddressTerm,
                "tutorGender" to tutorGender,
                "onboardingComplete" to true,
            ),
        ).await()
    }

    /** Updates language/address-term/tutor-gender preferences from Settings, without touching onboarding status. */
    suspend fun updatePreferences(
        uid: String,
        nativeLanguage: String?,
        preferredAddressTerm: String?,
        tutorGender: String?,
    ): Result<Unit> = runCatching {
        userDoc(uid).update(
            mapOf(
                "nativeLanguage" to nativeLanguage,
                "preferredAddressTerm" to preferredAddressTerm,
                "tutorGender" to tutorGender,
            ),
        ).await()
    }

    /** Called when a day's quiz is passed, so Home shows the next day's lessons from then on. */
    suspend fun advanceToTrack(uid: String, track: String): Result<Unit> = runCatching {
        userDoc(uid).update("currentTrack", track).await()
    }

    suspend fun addXp(uid: String, amount: Int): Result<Unit> = runCatching {
        firestore.runTransaction { transaction ->
            val snapshot = transaction.get(userDoc(uid))
            val currentXp = snapshot.getLong("xp") ?: 0L
            transaction.update(userDoc(uid), "xp", currentXp + amount)
        }.await()
    }
}
