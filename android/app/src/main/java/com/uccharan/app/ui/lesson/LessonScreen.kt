package com.uccharan.app.ui.lesson

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.VolumeUp
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.FilledIconButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.uccharan.app.di.LocalAppContainer
import com.uccharan.app.di.uccharanViewModel
import java.util.Locale

@Composable
fun LessonScreen(lessonId: String, onLessonFinished: () -> Unit) {
    val context = LocalContext.current
    val container = LocalAppContainer.current
    val viewModel = uccharanViewModel {
        LessonViewModel(lessonId, container.authRepository, container.userProfileRepository, container.lessonRepository, container.correctionApi)
    }
    val uiState by viewModel.uiState.collectAsState()

    var textToSpeech by remember { mutableStateOf<TextToSpeech?>(null) }
    DisposableEffect(Unit) {
        val tts = TextToSpeech(context) { }
        textToSpeech = tts
        onDispose { tts.shutdown() }
    }

    val permissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        if (granted) {
            startListening(context, viewModel)
        } else {
            viewModel.onSpeechError("Microphone permission is needed to practice speaking.")
        }
    }

    fun onMicClick() {
        val hasPermission = ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) ==
            PackageManager.PERMISSION_GRANTED
        if (hasPermission) {
            startListening(context, viewModel)
        } else {
            permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
        }
    }

    Column(modifier = Modifier.fillMaxSize().padding(24.dp)) {
        when {
            uiState.isLoadingLesson -> Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
            uiState.lesson == null -> Text(uiState.errorMessage ?: "Lesson not found", color = MaterialTheme.colorScheme.error)
            else -> {
                val lesson = uiState.lesson!!

                Text("Say this out loud", style = MaterialTheme.typography.titleMedium)
                Spacer(modifier = Modifier.height(12.dp))

                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = lesson.prompt.targetSentence,
                        style = MaterialTheme.typography.headlineSmall,
                        modifier = Modifier.weight(1f),
                    )
                    IconButton(onClick = {
                        textToSpeech?.language = Locale.US
                        textToSpeech?.speak(lesson.prompt.targetSentence, TextToSpeech.QUEUE_FLUSH, null, null)
                    }) {
                        Icon(Icons.AutoMirrored.Filled.VolumeUp, contentDescription = "Listen")
                    }
                }

                if (lesson.prompt.grammarNote.isNotBlank()) {
                    Text(
                        text = lesson.prompt.grammarNote,
                        style = MaterialTheme.typography.bodySmall,
                        modifier = Modifier.padding(top = 8.dp),
                    )
                }

                Spacer(modifier = Modifier.weight(1f))

                uiState.errorMessage?.let { message ->
                    Text(message, color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(bottom = 12.dp))
                }

                uiState.correctionResult?.let { result ->
                    FeedbackCard(spokenText = uiState.lastSpokenText.orEmpty(), result = result)
                    Spacer(modifier = Modifier.height(16.dp))
                }

                when {
                    uiState.isLessonComplete -> Button(onClick = onLessonFinished, modifier = Modifier.fillMaxWidth()) {
                        Text("Continue")
                    }
                    uiState.correctionResult != null && !uiState.correctionResult!!.isCorrect -> Button(
                        onClick = viewModel::retry,
                        modifier = Modifier.fillMaxWidth(),
                    ) { Text("Try again") }
                    uiState.isCheckingAttempt -> Box(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
                        CircularProgressIndicator()
                    }
                    else -> Box(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
                        MicButton(isListening = uiState.isListening, onClick = ::onMicClick)
                    }
                }
            }
        }
    }
}

@Composable
private fun MicButton(isListening: Boolean, onClick: () -> Unit) {
    FilledIconButton(
        onClick = onClick,
        modifier = Modifier.size(72.dp),
        colors = androidx.compose.material3.IconButtonDefaults.filledIconButtonColors(
            containerColor = if (isListening) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.primary,
        ),
    ) {
        Icon(Icons.Filled.Mic, contentDescription = if (isListening) "Listening…" else "Tap to speak", modifier = Modifier.size(32.dp))
    }
}

@Composable
private fun FeedbackCard(spokenText: String, result: com.uccharan.app.data.remote.CorrectionResult) {
    val containerColor = if (result.isCorrect) MaterialTheme.colorScheme.tertiaryContainer else MaterialTheme.colorScheme.errorContainer
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(16.dp))
            .background(containerColor)
            .padding(16.dp),
    ) {
        Text("You said: “$spokenText”", style = MaterialTheme.typography.bodySmall)
        Spacer(modifier = Modifier.height(8.dp))
        Text(result.feedback, style = MaterialTheme.typography.bodyLarge)
        result.nativeExplanation?.let { native ->
            Spacer(modifier = Modifier.height(8.dp))
            Text(native, style = MaterialTheme.typography.bodyMedium)
        }
    }
}

/**
 * SpeechRecognizer is callback-based and framework-bound, so it's driven from
 * here (UI layer) rather than the ViewModel — the ViewModel only receives the
 * final recognized text via [LessonViewModel.onSpeechRecognized], keeping it
 * unit-testable without any Android framework dependency.
 */
private fun startListening(context: android.content.Context, viewModel: LessonViewModel) {
    if (!SpeechRecognizer.isRecognitionAvailable(context)) {
        viewModel.onSpeechError("Speech recognition isn't available on this device.")
        return
    }

    viewModel.onListeningStarted()
    val recognizer = SpeechRecognizer.createSpeechRecognizer(context)
    val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
        putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
        putExtra(RecognizerIntent.EXTRA_LANGUAGE, "en-US")
    }

    recognizer.setRecognitionListener(object : RecognitionListener {
        override fun onResults(results: Bundle) {
            val text = results.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull()
            if (text != null) viewModel.onSpeechRecognized(text) else viewModel.onSpeechError("Didn't catch that — try again.")
            recognizer.destroy()
        }

        override fun onError(error: Int) {
            viewModel.onSpeechError("Didn't catch that — try again.")
            recognizer.destroy()
        }

        override fun onReadyForSpeech(params: Bundle?) = Unit
        override fun onBeginningOfSpeech() = Unit
        override fun onRmsChanged(rmsdB: Float) = Unit
        override fun onBufferReceived(buffer: ByteArray?) = Unit
        override fun onEndOfSpeech() = Unit
        override fun onPartialResults(partialResults: Bundle?) = Unit
        override fun onEvent(eventType: Int, params: Bundle?) = Unit
    })

    recognizer.startListening(intent)
}
