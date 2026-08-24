package com.uccharan.app.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.uccharan.app.data.model.Lesson
import com.uccharan.app.data.repository.AuthRepository
import com.uccharan.app.data.repository.LessonRepository
import com.uccharan.app.data.repository.QuizRepository
import com.uccharan.app.data.repository.UserProfileRepository
import com.uccharan.app.data.roadmap.RoadmapDay
import com.uccharan.app.data.roadmap.nextRoadmapDay
import com.uccharan.app.data.roadmap.roadmapDayForTrack
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class HomeUiState(
    val isLoading: Boolean = true,
    val day: RoadmapDay? = null,
    val lessons: List<Lesson> = emptyList(),
    val completedLessonIds: Set<String> = emptySet(),
    val errorMessage: String? = null,
    val showSkipConfirmation: Boolean = false,
    val isSkipping: Boolean = false,
    /** True once this day's quiz is passed but the next day's content isn't seeded yet. */
    val isBeyondAuthoredContent: Boolean = false,
) {
    /** Simple sequential unlock: a lesson is locked until the one before it (in curriculum order) is done. */
    fun isLocked(lesson: Lesson): Boolean {
        val index = lessons.indexOf(lesson)
        if (index <= 0) return false
        return lessons[index - 1].id !in completedLessonIds
    }

    /** Whether there's anything left in this track for "skip this section" to do. */
    val canSkipTrack: Boolean
        get() = lessons.any { it.id !in completedLessonIds }

    /** All of today's lessons are done — time for the day's quiz, if one is seeded. */
    val isReadyForQuiz: Boolean
        get() = !isBeyondAuthoredContent && lessons.isNotEmpty() && lessons.all { it.id in completedLessonIds } && day?.quizId != null
}

class HomeViewModel(
    private val authRepository: AuthRepository,
    private val userProfileRepository: UserProfileRepository,
    private val lessonRepository: LessonRepository,
    private val quizRepository: QuizRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        loadLessons()
    }

    fun loadLessons() {
        val uid = authRepository.currentUser?.uid
        _uiState.update { it.copy(isLoading = true, errorMessage = null) }
        viewModelScope.launch {
            val track = uid?.let { userProfileRepository.getProfile(it).getOrNull()?.currentTrack } ?: "foundations"
            val day = roadmapDayForTrack(track)

            if (day?.track == null) {
                _uiState.update { it.copy(isLoading = false, day = day, lessons = emptyList()) }
                return@launch
            }

            // If this day's quiz is already passed but there's no next day authored yet,
            // the learner is caught up — nothing to show but "more is coming soon".
            val hasNoNextContent = nextRoadmapDay(day.track)?.track == null
            val quizAlreadyPassed = if (uid != null && day.quizId != null && hasNoNextContent) {
                quizRepository.getPassedQuizIds(uid).getOrNull()?.contains(day.quizId) == true
            } else {
                false
            }

            if (quizAlreadyPassed) {
                _uiState.update { it.copy(isLoading = false, day = day, lessons = emptyList(), isBeyondAuthoredContent = true) }
                return@launch
            }

            val lessonsResult = lessonRepository.getLessonsForTrack(day.track)
            val completedResult = uid?.let { lessonRepository.getCompletedLessonIds(it) }

            lessonsResult
                .onSuccess { lessons ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            day = day,
                            lessons = lessons,
                            completedLessonIds = completedResult?.getOrNull().orEmpty(),
                            isBeyondAuthoredContent = false,
                        )
                    }
                }
                .onFailure { error ->
                    _uiState.update { it.copy(isLoading = false, errorMessage = error.message ?: "Couldn't load lessons") }
                }
        }
    }

    fun requestSkipTrack() = _uiState.update { it.copy(showSkipConfirmation = true) }

    fun dismissSkipConfirmation() = _uiState.update { it.copy(showSkipConfirmation = false) }

    /** Marks every remaining lesson in this day complete, so the learner moves straight to the quiz. */
    fun confirmSkipTrack() {
        val uid = authRepository.currentUser?.uid
        val remainingLessonIds = _uiState.value.lessons.map { it.id } - _uiState.value.completedLessonIds
        if (uid == null || remainingLessonIds.isEmpty()) {
            _uiState.update { it.copy(showSkipConfirmation = false) }
            return
        }
        _uiState.update { it.copy(showSkipConfirmation = false, isSkipping = true) }
        viewModelScope.launch {
            lessonRepository.markLessonsComplete(uid, remainingLessonIds)
                .onSuccess { loadLessons() }
                .onFailure { error ->
                    _uiState.update { it.copy(isSkipping = false, errorMessage = error.message ?: "Couldn't skip this section") }
                }
            _uiState.update { it.copy(isSkipping = false) }
        }
    }
}
