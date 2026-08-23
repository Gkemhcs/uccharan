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
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.automirrored.filled.VolumeUp
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
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
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.uccharan.app.data.remote.CorrectionResult
import com.uccharan.app.di.LocalAppContainer
import com.uccharan.app.di.uccharanViewModel
import com.uccharan.app.ui.theme.LocalUccharanGradients
import java.util.Locale

@Composable
fun LessonScreen(lessonId: String, onLessonFinished: () -> Unit) {
    val context = LocalContext.current
    val container = LocalAppContainer.current
    val viewModel = uccharanViewModel {
        LessonViewModel(lessonId, container.authRepository, container.userProfileRepository, container.lessonRepository, container.correctionApi)
    }
    val uiState by viewModel.uiState.collectAsState()
    val gradients = LocalUccharanGradients.current

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

    Column(modifier = Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background)) {
        when {
            uiState.isLoadingLesson -> Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
            uiState.lesson == null -> Text(
                uiState.errorMessage ?: "Lesson not found",
                color = MaterialTheme.colorScheme.error,
                modifier = Modifier.padding(24.dp),
            )
            else -> {
                val lesson = uiState.lesson!!

                Row(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp).padding(top = 8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween,
                ) {
                    Box(
                        modifier = Modifier
                            .size(44.dp)
                            .clip(CircleShape)
                            .clickable(onClick = onLessonFinished),
                        contentAlignment = Alignment.Center,
                    ) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                    Text(lesson.unit, style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Box(modifier = Modifier.size(44.dp))
                }

                Column(modifier = Modifier.padding(horizontal = 24.dp).padding(top = 20.dp)) {
                    Text(
                        "SAY THIS OUT LOUD",
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.primary,
                    )
                    Spacer(modifier = Modifier.height(12.dp))

                    Row(verticalAlignment = Alignment.Top) {
                        val isMidAttempt = uiState.isListening
                        Text(
                            text = lesson.prompt.targetSentence,
                            style = MaterialTheme.typography.titleLarge,
                            color = if (isMidAttempt) MaterialTheme.colorScheme.onSurfaceVariant else MaterialTheme.colorScheme.onBackground,
                            modifier = Modifier.weight(1f),
                        )
                        if (!isMidAttempt) {
                            Box(
                                modifier = Modifier
                                    .size(46.dp)
                                    .clip(CircleShape)
                                    .background(MaterialTheme.colorScheme.surface)
                                    .shadow(elevation = 4.dp, shape = CircleShape)
                                    .clickable {
                                        textToSpeech?.language = Locale.US
                                        textToSpeech?.speak(lesson.prompt.targetSentence, TextToSpeech.QUEUE_FLUSH, null, null)
                                    },
                                contentAlignment = Alignment.Center,
                            ) {
                                Icon(Icons.AutoMirrored.Filled.VolumeUp, contentDescription = "Listen", tint = MaterialTheme.colorScheme.primary)
                            }
                        }
                    }
                    if (lesson.prompt.grammarNote.isNotBlank() && uiState.correctionResult == null) {
                        Spacer(modifier = Modifier.height(10.dp))
                        Text(
                            text = lesson.prompt.grammarNote,
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }

                Spacer(modifier = Modifier.weight(1f))

                Column(modifier = Modifier.padding(horizontal = 24.dp)) {
                    uiState.errorMessage?.let { message ->
                        Text(message, color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(bottom = 12.dp))
                    }

                    uiState.correctionResult?.let { result ->
                        FeedbackCard(spokenText = uiState.lastSpokenText.orEmpty(), result = result)
                        Spacer(modifier = Modifier.height(18.dp))
                    }
                }

                Box(modifier = Modifier.padding(bottom = 56.dp)) {
                    when {
                        uiState.isLessonComplete -> Box(modifier = Modifier.padding(horizontal = 24.dp)) {
                            GradientCta(text = "Continue", icon = Icons.AutoMirrored.Filled.ArrowForward, onClick = onLessonFinished, brush = gradients.primaryButton)
                        }
                        uiState.correctionResult != null && uiState.correctionResult?.isCorrect == false -> Box(modifier = Modifier.padding(horizontal = 24.dp)) {
                            GradientCta(text = "Try again", icon = Icons.Filled.Refresh, onClick = viewModel::retry, brush = gradients.primaryButton)
                        }
                        uiState.isCheckingAttempt -> Box(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
                            CircularProgressIndicator()
                        }
                        else -> Column(modifier = Modifier.fillMaxWidth(), horizontalAlignment = Alignment.CenterHorizontally) {
                            if (uiState.isListening) {
                                SoundWave()
                                Spacer(modifier = Modifier.height(22.dp))
                            }
                            MicButton(isListening = uiState.isListening, onClick = ::onMicClick)
                            Spacer(modifier = Modifier.height(14.dp))
                            Text(
                                if (uiState.isListening) "Listening…" else "Tap to speak",
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = FontWeight.SemiBold,
                                color = if (uiState.isListening) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun MicButton(isListening: Boolean, onClick: () -> Unit) {
    val gradients = LocalUccharanGradients.current
    val brush = if (isListening) gradients.listening else gradients.primaryButton
    val glow = if (isListening) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.primary

    Box(
        modifier = Modifier
            .size(84.dp)
            .shadow(elevation = 20.dp, shape = CircleShape, ambientColor = glow, spotColor = glow)
            .clip(CircleShape)
            .background(brush)
            .clickable(onClick = onClick),
        contentAlignment = Alignment.Center,
    ) {
        Icon(
            Icons.Filled.Mic,
            contentDescription = if (isListening) "Listening…" else "Tap to speak",
            tint = MaterialTheme.colorScheme.onPrimary,
            modifier = Modifier.size(32.dp),
        )
    }
}

@Composable
private fun SoundWave() {
    val heights = listOf(10, 22, 14, 32, 18, 26, 12)
    Row(verticalAlignment = Alignment.Bottom, horizontalArrangement = Arrangement.spacedBy(4.dp)) {
        heights.forEach { h ->
            Box(
                modifier = Modifier
                    .width(4.dp)
                    .height(h.dp)
                    .clip(RoundedCornerShape(2.dp))
                    .background(MaterialTheme.colorScheme.error),
            )
        }
    }
}

@Composable
private fun GradientCta(text: String, icon: androidx.compose.ui.graphics.vector.ImageVector, onClick: () -> Unit, brush: androidx.compose.ui.graphics.Brush) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .shadow(elevation = 16.dp, shape = RoundedCornerShape(16.dp), ambientColor = MaterialTheme.colorScheme.primary, spotColor = MaterialTheme.colorScheme.primary)
            .clip(RoundedCornerShape(16.dp))
            .background(brush)
            .clickable(onClick = onClick)
            .padding(vertical = 17.dp),
        contentAlignment = Alignment.Center,
    ) {
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(text, style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.onPrimary)
            Icon(icon, contentDescription = null, tint = MaterialTheme.colorScheme.onPrimary, modifier = Modifier.size(16.dp))
        }
    }
}

@Composable
private fun FeedbackCard(spokenText: String, result: CorrectionResult) {
    val isCorrect = result.isCorrect
    val containerColor = if (isCorrect) MaterialTheme.colorScheme.tertiaryContainer else MaterialTheme.colorScheme.errorContainer
    val onContainerColor = if (isCorrect) MaterialTheme.colorScheme.onTertiaryContainer else MaterialTheme.colorScheme.onErrorContainer

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .shadow(elevation = 10.dp, shape = RoundedCornerShape(22.dp))
            .clip(RoundedCornerShape(22.dp))
            .background(containerColor)
            .padding(22.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            Box(
                modifier = Modifier
                    .size(34.dp)
                    .clip(CircleShape)
                    .background(if (isCorrect) MaterialTheme.colorScheme.tertiary else MaterialTheme.colorScheme.error),
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    if (isCorrect) Icons.Filled.Mic else Icons.Filled.Refresh,
                    contentDescription = null,
                    tint = if (isCorrect) MaterialTheme.colorScheme.onTertiary else MaterialTheme.colorScheme.onError,
                    modifier = Modifier.size(16.dp),
                )
            }
            Text(
                if (isCorrect) "Perfect!" else "Almost there",
                style = MaterialTheme.typography.titleMedium,
                color = onContainerColor,
            )
        }
        Spacer(modifier = Modifier.height(14.dp))
        Text("YOU SAID", style = MaterialTheme.typography.labelSmall, color = onContainerColor)
        Spacer(modifier = Modifier.height(4.dp))
        Text("\"$spokenText\"", style = MaterialTheme.typography.bodyMedium, color = onContainerColor)
        Spacer(modifier = Modifier.height(14.dp))
        Text(result.feedback, style = MaterialTheme.typography.bodyLarge, color = onContainerColor)

        result.nativeExplanation?.let { native ->
            androidx.compose.material3.HorizontalDivider(
                modifier = Modifier.padding(vertical = 16.dp),
                color = onContainerColor.copy(alpha = 0.2f),
            )
            Text(native, style = MaterialTheme.typography.bodyLarge, color = onContainerColor)
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
