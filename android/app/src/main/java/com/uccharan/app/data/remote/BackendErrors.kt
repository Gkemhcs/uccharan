package com.uccharan.app.data.remote

import com.google.firebase.crashlytics.FirebaseCrashlytics
import java.io.IOException
import java.net.SocketTimeoutException
import java.net.UnknownHostException

/** Thrown when the backend rejects a call with 401 — the learner's Firebase session token was missing, expired, or invalid. Distinct from a generic [IOException] so [friendlyBackendErrorMessage] can say something actionable instead of a generic connection error. */
class BackendAuthException(message: String) : IOException(message)

/**
 * The backend runs on Render's free tier, which spins the service down after
 * ~15 minutes of inactivity — the next request has to wait for it to wake
 * back up, which can take the better part of a minute. Without this, that
 * shows up to a learner as a plain timeout/"unresponsive" error indistinguishable
 * from their own internet being down, which is confusing and not actionable.
 * [com.uccharan.app.ui.lesson.LessonViewModel] and
 * [com.uccharan.app.ui.practice.PracticeConversationViewModel] additionally
 * surface an "isWakingUp" hint *while* a slow request is still in flight (see
 * their docs), so the learner isn't just staring at a spinner not knowing why.
 */
fun friendlyBackendErrorMessage(throwable: Throwable): String = when (throwable) {
    is BackendAuthException ->
        "Your session has expired — please sign in again."
    is SocketTimeoutException ->
        "Your tutor's server is waking up — this can take up to a minute since we're on free hosting. Please try again."
    is UnknownHostException ->
        "Can't reach the tutor — check your internet connection and try again."
    is IOException ->
        "Couldn't reach the tutor — check your connection and try again."
    else -> "Something went wrong. Please try again."
}

/**
 * Applied to every backend API call's `Result` so every call site gets the
 * same friendly mapping automatically. Also records the failure to
 * Crashlytics as a non-fatal — this is otherwise the only way to learn a
 * backend call is failing in the field once the app is on a learner's phone
 * — except for a cold Render start or no internet, which are expected,
 * already-handled states (see [friendlyBackendErrorMessage]) and would just
 * be noise drowning out failures worth actually looking at.
 */
internal fun <T> Result<T>.withFriendlyBackendError(): Result<T> =
    exceptionOrNull()?.let { error ->
        if (error !is SocketTimeoutException && error !is UnknownHostException) {
            // Swallowed deliberately: this must never be the reason a call
            // fails differently than it otherwise would've — including in
            // plain-JVM unit tests, where Firebase was never initialized.
            runCatching { FirebaseCrashlytics.getInstance().recordException(error) }
        }
        Result.failure(IOException(friendlyBackendErrorMessage(error), error))
    } ?: this
