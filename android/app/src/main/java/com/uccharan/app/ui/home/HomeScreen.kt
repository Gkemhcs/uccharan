package com.uccharan.app.ui.home

import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.automirrored.filled.Chat
import androidx.compose.material.icons.automirrored.filled.List
import androidx.compose.material.icons.filled.AccountCircle
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.outlined.Lock
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import com.uccharan.app.di.LocalAppContainer
import com.uccharan.app.di.uccharanViewModel
import com.uccharan.app.ui.theme.LocalUccharanGradients

@Composable
fun HomeScreen(
    onLessonClick: (String) -> Unit,
    onProfileClick: () -> Unit,
    onQuizClick: (String) -> Unit,
    onPracticeClick: (String) -> Unit,
    onRoadmapOverviewClick: () -> Unit,
    onPracticeScenarioPickerClick: () -> Unit,
) {
    val container = LocalAppContainer.current
    val viewModel = uccharanViewModel {
        HomeViewModel(container.authRepository, container.userProfileRepository, container.lessonRepository, container.quizRepository)
    }
    val uiState by viewModel.uiState.collectAsState()

    // HomeViewModel is scoped to this NavBackStackEntry, which stays alive
    // (just STARTED, not RESUMED) while a Lesson is pushed on top — so its
    // init{} loadLessons() doesn't refire on its own when we come back from
    // a completed lesson. Refresh explicitly on ON_RESUME instead.
    val lifecycleOwner = LocalLifecycleOwner.current
    val currentOnResume = rememberUpdatedState(viewModel::loadLessons)
    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_RESUME) currentOnResume.value()
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
    }

    Box(modifier = Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background)) {
        Box(
            modifier = Modifier
                .size(280.dp)
                .offset(x = (-100).dp, y = (-90).dp)
                .clip(CircleShape)
                .background(Brush.radialGradient(listOf(MaterialTheme.colorScheme.primary.copy(alpha = 0.08f), Color.Transparent))),
        )

        Column(modifier = Modifier.fillMaxSize()) {
            // Two separate rows, not one wide row sharing space with the icons: the
            // "Skip section" text button is long enough (two lines) that packing it
            // into the same row as both icon buttons overflowed the screen width on
            // a real device, pushing the roadmap and profile icons off-screen entirely
            // and making them untappable. Icons now get a dedicated, always-visible row.
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 24.dp).padding(top = 8.dp),
                horizontalArrangement = androidx.compose.foundation.layout.Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        uiState.day?.let { "DAY ${it.day} OF 90" } ?: "UCCHARAN",
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.primary,
                    )
                    Text(
                        uiState.day?.theme ?: "Loading…",
                        style = MaterialTheme.typography.headlineSmall,
                        color = MaterialTheme.colorScheme.onBackground,
                    )
                }

                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier.size(40.dp).clip(CircleShape).clickable(onClick = onRoadmapOverviewClick),
                        contentAlignment = Alignment.Center,
                    ) {
                        Icon(
                            Icons.AutoMirrored.Filled.List,
                            contentDescription = "Full roadmap — see every day, jump ahead",
                            tint = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.size(24.dp),
                        )
                    }
                    Box(
                        modifier = Modifier.size(40.dp).clip(CircleShape).clickable(onClick = onProfileClick),
                        contentAlignment = Alignment.Center,
                    ) {
                        Icon(
                            Icons.Filled.AccountCircle,
                            contentDescription = "Profile & settings",
                            tint = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.size(28.dp),
                        )
                    }
                }
            }

            if (uiState.canSkipTrack && !uiState.isLoading) {
                Row(modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp), horizontalArrangement = androidx.compose.foundation.layout.Arrangement.End) {
                    TextButton(onClick = viewModel::requestSkipTrack, enabled = !uiState.isSkipping) {
                        Text(
                            if (uiState.isSkipping) "Skipping…" else "Already know this? Skip section",
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.primary,
                        )
                    }
                }
            }
            Spacer(modifier = Modifier.height(12.dp))

            // Practice is always tied to today's topic — no free-pick menu, see PracticeConversationViewModel's doc.
            // `practiceScenario` gives Gemini a concrete real-world situation (e.g. "negotiate
            // an auto-rickshaw fare") instead of just the bare theme text, where one is curated.
            PracticeEntryCard(onClick = { uiState.day?.let { onPracticeClick(it.practiceScenario ?: it.theme) } })
            Row(modifier = Modifier.fillMaxWidth().padding(horizontal = 24.dp), horizontalArrangement = androidx.compose.foundation.layout.Arrangement.End) {
                Text(
                    "Or practice a different situation →",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.clickable(onClick = onPracticeScenarioPickerClick).padding(vertical = 6.dp),
                )
            }
            Spacer(modifier = Modifier.height(14.dp))

            if (uiState.showSkipConfirmation) {
                AlertDialog(
                    onDismissRequest = viewModel::dismissSkipConfirmation,
                    title = { Text("Skip ${uiState.day?.theme ?: "this section"}?") },
                    text = {
                        Text(
                            "This marks every remaining lesson in this section as done, so you can move straight " +
                                "on to what's next. You won't earn XP for skipped lessons, but you can always " +
                                "revisit them later.",
                        )
                    },
                    confirmButton = {
                        TextButton(onClick = viewModel::confirmSkipTrack) { Text("Skip section") }
                    },
                    dismissButton = {
                        TextButton(onClick = viewModel::dismissSkipConfirmation) { Text("Cancel") }
                    },
                )
            }

            when {
                uiState.isLoading -> Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator()
                }
                uiState.errorMessage != null -> Text(
                    text = uiState.errorMessage ?: "",
                    color = MaterialTheme.colorScheme.error,
                    modifier = Modifier.padding(horizontal = 24.dp),
                )
                uiState.isBeyondAuthoredContent -> Column(modifier = Modifier.padding(horizontal = 24.dp)) {
                    Text(
                        "🎉 You've completed every day we've built so far!",
                        style = MaterialTheme.typography.titleMedium,
                        color = MaterialTheme.colorScheme.onBackground,
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        "New days are added regularly — check back soon for more of the 30-day roadmap.",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                uiState.lessons.isEmpty() -> Text(
                    "No lessons yet — seed some into Firestore's `lessons` collection to get started.",
                    style = MaterialTheme.typography.bodyMedium,
                    modifier = Modifier.padding(horizontal = 24.dp),
                )
                else -> {
                    val completedCount = uiState.lessons.count { it.id in uiState.completedLessonIds }
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.fillMaxWidth().padding(horizontal = 24.dp).padding(bottom = 20.dp),
                    ) {
                        Box(
                            modifier = Modifier
                                .weight(1f)
                                .height(6.dp)
                                .clip(RoundedCornerShape(3.dp))
                                .background(MaterialTheme.colorScheme.outline),
                        ) {
                            val fraction = if (uiState.lessons.isEmpty()) 0f else completedCount.toFloat() / uiState.lessons.size
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth(fraction.coerceIn(0f, 1f))
                                    .height(6.dp)
                                    .clip(RoundedCornerShape(3.dp))
                                    .background(LocalUccharanGradients.current.primaryButton),
                            )
                        }
                        Spacer(modifier = Modifier.width(10.dp))
                        Text(
                            "$completedCount / ${uiState.lessons.size}",
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }

                    val day = uiState.day
                    val week = day?.let { com.uccharan.app.data.roadmap.weekContaining(it.day) }
                    Column(modifier = Modifier.fillMaxWidth().verticalScroll(rememberScrollState())) {
                        if (day != null && week != null) {
                            val items = buildWeekPathItems(
                                week = week,
                                currentDay = day,
                                todaysLessons = uiState.lessons,
                                completedLessonIds = uiState.completedLessonIds,
                                isLessonLocked = uiState::isLocked,
                                isQuizReady = uiState.isReadyForQuiz,
                            )
                            RoadmapPath(
                                items = items,
                                levelName = com.uccharan.app.data.roadmap.ROADMAP_LEVELS.firstOrNull { it.level == week.level }?.name.orEmpty(),
                                weekNumber = week.weekNumber,
                                onLessonClick = onLessonClick,
                                onQuizClick = onQuizClick,
                            )
                        }
                        Spacer(modifier = Modifier.height(32.dp))
                    }
                }
            }
        }
    }
}

