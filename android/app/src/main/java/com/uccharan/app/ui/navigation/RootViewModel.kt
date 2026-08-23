package com.uccharan.app.ui.navigation

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.uccharan.app.data.repository.AuthRepository
import com.uccharan.app.data.repository.UserProfileRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

sealed interface AppStartState {
    data object Loading : AppStartState
    data object NeedsSignIn : AppStartState
    data object NeedsOnboarding : AppStartState
    data object Ready : AppStartState
}

/**
 * Decides which screen the app should open on: watches Firebase auth state,
 * and for a signed-in user, checks whether they've completed onboarding.
 */
class RootViewModel(
    private val authRepository: AuthRepository,
    private val userProfileRepository: UserProfileRepository,
) : ViewModel() {

    private val _startState = MutableStateFlow<AppStartState>(AppStartState.Loading)
    val startState: StateFlow<AppStartState> = _startState.asStateFlow()

    init {
        viewModelScope.launch {
            authRepository.authStateFlow.collect { user ->
                if (user == null) {
                    _startState.value = AppStartState.NeedsSignIn
                    return@collect
                }

                userProfileRepository.ensureProfileExists(
                    uid = user.uid,
                    displayName = user.displayName.orEmpty(),
                    email = user.email.orEmpty(),
                )

                val profile = userProfileRepository.getProfile(user.uid).getOrNull()
                _startState.value = if (profile?.onboardingComplete == true) {
                    AppStartState.Ready
                } else {
                    AppStartState.NeedsOnboarding
                }
            }
        }
    }

    /** Call after onboarding finishes so the app moves straight to Home without re-fetching auth state. */
    fun markOnboardingComplete() {
        _startState.value = AppStartState.Ready
    }
}
