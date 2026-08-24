package com.uccharan.app.ui.profile

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.uccharan.app.data.model.UserProfile
import com.uccharan.app.data.repository.AuthRepository
import com.uccharan.app.data.repository.QuizAttemptRecord
import com.uccharan.app.data.repository.QuizRepository
import com.uccharan.app.data.repository.UserProfileRepository
import com.uccharan.app.data.roadmap.ROADMAP_WEEKS
import com.uccharan.app.data.roadmap.RoadmapWeek
import com.uccharan.app.ui.tutor.TutorGender
import com.uccharan.app.ui.tutor.toStorageValue
import com.uccharan.app.ui.tutor.tutorGenderFromStorage
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

enum class WeekStatus { NOT_AVAILABLE, IN_PROGRESS, COMPLETE }

data class WeekProgress(
    val week: RoadmapWeek,
    val status: WeekStatus,
    val daysComplete: Int,
    val daysWithContent: Int,
)

data class ProfileUiState(
    val isLoading: Boolean = true,
    val profile: UserProfile? = null,
    val weekProgress: List<WeekProgress> = emptyList(),
    val quizHistory: List<QuizAttemptRecord> = emptyList(),
    val isEditingPreferences: Boolean = false,
    val draftLanguage: String? = null,
    val draftAddressTerm: String = "",
    val draftTutorGender: TutorGender = TutorGender.FEMALE,
    val isSaving: Boolean = false,
    val errorMessage: String? = null,
)

class ProfileViewModel(
    private val authRepository: AuthRepository,
    private val userProfileRepository: UserProfileRepository,
    private val quizRepository: QuizRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow(ProfileUiState())
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()

    init {
        loadProfile()
    }

    fun loadProfile() {
        val uid = authRepository.currentUser?.uid
        if (uid == null) {
            _uiState.update { it.copy(isLoading = false, errorMessage = "Not signed in") }
            return
        }
        _uiState.update { it.copy(isLoading = true, errorMessage = null) }
        viewModelScope.launch {
            val profileResult = userProfileRepository.getProfile(uid)
            val passedQuizIds = quizRepository.getPassedQuizIds(uid).getOrNull().orEmpty()
            val quizHistory = quizRepository.getAttemptHistory(uid).getOrNull().orEmpty()

            profileResult
                .onSuccess { profile ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            profile = profile,
                            weekProgress = ROADMAP_WEEKS.map { week -> weekProgressFor(week, passedQuizIds) },
                            quizHistory = quizHistory,
                        )
                    }
                }
                .onFailure { error ->
                    _uiState.update { it.copy(isLoading = false, errorMessage = error.message ?: "Couldn't load your profile") }
                }
        }
    }

    fun startEditingPreferences() {
        val profile = _uiState.value.profile ?: return
        _uiState.update {
            it.copy(
                isEditingPreferences = true,
                draftLanguage = profile.nativeLanguage,
                draftAddressTerm = profile.preferredAddressTerm.orEmpty(),
                draftTutorGender = tutorGenderFromStorage(profile.tutorGender),
            )
        }
    }

    fun cancelEditingPreferences() = _uiState.update { it.copy(isEditingPreferences = false) }

    fun onDraftLanguageChange(language: String?) = _uiState.update { it.copy(draftLanguage = language) }

    fun onDraftAddressTermChange(term: String) = _uiState.update { it.copy(draftAddressTerm = term) }

    fun onDraftTutorGenderChange(gender: TutorGender) = _uiState.update { it.copy(draftTutorGender = gender) }

    fun savePreferences() {
        val uid = authRepository.currentUser?.uid ?: return
        val state = _uiState.value
        _uiState.update { it.copy(isSaving = true, errorMessage = null) }
        viewModelScope.launch {
            userProfileRepository.updatePreferences(
                uid = uid,
                nativeLanguage = state.draftLanguage,
                preferredAddressTerm = state.draftAddressTerm.ifBlank { null },
                tutorGender = state.draftTutorGender.toStorageValue(),
            ).onSuccess {
                _uiState.update { it.copy(isSaving = false, isEditingPreferences = false) }
                loadProfile()
            }.onFailure { error ->
                _uiState.update { it.copy(isSaving = false, errorMessage = error.message ?: "Couldn't save your changes") }
            }
        }
    }

    fun signOut() = authRepository.signOut()
}

/** Top-level (not a method) so it's testable against synthetic weeks, independent of ROADMAP_WEEKS' live content state. */
internal fun weekProgressFor(week: RoadmapWeek, passedQuizIds: Set<String>): WeekProgress {
    val daysWithContent = week.days.count { it.quizId != null }
    val daysComplete = week.days.count { it.quizId != null && it.quizId in passedQuizIds }
    val status = when {
        daysWithContent == 0 -> WeekStatus.NOT_AVAILABLE
        daysComplete == daysWithContent -> WeekStatus.COMPLETE
        else -> WeekStatus.IN_PROGRESS
    }
    return WeekProgress(week, status, daysComplete, daysWithContent)
}
