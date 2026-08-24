package com.uccharan.app.ui.quiz

import com.google.firebase.auth.FirebaseUser
import com.uccharan.app.MainDispatcherRule
import com.uccharan.app.data.model.Quiz
import com.uccharan.app.data.model.QuizOption
import com.uccharan.app.data.model.QuizQuestion
import com.uccharan.app.data.model.UserProfile
import com.uccharan.app.data.repository.AuthRepository
import com.uccharan.app.data.repository.QuizAttemptOutcome
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

class QuizViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val authRepository = mockk<AuthRepository>()
    private val userProfileRepository = mockk<UserProfileRepository>()
    private val quizRepository = mockk<QuizRepository>()

    private val fiveQuestionQuiz = Quiz(
        id = "quiz-day-2",
        track = "day-2-family",
        title = "Day 2 Quiz",
        xpReward = 30,
        questions = (1..5).map { i ->
            QuizQuestion(
                question = "Question $i",
                options = listOf(QuizOption("correct-$i", isCorrect = true), QuizOption("wrong-$i", isCorrect = false)),
            )
        },
    )

    private fun signedInAs(uid: String) {
        val user = mockk<FirebaseUser>()
        every { user.uid } returns uid
        every { authRepository.currentUser } returns user
        // The tutor-character shown on the pass screen loads the profile independently
        // of the quiz itself — stub it so it doesn't fail with an unrelated MockKException.
        coEvery { userProfileRepository.getProfile(uid) } returns Result.success(UserProfile(uid = uid))
    }

    private fun viewModel(quizId: String = "quiz-day-2") =
        QuizViewModel(quizId, authRepository, userProfileRepository, quizRepository)

    @Test
    fun `answering all questions correctly passes and awards full XP`() = runTest {
        signedInAs("uid-1")
        coEvery { quizRepository.getQuiz("quiz-day-2") } returns Result.success(fiveQuestionQuiz)
        coEvery { quizRepository.recordAttempt("uid-1", "quiz-day-2", "Day 2 Quiz", 5, 5, 30) } returns
            Result.success(QuizAttemptOutcome(passed = true, isFirstPass = true))
        coEvery { userProfileRepository.addXp("uid-1", 30) } returns Result.success(Unit)
        coEvery { userProfileRepository.advanceToTrack("uid-1", "day-3-routine") } returns Result.success(Unit)

        val vm = viewModel()
        repeat(5) { index ->
            vm.selectOption(0) // always the correct option, at index 0
            if (index < 4) vm.nextQuestion()
        }
        vm.nextQuestion() // finishes on the last question

        val state = vm.uiState.value
        assertTrue(state.isFinished)
        assertTrue(state.passed)
        assertEquals(5, state.correctCount)
        assertEquals(30, state.xpEarned)

        coVerify { quizRepository.recordAttempt("uid-1", "quiz-day-2", "Day 2 Quiz", 5, 5, 30) }
        coVerify { userProfileRepository.addXp("uid-1", 30) }
        coVerify { userProfileRepository.advanceToTrack("uid-1", "day-3-routine") }
    }

    @Test
    fun `scoring below 70 percent fails the quiz and awards no XP or advancement`() = runTest {
        signedInAs("uid-1")
        coEvery { quizRepository.getQuiz("quiz-day-2") } returns Result.success(fiveQuestionQuiz)
        coEvery { quizRepository.recordAttempt("uid-1", "quiz-day-2", "Day 2 Quiz", 2, 5, 0) } returns
            Result.success(QuizAttemptOutcome(passed = false, isFirstPass = false))

        val vm = viewModel()
        // Get questions 1-2 right, 3-5 wrong (2/5 = 40%, below the 70% pass bar).
        repeat(5) { index ->
            vm.selectOption(if (index < 2) 0 else 1)
            if (index < 4) vm.nextQuestion()
        }
        vm.nextQuestion()

        val state = vm.uiState.value
        assertTrue(state.isFinished)
        assertFalse(state.passed)
        assertEquals(2, state.correctCount)
        assertEquals(0, state.xpEarned)

        coVerify { quizRepository.recordAttempt("uid-1", "quiz-day-2", "Day 2 Quiz", 2, 5, 0) }
        coVerify(exactly = 0) { userProfileRepository.addXp(any(), any()) }
        coVerify(exactly = 0) { userProfileRepository.advanceToTrack(any(), any()) }
    }

    @Test
    fun `reviewing an already-passed quiz and scoring low again awards no XP and does not re-advance`() = runTest {
        // Regression test for a live bug report: a learner went back to revise an
        // already-completed day, scored below 70% on the review attempt, and their
        // earlier pass appeared to be lost. QuizRepository.recordAttempt is the one
        // that keeps `passed` sticky-true — this test locks in the ViewModel's half:
        // a review attempt (isFirstPass = false) must not re-award XP or re-advance
        // currentTrack, even when this particular attempt's own score was a fail.
        signedInAs("uid-1")
        coEvery { quizRepository.getQuiz("quiz-day-2") } returns Result.success(fiveQuestionQuiz)
        coEvery { quizRepository.recordAttempt("uid-1", "quiz-day-2", "Day 2 Quiz", 2, 5, 0) } returns
            Result.success(QuizAttemptOutcome(passed = true, isFirstPass = false))

        val vm = viewModel()
        repeat(5) { index ->
            vm.selectOption(if (index < 2) 0 else 1)
            if (index < 4) vm.nextQuestion()
        }
        vm.nextQuestion()

        val state = vm.uiState.value
        assertFalse(state.passed) // this attempt itself failed, and the result screen must reflect that
        assertEquals(0, state.xpEarned)

        coVerify(exactly = 0) { userProfileRepository.addXp(any(), any()) }
        coVerify(exactly = 0) { userProfileRepository.advanceToTrack(any(), any()) }
    }

    @Test
    fun `re-passing an already-passed quiz on review awards no duplicate XP and does not re-advance`() = runTest {
        signedInAs("uid-1")
        coEvery { quizRepository.getQuiz("quiz-day-2") } returns Result.success(fiveQuestionQuiz)
        coEvery { quizRepository.recordAttempt("uid-1", "quiz-day-2", "Day 2 Quiz", 5, 5, 30) } returns
            Result.success(QuizAttemptOutcome(passed = true, isFirstPass = false))

        val vm = viewModel()
        repeat(5) { index ->
            vm.selectOption(0)
            if (index < 4) vm.nextQuestion()
        }
        vm.nextQuestion()

        val state = vm.uiState.value
        assertTrue(state.passed)
        assertEquals(0, state.xpEarned) // no NEW xp — this quiz was already passed before
        assertTrue(state.isReviewPass)

        coVerify(exactly = 0) { userProfileRepository.addXp(any(), any()) }
        coVerify(exactly = 0) { userProfileRepository.advanceToTrack(any(), any()) }
    }

    @Test
    fun `selecting an option twice does not change the recorded answer`() = runTest {
        signedInAs("uid-1")
        coEvery { quizRepository.getQuiz("quiz-day-2") } returns Result.success(fiveQuestionQuiz)

        val vm = viewModel()
        vm.selectOption(0) // correct
        vm.selectOption(1) // should be ignored — an answer was already locked in

        assertEquals(0, vm.uiState.value.selectedOptionIndex)
        assertEquals(1, vm.uiState.value.correctCount)
    }

    @Test
    fun `a quiz with no questions surfaces an error instead of a blank quiz`() = runTest {
        every { authRepository.currentUser } returns null
        coEvery { quizRepository.getQuiz("empty-quiz") } returns Result.success(Quiz(id = "empty-quiz", questions = emptyList()))

        val state = viewModel(quizId = "empty-quiz").uiState.value

        assertFalse(state.isLoading)
        assertEquals("This quiz isn't ready yet", state.errorMessage)
    }
}
