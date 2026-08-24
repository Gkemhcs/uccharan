package com.uccharan.app.data.repository

import com.google.firebase.FirebaseNetworkException
import com.google.firebase.auth.FirebaseAuthException

/**
 * Firebase's raw exceptions ("Given String is empty or null", internal error
 * codes) are not something to show a learner. Map the ones we can identify
 * to plain-language messages; fall back to a generic, still-honest message
 * rather than leaking SDK internals.
 */
fun friendlyAuthErrorMessage(throwable: Throwable): String = when {
    throwable is FirebaseNetworkException ->
        "Couldn't reach the server — check your connection and try again."
    throwable is FirebaseAuthException -> when (throwable.errorCode) {
        "ERROR_INVALID_EMAIL" -> "That doesn't look like a valid email address."
        "ERROR_EMAIL_ALREADY_IN_USE" -> "That email already has an account — try signing in instead."
        "ERROR_WRONG_PASSWORD", "ERROR_INVALID_CREDENTIAL", "ERROR_USER_NOT_FOUND" ->
            "That email or password doesn't look right. Please check and try again."
        "ERROR_WEAK_PASSWORD" -> "Please choose a stronger password."
        "ERROR_TOO_MANY_REQUESTS" -> "Too many attempts — please wait a moment and try again."
        "ERROR_USER_DISABLED" -> "This account has been disabled. Contact support if that seems wrong."
        "ERROR_INVALID_VERIFICATION_CODE" -> "That code doesn't look right. Please check and try again."
        "ERROR_SESSION_EXPIRED" -> "That code has expired — request a new one."
        else -> "Something went wrong. Please try again."
    }
    else -> "Something went wrong. Please try again."
}
