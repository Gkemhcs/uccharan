package com.uccharan.app.ui.signin

import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.uccharan.app.data.repository.AuthRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class SignInUiState(
    val email: String = "",
    val password: String = "",
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
)

class SignInViewModel(private val authRepository: AuthRepository) : ViewModel() {

    private val _uiState = MutableStateFlow(SignInUiState())
    val uiState: StateFlow<SignInUiState> = _uiState.asStateFlow()

    fun onEmailChange(email: String) = _uiState.update { it.copy(email = email, errorMessage = null) }
    fun onPasswordChange(password: String) = _uiState.update { it.copy(password = password, errorMessage = null) }

    fun signIn() = attempt { authRepository.signInWithEmail(_uiState.value.email, _uiState.value.password) }

    fun signUp() = attempt { authRepository.signUpWithEmail(_uiState.value.email, _uiState.value.password) }

    fun signInWithGoogle(context: Context) = attempt { authRepository.signInWithGoogle(context) }

    private fun attempt(action: suspend () -> Result<*>) {
        _uiState.update { it.copy(isLoading = true, errorMessage = null) }
        viewModelScope.launch {
            val result = action()
            result.onFailure { error ->
                _uiState.update { it.copy(isLoading = false, errorMessage = error.message ?: "Something went wrong") }
            }
            // On success we don't touch isLoading/navigate here — RootViewModel's
            // authStateFlow collection picks up the new signed-in user and the
            // NavHost switches screens on its own.
        }
    }
}
