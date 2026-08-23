package com.uccharan.app.ui.theme

import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color

/**
 * Design tokens Material3's ColorScheme doesn't model — gradient fills for
 * the primary button/icon treatment, the amber celebration badge, and the
 * listening-state mic. Kept small and literal (matching the design canvas'
 * exact stops) rather than derived at runtime, so light/dark stay
 * intentional rather than algorithmically guessed.
 */
data class UccharanGradients(
    val primaryButton: Brush,
    val primaryIcon: Brush,
    val amberBadge: Brush,
    val listening: Brush,
)

private val LightGradients = UccharanGradients(
    primaryButton = Brush.linearGradient(listOf(Color(0xFF1B7D7A), Color(0xFF146C6B), Color(0xFF0E4B49))),
    primaryIcon = Brush.linearGradient(listOf(Color(0xFF1B7D7A), Color(0xFF0E4B49))),
    amberBadge = Brush.linearGradient(listOf(Color(0xFFFFE7BE), Color(0xFFFFD79A))),
    listening = Brush.linearGradient(listOf(Color(0xFFD96257), Color(0xFFC8524A), Color(0xFF9E362F))),
)

private val DarkGradients = UccharanGradients(
    primaryButton = Brush.linearGradient(listOf(Color(0xFF8FE3DE), Color(0xFF7FDAD5), Color(0xFF4AA8A2))),
    primaryIcon = Brush.linearGradient(listOf(Color(0xFF8FE3DE), Color(0xFF5FC4BF))),
    amberBadge = Brush.linearGradient(listOf(Color(0xFF4A3512), Color(0xFF3A2A0E))),
    listening = Brush.linearGradient(listOf(Color(0xFFD96257), Color(0xFFC8524A), Color(0xFF9E362F))),
)

val LocalUccharanGradients = staticCompositionLocalOf { LightGradients }

internal fun gradientsFor(darkTheme: Boolean) = if (darkTheme) DarkGradients else LightGradients
