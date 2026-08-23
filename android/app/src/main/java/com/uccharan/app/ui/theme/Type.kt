package com.uccharan.app.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp
import com.uccharan.app.R

/** Editorial serif — headlines and the lesson "hero" target sentence. Bundled as static TTFs (not a runtime Google Fonts fetch) so text renders correctly offline and without a Play Services dependency. */
val Newsreader = FontFamily(
    Font(R.font.newsreader_regular, FontWeight.Normal),
    Font(R.font.newsreader_medium, FontWeight.Medium),
    Font(R.font.newsreader_semibold, FontWeight.SemiBold),
    Font(R.font.newsreader_medium_italic, FontWeight.Medium, FontStyle.Italic),
    Font(R.font.newsreader_semibold_italic, FontWeight.SemiBold, FontStyle.Italic),
)

/** UI sans — body text, labels, buttons. */
val PlusJakartaSans = FontFamily(
    Font(R.font.plusjakarta_regular, FontWeight.Normal),
    Font(R.font.plusjakarta_medium, FontWeight.Medium),
    Font(R.font.plusjakarta_semibold, FontWeight.SemiBold),
    Font(R.font.plusjakarta_bold, FontWeight.Bold),
    Font(R.font.plusjakarta_extrabold, FontWeight.ExtraBold),
)

/** Native-language explanation text (Telugu, etc.) — Plus Jakarta Sans has no Telugu glyphs. */
val NotoSansTelugu = FontFamily(
    Font(R.font.notosanstelugu_regular, FontWeight.Normal),
    Font(R.font.notosanstelugu_semibold, FontWeight.SemiBold),
)

private val DisplaySmall = TextStyle(
    fontFamily = Newsreader,
    fontWeight = FontWeight.SemiBold,
    fontStyle = FontStyle.Italic,
    fontSize = 36.sp,
    lineHeight = 41.sp,
    letterSpacing = (-0.3).sp,
)

private val HeadlineMedium = TextStyle(
    fontFamily = Newsreader,
    fontWeight = FontWeight.SemiBold,
    fontSize = 27.sp,
    lineHeight = 33.sp,
    letterSpacing = (-0.2).sp,
)

private val HeadlineSmall = TextStyle(
    fontFamily = Newsreader,
    fontWeight = FontWeight.SemiBold,
    fontSize = 24.sp,
    lineHeight = 30.sp,
    letterSpacing = (-0.2).sp,
)

// Lesson "hero" target sentence — the one moment on screen that should feel
// spoken aloud, not just labeled.
private val TitleLarge = TextStyle(
    fontFamily = Newsreader,
    fontWeight = FontWeight.Medium,
    fontStyle = FontStyle.Italic,
    fontSize = 32.sp,
    lineHeight = 38.sp,
    letterSpacing = (-0.2).sp,
)

private val TitleMedium = TextStyle(
    fontFamily = Newsreader,
    fontWeight = FontWeight.Medium,
    fontSize = 18.sp,
    lineHeight = 24.sp,
)

private val BodyLarge = TextStyle(
    fontFamily = PlusJakartaSans,
    fontWeight = FontWeight.Normal,
    fontSize = 16.sp,
    lineHeight = 25.sp,
    letterSpacing = 0.1.sp,
)

private val BodyMedium = TextStyle(
    fontFamily = PlusJakartaSans,
    fontWeight = FontWeight.Normal,
    fontSize = 14.5.sp,
    lineHeight = 22.sp,
)

private val BodySmall = TextStyle(
    fontFamily = PlusJakartaSans,
    fontWeight = FontWeight.Normal,
    fontSize = 13.sp,
    lineHeight = 19.sp,
)

private val LabelLarge = TextStyle(
    fontFamily = PlusJakartaSans,
    fontWeight = FontWeight.Bold,
    fontSize = 15.5.sp,
    lineHeight = 20.sp,
    letterSpacing = 0.2.sp,
)

private val LabelMedium = TextStyle(
    fontFamily = PlusJakartaSans,
    fontWeight = FontWeight.Bold,
    fontSize = 12.5.sp,
    lineHeight = 16.sp,
    letterSpacing = 0.3.sp,
)

private val LabelSmall = TextStyle(
    fontFamily = PlusJakartaSans,
    fontWeight = FontWeight.SemiBold,
    fontSize = 11.5.sp,
    lineHeight = 15.sp,
    letterSpacing = 0.3.sp,
)

val Typography = Typography(
    displaySmall = DisplaySmall,
    headlineMedium = HeadlineMedium,
    headlineSmall = HeadlineSmall,
    titleLarge = TitleLarge,
    titleMedium = TitleMedium,
    bodyLarge = BodyLarge,
    bodyMedium = BodyMedium,
    bodySmall = BodySmall,
    labelLarge = LabelLarge,
    labelMedium = LabelMedium,
    labelSmall = LabelSmall,
)
