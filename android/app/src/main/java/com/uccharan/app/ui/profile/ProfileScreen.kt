package com.uccharan.app.ui.profile

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
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.uccharan.app.data.repository.QuizAttemptRecord
import com.uccharan.app.data.roadmap.ROADMAP_LEVELS
import com.uccharan.app.di.LocalAppContainer
import com.uccharan.app.di.uccharanViewModel
import com.uccharan.app.ui.onboarding.ADDRESS_TERM_SUGGESTIONS
import com.uccharan.app.ui.onboarding.LanguageChip
import com.uccharan.app.ui.onboarding.SUPPORTED_NATIVE_LANGUAGES
import com.uccharan.app.ui.onboarding.SuggestionChip
import com.uccharan.app.ui.onboarding.TutorGenderCard
import com.uccharan.app.ui.signin.uccharanTextFieldColors
import com.uccharan.app.ui.theme.LocalUccharanGradients
import com.uccharan.app.ui.tutor.TutorCharacter
import com.uccharan.app.ui.tutor.TutorGender
import com.uccharan.app.ui.tutor.tutorGenderFromStorage

@Composable
fun ProfileScreen(onBack: () -> Unit) {
    val container = LocalAppContainer.current
    val viewModel = uccharanViewModel {
        ProfileViewModel(container.authRepository, container.userProfileRepository, container.quizRepository, container.lessonRepository)
    }
    val uiState by viewModel.uiState.collectAsState()
    val gradients = LocalUccharanGradients.current

    Column(modifier = Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background)) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp).padding(top = 8.dp, bottom = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Box(
                modifier = Modifier.size(44.dp).clip(CircleShape).clickable(onClick = onBack),
                contentAlignment = Alignment.Center,
            ) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
            }
            Text("Profile & Settings", style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.onBackground)
        }

        when {
            uiState.isLoading -> Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { CircularProgressIndicator() }
            uiState.profile == null -> Text(
                uiState.errorMessage ?: "Couldn't load your profile",
                color = MaterialTheme.colorScheme.error,
                modifier = Modifier.padding(24.dp),
            )
            else -> {
                val profile = uiState.profile!!

                Column(
                    modifier = Modifier
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 24.dp)
                        .padding(top = 12.dp),
                ) {
                    Box(
                        modifier = Modifier
                            .size(72.dp)
                            .clip(CircleShape)
                            .background(gradients.primaryIcon),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(
                            profile.displayName.firstOrNull()?.uppercase() ?: profile.email.firstOrNull()?.uppercase() ?: "?",
                            style = MaterialTheme.typography.headlineSmall,
                            color = MaterialTheme.colorScheme.onPrimary,
                        )
                    }
                    Spacer(modifier = Modifier.height(14.dp))
                    Text(
                        profile.displayName.ifBlank { "Learner" },
                        style = MaterialTheme.typography.headlineSmall,
                        color = MaterialTheme.colorScheme.onBackground,
                    )
                    if (profile.email.isNotBlank()) {
                        Text(profile.email, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }

                    Spacer(modifier = Modifier.height(18.dp))
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        modifier = Modifier
                            .clip(RoundedCornerShape(14.dp))
                            .background(MaterialTheme.colorScheme.surface)
                            .padding(horizontal = 16.dp, vertical = 12.dp),
                    ) {
                        Icon(Icons.Filled.Star, contentDescription = null, tint = MaterialTheme.colorScheme.tertiary, modifier = Modifier.size(18.dp))
                        Text(
                            "${profile.xp} XP earned",
                            style = MaterialTheme.typography.bodyLarge,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onSurface,
                        )
                    }

                    Spacer(modifier = Modifier.height(28.dp))
                    Text("Your roadmap progress", style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Bold)
                    Spacer(modifier = Modifier.height(12.dp))
                    // Grouped by Level, not a flat week list — the program is three
                    // deliberately bounded 30-day stages (see RoadmapPlan.kt), and the
                    // progress view should read that way too: "Level 2: Consolidation",
                    // not an undifferentiated "Week 9".
                    uiState.weekProgress.groupBy { it.week.level }.toSortedMap().forEach { (levelNumber, weeksInLevel) ->
                        val level = ROADMAP_LEVELS.firstOrNull { it.level == levelNumber }
                        if (level != null) {
                            Text(
                                "Level $levelNumber: ${level.name} (${level.cefrTarget})",
                                style = MaterialTheme.typography.labelLarge,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.primary,
                                modifier = Modifier.padding(top = 8.dp, bottom = 6.dp),
                            )
                        }
                        weeksInLevel.forEach { weekProgress ->
                            WeekProgressRow(weekProgress)
                            Spacer(modifier = Modifier.height(8.dp))
                        }
                    }

                    if (uiState.weakSounds.isNotEmpty()) {
                        Spacer(modifier = Modifier.height(20.dp))
                        Text("Sounds to practice", style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Bold)
                        Text(
                            "Based on your recent lesson attempts",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        Spacer(modifier = Modifier.height(12.dp))
                        uiState.weakSounds.forEach { weakSound ->
                            WeakSoundRow(weakSound)
                            Spacer(modifier = Modifier.height(8.dp))
                        }
                    }

                    if (uiState.quizHistory.isNotEmpty()) {
                        Spacer(modifier = Modifier.height(20.dp))
                        Text("Quiz scores", style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Bold)
                        Spacer(modifier = Modifier.height(12.dp))
                        uiState.quizHistory.forEach { attempt ->
                            QuizHistoryRow(attempt)
                            Spacer(modifier = Modifier.height(8.dp))
                        }
                    }

                    Spacer(modifier = Modifier.height(28.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text("Tutor preferences", style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Bold)
                        if (!uiState.isEditingPreferences) {
                            Text(
                                "Edit",
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.primary,
                                modifier = Modifier.clickable(onClick = viewModel::startEditingPreferences),
                            )
                        }
                    }
                    Spacer(modifier = Modifier.height(12.dp))

                    if (uiState.isEditingPreferences) {
                        EditPreferences(uiState = uiState, viewModel = viewModel)
                    } else {
                        Text(
                            "Native language",
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        Text(
                            profile.nativeLanguage ?: "Not set",
                            style = MaterialTheme.typography.bodyLarge,
                            color = MaterialTheme.colorScheme.onBackground,
                        )
                        Spacer(modifier = Modifier.height(12.dp))
                        Text(
                            "Tutor calls you",
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        Text(
                            profile.preferredAddressTerm?.ifBlank { null } ?: "Not set",
                            style = MaterialTheme.typography.bodyLarge,
                            color = MaterialTheme.colorScheme.onBackground,
                        )
                        Spacer(modifier = Modifier.height(12.dp))
                        Text(
                            "Your tutor",
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                            TutorCharacter(gender = tutorGenderFromStorage(profile.tutorGender), avatarSize = 40.dp, animated = false)
                            Text(
                                tutorGenderFromStorage(profile.tutorGender).label,
                                style = MaterialTheme.typography.bodyLarge,
                                color = MaterialTheme.colorScheme.onBackground,
                            )
                        }
                    }

                    uiState.errorMessage?.let { message ->
                        Text(
                            message,
                            color = MaterialTheme.colorScheme.error,
                            style = MaterialTheme.typography.bodySmall,
                            modifier = Modifier.padding(top = 10.dp),
                        )
                    }

                    Spacer(modifier = Modifier.height(36.dp))
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(16.dp))
                            .background(MaterialTheme.colorScheme.errorContainer)
                            .clickable(onClick = viewModel::signOut)
                            .padding(vertical = 16.dp),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(
                            "Log out",
                            style = MaterialTheme.typography.labelLarge,
                            color = MaterialTheme.colorScheme.onErrorContainer,
                        )
                    }
                    Spacer(modifier = Modifier.height(24.dp))
                }
            }
        }
    }
}

