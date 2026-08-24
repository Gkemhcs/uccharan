package com.uccharan.app.ui.onboarding

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
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
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.filled.Check
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.uccharan.app.di.LocalAppContainer
import com.uccharan.app.di.uccharanViewModel
import com.uccharan.app.ui.signin.uccharanTextFieldColors
import com.uccharan.app.ui.theme.LocalUccharanGradients
import com.uccharan.app.ui.tutor.TutorCharacter
import com.uccharan.app.ui.tutor.TutorGender

@Composable
fun OnboardingScreen(onOnboardingComplete: () -> Unit) {
    val container = LocalAppContainer.current
    val viewModel = uccharanViewModel {
        OnboardingViewModel(container.authRepository, container.userProfileRepository, onOnboardingComplete)
    }
    val uiState by viewModel.uiState.collectAsState()
    val gradients = LocalUccharanGradients.current

    Column(modifier = Modifier.fillMaxSize()) {
        Column(modifier = Modifier.padding(horizontal = 28.dp).padding(top = 8.dp)) {
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp), modifier = Modifier.fillMaxWidth().padding(bottom = 26.dp)) {
                Box(
                    modifier = Modifier
                        .weight(1f)
                        .height(4.dp)
                        .clip(RoundedCornerShape(2.dp))
                        .background(gradients.primaryButton),
                )
                Box(
                    modifier = Modifier
                        .weight(1f)
                        .height(4.dp)
                        .clip(RoundedCornerShape(2.dp))
                        .background(MaterialTheme.colorScheme.outline),
                )
            }

            Text(
                text = "Let's personalize\nyour tutor",
                style = MaterialTheme.typography.headlineMedium,
                color = MaterialTheme.colorScheme.onBackground,
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "This is optional, but it helps your tutor feel more like a real person to you.",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Spacer(modifier = Modifier.height(26.dp))
        }

        Column(
            modifier = Modifier
                .weight(1f)
                .padding(horizontal = 28.dp)
                .verticalScroll(rememberScrollState()),
        ) {
            Text("What's your native language?", style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.height(12.dp))

            LazyRow(horizontalArrangement = Arrangement.spacedBy(9.dp)) {
                items(SUPPORTED_NATIVE_LANGUAGES) { language ->
                    LanguageChip(
                        label = language,
                        selected = uiState.selectedLanguage == language,
                        onClick = { viewModel.onLanguageSelected(if (uiState.selectedLanguage == language) null else language) },
                    )
                }
            }
            Spacer(modifier = Modifier.height(10.dp))
            Text(
                text = "We'll explain corrections in this language too, alongside English.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Spacer(modifier = Modifier.height(28.dp))

            Text("What should your tutor call you?", style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.height(12.dp))

            val suggestions = uiState.selectedLanguage?.let { ADDRESS_TERM_SUGGESTIONS[it] }.orEmpty()
            if (suggestions.isNotEmpty()) {
                Row(horizontalArrangement = Arrangement.spacedBy(9.dp), modifier = Modifier.padding(bottom = 14.dp)) {
                    suggestions.forEach { suggestion ->
                        SuggestionChip(
                            label = suggestion,
                            selected = uiState.preferredAddressTerm == suggestion,
                            onClick = { viewModel.onAddressTermChange(suggestion) },
                        )
                    }
                }
            }

            OutlinedTextField(
                value = uiState.preferredAddressTerm,
                onValueChange = viewModel::onAddressTermChange,
                label = { Text("Your name or a nickname") },
                shape = RoundedCornerShape(14.dp),
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
                colors = uccharanTextFieldColors(),
                textStyle = MaterialTheme.typography.titleMedium,
            )

            Spacer(modifier = Modifier.height(28.dp))
            Text("Choose your tutor", style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = "The same tutor will greet you everywhere in the app — you can change this later in Profile.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Spacer(modifier = Modifier.height(12.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                TutorGenderCard(
                    gender = TutorGender.FEMALE,
                    selected = uiState.tutorGender == TutorGender.FEMALE,
                    onClick = { viewModel.onTutorGenderSelected(TutorGender.FEMALE) },
                    modifier = Modifier.weight(1f),
                )
                TutorGenderCard(
                    gender = TutorGender.MALE,
                    selected = uiState.tutorGender == TutorGender.MALE,
                    onClick = { viewModel.onTutorGenderSelected(TutorGender.MALE) },
                    modifier = Modifier.weight(1f),
                )
            }

            uiState.errorMessage?.let { message ->
                Text(
                    text = message,
                    color = MaterialTheme.colorScheme.error,
                    style = MaterialTheme.typography.bodySmall,
                    modifier = Modifier.padding(top = 8.dp),
                )
            }
        }

        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 28.dp).padding(top = 16.dp, bottom = 40.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            if (uiState.isSaving) {
                CircularProgressIndicator(modifier = Modifier.fillMaxWidth())
            } else {
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(10.dp))
                        .clickable(onClick = viewModel::onSkip)
                        .padding(vertical = 14.dp, horizontal = 6.dp),
                ) {
                    Text("Skip for now", style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                }
                Box(
                    modifier = Modifier
                        .shadow(elevation = 14.dp, shape = RoundedCornerShape(16.dp), ambientColor = MaterialTheme.colorScheme.primary, spotColor = MaterialTheme.colorScheme.primary)
                        .clip(RoundedCornerShape(16.dp))
                        .background(gradients.primaryButton)
                        .clickable(onClick = viewModel::onContinue)
                        .padding(vertical = 15.dp, horizontal = 26.dp),
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text("Continue", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.onPrimary)
                        Icon(Icons.AutoMirrored.Filled.ArrowForward, contentDescription = null, tint = MaterialTheme.colorScheme.onPrimary, modifier = Modifier.size(16.dp))
                    }
                }
            }
        }
    }
}

@Composable
internal fun LanguageChip(label: String, selected: Boolean, onClick: () -> Unit) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(6.dp),
        modifier = Modifier
            .clip(RoundedCornerShape(12.dp))
            .background(if (selected) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surface)
            .clickable(onClick = onClick)
            .padding(horizontal = 18.dp, vertical = 13.dp),
    ) {
        if (selected) {
            Icon(Icons.Filled.Check, contentDescription = null, tint = MaterialTheme.colorScheme.onPrimaryContainer, modifier = Modifier.size(15.dp))
        }
        Text(
            label,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Bold,
            color = if (selected) MaterialTheme.colorScheme.onPrimaryContainer else MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

/** Reused from Profile's "Edit preferences" too, so choosing a tutor looks and behaves identically wherever it's offered. */
@Composable
internal fun TutorGenderCard(gender: TutorGender, selected: Boolean, onClick: () -> Unit, modifier: Modifier = Modifier) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = modifier
            .clip(RoundedCornerShape(16.dp))
            .background(if (selected) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surface)
            .clickable(onClick = onClick)
            .padding(vertical = 14.dp),
    ) {
        TutorCharacter(gender = gender, avatarSize = 64.dp, animated = selected)
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            gender.label,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Bold,
            color = if (selected) MaterialTheme.colorScheme.onPrimaryContainer else MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
internal fun SuggestionChip(label: String, selected: Boolean, onClick: () -> Unit) {
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(12.dp))
            .background(if (selected) MaterialTheme.colorScheme.tertiaryContainer else MaterialTheme.colorScheme.surface)
            .clickable(onClick = onClick)
            .padding(horizontal = 20.dp, vertical = 12.dp),
    ) {
        Text(
            label,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Bold,
            color = if (selected) MaterialTheme.colorScheme.tertiary else MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}
