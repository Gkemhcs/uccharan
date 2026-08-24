package com.uccharan.app.ui.speech

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.util.Log

private const val TAG = "SpeechRecognition"

/**
 * SpeechRecognizer is callback-based and framework-bound, so it's driven
 * from the UI layer rather than any ViewModel — callers only receive the
 * final recognized text, keeping their ViewModels unit-testable without any
 * Android framework dependency. Shared between [com.uccharan.app.ui.lesson.LessonScreen]
 * and [com.uccharan.app.ui.practice.PracticeConversationScreen] — both are
 * "listen to what the learner says" moments, just with different callbacks.
 */
fun startListening(
    context: Context,
    onListeningStarted: () -> Unit,
    onSpeechError: (String) -> Unit,
    onSpeechRecognized: (String) -> Unit,
) {
    if (!SpeechRecognizer.isRecognitionAvailable(context)) {
        Log.w(TAG, "isRecognitionAvailable() returned false — no recognizer service on this device/build")
        onSpeechError("Speech recognition isn't available on this device.")
        return
    }

    onListeningStarted()
    val recognizer = SpeechRecognizer.createSpeechRecognizer(context)
    val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
        putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
        putExtra(RecognizerIntent.EXTRA_LANGUAGE, "en-US")
    }

    recognizer.setRecognitionListener(object : RecognitionListener {
        override fun onResults(results: Bundle) {
            val text = results.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull()
            Log.d(TAG, "onResults: recognized=\"$text\"")
            if (text != null) onSpeechRecognized(text) else onSpeechError("Didn't catch that — try again.")
            recognizer.destroy()
        }

        override fun onError(error: Int) {
            Log.w(TAG, "onError: code=$error (${describeError(error)})")
            onSpeechError("Didn't catch that — try again.")
            recognizer.destroy()
        }

        override fun onReadyForSpeech(params: Bundle?) { Log.d(TAG, "onReadyForSpeech") }
        override fun onBeginningOfSpeech() { Log.d(TAG, "onBeginningOfSpeech") }
        override fun onRmsChanged(rmsdB: Float) = Unit
        override fun onBufferReceived(buffer: ByteArray?) = Unit
        override fun onEndOfSpeech() { Log.d(TAG, "onEndOfSpeech") }
        override fun onPartialResults(partialResults: Bundle?) = Unit
        override fun onEvent(eventType: Int, params: Bundle?) = Unit
    })

    Log.d(TAG, "startListening() calling recognizer.startListening")
    recognizer.startListening(intent)
}

private fun describeError(error: Int): String = when (error) {
    SpeechRecognizer.ERROR_AUDIO -> "ERROR_AUDIO — audio recording problem"
    SpeechRecognizer.ERROR_CLIENT -> "ERROR_CLIENT — client-side error"
    SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> "ERROR_INSUFFICIENT_PERMISSIONS"
    SpeechRecognizer.ERROR_NETWORK -> "ERROR_NETWORK"
    SpeechRecognizer.ERROR_NETWORK_TIMEOUT -> "ERROR_NETWORK_TIMEOUT"
    SpeechRecognizer.ERROR_NO_MATCH -> "ERROR_NO_MATCH — heard audio but couldn't match it to anything"
    SpeechRecognizer.ERROR_RECOGNIZER_BUSY -> "ERROR_RECOGNIZER_BUSY"
    SpeechRecognizer.ERROR_SERVER -> "ERROR_SERVER"
    SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> "ERROR_SPEECH_TIMEOUT — no speech input detected at all (likely no mic audio reaching the recognizer)"
    else -> "unknown error code"
}
