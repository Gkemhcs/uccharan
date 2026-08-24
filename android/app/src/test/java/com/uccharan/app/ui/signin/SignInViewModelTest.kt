package com.uccharan.app.ui.signin

import com.google.firebase.auth.FirebaseAuthException
import com.google.firebase.auth.FirebaseUser
import com.uccharan.app.MainDispatcherRule
import com.uccharan.app.data.repository.AuthRepository
import com.uccharan.app.data.repository.UserProfileRepository
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test

class SignInViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val authRepository = mockk<AuthRepository>()
    private val userProfileRepository = mockk<UserProfileRepository>()

    private fun viewModel() = SignInViewModel(authRepository, userProfileRepository)

    @Test
    fun `email and password fields update as the user types`() {
        val viewModel = viewModel()

        viewModel.onEmailChange("student@example.com")
        viewModel.onPasswordChange("hunter2")

        assertEquals("student@example.com", viewModel.uiState.value.email)
        assertEquals("hunter2", viewModel.uiState.value.password)
    }

    @Test
    fun `failed sign-in surfaces an error message and clears loading`() = runTest {
        coEvery { authRepository.signInWithEmail(any(), any()) } returns
            Result.failure(RuntimeException("Invalid credentials"))

        val viewModel = viewModel()
        viewModel.onEmailChange("student@example.com")
        viewModel.onPasswordChange("wrong")
        viewModel.signIn()

        val state = viewModel.uiState.value
        assertFalse(state.isLoading)
        assertEquals("Invalid credentials", state.errorMessage)
        assertFalse(state.suggestCreateAccount)
    }

    @Test
    fun `successful sign-in keeps loading true until navigation takes over`() = runTest {
        val user = mockk<FirebaseUser>()
        coEvery { authRepository.signInWithEmail(any(), any()) } returns Result.success(user)

        val viewModel = viewModel()
        viewModel.onEmailChange("student@example.com")
        viewModel.onPasswordChange("correct-password")
        viewModel.signIn()

        // Deliberate: RootViewModel's authStateFlow collection is what
        // navigates away, not this ViewModel — see the comment in
        // SignInViewModel.attempt(). isLoading should stay true so the
        // form doesn't flash back before navigation happens.
        assertEquals(true, viewModel.uiState.value.isLoading)
    }

    @Test
    fun `sign-in against a nonexistent account offers to create one instead`() = runTest {
        val authException = mockk<FirebaseAuthException>()
        every { authException.errorCode } returns "ERROR_USER_NOT_FOUND"
        coEvery { authRepository.signInWithEmail(any(), any()) } returns
            Result.failure(Exception("No account found", authException))

        val viewModel = viewModel()
        viewModel.onEmailChange("nobody@example.com")
        viewModel.onPasswordChange("whatever")
        viewModel.signIn()

        assertTrue(viewModel.uiState.value.suggestCreateAccount)
    }

    @Test
    fun `sign-in with an ambiguous invalid-credential error also offers to create an account`() = runTest {
        // Current-generation Firebase projects often return this same code for both
        // "wrong password" and "no such user" — see SignInViewModel's doc.
        val authException = mockk<FirebaseAuthException>()
        every { authException.errorCode } returns "ERROR_INVALID_CREDENTIAL"
        coEvery { authRepository.signInWithEmail(any(), any()) } returns
            Result.failure(Exception("Invalid credential", authException))

        val viewModel = viewModel()
        viewModel.onEmailChange("someone@example.com")
        viewModel.onPasswordChange("maybe-wrong")
        viewModel.signIn()

        assertTrue(viewModel.uiState.value.suggestCreateAccount)
    }

    @Test
    fun `switching to create account mode clears the password but keeps the email`() {
        val viewModel = viewModel()
        viewModel.onEmailChange("student@example.com")
        viewModel.onPasswordChange("hunter2")

        viewModel.switchToCreateAccount()

        val state = viewModel.uiState.value
        assertEquals(AuthMode.CREATE_ACCOUNT, state.mode)
        assertEquals("student@example.com", state.email)
        assertEquals("", state.password)
    }

    @Test
    fun `sign-up requires a name`() {
        val viewModel = viewModel()
        viewModel.switchToCreateAccount()
        viewModel.onEmailChange("student@example.com")
        viewModel.onPasswordChange("Str0ng!Pass")

        viewModel.signUp()

        assertEquals("Please tell us your name.", viewModel.uiState.value.errorMessage)
        assertFalse(viewModel.uiState.value.isLoading)
    }

    @Test
    fun `successful sign-up sets the display name on the new profile, explicitly, not left to chance`() = runTest {
        val user = mockk<FirebaseUser>()
        every { user.uid } returns "uid-1"
        coEvery { authRepository.signUpWithEmail("student@example.com", "Str0ng!Pass", "Lakshmi") } returns Result.success(user)
        coEvery { userProfileRepository.ensureProfileExists("uid-1", "Lakshmi", "student@example.com") } returns Result.success(Unit)

        val viewModel = viewModel()
        viewModel.switchToCreateAccount()
        viewModel.onNameChange("Lakshmi")
        viewModel.onEmailChange("student@example.com")
        viewModel.onPasswordChange("Str0ng!Pass")
        viewModel.signUp()

        coVerify { authRepository.signUpWithEmail("student@example.com", "Str0ng!Pass", "Lakshmi") }
        coVerify { userProfileRepository.ensureProfileExists("uid-1", "Lakshmi", "student@example.com") }
    }

    @Test
    fun `failed sign-up surfaces an error message and clears loading`() = runTest {
        coEvery { authRepository.signUpWithEmail(any(), any(), any()) } returns
            Result.failure(RuntimeException("That email already has an account"))

        val viewModel = viewModel()
        viewModel.switchToCreateAccount()
        viewModel.onNameChange("Lakshmi")
        viewModel.onEmailChange("student@example.com")
        viewModel.onPasswordChange("Str0ng!Pass")
        viewModel.signUp()

        val state = viewModel.uiState.value
        assertFalse(state.isLoading)
        assertEquals("That email already has an account", state.errorMessage)
    }
}