@Composable
private fun PracticeEntryCard(onClick: () -> Unit) {
    val gradients = LocalUccharanGradients.current

    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 24.dp)
            .shadow(elevation = 12.dp, shape = RoundedCornerShape(18.dp), ambientColor = MaterialTheme.colorScheme.tertiary, spotColor = MaterialTheme.colorScheme.tertiary)
            .clip(RoundedCornerShape(18.dp))
            .background(gradients.amberBadge)
            .clickable(onClick = onClick)
            .padding(16.dp),
    ) {
        Box(
            modifier = Modifier
                .size(42.dp)
                .clip(CircleShape)
                .background(gradients.onAmberBadge.copy(alpha = 0.18f)),
            contentAlignment = Alignment.Center,
        ) {
            Icon(
                Icons.AutoMirrored.Filled.Chat,
                contentDescription = null,
                tint = gradients.onAmberBadge,
                modifier = Modifier.size(20.dp),
            )
        }
        Column(modifier = Modifier.weight(1f).padding(start = 14.dp)) {
            Text("Practice with your Tutor", style = MaterialTheme.typography.titleMedium, color = gradients.onAmberBadge)
            Text(
                "Have a real spoken conversation, anytime",
                style = MaterialTheme.typography.bodySmall,
                color = gradients.onAmberBadge,
            )
        }
        Icon(
            Icons.AutoMirrored.Filled.ArrowForward,
            contentDescription = null,
            tint = gradients.onAmberBadge,
            modifier = Modifier.size(16.dp),
        )
    }
}

