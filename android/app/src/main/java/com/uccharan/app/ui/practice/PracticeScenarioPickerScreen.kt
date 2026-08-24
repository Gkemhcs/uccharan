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
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.automirrored.filled.Chat
import androidx.compose.material3.Button
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.unit.dp

/**
 * A curated set of common real-world situations to rehearse, plus a free-text
 * field to describe any other situation — reached via a clearly secondary
 * "Or practice a different situation" link on Home, never the default tap
 * target. The default flow (tapping the Practice card) stays tied to today's
 * lesson topic, unchanged; this is a deliberate, bounded ADDITION for when a
 * learner wants to rehearse something specific right now (e.g. "I have to
 * negotiate an auto fare tomorrow") — not a return to an open "chat about
 * anything" mode. Every entry here, curated or typed, still becomes ONE
 * concrete, bounded topic string handed to [PracticeConversationScreen] —
 * the backend already builds a realistic roleplay from any topic text (see
 * `GeminiService.continue_practice_conversation`), so no backend change was
 * needed to support a learner-typed situation.
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
fun PracticeScenarioPickerScreen(onBack: () -> Unit, onSituationChosen: (String) -> Unit) {
    var customSituation by rememberSaveable { mutableStateOf("") }

    Column(modifier = Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background)) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp).padding(top = 8.dp, bottom = 4.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Box(
                modifier = Modifier.size(44.dp).clip(CircleShape).clickable(onClick = onBack),
                contentAlignment = Alignment.Center,
            ) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
            }
            Text("Practice a Situation", style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.onBackground)
        }

        Text(
            "Pick a common real-world situation, or describe your own — your tutor will roleplay it with you.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.padding(horizontal = 24.dp).padding(top = 4.dp, bottom = 18.dp),
        )

        LazyColumn(
            modifier = Modifier.weight(1f),
            contentPadding = PaddingValues(horizontal = 24.dp, vertical = 0.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
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
                        "Or choose one:",
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
