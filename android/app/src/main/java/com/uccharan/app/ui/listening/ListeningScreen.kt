package com.uccharan.app.ui.listening

import android.speech.tts.TextToSpeech
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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Headphones
import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.filled.VolumeUp
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.uccharan.app.di.LocalAppContainer
import com.uccharan.app.di.uccharanViewModel
import com.uccharan.app.ui.theme.LocalUccharanGradients
import java.util.Locale

/**
 * A short listening-comprehension session — see [ListeningViewModel]'s class
 * doc for why this checks comprehension via multiple-choice rather than
 * reusing the speak-and-correct mechanism the rest of the app uses.
 *
 * The passage text is deliberately never composed onto the screen until
 * after the learner answers — [ListeningExercise.passage] only ever reaches
 * text-to-speech, never a `Text` composable, until [ListeningUiState.selectedOptionIndex]
 * is non-null. Reading along while it plays would defeat the exercise.
 */
@Composable
fun ListeningScreen(topic: String, onBack: () -> Unit) {
    val context = LocalContext.current
    val container = LocalAppContainer.current
    val viewModel = uccharanViewModel {
        ListeningViewModel(topic, container.authRepository, container.userProfileRepository, container.listeningApi)
    }
    val uiState by viewModel.uiState.collectAsState()
    val gradients = LocalUccharanGradients.current

    var textToSpeech by remember { mutableStateOf<TextToSpeech?>(null) }
    DisposableEffect(Unit) {
        val tts = TextToSpeech(context) { }
        textToSpeech = tts
        onDispose { tts.shutdown() }
    }
    fun playPassage() {
        val exercise = uiState.exercise ?: return
        textToSpeech?.language = Locale.US
        textToSpeech?.speak(exercise.passage, TextToSpeech.QUEUE_FLUSH, null, null)
        viewModel.onPlayed()
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
            Text("Listening Practice", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }

        when {
            uiState.isSessionComplete -> ListeningSessionResult(uiState = uiState, onDone = onBack)
            uiState.errorMessage != null && uiState.exercise == null -> Text(
                uiState.errorMessage ?: "",
                color = MaterialTheme.colorScheme.error,
                modifier = Modifier.padding(24.dp),
            )
            uiState.isLoadingRound -> Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { CircularProgressIndicator() }
            else -> uiState.exercise?.let { exercise ->
                ListeningRoundBody(uiState = uiState, exercise = exercise, viewModel = viewModel, gradients = gradients, onPlay = ::playPassage)
            }
        }
    }
}

