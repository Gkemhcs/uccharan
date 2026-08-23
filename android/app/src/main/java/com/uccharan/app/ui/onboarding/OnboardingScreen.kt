package com.uccharan.app.ui.onboarding

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.SuggestionChip
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.uccharan.app.di.LocalAppContainer
import com.uccharan.app.di.uccharanViewModel

@Composable
fun OnboardingScreen(onOnboardingComplete: () -> Unit) {
    val container = LocalAppContainer.current
    val viewModel = uccharanViewModel {
        OnboardingViewModel(container.authRepository, container.userProfileRepository, onOnboardingComplete)
    }
    val uiState by viewModel.uiState.collectAsState()

    Column(modifier = Modifier.fillMaxSize().padding(24.dp)) {
        Text("Let's personalize your tutor", style = MaterialTheme.typography.headlineSmall)
        Text(
            "This is optional, but it helps your tutor feel more like a real person to you.",
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.padding(top = 4.dp, bottom = 24.dp),
        )

        Text("What's your native language?", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        LazyRow {
            items(SUPPORTED_NATIVE_LANGUAGES) { language ->
                FilterChip(
                    selected = uiState.selectedLanguage == language,
                    onClick = {
                        viewModel.onLanguageSelected(if (uiState.selectedLanguage == language) null else language)
                    },
                    label = { Text(language) },
                    modifier = Modifier.padding(end = 8.dp),
                )
            }
        }
        Text(
            "We'll explain corrections in this language too, alongside English.",
            style = MaterialTheme.typography.bodySmall,
            modifier = Modifier.padding(top = 8.dp),
        )

        Spacer(modifier = Modifier.height(28.dp))

        Text("What should your tutor call you?", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))

        val suggestions = uiState.selectedLanguage?.let { ADDRESS_TERM_SUGGESTIONS[it] }.orEmpty()
        if (suggestions.isNotEmpty()) {
            Row(modifier = Modifier.padding(bottom = 8.dp)) {
                suggestions.forEach { suggestion ->
                    SuggestionChip(
                        onClick = { viewModel.onAddressTermChange(suggestion) },
                        label = { Text(suggestion) },
                        modifier = Modifier.padding(end = 8.dp),
                    )
                }
            }
        }

        OutlinedTextField(
            value = uiState.preferredAddressTerm,
            onValueChange = viewModel::onAddressTermChange,
            label = { Text("Your name or a nickname") },
            modifier = Modifier.fillMaxWidth(),
        )

        uiState.errorMessage?.let { message ->
            Text(
                text = message,
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier.padding(top = 8.dp),
            )
        }

        Spacer(modifier = Modifier.weight(1f))

        if (uiState.isSaving) {
            CircularProgressIndicator(modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp))
        } else {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                TextButton(onClick = viewModel::onSkip) { Text("Skip for now") }
                Button(onClick = viewModel::onContinue) { Text("Continue") }
            }
        }
    }
}
