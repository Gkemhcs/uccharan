package com.uccharan.app.ui.home

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import com.uccharan.app.data.model.Lesson
import com.uccharan.app.di.LocalAppContainer
import com.uccharan.app.di.uccharanViewModel

@Composable
fun HomeScreen(onLessonClick: (String) -> Unit) {
    val container = LocalAppContainer.current
    val viewModel = uccharanViewModel { HomeViewModel(container.authRepository, container.lessonRepository) }
    val uiState by viewModel.uiState.collectAsState()

    Column(modifier = Modifier.fillMaxSize().padding(20.dp)) {
        Text("Foundations", style = MaterialTheme.typography.headlineSmall)
        Text(
            "Greetings & Introductions",
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.padding(top = 4.dp, bottom = 16.dp),
        )

        when {
            uiState.isLoading -> Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
            uiState.errorMessage != null -> Text(
                text = uiState.errorMessage ?: "",
                color = MaterialTheme.colorScheme.error,
            )
            uiState.lessons.isEmpty() -> Text(
                "No lessons yet — seed some into Firestore's `lessons` collection to get started.",
                style = MaterialTheme.typography.bodyMedium,
            )
            else -> LazyColumn {
                items(uiState.lessons, key = { it.id }) { lesson ->
                    LessonRow(
                        lesson = lesson,
                        isCompleted = lesson.id in uiState.completedLessonIds,
                        onClick = { onLessonClick(lesson.id) },
                    )
                }
            }
        }
    }
}

@Composable
private fun LessonRow(lesson: Lesson, isCompleted: Boolean, onClick: () -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 6.dp)
            .clip(RoundedCornerShape(16.dp))
            .background(MaterialTheme.colorScheme.surfaceVariant)
            .clickable(onClick = onClick)
            .padding(16.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            imageVector = if (isCompleted) Icons.Filled.CheckCircle else Icons.Filled.PlayArrow,
            contentDescription = null,
            tint = if (isCompleted) MaterialTheme.colorScheme.tertiary else MaterialTheme.colorScheme.primary,
        )
        Column(modifier = Modifier.padding(start = 16.dp)) {
            Text(lesson.prompt.targetSentence, style = MaterialTheme.typography.titleMedium)
            Text("${lesson.xpReward} XP", style = MaterialTheme.typography.bodySmall)
        }
    }
}
