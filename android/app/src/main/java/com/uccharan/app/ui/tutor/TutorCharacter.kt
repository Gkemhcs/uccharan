package com.uccharan.app.ui.tutor

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.graphics.drawscope.translate
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import kotlin.math.PI
import kotlin.math.sin

/**
 * A real animated tutor character, not a static image or emoji — a simple
 * flat-illustration figure drawn with Compose `Canvas` primitives (circles,
 * rounded rects, lines) with genuinely moving limbs: one arm swings through
 * a talking/explaining gesture, the other sways gently at rest, the head
 * tilts slowly, and the whole figure has a soft standing bounce. [role]
 * layers on a small drawn accessory (a driver's cap + steering wheel, an
 * apron, a stethoscope, a necktie, …) so the SAME recognizable character —
 * same face, same build, same core color — looks dressed for whatever
 * situation is being practiced, rather than becoming a different character
 * each time. That consistency is deliberate: this is the one tutor the
 * learner comes to recognize everywhere (onboarding, lesson feedback, a
 * passed quiz, Practice with your Tutor), not a new face per scene.
 *
 * Fully native — no image/GIF assets, no network call, so it can never fail
 * to load or add latency anywhere it's used. [animated] `= false` freezes
 * the figure mid-gesture for small/cheap placements (e.g. a tiny avatar next
 * to a chat bubble) where constant motion would be visual noise.
 */
@Composable
fun TutorCharacter(
    gender: TutorGender,
    modifier: Modifier = Modifier,
    role: TutorRole = TutorRole.TEACHER,
    avatarSize: Dp = 96.dp,
    animated: Boolean = true,
) {
    val infiniteTransition = rememberInfiniteTransition(label = "tutorCharacter")
    val phase by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = (2f * PI).toFloat(),
        animationSpec = infiniteRepeatable(tween(1700, easing = LinearEasing), RepeatMode.Restart),
        label = "tutorPhase",
    )
    val t = if (animated) phase else 0.6f // a fixed mid-gesture pose when frozen, not a dead T-pose

    Canvas(modifier = modifier.size(avatarSize)) {
        val w = size.width
        val h = size.height
        val cx = w / 2f
        val bounceOffset = sin(t) * h * 0.015f

        translate(top = bounceOffset) {
            val skin = Color(0xFFF0C29A)
            val hair = Color(0xFF33221A)
            val outfit = Color(0xFF146C6B) // app teal — one consistent identity across every role
            val accent = Color(0xFF7FDAD5)

            val headCenter = Offset(cx, h * 0.22f)
            val headRadius = w * 0.14f
            val shoulderY = h * 0.38f
            val leftShoulder = Offset(cx - w * 0.15f, shoulderY)
            val rightShoulder = Offset(cx + w * 0.15f, shoulderY)
            val hipY = h * 0.68f
            val leftHip = Offset(cx - w * 0.08f, hipY)
            val rightHip = Offset(cx + w * 0.08f, hipY)

            // Legs: standing, a very small weight-shift sway (opposite phase per leg).
            val legSway = sin(t + PI.toFloat()) * 3f
            rotate(legSway, pivot = leftHip) {
                drawLine(outfit, leftHip, Offset(leftHip.x - w * 0.02f, h * 0.95f), strokeWidth = w * 0.07f, cap = StrokeCap.Round)
            }
            rotate(-legSway, pivot = rightHip) {
                drawLine(outfit, rightHip, Offset(rightHip.x + w * 0.02f, h * 0.95f), strokeWidth = w * 0.07f, cap = StrokeCap.Round)
            }

            // Torso.
            drawRoundRect(
                color = outfit,
                topLeft = Offset(cx - w * 0.17f, shoulderY - h * 0.02f),
                size = Size(w * 0.34f, hipY - shoulderY + h * 0.04f),
                cornerRadius = CornerRadius(w * 0.10f),
            )

            // Left arm: resting at the side, a gentle idle sway.
            val leftArmAngle = 14f + sin(t + PI.toFloat() / 2f) * 5f
            rotate(leftArmAngle, pivot = leftShoulder) {
                drawLine(skin, leftShoulder, Offset(leftShoulder.x, leftShoulder.y + h * 0.24f), strokeWidth = w * 0.045f, cap = StrokeCap.Round)
            }

            // Right arm: the "talking" gesture — swings through a real arc, not a static pose.
            val rightArmAngle = -70f + sin(t) * 35f
            rotate(rightArmAngle, pivot = rightShoulder) {
                drawLine(skin, rightShoulder, Offset(rightShoulder.x, rightShoulder.y + h * 0.24f), strokeWidth = w * 0.045f, cap = StrokeCap.Round)
            }

            // Head + hair (hairline length differs by gender — the only gender cue, kept simple on purpose).
            val headTilt = sin(t * 0.5f) * 4f
            rotate(headTilt, pivot = headCenter) {
                drawCircle(skin, radius = headRadius, center = headCenter)
                drawArc(
                    color = hair,
                    startAngle = 180f,
                    sweepAngle = 180f,
                    useCenter = true,
                    topLeft = Offset(headCenter.x - headRadius, headCenter.y - headRadius),
                    size = Size(headRadius * 2f, headRadius * 2f * if (gender == TutorGender.FEMALE) 0.9f else 0.6f),
                )
                if (gender == TutorGender.FEMALE) {
                    drawLine(
                        hair,
                        Offset(headCenter.x - headRadius * 0.9f, headCenter.y),
                        Offset(headCenter.x - headRadius * 0.9f, headCenter.y + headRadius * 0.9f),
                        strokeWidth = w * 0.03f,
                        cap = StrokeCap.Round,
                    )
                    drawLine(
                        hair,
                        Offset(headCenter.x + headRadius * 0.9f, headCenter.y),
                        Offset(headCenter.x + headRadius * 0.9f, headCenter.y + headRadius * 0.9f),
                        strokeWidth = w * 0.03f,
                        cap = StrokeCap.Round,
                    )
                }
            }

            drawRoleAccessory(role, cx, headCenter, headRadius, leftShoulder, rightShoulder, w, h, accent)
        }
    }
}