// A Duolingo/ELSA-style winding path rather than a flat list — same node
// states (locked/active/completed) as before, just laid out as a snake so
// the day's shape (lessons building up to a capstone quiz) reads at a
// glance, closer to a route on a map than a checklist.
private val PATH_ROW_HEIGHT = 122.dp
private val PATH_NODE_SIZE = 58.dp
private val PATH_QUIZ_NODE_SIZE = 78.dp
private val PATH_DAY_SUMMARY_SIZE = 52.dp
private val PATH_AMPLITUDE = 96.dp

/** Duolingo-style snake: center, right, far-right, right, center, left, far-left, left, repeat. */
private fun pathBias(index: Int): Float {
    val pattern = floatArrayOf(0f, 0.55f, 1f, 0.55f, 0f, -0.55f, -1f, -0.55f)
    return pattern[index % pattern.size]
}

/** A handful of deterministic "sparkle" positions along the path for background texture — fixed per index, not random, so it's stable across recompositions. */
private fun sparkleOffsets(index: Int): List<Pair<Float, Float>> {
    val seed = (index * 2654435761L).toInt()
    return listOf(
        (((seed and 0xFF) / 255f) - 0.5f) to 0.3f,
        ((((seed shr 8) and 0xFF) / 255f) - 0.5f) to 0.75f,
    )
}

