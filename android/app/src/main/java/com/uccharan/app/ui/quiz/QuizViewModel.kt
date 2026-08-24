package com.uccharan.app.ui.quiz

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.uccharan.app.data.model.Quiz
import com.uccharan.app.data.repository.AuthRepository
import com.uccharan.app.data.repository.QUIZ_PASS_THRESHOLD
import com.uccharan.app.data.repository.QuizRepository
import com.uccharan.app.data.repository.UserProfileRepository
import com.uccharan.app.data.roadmap.nextRoadmapDay
import com.uccharan.app.ui.tutor.TutorGender
import com.uccharan.app.ui.tutor.tutorGenderFromStorage
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class QuizUiState(
    val isLoading: Boolean = true,
    val quiz: Quiz? = null,
    val currentQuestionIndex: Int = 0,
    val selectedOptionIndex: Int? = null,
    val correctCount: Int = 0,
    val isFinished: Boolean = false,
    val passed: Boolean = false,
    val xpEarned: Int = 0,
    /** True when this pass wasn't the first — a revision retake of an already-passed quiz. No new XP is awarded and no day is newly unlocked, so the result screen should say so instead of repeating the first-pass copy. */
    val isReviewPass: Boolean = false,
    val tutorGender: TutorGender = TutorGender.FEMALE,
    val errorMessage: String? = null,
) {
    val isLastQuestion: Boolean
        get() = quiz != null && currentQuestionIndex == quiz.questions.lastIndex
}

class QuizViewModel(
    quizId: String,
    private val authRepository: AuthRepository,
    private val userProfileRepository: UserProfileRepository,
    private val quizRepository: QuizRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow(QuizUiState())
    val uiState: StateFlow<QuizUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            quizRepository.getQuiz(quizId)
                .onSuccess { quiz ->
                    if (quiz == null || quiz.questions.isEmpty()) {
                        _uiState.update { it.copy(isLoading = false, errorMessage = "This quiz isn't ready yet") }
                    } else {
                        _uiState.update { it.copy(isLoading = false, quiz = quiz) }
                    }
                }
                .onFailure { error ->
                    _uiState.update { it.copy(isLoading = false, errorMessage = error.message ?: "Couldn't load the quiz") }
                }

            // For the pass screen's tutor character — loads independently of the
            // quiz itself, so a slow/failed profile fetch never blocks the quiz.
            authRepository.currentUser?.uid?.let { uid ->
                userProfileRepository.getProfile(uid).getOrNull()?.let { profile ->
                    _uiState.update { it.copy(tutorGender = tutorGenderFromStorage(profile.tutorGender)) }
                }
            }
        }
    }

    /** Locks in an answer for the current question — selecting again after this does nothing, so the reveal can't be gamed. */
    fun selectOption(index: Int) {
        val state = _uiState.value
        if (state.selectedOptionIndex != null) return
        val question = state.quiz?.questions?.getOrNull(state.currentQuestionIndex) ?: return
        val tappedOption = question.options.getOrNull(index)
        val isCorrect = tappedOption?.isCorrect == true
        Log.d(
            "QuizViewModel",
            "selectOption: questionIndex=${state.currentQuestionIndex} tappedIndex=$index " +
                "tappedOption=${tappedOption?.text} tappedIsCorrect=${tappedOption?.isCorrect} " +
                "allOptions=${question.options.map { "${it.text}:${it.isCorrect}" }}",
        )
        _uiState.update {
            it.copy(selectedOptionIndex = index, correctCount = it.correctCount + if (isCorrect) 1 else 0)
        }
    }

    fun nextQuestion() {
        val state = _uiState.value
        if (state.isLastQuestion) {
            finish()
        } else {
            _uiState.update { it.copy(currentQuestionIndex = it.currentQuestionIndex + 1, selectedOptionIndex = null) }
        }
    }

    /**
     * A quiz can be retaken any number of times to revise — see
     * [QuizRepository.recordAttempt]. XP and next-day unlock must only ever
     * happen once per quiz though: without gating on `isFirstPass`, retaking
     * an already-passed quiz for practice would re-award XP every time, and
     * — worse — would push `currentTrack` forward to whatever comes after
     * THIS day, even if the learner is reviewing an old day while genuinely
     * further ahead, silently regressing their real position.
     */
    private fun finish() {
        val state = _uiState.value
        val quiz = state.quiz ?: return
        val totalCount = quiz.questions.size
        val passedThisAttempt = totalCount > 0 && state.correctCount.toDouble() / totalCount >= QUIZ_PASS_THRESHOLD
        val potentialXp = if (passedThisAttempt) quiz.xpReward else 0

        _uiState.update { it.copy(isFinished = true, passed = passedThisAttempt, xpEarned = 0, isReviewPass = false) }

        val uid = authRepository.currentUser?.uid ?: return
        viewModelScope.launch {
            quizRepository.recordAttempt(uid, quiz.id, quiz.title, state.correctCount, totalCount, potentialXp)
                .onSuccess { outcome ->
                    _uiState.update { it.copy(xpEarned = if (outcome.isFirstPass) potentialXp else 0, isReviewPass = passedThisAttempt && !outcome.isFirstPass) }
                    if (outcome.isFirstPass) {
                        if (potentialXp > 0) userProfileRepository.addXp(uid, potentialXp)
                        nextRoadmapDay(quiz.track)?.track?.let { nextTrack ->
                            userProfileRepository.advanceToTrack(uid, nextTrack)
                        }
                    }
                }
        }
    }
}
