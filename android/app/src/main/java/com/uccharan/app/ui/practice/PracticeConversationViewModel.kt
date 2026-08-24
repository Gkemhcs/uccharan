package com.uccharan.app.ui.practice

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.uccharan.app.data.remote.PracticeApi
import com.uccharan.app.data.remote.PracticeMessage
import com.uccharan.app.data.repository.AuthRepository
import com.uccharan.app.data.repository.UserProfileRepository
import com.uccharan.app.ui.tutor.TutorGender
import com.uccharan.app.ui.tutor.tutorGenderFromStorage
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.util.UUID

/** How long a turn waits before assuming a Render free-tier cold start, not just normal Gemini latency. */
private const val WAKING_UP_HINT_DELAY_MS = 6000L

data class PracticeConversationUiState(
    val topic: String = "",
    val tutorGender: TutorGender = TutorGender.FEMALE,
    val messages: List<PracticeMessage> = emptyList(),
    val isListening: Boolean = false,
    val isWaitingForTutor: Boolean = false,
    /** True once a turn has been in flight a while — see [PracticeConversationViewModel.onSpeechRecognized]. */
    val isWakingUp: Boolean = false,
    val lastCorrection: String? = null,
    val lastNativeNote: String? = null,
    val errorMessage: String? = null,
    /**
     * Long-conversation memory, carried verbatim between turns — see the
     * class doc. Internal bookkeeping only; never rendered in the chat UI.
     */
    val conversationSummary: String? = null,
    val summarizedThroughIndex: Int = 0,
)

/**
 * Drives one roleplay "Practice with your Tutor" conversation. Unlike
 * [com.uccharan.app.ui.lesson.LessonViewModel], there's no fixed target
 * sentence to check against — the backend's Gemini-backed tutor persona
 * carries the conversation and flags at most one gentle correction per turn.
 *
 * **Always tied to a topic, never open-ended.** [topic] is the learner's
 * CURRENT roadmap day theme (e.g. "Food & Ordering"), passed in via nav args
 * from [com.uccharan.app.ui.home.HomeScreen] — there is deliberately no
 * scenario picker and no "free conversation, no fixed topic" mode (see
 * CURRICULUM.md §8: practice is assigned around what was just taught, the
 * way a real tutor does, not an open menu to explore). Because the topic is
 * already known from nav args, the transcript is seeded with a locally-built
 * opening line immediately — no network round-trip needed before the screen
 * can render, unlike the old scenario-list lookup this replaced.
 *
 * **Session identity.** [chatId] is a fresh UUID generated once per
 * conversation (i.e. once per ViewModel instance — a new one is created each
 * time this screen is entered). Every request is otherwise fully stateless
 * (nothing is stored server-side), so this doesn't gate or look anything
 * up — it exists so concurrent conversations from different learners or
 * devices are always distinguishable server-side (logs/tracing), and so
 * each session has a stable identity if server-side persistence is added
 * later.
 *
 * **Long-conversation memory.** This ViewModel does no windowing or
 * threshold math itself — it always sends the full transcript-so-far as
 * `history`, plus whatever `conversationSummary`/`summarizedThroughIndex`
 * the last response returned (both start unset). The backend alone decides
 * when enough history has piled up to fold older turns into a summary and
 * returns the updated values; this class just stores and re-sends them
 * unchanged, so a fact mentioned early (a hometown, a family member)
 * doesn't silently vanish from the tutor's context once it's no longer in
 * the backend's recent-turns window.
 */
class PracticeConversationViewModel(
    private val topic: String,
    private val authRepository: AuthRepository,
    private val userProfileRepository: UserProfileRepository,
    private val practiceApi: PracticeApi,
) : ViewModel() {

    private val chatId: String = UUID.randomUUID().toString()

    private val _uiState = MutableStateFlow(
        PracticeConversationUiState(
            topic = topic,
            messages = listOf(PracticeMessage(speaker = "tutor", text = openingLineFor(topic))),
        ),
    )
    val uiState: StateFlow<PracticeConversationUiState> = _uiState.asStateFlow()

    private var nativeLanguage: String? = null
    private var preferredAddressTerm: String? = null

    init {
        // Learner preferences load in the background — nativeLanguage/preferredAddressTerm
        // are only needed once the first turn is actually sent, never to render the screen.
        // tutorGender DOES affect the first render (the scene banner's character), but
        // defaults sensibly (FEMALE) until it resolves, so there's still no loading gate.
        viewModelScope.launch {
            authRepository.currentUser?.uid?.let { uid ->
                userProfileRepository.getProfile(uid).getOrNull()?.let { profile ->
                    nativeLanguage = profile.nativeLanguage
                    preferredAddressTerm = profile.preferredAddressTerm
                    _uiState.update { it.copy(tutorGender = tutorGenderFromStorage(profile.tutorGender)) }
                }
            }
        }
    }

    fun onListeningStarted() = _uiState.update { it.copy(isListening = true, errorMessage = null) }

    fun onSpeechError(message: String) = _uiState.update { it.copy(isListening = false, errorMessage = message) }

    fun onSpeechRecognized(spokenText: String) {
        val state = _uiState.value
        // Guards against a second speech result racing in while a turn is
        // still in flight — the mic button is hidden/disabled during
        // isWaitingForTutor, but this keeps the state machine correct even
        // if a stray callback lands after the fact.
        if (state.isWaitingForTutor) return

        // Captured before this turn's messages are appended: `history` is
        // "everything before this new message", matching sendTurn's shape
        // (the new message goes in `learnerMessage`, separately).
        val historyForRequest = state.messages
        val summaryForRequest = state.conversationSummary
        val summarizedThroughIndexForRequest = state.summarizedThroughIndex

        _uiState.update {
            it.copy(
                isListening = false,
                isWaitingForTutor = true,
                isWakingUp = false,
                messages = it.messages + PracticeMessage(speaker = "learner", text = spokenText),
                errorMessage = null,
                lastCorrection = null,
                lastNativeNote = null,
            )
        }

        // Most turns come back in a couple seconds — only after a real wait
        // do we suggest a cold start, rather than assuming it up front.
        val wakingUpHintJob = viewModelScope.launch {
            delay(WAKING_UP_HINT_DELAY_MS)
            _uiState.update { it.copy(isWakingUp = true) }
        }

        viewModelScope.launch {
            practiceApi.sendTurn(
                chatId = chatId,
                topic = topic,
                history = historyForRequest,
                learnerMessage = spokenText,
                preferredAddressTerm = preferredAddressTerm,
                nativeLanguage = nativeLanguage,
                conversationSummary = summaryForRequest,
                summarizedThroughIndex = summarizedThroughIndexForRequest,
            ).onSuccess { result ->
                wakingUpHintJob.cancel()
                _uiState.update {
                    it.copy(
                        isWaitingForTutor = false,
                        isWakingUp = false,
                        messages = it.messages + PracticeMessage(speaker = "tutor", text = result.tutorReply),
                        lastCorrection = result.correction,
                        lastNativeNote = result.nativeNote,
                        conversationSummary = result.conversationSummary,
                        summarizedThroughIndex = result.summarizedThroughIndex,
                    )
                }
            }.onFailure { error ->
                wakingUpHintJob.cancel()
                _uiState.update {
                    it.copy(isWaitingForTutor = false, isWakingUp = false, errorMessage = error.message ?: "Couldn't reach the tutor — check your connection")
                }
            }
        }
    }
}

/** A friendly, generic opener naming the topic — built locally so the chat can start instantly, with no network round-trip. */
private fun openingLineFor(topic: String) = "Hi! Let's practice today's topic together — $topic. Whenever you're ready, say something!"