@Composable
private fun RoadmapPath(
    items: List<PathItem>,
    levelName: String,
    weekNumber: Int,
    onLessonClick: (String) -> Unit,
    onQuizClick: (String) -> Unit,
) {
    if (items.isEmpty()) return
    val density = LocalDensity.current
    val gradients = LocalUccharanGradients.current
    val lineColor = MaterialTheme.colorScheme.primary.copy(alpha = 0.35f)
    val sparkleColor = MaterialTheme.colorScheme.tertiary.copy(alpha = 0.28f)

    // The first actionable (not-yet-done, not-locked) lesson or quiz — day
    // summary markers are never "active", they're just context for the week.
    val activeIndex = items.indexOfFirst { item ->
        when (item) {
            is PathItem.LessonItem -> !item.isCompleted && !item.isLocked
            is PathItem.QuizItem -> !item.isLocked
            is PathItem.DaySummary -> false
        }
    }

    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier
            .padding(horizontal = 24.dp, vertical = 6.dp)
            .fillMaxWidth()
            .clip(RoundedCornerShape(16.dp))
            .background(gradients.primaryIcon)
            .padding(horizontal = 18.dp, vertical = 14.dp),
    ) {
        Box(
            modifier = Modifier.size(34.dp).clip(CircleShape).background(MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.2f)),
            contentAlignment = Alignment.Center,
        ) {
            Text("W$weekNumber", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onPrimary, fontWeight = FontWeight.Bold)
        }
        Column(modifier = Modifier.padding(start = 12.dp)) {
            Text("$levelName · WEEK $weekNumber".uppercase(), style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.85f))
            Text("Your path this week", style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.onPrimary)
        }
    }
    Spacer(modifier = Modifier.height(6.dp))

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(PATH_ROW_HEIGHT * items.size + 24.dp)
            .padding(horizontal = 24.dp),
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val centerX = size.width / 2f
            val rowHeightPx = with(density) { PATH_ROW_HEIGHT.toPx() }
            val amplitudePx = with(density) { PATH_AMPLITUDE.toPx() }
            val points = items.indices.map { i ->
                Offset(centerX + pathBias(i) * amplitudePx, rowHeightPx * i + rowHeightPx / 2f)
            }
            if (points.size > 1) {
                val path = Path().apply {
                    moveTo(points[0].x, points[0].y)
                    for (i in 1 until points.size) {
                        val prev = points[i - 1]
                        val curr = points[i]
                        val midY = (prev.y + curr.y) / 2f
                        cubicTo(prev.x, midY, curr.x, midY, curr.x, curr.y)
                    }
                }
                drawPath(
                    path = path,
                    color = lineColor,
                    style = Stroke(
                        width = with(density) { 5.dp.toPx() },
                        pathEffect = PathEffect.dashPathEffect(floatArrayOf(with(density) { 3.dp.toPx() }, with(density) { 12.dp.toPx() })),
                    ),
                )
            }
            // Faint scattered dots behind the path — pure texture, breaks up the empty background.
            items.indices.forEach { i ->
                val rowTop = rowHeightPx * i
                sparkleOffsets(i).forEach { (xBias, yFraction) ->
                    drawCircle(
                        color = sparkleColor,
                        radius = with(density) { 3.dp.toPx() },
                        center = Offset(centerX + xBias * amplitudePx * 2.2f, rowTop + yFraction * rowHeightPx),
                    )
                }
            }
        }

        items.forEachIndexed { index, item ->
            when (item) {
                is PathItem.LessonItem -> PathNode(
                    index = index,
                    label = item.lesson.prompt.targetSentence,
                    isCompleted = item.isCompleted,
                    isLocked = item.isLocked,
                    isActive = index == activeIndex,
                    size = PATH_NODE_SIZE,
                    onClick = { onLessonClick(item.lesson.id) },
                )
                is PathItem.QuizItem -> PathNode(
                    index = index,
                    label = item.label,
                    isCompleted = false,
                    isLocked = item.isLocked,
                    isActive = index == activeIndex,
                    size = PATH_QUIZ_NODE_SIZE,
                    isQuiz = true,
                    onClick = { onQuizClick(item.quizId) },
                )
                is PathItem.DaySummary -> DaySummaryNode(index = index, day = item.day, isDone = item.isDone)
            }
        }
    }
}

@Composable
private fun androidx.compose.foundation.layout.BoxScope.PathNode(
    index: Int,
    label: String,
    isCompleted: Boolean,
    isLocked: Boolean,
    isActive: Boolean,
    size: androidx.compose.ui.unit.Dp,
    onClick: () -> Unit,
    isQuiz: Boolean = false,
) {
    val gradients = LocalUccharanGradients.current
    val bias = pathBias(index)
    val topOffset = PATH_ROW_HEIGHT * index + (PATH_ROW_HEIGHT - size) / 2f - 4.dp

    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier
            .align(Alignment.TopCenter)
            .offset(x = PATH_AMPLITUDE * bias, y = topOffset)
            .width(132.dp),
    ) {
        if (isActive) {
            PulsingStartBubble(text = if (isQuiz) "QUIZ" else "START")
            Spacer(modifier = Modifier.height(6.dp))
        }

        Box(contentAlignment = Alignment.Center, modifier = Modifier.align(Alignment.CenterHorizontally)) {
            // A soft halo ring behind completed/active nodes — a plain flat
            // circle reads flat; this gives it a little glow/polish.
            if (isCompleted || isActive) {
                Box(
                    modifier = Modifier
                        .size(size + 14.dp)
                        .clip(CircleShape)
                        .background((if (isQuiz) MaterialTheme.colorScheme.tertiary else MaterialTheme.colorScheme.primary).copy(alpha = 0.14f)),
                )
            }

            val nodeModifier = Modifier
                .size(size)
                .let { base ->
                    if (!isLocked) {
                        val glow = if (isQuiz) MaterialTheme.colorScheme.tertiary else MaterialTheme.colorScheme.primary
                        base.shadow(elevation = 12.dp, shape = CircleShape, ambientColor = glow, spotColor = glow)
                    } else {
                        base
                    }
                }
                .clip(CircleShape)
                .background(
                    when {
                        isCompleted -> gradients.primaryIcon
                        isLocked -> SolidColor(MaterialTheme.colorScheme.surfaceVariant)
                        isQuiz -> gradients.amberBadge
                        else -> gradients.primaryIcon
                    },
                )
                .clickable(enabled = !isLocked, onClick = onClick)

            Box(modifier = nodeModifier, contentAlignment = Alignment.Center) {
                when {
                    isCompleted -> Icon(Icons.Filled.CheckCircle, contentDescription = "Completed", tint = MaterialTheme.colorScheme.onPrimary, modifier = Modifier.size(size * 0.4f))
                    isLocked -> Icon(Icons.Outlined.Lock, contentDescription = "Locked", tint = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.size(size * 0.3f))
                    isQuiz -> Icon(Icons.Filled.Star, contentDescription = "Quiz", tint = gradients.onAmberBadge, modifier = Modifier.size(size * 0.4f))
                    else -> Icon(Icons.Filled.PlayArrow, contentDescription = "Start lesson", tint = MaterialTheme.colorScheme.onPrimary, modifier = Modifier.size(size * 0.35f))
                }
            }
        }

        Spacer(modifier = Modifier.height(7.dp))
        Text(
            label,
            style = if (isActive) MaterialTheme.typography.bodyMedium else MaterialTheme.typography.bodySmall,
            fontWeight = if (isActive) FontWeight.Bold else FontWeight.Normal,
            textAlign = TextAlign.Center,
            maxLines = if (isActive) 3 else 2,
            overflow = TextOverflow.Ellipsis,
            color = when {
                isLocked -> MaterialTheme.colorScheme.onSurfaceVariant
                isActive -> MaterialTheme.colorScheme.onBackground
                else -> MaterialTheme.colorScheme.onSurfaceVariant
            },
        )
    }
}

