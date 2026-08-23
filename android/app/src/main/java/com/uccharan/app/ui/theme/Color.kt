package com.uccharan.app.ui.theme

import androidx.compose.ui.graphics.Color

// Primary — deep teal. Calm, trustworthy, distinct from the generic
// "AI purple" every other AI app defaults to.
val TealPrimaryLight = Color(0xFF146C6B)
val TealPrimaryDark = Color(0xFF7FDAD5)
val OnTealPrimaryLight = Color(0xFFFFFFFF)
val OnTealPrimaryDark = Color(0xFF003736)
val TealPrimaryContainerLight = Color(0xFFA6F1E0)
val TealPrimaryContainerDark = Color(0xFF00504E)

// Secondary — muted slate teal, for less prominent UI (chips, secondary text emphasis)
val SlateSecondaryLight = Color(0xFF4A6363)
val SlateSecondaryDark = Color(0xFFB1CCCB)

// Tertiary — warm amber, reserved for streaks / XP / celebratory moments so
// it stays meaningful instead of decorative
val AmberTertiaryLight = Color(0xFF8C5000)
val AmberTertiaryDark = Color(0xFFFFB951)
val AmberTertiaryContainerLight = Color(0xFFFFDDB3)
val AmberTertiaryContainerDark = Color(0xFF6B3D00)

// Neutral surfaces
val BackgroundLight = Color(0xFFFAFDFB)
val BackgroundDark = Color(0xFF0E1514)
val SurfaceLight = Color(0xFFFAFDFB)
val SurfaceDark = Color(0xFF0E1514)
val SurfaceVariantLight = Color(0xFFF0F5F3)
val SurfaceVariantDark = Color(0xFF161F1E)
val OnBackgroundLight = Color(0xFF171D1C)
val OnBackgroundDark = Color(0xFFE0E3E1)
val OnSurfaceVariantLight = Color(0xFF45514F)
val OnSurfaceVariantDark = Color(0xFFB8C4C1)
val OutlineLight = Color(0xFFDCE5E2)
val OutlineDark = Color(0xFF2E3A38)

val ErrorLight = Color(0xFFBA1A1A)
val ErrorDark = Color(0xFFFFB4AB)

// Listening / retry state — a warm coral, distinct from the semantic error
// red so "recording" never reads as "something went wrong"
val ListeningLight = Color(0xFFC8524A)
val ListeningDark = Color(0xFF9E362F)

// Muted secondary text (e.g. "10 XP" labels) — picked to clear WCAG AA
// (~4.5:1) against SurfaceVariant in both themes.
val MutedTextLight = Color(0xFF57635F)
val MutedTextDark = Color(0xFF8A9895)
