package com.uccharan.app.ui.practice

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.uccharan.app.data.repository.AuthRepository
import com.uccharan.app.data.repository.UserProfileRepository
import com.uccharan.app.data.roadmap.roadmapDayForTrack
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class PracticeTabUiState(
    val isLoading: Boolean = true,
    /** The theme label shown on the "today" card, e.g. "Family & People" — null if the learner's current day isn't loaded/authored yet. */
    val todayThemeLabel: String? = null,
    /** What actually gets sent as the practice topic — `practiceScenario` where curated, else the bare theme text. */
    val todayTopic: String? = null,
)

/**
 * Backs the Practice tab's "Today's Practice" card — a small, independent
 * fetch of the learner's current roadmap day (not shared with
 * [com.uccharan.app.ui.home.HomeViewModel]) so the two tabs stay decoupled:
 * switching tabs never risks stale state leaking between them, at the cost
 * of one extra cheap Firestore read the first time this tab is opened.
 */
class PracticeTabViewModel(
    private val authRepository: AuthRepository,
    private val userProfileRepository: UserProfileRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow(PracticeTabUiState())
    val uiState: StateFlow<PracticeTabUiState> = _uiState.asStateFlow()

    init {
        load()
    }

    fun load() {
        val uid = authRepository.currentUser?.uid
        if (uid == null) {
            _uiState.update { it.copy(isLoading = false) }
            return
        }
        _uiState.update { it.copy(isLoading = true) }
        viewModelScope.launch {
            val profile = userProfileRepository.getProfile(uid).getOrNull()
            val day = profile?.currentTrack?.let { roadmapDayForTrack(it) }
            _uiState.update {
                it.copy(
                    isLoading = false,
                    todayThemeLabel = day?.theme,
                    todayTopic = day?.practiceScenario ?: day?.theme,
                )
            }
        }
    }
}