@Composable
private fun WeekProgressRow(progress: WeekProgress) {
    val gradients = LocalUccharanGradients.current
    val firstDay = progress.week.days.first().day
    val lastDay = progress.week.days.last().day

    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(14.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(horizontal = 16.dp, vertical = 14.dp),
    ) {
        Box(
            modifier = Modifier
                .size(36.dp)
                .clip(CircleShape)
                .background(
                    when (progress.status) {
                        WeekStatus.COMPLETE -> gradients.primaryIcon
                        WeekStatus.IN_PROGRESS -> gradients.amberBadge
                        WeekStatus.NOT_AVAILABLE -> SolidColor(MaterialTheme.colorScheme.surfaceVariant)
                    },
                ),
            contentAlignment = Alignment.Center,
        ) {
            if (progress.status == WeekStatus.COMPLETE) {
                Icon(Icons.Filled.CheckCircle, contentDescription = "Complete", tint = MaterialTheme.colorScheme.onPrimary, modifier = Modifier.size(18.dp))
            } else {
                Text(
                    "${progress.week.weekNumber}",
                    style = MaterialTheme.typography.labelLarge,
                    color = if (progress.status == WeekStatus.IN_PROGRESS) gradients.onAmberBadge else MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
        Column(modifier = Modifier.weight(1f).padding(start = 14.dp)) {
            Text("Week ${progress.week.weekNumber} — Days $firstDay-$lastDay", style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold)
            Text(
                when (progress.status) {
                    WeekStatus.COMPLETE -> "Complete — all ${progress.daysWithContent} days done"
                    WeekStatus.IN_PROGRESS -> "${progress.daysComplete} of ${progress.daysWithContent} days done"
                    WeekStatus.NOT_AVAILABLE -> "Coming soon"
                },
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun WeakSoundRow(weakSound: WeakSound) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(14.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(horizontal = 16.dp, vertical = 13.dp),
    ) {
        Text("🎯", style = MaterialTheme.typography.titleMedium)
        Column(modifier = Modifier.weight(1f).padding(start = 12.dp)) {
            Text("\"${weakSound.sound}\" sound", style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold)
            Text(
                "${(weakSound.accuracy * 100).toInt()}% correct over ${weakSound.attempts} attempts",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun QuizHistoryRow(attempt: QuizAttemptRecord) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(14.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(horizontal = 16.dp, vertical = 13.dp),
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(attempt.title.ifBlank { attempt.quizId }, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold)
            Text(
                "${attempt.correctCount} / ${attempt.totalCount} correct" + if (attempt.xpEarned > 0) " · +${attempt.xpEarned} XP" else "",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        Box(
            modifier = Modifier
                .clip(RoundedCornerShape(8.dp))
                .background(if (attempt.passed) MaterialTheme.colorScheme.tertiaryContainer else MaterialTheme.colorScheme.errorContainer)
                .padding(horizontal = 10.dp, vertical = 5.dp),
        ) {
            Text(
                if (attempt.passed) "Passed" else "Retry",
                style = MaterialTheme.typography.labelSmall,
                color = if (attempt.passed) MaterialTheme.colorScheme.onTertiaryContainer else MaterialTheme.colorScheme.onErrorContainer,
            )
        }
    }
}

@Composable
private fun EditPreferences(uiState: ProfileUiState, viewModel: ProfileViewModel) {
    Text("Native language", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
    Spacer(modifier = Modifier.height(8.dp))
    LazyRow(horizontalArrangement = Arrangement.spacedBy(9.dp)) {
        items(SUPPORTED_NATIVE_LANGUAGES) { language ->
            LanguageChip(
                label = language,
                selected = uiState.draftLanguage == language,
                onClick = { viewModel.onDraftLanguageChange(if (uiState.draftLanguage == language) null else language) },
            )
        }
    }
    Spacer(modifier = Modifier.height(18.dp))

    Text("Tutor calls you", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
    Spacer(modifier = Modifier.height(8.dp))
    val suggestions = uiState.draftLanguage?.let { ADDRESS_TERM_SUGGESTIONS[it] }.orEmpty()
    if (suggestions.isNotEmpty()) {
        Row(horizontalArrangement = Arrangement.spacedBy(9.dp), modifier = Modifier.padding(bottom = 12.dp)) {
            suggestions.forEach { suggestion ->
                SuggestionChip(
                    label = suggestion,
                    selected = uiState.draftAddressTerm == suggestion,
                    onClick = { viewModel.onDraftAddressTermChange(suggestion) },
                )
            }
        }
    }
    OutlinedTextField(
        value = uiState.draftAddressTerm,
        onValueChange = viewModel::onDraftAddressTermChange,
        label = { Text("Your name or a nickname") },
        shape = RoundedCornerShape(14.dp),
        singleLine = true,
        modifier = Modifier.fillMaxWidth(),
        colors = uccharanTextFieldColors(),
        textStyle = MaterialTheme.typography.titleMedium,
    )

    Spacer(modifier = Modifier.height(18.dp))
    Text("Your tutor", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
    Spacer(modifier = Modifier.height(8.dp))
    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        TutorGenderCard(
            gender = TutorGender.FEMALE,
            selected = uiState.draftTutorGender == TutorGender.FEMALE,
            onClick = { viewModel.onDraftTutorGenderChange(TutorGender.FEMALE) },
            modifier = Modifier.weight(1f),
        )
        TutorGenderCard(
            gender = TutorGender.MALE,
            selected = uiState.draftTutorGender == TutorGender.MALE,
            onClick = { viewModel.onDraftTutorGenderChange(TutorGender.MALE) },
            modifier = Modifier.weight(1f),
        )
    }

    Spacer(modifier = Modifier.height(16.dp))
    val gradients = LocalUccharanGradients.current
    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        Box(
            modifier = Modifier
                .clip(RoundedCornerShape(12.dp))
                .clickable(enabled = !uiState.isSaving, onClick = viewModel::cancelEditingPreferences)
                .padding(vertical = 12.dp, horizontal = 6.dp),
        ) {
            Text("Cancel", style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        Box(
            modifier = Modifier
                .weight(1f)
                .shadow(elevation = 10.dp, shape = RoundedCornerShape(14.dp), ambientColor = MaterialTheme.colorScheme.primary, spotColor = MaterialTheme.colorScheme.primary)
                .clip(RoundedCornerShape(14.dp))
                .background(gradients.primaryButton)
                .clickable(enabled = !uiState.isSaving, onClick = viewModel::savePreferences)
                .padding(vertical = 13.dp),
            contentAlignment = Alignment.Center,
        ) {
            if (uiState.isSaving) {
                CircularProgressIndicator(modifier = Modifier.size(18.dp), color = MaterialTheme.colorScheme.onPrimary)
            } else {
                Text("Save changes", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.onPrimary)
            }
        }
    }
}
