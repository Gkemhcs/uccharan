package com.uccharan.app.ui.home

import com.uccharan.app.data.model.Lesson
import com.uccharan.app.data.roadmap.RoadmapDay
import com.uccharan.app.data.roadmap.RoadmapWeek
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class WeekPathItemsTest {

    private val week = RoadmapWeek(
        level = 1,
        weekNumber = 1,
        days = listOf(
            RoadmapDay(1, "Greetings", "foundations", "quiz-day-1"),
            RoadmapDay(2, "Family", "day-2-family", "quiz-day-2"),
            RoadmapDay(3, "Routine", "day-3-routine", "quiz-day-3"),
        ),
    )

    private val todaysLessons = listOf(
        Lesson(id = "l1", track = "day-2-family"),
        Lesson(id = "l2", track = "day-2-family"),
    )

    @Test
    fun `days before today collapse to a done marker, days after to a locked marker`() {
        val items = buildWeekPathItems(
            week = week,
            currentDay = week.days[1], // Day 2 is "today"
            todaysLessons = todaysLessons,
            completedLessonIds = emptySet(),
            isLessonLocked = { false },
            isQuizReady = false,
        )

        val day1Summary = items.filterIsInstance<PathItem.DaySummary>().first { it.day.day == 1 }
        assertTrue(day1Summary.isDone)

        val day3Summary = items.filterIsInstance<PathItem.DaySummary>().first { it.day.day == 3 }
        assertFalse(day3Summary.isDone)
    }

    @Test
    fun `today expands into its actual lessons, not a collapsed marker`() {
        val items = buildWeekPathItems(
            week = week,
            currentDay = week.days[1],
            todaysLessons = todaysLessons,
            completedLessonIds = setOf("l1"),
            isLessonLocked = { lesson -> lesson.id == "l2" },
            isQuizReady = false,
        )

        val lessonItems = items.filterIsInstance<PathItem.LessonItem>()
        assertEquals(2, lessonItems.size)
        assertTrue(lessonItems.first { it.lesson.id == "l1" }.isCompleted)
        assertTrue(lessonItems.first { it.lesson.id == "l2" }.isLocked)

        // No DaySummary entry for day 2 itself — it's expanded, not collapsed.
        assertTrue(items.filterIsInstance<PathItem.DaySummary>().none { it.day.day == 2 })
    }

    @Test
    fun `today's quiz item reflects readiness and carries the day theme`() {
        val readyItems = buildWeekPathItems(week, week.days[1], todaysLessons, emptySet(), { false }, isQuizReady = true)
        val quiz = readyItems.filterIsInstance<PathItem.QuizItem>().single()
        assertFalse(quiz.isLocked)
        assertEquals("quiz-day-2", quiz.quizId)
        assertEquals("Family Quiz", quiz.label)

        val notReadyItems = buildWeekPathItems(week, week.days[1], todaysLessons, emptySet(), { false }, isQuizReady = false)
        assertTrue(notReadyItems.filterIsInstance<PathItem.QuizItem>().single().isLocked)
    }

    @Test
    fun `items preserve the week's day order`() {
        val items = buildWeekPathItems(week, week.days[1], todaysLessons, emptySet(), { false }, isQuizReady = true)

        // Day 1 summary, then day 2's lessons+quiz, then day 3 summary — in that order.
        assertTrue(items.first() is PathItem.DaySummary)
        assertEquals(1, (items.first() as PathItem.DaySummary).day.day)
        assertTrue(items.last() is PathItem.DaySummary)
        assertEquals(3, (items.last() as PathItem.DaySummary).day.day)
    }

    @Test
    fun `a day with no quiz id contributes no quiz item`() {
        val weekWithoutQuiz = RoadmapWeek(1, 1, listOf(RoadmapDay(1, "No quiz yet", "day-1-track", quizId = null)))

        val items = buildWeekPathItems(weekWithoutQuiz, weekWithoutQuiz.days[0], emptyList(), emptySet(), { false }, isQuizReady = true)

        assertTrue(items.filterIsInstance<PathItem.QuizItem>().isEmpty())
    }
}
