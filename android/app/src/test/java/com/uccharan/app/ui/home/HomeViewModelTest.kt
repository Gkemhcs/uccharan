package com.uccharan.app.ui.home

import com.google.firebase.auth.FirebaseUser
import com.uccharan.app.MainDispatcherRule
import com.uccharan.app.data.model.Lesson
import com.uccharan.app.data.model.UserProfile
import com.uccharan.app.data.repository.AuthRepository
import com.uccharan.app.data.repository.LessonRepository
import com.uccharan.app.data.repository.QuizRepository
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

class HomeViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val authRepository = mockk<AuthRepository>()
    private val userProfileRepository = mockk<UserProfileRepository>()
    private val lessonRepository = mockk<LessonRepository>()
    private val quizRepository = mockk<QuizRepository>()

    private fun viewModel() = HomeViewModel(authRepository, userProfileRepository, lessonRepository, quizRepository)

    private fun signedInAs(uid: String, currentTrack: String = "foundations") {
        val user = mockk<FirebaseUser>()
        every { user.uid } returns uid
        every { authRepository.currentUser } returns user
        coEvery { userProfileRepository.getProfile(uid) } returns Result.success(UserProfile(uid = uid, currentTrack = currentTrack))
    }

    @Test
    fun `loads lessons for the learner's current day and marks completed ones`() = runTest {
        signedInAs("uid-1")

        val lessons = listOf(
            Lesson(id = "l1", track = "foundations"),
            Lesson(id = "l2", track = "foundations"),
        )
        coEvery { lessonRepository.getLessonsForTrack("foundations") } returns Result.success(lessons)
        coEvery { lessonRepository.getCompletedLessonIds("uid-1") } returns Result.success(setOf("l1"))

        val state = viewModel().uiState.value

        assertFalse(state.isLoading)
        assertEquals(1, state.day?.day)
        assertEquals(2, state.lessons.size)
        assertTrue("l1" in state.completedLessonIds)
        assertFalse("l2" in state.completedLessonIds)
    }

    @Test
    fun `surfaces an error message when lessons fail to load`() = runTest {
        every { authRepository.currentUser } returns null
        coEvery { lessonRepository.getLessonsForTrack("foundations") } returns Result.failure(RuntimeException("offline"))

        val state = viewModel().uiState.value

        assertFalse(state.isLoading)
        assertEquals("offline", state.errorMessage)
    }

    @Test
    fun `skip section marks all remaining lessons complete and reloads`() = runTest {
        signedInAs("uid-1")

        val lessons = listOf(
            Lesson(id = "l1", track = "foundations"),
            Lesson(id = "l2", track = "foundations"),
            Lesson(id = "l3", track = "foundations"),
        )
        coEvery { lessonRepository.getLessonsForTrack("foundations") } returns Result.success(lessons)
        coEvery { lessonRepository.getCompletedLessonIds("uid-1") } returnsMany listOf(
            Result.success(setOf("l1")),
            Result.success(setOf("l1", "l2", "l3")),
        )
        coEvery { lessonRepository.markLessonsComplete("uid-1", listOf("l2", "l3")) } returns Result.success(Unit)

        val vm = viewModel()
        assertTrue(vm.uiState.value.canSkipTrack)

        vm.requestSkipTrack()
        assertTrue(vm.uiState.value.showSkipConfirmation)

        vm.confirmSkipTrack()

        coVerify { lessonRepository.markLessonsComplete("uid-1", listOf("l2", "l3")) }
        val state = vm.uiState.value
        assertFalse(state.showSkipConfirmation)
        assertFalse(state.isSkipping)
        assertEquals(setOf("l1", "l2", "l3"), state.completedLessonIds)
        assertFalse(state.canSkipTrack)
    }

    @Test
    fun `dismissing the skip confirmation does not touch any lessons`() = runTest {
        signedInAs("uid-1")

        val lessons = listOf(Lesson(id = "l1", track = "foundations"))
        coEvery { lessonRepository.getLessonsForTrack("foundations") } returns Result.success(lessons)
        coEvery { lessonRepository.getCompletedLessonIds("uid-1") } returns Result.success(emptySet())

        val vm = viewModel()
        vm.requestSkipTrack()
        vm.dismissSkipConfirmation()

        assertFalse(vm.uiState.value.showSkipConfirmation)
        coVerify(exactly = 0) { lessonRepository.markLessonsComplete(any(), any()) }
    }

    @Test
    fun `all lessons done and a quiz is seeded means ready for quiz`() = runTest {
        signedInAs("uid-1")

        val lessons = listOf(Lesson(id = "l1", track = "foundations"))
        coEvery { lessonRepository.getLessonsForTrack("foundations") } returns Result.success(lessons)
        coEvery { lessonRepository.getCompletedLessonIds("uid-1") } returns Result.success(setOf("l1"))

        val state = viewModel().uiState.value

        assertTrue(state.isReadyForQuiz)
        assertEquals("quiz-day-1", state.day?.quizId)
    }

    @Test
    fun `finishing the last authored day's quiz shows the beyond-content state`() = runTest {
        // Day 90 is the last entry in ROADMAP_DAYS (Level 3's capstone) — there's
        // no "next day" to advance to once its quiz is passed, regardless of how
        // much content exists overall (unlike day-7, which has day-8 right after it).
        signedInAs("uid-1", currentTrack = "day-90-capstone")
        coEvery { quizRepository.getPassedQuizIds("uid-1") } returns Result.success(setOf("quiz-day-90"))

        val state = viewModel().uiState.value

        assertFalse(state.isLoading)
        assertTrue(state.isBeyondAuthoredContent)
        coVerify(exactly = 0) { lessonRepository.getLessonsForTrack(any()) }
    }
}
