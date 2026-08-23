package com.uccharan.app.ui.home

import com.google.firebase.auth.FirebaseUser
import com.uccharan.app.MainDispatcherRule
import com.uccharan.app.data.model.Lesson
import com.uccharan.app.data.repository.AuthRepository
import com.uccharan.app.data.repository.LessonRepository
import io.mockk.coEvery
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test

class HomeViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val authRepository = mockk<AuthRepository>()
    private val lessonRepository = mockk<LessonRepository>()

    @Test
    fun `loads lessons and marks completed ones`() = runTest {
        val user = mockk<FirebaseUser>()
        every { user.uid } returns "uid-1"
        every { authRepository.currentUser } returns user

        val lessons = listOf(
            Lesson(id = "l1", track = "foundations"),
            Lesson(id = "l2", track = "foundations"),
        )
        coEvery { lessonRepository.getLessonsForTrack("foundations") } returns Result.success(lessons)
        coEvery { lessonRepository.getCompletedLessonIds("uid-1") } returns Result.success(setOf("l1"))

        val viewModel = HomeViewModel(authRepository, lessonRepository)

        val state = viewModel.uiState.value
        assertFalse(state.isLoading)
        assertEquals(2, state.lessons.size)
        assertTrue("l1" in state.completedLessonIds)
        assertFalse("l2" in state.completedLessonIds)
    }

    @Test
    fun `surfaces an error message when lessons fail to load`() = runTest {
        every { authRepository.currentUser } returns null
        coEvery { lessonRepository.getLessonsForTrack("foundations") } returns Result.failure(RuntimeException("offline"))

        val viewModel = HomeViewModel(authRepository, lessonRepository)

        val state = viewModel.uiState.value
        assertFalse(state.isLoading)
        assertEquals("offline", state.errorMessage)
    }
}
