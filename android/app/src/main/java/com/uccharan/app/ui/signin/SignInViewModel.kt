package com.uccharan.app.ui.signin

import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.google.firebase.auth.FirebaseAuthException
import com.uccharan.app.data.repository.AuthRepository
import com.uccharan.app.data.repository.UserProfileRepository
import com.uccharan.app.data.validation.isValidEmail
import com.uccharan.app.data.validation.unmetPasswordRequirements
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

/** Which form [SignInScreen] is showing — see [SignInViewModel]'s class doc. */
enum class AuthMode { SIGN_IN, CREATE_ACCOUNT }

/**
 * Firebase Auth error codes meaning either "no account exists for this
 * email" or something close enough that we can't be sure which. Some
 * Firebase projects still return ERROR_USER_NOT_FOUND distinctly, but
 * current-generation Identity Platform projects often fold "no such user"
 * into the SAME ERROR_INVALID_CREDENTIAL as "wrong password", deliberately,
 * to prevent account enumeration — so rather than gamble on which behavior
 * this project has, [SignInViewModel.signIn] offers "create an account
 * instead" for all of them. Worst case it's an extra, harmless link; it
 * never asserts a real account doesn't exist when the truth is just a
 * typo'd password (which would risk the learner creating a duplicate
 * account and losing access to their real one).
 */
private val NO_ACCOUNT_OR_AMBIGUOUS_CODES = setOf("ERROR_USER_NOT_FOUND", "ERROR_INVALID_CREDENTIAL", "ERROR_WRONG_PASSWORD")

data class SignInUiState(
    val mode: AuthMode = AuthMode.SIGN_IN,
    val email: String = "",
    val name: String = "",
    val password: String = "",
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
    /** See [NO_ACCOUNT_OR_AMBIGUOUS_CODES] — offers a "create an account instead" CTA alongside [errorMessage]. */
    val suggestCreateAccount: Boolean = false,
)

/**
 * Sign-in and create-account are two distinct forms sharing one screen and
 * one email field carried across between them — not, as before, a single
 * form showing both a "Sign in" and a "Create an account" button at once
 * (confusing: it wasn't clear which fields belonged to which action, and
 * there was nowhere to enter a name, so every email/password account
 * permanently had a blank display name). [switchToCreateAccount] /
 * [switchToSignIn] toggle which form is showing.
 */
class SignInViewModel(
    private val authRepository: AuthRepository,
    private val userProfileRepository: UserProfileRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow(SignInUiState())
    val uiState: StateFlow<SignInUiState> = _uiState.asStateFlow()

    fun onEmailChange(email: String) = _uiState.update { it.copy(email = email, errorMessage = null, suggestCreateAccount = false) }
    fun onNameChange(name: String) = _uiState.update { it.copy(name = name, errorMessage = null) }
    fun onPasswordChange(password: String) = _uiState.update { it.copy(password = password, errorMessage = null, suggestCreateAccount = false) }

    /** Switches to the create-account form, carrying the email already typed over. */
    fun switchToCreateAccount() = _uiState.update {
        it.copy(mode = AuthMode.CREATE_ACCOUNT, password = "", errorMessage = null, suggestCreateAccount = false)
    }

    fun switchToSignIn() = _uiState.update {
        it.copy(mode = AuthMode.SIGN_IN, password = "", errorMessage = null, suggestCreateAccount = false)
    }

    fun signIn() {
        val state = _uiState.value
        if (!isValidEmail(state.email)) {
            setError("Please enter a valid email address.")
            return
        }
        if (state.password.isEmpty()) {
            setError("Please enter your password.")
            return
        }
        _uiState.update { it.copy(isLoading = true, errorMessage = null, suggestCreateAccount = false) }
        viewModelScope.launch {
            authRepository.signInWithEmail(state.email, state.password).onFailure { error ->
                val code = (error.cause as? FirebaseAuthException)?.errorCode
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        errorMessage = error.message ?: "Something went wrong",
                        suggestCreateAccount = code in NO_ACCOUNT_OR_AMBIGUOUS_CODES,
                    )
                }
            }
            // On success we don't touch isLoading/navigate here — RootViewModel's
            // authStateFlow collection picks up the new signed-in user and the
            // NavHost switches screens on its own.
        }
    }

    fun signUp() {
        val state = _uiState.value
        if (state.name.isBlank()) {
            setError("Please tell us your name.")
            return
        }
        if (!isValidEmail(state.email)) {
            setError("Please enter a valid email address.")
            return
        }
        val unmet = unmetPasswordRequirements(state.password)
        if (unmet.isNotEmpty()) {
            setError("Your password needs: ${unmet.joinToString(", ") { it.label.replaceFirstChar(Char::lowercase) }}.")
            return
        }

        val name = state.name.trim()
        _uiState.update { it.copy(isLoading = true, errorMessage = null) }
        viewModelScope.launch {
            authRepository.signUpWithEmail(state.email, state.password, name)
                .onSuccess { user ->
                    // Explicit, not left to RootViewModel's reactive listener alone — see
                    // AuthRepository.signUpWithEmail's doc on the race this closes.
                    userProfileRepository.ensureProfileExists(user.uid, name, state.email)
                }
                .onFailure { error ->
                    _uiState.update { it.copy(isLoading = false, errorMessage = error.message ?: "Something went wrong") }
                }
        }
    }

    fun signInWithGoogle(context: Context) = attempt { authRepository.signInWithGoogle(context) }

    private fun setError(message: String) = _uiState.update { it.copy(errorMessage = message) }

    private fun attempt(action: suspend () -> Result<*>) {
        _uiState.update { it.copy(isLoading = true, errorMessage = null) }
        viewModelScope.launch {
            action().onFailure { error ->
                _uiState.update { it.copy(isLoading = false, errorMessage = error.message ?: "Something went wrong") }
            }
            // On success we don't touch isLoading/navigate here — RootViewModel's
            // authStateFlow collection picks up the new signed-in user and the
            // NavHost switches screens on its own.
        }
    }
}
