package com.uccharan.app.ui.listening

import com.google.firebase.auth.FirebaseUser
import com.uccharan.app.MainDispatcherRule
import com.uccharan.app.data.remote.ListeningApi
import com.uccharan.app.data.remote.ListeningExercise
import com.uccharan.app.data.repository.AuthRepository
import com.uccharan.app.data.repository.UserProfileRepository
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test

class ListeningViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val authRepository = mockk<AuthRepository>()
    private val userProfileRepository = mockk<UserProfileRepository>()
    private val listeningApi = mockk<ListeningApi>()

    private val topic = "Ordering food at a restaurant"

    private fun exercise(correctIndex: Int = 0) = ListeningExercise(
        passage = "Hi, table for two please.",
        question = "What did the speaker ask for?",
        options = listOf("A table for two", "The bill", "A menu", "Directions"),
        correctOptionIndex = correctIndex,
        explanation = "They said 'table for two'.",
    )

    private fun signedInAs(uid: String) {
        val user = mockk<FirebaseUser>()
        every { user.uid } returns uid
        every { authRepository.currentUser } returns user
    }

    private fun viewModel() = ListeningViewModel(topic, authRepository, userProfileRepository, listeningApi)

    @Test
    fun `loads a round on init and requests it with the given topic`() = runTest {
        signedInAs("uid-1")
        coEvery { listeningApi.generateExercise(topic) } returns Result.success(exercise())

        val vm = viewModel()

        assertFalse(vm.uiState.value.isLoadingRound)
        assertEquals(exercise(), vm.uiState.value.exercise)
        coVerify { listeningApi.generateExercise(topic) }
    }

    @Test
    fun `a load failure surfaces an error message`() = runTest {
        signedInAs("uid-1")
        coEvery { listeningApi.generateExercise(topic) } returns Result.failure(RuntimeException("offline"))

        val vm = viewModel()

        assertFalse(vm.uiState.value.isLoadingRound)
        assertEquals("offline", vm.uiState.value.errorMessage)
    }

    @Test
    fun `selecting an option locks it in and counts correctness`() = runTest {
        signedInAs("uid-1")
        coEvery { listeningApi.generateExercise(topic) } returns Result.success(exercise(correctIndex = 0))

        val vm = viewModel()
        vm.selectOption(0)
        vm.selectOption(1) // ignored — already answered

        val state = vm.uiState.value
        assertEquals(0, state.selectedOptionIndex)
        assertEquals(1, state.correctCount)
    }

    @Test
    fun `an incorrect selection does not increment the correct count`() = runTest {
        signedInAs("uid-1")
        coEvery { listeningApi.generateExercise(topic) } returns Result.success(exercise(correctIndex = 0))

        val vm = viewModel()
        vm.selectOption(2)

        assertEquals(0, vm.uiState.value.correctCount)
    }

    @Test
    fun `nextRound loads a fresh exercise and advances the round counter`() = runTest {
        signedInAs("uid-1")
        coEvery { listeningApi.generateExercise(topic) } returns Result.success(exercise())

        val vm = viewModel()
        vm.selectOption(0)
        vm.nextRound()

        val state = vm.uiState.value
        assertEquals(1, state.roundsCompleted)
        assertFalse(state.isSessionComplete)
        assertNull(state.selectedOptionIndex) // fresh round, nothing answered yet
        coVerify(exactly = 2) { listeningApi.generateExercise(topic) } // once on init, once for this nextRound
    }

    @Test
    fun `finishing the last round completes the session and awards xp for every correct answer`() = runTest {
        signedInAs("uid-1")
        coEvery { listeningApi.generateExercise(topic) } returns Result.success(exercise(correctIndex = 0))
        coEvery { userProfileRepository.addXp("uid-1", any()) } returns Result.success(Unit)

        val vm = viewModel()
        repeat(LISTENING_SESSION_ROUNDS) { roundIndex ->
            vm.selectOption(0) // always correct
            vm.nextRound()
        }

        val state = vm.uiState.value
        assertTrue(state.isSessionComplete)
        assertEquals(LISTENING_SESSION_ROUNDS, state.correctCount)
        assertEquals(LISTENING_SESSION_ROUNDS * LISTENING_XP_PER_CORRECT, state.xpEarned)
        coVerify { userProfileRepository.addXp("uid-1", LISTENING_SESSION_ROUNDS * LISTENING_XP_PER_CORRECT) }
    }

    @Test
    fun `a session with zero correct answers awards no xp`() = runTest {
        signedInAs("uid-1")
        coEvery { listeningApi.generateExercise(topic) } returns Result.success(exercise(correctIndex = 0))

        val vm = viewModel()
        repeat(LISTENING_SESSION_ROUNDS) {
            vm.selectOption(1) // always wrong
            vm.nextRound()
        }

        assertEquals(0, vm.uiState.value.xpEarned)
        coVerify(exactly = 0) { userProfileRepository.addXp(any(), any()) }
    }
}