/** Draws a small, simple prop matching [role] — layered on top of the same base character, never redrawing it. */
private fun DrawScope.drawRoleAccessory(
    role: TutorRole,
    cx: Float,
    headCenter: Offset,
    headRadius: Float,
    leftShoulder: Offset,
    rightShoulder: Offset,
    w: Float,
    h: Float,
    accent: Color,
) {
    when (role) {
        TutorRole.AUTO -> {
            drawArc(
                color = Color(0xFF2E2E2E),
                startAngle = 180f,
                sweepAngle = 180f,
                useCenter = true,
                topLeft = Offset(headCenter.x - headRadius, headCenter.y - headRadius * 1.15f),
                size = Size(headRadius * 2f, headRadius * 1.1f),
            )
            drawCircle(accent, radius = w * 0.11f, center = Offset(cx, leftShoulder.y + h * 0.24f), style = Stroke(width = w * 0.02f))
        }
        TutorRole.RESTAURANT -> {
            drawRoundRect(
                color = Color(0xFFFFF3E0),
                topLeft = Offset(cx - w * 0.12f, leftShoulder.y + h * 0.02f),
                size = Size(w * 0.24f, h * 0.20f),
                cornerRadius = CornerRadius(w * 0.03f),
            )
        }
        TutorRole.MEDICAL -> {
            val neckY = headCenter.y + headRadius * 1.1f
            drawArc(
                color = Color(0xFFDDDDDD),
                startAngle = 0f,
                sweepAngle = 180f,
                useCenter = false,
                topLeft = Offset(cx - w * 0.09f, neckY),
                size = Size(w * 0.18f, w * 0.14f),
                style = Stroke(width = w * 0.02f),
            )
            drawCircle(Color(0xFFDDDDDD), radius = w * 0.025f, center = Offset(cx, neckY + w * 0.14f))
        }
        TutorRole.SHOP -> {
            drawRoundRect(
                color = accent,
                topLeft = Offset(leftShoulder.x - w * 0.06f, h * 0.55f),
                size = Size(w * 0.12f, w * 0.12f),
                cornerRadius = CornerRadius(w * 0.02f),
            )
        }
        TutorRole.DIRECTIONS -> {
            drawLine(Color(0xFF8D6E63), Offset(w * 0.86f, h * 0.40f), Offset(w * 0.86f, h * 0.85f), strokeWidth = w * 0.02f, cap = StrokeCap.Round)
            drawRoundRect(accent, topLeft = Offset(w * 0.80f, h * 0.36f), size = Size(w * 0.16f, w * 0.06f), cornerRadius = CornerRadius(w * 0.01f))
        }
        TutorRole.OFFICE -> {
            val tieTop = Offset(cx, leftShoulder.y + h * 0.02f)
            drawLine(Color(0xFF8E1B1B), tieTop, Offset(cx, tieTop.y + h * 0.16f), strokeWidth = w * 0.025f, cap = StrokeCap.Round)
        }
        TutorRole.HOME -> {
            val roofTop = Offset(w * 0.88f, h * 0.30f)
            val roofPath = Path().apply {
                moveTo(roofTop.x - w * 0.10f, roofTop.y + w * 0.08f)
                lineTo(roofTop.x, roofTop.y)
                lineTo(roofTop.x + w * 0.10f, roofTop.y + w * 0.08f)
                close()
            }
            drawPath(roofPath, color = accent)
        }
        TutorRole.PHONE -> {
            drawRoundRect(
                color = Color(0xFF333333),
                topLeft = Offset(headCenter.x + headRadius * 0.7f, headCenter.y - w * 0.02f),
                size = Size(w * 0.06f, w * 0.11f),
                cornerRadius = CornerRadius(w * 0.015f),
            )
        }
        TutorRole.TRAVEL -> {
            drawRoundRect(
                color = accent,
                topLeft = Offset(rightShoulder.x - w * 0.02f, h * 0.72f),
                size = Size(w * 0.14f, w * 0.10f),
                cornerRadius = CornerRadius(w * 0.02f),
            )
        }
        TutorRole.TEACHER -> {
            drawRoundRect(
                color = Color(0xFF2E2E2E),
                topLeft = Offset(headCenter.x - headRadius * 0.9f, headCenter.y - headRadius * 1.3f),
                size = Size(headRadius * 1.8f, headRadius * 0.35f),
                cornerRadius = CornerRadius(headRadius * 0.08f),
            )
        }
    }
}
