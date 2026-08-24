package com.uccharan.app.ui.practice

import com.google.firebase.auth.FirebaseUser
import com.uccharan.app.MainDispatcherRule
import com.uccharan.app.data.model.UserProfile
import com.uccharan.app.data.remote.PracticeApi
import com.uccharan.app.data.remote.PracticeMessage
import com.uccharan.app.data.remote.PracticeTurnResult
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

class PracticeConversationViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val authRepository = mockk<AuthRepository>()
    private val userProfileRepository = mockk<UserProfileRepository>()
    private val practiceApi = mockk<PracticeApi>()

    private val topic = "Food & Ordering"

    private fun signedInAs(uid: String, nativeLanguage: String? = "Telugu", addressTerm: String? = "Nanna") {
        val user = mockk<FirebaseUser>()
        every { user.uid } returns uid
        every { authRepository.currentUser } returns user
        coEvery { userProfileRepository.getProfile(uid) } returns Result.success(
            UserProfile(uid = uid, nativeLanguage = nativeLanguage, preferredAddressTerm = addressTerm),
        )
    }

    private fun viewModel() = PracticeConversationViewModel(topic, authRepository, userProfileRepository, practiceApi)

    @Test
    fun `seeds the transcript with a locally-built opening line naming the topic, with no network call`() = runTest {
        every { authRepository.currentUser } returns null

        val state = viewModel().uiState.value

        assertEquals(topic, state.topic)
        assertEquals(1, state.messages.size)
        assertEquals("tutor", state.messages.first().speaker)
        assertTrue(state.messages.first().text.contains(topic))
    }

    @Test
    fun `a recognized turn is appended, sent with the topic and preferences, and the reply is appended back`() = runTest {
        signedInAs("uid-1", nativeLanguage = "Telugu", addressTerm = "Nanna")
        val openingLine = "Hi! Let's practice today's topic together — $topic. Whenever you're ready, say something!"
        coEvery {
            practiceApi.sendTurn(
                chatId = any(),
                topic = topic,
                history = listOf(PracticeMessage(speaker = "tutor", text = openingLine)),
                learnerMessage = "I would like a cup of coffee.",
                preferredAddressTerm = "Nanna",
                nativeLanguage = "Telugu",
                conversationSummary = null,
                summarizedThroughIndex = 0,
            )
        } returns Result.success(
            PracticeTurnResult(
                tutorReply = "Great choice! Anything else?",
                correction = null,
                nativeNote = null,
                conversationSummary = null,
                summarizedThroughIndex = 0,
            ),
        )

        val vm = viewModel()
        vm.onSpeechRecognized("I would like a cup of coffee.")

        val state = vm.uiState.value
        assertFalse(state.isWaitingForTutor)
        assertEquals(3, state.messages.size)
        assertEquals("learner", state.messages[1].speaker)
        assertEquals("I would like a cup of coffee.", state.messages[1].text)
        assertEquals("tutor", state.messages[2].speaker)
        assertEquals("Great choice! Anything else?", state.messages[2].text)
    }

    @Test
    fun `carries conversation summary and index forward from the response, unmodified`() = runTest {
        signedInAs("uid-1")
        coEvery {
            practiceApi.sendTurn(
                chatId = any(),
                topic = any(),
                history = any(),
                learnerMessage = any(),
                preferredAddressTerm = any(),
                nativeLanguage = any(),
                conversationSummary = any(),
                summarizedThroughIndex = any(),
            )
        } returns Result.success(
            PracticeTurnResult(
                tutorReply = "Got it!",
                correction = null,
                nativeNote = null,
                conversationSummary = "The learner is from Uravakonda.",
                summarizedThroughIndex = 14,
            ),
        )

        val vm = viewModel()
        vm.onSpeechRecognized("I am from Uravakonda.")

        val state = vm.uiState.value
        assertEquals("The learner is from Uravakonda.", state.conversationSummary)
        assertEquals(14, state.summarizedThroughIndex)

        // The ViewModel never computes or windows this itself — it just echoes back
        // what the previous response said, verbatim, on the next turn.
        vm.onSpeechRecognized("It's a small town.")
        coVerify {
            practiceApi.sendTurn(
                chatId = any(),
                topic = any(),
                history = any(),
                learnerMessage = "It's a small town.",
                preferredAddressTerm = any(),
                nativeLanguage = any(),
                conversationSummary = "The learner is from Uravakonda.",
                summarizedThroughIndex = 14,
            )
        }
    }

    @Test
    fun `a second speech result while waiting for the tutor is ignored`() = runTest {
        signedInAs("uid-1")

        // sendTurn is deliberately left unstubbed for the *second* call — if the
        // guard fails, this test blows up with an unanswered-call error, which is
        // exactly the signal we want.
        coEvery {
            practiceApi.sendTurn(
                chatId = any(),
                topic = any(),
                history = any(),
                learnerMessage = "first message",
                preferredAddressTerm = any(),
                nativeLanguage = any(),
                conversationSummary = any(),
                summarizedThroughIndex = any(),
            )
        } coAnswers {
            // Never resolves within this test — simulates a turn still in flight.
            kotlinx.coroutines.suspendCancellableCoroutine { }
        }

        val vm = viewModel()
        vm.onSpeechRecognized("first message")
        assertTrue(vm.uiState.value.isWaitingForTutor)

        vm.onSpeechRecognized("second message")

        // Still just the opening line + the one learner message — the second call never landed.
        assertEquals(2, vm.uiState.value.messages.size)
        coVerify(exactly = 0) {
            practiceApi.sendTurn(
                chatId = any(),
                topic = any(),
                history = any(),
                learnerMessage = "second message",
                preferredAddressTerm = any(),
                nativeLanguage = any(),
                conversationSummary = any(),
                summarizedThroughIndex = any(),
            )
        }
    }

    @Test
    fun `a failed turn surfaces an error message and clears the waiting state`() = runTest {
        signedInAs("uid-1")
        coEvery {
            practiceApi.sendTurn(
                chatId = any(),
                topic = any(),
                history = any(),
                learnerMessage = any(),
                preferredAddressTerm = any(),
                nativeLanguage = any(),
                conversationSummary = any(),
                summarizedThroughIndex = any(),
            )
        } returns Result.failure(RuntimeException("offline"))

        val vm = viewModel()
        vm.onSpeechRecognized("hello")

        val state = vm.uiState.value
        assertFalse(state.isWaitingForTutor)
        assertEquals("offline", state.errorMessage)
    }

    private fun stubTurn(learnerMessage: String, correction: String? = null) {
        coEvery {
            practiceApi.sendTurn(
                chatId = any(),
                topic = any(),
                history = any(),
                learnerMessage = learnerMessage,
                preferredAddressTerm = any(),
                nativeLanguage = any(),
                conversationSummary = any(),
                summarizedThroughIndex = any(),
            )
        } returns Result.success(
            PracticeTurnResult(tutorReply = "Okay!", correction = correction, nativeNote = null, conversationSummary = null, summarizedThroughIndex = 0),
        )
    }

    @Test
    fun `ending a session below the turn threshold shows a summary but awards no xp`() = runTest {
        signedInAs("uid-1")
        stubTurn("one")
        stubTurn("two")

        val vm = viewModel()
        vm.onSpeechRecognized("one")
        vm.onSpeechRecognized("two")
        vm.endSession()

        val summary = vm.uiState.value.sessionSummary
        assertEquals(2, summary?.learnerTurns)
        assertEquals(0, summary?.xpEarned)
        coVerify(exactly = 0) { userProfileRepository.addXp(any(), any()) }
    }

    @Test
    fun `ending a session at the turn threshold awards xp exactly once`() = runTest {
        signedInAs("uid-1")
        coEvery { userProfileRepository.addXp("uid-1", PRACTICE_SESSION_XP_REWARD) } returns Result.success(Unit)
        stubTurn("one")
        stubTurn("two")
        stubTurn("three")

        val vm = viewModel()
        vm.onSpeechRecognized("one")
        vm.onSpeechRecognized("two")
        vm.onSpeechRecognized("three")
        vm.endSession()
        vm.endSession() // a stray double-tap must not double-award

        val summary = vm.uiState.value.sessionSummary
        assertEquals(3, summary?.learnerTurns)
        assertEquals(PRACTICE_SESSION_XP_REWARD, summary?.xpEarned)
        coVerify(exactly = 1) { userProfileRepository.addXp("uid-1", PRACTICE_SESSION_XP_REWARD) }
    }

    @Test
    fun `session summary collects every distinct correction given, not just the latest`() = runTest {
        signedInAs("uid-1")
        coEvery { userProfileRepository.addXp("uid-1", PRACTICE_SESSION_XP_REWARD) } returns Result.success(Unit)
        stubTurn("one", correction = "Use 'went' not 'go'.")
        stubTurn("two", correction = null)
        stubTurn("three", correction = "Say 'an apple', not 'a apple'.")

        val vm = viewModel()
        vm.onSpeechRecognized("one")
        vm.onSpeechRecognized("two")
        vm.onSpeechRecognized("three")
        vm.endSession()

        assertEquals(
            listOf("Use 'went' not 'go'.", "Say 'an apple', not 'a apple'."),
            vm.uiState.value.sessionSummary?.correctionsGiven,
        )
    }
}
