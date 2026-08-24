package com.uccharan.app.ui.roadmap

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
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.outlined.Circle
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.uccharan.app.data.roadmap.ROADMAP_LEVELS
import com.uccharan.app.data.roadmap.RoadmapDay
import com.uccharan.app.data.roadmap.RoadmapLevel
import com.uccharan.app.di.LocalAppContainer
import com.uccharan.app.di.uccharanViewModel
import com.uccharan.app.ui.theme.LocalUccharanGradients

/**
 * The full 90-day syllabus, up front — every Level, every week, every day's
 * theme, all visible at once. Addresses "nothing should be open-ended, he
 * needs to see what's there and be able to skip what he already knows"
 * (CURRICULUM.md §8): this is the structured alternative to an open-ended
 * "just explore" mode. Tapping any day the learner isn't currently on offers
 * a deliberate jump — confirmed, never accidental.
 */
@Composable
fun RoadmapOverviewScreen(onBack: () -> Unit) {
    val container = LocalAppContainer.current
    val viewModel = uccharanViewModel {
        RoadmapOverviewViewModel(container.authRepository, container.userProfileRepository, container.quizRepository)
    }
    val uiState by viewModel.uiState.collectAsState()

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
            Column {
                Text("Your 90-Day Roadmap", style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.onBackground)
                Text(
                    "Tap any day to jump there",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }

        when {
            uiState.isLoading -> Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
            uiState.errorMessage != null && uiState.currentTrack == null -> Text(
                uiState.errorMessage ?: "",
                color = MaterialTheme.colorScheme.error,
                modifier = Modifier.padding(horizontal = 24.dp).padding(top = 12.dp),
            )
            else -> LazyColumn(
                contentPadding = PaddingValues(horizontal = 20.dp, vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                ROADMAP_LEVELS.forEach { level ->
                    item(key = "level-${level.level}") { LevelHeader(level) }
                    items(level.days, key = { it.day }) { day ->
                        DayRow(day = day, status = uiState.statusFor(day), onClick = { viewModel.requestJump(day) })
                    }
                }
                item { Spacer(modifier = Modifier.height(24.dp)) }
            }
        }
    }

    uiState.pendingJumpDay?.let { day ->
        AlertDialog(
            onDismissRequest = viewModel::dismissJump,
            title = { Text("Jump to Day ${day.day}?") },
            text = {
                Text(
                    "This moves you straight to \"${day.theme}\". Days in between won't be marked as done — " +
                        "you can always come back and do them later from this same screen.",
                )
            },
            confirmButton = {
                TextButton(onClick = viewModel::confirmJump, enabled = !uiState.isJumping) {
                    Text(if (uiState.isJumping) "Jumping…" else "Jump there")
                }
            },
            dismissButton = {
                TextButton(onClick = viewModel::dismissJump, enabled = !uiState.isJumping) { Text("Cancel") }
            },
        )
    }
}

@Composable
private fun LevelHeader(level: RoadmapLevel) {
    val gradients = LocalUccharanGradients.current
    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier
            .fillMaxWidth()
            .padding(top = 12.dp, bottom = 2.dp)
            .clip(RoundedCornerShape(14.dp))
            .background(gradients.primaryIcon)
            .padding(horizontal = 16.dp, vertical = 12.dp),
    ) {
        Column {
            Text(
                "LEVEL ${level.level} · ${level.cefrTarget}",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.85f),
            )
            Text(level.name, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onPrimary)
        }
    }
}

@Composable
private fun DayRow(day: RoadmapDay, status: DayStatus, onClick: () -> Unit) {
    val gradients = LocalUccharanGradients.current
    val isTappable = status == DayStatus.AVAILABLE || status == DayStatus.COMPLETED

    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(14.dp))
            .background(if (status == DayStatus.CURRENT) MaterialTheme.colorScheme.surfaceVariant else MaterialTheme.colorScheme.surface)
            .let { if (isTappable) it.clickable(onClick = onClick) else it }
            .padding(horizontal = 14.dp, vertical = 12.dp),
    ) {
        Box(
            modifier = Modifier
                .size(34.dp)
                .clip(CircleShape)
                .background(
                    when (status) {
                        DayStatus.COMPLETED -> gradients.primaryIcon
                        DayStatus.CURRENT -> gradients.amberBadge
                        DayStatus.AVAILABLE -> SolidColor(MaterialTheme.colorScheme.surfaceVariant)
                        DayStatus.NOT_READY -> SolidColor(MaterialTheme.colorScheme.surfaceVariant)
                    },
                ),
            contentAlignment = Alignment.Center,
        ) {
            when (status) {
                DayStatus.COMPLETED -> Icon(Icons.Filled.CheckCircle, contentDescription = "Completed", tint = MaterialTheme.colorScheme.onPrimary, modifier = Modifier.size(16.dp))
                DayStatus.CURRENT -> Icon(Icons.Filled.PlayArrow, contentDescription = "Current day", tint = gradients.onAmberBadge, modifier = Modifier.size(16.dp))
                else -> Icon(Icons.Outlined.Circle, contentDescription = null, tint = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.size(10.dp))
            }
        }
        Column(modifier = Modifier.weight(1f).padding(start = 12.dp)) {
            Text(
                "Day ${day.day}",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                if (status == DayStatus.NOT_READY) "Coming soon" else day.theme,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = if (status == DayStatus.CURRENT) FontWeight.Bold else FontWeight.Normal,
                color = if (status == DayStatus.NOT_READY) MaterialTheme.colorScheme.onSurfaceVariant else MaterialTheme.colorScheme.onSurface,
            )
        }
        if (status == DayStatus.CURRENT) {
            Text("You are here", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold)
        }
    }
}
