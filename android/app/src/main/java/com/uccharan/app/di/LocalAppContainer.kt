package com.uccharan.app.di

import androidx.compose.runtime.compositionLocalOf

val LocalAppContainer = compositionLocalOf<AppContainer> {
    error("AppContainer not provided — wrap the app in CompositionLocalProvider(LocalAppContainer provides ...)")
}
