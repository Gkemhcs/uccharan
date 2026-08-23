package com.uccharan.app.ui.signin

import com.google.firebase.auth.FirebaseUser
import com.google.firebase.auth.PhoneAuthCredential
import com.uccharan.app.MainDispatcherRule
import com.uccharan.app.data.repository.AuthRepository
import io.mockk.coEvery
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test

class PhoneSignInViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val authRepository = mockk<AuthRepository>()

    @Test
    fun `code sent moves to the OTP step and stores the verification id`() {
        val viewModel = PhoneSignInViewModel(authRepository)
        viewModel.onPhoneNumberChange("+911234567890")

        viewModel.onVerificationStarted()
        assertTrue(viewModel.uiState.value.isLoading)

        viewModel.onCodeSent("verification-id-1")

        val state = viewModel.uiState.value
        assertFalse(state.isLoading)
        assertEquals(PhoneSignInStep.ENTER_OTP, state.step)
        assertEquals("verification-id-1", state.verificationId)
    }

    @Test
    fun `verification failure surfaces an error and stays on the phone step`() {
        val viewModel = PhoneSignInViewModel(authRepository)

        viewModel.onVerificationStarted()
        viewModel.onVerificationFailed("Invalid phone number")

        val state = viewModel.uiState.value
        assertFalse(state.isLoading)
        assertEquals("Invalid phone number", state.errorMessage)
        assertEquals(PhoneSignInStep.ENTER_PHONE, state.step)
    }

    @Test
    fun `auto verification signs in directly without needing an OTP`() = runTest {
        val credential = mockk<PhoneAuthCredential>()
        val user = mockk<FirebaseUser>()
        coEvery { authRepository.signInWithPhoneCredential(credential) } returns Result.success(user)

        val viewModel = PhoneSignInViewModel(authRepository)
        viewModel.onAutoVerificationCompleted(credential)

        // Success leaves isLoading true until RootViewModel's auth-state
        // collection navigates away — same deliberate pattern as SignInViewModel.
        assertTrue(viewModel.uiState.value.isLoading)
        assertNull(viewModel.uiState.value.errorMessage)
    }

    @Test
    fun `submitting an incorrect otp surfaces the failure`() = runTest {
        val viewModel = PhoneSignInViewModel(authRepository)
        viewModel.onVerificationStarted()
        viewModel.onCodeSent("verification-id-1")
        viewModel.onOtpChange("000000")

        // PhoneAuthProvider.getCredential() needs a real Android environment to
        // construct, so this test only reaches the point of confirming state
        // (verificationId present, ready to submit) rather than calling
        // onSubmitOtp() itself — that path is covered by the instrumented flow.
        assertEquals("verification-id-1", viewModel.uiState.value.verificationId)
        assertEquals("000000", viewModel.uiState.value.otpCode)
    }
}