/** A day marker before/after today — visually distinct (amber "milestone" tint, short label) from the circular lesson/quiz nodes so a whole week's shape reads at a glance, not just a wall of identical checkmarks. */
@Composable
private fun androidx.compose.foundation.layout.BoxScope.DaySummaryNode(index: Int, day: com.uccharan.app.data.roadmap.RoadmapDay, isDone: Boolean) {
    val gradients = LocalUccharanGradients.current
    val bias = pathBias(index)
    val topOffset = PATH_ROW_HEIGHT * index + (PATH_ROW_HEIGHT - PATH_DAY_SUMMARY_SIZE) / 2f - 4.dp

    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier
            .align(Alignment.TopCenter)
            .offset(x = PATH_AMPLITUDE * bias, y = topOffset)
            .width(120.dp),
    ) {
        Box(
            modifier = Modifier
                .size(PATH_DAY_SUMMARY_SIZE)
                .clip(CircleShape)
                .background(if (isDone) gradients.amberBadge else SolidColor(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.6f))),
            contentAlignment = Alignment.Center,
        ) {
            if (isDone) {
                Icon(Icons.Filled.CheckCircle, contentDescription = "Day ${day.day} complete", tint = gradients.onAmberBadge, modifier = Modifier.size(20.dp))
            } else {
                Icon(Icons.Outlined.Lock, contentDescription = "Day ${day.day} locked", tint = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.size(15.dp))
            }
        }
        Spacer(modifier = Modifier.height(6.dp))
        Text(
            "Day ${day.day}",
            style = MaterialTheme.typography.labelSmall,
            fontWeight = FontWeight.Bold,
            color = if (isDone) MaterialTheme.colorScheme.tertiary else MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

/** A small "you are here" bubble with a gentle up-down pulse, above the next thing to do. */
@Composable
private fun PulsingStartBubble(text: String) {
    val gradients = LocalUccharanGradients.current
    val transition = rememberInfiniteTransition(label = "start-bubble")
    val offsetY by transition.animateFloat(
        initialValue = 0f,
        targetValue = -6f,
        animationSpec = infiniteRepeatable(
            animation = tween(700, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse,
        ),
        label = "start-bubble-offset",
    )
    Box(
        modifier = Modifier
            .offset(y = offsetY.dp)
            .clip(RoundedCornerShape(10.dp))
            .background(gradients.primaryButton)
            .padding(horizontal = 10.dp, vertical = 5.dp),
    ) {
        Text(text, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onPrimary)
    }
}
