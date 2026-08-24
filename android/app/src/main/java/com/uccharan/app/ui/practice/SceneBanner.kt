package com.uccharan.app.ui.practice

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.uccharan.app.ui.theme.LocalUccharanGradients
import com.uccharan.app.ui.tutor.TutorCharacter
import com.uccharan.app.ui.tutor.TutorGender
import com.uccharan.app.ui.tutor.TutorRole

/**
 * A themed "scene" for a practice topic: a real, colorful emoji as the main
 * scene identifier (🛺 for an auto-rickshaw fare, 🍽️ for a restaurant, …),
 * a simple illustrated backdrop drawn with Compose `Canvas` suggesting the
 * setting (a street with buildings, a table setting, shop shelves, …), and
 * the learner's small tutor character tucked in a corner — present and
 * animated, but not competing with the emoji as the main visual. Everything
 * here is native Compose drawing: no image/GIF assets, no backend call, no
 * per-session cost or loading delay. A real AI-generated scene image per
 * arbitrary situation remains a bigger, later upgrade (needs a backend
 * image-gen integration, storage, and cost) — this is the fast, free
 * version of the same idea.
 */
@Composable
fun SceneBanner(topic: String, tutorGender: TutorGender) {
    val role = remember(topic) { TutorRole.forTopic(topic) }
    val gradients = LocalUccharanGradients.current

    val infiniteTransition = rememberInfiniteTransition(label = "scene")
    // Drives the backdrop's parallax (buildings/clouds sliding by) for scenes
    // where that reads naturally — a cheap way to suggest a moving scene.
    val drift by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(tween(8000, easing = LinearEasing), RepeatMode.Restart),
        label = "drift",
    )

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp)
            .height(132.dp)
            .clip(RoundedCornerShape(20.dp))
            .background(gradients.primaryIcon),
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            drawSceneBackdrop(role, drift)
        }

        Column(
            modifier = Modifier.align(Alignment.CenterStart).padding(start = 20.dp, end = 74.dp),
        ) {
            Text(
                role.label.uppercase(),
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.85f),
            )
            Text(
                topic,
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onPrimary,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis,
            )
        }

        // The real emoji is the main scene identifier — large and prominent.
        Text(
            role.emoji,
            fontSize = 40.sp,
            modifier = Modifier.align(Alignment.TopEnd).padding(top = 12.dp, end = 16.dp),
        )

        // The tutor character is present and animated, but small and tucked in
        // a corner — a companion, not competing with the emoji for attention.
        TutorCharacter(
            gender = tutorGender,
            role = role,
            avatarSize = 44.dp,
            modifier = Modifier.align(Alignment.BottomEnd).padding(end = 14.dp, bottom = 6.dp),
        )
    }
}

