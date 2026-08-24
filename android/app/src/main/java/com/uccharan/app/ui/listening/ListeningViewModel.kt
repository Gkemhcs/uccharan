package com.uccharan.app.ui.listening

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.uccharan.app.data.remote.ListeningApi
import com.uccharan.app.data.remote.ListeningExercise
import com.uccharan.app.data.repository.AuthRepository
import com.uccharan.app.data.repository.UserProfileRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

/** A session is a short, fixed set of rounds — long enough to be worth doing, short enough not to feel like a chore. */
internal const val LISTENING_SESSION_ROUNDS = 5

/** Per correct answer, awarded once at the end of the session — see [ListeningViewModel.finishSession]. */
internal const val LISTENING_XP_PER_CORRECT = 5

data class ListeningUiState(
    val topic: String = "",
    val isLoadingRound: Boolean = true,
    val exercise: ListeningExercise? = null,
    val hasPlayedOnce: Boolean = false,
    val selectedOptionIndex: Int? = null,
    val roundsCompleted: Int = 0,
    val correctCount: Int = 0,
    val isSessionComplete: Boolean = false,
    val xpEarned: Int = 0,
    val errorMessage: String? = null,
) {
    val isLastRound: Boolean get() = roundsCompleted == LISTENING_SESSION_ROUNDS - 1
}

/**
 * Drives a short "Listening Practice" session: [LISTENING_SESSION_ROUNDS]
 * rounds, each a short passage generated around [topic] (see
 * [com.uccharan.app.data.remote.ListeningApi]) that the learner hears via
 * on-device text-to-speech, then answers ONE multiple-choice comprehension
 * question about.
 *
 * **Why multiple-choice, not "repeat what you heard."** Every other
 * exercise in this app checks PRODUCTION (can the learner say the target
 * sentence), graded against a speech-recognition transcript — a proxy that
 * can be wrong in both directions (the recognizer can clean up a real
 * mispronunciation into matching text, or mishear a correct attempt). This
 * exercise is deliberately checking COMPREHENSION instead, a different
 * skill real conversations demand just as much — understanding a shopkeeper
 * or a doctor, not just producing sentences oneself — and multiple-choice
 * measures it directly, without inheriting that same speech-recognition
 * proxy problem.
 *
 * **Why the passage is never shown until after answering.** Reading the
 * passage while it plays would turn this into a reading exercise wearing a
 * listening costume — the whole point is training the ear.
 */
class ListeningViewModel(
    private val topic: String,
    private val authRepository: AuthRepository,
    private val userProfileRepository: UserProfileRepository,
    private val listeningApi: ListeningApi,
) : ViewModel() {

    private val _uiState = MutableStateFlow(ListeningUiState(topic = topic))
    val uiState: StateFlow<ListeningUiState> = _uiState.asStateFlow()

    init {
        loadRound()
    }

    private fun loadRound() {
        _uiState.update {
            it.copy(isLoadingRound = true, exercise = null, hasPlayedOnce = false, selectedOptionIndex = null, errorMessage = null)
        }
        viewModelScope.launch {
            listeningApi.generateExercise(topic)
                .onSuccess { exercise -> _uiState.update { it.copy(isLoadingRound = false, exercise = exercise) } }
                .onFailure { error ->
                    _uiState.update { it.copy(isLoadingRound = false, errorMessage = error.message ?: "Couldn't load this exercise") }
                }
        }
    }

    /** The learner has to have listened at least once before answering — see [ListeningUiState.hasPlayedOnce]'s use in the screen's enabled state. */
    fun onPlayed() = _uiState.update { it.copy(hasPlayedOnce = true) }

    /** Locks in an answer — selecting again after this does nothing, matching QuizViewModel's same rule so the reveal can't be gamed. */
    fun selectOption(index: Int) {
        val state = _uiState.value
        if (state.selectedOptionIndex != null || state.exercise == null) return
        val isCorrect = index == state.exercise.correctOptionIndex
        _uiState.update {
            it.copy(selectedOptionIndex = index, correctCount = it.correctCount + if (isCorrect) 1 else 0)
        }
    }

    fun nextRound() {
        val state = _uiState.value
        if (state.roundsCompleted + 1 >= LISTENING_SESSION_ROUNDS) {
            finishSession()
        } else {
            _uiState.update { it.copy(roundsCompleted = it.roundsCompleted + 1) }
            loadRound()
        }
    }

    private fun finishSession() {
        val state = _uiState.value
        val xpEarned = state.correctCount * LISTENING_XP_PER_CORRECT
        _uiState.update { it.copy(roundsCompleted = it.roundsCompleted + 1, isSessionComplete = true, xpEarned = xpEarned) }

        val uid = authRepository.currentUser?.uid ?: return
        if (xpEarned > 0) {
            viewModelScope.launch { userProfileRepository.addXp(uid, xpEarned) }
        }
    }
}
