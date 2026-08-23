package com.uccharan.app.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

private val LightColorScheme = lightColorScheme(
    primary = TealPrimaryLight,
    onPrimary = OnTealPrimaryLight,
    primaryContainer = TealPrimaryContainerLight,
    secondary = SlateSecondaryLight,
    tertiary = AmberTertiaryLight,
    tertiaryContainer = AmberTertiaryContainerLight,
    background = BackgroundLight,
    surface = SurfaceLight,
    onBackground = OnBackgroundLight,
    onSurface = OnBackgroundLight,
    error = ErrorLight,
)

private val DarkColorScheme = darkColorScheme(
    primary = TealPrimaryDark,
    onPrimary = OnTealPrimaryDark,
    primaryContainer = TealPrimaryContainerDark,
    secondary = SlateSecondaryDark,
    tertiary = AmberTertiaryDark,
    tertiaryContainer = AmberTertiaryContainerDark,
    background = BackgroundDark,
    surface = SurfaceDark,
    onBackground = OnBackgroundDark,
    onSurface = OnBackgroundDark,
    error = ErrorDark,
)

/**
 * Uccharan's Material 3 theme. Dynamic color (Android 12+ wallpaper-derived
 * palettes) is deliberately NOT used here — a tutor app wants a consistent,
 * recognizable brand identity across every device, not one that shifts with
 * the user's wallpaper.
 */
@Composable
fun UccharanTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content,
    )
}
