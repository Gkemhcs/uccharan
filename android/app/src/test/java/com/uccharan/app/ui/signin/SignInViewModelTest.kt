package com.uccharan.app.ui.signin

import com.google.firebase.auth.FirebaseUser
import com.uccharan.app.MainDispatcherRule
import com.uccharan.app.data.repository.AuthRepository
import io.mockk.coEvery
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Rule
import org.junit.Test

class SignInViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val authRepository = mockk<AuthRepository>()

    @Test
    fun `email and password fields update as the user types`() {
        val viewModel = SignInViewModel(authRepository)

        viewModel.onEmailChange("student@example.com")
        viewModel.onPasswordChange("hunter2")

        assertEquals("student@example.com", viewModel.uiState.value.email)
        assertEquals("hunter2", viewModel.uiState.value.password)
    }

    @Test
    fun `failed sign-in surfaces an error message and clears loading`() = runTest {
        coEvery { authRepository.signInWithEmail(any(), any()) } returns
            Result.failure(RuntimeException("Invalid credentials"))

        val viewModel = SignInViewModel(authRepository)
        viewModel.onEmailChange("student@example.com")
        viewModel.onPasswordChange("wrong")
        viewModel.signIn()

        val state = viewModel.uiState.value
        assertFalse(state.isLoading)
        assertEquals("Invalid credentials", state.errorMessage)
    }

    @Test
    fun `successful sign-in keeps loading true until navigation takes over`() = runTest {
        val user = mockk<FirebaseUser>()
        coEvery { authRepository.signInWithEmail(any(), any()) } returns Result.success(user)

        val viewModel = SignInViewModel(authRepository)
        viewModel.onEmailChange("student@example.com")
        viewModel.onPasswordChange("correct-password")
        viewModel.signIn()

        // Deliberate: RootViewModel's authStateFlow collection is what
        // navigates away, not this ViewModel — see the comment in
        // SignInViewModel.attempt(). isLoading should stay true so the
        // form doesn't flash back before navigation happens.
        assertEquals(true, viewModel.uiState.value.isLoading)
    }
}
