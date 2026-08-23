package com.uccharan.app.ui.lesson

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.uccharan.app.data.model.Lesson
import com.uccharan.app.data.model.LessonAttempt
import com.uccharan.app.data.remote.CorrectionApi
import com.uccharan.app.data.remote.CorrectionResult
import com.uccharan.app.data.repository.AuthRepository
import com.uccharan.app.data.repository.LessonRepository
import com.uccharan.app.data.repository.UserProfileRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class LessonUiState(
    val isLoadingLesson: Boolean = true,
    val lesson: Lesson? = null,
    val isListening: Boolean = false,
    val isCheckingAttempt: Boolean = false,
    val lastSpokenText: String? = null,
    val correctionResult: CorrectionResult? = null,
    val isLessonComplete: Boolean = false,
    val errorMessage: String? = null,
)

class LessonViewModel(
    private val lessonId: String,
    private val authRepository: AuthRepository,
    private val userProfileRepository: UserProfileRepository,
    private val lessonRepository: LessonRepository,
    private val correctionApi: CorrectionApi,
) : ViewModel() {

    private val _uiState = MutableStateFlow(LessonUiState())
    val uiState: StateFlow<LessonUiState> = _uiState.asStateFlow()

    private var nativeLanguage: String? = null
    private var preferredAddressTerm: String? = null

    init {
        viewModelScope.launch {
            authRepository.currentUser?.uid?.let { uid ->
                userProfileRepository.getProfile(uid).getOrNull()?.let { profile ->
                    nativeLanguage = profile.nativeLanguage
                    preferredAddressTerm = profile.preferredAddressTerm
                }
            }

            lessonRepository.getLesson(lessonId)
                .onSuccess { lesson -> _uiState.update { it.copy(isLoadingLesson = false, lesson = lesson) } }
                .onFailure { error ->
                    _uiState.update { it.copy(isLoadingLesson = false, errorMessage = error.message ?: "Couldn't load this lesson") }
                }
        }
    }

    fun onListeningStarted() = _uiState.update { it.copy(isListening = true, errorMessage = null) }

    fun onSpeechError(message: String) = _uiState.update { it.copy(isListening = false, errorMessage = message) }

    fun onSpeechRecognized(spokenText: String) {
        val lesson = _uiState.value.lesson ?: return
        _uiState.update {
            it.copy(isListening = false, isCheckingAttempt = true, lastSpokenText = spokenText, correctionResult = null, errorMessage = null)
        }
        viewModelScope.launch {
            correctionApi.correctAttempt(
                targetSentence = lesson.prompt.targetSentence,
                spokenText = spokenText,
                preferredAddressTerm = preferredAddressTerm,
                nativeLanguage = nativeLanguage,
            ).onSuccess { result ->
                _uiState.update { it.copy(isCheckingAttempt = false, correctionResult = result) }
                logAttemptAndMaybeComplete(lesson, spokenText, result)
            }.onFailure { error ->
                _uiState.update {
                    it.copy(isCheckingAttempt = false, errorMessage = error.message ?: "Couldn't reach the tutor — check your connection")
                }
            }
        }
    }

    fun retry() = _uiState.update { it.copy(correctionResult = null, lastSpokenText = null) }

    private fun logAttemptAndMaybeComplete(lesson: Lesson, spokenText: String, result: CorrectionResult) {
        val uid = authRepository.currentUser?.uid ?: return
        viewModelScope.launch {
            lessonRepository.logAttempt(
                uid,
                LessonAttempt(
                    lessonId = lesson.id,
                    targetSentence = lesson.prompt.targetSentence,
                    spokenText = spokenText,
                    isCorrect = result.isCorrect,
                    feedback = result.feedback,
                    nativeExplanation = result.nativeExplanation,
                ),
            )
            if (result.isCorrect) {
                lessonRepository.markLessonComplete(uid, lesson.id)
                userProfileRepository.addXp(uid, lesson.xpReward)
                _uiState.update { it.copy(isLessonComplete = true) }
            }
        }
    }
}
