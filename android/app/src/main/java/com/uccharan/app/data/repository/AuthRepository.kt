package com.uccharan.app.data.repository

import android.content.Context
import androidx.credentials.CredentialManager
import androidx.credentials.CustomCredential
import androidx.credentials.GetCredentialRequest
import com.google.android.libraries.identity.googleid.GetGoogleIdOption
import com.google.android.libraries.identity.googleid.GoogleIdTokenCredential
import com.google.android.libraries.identity.googleid.GoogleIdTokenParsingException
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.FirebaseUser
import com.google.firebase.auth.GoogleAuthProvider
import com.google.firebase.auth.PhoneAuthCredential
import com.uccharan.app.BuildConfig
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import kotlinx.coroutines.tasks.await

/**
 * Wraps Firebase Auth's Task-based API with suspend functions, and handles
 * Sign in with Google via Credential Manager (the current, non-deprecated
 * approach — replaces the old GoogleSignInClient).
 */
class AuthRepository(
    private val firebaseAuth: FirebaseAuth = FirebaseAuth.getInstance(),
) {
    val currentUser: FirebaseUser?
        get() = firebaseAuth.currentUser

    /** Emits the current user on every sign-in/sign-out, including immediately on collection. */
    val authStateFlow: Flow<FirebaseUser?> = callbackFlow {
        val listener = FirebaseAuth.AuthStateListener { auth -> trySend(auth.currentUser) }
        firebaseAuth.addAuthStateListener(listener)
        awaitClose { firebaseAuth.removeAuthStateListener(listener) }
    }

    suspend fun signUpWithEmail(email: String, password: String): Result<FirebaseUser> = runCatching {
        firebaseAuth.createUserWithEmailAndPassword(email, password).await().user
            ?: error("Sign-up succeeded but returned no user")
    }.withFriendlyAuthError()

    suspend fun signInWithEmail(email: String, password: String): Result<FirebaseUser> = runCatching {
        firebaseAuth.signInWithEmailAndPassword(email, password).await().user
            ?: error("Sign-in succeeded but returned no user")
    }.withFriendlyAuthError()

    /**
     * Launches the system Sign in with Google sheet via Credential Manager,
     * then exchanges the resulting Google ID token for a Firebase session.
     */
    suspend fun signInWithGoogle(context: Context): Result<FirebaseUser> = runCatching {
        val credentialManager = CredentialManager.create(context)

        val googleIdOption = GetGoogleIdOption.Builder()
            .setFilterByAuthorizedAccounts(false)
            .setServerClientId(BuildConfig.GOOGLE_WEB_CLIENT_ID)
            .build()

        val request = GetCredentialRequest.Builder()
            .addCredentialOption(googleIdOption)
            .build()

        val result = credentialManager.getCredential(context, request)
        val credential = result.credential

        if (credential !is CustomCredential || credential.type != GoogleIdTokenCredential.TYPE_GOOGLE_ID_TOKEN_CREDENTIAL) {
            error("Unexpected credential type from Credential Manager: ${credential.type}")
        }

        val googleIdToken = try {
            GoogleIdTokenCredential.createFrom(credential.data).idToken
        } catch (e: GoogleIdTokenParsingException) {
            throw IllegalStateException("Could not parse Google ID token", e)
        }

        val firebaseCredential = GoogleAuthProvider.getCredential(googleIdToken, null)
        firebaseAuth.signInWithCredential(firebaseCredential).await().user
            ?: error("Google sign-in succeeded but returned no Firebase user")
    }.withFriendlyAuthError()

    /** Exchanges a phone verification credential (auto-verified or OTP-built) for a Firebase session. */
    suspend fun signInWithPhoneCredential(credential: PhoneAuthCredential): Result<FirebaseUser> = runCatching {
        firebaseAuth.signInWithCredential(credential).await().user
            ?: error("Phone sign-in succeeded but returned no user")
    }.withFriendlyAuthError()

    fun signOut() {
        firebaseAuth.signOut()
    }

    private fun <T> Result<T>.withFriendlyAuthError(): Result<T> = fold(
        onSuccess = { Result.success(it) },
        onFailure = { Result.failure(Exception(friendlyAuthErrorMessage(it), it)) },
    )
}
