package com.uccharan.app.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.uccharan.app.data.model.Lesson
import com.uccharan.app.data.repository.AuthRepository
import com.uccharan.app.data.repository.LessonRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class HomeUiState(
    val isLoading: Boolean = true,
    val lessons: List<Lesson> = emptyList(),
    val completedLessonIds: Set<String> = emptySet(),
    val errorMessage: String? = null,
)

class HomeViewModel(
    private val authRepository: AuthRepository,
    private val lessonRepository: LessonRepository,
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
            val lessonsResult = lessonRepository.getLessonsForTrack("foundations")
            val completedResult = uid?.let { lessonRepository.getCompletedLessonIds(it) }

            lessonsResult
                .onSuccess { lessons ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            lessons = lessons,
                            completedLessonIds = completedResult?.getOrNull().orEmpty(),
                        )
                    }
                }
                .onFailure { error ->
                    _uiState.update { it.copy(isLoading = false, errorMessage = error.message ?: "Couldn't load lessons") }
                }
        }
    }
}