/** Draws a simple illustrated backdrop suggesting [role]'s setting — plain geometric shapes, not a generated image. */
private fun DrawScope.drawSceneBackdrop(role: TutorRole, drift: Float) {
    val w = size.width
    val h = size.height
    val tint = Color.White.copy(alpha = 0.10f)
    val tintStrong = Color.White.copy(alpha = 0.16f)

    when (role) {
        TutorRole.AUTO, TutorRole.DIRECTIONS -> {
            // A street: a few building silhouettes drifting slowly by, a ground line, a dashed road.
            val groundY = h * 0.86f
            drawLine(tint, Offset(0f, groundY), Offset(w, groundY), strokeWidth = 2.dp.toPx())
            val buildingWidths = floatArrayOf(0.14f, 0.10f, 0.18f, 0.12f, 0.15f)
            var bx = -(drift * w * 0.6f).mod(w + 200f) - 100f
            buildingWidths.forEachIndexed { i, bw ->
                val bh = h * (0.28f + (i % 3) * 0.08f)
                drawRoundRect(tint, topLeft = Offset(bx, groundY - bh), size = Size(w * bw, bh), cornerRadius = CornerRadius(4.dp.toPx()))
                bx += w * bw + w * 0.05f
            }
            drawLine(
                tintStrong,
                Offset(0f, groundY + h * 0.05f),
                Offset(w, groundY + h * 0.05f),
                strokeWidth = 3.dp.toPx(),
                cap = StrokeCap.Round,
                pathEffect = PathEffect.dashPathEffect(floatArrayOf(14f, 12f), (drift * 26f).mod(26f)),
            )
        }
        TutorRole.RESTAURANT -> {
            // A table setting: a tabletop line, a plate, and a cup.
            val tableY = h * 0.78f
            drawLine(tint, Offset(w * 0.05f, tableY), Offset(w * 0.95f, tableY), strokeWidth = 4.dp.toPx(), cap = StrokeCap.Round)
            drawCircle(tint, radius = h * 0.14f, center = Offset(w * 0.30f, tableY - h * 0.16f), style = Stroke(width = 2.dp.toPx()))
            drawRoundRect(
                tint,
                topLeft = Offset(w * 0.58f, tableY - h * 0.30f),
                size = Size(w * 0.10f, h * 0.20f),
                cornerRadius = CornerRadius(4.dp.toPx()),
            )
        }
        TutorRole.MEDICAL -> {
            // A cross symbol and a shelf line.
            val cx = w * 0.20f
            val cy = h * 0.34f
            val armLen = h * 0.14f
            val armThickness = h * 0.05f
            drawRoundRect(tint, topLeft = Offset(cx - armThickness / 2, cy - armLen), size = Size(armThickness, armLen * 2), cornerRadius = CornerRadius(2.dp.toPx()))
            drawRoundRect(tint, topLeft = Offset(cx - armLen, cy - armThickness / 2), size = Size(armLen * 2, armThickness), cornerRadius = CornerRadius(2.dp.toPx()))
            drawLine(tint, Offset(0f, h * 0.88f), Offset(w, h * 0.88f), strokeWidth = 3.dp.toPx())
        }
        TutorRole.SHOP -> {
            // Shelves with a few small "products".
            listOf(0.55f, 0.75f).forEach { rowY ->
                drawLine(tint, Offset(w * 0.06f, h * rowY), Offset(w * 0.94f, h * rowY), strokeWidth = 3.dp.toPx())
                for (i in 0..4) {
                    val bx = w * (0.10f + i * 0.16f)
                    drawRoundRect(tint, topLeft = Offset(bx, h * rowY - h * 0.10f), size = Size(w * 0.08f, h * 0.10f), cornerRadius = CornerRadius(2.dp.toPx()))
                }
            }
        }
        TutorRole.OFFICE -> {
            // A window with blinds, and a desk line.
            drawRoundRect(tint, topLeft = Offset(w * 0.60f, h * 0.14f), size = Size(w * 0.30f, h * 0.34f), cornerRadius = CornerRadius(4.dp.toPx()), style = Stroke(width = 2.dp.toPx()))
            for (i in 1..3) {
                val ly = h * 0.14f + (h * 0.34f) * (i / 4f)
                drawLine(tint, Offset(w * 0.60f, ly), Offset(w * 0.90f, ly), strokeWidth = 1.5.dp.toPx())
            }
            drawLine(tintStrong, Offset(0f, h * 0.88f), Offset(w, h * 0.88f), strokeWidth = 3.dp.toPx())
        }
        TutorRole.HOME -> {
            // A little house silhouette.
            val baseX = w * 0.14f
            val baseY = h * 0.80f
            val roofWidth = w * 0.20f
            drawRoundRect(tint, topLeft = Offset(baseX, baseY - h * 0.20f), size = Size(roofWidth, h * 0.20f), cornerRadius = CornerRadius(2.dp.toPx()))
            drawLine(tint, Offset(baseX - w * 0.02f, baseY - h * 0.20f), Offset(baseX + roofWidth / 2, baseY - h * 0.34f), strokeWidth = 3.dp.toPx(), cap = StrokeCap.Round)
            drawLine(tint, Offset(baseX + roofWidth / 2, baseY - h * 0.34f), Offset(baseX + roofWidth + w * 0.02f, baseY - h * 0.20f), strokeWidth = 3.dp.toPx(), cap = StrokeCap.Round)
        }
        TutorRole.PHONE -> {
            // Signal arcs radiating from a corner.
            val cx = w * 0.18f
            val cy = h * 0.30f
            for (i in 1..3) {
                drawArc(
                    tint,
                    startAngle = -50f,
                    sweepAngle = 100f,
                    useCenter = false,
                    topLeft = Offset(cx - i * h * 0.11f, cy - i * h * 0.11f),
                    size = Size(i * h * 0.22f, i * h * 0.22f),
                    style = Stroke(width = 2.dp.toPx()),
                )
            }
        }
        TutorRole.TRAVEL -> {
            // Drifting clouds and a horizon line.
            val cloudY = h * 0.24f
            var cloudX = -(drift * w * 0.5f).mod(w + 160f) - 80f
            repeat(3) {
                drawCircle(tint, radius = h * 0.09f, center = Offset(cloudX, cloudY))
                drawCircle(tint, radius = h * 0.07f, center = Offset(cloudX + h * 0.10f, cloudY + h * 0.02f))
                cloudX += w * 0.4f
            }
            drawLine(tintStrong, Offset(0f, h * 0.88f), Offset(w, h * 0.88f), strokeWidth = 3.dp.toPx())
        }
        TutorRole.TEACHER -> {
            // A small chalkboard with a couple of "chalk lines".
            drawRoundRect(tint, topLeft = Offset(w * 0.62f, h * 0.16f), size = Size(w * 0.28f, h * 0.34f), cornerRadius = CornerRadius(4.dp.toPx()), style = Stroke(width = 2.dp.toPx()))
            drawLine(tint, Offset(w * 0.66f, h * 0.26f), Offset(w * 0.86f, h * 0.26f), strokeWidth = 1.5.dp.toPx())
            drawLine(tint, Offset(w * 0.66f, h * 0.33f), Offset(w * 0.80f, h * 0.33f), strokeWidth = 1.5.dp.toPx())
        }
    }
}
