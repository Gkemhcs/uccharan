package com.uccharan.app.ui.practice

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
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.automirrored.filled.Chat
import androidx.compose.material.icons.filled.Headphones
import androidx.compose.material3.Button
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.unit.dp
import com.uccharan.app.di.LocalAppContainer
import com.uccharan.app.di.uccharanViewModel
import com.uccharan.app.ui.theme.LocalUccharanGradients

/**
 * The Practice tab: a "Today's Practice" card tied to the learner's current
 * lesson topic (the default, structured path — see
 * [PracticeConversationViewModel]'s doc on why there's no open-ended "no
 * fixed topic" mode), plus a curated set of common real-world situations and
 * a free-text field for describing any other one. Every entry here, curated,
 * typed, or today's topic, becomes ONE concrete, bounded topic string handed
 * to [PracticeConversationScreen] — the backend already builds a realistic
 * roleplay from any topic text, so no backend change was needed to support
 * a learner-typed situation.
 */
private val CURATED_SITUATIONS = listOf(
    "Negotiating an auto-rickshaw or taxi fare",
    "Asking a stranger for directions",
    "Ordering food at a restaurant",
    "Checking into a hotel",
    "Returning or exchanging something at a shop",
    "Explaining symptoms to a doctor",
    "Small talk with a new neighbor",
    "A job interview",
    "Booking an appointment over the phone",
    "Handling a delayed flight or train",
)

@Composable
fun PracticeTabScreen(onSituationChosen: (String) -> Unit, onListeningPracticeClick: (String) -> Unit) {
    val container = LocalAppContainer.current
    val viewModel = uccharanViewModel { PracticeTabViewModel(container.authRepository, container.userProfileRepository) }
    val uiState by viewModel.uiState.collectAsState()
    var customSituation by rememberSaveable { mutableStateOf("") }

    Column(modifier = Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background)) {
        LazyColumn(
            modifier = Modifier.weight(1f),
            contentPadding = PaddingValues(horizontal = 24.dp, vertical = 16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            if (uiState.todayTopic != null) {
                item {
                    TodayPracticeCard(
                        themeLabel = uiState.todayThemeLabel.orEmpty(),
                        onClick = { uiState.todayTopic?.let(onSituationChosen) },
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                }
            }
            item {
                // Not gated on todayTopic like the speaking card above — listening
                // comprehension is useful practice even between lessons, so it
                // always falls back to a generic everyday topic rather than
                // disappearing when there's nothing new to speak about today.
                ListeningPracticeCard(
                    onClick = { onListeningPracticeClick(uiState.todayTopic ?: "Everyday conversation") },
                )
                Spacer(modifier = Modifier.height(8.dp))
            }
            item {
                Column {
                    Text(
                        "Describe your own situation",
                        style = MaterialTheme.typography.labelLarge,
                        color = MaterialTheme.colorScheme.onSurface,
                        modifier = Modifier.padding(bottom = 8.dp),
                    )
                    OutlinedTextField(
                        value = customSituation,
                        onValueChange = { customSituation = it },
                        placeholder = { Text("e.g. Talking to my child's teacher") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                    )
                    Spacer(modifier = Modifier.height(10.dp))
                    Button(
                        onClick = { onSituationChosen(customSituation.trim()) },
                        enabled = customSituation.isNotBlank(),
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text("Start this practice")
                    }
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        "Or choose a common situation:",
                        style = MaterialTheme.typography.labelLarge,
                        color = MaterialTheme.colorScheme.onSurface,
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                }
            }
            items(CURATED_SITUATIONS) { situation ->
                SituationCard(situation = situation, onClick = { onSituationChosen(situation) })
            }
            item { Spacer(modifier = Modifier.height(24.dp)) }
        }
    }
}

@Composable
private fun TodayPracticeCard(themeLabel: String, onClick: () -> Unit) {
    val gradients = LocalUccharanGradients.current

    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier
            .fillMaxWidth()
            .shadow(elevation = 12.dp, shape = RoundedCornerShape(18.dp), ambientColor = MaterialTheme.colorScheme.tertiary, spotColor = MaterialTheme.colorScheme.tertiary)
            .clip(RoundedCornerShape(18.dp))
            .background(gradients.amberBadge)
            .clickable(onClick = onClick)
            .padding(16.dp),
    ) {
        Box(
            modifier = Modifier
                .size(42.dp)
                .clip(CircleShape)
                .background(gradients.onAmberBadge.copy(alpha = 0.18f)),
            contentAlignment = Alignment.Center,
        ) {
            Icon(
                Icons.AutoMirrored.Filled.Chat,
                contentDescription = null,
                tint = gradients.onAmberBadge,
                modifier = Modifier.size(20.dp),
            )
        }
        Column(modifier = Modifier.weight(1f).padding(start = 14.dp)) {
            Text("Today's Practice", style = MaterialTheme.typography.titleMedium, color = gradients.onAmberBadge)
            Text(
                themeLabel.ifBlank { "Have a real spoken conversation" },
                style = MaterialTheme.typography.bodySmall,
                color = gradients.onAmberBadge,
            )
        }
        Icon(
            Icons.AutoMirrored.Filled.ArrowForward,
            contentDescription = null,
            tint = gradients.onAmberBadge,
            modifier = Modifier.size(16.dp),
        )
    }
}

@Composable
private fun ListeningPracticeCard(onClick: () -> Unit) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier
            .fillMaxWidth()
            .shadow(elevation = 6.dp, shape = RoundedCornerShape(18.dp), ambientColor = MaterialTheme.colorScheme.primary, spotColor = MaterialTheme.colorScheme.primary)
            .clip(RoundedCornerShape(18.dp))
            .background(MaterialTheme.colorScheme.surface)
            .clickable(onClick = onClick)
            .padding(16.dp),
    ) {
        Box(
            modifier = Modifier
                .size(42.dp)
                .clip(CircleShape)
                .background(MaterialTheme.colorScheme.primaryContainer),
            contentAlignment = Alignment.Center,
        ) {
            Icon(
                Icons.Filled.Headphones,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onPrimaryContainer,
                modifier = Modifier.size(20.dp),
            )
        }
        Column(modifier = Modifier.weight(1f).padding(start = 14.dp)) {
            Text("Listening Practice", style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.onSurface)
            Text(
                "Train your ear — listen, then answer",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        Icon(
            Icons.AutoMirrored.Filled.ArrowForward,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.size(16.dp),
        )
    }
}

@Composable
private fun SituationCard(situation: String, onClick: () -> Unit) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier
            .fillMaxWidth()
            .shadow(elevation = 6.dp, shape = RoundedCornerShape(16.dp), ambientColor = MaterialTheme.colorScheme.primary, spotColor = MaterialTheme.colorScheme.primary)
            .clip(RoundedCornerShape(16.dp))
            .background(MaterialTheme.colorScheme.surface)
            .clickable(onClick = onClick)
            .padding(16.dp),
    ) {
        Icon(
            Icons.AutoMirrored.Filled.Chat,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.primary,
            modifier = Modifier.size(20.dp),
        )
        Text(
            situation,
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onBackground,
            modifier = Modifier.weight(1f).padding(start = 14.dp),
        )
        Icon(
            Icons.AutoMirrored.Filled.ArrowForward,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.size(16.dp),
        )
    }
}
