package com.uccharan.app.ui.home

import com.uccharan.app.data.model.Lesson
import com.uccharan.app.data.roadmap.RoadmapDay
import com.uccharan.app.data.roadmap.RoadmapWeek

/** One node on Home's winding path — a single lesson/quiz for today, or a collapsed marker for another day in the week. */
sealed interface PathItem {
    data class LessonItem(val lesson: Lesson, val isCompleted: Boolean, val isLocked: Boolean) : PathItem
    data class QuizItem(val quizId: String, val label: String, val isLocked: Boolean) : PathItem
    data class DaySummary(val day: RoadmapDay, val isDone: Boolean) : PathItem
}

/**
 * Builds one continuous path spanning the learner's whole current WEEK, not
 * just today — addresses the "why can I only see today, not the roadmap"
 * feedback. Days before today in the week collapse to a single marker (their
 * quiz is provably already passed, since [com.uccharan.app.ui.home.HomeViewModel]
 * only ever advances `currentTrack` one day at a time — no extra lookup
 * needed); today expands into its actual lessons + quiz; days after today
 * show as locked markers. Kept as a plain function (not a composable) so the
 * day-inclusion logic is unit-testable on its own.
 */
fun buildWeekPathItems(
    week: RoadmapWeek,
    currentDay: RoadmapDay,
    todaysLessons: List<Lesson>,
    completedLessonIds: Set<String>,
    isLessonLocked: (Lesson) -> Boolean,
    isQuizReady: Boolean,
): List<PathItem> = week.days.flatMap { day ->
    when {
        day.day < currentDay.day -> listOf(PathItem.DaySummary(day, isDone = true))
        day.day > currentDay.day -> listOf(PathItem.DaySummary(day, isDone = false))
        else -> {
            val lessonItems = todaysLessons.map { lesson ->
                PathItem.LessonItem(lesson, isCompleted = lesson.id in completedLessonIds, isLocked = isLessonLocked(lesson))
            }
            val quizItem = day.quizId?.let { quizId ->
                listOf(PathItem.QuizItem(quizId, label = "${day.theme} Quiz", isLocked = !isQuizReady))
            }.orEmpty()
            lessonItems + quizItem
        }
    }
}
