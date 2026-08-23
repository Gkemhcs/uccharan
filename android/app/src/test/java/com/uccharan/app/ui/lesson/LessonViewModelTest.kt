package com.uccharan.app.ui.lesson

import com.google.firebase.auth.FirebaseUser
import com.uccharan.app.MainDispatcherRule
import com.uccharan.app.data.model.Lesson
import com.uccharan.app.data.model.LessonAttempt
import com.uccharan.app.data.model.LessonPrompt
import com.uccharan.app.data.model.UserProfile
import com.uccharan.app.data.remote.CorrectionApi
import com.uccharan.app.data.remote.CorrectionResult
import com.uccharan.app.data.repository.AuthRepository
import com.uccharan.app.data.repository.LessonRepository
import com.uccharan.app.data.repository.UserProfileRepository
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Rule
import org.junit.Test

class LessonViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val authRepository = mockk<AuthRepository>()
    private val userProfileRepository = mockk<UserProfileRepository>()
    private val lessonRepository = mockk<LessonRepository>()
    private val correctionApi = mockk<CorrectionApi>()

    private val lesson = Lesson(
        id = "found-a1-01",
        track = "foundations",
        prompt = LessonPrompt(targetSentence = "Nice to meet you."),
        xpReward = 10,
    )
    private val uid = "test-uid"

    @Before
    fun setUp() {
        val user = mockk<FirebaseUser>()
        every { user.uid } returns uid
        every { authRepository.currentUser } returns user
        coEvery { userProfileRepository.getProfile(uid) } returns Result.success(
            UserProfile(uid = uid, nativeLanguage = "Telugu", preferredAddressTerm = "Nanna"),
        )
        coEvery { lessonRepository.getLesson(lesson.id) } returns Result.success(lesson)
        coEvery { lessonRepository.logAttempt(any(), any()) } returns Result.success(Unit)
        coEvery { lessonRepository.markLessonComplete(any(), any()) } returns Result.success(Unit)
        coEvery { userProfileRepository.addXp(any(), any()) } returns Result.success(Unit)
    }

    private fun createViewModel() =
        LessonViewModel(lesson.id, authRepository, userProfileRepository, lessonRepository, correctionApi)

    @Test
    fun `loads lesson and stored language preferences on init`() = runTest {
        val viewModel = createViewModel()

        val state = viewModel.uiState.value
        assertFalse(state.isLoadingLesson)
        assertEquals(lesson, state.lesson)
    }

    @Test
    fun `correct attempt logs it, marks lesson complete, and awards xp`() = runTest {
        coEvery {
            correctionApi.correctAttempt("Nice to meet you.", "Nice to meet you.", "Nanna", "Telugu")
        } returns Result.success(CorrectionResult(isCorrect = true, feedback = "Great job!", nativeExplanation = null))

        val viewModel = createViewModel()
        viewModel.onSpeechRecognized("Nice to meet you.")

        val state = viewModel.uiState.value
        assertTrue(state.correctionResult?.isCorrect == true)
        assertTrue(state.isLessonComplete)
        coVerify { lessonRepository.logAttempt(uid, match<LessonAttempt> { it.isCorrect && it.spokenText == "Nice to meet you." }) }
        coVerify { lessonRepository.markLessonComplete(uid, lesson.id) }
        coVerify { userProfileRepository.addXp(uid, lesson.xpReward) }
    }

    @Test
    fun `incorrect attempt logs it but does not mark the lesson complete`() = runTest {
        coEvery {
            correctionApi.correctAttempt(any(), any(), any(), any())
        } returns Result.success(CorrectionResult(isCorrect = false, feedback = "Try again", nativeExplanation = null))

        val viewModel = createViewModel()
        viewModel.onSpeechRecognized("Nice to meat you.")

        val state = viewModel.uiState.value
        assertFalse(state.correctionResult?.isCorrect ?: true)
        assertFalse(state.isLessonComplete)
        coVerify { lessonRepository.logAttempt(uid, any()) }
        coVerify(exactly = 0) { lessonRepository.markLessonComplete(any(), any()) }
        coVerify(exactly = 0) { userProfileRepository.addXp(any(), any()) }
    }

    @Test
    fun `backend failure surfaces an error message instead of crashing`() = runTest {
        coEvery {
            correctionApi.correctAttempt(any(), any(), any(), any())
        } returns Result.failure(java.io.IOException("network down"))

        val viewModel = createViewModel()
        viewModel.onSpeechRecognized("Nice to meet you.")

        val state = viewModel.uiState.value
        assertFalse(state.isCheckingAttempt)
        assertEquals("network down", state.errorMessage)
    }

    @Test
    fun `retry clears the previous result so the mic can be used again`() = runTest {
        coEvery {
            correctionApi.correctAttempt(any(), any(), any(), any())
        } returns Result.success(CorrectionResult(isCorrect = false, feedback = "Try again", nativeExplanation = null))

        val viewModel = createViewModel()
        viewModel.onSpeechRecognized("Nice to meat you.")
        viewModel.retry()

        val state = viewModel.uiState.value
        assertEquals(null, state.correctionResult)
        assertEquals(null, state.lastSpokenText)
    }
}
