package com.uccharan.app.ui.profile

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.uccharan.app.data.model.LessonAttempt
import com.uccharan.app.data.model.UserProfile
import com.uccharan.app.data.repository.AuthRepository
import com.uccharan.app.data.repository.LessonRepository
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

/** One pronunciation sound the learner hasn't yet reliably gotten right — see [computeWeakSounds]. */
data class WeakSound(val sound: String, val attempts: Int, val correct: Int) {
    val accuracy: Double get() = if (attempts == 0) 0.0 else correct.toDouble() / attempts
}

data class ProfileUiState(
    val isLoading: Boolean = true,
    val profile: UserProfile? = null,
    val weekProgress: List<WeekProgress> = emptyList(),
    val quizHistory: List<QuizAttemptRecord> = emptyList(),
    val weakSounds: List<WeakSound> = emptyList(),
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
    private val lessonRepository: LessonRepository,
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
            val recentAttempts = lessonRepository.getRecentAttempts(uid).getOrNull().orEmpty()

            profileResult
                .onSuccess { profile ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            profile = profile,
                            weekProgress = ROADMAP_WEEKS.map { week -> weekProgressFor(week, passedQuizIds) },
                            quizHistory = quizHistory,
                            weakSounds = computeWeakSounds(recentAttempts),
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

/** A sound only surfaces as a weak point once there's enough signal to trust it — one unlucky attempt shouldn't label a sound "weak". */
private const val MIN_ATTEMPTS_TO_SURFACE = 2

/** Same 70% bar the rest of the app uses for "not yet mastered" (see [com.uccharan.app.data.repository.QUIZ_PASS_THRESHOLD]). */
private const val WEAK_SOUND_ACCURACY_THRESHOLD = 0.7

/**
 * Aggregates recent [LessonAttempt]s by their `focusSounds` into per-sound
 * accuracy, and returns the ones worth calling out — this is CURRICULUM.md
 * §7's "Phase 3 weak-point analytics", now actually surfaced: `focusSounds`
 * was authored into every lesson from day one but never read back until now.
 * Top-level (not a method) so it's testable against synthetic attempt lists,
 * independent of live Firestore data — same pattern as [weekProgressFor].
 */
internal fun computeWeakSounds(attempts: List<LessonAttempt>): List<WeakSound> {
    val bySound = mutableMapOf<String, Pair<Int, Int>>() // sound -> (attempts, correct)
    for (attempt in attempts) {
        for (sound in attempt.focusSounds) {
            val (attemptCount, correctCount) = bySound.getOrDefault(sound, 0 to 0)
            bySound[sound] = (attemptCount + 1) to (correctCount + if (attempt.isCorrect) 1 else 0)
        }
    }
    return bySound
        .map { (sound, counts) -> WeakSound(sound = sound, attempts = counts.first, correct = counts.second) }
        .filter { it.attempts >= MIN_ATTEMPTS_TO_SURFACE && it.accuracy < WEAK_SOUND_ACCURACY_THRESHOLD }
        .sortedBy { it.accuracy }
        .take(5)
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
