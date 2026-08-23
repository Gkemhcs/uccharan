package com.uccharan.app.ui.signin

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.google.firebase.auth.PhoneAuthCredential
import com.google.firebase.auth.PhoneAuthProvider
import com.uccharan.app.data.repository.AuthRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

enum class PhoneSignInStep { ENTER_PHONE, ENTER_OTP }

data class PhoneSignInUiState(
    val step: PhoneSignInStep = PhoneSignInStep.ENTER_PHONE,
    val phoneNumber: String = "",
    val otpCode: String = "",
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
    val verificationId: String? = null,
)

/**
 * Firebase's PhoneAuthProvider is callback-based and needs an Activity, so
 * (same pattern as SpeechRecognizer in LessonScreen) the actual
 * verifyPhoneNumber() call is driven from the UI layer — this ViewModel only
 * receives the outcomes, keeping it unit-testable without Android framework
 * dependencies.
 */
class PhoneSignInViewModel(private val authRepository: AuthRepository) : ViewModel() {

    private val _uiState = MutableStateFlow(PhoneSignInUiState())
    val uiState: StateFlow<PhoneSignInUiState> = _uiState.asStateFlow()

    fun onPhoneNumberChange(value: String) = _uiState.update { it.copy(phoneNumber = value, errorMessage = null) }

    fun onOtpChange(value: String) = _uiState.update { it.copy(otpCode = value, errorMessage = null) }

    fun onVerificationStarted() = _uiState.update { it.copy(isLoading = true, errorMessage = null) }

    fun onCodeSent(verificationId: String) = _uiState.update {
        it.copy(isLoading = false, step = PhoneSignInStep.ENTER_OTP, verificationId = verificationId)
    }

    fun onVerificationFailed(message: String) = _uiState.update { it.copy(isLoading = false, errorMessage = message) }

    /** Some devices auto-detect the SMS and verify without the user typing anything. */
    fun onAutoVerificationCompleted(credential: PhoneAuthCredential) = signIn(credential)

    fun onSubmitOtp() {
        val verificationId = _uiState.value.verificationId ?: return
        signIn(PhoneAuthProvider.getCredential(verificationId, _uiState.value.otpCode))
    }

    private fun signIn(credential: PhoneAuthCredential) {
        _uiState.update { it.copy(isLoading = true, errorMessage = null) }
        viewModelScope.launch {
            authRepository.signInWithPhoneCredential(credential).onFailure { error ->
                _uiState.update { it.copy(isLoading = false, errorMessage = error.message ?: "Couldn't verify that code") }
            }
            // On success, RootViewModel's authStateFlow collection navigates away
            // — same deliberate pattern as SignInViewModel, see its comment.
        }
    }
}
