package com.uccharan.app.ui.onboarding

import com.google.firebase.auth.FirebaseUser
import com.uccharan.app.MainDispatcherRule
import com.uccharan.app.data.repository.AuthRepository
import com.uccharan.app.data.repository.UserProfileRepository
import com.uccharan.app.ui.tutor.TutorGender
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

class OnboardingViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val authRepository = mockk<AuthRepository>()
    private val userProfileRepository = mockk<UserProfileRepository>()
    private val uid = "uid-1"

    private fun createViewModel(onComplete: () -> Unit = {}): OnboardingViewModel {
        val user = mockk<FirebaseUser>()
        every { user.uid } returns uid
        every { authRepository.currentUser } returns user
        return OnboardingViewModel(authRepository, userProfileRepository, onComplete)
    }

    @Test
    fun `continue saves the selected language and address term, then completes`() = runTest {
        coEvery { userProfileRepository.completeOnboarding(uid, "Telugu", "Nanna", null) } returns Result.success(Unit)
        var completed = false

        val viewModel = createViewModel(onComplete = { completed = true })
        viewModel.onLanguageSelected("Telugu")
        viewModel.onAddressTermChange("Nanna")
        viewModel.onContinue()

        coVerify { userProfileRepository.completeOnboarding(uid, "Telugu", "Nanna", null) }
        assertTrue(completed)
    }

    @Test
    fun `continue saves the selected tutor gender`() = runTest {
        coEvery { userProfileRepository.completeOnboarding(uid, null, null, "male") } returns Result.success(Unit)
        var completed = false

        val viewModel = createViewModel(onComplete = { completed = true })
        viewModel.onTutorGenderSelected(TutorGender.MALE)
        viewModel.onContinue()

        coVerify { userProfileRepository.completeOnboarding(uid, null, null, "male") }
        assertTrue(completed)
    }

    @Test
    fun `skip saves null preferences and still completes`() = runTest {
        coEvery { userProfileRepository.completeOnboarding(uid, null, null, null) } returns Result.success(Unit)
        var completed = false

        val viewModel = createViewModel(onComplete = { completed = true })
        viewModel.onSkip()

        coVerify { userProfileRepository.completeOnboarding(uid, null, null, null) }
        assertTrue(completed)
    }

    @Test
    fun `save failure surfaces an error and does not call onComplete`() = runTest {
        coEvery { userProfileRepository.completeOnboarding(any(), any(), any(), any()) } returns
            Result.failure(RuntimeException("offline"))
        var completed = false

        val viewModel = createViewModel(onComplete = { completed = true })
        viewModel.onContinue()

        assertFalse(completed)
        assertEquals("offline", viewModel.uiState.value.errorMessage)
        assertFalse(viewModel.uiState.value.isSaving)
    }
}