@Composable
private fun ListeningRoundBody(
    uiState: ListeningUiState,
    exercise: com.uccharan.app.data.remote.ListeningExercise,
    viewModel: ListeningViewModel,
    gradients: com.uccharan.app.ui.theme.UccharanGradients,
    onPlay: () -> Unit,
) {
    Column(modifier = Modifier.padding(horizontal = 24.dp).padding(top = 12.dp)) {
        LinearProgressIndicator(
            progress = { (uiState.roundsCompleted + 1).toFloat() / LISTENING_SESSION_ROUNDS },
            modifier = Modifier.fillMaxWidth().height(6.dp).clip(RoundedCornerShape(3.dp)),
            trackColor = MaterialTheme.colorScheme.outline,
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            "Round ${uiState.roundsCompleted + 1} of $LISTENING_SESSION_ROUNDS",
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Spacer(modifier = Modifier.height(20.dp))

        Box(
            modifier = Modifier
                .fillMaxWidth()
                .shadow(elevation = 14.dp, shape = RoundedCornerShape(20.dp), ambientColor = MaterialTheme.colorScheme.primary, spotColor = MaterialTheme.colorScheme.primary)
                .clip(RoundedCornerShape(20.dp))
                .background(gradients.primaryButton)
                .clickable(onClick = onPlay)
                .padding(vertical = 26.dp),
            contentAlignment = Alignment.Center,
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Icon(
                    if (uiState.hasPlayedOnce) Icons.Filled.VolumeUp else Icons.Filled.Headphones,
                    contentDescription = "Play",
                    tint = MaterialTheme.colorScheme.onPrimary,
                    modifier = Modifier.size(36.dp),
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    if (uiState.hasPlayedOnce) "Tap to hear it again" else "Tap to listen",
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.onPrimary,
                )
            }
        }
        Spacer(modifier = Modifier.height(24.dp))

        Text(exercise.question, style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.onBackground)
        Spacer(modifier = Modifier.height(4.dp))
        if (!uiState.hasPlayedOnce) {
            Text(
                "Listen first, then choose your answer",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        Spacer(modifier = Modifier.height(16.dp))

        exercise.options.forEachIndexed { index, option ->
            ListeningOptionRow(
                text = option,
                state = when {
                    uiState.selectedOptionIndex == null -> OptionRowState.IDLE
                    index == exercise.correctOptionIndex -> OptionRowState.CORRECT
                    index == uiState.selectedOptionIndex -> OptionRowState.WRONG_SELECTED
                    else -> OptionRowState.DIMMED
                },
                enabled = uiState.hasPlayedOnce,
                onClick = { viewModel.selectOption(index) },
            )
            Spacer(modifier = Modifier.height(10.dp))
        }

        if (uiState.selectedOptionIndex != null) {
            Spacer(modifier = Modifier.height(8.dp))
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(16.dp))
                    .background(MaterialTheme.colorScheme.surfaceVariant)
                    .padding(16.dp),
            ) {
                Text("WHAT WAS SAID", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                Spacer(modifier = Modifier.height(4.dp))
                Text("\"${exercise.passage}\"", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurface)
                if (exercise.explanation.isNotBlank()) {
                    Spacer(modifier = Modifier.height(10.dp))
                    Text(exercise.explanation, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
        }

        Spacer(modifier = Modifier.weight(1f))

        if (uiState.selectedOptionIndex != null) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 32.dp)
                    .shadow(elevation = 16.dp, shape = RoundedCornerShape(16.dp), ambientColor = MaterialTheme.colorScheme.primary, spotColor = MaterialTheme.colorScheme.primary)
                    .clip(RoundedCornerShape(16.dp))
                    .background(gradients.primaryButton)
                    .clickable(onClick = viewModel::nextRound)
                    .padding(vertical = 17.dp),
                contentAlignment = Alignment.Center,
            ) {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(
                        if (uiState.isLastRound) "Finish" else "Next round",
                        style = MaterialTheme.typography.labelLarge,
                        color = MaterialTheme.colorScheme.onPrimary,
                    )
                    Icon(Icons.AutoMirrored.Filled.ArrowForward, contentDescription = null, tint = MaterialTheme.colorScheme.onPrimary, modifier = Modifier.size(16.dp))
                }
            }
        } else {
            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}

private enum class OptionRowState { IDLE, CORRECT, WRONG_SELECTED, DIMMED }

@Composable
private fun ListeningOptionRow(text: String, state: OptionRowState, enabled: Boolean, onClick: () -> Unit) {
    val containerColor = when (state) {
        OptionRowState.IDLE -> MaterialTheme.colorScheme.surface
        OptionRowState.CORRECT -> MaterialTheme.colorScheme.tertiaryContainer
        OptionRowState.WRONG_SELECTED -> MaterialTheme.colorScheme.errorContainer
        OptionRowState.DIMMED -> MaterialTheme.colorScheme.surface
    }
    val contentColor = when (state) {
        OptionRowState.IDLE -> if (enabled) MaterialTheme.colorScheme.onSurface else MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f)
        OptionRowState.CORRECT -> MaterialTheme.colorScheme.onTertiaryContainer
        OptionRowState.WRONG_SELECTED -> MaterialTheme.colorScheme.onErrorContainer
        OptionRowState.DIMMED -> MaterialTheme.colorScheme.onSurfaceVariant
    }

    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(14.dp))
            .background(containerColor)
            .clickable(enabled = enabled && state == OptionRowState.IDLE, onClick = onClick)
            .padding(horizontal = 16.dp, vertical = 15.dp),
    ) {
        Text(text, style = MaterialTheme.typography.bodyLarge, color = contentColor, modifier = Modifier.weight(1f))
        if (state == OptionRowState.CORRECT) {
            Icon(Icons.Filled.Check, contentDescription = "Correct", tint = contentColor, modifier = Modifier.size(18.dp))
        } else if (state == OptionRowState.WRONG_SELECTED) {
            Icon(Icons.Filled.Close, contentDescription = "Incorrect", tint = contentColor, modifier = Modifier.size(18.dp))
        }
    }
}

@Composable
private fun ListeningSessionResult(uiState: ListeningUiState, onDone: () -> Unit) {
    val gradients = LocalUccharanGradients.current

    Column(
        modifier = Modifier.fillMaxSize().padding(horizontal = 24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Spacer(modifier = Modifier.weight(1f))
        Box(
            modifier = Modifier.size(72.dp).clip(CircleShape).background(gradients.primaryIcon),
            contentAlignment = Alignment.Center,
        ) {
            Icon(Icons.Filled.Headphones, contentDescription = null, tint = MaterialTheme.colorScheme.onPrimary, modifier = Modifier.size(32.dp))
        }
        Spacer(modifier = Modifier.height(18.dp))
        Text("Session complete!", style = MaterialTheme.typography.headlineSmall, color = MaterialTheme.colorScheme.onBackground)
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            "You got ${uiState.correctCount} of $LISTENING_SESSION_ROUNDS right.",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        if (uiState.xpEarned > 0) {
            Spacer(modifier = Modifier.height(14.dp))
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                modifier = Modifier
                    .clip(RoundedCornerShape(14.dp))
                    .background(gradients.amberBadge)
                    .padding(horizontal = 16.dp, vertical = 10.dp),
            ) {
                Icon(Icons.Filled.Star, contentDescription = null, tint = gradients.onAmberBadge, modifier = Modifier.size(18.dp))
                Text("+${uiState.xpEarned} XP", style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Bold, color = gradients.onAmberBadge)
            }
        }
        Spacer(modifier = Modifier.weight(1f))
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .shadow(elevation = 16.dp, shape = RoundedCornerShape(16.dp), ambientColor = MaterialTheme.colorScheme.primary, spotColor = MaterialTheme.colorScheme.primary)
                .clip(RoundedCornerShape(16.dp))
                .background(gradients.primaryButton)
                .clickable(onClick = onDone)
                .padding(vertical = 17.dp),
            contentAlignment = Alignment.Center,
        ) {
            Text("Done", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.onPrimary)
        }
        Spacer(modifier = Modifier.height(40.dp))
    }
}
