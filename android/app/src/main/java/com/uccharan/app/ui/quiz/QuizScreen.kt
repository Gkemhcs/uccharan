package com.uccharan.app.ui.quiz

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.LinearOutSlowInEasing
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.uccharan.app.di.LocalAppContainer
import com.uccharan.app.di.uccharanViewModel
import com.uccharan.app.ui.theme.LocalUccharanGradients
import com.uccharan.app.ui.tutor.TutorCharacter
import kotlin.math.cos
import kotlin.math.sin

@Composable
fun QuizScreen(quizId: String, onFinished: () -> Unit) {
    val container = LocalAppContainer.current
    val viewModel = uccharanViewModel {
        QuizViewModel(quizId, container.authRepository, container.userProfileRepository, container.quizRepository)
    }
    val uiState by viewModel.uiState.collectAsState()
    val gradients = LocalUccharanGradients.current

    Column(modifier = Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background)) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp).padding(top = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Box(
                modifier = Modifier.size(44.dp).clip(CircleShape).clickable(onClick = onFinished),
                contentAlignment = Alignment.Center,
            ) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
            }
            uiState.quiz?.let { quiz ->
                Text(quiz.title, style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }

        when {
            uiState.isLoading -> Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { CircularProgressIndicator() }
            uiState.errorMessage != null && uiState.quiz == null -> Text(
                uiState.errorMessage ?: "",
                color = MaterialTheme.colorScheme.error,
                modifier = Modifier.padding(24.dp),
            )
            uiState.isFinished -> QuizResult(uiState = uiState, onContinue = onFinished)
            else -> uiState.quiz?.let { quiz -> QuizQuestionBody(uiState = uiState, quiz = quiz, viewModel = viewModel, gradients = gradients) }
        }
    }
}

@Composable
private fun QuizQuestionBody(
    uiState: QuizUiState,
    quiz: com.uccharan.app.data.model.Quiz,
    viewModel: QuizViewModel,
    gradients: com.uccharan.app.ui.theme.UccharanGradients,
) {
    val question = quiz.questions[uiState.currentQuestionIndex]

    Column(modifier = Modifier.padding(horizontal = 24.dp).padding(top = 12.dp)) {
        LinearProgressIndicator(
            progress = { (uiState.currentQuestionIndex + 1).toFloat() / quiz.questions.size },
            modifier = Modifier.fillMaxWidth().height(6.dp).clip(RoundedCornerShape(3.dp)),
            trackColor = MaterialTheme.colorScheme.outline,
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            "Question ${uiState.currentQuestionIndex + 1} of ${quiz.questions.size}",
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Spacer(modifier = Modifier.height(18.dp))
        Text(question.question, style = MaterialTheme.typography.titleLarge, color = MaterialTheme.colorScheme.onBackground)
        Spacer(modifier = Modifier.height(22.dp))

        question.options.forEachIndexed { index, option ->
            QuizOptionRow(
                text = option.text,
                state = when {
                    uiState.selectedOptionIndex == null -> OptionRowState.IDLE
                    option.isCorrect -> OptionRowState.CORRECT
                    index == uiState.selectedOptionIndex -> OptionRowState.WRONG_SELECTED
                    else -> OptionRowState.DIMMED
                },
                onClick = { viewModel.selectOption(index) },
            )
            Spacer(modifier = Modifier.height(10.dp))
        }

        if (uiState.selectedOptionIndex != null && question.explanation.isNotBlank()) {
            Spacer(modifier = Modifier.height(4.dp))
            Text(question.explanation, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }

        Spacer(modifier = Modifier.weight(1f))

        if (uiState.selectedOptionIndex != null) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 32.dp)
                    .shadow(elevation = 14.dp, shape = RoundedCornerShape(16.dp), ambientColor = MaterialTheme.colorScheme.primary, spotColor = MaterialTheme.colorScheme.primary)
                    .clip(RoundedCornerShape(16.dp))
                    .background(gradients.primaryButton)
                    .clickable(onClick = viewModel::nextQuestion)
                    .padding(vertical = 17.dp),
                contentAlignment = Alignment.Center,
            ) {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(
                        if (uiState.isLastQuestion) "See results" else "Next question",
                        style = MaterialTheme.typography.labelLarge,
                        color = MaterialTheme.colorScheme.onPrimary,
                    )
                    Icon(Icons.AutoMirrored.Filled.ArrowForward, contentDescription = null, tint = MaterialTheme.colorScheme.onPrimary, modifier = Modifier.size(16.dp))
                }
            }
        } else {
            Spacer(modifier = Modifier.height(80.dp))
        }
    }
}

private enum class OptionRowState { IDLE, CORRECT, WRONG_SELECTED, DIMMED }

