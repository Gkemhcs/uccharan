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
    /**
     * [DayStatus.NOT_READY] is a day whose content hasn't been seeded yet
     * (track/quizId null) — shown, but not tappable.
     *
     * COMPLETED is checked before CURRENT deliberately: reviewing an
     * already-passed day repoints `currentTrack` to it the same way a
     * forward jump does (see [reviewDay]), so a day the learner just came
     * back to revise would otherwise flip from "done" to "you are here" —
     * making finished progress look lost even though `passedQuizIds` never
     * changed. Checking COMPLETED first keeps its checkmark no matter where
     * `currentTrack` currently points.
     */
    fun statusFor(day: RoadmapDay): DayStatus = when {
        day.track == null -> DayStatus.NOT_READY
        day.quizId != null && day.quizId in passedQuizIds -> DayStatus.COMPLETED
        day.track == currentTrack -> DayStatus.CURRENT
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

    /** Opens the confirmation dialog for a forward/skip-ahead jump onto a day not yet completed — a genuine position change (days in between won't be marked done), so it's confirmed, never a stray tap. Reviewing an already-completed day skips this entirely — see [reviewDay]. */
    fun requestJump(day: RoadmapDay) {
        if (day.track == null || day.track == _uiState.value.currentTrack) return
        _uiState.update { it.copy(pendingJumpDay = day) }
    }

    fun dismissJump() = _uiState.update { it.copy(pendingJumpDay = null) }

    fun confirmJump() {
        val track = _uiState.value.pendingJumpDay?.track
        performJump(track) { _uiState.update { it.copy(pendingJumpDay = null) } }
    }

    /**
     * Revisits an already-completed day immediately, with no confirmation
     * dialog — unlike [requestJump] this isn't a destructive position change:
     * `passedQuizIds` is untouched by simply being here, and retaking the
     * quiz to revise is now safe too (a lower score on a review attempt can
     * no longer erase the earlier pass — see [QuizRepository.recordAttempt]).
     */
    fun reviewDay(day: RoadmapDay) {
        performJump(day.track) {}
    }

    private fun performJump(track: String?, onSettled: () -> Unit) {
        val uid = authRepository.currentUser?.uid
        if (uid == null || track == null) {
            onSettled()
            return
        }
        _uiState.update { it.copy(isJumping = true) }
        viewModelScope.launch {
            userProfileRepository.advanceToTrack(uid, track)
                .onSuccess { _uiState.update { it.copy(isJumping = false, currentTrack = track) } }
                .onFailure { error ->
                    _uiState.update { it.copy(isJumping = false, errorMessage = error.message ?: "Couldn't open that day") }
                }
            onSettled()
        }
    }
}
