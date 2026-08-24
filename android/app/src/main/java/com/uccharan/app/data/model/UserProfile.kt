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
    /** "male" | "female" | null (unset — [com.uccharan.app.ui.tutor.tutorGenderFromStorage] defaults to female). Purely a visual/identity choice, never sent to the backend. */
    val tutorGender: String? = null,
    val onboardingComplete: Boolean = false,
    val currentTrack: String = "foundations",
    val xp: Int = 0,
)