@Composable
private fun QuizOptionRow(text: String, state: OptionRowState, onClick: () -> Unit) {
    val containerColor = when (state) {
        OptionRowState.IDLE -> MaterialTheme.colorScheme.surface
        OptionRowState.CORRECT -> MaterialTheme.colorScheme.tertiaryContainer
        OptionRowState.WRONG_SELECTED -> MaterialTheme.colorScheme.errorContainer
        OptionRowState.DIMMED -> MaterialTheme.colorScheme.surface
    }
    val contentColor = when (state) {
        OptionRowState.IDLE -> MaterialTheme.colorScheme.onSurface
        OptionRowState.CORRECT -> MaterialTheme.colorScheme.onTertiaryContainer
        OptionRowState.WRONG_SELECTED -> MaterialTheme.colorScheme.onErrorContainer
        OptionRowState.DIMMED -> MaterialTheme.colorScheme.onSurfaceVariant
    }

    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(14.dp))
            .background(containerColor)
            .clickable(enabled = state == OptionRowState.IDLE, onClick = onClick)
            .padding(horizontal = 16.dp, vertical = 15.dp),
    ) {
        Text(text, style = MaterialTheme.typography.bodyLarge, color = contentColor, modifier = Modifier.weight(1f))
        if (state == OptionRowState.CORRECT) {
            Icon(Icons.Filled.Check, contentDescription = "Correct", tint = contentColor, modifier = Modifier.size(18.dp))
        } else if (state == OptionRowState.WRONG_SELECTED) {
            Icon(Icons.Filled.Close, contentDescription = "Incorrect", tint = contentColor, modifier = Modifier.size(18.dp))
        }
    }
}

/** The moment of truth: a bouncy scale-in, confetti on a pass, a short shake on a fail — the quiz's one "achievement beat". */
@Composable
private fun ResultBadge(passed: Boolean) {
    val gradients = LocalUccharanGradients.current
    val scale = remember { Animatable(0f) }
    val shakeX = remember { Animatable(0f) }

    LaunchedEffect(passed) {
        scale.animateTo(1f, animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy, stiffness = Spring.StiffnessLow))
        if (!passed) {
            repeat(3) {
                shakeX.animateTo(8f, tween(60))
                shakeX.animateTo(-8f, tween(60))
            }
            shakeX.animateTo(0f, tween(60))
        }
    }

    Box(contentAlignment = Alignment.Center) {
        if (passed) ConfettiBurst()
        Box(
            modifier = Modifier
                .size(88.dp)
                .offset(x = shakeX.value.dp)
                .graphicsLayer { scaleX = scale.value; scaleY = scale.value }
                .clip(CircleShape)
                .background(if (passed) gradients.primaryIcon else androidx.compose.ui.graphics.SolidColor(MaterialTheme.colorScheme.surfaceVariant)),
            contentAlignment = Alignment.Center,
        ) {
            Icon(
                if (passed) Icons.Filled.Star else Icons.Filled.Close,
                contentDescription = null,
                tint = if (passed) MaterialTheme.colorScheme.onPrimary else MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.size(38.dp),
            )
        }
    }
}

/** A handful of particles bursting outward and fading — plays once behind a passed [ResultBadge]. */
@Composable
private fun ConfettiBurst() {
    val progress = remember { Animatable(0f) }
    LaunchedEffect(Unit) { progress.animateTo(1f, animationSpec = tween(900, easing = LinearOutSlowInEasing)) }

    val colors = listOf(
        MaterialTheme.colorScheme.tertiary,
        MaterialTheme.colorScheme.primary,
        MaterialTheme.colorScheme.secondary,
        MaterialTheme.colorScheme.error,
    )
    Canvas(modifier = Modifier.size(180.dp)) {
        val center = Offset(size.width / 2f, size.height / 2f)
        val maxRadius = size.minDimension / 2f
        val particleCount = 10
        repeat(particleCount) { i ->
            val angle = (i * (360f / particleCount)) * (Math.PI / 180f).toFloat()
            val radius = maxRadius * progress.value
            val x = center.x + radius * cos(angle)
            val y = center.y + radius * sin(angle)
            val alpha = (1f - progress.value).coerceIn(0f, 1f)
            drawCircle(color = colors[i % colors.size].copy(alpha = alpha), radius = 5.dp.toPx(), center = Offset(x, y))
        }
    }
}

@Composable
private fun QuizResult(uiState: QuizUiState, onContinue: () -> Unit) {
    val gradients = LocalUccharanGradients.current
    val quiz = uiState.quiz
    val total = quiz?.questions?.size ?: 0

    Column(
        modifier = Modifier.fillMaxSize().padding(horizontal = 24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Spacer(modifier = Modifier.weight(1f))
        ResultBadge(passed = uiState.passed)
        Spacer(modifier = Modifier.height(20.dp))
        Text(
            if (uiState.passed) "Quiz passed!" else "Not quite there yet",
            style = MaterialTheme.typography.headlineSmall,
            color = MaterialTheme.colorScheme.onBackground,
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            "You got ${uiState.correctCount} out of $total right.",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        if (uiState.passed) {
            Spacer(modifier = Modifier.height(6.dp))
            Text(
                "+${uiState.xpEarned} XP — next day unlocked!",
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.tertiary,
            )
            Spacer(modifier = Modifier.height(16.dp))
            TutorCharacter(gender = uiState.tutorGender, avatarSize = 64.dp)
        } else {
            Spacer(modifier = Modifier.height(6.dp))
            Text(
                "Review this week's lessons and try again — you need 70% to move on.",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        Spacer(modifier = Modifier.weight(1f))

        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 32.dp)
                .shadow(elevation = 14.dp, shape = RoundedCornerShape(16.dp), ambientColor = MaterialTheme.colorScheme.primary, spotColor = MaterialTheme.colorScheme.primary)
                .clip(RoundedCornerShape(16.dp))
                .background(gradients.primaryButton)
                .clickable(onClick = onContinue)
                .padding(vertical = 17.dp),
            contentAlignment = Alignment.Center,
        ) {
            Text("Continue", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.onPrimary)
        }
    }
}
