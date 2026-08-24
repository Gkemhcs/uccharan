package com.uccharan.app.data.remote

import java.io.IOException
import java.net.SocketTimeoutException
import java.net.UnknownHostException

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
    is SocketTimeoutException ->
        "Your tutor's server is waking up — this can take up to a minute since we're on free hosting. Please try again."
    is UnknownHostException ->
        "Can't reach the tutor — check your internet connection and try again."
    is IOException ->
        "Couldn't reach the tutor — check your connection and try again."
    else -> "Something went wrong. Please try again."
}

/** Applied to every backend API call's `Result` so every call site gets the same friendly mapping automatically. */
internal fun <T> Result<T>.withFriendlyBackendError(): Result<T> =
    exceptionOrNull()?.let { Result.failure(IOException(friendlyBackendErrorMessage(it), it)) } ?: this
