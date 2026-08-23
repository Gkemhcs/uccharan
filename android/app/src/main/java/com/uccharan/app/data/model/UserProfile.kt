package com.uccharan.app.data.model

/**
 * One document per user in Firestore's `users` collection, keyed by uid.
 * `onboardingComplete` is what routes a signed-in user to Onboarding vs Home.
 */
data class UserProfile(
    val uid: String = "",
    val displayName: String = "",
    val email: String = "",
    val nativeLanguage: String? = null,
    val preferredAddressTerm: String? = null,
    val onboardingComplete: Boolean = false,
    val currentTrack: String = "foundations",
    val xp: Int = 0,
)
