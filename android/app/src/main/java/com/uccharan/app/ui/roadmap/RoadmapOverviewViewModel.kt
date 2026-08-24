package com.uccharan.app.ui.roadmap

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.uccharan.app.data.repository.AuthRepository
import com.uccharan.app.data.repository.QuizRepository
import com.uccharan.app.data.repository.UserProfileRepository
import com.uccharan.app.data.roadmap.RoadmapDay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

/** Where a single day stands relative to the learner's current position. */
enum class DayStatus { COMPLETED, CURRENT, AVAILABLE, NOT_READY }

data class RoadmapOverviewUiState(
    val isLoading: Boolean = true,
    val currentTrack: String? = null,
    val passedQuizIds: Set<String> = emptySet(),
    val pendingJumpDay: RoadmapDay? = null,
    val isJumping: Boolean = false,
    val errorMessage: String? = null,
) {
    /** [DayStatus.NOT_READY] is a day whose content hasn't been seeded yet (track/quizId null) — shown, but not tappable. */
    fun statusFor(day: RoadmapDay): DayStatus = when {
        day.track == null -> DayStatus.NOT_READY
        day.track == currentTrack -> DayStatus.CURRENT
        day.quizId != null && day.quizId in passedQuizIds -> DayStatus.COMPLETED
        else -> DayStatus.AVAILABLE
    }
}

/**
 * Backs the full-syllabus screen (CURRICULUM.md §8 "structured, not open-ended" —
 * every week/level shown up front, with a deliberate jump instead of an
 * open-ended free-explore mode). Jumping just repoints `currentTrack`
 * ([UserProfileRepository.advanceToTrack], the same call a passed quiz makes) —
 * it never fabricates completed-lesson/quiz records for days skipped past, so a
 * learner's history stays honest about what they actually did.
 */
class RoadmapOverviewViewModel(
    private val authRepository: AuthRepository,
    private val userProfileRepository: UserProfileRepository,
    private val quizRepository: QuizRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow(RoadmapOverviewUiState())
    val uiState: StateFlow<RoadmapOverviewUiState> = _uiState.asStateFlow()

    init {
        load()
    }

    fun load() {
        val uid = authRepository.currentUser?.uid
        if (uid == null) {
            _uiState.update { it.copy(isLoading = false, errorMessage = "Not signed in") }
            return
        }
        _uiState.update { it.copy(isLoading = true, errorMessage = null) }
        viewModelScope.launch {
            val profile = userProfileRepository.getProfile(uid).getOrNull()
            val passedQuizIds = quizRepository.getPassedQuizIds(uid).getOrNull().orEmpty()
            _uiState.update {
                it.copy(isLoading = false, currentTrack = profile?.currentTrack, passedQuizIds = passedQuizIds)
            }
        }
    }

    /** Opens the confirmation dialog — a jump is a deliberate action, never a stray tap. */
    fun requestJump(day: RoadmapDay) {
        if (day.track == null || day.track == _uiState.value.currentTrack) return
        _uiState.update { it.copy(pendingJumpDay = day) }
    }

    fun dismissJump() = _uiState.update { it.copy(pendingJumpDay = null) }

    fun confirmJump() {
        val uid = authRepository.currentUser?.uid
        val track = _uiState.value.pendingJumpDay?.track
        if (uid == null || track == null) {
            _uiState.update { it.copy(pendingJumpDay = null) }
            return
        }
        _uiState.update { it.copy(isJumping = true) }
        viewModelScope.launch {
            userProfileRepository.advanceToTrack(uid, track)
                .onSuccess {
                    _uiState.update { it.copy(isJumping = false, pendingJumpDay = null, currentTrack = track) }
                }
                .onFailure { error ->
                    _uiState.update { it.copy(isJumping = false, pendingJumpDay = null, errorMessage = error.message ?: "Couldn't jump to that day") }
                }
        }
    }
}
