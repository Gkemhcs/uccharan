package com.uccharan.app.ui.onboarding

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.uccharan.app.data.repository.AuthRepository
import com.uccharan.app.data.repository.UserProfileRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

/** language name -> suggested address-term options (Telugu's Nanna/Amma pattern; see CURRICULUM.md §6.5) */
val ADDRESS_TERM_SUGGESTIONS: Map<String, List<String>> = mapOf(
    "Telugu" to listOf("Nanna", "Amma"),
)

val SUPPORTED_NATIVE_LANGUAGES = listOf("Telugu", "Hindi", "Tamil", "Kannada", "Marathi", "Bengali")

data class OnboardingUiState(
    val selectedLanguage: String? = null,
    val preferredAddressTerm: String = "",
    val isSaving: Boolean = false,
    val errorMessage: String? = null,
)

class OnboardingViewModel(
    private val authRepository: AuthRepository,
    private val userProfileRepository: UserProfileRepository,
    private val onComplete: () -> Unit,
) : ViewModel() {

    private val _uiState = MutableStateFlow(OnboardingUiState())
    val uiState: StateFlow<OnboardingUiState> = _uiState.asStateFlow()

    fun onLanguageSelected(language: String?) = _uiState.update { it.copy(selectedLanguage = language) }

    fun onAddressTermChange(term: String) = _uiState.update { it.copy(preferredAddressTerm = term) }

    fun onSkip() = save(nativeLanguage = null, addressTerm = null)

    fun onContinue() {
        val state = _uiState.value
        save(
            nativeLanguage = state.selectedLanguage,
            addressTerm = state.preferredAddressTerm.ifBlank { null },
        )
    }

    private fun save(nativeLanguage: String?, addressTerm: String?) {
        val uid = authRepository.currentUser?.uid ?: return
        _uiState.update { it.copy(isSaving = true, errorMessage = null) }
        viewModelScope.launch {
            userProfileRepository.completeOnboarding(uid, nativeLanguage, addressTerm)
                .onSuccess { onComplete() }
                .onFailure { error ->
                    _uiState.update { it.copy(isSaving = false, errorMessage = error.message ?: "Couldn't save, try again") }
                }
        }
    }
}
