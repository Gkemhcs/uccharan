package com.uccharan.app.ui.practice

import android.Manifest
import android.content.pm.PackageManager
import android.speech.tts.TextToSpeech
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.VolumeUp
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.uccharan.app.data.remote.PracticeMessage
import com.uccharan.app.di.LocalAppContainer
import com.uccharan.app.di.uccharanViewModel
import com.uccharan.app.ui.lesson.MicButton
import com.uccharan.app.ui.lesson.SoundWave
import com.uccharan.app.ui.speech.startListening
import com.uccharan.app.ui.theme.LocalUccharanGradients
import com.uccharan.app.ui.theme.NotoSansTelugu
import com.uccharan.app.ui.tutor.TutorCharacter
import com.uccharan.app.ui.tutor.TutorGender
import java.util.Locale

private val TELUGU_LOCALE: Locale = Locale.Builder().setLanguage("te").setRegion("IN").build()

@Composable
fun PracticeConversationScreen(topic: String, onBack: () -> Unit) {
    val context = LocalContext.current
    val container = LocalAppContainer.current
    val viewModel = uccharanViewModel {
        PracticeConversationViewModel(topic, container.authRepository, container.userProfileRepository, container.practiceApi)
    }
    val uiState by viewModel.uiState.collectAsState()
    val gradients = LocalUccharanGradients.current

    var textToSpeech by remember { mutableStateOf<TextToSpeech?>(null) }
    DisposableEffect(Unit) {
        val tts = TextToSpeech(context) { }
        textToSpeech = tts
        onDispose { tts.shutdown() }
    }

    // Auto-play each new tutor line as it arrives — a real conversation
    // partner speaks without being asked. lastSpokenCount guards against
    // re-speaking on recomposition/rotation.
    var lastSpokenCount by remember { mutableIntStateOf(0) }
    LaunchedEffect(uiState.messages.size) {
        val messages = uiState.messages
        if (messages.size > lastSpokenCount) {
            val latest = messages.last()
            if (latest.speaker == "tutor") {
                textToSpeech?.language = Locale.US
                textToSpeech?.speak(latest.text, TextToSpeech.QUEUE_FLUSH, null, null)
            }
            lastSpokenCount = messages.size
        }
    }

    val permissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        if (granted) {
            startListening(context, viewModel::onListeningStarted, viewModel::onSpeechError, viewModel::onSpeechRecognized)
        } else {
            viewModel.onSpeechError("Microphone permission is needed to practice speaking.")
        }
    }

    fun onMicClick() {
        val hasPermission = ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) ==
            PackageManager.PERMISSION_GRANTED
        if (hasPermission) {
            startListening(context, viewModel::onListeningStarted, viewModel::onSpeechError, viewModel::onSpeechRecognized)
        } else {
            permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
        }
    }

    Column(modifier = Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background)) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp).padding(top = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Box(
                modifier = Modifier.size(44.dp).clip(CircleShape).clickable(onClick = onBack),
                contentAlignment = Alignment.Center,
            ) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
            }
            Text(
                uiState.topic,
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onBackground,
            )
        }

        SceneBanner(topic = uiState.topic, tutorGender = uiState.tutorGender)

        val listState = rememberLazyListState()
        LaunchedEffect(uiState.messages.size) {
            if (uiState.messages.isNotEmpty()) listState.animateScrollToItem(uiState.messages.lastIndex)
        }

        LazyColumn(
            state = listState,
            modifier = Modifier.weight(1f),
            contentPadding = PaddingValues(horizontal = 20.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            itemsIndexed(uiState.messages) { index, message ->
                val isLatestTutorMessage = message.speaker == "tutor" && index == uiState.messages.lastIndex
                MessageBubble(message = message, tutorGender = uiState.tutorGender)
                if (isLatestTutorMessage && (uiState.lastCorrection != null || uiState.lastNativeNote != null)) {
                    Spacer(modifier = Modifier.height(6.dp))
                    CorrectionNote(
                        correction = uiState.lastCorrection,
                        nativeNote = uiState.lastNativeNote,
                        onPlayNative = {
                            uiState.lastNativeNote?.let { note ->
                                textToSpeech?.language = TELUGU_LOCALE
                                textToSpeech?.speak(note, TextToSpeech.QUEUE_FLUSH, null, null)
                            }
                        },
                    )
                }
            }
        }

        uiState.errorMessage?.let { message ->
            Text(
                message,
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier.padding(horizontal = 24.dp, vertical = 4.dp),
            )
        }

        Column(
            modifier = Modifier.fillMaxWidth().padding(bottom = 40.dp, top = 8.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            when {
                uiState.isWaitingForTutor -> {
                    CircularProgressIndicator(modifier = Modifier.size(32.dp))
                    Spacer(modifier = Modifier.height(10.dp))
                    Text(
                        if (uiState.isWakingUp) {
                            "Your tutor's server is waking up — this can take up to a minute on free hosting…"
                        } else {
                            "Your tutor is thinking…"
                        },
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        textAlign = TextAlign.Center,
                        modifier = Modifier.padding(horizontal = 32.dp),
                    )
                }
                else -> {
                    if (uiState.isListening) {
                        SoundWave()
                        Spacer(modifier = Modifier.height(18.dp))
                    }
                    MicButton(isListening = uiState.isListening, onClick = ::onMicClick)
                    Spacer(modifier = Modifier.height(10.dp))
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

@Composable
private fun MessageBubble(message: PracticeMessage, tutorGender: TutorGender) {
    val isLearner = message.speaker == "learner"
    val gradients = LocalUccharanGradients.current

    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (isLearner) Arrangement.End else Arrangement.Start,
        verticalAlignment = Alignment.Bottom,
    ) {
        if (!isLearner) {
            // Unanimated here — a constantly-swaying icon next to every single message
            // would be visual noise; the SceneBanner above is where the character lives and moves.
            TutorCharacter(gender = tutorGender, avatarSize = 28.dp, animated = false)
            Spacer(modifier = Modifier.width(6.dp))
        }
        Box(
            modifier = Modifier
                .widthIn(max = 280.dp)
                .clip(
                    RoundedCornerShape(
                        topStart = 16.dp,
                        topEnd = 16.dp,
                        bottomStart = if (isLearner) 16.dp else 4.dp,
                        bottomEnd = if (isLearner) 4.dp else 16.dp,
                    ),
                )
                .background(if (isLearner) gradients.primaryButton else androidx.compose.ui.graphics.SolidColor(MaterialTheme.colorScheme.surface))
                .padding(horizontal = 14.dp, vertical = 10.dp),
        ) {
            Text(
                message.text,
                style = MaterialTheme.typography.bodyLarge,
                color = if (isLearner) MaterialTheme.colorScheme.onPrimary else MaterialTheme.colorScheme.onSurface,
            )
        }
    }
}

@Composable
private fun CorrectionNote(correction: String?, nativeNote: String?, onPlayNative: () -> Unit) {
    Row(
        verticalAlignment = Alignment.Top,
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(14.dp))
            .background(MaterialTheme.colorScheme.tertiaryContainer)
            .padding(horizontal = 20.dp, vertical = 4.dp)
            .padding(14.dp),
    ) {
        Column(modifier = Modifier.weight(1f)) {
            correction?.let {
                Text(
                    "💡 $it",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onTertiaryContainer,
                )
            }
            nativeNote?.let {
                if (correction != null) Spacer(modifier = Modifier.height(6.dp))
                Text(
                    it,
                    style = MaterialTheme.typography.bodyMedium.copy(fontFamily = NotoSansTelugu),
                    color = MaterialTheme.colorScheme.onTertiaryContainer,
                )
            }
        }
        if (nativeNote != null) {
            Box(
                modifier = Modifier
                    .size(30.dp)
                    .clip(CircleShape)
                    .background(MaterialTheme.colorScheme.onTertiaryContainer.copy(alpha = 0.12f))
                    .clickable(onClick = onPlayNative),
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    Icons.AutoMirrored.Filled.VolumeUp,
                    contentDescription = "Listen in Telugu",
                    tint = MaterialTheme.colorScheme.onTertiaryContainer,
                    modifier = Modifier.size(14.dp),
                )
            }
        }
    }
}
