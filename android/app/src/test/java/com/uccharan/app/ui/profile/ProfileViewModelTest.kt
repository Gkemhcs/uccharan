package com.uccharan.app.ui.profile

import com.google.firebase.auth.FirebaseUser
import com.uccharan.app.MainDispatcherRule
import com.uccharan.app.data.model.LessonAttempt
import com.uccharan.app.data.model.UserProfile
import com.uccharan.app.data.repository.AuthRepository
import com.uccharan.app.data.repository.LessonRepository
import com.uccharan.app.data.repository.QuizAttemptRecord
import com.uccharan.app.data.repository.QuizRepository
import com.uccharan.app.data.repository.UserProfileRepository
import com.uccharan.app.data.roadmap.RoadmapDay
import com.uccharan.app.data.roadmap.RoadmapWeek
import io.mockk.coEvery
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test

class ProfileViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val authRepository = mockk<AuthRepository>()
    private val userProfileRepository = mockk<UserProfileRepository>()
    private val quizRepository = mockk<QuizRepository>()
    private val lessonRepository = mockk<LessonRepository>()

    private fun viewModel() = ProfileViewModel(authRepository, userProfileRepository, quizRepository, lessonRepository)

    private fun signedInAs(uid: String) {
        val user = mockk<FirebaseUser>()
        every { user.uid } returns uid
        every { authRepository.currentUser } returns user
        coEvery { userProfileRepository.getProfile(uid) } returns Result.success(UserProfile(uid = uid, xp = 120))
        coEvery { lessonRepository.getRecentAttempts(uid) } returns Result.success(emptyList())
    }

    @Test
    fun `week 1 shows complete once all seven day quizzes are passed`() = runTest {
        signedInAs("uid-1")
        coEvery { quizRepository.getPassedQuizIds("uid-1") } returns Result.success(
            setOf("quiz-day-1", "quiz-day-2", "quiz-day-3", "quiz-day-4", "quiz-day-5", "quiz-day-6", "quiz-day-7"),
        )
        coEvery { quizRepository.getAttemptHistory("uid-1") } returns Result.success(emptyList())

        val state = viewModel().uiState.value

        val week1 = state.weekProgress.first { it.week.level == 1 && it.week.weekNumber == 1 }
        assertEquals(WeekStatus.COMPLETE, week1.status)
        assertEquals(7, week1.daysComplete)
        assertEquals(7, week1.daysWithContent)
    }

    @Test
    fun `week 1 shows in progress with a partial pass count`() = runTest {
        signedInAs("uid-1")
        coEvery { quizRepository.getPassedQuizIds("uid-1") } returns Result.success(setOf("quiz-day-1", "quiz-day-2", "quiz-day-3"))
        coEvery { quizRepository.getAttemptHistory("uid-1") } returns Result.success(emptyList())

        val state = viewModel().uiState.value

        val week1 = state.weekProgress.first { it.week.level == 1 && it.week.weekNumber == 1 }
        assertEquals(WeekStatus.IN_PROGRESS, week1.status)
        assertEquals(3, week1.daysComplete)
    }

    @Test
    fun `a week with no authored quizzes yet is not available`() {
        // Tested against a synthetic week rather than live ROADMAP_WEEKS content —
        // every real week now has content, so this exercises the still-relevant
        // "days not authored yet" branch directly instead of depending on that
        // staying true of the real roadmap forever.
        val unauthoredWeek = RoadmapWeek(level = 99, weekNumber = 99, days = listOf(RoadmapDay(99, "Not yet written", track = null, quizId = null)))

        val progress = weekProgressFor(unauthoredWeek, passedQuizIds = emptySet())

        assertEquals(WeekStatus.NOT_AVAILABLE, progress.status)
        assertEquals(0, progress.daysWithContent)
    }

    @Test
    fun `every real roadmap week currently has authored content`() = runTest {
        // Documents the current state explicitly, so it's obvious in test
        // output (not just silently true) once/if this stops holding.
        signedInAs("uid-1")
        coEvery { quizRepository.getPassedQuizIds("uid-1") } returns Result.success(emptySet())
        coEvery { quizRepository.getAttemptHistory("uid-1") } returns Result.success(emptyList())

        val state = viewModel().uiState.value

        assertTrue(state.weekProgress.all { it.status != WeekStatus.NOT_AVAILABLE })
    }

    @Test
    fun `quiz history from the repository is surfaced to the UI state`() = runTest {
        signedInAs("uid-1")
        coEvery { quizRepository.getPassedQuizIds("uid-1") } returns Result.success(setOf("quiz-day-1"))
        val history = listOf(QuizAttemptRecord("quiz-day-1", "Day 1 Quiz", 5, 5, 30, true))
        coEvery { quizRepository.getAttemptHistory("uid-1") } returns Result.success(history)

        val state = viewModel().uiState.value

        assertEquals(history, state.quizHistory)
    }

    @Test
    fun `weak sounds from the repository's recent attempts are surfaced to the UI state`() = runTest {
        signedInAs("uid-1")
        coEvery { quizRepository.getPassedQuizIds("uid-1") } returns Result.success(emptySet())
        coEvery { quizRepository.getAttemptHistory("uid-1") } returns Result.success(emptyList())
        coEvery { lessonRepository.getRecentAttempts("uid-1") } returns Result.success(
            listOf(
                LessonAttempt(isCorrect = false, focusSounds = listOf("th")),
                LessonAttempt(isCorrect = false, focusSounds = listOf("th")),
            ),
        )

        val state = viewModel().uiState.value

        assertEquals(listOf("th"), state.weakSounds.map { it.sound })
    }

    @Test
    fun `computeWeakSounds ignores a sound with too few attempts to be meaningful`() {
        val attempts = listOf(LessonAttempt(isCorrect = false, focusSounds = listOf("th")))

        assertTrue(computeWeakSounds(attempts).isEmpty())
    }

    @Test
    fun `computeWeakSounds ignores a sound the learner has already mastered`() {
        val attempts = List(5) { LessonAttempt(isCorrect = true, focusSounds = listOf("v")) }

        assertTrue(computeWeakSounds(attempts).isEmpty())
    }

    @Test
    fun `computeWeakSounds surfaces a sound below the accuracy bar, worst first`() {
        val attempts = listOf(
            // "th": 1/4 correct = 25%
            LessonAttempt(isCorrect = true, focusSounds = listOf("th")),
            LessonAttempt(isCorrect = false, focusSounds = listOf("th")),
            LessonAttempt(isCorrect = false, focusSounds = listOf("th")),
            LessonAttempt(isCorrect = false, focusSounds = listOf("th")),
            // "v": 1/2 correct = 50%
            LessonAttempt(isCorrect = true, focusSounds = listOf("v")),
            LessonAttempt(isCorrect = false, focusSounds = listOf("v")),
        )

        val weakSounds = computeWeakSounds(attempts)

        assertEquals(listOf("th", "v"), weakSounds.map { it.sound })
        assertEquals(0.25, weakSounds.first { it.sound == "th" }.accuracy, 0.001)
    }

    @Test
    fun `computeWeakSounds credits every focus sound on a multi-sound attempt`() {
        val attempts = listOf(
            LessonAttempt(isCorrect = false, focusSounds = listOf("th", "v")),
            LessonAttempt(isCorrect = false, focusSounds = listOf("th", "v")),
        )

        val weakSounds = computeWeakSounds(attempts)

        assertEquals(setOf("th", "v"), weakSounds.map { it.sound }.toSet())
    }
}
