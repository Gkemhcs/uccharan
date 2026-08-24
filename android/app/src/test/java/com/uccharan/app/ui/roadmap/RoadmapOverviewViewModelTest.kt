package com.uccharan.app.ui.roadmap

import com.google.firebase.auth.FirebaseUser
import com.uccharan.app.MainDispatcherRule
import com.uccharan.app.data.model.UserProfile
import com.uccharan.app.data.repository.AuthRepository
import com.uccharan.app.data.repository.QuizRepository
import com.uccharan.app.data.repository.UserProfileRepository
import com.uccharan.app.data.roadmap.ROADMAP_DAYS
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Rule
import org.junit.Test

class RoadmapOverviewViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val authRepository = mockk<AuthRepository>()
    private val userProfileRepository = mockk<UserProfileRepository>()
    private val quizRepository = mockk<QuizRepository>()

    private val day1 = ROADMAP_DAYS.first { it.day == 1 }
    private val day2 = ROADMAP_DAYS.first { it.day == 2 }

    private fun signedInAs(uid: String, currentTrack: String) {
        val user = mockk<FirebaseUser>()
        every { user.uid } returns uid
        every { authRepository.currentUser } returns user
        coEvery { userProfileRepository.getProfile(uid) } returns Result.success(UserProfile(uid = uid, currentTrack = currentTrack))
    }

    private fun viewModel() = RoadmapOverviewViewModel(authRepository, userProfileRepository, quizRepository)

    @Test
    fun `a passed day still shows completed even after jumping back to it to review`() = runTest {
        // Regression test for a live bug report: reviewing a completed day made it look
        // like the day's progress had been lost. currentTrack is deliberately pointed
        // AT day1's own track here — the exact state right after a review jump.
        signedInAs("uid-1", currentTrack = day1.track!!)
        coEvery { quizRepository.getPassedQuizIds("uid-1") } returns Result.success(setOf(day1.quizId!!))

        val vm = viewModel()
        val state = vm.uiState.value

        assertEquals(DayStatus.COMPLETED, state.statusFor(day1))
    }

    @Test
    fun `reviewing a completed day repoints the track without a confirmation dialog`() = runTest {
        signedInAs("uid-1", currentTrack = day2.track!!)
        coEvery { quizRepository.getPassedQuizIds("uid-1") } returns Result.success(setOf(day1.quizId!!))
        coEvery { userProfileRepository.advanceToTrack("uid-1", day1.track!!) } returns Result.success(Unit)

        val vm = viewModel()
        vm.reviewDay(day1)

        assertNull(vm.uiState.value.pendingJumpDay) // no dialog was ever opened
        assertEquals(day1.track, vm.uiState.value.currentTrack)
        coVerify { userProfileRepository.advanceToTrack("uid-1", day1.track!!) }
    }

    @Test
    fun `jumping ahead to a not-yet-completed day still asks for confirmation first`() = runTest {
        signedInAs("uid-1", currentTrack = day1.track!!)
        coEvery { quizRepository.getPassedQuizIds("uid-1") } returns Result.success(emptySet())

        val vm = viewModel()
        vm.requestJump(day2)

        assertEquals(day2, vm.uiState.value.pendingJumpDay)
        coVerify(exactly = 0) { userProfileRepository.advanceToTrack(any(), any()) }
    }
}
